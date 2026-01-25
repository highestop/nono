---
name: commit
description: This skill should be used when the user asks to "commit", "create commit", "git commit", mentions "commit changes", needs help with git commits and conventional commit messages.
allowed-tools:
  - "Bash(git *)"
  - "Bash(gh pr create*)"
---

# Git Commit Skill

## Configuration API

The skill reads configuration from `.claude/config/commit.config.json` using a proximity-based search:

1. **Project Config**: `.claude/config/commit.config.json` relative to current working directory
2. **Global Config**: `~/.claude/config/commit.config.json` if project config not found

You can choose whether to commit the project config file to share team conventions or keep it local by adding to .gitignore.

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

### Command-line Configuration Overrides

Users can override any configuration setting directly in their request using natural language. The skill should intelligently parse the user's intent and map it to appropriate configuration overrides.

**Priority Order** (highest to lowest):
1. **User arguments** - Settings inferred from current request
2. **Config file values** - Project config or global configuration
3. **Default values** - System defaults

**Semantic Parsing Guidelines**:
- Parse user intent rather than matching exact phrases
- Look for indicators of configuration preferences in the request
- Map natural language expressions to configuration field overrides
- Support various ways users might express the same preference

**Common Override Patterns**:
| Configuration Field | Natural Language Indicators | Example Expressions |
|---------------------|----------------------------|-------------------|
| `strategy` | Branch strategy preferences | "use feature branch", "commit to main", "create branch" |
| `autoPush` | Push behavior preferences | "don't push", "without push", "and push", "skip push" |
| `createPullRequest` | PR creation preferences | "create PR", "make pull request", "no PR", "skip PR" |
| `splitCommits` | Commit splitting preferences | "single commit", "one commit", "split commits", "separate" |
| `coAuthor` | Co-author preferences | "no co-author", "without co-author", "skip co-author" |

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

- **Config locations**:
  - Project Config: `.claude/config/commit.config.json` (current working directory)
  - Global Config: `~/.claude/config/commit.config.json`
- **Search priority**: Project config takes precedence over global config
- **Cowork sharing**: Choose whether to commit project config file for team conventions or add to .gitignore for local-only settings

## Workflow

Execute the following steps when this skill is triggered:

### 1. Load Configuration and Parse Arguments

- Analyze user input to identify configuration intent and preferences
- Extract configuration overrides from natural language expressions
- Search for config file in order:
  1. `.claude/config/commit.config.json` (current working directory)
  2. `~/.claude/config/commit.config.json` (global config)
- Merge configurations with priority order (highest to lowest):
  1. **User arguments** (parsed from current request)
  2. **Config file values** (project config or global config)
  3. **Default values**
- Create `.claude/config/` directory if it doesn't exist when saving new config

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

- Check if current repository is a fork by looking for `upstream` remote using `git remote -v`
- If fork detected (upstream remote exists):
  - **Force feature branch strategy** regardless of config (required for open source contribution)
  - Create new feature branch with format `<change-type>/<short-description>`
- If not a fork:
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
  - If repository is a fork (determined in step 3):
    - Create PR to `upstream/main` using `gh pr create --repo <upstream-owner>/<upstream-repo>`
    - Extract upstream owner/repo from upstream remote URL
  - If not a fork:
    - Create PR to `origin/main` using `gh pr create`
  - Return PR URL to user

### 7. Handle Configuration Updates

- If user provided configuration overrides during this session, use AskUserQuestion tool:
  - Question: "Save these settings for future use?"
  - Options: ["Yes, save settings", "No, use only for this commit"]
- If user chooses to save, use AskUserQuestion tool:
  - Question: "Where should these settings be saved?"
  - Options: ["Project Config (current project only)", "Global Config (all projects)"]
- When creating project config for the first time, use AskUserQuestion tool:
  - Question: "Should the config file be added to .gitignore?"
  - Options: ["Yes, keep config local only", "No, share with team"]
- Update existing config file with only the overridden values, keeping other settings unchanged

## Critical Rules

- Use TaskCreate to track all steps at the beginning and update status throughout
- Provide clear options for user selection rather than free text input
- If any new changes appear during execution, restart the entire commit workflow from beginning
- Commit messages must be in English using Angular Conventional Commit format
- Handle git errors gracefully with clear error messages



## Examples

### Example 1: Default behavior (no config file)

**Trigger**: "Help me commit my changes"

**Scenario**:
- No `.claude/config/commit.config.json` exists (neither project config nor global config)
- Modified files: `src/auth.js`, `tests/auth.test.js`
- All changes related to fixing login validation

**Expected flow**:
1. Load default configuration
2. Analyze changes: single logical group (auth fix + tests)
3. Auto-stage files and commit directly to main branch
4. Create commit: `fix(auth): resolve login validation logic`
5. Push to remote

### Example 2: Feature branch strategy

**Configuration** (`.claude/config/commit.config.json`):
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

**Configuration** (`.claude/config/commit.config.json`):
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

**Configuration** (`.claude/config/commit.config.json`):
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

**Configuration** (`.claude/config/commit.config.json`):
```json
{
  "strategy": "feature",
  "createPullRequest": true
}
```

**Expected flow**:
1. Create feature branch
2. Commit and push changes
3. Check remotes using `git remote -v` and confirm no `upstream` remote exists
4. Create PR to origin repository using `gh pr create`
5. Return PR URL to user

### Example 6: Disable co-author tag

**Configuration** (`.claude/config/commit.config.json`):
```json
{
  "coAuthor": false
}
```

**Expected flow**:
1. Create commit without `Co-authored-by: Claude <noreply@anthropic.com>` line
2. Commit message contains only the conventional commit format

### Example 7: Custom commit types

**Configuration** (`.claude/config/commit.config.json`):
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

**Configuration** (`.claude/config/commit.config.json`):
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

### Example 9: Command-line overrides with config save

**Trigger**: "commit with feature branch and create PR"

**Scenario**:
- User has existing config: `{"strategy": "main", "createPullRequest": false}`
- User wants to override for this commit

**Expected flow**:
1. Analyze user intent: infer strategy="feature" from "with feature branch", createPullRequest=true from "create PR"
2. Apply overridden values for this commit
3. Create feature branch and PR as requested
4. Ask via AskUserQuestion: "Save these settings for future use?" with options ["Yes, save settings", "No, use only for this commit"]
5. If yes, ask via AskUserQuestion: "Where should these settings be saved?" with options ["Project Config (current project only)", "Global Config (all projects)"]
6. Update config file with new values

### Example 10: Command-line override without existing config

**Trigger**: "commit without push"

**Scenario**:
- No existing config file
- User wants to commit locally only

**Expected flow**:
1. Analyze user intent: infer autoPush=false from "without push"
2. Apply defaults with override: autoPush=false
3. Create commit but don't push to remote
4. Ask via AskUserQuestion: "Save these settings for future use?" with options ["Yes, save settings", "No, use only for this commit"]
5. If yes, ask via AskUserQuestion: "Where should these settings be saved?" with options ["Project Config (current project only)", "Global Config (all projects)"]
6. Create new config file with the override
7. If creating project config for first time, ask via AskUserQuestion: "Should the config file be added to .gitignore?" with options ["Yes, keep config local only", "No, share with team"]

### Example 11: Fork project (forced feature branch)

**Trigger**: "commit"

**Configuration** (`.claude/config/commit.config.json`):
```json
{
  "strategy": "main",
  "createPullRequest": true
}
```

**Scenario**:
- Repository is a fork (has upstream remote pointing to original repo)
- User configured strategy as "main" but this will be overridden
- Modified files: `src/feature.js`, `tests/feature.test.js`

**Expected flow**:
1. Check remotes using `git remote -v` and detect `upstream` remote
2. **Override strategy to "feature"** (fork projects require feature branches)
3. Create feature branch: `feat/add-new-feature`
4. Commit changes to the feature branch
5. Push feature branch to origin (user's fork)
6. Extract upstream owner/repo from upstream remote URL
7. Create PR to upstream repository using `gh pr create --repo <upstream-owner>/<upstream-repo>`
8. Return PR URL pointing to upstream repository

### Example 12: Fork project with feature strategy

**Trigger**: "commit with create PR"

**Configuration** (`.claude/config/commit.config.json`):
```json
{
  "strategy": "feature",
  "createPullRequest": true
}
```

**Scenario**:
- Repository is a fork (has upstream remote pointing to original repo)
- User already configured feature strategy (aligned with fork requirements)
- Modified files: `docs/README.md`

**Expected flow**:
1. Check remotes and detect fork, confirm feature strategy is appropriate
2. Create feature branch: `docs/update-readme`
3. Commit changes to the feature branch
4. Push feature branch to origin (user's fork)
5. Create PR to upstream repository
6. Return PR URL pointing to upstream repository
