---
name: commit
description: This skill should be used when the user asks to "commit", "create commit", "git commit", mentions "commit changes", needs help with git commits and conventional commit messages, or wants to "reset commit preferences", "change commit settings", "override commit preference".
---

# Git Commit Skill

## Workflow

Execute the following steps when this skill is triggered:

### 1. Analyze Changes

- Verify current directory is a git repository using `git status`
- Run `git diff` and `git diff --cached` to analyze changes
- Categorize changes by:
  - File type (source code, docs, tests, config)
  - Change type (feat, fix, docs, style, refactor, perf, test, chore)
- If multiple unrelated changes detected, suggest splitting into separate commits
- Present analysis and use AskUserQuestion tool to confirm: "Proceed with commit?"

### 2. Load User Preferences

- Get remote repository identifier using `git remote get-url origin`
- Extract owner/repo from URL using regex (e.g., "owner/repo" from https://github.com/owner/repo)
- If no remote exists, ABORT the process
- Check if user request contains reset keywords: "reset", "clear", "override", "change settings"
- Read preferences from both `skills/commit/configs/preferences.json` and `skills/commit/configs/preferences.local.json`
- Merge preferences with local file taking priority over shared file
- Create empty `{}` files if they don't exist (in `skills/commit/configs/` directory)
- **If reset requested**: Skip existing preference check and force re-configuration
- **If no reset and no existing preference**: Use AskUserQuestion tool with options:
  - Option 1: "Direct commit to main branch" → save as "main"
  - Option 2: "Create feature branch and PR later" → save as "feature"
- Use AskUserQuestion tool to ask: "Save preference as shared (cross-device) or local-only?"
  - Option 1: "Shared (cross-device sync)"
  - Option 2: "Local-only (this machine)"
- Save user choice to selected file with repo identifier as key

### 3. Execute Branch Strategy

- If preference is "main": Stay on current branch
- If preference is "feature": Create new feature branch with format `<change-type>/<short-description>` (e.g., "feature/auth-login-fix")

### 4. Create Commits

For each commit group:

- Ensure git author and email are properly configured
- Stage relevant files using `git add`
- Generate Angular Conventional Commit message:
  - Format: `<change-type>(<scope-if-needed>): <commit-title>`
  - Add body if needed for complex changes
  - Add `Co-authored-by: Claude <noreply@anthropic.com>`
- Create commit using `git commit`

### 5. Push and PR

- Push commits to remote using `git push`
- If on feature branch:
  - Create PR using `gh pr create`
  - Return PR URL to user

## Configuration File Format

### Shared Preferences

`skills/commit/configs/preferences.json` (committed, cross-device sync):

```json
{
  "owner/repo": "main|feature"
}
```

### Local Preferences

`skills/commit/configs/preferences.local.json` (git-ignored, machine-specific):

```json
{
  "owner/repo": "main|feature"
}
```

### Priority Rules

- Settings in `preferences.local.json` override those in `preferences.json`
- Both files are checked during preference loading
- User chooses which file to write to when saving new preferences

## Critical Rules

- Use TodoWrite to track all steps at the beginning and update status throughout
- If any new file changes appear at ANY point during execution, restart the entire commit workflow from beginning
- Use AskUserQuestion tool for all user interactions instead of free text prompts
- Commit messages in English
- Handle git errors gracefully with clear error messages

## Examples

### Example 1: First-time user with single logical change

**Trigger**: "Help me commit my changes"

**Scenario**:

- New repository (no preferences saved)
- Modified files: `src/auth.js`, `tests/auth.test.js`
- All changes related to fixing login validation

**Expected flow**:

1. Get repo identifier: "owner/my-app"
2. No preferences found in either file, use AskUserQuestion with options: "Direct commit to main branch" vs "Create feature branch and PR later"
3. User chooses "feature"
4. Use AskUserQuestion: "Save as shared (cross-device) or local-only?" → user chooses "shared"
5. Save to preferences.json: `{"owner/my-app": "feature"}`
6. Analyze changes: single logical group (auth fix + tests)
7. Create feature branch: `feature/fix-login-validation`
8. Create single commit: `fix(auth): resolve login validation logic`
9. Push and create PR

### Example 2: Returning user with multiple unrelated changes

**Trigger**: "Commit these changes"

**Scenario**:

- Shared preferences.json: `{"owner/my-app": "feature"}`
- Local preferences.local.json: `{"owner/my-app": "main"}` (overrides shared)
- Modified files: `README.md`, `src/utils.js`, `package.json`
- Unrelated changes: docs update, utility function, dependency upgrade

**Expected flow**:

1. Load preferences: merge files, local takes priority → use "main" strategy
2. Analyze changes: detect 3 separate logical groups
3. Suggest split:
   - `docs: update README`
   - `feat(utils): add helper function`
   - `chore: upgrade dependencies`
4. User confirms split
5. Create 3 separate commits on main branch
6. Push to remote

### Example 3: Preference reset scenario

**Trigger**: "Help me commit and reset my commit preferences"

**Scenario**:

- Existing preferences.json: `{"owner/my-app": "feature"}`
- User wants to change strategy for this project
- Modified files: `src/bugfix.js`

**Expected flow**:

1. Detect reset keywords: "reset my commit preferences"
2. Skip loading existing preferences for this repo
3. Use AskUserQuestion: "Direct commit to main branch" vs "Create feature branch and PR later"
4. User chooses "main"
5. Use AskUserQuestion: "Save as shared (cross-device) or local-only?" → user chooses "local-only"
6. Save to preferences.local.json: `{"owner/my-app": "main"}`
7. Proceed with main branch strategy for this commit

### Example 4: Error handling scenario

**Trigger**: "Commit my work"

**Scenario**:

- No git remote configured
- Some files staged, some unstaged

**Expected flow**:

1. Fallback to directory name as identifier
2. Handle mixed staging gracefully
3. Provide clear error messages
4. Continue with available functionality
