---
name: agent-docs-writer
description: Use this skill when writing/editing any agent markdown files (skills, rules, configs, etc.)
---

- **NEVER** include absolute paths that expose system path with username. Use relative paths from a clearly defined base directory
- Use `<angle-bracket>` notation for placeholders, variables
- Use `inline code` syntax for technical terms, file names, and command names
- Keep documentation as concise as possible to minimize context usage. For examples:
  - Use simple lists instead of headers when structure is straightforward
  - Write examples inline when they can be explained clearly without separate sections or files
  - Avoid unnecessary structural complexity that doesn't add clarity