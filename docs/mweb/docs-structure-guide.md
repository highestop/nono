> Use this guide when you need to understand how MWeb documents and their media files are organized in a document library.

## Fundamentals

- MWeb's timestamp-based file-naming convention
- The relationship between documents and media directories
- File-path patterns and reference structure
- Examples of how documents link to media files

## Document structure

### File organization
- **Documents**: Stored in the `docs/` directory
- **Media files**: Stored in `docs/media/{timestamp}/` subdirectories
- **Naming convention**: Both use the same timestamp identifier

### Structure pattern
```
docs/
├── {timestamp}.md              # Document file
└── media/
    └── {timestamp}/           # Media directory for this document
        ├── image1.png
        ├── image2.jpg
        └── ...
```

### Example
- **Document file**: `docs/17671544643078.md`
- **Media directory**: `docs/media/17671544643078/`
- **Media reference in the document**: `![](media/17671544643078/hello.png)`
- **Actual file path**: `docs/media/17671544643078/hello.png`

## Use cases

- Before processing an MWeb document library
- When building tools that process MWeb files
- When you need to understand file-path relationships
- Before implementing media-file operations

## Constraints

- This is a knowledge-only guide and does not perform file operations
- This structure applies only to MWeb document libraries, not other Markdown systems
- Assume the standard MWeb export and organization pattern
