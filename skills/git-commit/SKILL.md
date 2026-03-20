---
name: git-commit
description: 提交并推送变更到 git 仓库
---

# Git 提交

## 配置 API

此技能通过就近搜索从 `.claude/config/commit.config.json` 读取配置：

1. **项目配置**：相对于当前工作目录的 `.claude/config/commit.config.json`
2. **全局配置**：如果项目配置未找到，则使用 `~/.claude/config/commit.config.json`

**重要**：包含个人信息（如 `gitUser` 凭据）的配置文件不应提交到版本控制。务必确保 `.claude/config/` 目录在 `.gitignore` 中被正确忽略，以保护敏感配置的隐私。使用全局配置（`~/.claude/config/`）存放个人偏好。

### 配置 Schema

| 字段 | 类型 | 描述 | 默认值 |
| - | - | - | - |
| `strategy` | `"main"` | `"feature"` | 提交策略：直接提交到 main 分支或创建 feature 分支 | `"main"` |
| `splitCommits` | `boolean` | 将不相关的变更拆分为独立的提交 | `true` |
| `autoPush` | `boolean` | 自动推送提交到远程 | `true` |
| `createPullRequest` | `boolean` | 使用 feature 分支策略时创建 PR | `true` |
| `coAuthor` | `boolean` | 在提交中添加 Claude 共同作者标签 | `true` |
| `types` | `string[]` | 允许的提交类型 | `["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"]` |
| `scopes` | `string[]` | 此项目允许的作用域 | `["rule", "skill", "command", "plugin"]` |
| `gitUser` | `object` | Git 用户身份验证配置 | `null` |
| `gitUser.name` | `string` | 提交时预期的 git 用户名 | `null` |
| `gitUser.email` | `string` | 提交时预期的 git 用户邮箱 | `null` |

### 命令行配置覆盖

用户可以在请求中使用自然语言直接覆盖任何配置设置。技能应智能解析用户意图并映射到相应的配置覆盖。

**优先级顺序**（从高到低）：

1. **用户参数** - 从当前请求推断的设置
2. **配置文件值** - 项目配置或全局配置
3. **默认值** - 系统默认值

**语义解析指南**：

- 解析用户意图而非匹配精确短语
- 在请求中查找配置偏好的指示信息
- 将自然语言表达映射到配置字段覆盖
- 支持用户表达同一偏好的多种方式

### 配置示例

```json
{
  "strategy": "feature",
  "splitCommits": true,
  "autoPush": true,
  "createPullRequest": true,
  "coAuthor": false,
  "types": ["feat", "fix", "docs", "refactor", "test"],
  "scopes": ["api", "ui", "auth"],
  "gitUser": {
    "name": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

### 配置管理

- **配置位置**：
  - 项目配置（当前工作目录）：`.claude/config/commit.config.json`
  - 全局配置：`~/.claude/config/commit.config.json`
- **搜索优先级**：项目配置优先于全局配置
- **协作共享**：选择是否将项目配置文件提交用于团队规范，或添加到 .gitignore 仅本地使用

## 工作流程

触发此技能时执行以下步骤：

### 1. 加载配置并解析参数

- 分析用户输入以识别配置意图和偏好
- 从自然语言表达中提取配置覆盖
- 按顺序搜索配置文件：
  1. `.claude/config/commit.config.json`（当前工作目录）
  2. `~/.claude/config/commit.config.json`（全局配置）
- 按优先级合并配置（从高到低）：
  1. **用户参数**（从当前请求解析）
  2. **配置文件值**（项目配置或全局配置）
  3. **默认值**
- 保存新配置时，如果 `.claude/config/` 目录不存在则创建

### 2. 验证 Git 用户身份

- 如果存在 `gitUser` 配置（配置了 `gitUser.name` 或 `gitUser.email`）：
  - 使用 `git config user.name` 获取当前 git 用户名
  - 使用 `git config user.email` 获取当前 git 用户邮箱
  - 与配置值进行比较：
    - 如果配置了 `gitUser.name` 且与当前 git 用户名不匹配，**终止并报错**
    - 如果配置了 `gitUser.email` 且与当前 git 用户邮箱不匹配，**终止并报错**
    - 如果无法获取 git 用户名/邮箱（未配置），**终止并报错**
  - 显示验证错误，包含预期值与实际值
  - 建议修复 git 配置的命令：`git config user.name "Expected Name"` 和/或 `git config user.email "expected@example.com"`
- 如果不存在 `gitUser` 配置，跳过验证

### 3. 分析变更

- 使用 `git status` 验证当前目录是否为 git 仓库
- 运行 `git diff` 和 `git diff --cached` 分析变更
- 按以下维度分类变更：
  - 文件类型（源代码、文档、测试、配置）
  - 基于 `types` 配置的变更类型
- 自动确定作用域：
  - 为 Claude Agent 文件（rule、skill、command、plugin）添加作用域，其他不添加
  - 适用时使用 `scopes` 配置中的作用域
- 如果 `splitCommits` 为 true 且检测到多个不相关的变更，拆分为独立提交

### 4. 执行分支策略

- 通过 `git remote -v` 查找 `upstream` 远程来检查当前仓库是否为 fork
- 如果检测到 fork（存在 upstream 远程）：
  - **强制使用 feature 分支策略**，无论配置如何（开源贡献的要求）
  - 创建新的 feature 分支，格式为 `<change-type>/<short-description>`
- 如果不是 fork：
  - 如果 `strategy` 为 `"main"`：保持在当前分支
  - 如果 `strategy` 为 `"feature"`：创建新的 feature 分支，格式为 `<change-type>/<short-description>`

### 5. 暂存文件

- 使用 `git add` 自动暂存所有修改的文件

### 6. 创建提交

对每个提交组：

- 生成 Angular Conventional Commit 消息：
  - 格式：`<change-type>(<scope-if-configured>): <commit-title>`
  - 复杂变更时添加 body
  - 如果 `coAuthor` 为 true，添加 `Co-authored-by: Claude <noreply@anthropic.com>`
- 使用 `git commit` 创建提交

### 7. 推送和 PR

**线性历史维护**：所有操作必须通过避免合并提交来保持线性 git 历史。

- 如果 `autoPush` 为 true：
  - 尝试 `git push`
  - 如果因 non-fast-forward 推送失败（远程有新提交）：
    1. 运行 `git pull --rebase` 以维护线性历史
    2. 如果发生 rebase 冲突：
       - 显示冲突文件并引导用户手动解决
       - 用户解决后，运行 `git rebase --continue`
    3. rebase 成功完成后，运行 `git push --force-with-lease`
    4. 如果 `--force-with-lease` 失败，使用 `git push --force` 作为后备

- 如果在 feature 分支上且 `createPullRequest` 为 true：
  - **基于策略的 PR 创建**：
    - 如果使用 `"main"` 策略：跳过 PR 创建（提交已直接在 main 上）
    - 如果使用 `"feature"` 策略：使用线性历史设置创建 PR

  - **使用线性合并设置创建 PR**：
    - 如果仓库是 fork：
      - 使用 `gh pr create --repo <upstream-owner>/<upstream-repo>` 创建到 `upstream/main` 的 PR
      - 从 upstream 远程 URL 提取 upstream owner/repo
    - 如果不是 fork：
      - 使用 `gh pr create` 创建到 `origin/main` 的 PR

  - **配置 PR 以维护线性历史**：
    - 设置 PR 使用 squash merge：在 `--body` 中包含 "This PR should be merged using squash and merge to maintain linear history"
    - 在 PR 描述中请求合并后自动删除分支

  - 向用户返回 PR URL

### 8. 处理配置更新

- 如果用户在本次会话中提供了配置覆盖，使用 AskUserQuestion 工具：
  - 问题："是否保存这些设置以供将来使用？"
  - 选项：
    - "是，保存设置"
    - "否，仅用于本次提交"
- 如果用户选择保存，使用 AskUserQuestion 工具：
  - 问题："设置应保存在哪里？"
  - 选项：
    - "项目配置（仅当前项目）"
    - "全局配置（所有项目）"
- 首次创建项目配置时，使用 AskUserQuestion 工具：
  - 问题："是否将配置文件添加到 .gitignore？"
  - 选项：
    - "是，仅本地保留"
    - "否，与团队共享"
- 更新已有配置文件时仅修改被覆盖的值，保持其他设置不变

## 关键规则

- **线性历史原则**：保证 git 历史是线性的，始终可以 fast-forward push/pull
- 使用 `git pull --rebase` 而非 `git pull` 以避免合并提交
- 推送 rebase 后的提交时使用 `git push --force-with-lease`
- 配置 PR 使用 squash merge 以防止合并 feature 分支时产生合并提交
- 使用 TaskCreate 在开始时跟踪所有步骤，并在整个过程中更新状态
- 为用户提供清晰的选项而非自由文本输入
- 如果执行过程中出现任何新变更，从头重新开始整个提交工作流
- 提交消息必须使用 Angular Conventional Commit 格式的英文
- 妥善处理 git 错误，提供清晰的错误信息
