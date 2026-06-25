#!/usr/bin/env python3
"""Generate articles/tags.csv from all article metadata.

Uses server.extract_metadata() to collect tags across all articles,
then writes a CSV with tag name and article count.

Run from the project root:
    python3 scripts/generate-tags.py
"""

import csv
import os
import sys

ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "articles")
sys.path.insert(0, ARTICLES_DIR)
from server import extract_metadata


def main():
    tag_counts = {}  # tag -> count

    for dirname in sorted(os.listdir(ARTICLES_DIR)):
        dirpath = os.path.join(ARTICLES_DIR, dirname)
        if not os.path.isdir(dirpath) or dirname.startswith(".") or dirname.startswith("__"):
            continue
        for filename in sorted(os.listdir(dirpath)):
            if not filename.endswith(".md") or filename.endswith("-en.md"):
                continue
            filepath = os.path.join(dirpath, filename)
            _, tags = extract_metadata(filepath)
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by count descending, then alphabetically
    sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))

    output_path = os.path.join(ARTICLES_DIR, "tags.csv")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for tag, count in sorted_tags:
            writer.writerow([tag, count])

    print(f"Generated {output_path} with {len(sorted_tags)} tags.")


if __name__ == "__main__":
    main()
