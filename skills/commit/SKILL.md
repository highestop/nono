---
name: commit
description: This skill should be used when the user asks to "commit", "create commit", "git commit", mentions "commit changes", needs help with git commits and conventional commit messages, or wants to "reset commit config", "change commit settings", "configure commit behavior".
allowed-tools:
  - "Bash(git *)"
  - "Bash(gh pr create*)"
---

# Git Commit Skill

## Configuration API

The skill reads configuration from `skills/commit/config.json` relative to the current working directory. You can choose whether to commit this file to share team conventions or keep it local by adding to .gitignore.

### Configuration Schema

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `strategy` | `"main"` \| `"feature"` | Commit strategy: commit directly to main branch or create feature branch | `"main"` |
| `splitCommits` | `boolean` | Split unrelated changes into separate commits | `true` |
| `autoPush` | `boolean` | Automatically push commits to remote | `true` |
| `createPullRequest` | `boolean` | Create PR when using feature branch strategy | `false` |
| `coAuthor` | `boolean` | Add Claude co-author tag to commits | `true` |
| `types` | `string[]` | Allowed commit types | `["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]` |
| `scopes` | `string[]` | Allowed scopes for this project | `["rule", "skill", "command", "plugin"]` |

### Example Configuration

```json
{
  "strategy": "feature",
  "splitCommits": true,
  "autoPush": true,
  "createPullRequest": true,
  "coAuthor": false,
  "types": ["feat", "fix", "docs", "refactor", "test"],
  "scopes": ["api", "ui", "auth"]
}
```

### Configuration Management

- **Reset configuration**: When user mentions "reset", "clear", "override", or "change settings", delete existing config file and use defaults
- **Config location**: `skills/commit/config.json` in current working directory
- **Team sharing**: Choose whether to commit config file for team conventions or add to .gitignore for local-only settings

## Workflow

Execute the following steps when this skill is triggered:

### 1. Load Configuration

- Check if `skills/commit/config.json` exists in current directory
- If exists, merge with defaults (config values override defaults)
- If not exists or if reset requested, use default values
- Create `skills/commit/` directory if it doesn't exist

### 2. Analyze Changes

- Verify current directory is a git repository using `git status`
- Run `git diff` and `git diff --cached` to analyze changes
- Categorize changes by:
  - File type (source code, docs, tests, config)
  - Change type based on `types` config
- Determine scope automatically:
  - Add scope for Claude Agent files (rule, skill, command, plugin), no scope for others
  - Use scopes from `scopes` config when applicable
- If `splitCommits` is true and multiple unrelated changes detected, split into separate commits

### 3. Execute Branch Strategy

- If `strategy` is `"main"`: Stay on current branch
- If `strategy` is `"feature"`: Create new feature branch with format `<change-type>/<short-description>`

### 4. Stage Files

- Automatically stage all modified files using `git add`

### 5. Create Commits

For each commit group:

- Ensure git author and email are properly configured
- Generate Angular Conventional Commit message:
  - Format: `<change-type>(<scope-if-configured>): <commit-title>`
  - Add body if needed for complex changes
  - Add `Co-authored-by: Claude <noreply@anthropic.com>` if `coAuthor` is true
- Create commit using `git commit`

### 6. Push and PR

- If `autoPush` is true: Push commits to remote using `git push`
- If on feature branch and `createPullRequest` is true:
  - Create PR using `gh pr create`
  - Return PR URL to user

### 7. Handle Configuration File

- Check if config file should be version controlled or ignored
- If this is the first time creating config, ask user whether to add to .gitignore

## Critical Rules

- Use TaskCreate to track all steps at the beginning and update status throughout
- If any new file changes appear at ANY point during execution, restart the entire commit workflow from beginning
- Execute automatically without user confirmation (removed interactive prompts)
- Commit messages in English
- Handle git errors gracefully with clear error messages
- Never commit the config.json file itself

## Examples

### Example 1: Default behavior (no config file)

**Trigger**: "Help me commit my changes"

**Scenario**:
- No `skills/commit/config.json` exists
- Modified files: `src/auth.js`, `tests/auth.test.js`
- All changes related to fixing login validation

**Expected flow**:
1. Load default configuration
2. Analyze changes: single logical group (auth fix + tests)
3. Auto-stage files and commit directly to main branch
4. Create commit: `fix(auth): resolve login validation logic`
5. Push to remote

### Example 2: Feature branch strategy

**Configuration** (`skills/commit/config.json`):
```json
{
  "strategy": "feature"
}
```

**Expected flow**:
1. Create feature branch: `fix/auth-validation`
2. Commit changes to the feature branch
3. Push feature branch to remote

### Example 3: Disable commit splitting

**Configuration** (`skills/commit/config.json`):
```json
{
  "splitCommits": false
}
```

**Scenario**:
- Modified files: `README.md`, `src/utils.js`, `package.json`
- Multiple unrelated changes

**Expected flow**:
1. Treat all changes as single commit group
2. Create one commit: `feat: update docs, add utility, and upgrade deps`

### Example 4: Disable auto-push

**Configuration** (`skills/commit/config.json`):
```json
{
  "autoPush": false
}
```

**Expected flow**:
1. Create commits locally
2. Do NOT push to remote automatically
3. User must manually push later

### Example 5: Enable automatic PR creation

**Configuration** (`skills/commit/config.json`):
```json
{
  "strategy": "feature",
  "createPullRequest": true
}
```

**Expected flow**:
1. Create feature branch
2. Commit and push changes
3. Automatically create PR using `gh pr create`
4. Return PR URL to user

### Example 6: Disable co-author tag

**Configuration** (`skills/commit/config.json`):
```json
{
  "coAuthor": false
}
```

**Expected flow**:
1. Create commit without `Co-authored-by: Claude <noreply@anthropic.com>` line
2. Commit message contains only the conventional commit format

### Example 7: Custom commit types

**Configuration** (`skills/commit/config.json`):
```json
{
  "types": ["feat", "fix", "docs", "refactor"]
}
```

**Expected flow**:
1. Only use specified commit types when analyzing changes
2. Categorize changes using the limited type set
3. Other standard types like "chore", "test" will not be used

### Example 8: Custom scopes

**Configuration** (`skills/commit/config.json`):
```json
{
  "scopes": ["api", "ui", "auth", "database"]
}
```

**Expected flow**:
1. Use custom scopes when auto-detecting scope for changes
2. For files matching patterns, apply appropriate scope:
   - API-related files → `feat(api): ...`
   - UI components → `feat(ui): ...`
   - Auth modules → `fix(auth): ...`
   - Database files → `chore(database): ...`

### Example 9: Configuration reset

**Trigger**: "Help me commit and reset my commit preferences"

**Scenario**:
- Existing config file with custom settings
- User wants to reset to defaults

**Expected flow**:
1. Detect reset keywords: "reset my commit preferences"
2. Delete existing `skills/commit/config.json`
3. Use default configuration for this commit
4. Continue with default behavior (main branch strategy)
