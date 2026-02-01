---
name: mweb-media-reference-checker
description: Check for missing or redundant media file references in MWeb document library
---

# Workflow

- Load `/mweb-structure-guide` skill to learn about how document content and their media files are arranged in library
- Use `./script.sh` (relative to skill root) to check for missing or redundant media file references
- Analyze script output and present findings in natural language to the user
- For **missing media files** (referenced but don't exist): Ask user whether to remove these references from documents
- For **redundant media files** (exist but not referenced): Ask user whether to delete these unused files

# What it does

- Scans all markdown files in the `docs` directory
- Identifies missing media files (referenced in documents but files don't exist)
- Identifies redundant media files (files exist but not referenced in any document)
- Outputs results to command line with color-coded information
- Offers to clean up issues by removing broken references or deleting unused files

# When to use

- When you suspect there might be broken image links in your documents
- Before cleaning up your media directory to remove unused files
- As part of regular maintenance to keep your document library organized
- After bulk operations on documents or media files

# Cleanup Options

After identifying issues, the skill will offer these cleanup actions:

## Missing Media Files
- **Issue**: Document references `![](media/123/image.jpg)` but the file doesn't exist
- **Action**: Remove the broken image reference from the document
- **Safety**: Always ask user confirmation before modifying documents

## Redundant Media Files
- **Issue**: File exists at `docs/media/123/unused.jpg` but no document references it
- **Action**: Delete the unused media file to save space
- **Safety**: Always ask user confirmation before deleting files

## User Control
- Users can choose to fix all issues at once or handle them selectively
- All modifications require explicit user approval
- No automatic changes are made without permission