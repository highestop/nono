#!/usr/bin/env python3
"""Unit tests for articles/local.py extract_metadata()."""

import os
import sys
import tempfile

# Add articles dir to path so we can import local
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from local import extract_metadata


def test_standard_header():
    """Standard article with title and tags."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# 测试文章\n\n> - 来源：test\n> - 标签：AI 编程, Agent\n\n---\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "测试文章", f"Expected '测试文章', got '{title}'"
    assert tags == ["AI 编程", "Agent"], f"Expected ['AI 编程', 'Agent'], got {tags}"


def test_no_tags():
    """Article without tags (e.g. -en file)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# English Title\n\n> - 作者：John\n\n---\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "English Title", f"Expected 'English Title', got '{title}'"
    assert tags == [], f"Expected [], got {tags}"


def test_bare_url_header():
    """Older format with bare URL blockquote."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# 旧格式\n\n> https://example.com\n>\n> - 标签：Vibe Coding\n\n> 正文开始\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "旧格式", f"Expected '旧格式', got '{title}'"
    assert tags == ["Vibe Coding"], f"Expected ['Vibe Coding'], got {tags}"


def test_empty_file():
    """Empty file should return None title and empty tags."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title is None, f"Expected None, got '{title}'"
    assert tags == [], f"Expected [], got {tags}"


def test_single_tag():
    """Single tag without comma."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("# 单标签\n\n> - 标签：Agent\n\n---\n")
        f.flush()
        title, tags = extract_metadata(f.name)
    os.unlink(f.name)
    assert title == "单标签", f"Expected '单标签', got '{title}'"
    assert tags == ["Agent"], f"Expected ['Agent'], got {tags}"


def test_nonexistent_file():
    """Non-existent file should return None and []."""
    title, tags = extract_metadata("/tmp/nonexistent-article-12345.md")
    assert title is None, f"Expected None, got '{title}'"
    assert tags == [], f"Expected [], got {tags}"


def main():
    tests = [
        test_standard_header,
        test_no_tags,
        test_bare_url_header,
        test_empty_file,
        test_single_tag,
        test_nonexistent_file,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  ✓ {test.__doc__.strip()}")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {test.__doc__.strip()}: {e}")

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
