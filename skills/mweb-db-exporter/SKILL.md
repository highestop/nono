---
name: mweb-db-exporter
description: Export MWeb database tables to JSON format for analysis and data processing
---

# MWeb Database Exporter

Use this skill when you need to export MWeb's SQLite database tables to JSON format for data analysis, backup, or integration with other tools.

## Workflow

- Load `/mweb-database-guide` skill to understand database structure
- Execute `./script.sh` (relative to skill root) to export database tables
- Analyze script output and present export results in natural language to the user
- Validate exported data integrity and format correctness
- Report any issues found during the export process

## What it does

- Scans all tables in MWeb's `mainlib.db` SQLite database
- Exports each table's data to JSON format via command line output
- Validates JSON format correctness and data integrity
- Checks record counts and handles empty tables properly
- Reports export statistics and any validation issues
- Handles special characters, Unicode content, and NULL values correctly

## Export Process

### Database Tables Exported
- **`article`** - Document metadata and properties
- **`cat`** - Category/folder structure
- **`cat_article`** - Category-document relationships
- **`tag`** - Tag definitions
- **`tag_article`** - Tag-document relationships
- **`settings`** - Application configuration

### Validation Checks
- **JSON Format**: Ensures all output is valid JSON
- **Record Counts**: Verifies data completeness
- **Empty Tables**: Handles empty tables as valid empty arrays `[]`
- **Data Types**: Preserves INTEGER, TEXT, and NULL values correctly
- **Special Characters**: Properly escapes Unicode and special characters

## When to use

- When you need to analyze MWeb data outside of the application
- Before migrating data to another system or format
- For creating backups of library metadata
- When building integrations that need access to MWeb's data structure
- For debugging data relationships and integrity issues

## Constraints

- Requires `mainlib.db` file to exist in the current directory
- Does not modify the original database (read-only operation)
- Output is command-line only, no files are created
- Depends on SQLite3 being available in the system
- May take time for large databases with many records