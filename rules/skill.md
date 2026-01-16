---
description: Core requirements and standards for creating and maintaining Claude Code skills
paths: ["skills/**/*"]
---

## 1. Target Audience

- Skills are **exclusively** written for Claude's execution, not user documentation
- Focus solely on actionable execution steps and technical specifications

## 2. Privacy Protection

- **NEVER** include absolute paths that expose usernames or system details
- Use relative paths from Claude root directory when referencing skill files

## 3. File Organization

### Required Structure

```
skills/
└── <skill-name>/
    ├── SKILL.md                    # Main skill definition (required)
    ├── configs/                    # Configuration directory (if needed)
    │   ├── preferences.json        # User preferences (shared)
    |   └── preferences.local.json  # User preferences (local, git-ignored)
    └── docs/                       # Additional documentation (for complex skills)
        └── examples.md             # Example scenarios and test cases
```

### Directory Rules

- **Skill root directory**: MUST contain ONLY the `SKILL.md` file
- **All other files**: MUST be placed in subdirectories
- **Single version only**: Each skill can only have one version - no multi-version support

## 4. User Preferences

### Dual Preference File Strategy

- **Two-file approach**: Create both `configs/preferences.json` and `configs/preferences.local.json`
- **Cross-device sharing**: `preferences.json` can be committed for device synchronization
- **Local-only settings**: `preferences.local.json` is git-ignored for machine-specific preferences

### Read Priority

- Always check both files when reading preferences
- **Priority order**: `preferences.local.json` overrides `preferences.json`
- Merge settings with local taking precedence over shared

### Write Strategy

- **Ask user choice**: When writing preferences, ask user whether to save as shared or local-only
- **Shared option**: Save to `preferences.json` for cross-device sync
- **Local option**: Save to `preferences.local.json` for current machine only

### Preference Reset Capability

- **Override existing preferences**: When user explicitly mentions "clear", "reset", "override", or "change settings", ignore existing preferences and re-prompt for new settings
- **Trigger keywords**: Watch for phrases like "reset preferences", "clear settings", "change my preference", "override setting"
- **Force re-configuration**: Always ask for both preference value and storage location when reset is requested

## 5. Complex Skills

- **Examples**: Complex skills MUST include example scenarios for understanding and validation. Examples can be writen in GWT (Given/Scenario, When/Trigger, Then/Expected) patterns.
- **Documentation Splitting**: If SKILL.md becomes too long, split content into separate markdown files in `docs/` directory and reference them from the main file
