---
name: mweb-structure-guide
description: Provides knowledge about MWeb document and media file organization structure
---

# MWeb Structure Guide

Use this skill when you need to understand how MWeb documents and their media files are organized in the library structure.

## What it provides

- Knowledge of MWeb's timestamp-based file naming convention
- Understanding of document-to-media directory relationships
- File path patterns and referencing structure
- Examples of how documents link to their media files

## Document Structure

### File Organization
- **Documents**: Stored in `docs/` directory
- **Media files**: Stored in `docs/media/{timestamp}/` subdirectories
- **Naming convention**: Both use the same timestamp identifier

### Structure Pattern
```
docs/
├── {timestamp}.md              # Document file
└── media/
    └── {timestamp}/           # Media directory for that document
        ├── image1.png
        ├── image2.jpg
        └── ...
```

### Example
- **Document file**: `docs/17671544643078.md`
- **Media directory**: `docs/media/17671544643078/`
- **Media reference in document**: `![](media/17671544643078/hello.png)`
- **Actual file path**: `docs/media/17671544643078/hello.png`

## When to use

- Before working with MWeb document libraries
- When building tools that process MWeb files
- When you need to understand file path relationships
- Before implementing media file operations

## Constraints

- This is knowledge-only skill - it doesn't perform file operations
- Structure applies specifically to MWeb libraries, not other markdown systems
- Assumes standard MWeb export/organization patterns