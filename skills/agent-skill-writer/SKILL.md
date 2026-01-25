---
name: agent-skill-writer
description: Use this skill when writing/editing skills
---

**Description Format:**
- Use directive format like: "Use this skill to/when..."
- Clearly convey **what** the skill does and **when** to use it
- Include **constraints** about what it shouldn't do or when not to use it
- Keep it concise and actionable

**Naming Convention:**
- Name skills with a role or identity (e.g., "agent-docs-writter", "git-committer", "budget-formatter")
- Directory name must match the `name` field in the SKILL.md frontmatter
- Avoid generic names, prefer specific functional identities

**Examples of good descriptions:**
- "Use this skill when committing code changes to ensure conventional commit format"
- "Use this skill to format CSV budget exports, but not for other file types"
- "Use this skill when writing agent markdown files (skills, rules, configs, etc.)"
