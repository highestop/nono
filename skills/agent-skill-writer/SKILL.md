---
name: agent-skill-writer
description: Use this skill when writing/editing skills
---

Follow the Agent Skills specification: <https://agentskills.io/specification>

**Description Format:**
- Use directive format like: "Use this skill to/when..."
- Clearly convey **what** the skill does and **when** to use it
- Include **constraints** about what it shouldn't do or when not to use it
- Keep it concise and actionable

**Directory Structure:**
- Must be placed in global or project `.claude/skills/` directory
- Required structure: `skills/<skill-name>/SKILL.md`
- The `<skill-name>` directory must contain `SKILL.md` file

**Naming Convention:**
- Name skills with a role or identity (e.g., "agent-docs-writer", "git-committer", "budget-formatter")
- Directory name must match the `name` field in the SKILL.md frontmatter
- Avoid generic names, prefer specific functional identities

**User Interaction:**
- Must use `AskUserQuestion` tool for user choices instead of free text prompts
- Provide clear options with labels and descriptions
- Prefer button-based selections over text input

**User Preference Configuration (if needed):**
- Config files should be named `<skill-name>.config.{json|yaml|...}` in `.claude/config/` directory
- Use proximity principle: project config (`.claude/config/`) takes precedence over global (`~/.claude/config/`)
- **IMPORTANT**: Configuration files containing sensitive or user-specific data should NOT be committed to version control
  - Ensure `.claude/config/` directory is properly ignored in `.gitignore`
  - When documenting skills, remind users that config files are meant to be local/private
  - Use global config (`~/.claude/config/`) for personal preferences that shouldn't be shared
- Must document all config fields with clear default values in a schema table (Field | Type | Description | Default)
- Must explain how to configure each field and provide example configurations
- Support command-line overrides: users can override config via natural language in their requests
- Priority order: User arguments > Config file values > Default values
- When user provides different preferences when using skill, ask via `AskUserQuestion` whether to save/modify config after everything finished
- Use `AskUserQuestion` to ask where to save: "Project Config" vs "Global Config"
- When creating project config for first time, ask whether to add to .gitignore (team sharing vs local-only)
- Update existing config files with only overridden values, keep other settings unchanged

**Documentation Requirements:**
- Must include example scenarios using GWT (Given/When/Then) patterns
- For complex skills, split long content into `docs/` directory
- Reference additional documentation from main SKILL.md file

**Examples of good descriptions:**
- "Use this skill when committing code changes to ensure conventional commit format"
- "Use this skill to format CSV budget exports, but not for other file types"
- "Use this skill when writing agent markdown files (skills, rules, configs, etc.)"
