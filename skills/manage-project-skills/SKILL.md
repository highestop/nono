---
name: manage-project-skills
description: Manage project-level third-party skills in a repository with the skills CLI, including installing, restoring, updating, removing, and using skills while keeping generated skill files out of Git.
---

# Manage project skills

Use this skill when a user asks to add, restore, update, remove, or use a third-party skill in the current repository. Work from the repository root and keep operations project-scoped unless the user explicitly requests a global installation.

## Rules

- Use the pinned CLI: `npx skills@1.7.2`.
- Omit `-g` and use `--agent codex` for project skills. The project files are restored under `.agents/skills/`.
- Keep `skills-lock.json` in Git. Do not stage `.agents/skills/` or downloaded skill contents.
- If `.gitignore` hides `skills-lock.json`, add an explicit `!skills-lock.json` exception; keep `.agents/skills/` ignored.
- Prefer a 40-character Git commit SHA for GitHub sources. A branch or tag can move and is less reproducible.
- Before a destructive removal, verify the exact skill name. Do not use `--all` unless the user explicitly asks to remove every project skill.
- Review a third-party `SKILL.md` and its supporting files before invoking it; skills run with the agent's permissions.

## Install a new skill

1. Confirm the source, skill name, and requested scope. For a GitHub source, resolve a branch or tag to a commit when the user has not supplied one.
2. Install the selected skill into the project:

   ```bash
   npx skills@1.7.2 add "<owner>/<repo>#<commit-sha>" \
     --skill <skill-name> \
     --agent codex \
     --yes
   ```

   Use the full GitHub tree URL when the skill is in a known subdirectory:

   ```bash
   npx skills@1.7.2 add \
     "https://github.com/<owner>/<repo>/tree/<commit-sha>/<skill-path>" \
     --agent codex \
     --yes
   ```

3. Check that `skills-lock.json` records the source, skill path, commit ref, and content hash. Confirm `.agents/skills/<skill-name>/SKILL.md` exists and is ignored by Git.

Do not install the whole repository when it contains multiple skills unless the user asks for all of them; pass `--skill <skill-name>`.

## Restore skills after cloning

From a fresh clone, install project dependencies first when the lock contains `node_modules` entries. Then restore the locked project skills:

```bash
npx skills@1.7.2 experimental_install -y
```

This reads the current directory's `skills-lock.json` and attempts every entry. Remote entries are fetched from their recorded source and ref into `.agents/skills/`; `node_modules` entries are synchronized from already-installed dependencies. It does not install skills that are absent from the lock file or install global skills.

After restoring, verify the result:

```bash
npx skills@1.7.2 list --json
```

Restart the agent session if the skill was not visible before the restore.

## Update an existing skill

To check or refresh project skills at the ref recorded in the lock file:

```bash
npx skills@1.7.2 update <skill-name> --project --yes
```

For all project skills:

```bash
npx skills@1.7.2 update --project --yes
```

A commit-pinned entry is expected to remain unchanged because the ref identifies an immutable snapshot. To intentionally upgrade it, review the new upstream commit and reinstall the same skill with the new ref:

```bash
npx skills@1.7.2 add "<owner>/<repo>#<new-commit-sha>" \
  --skill <skill-name> \
  --agent codex \
  --yes
```

Review the resulting `skills-lock.json` diff before accepting the upgrade.

## Remove a skill

Remove one named project skill and its lock entry:

```bash
npx skills@1.7.2 remove <skill-name> --agent codex --yes
```

Check that the skill directory and, when no other project agent still uses it, its `skills-lock.json` entry are gone. Do not remove a skill only by deleting `.agents/skills/<skill-name>/`; that leaves the lock file inconsistent.

## Use a skill

For an installed project skill, start a new agent session after installation or restoration and invoke it explicitly:

```text
$<skill-name> <describe the task>
```

Natural-language requests can also trigger the skill when its description matches. For a one-off use without adding the skill to the project, ask the CLI to download it and generate a prompt:

```bash
npx skills@1.7.2 use "<owner>/<repo>@<skill-name>" --agent codex
```

This temporary command does not update `skills-lock.json` or install the skill into `.agents/skills/`.

## Verify changes

After any install, update, or removal, inspect the repository state and lock diff:

```bash
git status --short
git diff -- skills-lock.json
git check-ignore -q .agents/skills/<skill-name>
```

Only the intended lock-file and ignore-rule changes should be committed. Never commit generated skill contents. If a generated skill directory appears as an untracked file, stop and fix the ignore rule before committing.
