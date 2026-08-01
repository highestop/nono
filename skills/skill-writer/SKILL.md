---
name: skill-writer
description: Create and revise Agent Skills-compliant skills, including metadata, directory structure, interaction design, preference configuration, and examples. Use when creating, converting, or editing a skill; do not use for general documentation, rules, or non-skill agent files.
---

# Skill Writer

Follow the Agent Skills specification: <https://agentskills.io/specification>.

## Workflow

1. Clarify the skill's purpose, trigger scenarios, constraints, and target skills directory. Prefer a structured question tool when the user must choose between known options.
2. Choose a specific functional name and create `skills/<skill-name>/SKILL.md` in the selected global or project agent skills directory.
3. Write or revise the frontmatter and instructions using the requirements below.
4. Add GWT examples and any required preference configuration guidance.
5. Review the completed skill against the specification, verify all referenced files, and validate it with an available skill validator.

## Description

- Clearly state what the skill does and when to use it.
- Include constraints that explain what the skill should not do or when it does not apply.
- Keep the description concise and actionable; omit implementation details.

## Directory and naming

- Place the skill in a global or project agent skills directory, such as `~/.agents/skills/`, `~/.claude/skills/`, or `~/.codex/skills/`.
- Use the required structure `skills/<skill-name>/SKILL.md`.
- Ensure the `<skill-name>` directory contains `SKILL.md`.
- Match the directory name to the `name` field in the `SKILL.md` frontmatter.
- Avoid generic names; prefer a specific functional identity.

## User interaction

- Prefer structured question tools provided by the current agent, such as `AskUserQuestion` or `request_user_input`, when users must choose between known options.
- Present clearly labeled and described choices instead of relying on free-form prompts.

## User preference configuration

Apply these requirements only when the skill needs persistent user preferences:

- Name the configuration file `<skill-name>.config.{json|yaml|...}` and place it in an agent configuration directory.
- Follow proximity precedence: project configuration overrides global configuration, for example `.agents/config/`, `.claude/config/`, or `.codex/config/`.
- Do not commit configuration files containing sensitive or user-specific data.
  - Ensure agent configuration directories are properly ignored in `.gitignore`.
  - Remind users to keep configuration files local or private.
  - Store personal preferences that should not be shared in a global configuration directory.
- Document every configuration field and its explicit default value in a schema table: Field | Type | Description | Default.
- Explain how to configure every field and provide an example configuration.
- Support request-level overrides through natural-language requests.
- Apply precedence in this order: user parameters > configuration file values > defaults.
- When a user supplies different preferences while using the skill, complete the requested operations before using a structured question tool to ask whether to save or update the configuration.
- Ask whether to save preferences as project or global configuration.
- Before creating project configuration for the first time, ask whether it should be added to `.gitignore` for local-only use or kept available for team sharing.
- When updating an existing configuration file, modify only the overridden values and preserve all other settings.

## Documentation

- Include example scenarios using the Given/When/Then pattern.
- For complex skills, split lengthy content into the `docs/` directory and link every additional document directly from the main `SKILL.md`.

## Example scenarios

### Create a skill

- **Given:** A user describes a repeatable workflow and the requests that should trigger it.
- **When:** Use `skill-writer` to create the skill.
- **Then:** Create a correctly named skill directory with compliant frontmatter, focused instructions, relevant constraints, and GWT examples.

### Convert rules into a skill

- **Given:** A repository contains a rules document that should become an invocable skill.
- **When:** Use `skill-writer` to convert the document.
- **Then:** Preserve its substantive requirements, add skill metadata and an actionable workflow, update references, and remove the superseded rules file when requested.
