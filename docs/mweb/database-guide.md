> Use this guide when you need to understand MWeb's internal database structure for querying, analysis, or building tools that interact with MWeb data.

## Fundamentals

- Schema knowledge for the MWeb `mainlib.db` SQLite database
- Relationships and data flow between tables
- Field definitions and data types for key tables
- Query patterns and common use cases

## Database overview

MWeb stores all document-library data in a SQLite database file named `mainlib.db` at the root of the document library.

### Core tables

#### `article` - Document metadata
- **Purpose**: Store metadata for all documents in the library
- **Key fields**:
  - `id` - Auto-incrementing primary key
  - `uuid` - Unique document identifier
  - `type` - Document type, such as Markdown
  - `state` - Document state, such as published or draft
  - `docName` - Document filename without the extension, usually NULL or empty
  - `dateAdd` - Document creation timestamp
  - `dateModif` - Last modification timestamp
  - `dateArt` - Article date timestamp

#### `cat` - Category and folder structure
- **Purpose**: Define the hierarchical folder structure
- **Key fields**:
  - `id` - Primary key and category identifier
  - `name` - Category or folder name
  - `pid` - Parent category UUID, used for hierarchy; 0 represents the root category
  - `siteName` - Associated site name
  - `siteURL` - Associated site URL

#### `cat_article` - Category-to-document relationships
- **Purpose**: Represent the many-to-many relationship between categories and articles
- **Key fields**:
  - `rid` - Foreign key referencing `cat.uuid`
  - `aid` - Foreign key referencing `article.uuid`

#### `tag` - Tag definitions
- **Purpose**: Store all available tags
- **Key fields**:
  - `id` - Primary key and tag identifier
  - `name` - Tag name
  - `uuid` - Unique tag identifier

#### `tag_article` - Tag-to-document relationships
- **Purpose**: Represent the many-to-many relationship between tags and articles
- **Key fields**:
  - `rid` - Foreign key referencing `tag.uuid`
  - `aid` - Foreign key referencing `article.uuid`

#### `settings` - Application configuration
- **Purpose**: Store MWeb application settings and preferences
- **Key fields**:
  - Configuration key-value pairs for application behavior

## Common query patterns

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

### Retrieve the category hierarchy
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

## Use cases

- Before building tools that query MWeb data
- When analyzing document metadata and relationships
- Before implementing category or tag management features
- When understanding the MWeb data model for integration purposes

## Constraints

- This is a knowledge-only guide and does not perform database operations
- The database schema may vary between MWeb versions
- Always back up the database before making changes
- Direct database modifications may affect the stability of the MWeb application
