# Skills

Follow the Agent Skills specification: <https://agentskills.io/specification>

**Description format:**
- Clearly communicate **what** the skill does and **when to use it**.
- Include **constraints** that explain what the skill should not do or when it does not apply.
- Keep the description concise and actionable without including implementation details.

**Directory structure:**
- Store the skill in a global or project agent skills directory, such as `~/.agents/skills/`, `~/.claude/skills/`, or `~/.codex/skills/`.
- Required structure: `skills/<skill-name>/SKILL.md`.
- The `<skill-name>` directory must contain a `SKILL.md` file.

**Naming conventions:**
- The directory name must match the `name` field in the `SKILL.md` frontmatter.
- Avoid generic names and prefer a specific functional identity.

**User interaction:**
- Prefer the current agent's structured question tool (such as `AskUserQuestion` or `request_user_input`) to let users choose from clear options with labels and descriptions. Avoid free-form prompts.

**User preference configuration (if needed):**
- Name the configuration file `<skill-name>.config.{json|yaml|...}` and place it in the agent configuration directory.
- Follow the proximity principle: project configuration takes precedence over global configuration, such as `.agents/config/`, `.claude/config/`, or `.codex/config/`.
- **Important:** Configuration files containing sensitive or user-specific data must not be committed to version control.
    - Ensure the agent configuration directory is properly ignored in `.gitignore`.
    - When writing skill documentation, remind users to keep configuration files local or private.
    - Use the global configuration directory for personal preferences that should not be shared.
- Document every configuration field and its explicit default value in a schema table (field | type | description | default).
- Explain how to configure each field and provide an example configuration.
- Support command-line overrides: users can override configuration through natural language in their requests.
- Precedence: user parameters > configuration file values > default values.
- When a user provides different preferences while using the skill, use the current agent's structured question tool after all operations are complete to ask whether to save or update the configuration.
- Use the current agent's structured question tool to ask where to save the configuration: "project configuration" or "global configuration".
- When creating project configuration for the first time, ask whether to add it to `.gitignore` (shared with the team vs. local only).
- When updating an existing configuration file, modify only the overridden values and preserve all other settings.

**Documentation requirements:**
- Include example scenarios that use the GWT (Given/When/Then) pattern.
- For complex skills, split lengthy content into the `docs/` directory.
- Reference additional documentation from the main `SKILL.md` file.
