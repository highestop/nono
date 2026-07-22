---
name: mweb-media-reference-checker
description: Check an MWeb document library for missing or redundant media file references
---

# Workflow

- Refer to [docs-structure-guide](/docs/mweb/docs-structure-guide.md) to understand how document content and media files are organized in the document library
- Use `./script.sh`, relative to the skill root, to check for missing or redundant media file references
- Analyze the script output and present the results to the user in natural language
- For **missing media files**, which are referenced but do not exist, ask whether to remove the references from the documents
- For **redundant media files**, which exist but are not referenced, ask whether to delete the unused files

# Features

- Scan all Markdown files in the `docs` directory
- Identify missing media files that are referenced in documents but do not exist
- Identify redundant media files that exist but are not referenced by any document
- Print results to the command line with color-coded messages
- Provide cleanup options to remove broken references or delete unused files

# Use cases

- When documents may contain broken image links
- Before cleaning a media directory to remove unused files
- As part of routine maintenance to keep the document library tidy
- After bulk operations on documents or media files

# Cleanup options

After identifying problems, the skill provides the following cleanup actions:

## Missing media files
- **Problem**: A document references `![](media/123/image.jpg)`, but the file does not exist
- **Action**: Remove the broken image reference from the document
- **Safety**: Always obtain user confirmation before modifying a document

## Redundant media files
- **Problem**: A file exists at `docs/media/123/unused.jpg`, but no document references it
- **Action**: Delete the unused media file to save space
- **Safety**: Always obtain user confirmation before deleting a file

## User control
- Let the user choose whether to fix all problems at once or handle them individually
- Require explicit user approval for every modification
- Do not make any changes automatically without permission
