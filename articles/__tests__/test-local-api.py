#!/usr/bin/env python3
"""Tests for articles/local.py: extract_metadata() and HTTP API."""

import json
import os
import sys
import tempfile
import threading
import time
import urllib.request
import urllib.error

# Add articles dir to path so we can import local
ARTICLES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ARTICLES_DIR)
from local import extract_metadata, Handler

from http.server import HTTPServer

FIXTURES_DIR = os.path.join(ARTICLES_DIR, "__fixtures__")

# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

tests = []
passed = 0
failed = 0


def test(fn):
    tests.append(fn)
    return fn


def run_tests(test_list):
    global passed, failed
    for t in test_list:
        try:
            t()
            passed += 1
            print(f"  ✓ {t.__doc__.strip()}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {t.__doc__.strip()}: {e}")


# ---------------------------------------------------------------------------
# extract_metadata() tests
# ---------------------------------------------------------------------------

@test
def test_standard_header():
    """extract_metadata: standard article with title and tags."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# 测试文章\n\n> - 来源：test\n> - 标签：AI 编程, Agent\n\n---\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "测试文章", f"Expected '测试文章', got '{title}'"
    assert tags == ["AI 编程", "Agent"], f"Expected ['AI 编程', 'Agent'], got {tags}"


@test
def test_no_tags():
    """extract_metadata: article without tags (e.g. -en file)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# English Title\n\n> - 作者：John\n\n---\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "English Title", f"Expected 'English Title', got '{title}'"
    assert tags == [], f"Expected [], got {tags}"


@test
def test_bare_url_header():
    """extract_metadata: older format with bare URL blockquote."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# 旧格式\n\n> https://example.com\n>\n> - 标签：Vibe Coding\n\n> 正文开始\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "旧格式", f"Expected '旧格式', got '{title}'"
    assert tags == ["Vibe Coding"], f"Expected ['Vibe Coding'], got {tags}"


@test
def test_empty_file():
    """extract_metadata: empty file returns None and []."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title is None, f"Expected None, got '{title}'"
    assert tags == [], f"Expected [], got {tags}"


@test
def test_single_tag():
    """extract_metadata: single tag without comma."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# 单标签\n\n> - 标签：Agent\n\n---\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "单标签", f"Expected '单标签', got '{title}'"
    assert tags == ["Agent"], f"Expected ['Agent'], got {tags}"


@test
def test_nonexistent_file():
    """extract_metadata: non-existent file returns None and []."""
    title, tags = extract_metadata("/tmp/nonexistent-article-12345.md")
    assert title is None, f"Expected None, got '{title}'"
    assert tags == [], f"Expected [], got {tags}"


# ---------------------------------------------------------------------------
# HTTP API test helpers
# ---------------------------------------------------------------------------

_server = None
_server_thread = None
_server_port = None
_original_cwd = None


def start_server():
    """Start HTTP server serving __fixtures__ directory."""
    global _server, _server_thread, _server_port, _original_cwd
    _original_cwd = os.getcwd()
    os.chdir(FIXTURES_DIR)
    _server = HTTPServer(("127.0.0.1", 0), Handler)
    _server_port = _server.server_address[1]
    _server_thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _server_thread.start()


def stop_server():
    """Stop HTTP server and restore cwd."""
    global _server, _original_cwd
    if _server:
        _server.shutdown()
        _server = None
    if _original_cwd:
        os.chdir(_original_cwd)
        _original_cwd = None


def api_get(path):
    """GET request to test server, returns (status, body_str)."""
    url = f"http://127.0.0.1:{_server_port}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def api_post(path, data):
    """POST JSON to test server, returns (status, body_str)."""
    url = f"http://127.0.0.1:{_server_port}{path}"
    body = json.dumps(data).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


# ---------------------------------------------------------------------------
# HTTP API tests
# ---------------------------------------------------------------------------

api_tests = []


def api_test(fn):
    api_tests.append(fn)
    return fn


@api_test
def test_get_articles_structure():
    """GET /api/articles: returns correct JSON structure."""
    status, body = api_get("/api/articles")
    assert status == 200, f"Expected 200, got {status}"
    data = json.loads(body)
    assert "2099-01-01" in data, f"Expected '2099-01-01' folder, got keys: {list(data.keys())}"
    items = data["2099-01-01"]
    files = [item["file"] for item in items]
    assert "wx-testHash123.md" in files, f"Expected wx fixture, got: {files}"
    assert "xhs-abc123def456.md" in files, f"Expected xhs fixture, got: {files}"
    assert "x-9999999999999999999.md" in files, f"Expected x fixture, got: {files}"
    assert "x-9999999999999999999-en.md" in files, f"Expected x-en fixture, got: {files}"
    assert "1234567890000.md" in files, f"Expected generic fixture, got: {files}"


@api_test
def test_get_articles_metadata():
    """GET /api/articles: each item has correct title and tags."""
    status, body = api_get("/api/articles")
    data = json.loads(body)
    items = {item["file"]: item for item in data["2099-01-01"]}

    wx = items["wx-testHash123.md"]
    assert wx["title"] == "测试微信公众号文章", f"wx title: {wx['title']}"
    assert wx["tags"] == ["AI 编程", "测试"], f"wx tags: {wx['tags']}"

    xhs = items["xhs-abc123def456.md"]
    assert xhs["title"] == "测试小红书笔记标题", f"xhs title: {xhs['title']}"

    x_cn = items["x-9999999999999999999.md"]
    assert x_cn["tags"] == ["Agent", "产品设计"], f"x tags: {x_cn['tags']}"

    x_en = items["x-9999999999999999999-en.md"]
    assert x_en["tags"] == [], f"x-en should have no tags, got: {x_en['tags']}"

    generic = items["1234567890000.md"]
    assert generic["title"] == "测试通用文章", f"generic title: {generic['title']}"
    assert generic["tags"] == ["Vibe Coding", "工程实践"], f"generic tags: {generic['tags']}"


@api_test
def test_get_articles_skips_hidden():
    """GET /api/articles: skips hidden directories."""
    status, body = api_get("/api/articles")
    data = json.loads(body)
    for key in data:
        assert not key.startswith("."), f"Should skip hidden dir: {key}"


@api_test
def test_post_notes_save_and_delete():
    """POST /api/notes: save notes then delete by sending empty list."""
    file_path = "2099-01-01/wx-testHash123.md"
    notes_path = os.path.join(FIXTURES_DIR, "2099-01-01", "wx-testHash123.notes.json")

    # Save notes
    notes = [{"id": 1, "startOffset": 0, "endOffset": 5, "text": "测试", "note": "a note"}]
    status, body = api_post("/api/notes", {"file": file_path, "notes": notes})
    assert status == 200, f"Expected 200, got {status}"
    assert os.path.exists(notes_path), "notes.json should be created"
    with open(notes_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved[0]["note"] == "a note", f"Saved note mismatch: {saved}"

    # Delete notes (empty list)
    status, body = api_post("/api/notes", {"file": file_path, "notes": []})
    assert status == 200, f"Expected 200, got {status}"
    assert not os.path.exists(notes_path), "notes.json should be removed when empty"


@api_test
def test_post_notes_bad_request():
    """POST /api/notes: returns 400 for missing fields."""
    status, _ = api_post("/api/notes", {"file": "test.md"})
    assert status == 400, f"Expected 400 for missing notes, got {status}"

    status, _ = api_post("/api/notes", {"notes": []})
    assert status == 400, f"Expected 400 for missing file, got {status}"


@api_test
def test_post_notes_path_traversal():
    """POST /api/notes: rejects path traversal attempts."""
    status, _ = api_post("/api/notes", {"file": "../../../etc/passwd", "notes": [{"id": 1}]})
    assert status == 403, f"Expected 403 for path traversal, got {status}"

    status, _ = api_post("/api/notes", {"file": "/etc/passwd", "notes": [{"id": 1}]})
    assert status == 403, f"Expected 403 for absolute path, got {status}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global passed, failed

    print("extract_metadata() tests:")
    run_tests(tests)

    print("\nHTTP API tests:")
    try:
        start_server()
        run_tests(api_tests)
    finally:
        # Clean up any leftover notes files
        for root, dirs, files in os.walk(FIXTURES_DIR):
            for f in files:
                if f.endswith(".notes.json"):
                    os.remove(os.path.join(root, f))
        stop_server()

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
