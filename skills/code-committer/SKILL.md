---
name: code-committer
description: Handle Git repository changes with verified commit identities, automatic agent co-authorship, conventional commits, and GitHub PR management. When a Git workspace has changes, automatically commit, push, and create or update a PR without asking whether to submit it.
---

# Code committer

## GitHub command selection

- Use high-level `gh` commands for routine GitHub operations.
- If a high-level `gh` command is blocked by an unnecessary GraphQL scope or hidden preflight query, use the equivalent REST endpoint through `gh api` with the narrowest required permissions instead of broadening token scopes solely to satisfy the command.

## Scope and authorization

- Honor explicit requests not to commit, push, or submit a PR.
- Keep workspace-specific exceptions scoped to that workspace; do not record them in this skill, `AGENTS.md`, shared rules, or configuration files.
- Use the user's instructions directly.
- Do not read or write skill-specific configuration files.
- When `git status --short` shows modified, staged, deleted, or untracked files, automatically commit the task-related changes, push, and create or update a PR without asking whether to submit it, even when the user only requested edits.
- Skip the commit and PR workflow when there are no changes.
- Complete requested edits and relevant verification before proceeding with the commit and PR workflow.
- Summarize the changes before proceeding with the commit and PR workflow.
- If any step is blocked, preserve the work and report the cause and remaining steps.

## Inspect the repository and prepare the branch

- Inspect the repository, branch, remotes, `git status`, `git diff`, and `git diff --cached`.
- Include only task-related changes; do not bundle unrelated pre-existing changes.
- Split unrelated topics into separate commits.
- Recheck the workspace if the user changes files during the task.
- Use a feature branch; never commit directly to the default branch.
- Reuse an appropriate existing feature branch when available.
- Name a new branch `<user-name>-<short-description>` in kebab-case, using `git config user.name` or the authenticated `gh` login; ask if neither is available.
- Keep history linear by fetching and rebasing when needed; do not create merge commits.
- Do not amend existing commits.
- Do not overwrite unrelated work.

## Verify identity and co-authorship

- Before each commit, run `git config --show-origin --get user.name`, `git config --show-origin --get user.email`, `git var GIT_AUTHOR_IDENT`, and `git var GIT_COMMITTER_IDENT` in the target workspace using the same environment as the commit.
- Require effective author and committer identities with nonempty names and emails; if they do not resolve, explain what is missing and ask the user to supply it.
- Never silently change Git identity settings.
- Infer the co-author trailer from the agent that contributed to the changes:
  - Codex: `Co-Authored-By: Codex <noreply@openai.com>`
  - Claude: `Co-Authored-By: Claude <noreply@anthropic.com>`
  - If the agent is unknown, omit the trailer and explain why; do not invent an identity.
- Report the effective author and committer names and emails, the Git setting sources, and any difference caused by environment overrides.
- Include the inferred co-author trailer in the identity summary.

## Commit and push

- After verification, stage only the intended files.
- Write English Angular Conventional Commit messages, adding a concise scope when useful.
- Append the inferred `Co-Authored-By` trailer after a blank line in the commit body.
- Determine the PR target from `upstream` when present; otherwise use `gh repo view --json isFork,parent,nameWithOwner`.
- Push the feature branch to the fork when working in a fork, or to the repository's remote otherwise.
- For a non-fast-forward rejection, fetch and rebase, resolve conflicts within the task's scope, then retry a normal push.
- Use `--force-with-lease` only when an intentional history rewrite requires it.
- Never fall back to `--force` without explicit authorization.

## Create or update the PR

- Manage PRs with `gh`.
- Update the branch's existing PR when present; otherwise create one.
- For a fork, open the PR against the original repository with `gh pr create --repo <upstream-owner>/<upstream-repo> --head <fork-owner>:<feature-branch>`.
- Use an English Conventional Commit title.
- Write an English description covering the problem, resulting behavior, relevant validation, and related issues.
- State the preference for rebase merge in the PR description.
- State the preference for feature branch deletion in the PR description.
- End the PR body with the same agent `Co-Authored-By` trailer used in the commit, separated from the description by a blank line.
- If the PR author differs from the commit author, add `Co-Authored-By: <commit-author-name> <commit-author-email>` before the agent trailer, using the commit's effective author identity and enclosing the email in angle brackets.
- When both trailers are present, they must be the final two lines of the PR body, with no blank line between them.
- When updating a PR, preserve the trailer order and format without duplicating trailers.
- Attach created or updated PRs to the current task when the host supports it.
- Provide the PR link.

## Review and merge

- Check CI and review status with `gh pr checks` and `gh pr view`.
- Fix task-related failures and valid blocking review issues with new commits that follow the same identity reporting and co-author rules.
- Ask for direction when a review requires a material scope change or its resolution is unclear.
- Merge only when required checks pass and no unresolved blocking review issues remain.
- Require the user's authorization before merging; honor existing standing authorization without asking again, otherwise ask before merging.
- Prefer the project's merge queue when enabled.
- Prefer rebase merge.
- Prefer feature branch deletion after merging.
- Preserve commit messages and co-author trailers during the merge.
- If squash is required, retain all co-author trailers in the squash commit body.
- Confirm the merge.
- Confirm remote feature branch deletion.
- Check closure of any issue the PR should close.
- Provide an available preview link.
