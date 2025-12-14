---
allowed-tools: Bash(git checkout*, git branch*, git commit*, git status*, git diff*, git log*)
description: Create commits on main branch and push to remote repository
---

## Task

Create commits for local code modifications on the main branch, then push to remote repository after successful commit

### Main Workflow

1. Commit changes on main branch, create commit
1. Return successful commit information
1. Push to remote main branch

## Status

- Current branch: !`git branch --show-current`
- Locally modified files: !`git status --porcelain | head -10`
- Recent commit history: !`git log --oneline | head -5`

## Important Notes

- Commit messages should follow Angular Conventional Commit specification, simple format: `<type>: <subject>`. Where `type: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert`, subject should be concise description, verb in base form, lowercase first letter, no ending punctuation
- If many files or extensive content are modified, provide appropriate additional commit description
- If modified files clearly represent different tasks, split into multiple commits
- Do not use `--amend` to merge into existing commits, always create new commits for code submission