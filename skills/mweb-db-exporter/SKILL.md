---
name: mweb-db-exporter
description: Export MWeb database tables to JSON for analysis and data processing
---

# MWeb database exporter

Use this skill when you need to export MWeb SQLite database tables to JSON for data analysis, backup, or integration with other tools.

## Workflow

- Refer to [database-guide](/docs/mweb/database-guide.md) to understand the database structure
- Run `./script.sh`, relative to the skill root, to export the database tables
- Analyze the script output and present the exported results to the user in natural language
- Verify the completeness and correct format of the exported data
- Report any issues found during export

## Features

- Scan every table in the MWeb `mainlib.db` SQLite database
- Export data from each table as JSON through command-line output
- Validate JSON formatting and data completeness
- Check record counts and handle empty tables correctly
- Report export statistics and validation issues
- Handle special characters, Unicode content, and NULL values correctly

## Export process

### Exported database tables
- **`article`** - Document metadata and properties
- **`cat`** - Category and folder structure
- **`cat_article`** - Category-to-document relationships
- **`tag`** - Tag definitions
- **`tag_article`** - Tag-to-document relationships
- **`settings`** - Application configuration

### Validation checks
- **JSON format**: Ensure all output is valid JSON
- **Record count**: Verify data completeness
- **Empty tables**: Handle empty tables as valid empty arrays, `[]`
- **Data types**: Preserve INTEGER, TEXT, and NULL values correctly
- **Special characters**: Escape Unicode and special characters correctly

## Use cases

- When analyzing MWeb data outside the application
- Before migrating data to another system or format
- When creating backups of document-library metadata
- When building integrations that need access to MWeb data structures
- When debugging data relationships and integrity issues

## Constraints

- Require a `mainlib.db` file in the current directory
- Do not modify the original database; operations are read-only
- Output only to the command line; do not create files
- Require SQLite3 to be available on the system
- Large databases with many records may take longer to process
