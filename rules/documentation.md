---
description: Universal documentation standards for all markdown files across Claude Code project
paths: ["**/*.md"]
---

- Use angle bracket notation for all placeholders/variables: `<variable-name>`
- **NEVER** include absolute paths that expose usernames or system details. Use relative paths from a clearly defined base directory
- Keep documentation as concise as possible to minimize context usage. For examples:
  - Use simple lists instead of headers when structure is straightforward
  - Write examples inline when they can be explained clearly without separate sections or files
  - Avoid unnecessary structural complexity that doesn't add clarity
