---
name: mweb-database-guide
description: Provides knowledge about MWeb's SQLite database schema and table relationships
---

# MWeb Database Guide

Use this skill when you need to understand MWeb's internal database structure for querying, analyzing, or building tools that interact with MWeb data.

## What it provides

- Knowledge of MWeb's `mainlib.db` SQLite database schema
- Understanding of table relationships and data flow
- Field definitions and data types for key tables
- Query patterns and common use cases

## Database Overview

MWeb stores all library data in a SQLite database file named `mainlib.db` located in the library root directory.

### Core Tables

#### `article` - Document Metadata
- **Purpose**: Stores metadata for all documents in the library
- **Key Fields**:
  - `id` - Primary key, auto-increment
  - `uuid` - Unique identifier for the document
  - `type` - Document type (markdown, etc.)
  - `state` - Document state (published, draft, etc.)
  - `docName` - Document filename without extension (often NULL/empty)
  - `dateAdd` - Document creation timestamp
  - `dateModif` - Last modification timestamp
  - `dateArt` - Article date timestamp

#### `cat` - Categories/Folders Structure
- **Purpose**: Defines the hierarchical folder structure
- **Key Fields**:
  - `id` - Primary key, category identifier
  - `name` - Category/folder name
  - `pid` - Parent category UUID (for hierarchy, 0 = root category)
  - `siteName` - Associated site name
  - `siteURL` - Associated site URL

#### `cat_article` - Category-Document Relationships
- **Purpose**: Many-to-many relationship between categories and articles
- **Key Fields**:
  - `rid` - Foreign key to `cat.uuid`
  - `aid` - Foreign key to `article.uuid`

#### `tag` - Tag Definitions
- **Purpose**: Stores all available tags
- **Key Fields**:
  - `id` - Primary key, tag identifier
  - `name` - Tag name/label
  - `uuid` - Unique identifier for the tag

#### `tag_article` - Tag-Document Relationships
- **Purpose**: Many-to-many relationship between tags and articles
- **Key Fields**:
  - `rid` - Foreign key to `tag.uuid`
  - `aid` - Foreign key to `article.uuid`

#### `settings` - Application Configuration
- **Purpose**: Stores MWeb application settings and preferences
- **Key Fields**:
  - Configuration key-value pairs for application behavior

## Common Query Patterns

### Find documents in a specific category
```sql
SELECT a.* FROM article a
JOIN cat_article ca ON a.uuid = ca.aid
JOIN cat c ON ca.rid = c.uuid
WHERE c.name = 'CategoryName';
```

### Find all categories for a document
```sql
SELECT c.name FROM cat c
JOIN cat_article ca ON c.uuid = ca.rid
WHERE ca.aid = ?;  -- Use article.uuid here
```

### Find all tags for a document
```sql
SELECT t.name FROM tag t
JOIN tag_article ta ON t.uuid = ta.rid
WHERE ta.aid = ?;  -- Use article.uuid here
```

### Get category hierarchy
```sql
WITH RECURSIVE category_tree AS (
  SELECT id, uuid, name, pid, 0 as level
  FROM cat WHERE pid = 0
  UNION ALL
  SELECT c.id, c.uuid, c.name, c.pid, ct.level + 1
  FROM cat c
  JOIN category_tree ct ON c.pid = ct.uuid
)
SELECT * FROM category_tree ORDER BY level, name;
```

## When to use

- Before building tools that need to query MWeb data
- When analyzing document metadata and relationships
- Before implementing category or tag management features
- When understanding MWeb's data model for integration purposes

## Constraints

- This is knowledge-only skill - it doesn't perform database operations
- Database schema may vary between MWeb versions
- Always backup the database before making modifications
- Direct database modifications may affect MWeb application stability