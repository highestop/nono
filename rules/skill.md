# Skills

Follow the Agent Skills specification: <https://agentskills.io/specification>

**Description format:**
- Clearly state **what** the skill does and **when** to use it
- Include **constraints** that explain what the skill should not do or when it does not apply
- Keep it concise and actionable; do not include implementation details in the description

**Directory structure:**
- Place the skill in a global or project agent skills directory, such as `~/.agents/skills/`, `~/.claude/skills/`, or `~/.codex/skills/`
- Required structure: `skills/<skill-name>/SKILL.md`
- The `<skill-name>` directory must contain a `SKILL.md` file

**Naming conventions:**
- The directory name must match the `name` field in the `SKILL.md` frontmatter
- Avoid generic names; prefer a specific functional identity

**User interaction:**
- Prefer structured question tools provided by the current agent, such as `AskUserQuestion` or `request_user_input`, to let the user choose from clearly labeled and described options instead of using free-form prompts

**User preference configuration, if needed:**
- Name the configuration file `<skill-name>.config.{json|yaml|...}` and place it in an agent configuration directory
- Follow proximity precedence: project configuration overrides global configuration, for example `.agents/config/`, `.claude/config/`, or `.codex/config/`
- **Important**: Do not commit configuration files containing sensitive or user-specific data to version control
  - Ensure agent configuration directories are properly ignored in `.gitignore`
  - When writing skill documentation, remind users to keep configuration files local or private
  - Store personal preferences that should not be shared in a global configuration directory
- Document every configuration field and its explicit default value in a schema table: Field | Type | Description | Default
- Explain how to configure each field and provide an example configuration
- Support request-level overrides: users may override configuration through natural-language requests
- Precedence: user parameters > configuration file values > defaults
- When a user provides different preferences while using the skill, use the current agent's structured question tool after all operations are complete to ask whether to save or update the configuration
- Use the current agent's structured question tool to ask where to save it: "Project configuration" or "Global configuration"
- When creating project configuration for the first time, ask whether to add it to `.gitignore`: team-shared or local only
- When updating an existing configuration file, modify only the overridden values and preserve all other settings

**Documentation requirements:**
- Include example scenarios using the GWT (Given/When/Then) pattern
- For complex skills, split lengthy content into the `docs/` directory
- Reference additional documents from the main `SKILL.md` file
