#!/usr/bin/env python3
"""Manage external skills beside Nono's own skills (Python 3.9+, macOS/Linux)."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def read_json(path):
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or value.get("version") != 1:
        raise ValueError(f"Unsupported format in {path.name}")
    if not isinstance(value.get("skills"), dict):
        raise ValueError(f"Missing skills map in {path.name}")
    return value


def manifest(root):
    specs = read_json(root / "skills.json")["skills"]
    for name, spec in specs.items():
        if not NAME.fullmatch(name) or len(name) > 64:
            raise ValueError(f"Invalid skill name: {name}")
        if not isinstance(spec, dict) or set(spec) != {"source", "ref", "path"}:
            raise ValueError(f"{name}: provide source, ref, and path")
        if any(not isinstance(value, str) or not value for value in spec.values()):
            raise ValueError(f"{name}: source, ref, and path must be nonempty strings")
        source, ref, path = spec["source"], spec["ref"], PurePosixPath(spec["path"])
        if not (
            source.startswith(("https://", "http://", "ssh://", "git://", "file://"))
            or re.fullmatch(r"[^/\s:]+@[^/\s:]+:.+", source)
            or Path(source).is_absolute()
        ):
            raise ValueError(f"{name}: source must be a full Git URL or absolute local Git path")
        if source.startswith("-") or ref.startswith("-") or any(
            char in source + ref + spec["path"] for char in "\n\r\0"
        ):
            raise ValueError(f"{name}: invalid source, ref, or path")
        if path.is_absolute() or ".." in path.parts or "\\" in spec["path"]:
            raise ValueError(f"{name}: path must stay inside the source repository")
        if spec["path"] != path.as_posix():
            raise ValueError(f"{name}: use a normalized repository-relative path")
    return specs


def read_lock(root):
    lock = read_json(root / "skills-lock.json")
    for name, entry in lock["skills"].items():
        if not isinstance(entry, dict) or not NAME.fullmatch(name):
            raise ValueError("Invalid skill entry in skills-lock.json")
        if any(not isinstance(entry.get(key), str) for key in ("source", "ref", "path")):
            raise ValueError(f"{name}: invalid source metadata in skills-lock.json")
        if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", str(entry.get("commit", ""))):
            raise ValueError(f"{name}: invalid commit in skills-lock.json")
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("contentHash", ""))):
            raise ValueError(f"{name}: invalid content hash in skills-lock.json")
    return lock


def git(cwd, *args):
    result = subprocess.run(
        ["git", "-C", str(cwd), *args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def write_json(path, value):
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def fingerprint(folder):
    digest = hashlib.sha256()
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            kind, data = b"link", os.readlink(path).encode()
        elif path.is_file():
            kind, data = b"file", path.read_bytes()
        else:
            continue
        digest.update(path.relative_to(folder).as_posix().encode() + b"\0")
        digest.update(kind + b"\0" + str(path.lstat().st_mode & 0o777).encode() + b"\0")
        digest.update(len(data).to_bytes(8, "big") + data)
    return digest.hexdigest()


def managed_target(root, name, entry):
    destination = root / "skills" / name
    if not destination.is_symlink() or not isinstance(entry, dict):
        return None
    target = destination.resolve()
    installed = root / ".cache" / "external-skills" / "installed" / name
    if not target.is_relative_to(installed) or not target.is_dir():
        return None
    if fingerprint(target) != entry.get("contentHash"):
        return None
    return target


def check_destination(root, name, entry):
    relative = f"skills/{name}"
    if git(root, "ls-files", "--", relative):
        raise ValueError(f"{name}: refusing to replace a version-controlled skill")
    destination = root / relative
    if os.path.lexists(destination) and managed_target(root, name, entry) is None:
        raise ValueError(f"{name}: destination is unmanaged or locally modified")


def ignore_generated_link(root, name):
    exclude = root / "skills" / ".gitignore"
    if exclude.is_symlink() or git(root, "ls-files", "--", "skills/.gitignore"):
        raise ValueError("skills/.gitignore must be an untracked, regular generated file")
    content = exclude.read_text() if exclude.exists() else ""
    pattern = f"/{name}"
    if pattern not in content.splitlines():
        exclude.parent.mkdir(parents=True, exist_ok=True)
        with exclude.open("a") as stream:
            stream.write(("\n" if content and not content.endswith("\n") else "") + pattern + "\n")


def fetch(root, spec, ref, fetched):
    key = (spec["source"], ref)
    if key in fetched:
        return fetched[key]
    cache = root / ".cache" / "external-skills"
    repo = cache / "repos" / hashlib.sha256(spec["source"].encode()).hexdigest()
    if not repo.exists():
        repo.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".init-", dir=repo.parent) as temporary:
            staged = Path(temporary)
            git(staged, "init", "--bare", "--quiet")
            git(staged, "remote", "add", "origin", spec["source"])
            staged.rename(repo)
    git(repo, "fetch", "--quiet", "--no-tags", "--depth=1", "origin", ref)
    commit = git(repo, "rev-parse", "FETCH_HEAD^{commit}")
    fetched[key] = (repo, commit)
    return repo, commit


def extract_skill(repo, commit, path, destination, name):
    treeish = commit if path == "." else f"{commit}:{path}"
    if git(repo, "cat-file", "-t", treeish) not in ("tree", "commit"):
        raise ValueError(f"{name}: source path is not a directory")
    with tempfile.TemporaryFile() as archive:
        subprocess.run(
            ["git", "-C", str(repo), "archive", "--format=tar", treeish],
            stdout=archive, stderr=subprocess.PIPE, check=True, timeout=60,
        )
        archive.seek(0)
        with tarfile.open(fileobj=archive) as bundle:
            members = bundle.getmembers()
            for member in members:
                member_path = PurePosixPath(member.name)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise ValueError(f"{name}: unsafe archive path")
                if not (member.isdir() or member.isfile() or member.issym()):
                    raise ValueError(f"{name}: unsupported archive entry")
                if member.issym():
                    target = destination / member.name
                    resolved = (target.parent / member.linkname).resolve()
                    if Path(member.linkname).is_absolute() or not resolved.is_relative_to(destination):
                        raise ValueError(f"{name}: symlink escapes the skill directory")
            # Extract files before links, so extraction never writes through a link.
            for member in members:
                target = destination / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                if member.isdir():
                    target.mkdir(exist_ok=True)
                elif member.isfile():
                    with bundle.extractfile(member) as source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
                    target.chmod(member.mode & 0o777)
            for member in members:
                if member.issym():
                    (destination / member.name).symlink_to(member.linkname)
    skill = destination / "SKILL.md"
    if not skill.is_file() or skill.is_symlink():
        raise ValueError(f"{name}: source must contain a regular SKILL.md")
    text = skill.read_text()
    parts = re.split(r"(?m)^---[ \t]*\r?$", text, maxsplit=2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"{name}: SKILL.md needs YAML frontmatter")
    match = re.search(r"(?m)^name:[ \t]*([^\r\n]+)", parts[1])
    declared = match.group(1).split(" #", 1)[0].strip().strip("'\"") if match else ""
    if declared != name:
        raise ValueError(f"{name}: SKILL.md name must match the manifest key")
    for link in destination.rglob("*"):
        if link.is_symlink() and not link.resolve().is_relative_to(destination):
            raise ValueError(f"{name}: symlink chain escapes the skill directory")


def replace_link(destination, target):
    fd, temporary = tempfile.mkstemp(prefix=".skill-link-", dir=destination.parent)
    os.close(fd)
    link = Path(temporary)
    link.unlink()
    try:
        link.symlink_to(os.path.relpath(target, destination.parent))
        os.replace(link, destination)
    finally:
        link.unlink(missing_ok=True)


def install_one(root, name, spec, lock, mode, fetched):
    previous = lock["skills"].get(name)
    check_destination(root, name, previous)
    matches = isinstance(previous, dict) and all(previous.get(k) == v for k, v in spec.items())
    existing = managed_target(root, name, previous)
    if mode == "setup" and matches and existing is not None:
        return False
    ref = previous["commit"] if mode == "setup" and matches else spec["ref"]
    repo, commit = fetch(root, spec, ref, fetched)
    snapshots = root / ".cache" / "external-skills" / "installed" / name
    snapshots.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".staging-", dir=snapshots) as temporary:
        staged = Path(temporary)
        extract_skill(repo, commit, spec["path"], staged, name)
        content_hash = fingerprint(staged)
        if mode == "setup" and matches and content_hash != previous["contentHash"]:
            raise ValueError(f"{name}: downloaded content does not match the lock")
        if matches and existing is not None and previous["contentHash"] == content_hash:
            return False
        snapshot = snapshots / content_hash
        if snapshot.exists():
            if fingerprint(snapshot) != content_hash:
                raise ValueError(f"{name}: cached snapshot was locally modified")
        else:
            staged.rename(snapshot)
    destination = root / "skills" / name
    destination.parent.mkdir(exist_ok=True)
    ignore_generated_link(root, name)
    entry = {**spec, "commit": commit, "contentHash": content_hash}
    replace_link(destination, snapshot)
    try:
        lock["skills"][name] = entry
        write_json(root / "skills-lock.json", lock)
    except BaseException:
        if existing is None:
            destination.unlink()
        else:
            replace_link(destination, existing)
        if previous is None:
            lock["skills"].pop(name, None)
        else:
            lock["skills"][name] = previous
        raise
    print(f"{name}: installed {commit[:12]}", file=sys.stderr, flush=True)
    return True


def sync(root, mode="update", quiet=False):
    specs = manifest(root)
    if not specs:
        if not quiet:
            print("No external skills configured.", file=sys.stderr)
        return True
    cache = root / ".cache" / "external-skills"
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / "sync.lock").open("a") as mutex:
        try:
            fcntl.flock(mutex, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Another skill sync is running; skipping this check.", file=sys.stderr)
            return False
        lock = read_lock(root)
        fetched, success, changed = {}, True, False
        for name, spec in specs.items():
            try:
                changed = install_one(root, name, spec, lock, mode, fetched) or changed
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, tarfile.TarError) as error:
                print(f"{name}: sync failed: {error}", file=sys.stderr, flush=True)
                success = False
        if success and not changed and not quiet:
            print("External skills are up to date.", file=sys.stderr)
        return success


def available(root):
    specs = manifest(root)
    if not specs:
        return True
    cache = root / ".cache" / "external-skills"
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / "sync.lock").open("a") as mutex:
        fcntl.flock(mutex, fcntl.LOCK_SH)
        lock = read_lock(root)
        return all(managed_target(root, name, lock["skills"].get(name)) is not None for name in specs)


def interval(value):
    seconds = float(value)
    if not 0 < seconds <= 86400:
        raise argparse.ArgumentTypeError("interval must be between 0 and 86400 seconds")
    return seconds


def run_agent(root, command, seconds):
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("Provide an agent command, for example: agent.sh codex")
    updated = sync(root)
    if not available(root):
        raise ValueError("Required skills are unavailable; the agent was not started")
    if not updated:
        print("Continuing with the last usable external skills.", file=sys.stderr)
    with subprocess.Popen(command) as agent:
        # The terminal delivers Ctrl-C to the agent; let it handle cancellation.
        old_int = signal.signal(signal.SIGINT, signal.SIG_IGN)
        old_term = signal.signal(signal.SIGTERM, lambda *_: agent.terminate())
        try:
            while True:
                try:
                    code = agent.wait(timeout=seconds)
                    return code if code >= 0 else 128 - code
                except subprocess.TimeoutExpired:
                    try:
                        sync(root, quiet=True)
                    except (OSError, ValueError, RuntimeError) as error:
                        print(f"Skill update failed: {error}", file=sys.stderr)
        finally:
            signal.signal(signal.SIGINT, old_int)
            signal.signal(signal.SIGTERM, old_term)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    commands.add_parser("setup", help="Install missing skills using the lock when available")
    update = commands.add_parser("update", help="Follow the refs declared in skills.json")
    update.add_argument("--watch", action="store_true", help="Repeat until interrupted")
    update.add_argument("--interval", type=interval, default=300)
    run = commands.add_parser("run", help="Sync, launch an agent, and update while it runs")
    run.add_argument("--interval", type=interval, default=300)
    run.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.mode == "run":
            return run_agent(ROOT, args.command, args.interval)
        while True:
            success = sync(ROOT, args.mode)
            if args.mode != "update" or not args.watch or not manifest(ROOT):
                return 0 if success else 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Skill sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
