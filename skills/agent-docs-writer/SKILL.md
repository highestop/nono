---
name: agent-docs-writer
description: Use this skill when writing/editing any agent markdown files (skills, rules, configs, etc.)
---

**Privacy Protection:**
- **NEVER** include absolute paths that expose system path with username
- Prefer `~/` or `$HOME` notation for home directory references

**Content Standards:**
- Use English as default language, unless explicitly told to use other language
- Use `<angle-bracket>` notation for placeholders and variables
- Use `inline code` syntax for technical terms, file names, and command names
- Keep documentation as concise as possible to minimize context usage
- Use simple lists instead of headers when structure is straightforward
- Write examples inline when they can be explained clearly without separate sections or files
- Avoid unnecessary structural complexity that doesn't add clarity