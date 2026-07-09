---
name: commit
description: 提交代码、跟踪 PR 状态、完成代码合并
---

# Git 提交

严格按步骤执行。只有完成或明确跳过当前步骤后，才能进入下一步。

## 配置

可从当前请求、项目配置或全局配置读取偏好。优先级：

1. 用户当前请求
2. 项目配置：`.agents/config/commit.config.json`、`.claude/config/commit.config.json`、`.codex/config/commit.config.json`
3. 全局配置：`~/.agents/config/commit.config.json`、`~/.claude/config/commit.config.json`、`~/.codex/config/commit.config.json`
4. 默认值

支持字段：

| 字段 | 默认值 | 说明 |
| - | - | - |
| `gitUser.name` | `null` | 期望的 git 用户名 |
| `gitUser.email` | `null` | 期望的 git 邮箱 |
| `coAuthor` | `true` | 是否添加当前 agent 的 co-author |
| `featureBranchPrefix` | 当前 `git config user.name` | feature 分支名前缀，使用 kebab-case |
| `prMergeMethod` | `rebase` | PR 合并方式，默认使用 rebase merge 保留每个 commit 及其 message |

如用户在请求中临时覆盖配置，完成后询问是否保存；保存时优先写入 `.agents/config/commit.config.json`，除非用户指定其他 agent 目录。包含个人信息的配置不得提交到版本控制。

## 工作流

### 1. 检查环境

- 确认当前目录是 git 仓库。
- 检查 `git config user.name` 和 `git config user.email`。
- 仅检查已配置的 `gitUser` 字段：配置了 `gitUser.name` 就校验 `user.name`，配置了 `gitUser.email` 就校验 `user.email`；未配置字段不做要求。已配置字段缺失或不匹配时终止，并给出修复命令。
- 必须先区分 fork 和非 fork 仓库，再决定 PR 目标：
  - 先使用 `git remote -v` 检查是否存在 `upstream`；存在时视为 fork，原 repo 为 `upstream` 对应的仓库。
  - 如果没有 `upstream`，继续使用 `gh repo view --json isFork,parent,nameWithOwner` 检查当前 `origin` 是否为 GitHub fork；`isFork` 为 `true` 时，原 repo 为 `parent.nameWithOwner`。
  - 判定是否为 fork 的方法：存在 `upstream` remote，或 `gh repo view` 返回 `isFork` 的值，为 `true` 则为 fork，为 `false` 则为非 fork。

### 2. 分析变更

- 使用 `git status`、`git diff`、`git diff --cached` 分析变更。
- 如果执行过程中发现用户新增或修改了工作区内容，重新从本步骤开始。
- 按不相关主题拆分提交；不要把无关变更放进同一个 commit。

### 3. 处理分支

- 默认都使用 feature 分支提交；不要在 `main` 分支上直接提交。
- feature 分支名使用 `<featureBranchPrefix>-<short-description>`，整体使用 kebab-case；未配置 `featureBranchPrefix` 时，从当前 `git config user.name` 推导。
- 保持线性历史；使用 `git pull --rebase`，不要创建 merge commit。

### 4. 创建提交

- 使用 `git add` 暂存本次提交需要的文件。
- Commit message 使用英文 Angular Conventional Commit，且不使用 scope：
  - 示例：`chore: remove article assets`
- 不要使用 amend 修改既有提交；创建新的 commit。
- 如果 `coAuthor` 为 true，在提交正文最后添加当前 agent：
  - Claude：`Co-Authored-By: Claude <noreply@anthropic.com>`
  - Codex：`Co-Authored-By: Codex <noreply@openai.com>`
  - 无法判断当前 agent 时，询问用户或跳过并说明原因。

### 5. 推送和创建 PR

- 提交后自动推送。
- PR title 使用英文 Angular Conventional Commit，且不使用 scope：
  - 示例：`chore: remove article assets`
- 推送失败且原因是 non-fast-forward：
  1. 运行 `git pull --rebase`
  2. 如有冲突，说明冲突文件并解决或等待用户处理
  3. rebase 完成后使用 `git push --force-with-lease`
- 如果 `--force-with-lease` 失败，不要直接使用 `--force`，先说明风险并询问用户。
- 如果当前是 feature 分支且没有 PR，默认创建 PR；只有用户明确要求只提交不提 PR 时才跳过。
  - fork 仓库：把 feature branch 推送到自己的 fork，再用 `gh pr create --repo <upstream-owner>/<upstream-repo> --head <fork-owner>:<feature-branch>` 向原 repo 创建跨仓库 PR；不需要切换到原 repo owner 身份。
  - 非 fork 仓库：推送当前 feature 分支后，用 `gh pr create` 向当前仓库创建 PR。
- PR 描述中说明默认使用 rebase merge，并请求合并后删除 feature 分支。
- 如果此次修改有关联 Issue，在 PR 中关联 Issue。

### 6. 跟踪 PR

- 创建或找到 PR 后，告诉用户 PR 链接。
- 使用 `gh pr checks`、`gh pr view` 跟踪 check 和 review 状态。
- 如果有 check 失败：
  1. 总结失败 job 和关键错误
  2. 修复问题
  3. 按提交流程新增 commit、推送，并继续跟踪 PR
- 如果 review 提出严重问题：
  1. 总结问题
  2. 判断问题是否真实、合理、需要修复，并说明依据
  3. 询问用户是修复还是拒绝
  4. 修复则新增 commit 并继续跟踪；拒绝则 dismiss review 并写明理由
- 如果严重问题已修复但 review 被跳过，可按 reviewer 约定评论触发重审，例如 `@codex review`。

### 7. 合并 PR

- PR checks 和 reviews 没问题后，询问用户是否自动合并。
- 用户选择不合并时，到此结束。
- 用户选择合并时：
  - 如果项目开启了 merge queue，优先使用 merge queue
  - 默认使用 rebase merge，保留每个 commit 及其完整 message 和 co-author trailer
  - 仅当用户明确要求 squash，或 PR 包含多个细碎临时提交且需要压缩时，才使用 squash merge
    - 使用 squash merge 时，必须在 squash commit body 中保留所有必要的 `Co-Authored-By` trailer
  - 不要使用 merge commit，避免在 `main` 分支上出现分叉
  - 等待 PR 合并完成
  - 确认远程 feature 分支已删除
  - 如果有关联 Issue，确认 Issue 已关闭
  - 如有预览环境，提供最新预览链接

## 关键规则

- 使用 `gh` CLI 操作 PR。
- 默认保持线性历史。
- 默认使用 rebase merge 合并 PR，以保留每个 commit 及其 co-author 信息。
- 不直接在 `main` 提交。
- 不使用 amend。
- PR title 和 Commit message 均使用英文 Angular Conventional Commit，且不使用 scope。
- 妥善处理 git 错误，说明原因、影响和下一步。
