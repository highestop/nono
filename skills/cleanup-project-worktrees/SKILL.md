---
name: cleanup-project-worktrees
description: Clean stale local Git worktrees and branches for the current project, archive their associated Codex chats, and report the results in tables. Use for project cleanup from inside a Git working directory, including leftover branches and chats whose worktrees were already removed.
---

# Cleanup Project Worktrees

Inspect one local repository, remove confirmed stale worktrees and local branches,
and archive their completed Codex chats. A cleanup request authorizes these actions
once the checks below pass. Honor an inspection-only request without mutations.

## Establish the repository and exclusions

Run these commands in the invocation's actual working directory before fetching,
deleting, or archiving anything.

```sh
git rev-parse --is-inside-work-tree
git rev-parse --show-toplevel
git rev-parse --path-format=absolute --git-common-dir
```

Require the first result to be `true` and all commands to succeed. Otherwise stop
and ask the user to run the skill inside the intended Git working directory.
Do not select a repository from chat history or change directories to bypass this
requirement. Reject bare repositories and Git administrative directories.

- Use the canonical common Git directory as the repository identity. Resolve
  paths on the invocation's host. Include only worktrees sharing that identity.
- Exclude `main` by default, the repository's actual default branch, and any extra
  branches or paths the user asks to keep. Apply exclusions to associated chats.
- Always retain the primary worktree, the invocation worktree and its branch, and
  the calling chat. Require a separate explicit request to remove protected items.
- Limit changes to local worktrees, local branches, obsolete remote-tracking refs,
  and eligible Codex chat archive state. Remote branches and PR state are read-only.

## Collect evidence before cleanup

Keep an in-memory record of paths, branch names, full commit IDs, upstreams, PRs,
and chat IDs before removing anything. Include branch-only and chat-only leftovers.

### Worktrees and branches

- Enumerate `git worktree list --porcelain -z` and local branches with
  `git for-each-ref`. Parse structured records without splitting paths on spaces.
  Record whether each worktree is primary, current, detached, locked, or prunable.
- Check each directory's existence. For an existing directory, verify its canonical
  common Git directory and recorded HEAD before running cleanup there. A path that
  now contains another repository or a broken checkout must be retained.
- Inspect staged, unstaged, and all untracked files with
  `git -C <path> status --porcelain=v1 -z --untracked-files=all`.
  Inspect ignored files before deleting a directory. Preserve user-created data,
  credentials, and anything whose disposability is uncertain. Reproducible caches
  may be discarded when their purpose is known. Read failures mean `unknown`.
- Record every local branch's tip and upstream, including branches without a
  worktree. For detached worktrees, use their full HEAD commit ID.
- For already missing directories, preserve the registered branch and HEAD evidence
  before pruning. An unavailable mount or inaccessible parent is not proof of removal.
- Inspect extra directories only when an exact Git administrative record or Codex
  chat identifies them. A matching project directory name alone proves nothing.

### Remotes and pull requests

- Resolve the branch's actual remote and hosting repository from upstream and remote
  metadata. Account for fork heads and repository renames. Keep repository identity
  with every branch name and PR number.
- Refresh relevant remotes with `git fetch --prune <remote>` during cleanup. For an
  inspection-only request, use read-only remote queries. Check live branch listings
  with `git ls-remote --heads <remote>` or the hosting API, including pagination.
  Local `origin/*` refs alone cannot establish remote existence.
- Query all PR states for each exact head repository and branch. On GitHub, use the
  available connector or `gh api` REST. Record URL, state, `merged_at`, head SHA,
  base branch, and merge commit SHA. Check for newer PRs reusing the same branch.
  Distinguish `open`, `merged`, `closed without merge`, `none`, and `unknown`.
- Failed authentication, network errors, and incomplete pagination mean `unknown`,
  never `absent` or `closed`. Keep affected candidates when required evidence is
  unavailable and continue independent checks.

### Codex chats

Discover the current tool schemas for `list_threads`, `list_archived_threads`,
`read_thread`, `wait_threads`, and `set_thread_archived`.

- Enumerate Codex history on the same host with
  `list_threads(mode="history", source="codex", limit=50)` and follow `nextCursor`.
  Include older chats, not just the recent sidebar. Use archived history to resolve
  already archived matches and to verify archive outcomes.
- Match a chat using its exact worktree `cwd`, or explicit evidence of the same
  repository and branch or PR. Use `read_thread` on candidates when the listing lacks
  sufficient context. Preserve returned titles verbatim in the result.
- A shared project, similar title, or mention of a branch is insufficient. For a
  reused directory or branch, verify the chat's actual work context against the
  recorded commit or PR. Keep ambiguous matches and report the missing evidence.
- Distinguish an unarchived chat from a running task. Use
  `wait_threads(timeoutMs=0)` for fresh execution status when needed. Retain a target
  used by running work, queued work, an active goal, or a pending approval or user
  response. An idle chat can still contain unfinished work, so inspect its outcome.
- Consider chats whose worktrees and branches were already removed. Require exact
  repository association, a completed or explicitly abandoned task, and evidence
  that its recorded work was merged or otherwise preserved. Missing paths alone
  do not make a chat eligible for archival.
- Keep a chat that also owns unfinished or protected work. Never archive the calling
  chat through this workflow. If listing or archive tools are unavailable, report
  the limitation. Do not edit Codex databases, indexes, or session files directly.

## Decide whether a target is stale

All applicable checks must pass. A missing remote branch, old timestamp, closed PR,
or clean working directory alone is insufficient.

| Evidence | Decision |
| --- | --- |
| Excluded branch/path, primary/current worktree, or calling chat | Retain |
| Local changes, valuable ignored files, locked checkout, active work, open PR, or uncertain evidence | Retain and state the reason |
| Merged PR, local work verified as included in a retained base, and no later local work | Eligible |
| Closed but unmerged PR | Retain unless all local work is already preserved in a retained base or the user explicitly authorizes discarding that work |
| No PR and remote branch absent | Eligible only when the local tip is already included in a retained base and there is no unfinished associated work |
| No PR and remote branch still exists | Retain unless the user identifies the branch as finished and local work is preserved |
| Missing worktree directory | Eligible registration only after confirming genuine removal and the same completion and preservation checks |
| Detached worktree | Eligible only when HEAD is preserved by a retained branch and the associated work is finished |
| Worktree and branch already removed, completed matching chat remains | Archive the chat after verifying the historical work and exclusions |

Use `git merge-base --is-ancestor <tip> <retained-base>` for ordinary merges.
Compare against the actual PR target and retain the branch protecting that history.
Do not count a ref that will be deleted as the only preserved copy.

Rebase and squash merges may have different commit IDs. Verify the local tip
matches the merged PR's head, its recorded merge result is reachable from the
retained base, and its changes are included. Equal trees between the local tip
and recorded merge result provide direct proof. For rebases with different trees,
`git cherry <retained-base> <tip>` may confirm patch equivalence when there are no
unaccounted merge commits. For squash merges, inspect the aggregate change against
the recorded merge result. Preserve the candidate when this remains ambiguous.
Always check for commits added after the PR merged.

## Clean up and archive

Summarize the concrete candidates, then execute the authorized cleanup. Recheck
HEADs, worktree status, exclusions, PR state, and chat activity immediately before
mutation. Stop that candidate if evidence changed. Process targets independently
so a failure does not erase another target's evidence or imply full success.

1. Remove an eligible existing worktree using `git worktree remove <path>` from a
   retained directory. Avoid `--force`, recursive deletion, and unlocking worktrees
   automatically. If a supported managed-worktree lifecycle tool applies, use its
   documented identity and protections. `archive_worktree` applies only to eligible
   attachments returned by `list_artifacts` on the calling chat and does not archive
   the chat itself. Preserve submodules and embedded repositories for separate handling.
2. For missing directories, inspect `git worktree prune --dry-run --verbose --expire now`.
   Run the matching prune only when every registration it would remove has passed
   the checks. Otherwise retain the unresolved registrations and report them.
3. Delete an eligible local branch only after all its worktrees are removed and no
   remaining worktree uses it. Prefer `git branch -d -- <branch>`. Use `-D` only when
   the verified rebase/squash proof above establishes that the work is preserved,
   or the user has explicitly authorized discarding the identified work. A failed
   deletion alone is never permission to force it.
4. Verify removal of the worktree registration, its exact directory, and the local
   branch. For partial failures, retain associated chats and report remaining items.
   Objects already absent count as complete when their history passed the checks.
5. Archive each eligible completed chat with
   `set_thread_archived(threadId=<id>, hostId=<matching-host>, source="codex", archived=true)`.
   Always supply the exact target ID. Skip already archived chats. Verify the tool
   result or archived listing. If archival fails, report the cleanup as partial and
   retain the ID for a retry. Do not recreate deleted worktrees or erase chat history.

Rerun the Git inventory after mutations. Confirm that retained worktrees and branches
still exist. Make retries idempotent by checking current state before each action.
Local cleanup alone creates no source changes to commit or PR to open.

## Report results

Always finish with tables in the user's language, including retained and unresolved
items. State total worktrees before and after, whether the primary worktree is counted,
and counts of removed worktrees, deleted branches, archived chats, and unresolved
failures. Count failed attempts that later recovered separately from unresolved
failures. Show missing directories as `missing` and unavailable evidence as `unknown`.

| Worktree / branch | Directory before | Local changes | Remote branch | PR and state | Decision / reason | Worktree / directory / branch result |
| --- | --- | --- | --- | --- | --- | --- |

| Codex chat title / ID | Associated worktree, branch, or PR | Outcome before | Archive result / reason |
| --- | --- | --- | --- |

Use `not applicable` for branch-only rows. Include detached worktrees and chat-only
leftovers explicitly. Link PR numbers to their verified URLs. Distinguish confirmed
`no matching chat` from `chat lookup unavailable`. Use `~` or project-relative paths
where readable and escape table delimiters in paths and titles. Never label an
attempted deletion or archive as completed without verifying the outcome.
