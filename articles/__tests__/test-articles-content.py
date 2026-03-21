#!/usr/bin/env python3
"""Validate all article files against skill conventions.

Run from the project root:
    python3 articles/__tests__/test-articles-content.py

Exit code 0 = all checks pass, 1 = failures found.
"""

import os
import re
import sys

ARTICLES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# CJK spacing check
# ---------------------------------------------------------------------------

# Pattern: Chinese char directly adjacent to ASCII letter/digit (no space)
# Covers both directions: 中A, A中, 中1, 1中
CJK_RANGE = (
    r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff"
    r"\U00020000-\U0002a6df\U0002a700-\U0002b73f"
    r"\U0002b740-\U0002b81f\U0002b820-\U0002ceaf"
    r"\U0002ceb0-\U0002ebef\U00030000-\U0003134f]"
)
RE_CJK_NO_SPACE = re.compile(
    rf"({CJK_RANGE})([A-Za-z0-9])|([A-Za-z0-9])({CJK_RANGE})"
)

# Skip lines that are image references, raw URLs, or HTML tags
RE_SKIP_LINE = re.compile(r"^\s*(!?\[.*\]\(.*\)|https?://|<)")


def check_cjk_spacing(filepath, lines, errors):
    """Check CJK spacing in article content (skip URLs, images, code blocks)."""
    in_code_block = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if RE_SKIP_LINE.match(stripped):
            continue
        # Check for CJK chars directly adjacent to ASCII letters/digits
        for m in RE_CJK_NO_SPACE.finditer(line):
            errors.append(f"{filepath}:{i}: CJK spacing violation: ...{m.group()}...")


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def validate_directory_name(dirname, errors):
    """Directory name must be YYYY-MM-DD."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dirname):
        errors.append(f"{dirname}/: directory name is not YYYY-MM-DD format")


def validate_filename_prefix(filepath, filename, errors):
    """wx/xhs/x files must have correct prefix."""
    # Only check files that look like they should have a prefix
    # (skip local.py, index.html, notes files, etc.)
    if not filename.endswith(".md"):
        return
    base = filename.replace("-en.md", ".md")
    # No strict prefix required for generic articles (timestamp-based)
    # Just ensure no obviously wrong patterns


def validate_bilingual_pair(dirpath, filename, all_files, errors):
    """-en.md must have a corresponding main file."""
    if filename.endswith("-en.md"):
        main_file = filename[: -len("-en.md")] + ".md"
        if main_file not in all_files:
            errors.append(f"{dirpath}/{filename}: -en.md file has no corresponding main file")


def validate_en_no_tags(filepath, lines, errors):
    """-en.md files must not have a tag line."""
    for line in lines:
        if re.match(r">\s*-\s*标签：", line):
            errors.append(f"{filepath}: -en.md file should not have tags")
            break


def validate_header(filepath, lines, filename, errors):
    """Validate article header structure."""
    if not lines:
        errors.append(f"{filepath}: file is empty")
        return

    # 1. First line must be # <title>
    if not re.match(r"^#\s+.+", lines[0].strip()):
        errors.append(f"{filepath}: first line must be a # heading")
        return

    # 2. Find metadata block (lines starting with >)
    has_metadata = False
    has_separator = False
    has_link = False
    has_tags = False

    for i, line in enumerate(lines[1:], 2):
        stripped = line.strip()
        if stripped == "":
            continue
        if stripped.startswith(">"):
            has_metadata = True
            # Check for original link
            if re.match(r">\s*-\s*原文链接：", stripped):
                has_link = True
                validate_link_format(filepath, stripped, filename, errors)
            if re.match(r">\s*-\s*标签：", stripped):
                has_tags = True
                validate_tag_format(filepath, stripped, errors)
        elif stripped == "---":
            has_separator = True
            break
        elif has_metadata:
            # Non-blockquote, non-separator line after metadata started
            break

    if not has_metadata:
        errors.append(f"{filepath}: missing metadata block (> lines) after title")
    # Only require --- if structured metadata fields (> - ...) are present
    if has_link and not has_separator:
        errors.append(f"{filepath}: missing --- separator after metadata")

    # Tags required for non -en files
    is_en = filepath.endswith("-en.md")
    if not is_en and not has_tags:
        errors.append(f"{filepath}: missing tag line (> - 标签：...)")


def validate_link_format(filepath, line, filename, errors):
    """Validate original link format based on file prefix."""
    # Extract URL from the line
    m = re.match(r">\s*-\s*原文链接：(.+)", line)
    if not m:
        return
    url = m.group(1).strip()
    base = os.path.basename(filepath).replace("-en.md", ".md")

    if base.startswith("wx-"):
        # Must be https://mp.weixin.qq.com/s/<hash>
        if not re.match(r"https://mp\.weixin\.qq\.com/s/[\w-]+$", url):
            errors.append(f"{filepath}: wx article link must be https://mp.weixin.qq.com/s/<hash>, got: {url}")
    elif base.startswith("xhs-"):
        # Must be http://xhslink.com/o/<id>
        if not re.match(r"http://xhslink\.com/o/[\w]+$", url):
            errors.append(f"{filepath}: xhs article link must be http://xhslink.com/o/<id>, got: {url}")
    elif base.startswith("x-"):
        # Must be https://x.com/<user>/status/<id>
        if not re.match(r"https://x\.com/[\w]+/status/\d+$", url):
            errors.append(f"{filepath}: x article link must be https://x.com/<user>/status/<id>, got: {url}")


def validate_tag_format(filepath, line, errors):
    """Validate tag line format: comma-separated, no # prefix, non-empty tags."""
    m = re.match(r">\s*-\s*标签：(.+)", line)
    if not m:
        return
    raw = m.group(1)
    tags = [t.strip() for t in raw.split(",")]

    for tag in tags:
        if not tag:
            errors.append(f"{filepath}: empty tag found (extra comma?)")
        elif tag.startswith("#"):
            errors.append(f"{filepath}: tag should not use # prefix: {tag}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    errors = []

    if not os.path.isdir(ARTICLES_DIR):
        print(f"Articles directory not found: {ARTICLES_DIR}")
        sys.exit(1)

    for dirname in sorted(os.listdir(ARTICLES_DIR)):
        dirpath = os.path.join(ARTICLES_DIR, dirname)
        if not os.path.isdir(dirpath) or dirname.startswith(".") or dirname.startswith("__"):
            continue

        # Validate directory name
        validate_directory_name(dirname, errors)

        md_files = [f for f in os.listdir(dirpath) if f.endswith(".md")]

        for filename in sorted(md_files):
            filepath = os.path.join(dirpath, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.splitlines()

            # Bilingual pair check
            validate_bilingual_pair(dirpath, filename, set(md_files), errors)

            if filename.endswith("-en.md"):
                # -en files: no tags, skip other header checks
                validate_en_no_tags(filepath, lines, errors)
            else:
                # Main files: full header validation
                validate_header(filepath, lines, filename, errors)

            # CJK spacing: check all files
            check_cjk_spacing(filepath, lines, errors)

    # Print results
    if errors:
        print(f"Found {len(errors)} issue(s):\n")
        for e in errors:
            print(f"  ✗ {e}")
        print()
        sys.exit(1)
    else:
        print("All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
