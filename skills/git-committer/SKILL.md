---
name: git-committer
description: 使用此技能提交并推送变更到 git 仓库，如需要则创建 pull request。
---

# Git 提交技能

## 配置 API

此技能通过就近搜索从 `.claude/config/commit.config.json` 读取配置：

1. **项目配置**：相对于当前工作目录的 `.claude/config/commit.config.json`
2. **全局配置**：如果项目配置未找到，则使用 `~/.claude/config/commit.config.json`

**重要**：包含个人信息（如 `gitUser` 凭据）的配置文件不应提交到版本控制。务必确保 `.claude/config/` 目录在 `.gitignore` 中被正确忽略，以保护敏感配置的隐私。使用全局配置（`~/.claude/config/`）存放个人偏好。

### 配置 Schema

| 字段 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `strategy` | `"main"` \| `"feature"` | 提交策略：直接提交到 main 分支或创建 feature 分支 | `"main"` |
| `splitCommits` | `boolean` | 将不相关的变更拆分为独立的提交 | `true` |
| `autoPush` | `boolean` | 自动推送提交到远程 | `true` |
| `createPullRequest` | `boolean` | 使用 feature 分支策略时创建 PR | `false` |
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

**常见覆盖模式**：
| 配置字段 | 自然语言指示 | 示例表达 |
|----------|-------------|----------|
| `strategy` | 分支策略偏好 | "use feature branch"、"commit to main"、"create branch" |
| `autoPush` | 推送行为偏好 | "don't push"、"without push"、"and push"、"skip push" |
| `createPullRequest` | PR 创建偏好 | "create PR"、"make pull request"、"no PR"、"skip PR" |
| `splitCommits` | 提交拆分偏好 | "single commit"、"one commit"、"split commits"、"separate" |
| `coAuthor` | 共同作者偏好 | "no co-author"、"without co-author"、"skip co-author" |

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
  - 项目配置：`.claude/config/commit.config.json`（当前工作目录）
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
  - 选项：["是，保存设置"、"否，仅用于本次提交"]
- 如果用户选择保存，使用 AskUserQuestion 工具：
  - 问题："设置应保存在哪里？"
  - 选项：["项目配置（仅当前项目）"、"全局配置（所有项目）"]
- 首次创建项目配置时，使用 AskUserQuestion 工具：
  - 问题："是否将配置文件添加到 .gitignore？"
  - 选项：["是，仅本地保留"、"否，与团队共享"]
- 更新已有配置文件时仅修改被覆盖的值，保持其他设置不变

## 关键规则

- **线性历史原则**：不惜一切代价维护线性 git 历史——永远不要在 main 分支上创建合并提交
- 使用 `git pull --rebase` 而非 `git pull` 以避免合并提交
- 推送 rebase 后的提交时使用 `git push --force-with-lease`
- 配置 PR 使用 squash merge 以防止合并 feature 分支时产生合并提交
- 使用 TaskCreate 在开始时跟踪所有步骤，并在整个过程中更新状态
- 为用户提供清晰的选项而非自由文本输入
- 如果执行过程中出现任何新变更，从头重新开始整个提交工作流
- 提交消息必须使用 Angular Conventional Commit 格式的英文
- 妥善处理 git 错误，提供清晰的错误信息



## 示例

### 示例 1：默认行为（无配置文件）

**触发**："帮我提交变更"

**场景**：
- 不存在 `.claude/config/commit.config.json`（项目配置和全局配置均无）
- 修改的文件：`src/auth.js`、`tests/auth.test.js`
- 所有变更都与修复登录验证相关

**预期流程**：
1. 加载默认配置
2. 分析变更：单个逻辑组（认证修复 + 测试）
3. 自动暂存文件并直接提交到 main 分支
4. 创建提交：`fix(auth): resolve login validation logic`
5. 推送到远程

### 示例 2：Feature 分支策略

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "strategy": "feature"
}
```

**预期流程**：
1. 创建 feature 分支：`fix/auth-validation`
2. 将变更提交到 feature 分支
3. 推送 feature 分支到远程

### 示例 3：禁用提交拆分

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "splitCommits": false
}
```

**场景**：
- 修改的文件：`README.md`、`src/utils.js`、`package.json`
- 多个不相关的变更

**预期流程**：
1. 将所有变更视为单个提交组
2. 创建一个提交：`feat: update docs, add utility, and upgrade deps`

### 示例 4：禁用自动推送

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "autoPush": false
}
```

**预期流程**：
1. 在本地创建提交
2. 不自动推送到远程
3. 用户需要稍后手动推送

### 示例 5：启用自动创建 PR

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "strategy": "feature",
  "createPullRequest": true
}
```

**预期流程**：
1. 创建 feature 分支
2. 提交并推送变更
3. 使用 `git remote -v` 检查远程并确认不存在 `upstream` 远程
4. 使用 `gh pr create` 创建到 origin 仓库的 PR
5. 向用户返回 PR URL

### 示例 6：禁用共同作者标签

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "coAuthor": false
}
```

**预期流程**：
1. 创建提交时不包含 `Co-authored-by: Claude <noreply@anthropic.com>` 行
2. 提交消息仅包含 conventional commit 格式

### 示例 7：自定义提交类型

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "types": ["feat", "fix", "docs", "refactor"]
}
```

**预期流程**：
1. 分析变更时仅使用指定的提交类型
2. 使用有限的类型集对变更进行分类
3. 其他标准类型如 "chore"、"test" 将不会使用

### 示例 8：自定义作用域

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "scopes": ["api", "ui", "auth", "database"]
}
```

**预期流程**：
1. 自动检测变更作用域时使用自定义作用域
2. 对匹配模式的文件应用相应作用域：
   - API 相关文件 → `feat(api): ...`
   - UI 组件 → `feat(ui): ...`
   - 认证模块 → `fix(auth): ...`
   - 数据库文件 → `chore(database): ...`

### 示例 9：命令行覆盖并保存配置

**触发**："commit with feature branch and create PR"

**场景**：
- 用户已有配置：`{"strategy": "main", "createPullRequest": false}`
- 用户想要为本次提交覆盖

**预期流程**：
1. 分析用户意图：从 "with feature branch" 推断 strategy="feature"，从 "create PR" 推断 createPullRequest=true
2. 为本次提交应用覆盖的值
3. 按请求创建 feature 分支和 PR
4. 通过 AskUserQuestion 询问："是否保存这些设置以供将来使用？"，选项 ["是，保存设置"、"否，仅用于本次提交"]
5. 如果是，通过 AskUserQuestion 询问："设置应保存在哪里？"，选项 ["项目配置（仅当前项目）"、"全局配置（所有项目）"]
6. 用新值更新配置文件

### 示例 10：无已有配置时的命令行覆盖

**触发**："commit without push"

**场景**：
- 不存在已有配置文件
- 用户只想在本地提交

**预期流程**：
1. 分析用户意图：从 "without push" 推断 autoPush=false
2. 应用默认值并覆盖：autoPush=false
3. 创建提交但不推送到远程
4. 通过 AskUserQuestion 询问："是否保存这些设置以供将来使用？"，选项 ["是，保存设置"、"否，仅用于本次提交"]
5. 如果是，通过 AskUserQuestion 询问："设置应保存在哪里？"，选项 ["项目配置（仅当前项目）"、"全局配置（所有项目）"]
6. 用覆盖值创建新配置文件
7. 如果是首次创建项目配置，通过 AskUserQuestion 询问："是否将配置文件添加到 .gitignore？"，选项 ["是，仅本地保留"、"否，与团队共享"]

### 示例 11：Fork 项目（强制 feature 分支）

**触发**："commit"

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "strategy": "main",
  "createPullRequest": true
}
```

**场景**：
- 仓库是 fork（有指向原始仓库的 upstream 远程）
- 用户配置策略为 "main"，但将被覆盖
- 修改的文件：`src/feature.js`、`tests/feature.test.js`

**预期流程**：
1. 使用 `git remote -v` 检查远程并检测到 `upstream` 远程
2. **覆盖策略为 "feature"**（fork 项目要求使用 feature 分支）
3. 创建 feature 分支：`feat/add-new-feature`
4. 将变更提交到 feature 分支
5. 推送 feature 分支到 origin（用户的 fork）
6. 从 upstream 远程 URL 提取 upstream owner/repo
7. 使用 `gh pr create --repo <upstream-owner>/<upstream-repo>` 创建到 upstream 仓库的 PR
8. 返回指向 upstream 仓库的 PR URL

### 示例 12：使用 feature 策略的 fork 项目

**触发**："commit with create PR"

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "strategy": "feature",
  "createPullRequest": true
}
```

**场景**：
- 仓库是 fork（有指向原始仓库的 upstream 远程）
- 用户已配置 feature 策略（与 fork 要求一致）
- 修改的文件：`docs/README.md`

**预期流程**：
1. 检查远程并检测到 fork，确认 feature 策略合适
2. 创建 feature 分支：`docs/update-readme`
3. 将变更提交到 feature 分支
4. 推送 feature 分支到 origin（用户的 fork）
5. 创建到 upstream 仓库的 PR
6. 返回指向 upstream 仓库的 PR URL

### 示例 13：推送冲突时的线性历史维护

**触发**："commit my changes"

**场景**：
- 本地提交已成功创建
- 远程仓库有新提交（推送将因 non-fast-forward 错误失败）
- `autoPush` 已启用

**预期流程**：
1. 照常在本地创建提交
2. 尝试 `git push` - 失败，提示 "Updates were rejected because the remote contains work that you do not have locally"
3. 运行 `git pull --rebase` 以维护线性历史
4. 如果没有冲突：rebase 成功完成
5. 运行 `git push --force-with-lease` 推送 rebase 后的提交
6. 如果 `--force-with-lease` 失败，后备使用 `git push --force`

**有冲突时的预期流程**：
1. 照常在本地创建提交
2. 尝试 `git push` - 因 non-fast-forward 错误失败
3. 运行 `git pull --rebase` - 遇到合并冲突
4. 向用户显示冲突文件："Rebase conflicts in: `file1.js`, `file2.md`"
5. 引导用户："请手动解决冲突，然后告诉我继续"
6. 用户解决并确认后，运行 `git rebase --continue`
7. rebase 完成后，运行 `git push --force-with-lease`

### 示例 14：Feature 分支 PR 的线性历史设置

**配置**：
```json
{
  "strategy": "feature",
  "createPullRequest": true
}
```

**预期流程**：
1. 创建 feature 分支并提交变更
2. 推送 feature 分支到远程
3. 使用 `gh pr create` 创建 PR，附加以下设置：
   - 在 PR body 中包含："This PR should be merged using squash and merge to maintain linear history"
   - 请求合并后自动删除分支
4. 返回 PR URL，并附注线性合并要求

### 示例 15：Main 策略不创建 PR

**配置**：
```json
{
  "strategy": "main",
  "createPullRequest": true
}
```

**预期流程**：
1. 直接提交到 main 分支
2. 推送到远程（如需要则处理 rebase）
3. 跳过 PR 创建，因为提交已在 main 分支上
4. 注意：`createPullRequest` 设置在 main 策略下被忽略

### 示例 16：Git 用户身份验证

**配置**（`.claude/config/commit.config.json`）：
```json
{
  "gitUser": {
    "name": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

**场景 A**：Git 用户与配置匹配
- 当前 git 用户：name="John Doe"、email="john.doe@example.com"

**预期流程**：
1. 加载带有 git 用户验证的配置
2. 获取当前 git 用户：`git config user.name` 和 `git config user.email`
3. 验证通过——继续正常的提交流程

**场景 B**：Git 用户名不匹配
- 当前 git 用户：name="Jane Smith"、email="john.doe@example.com"
- 配置预期：name="John Doe"、email="john.doe@example.com"

**预期流程**：
1. 加载带有 git 用户验证的配置
2. 获取当前 git 用户：`git config user.name` 返回 "Jane Smith"
3. **终止并报错**："Git user name mismatch. Expected: 'John Doe', Got: 'Jane Smith'"
4. 建议修复："Run: git config user.name 'John Doe'"

**场景 C**：Git 用户未配置
- git config 中未设置 git 用户名/邮箱

**预期流程**：
1. 加载带有 git 用户验证的配置
2. 获取当前 git 用户：`git config user.name` 返回空/null
3. **终止并报错**："Git user name not configured. Expected: 'John Doe'"
4. 建议修复："Run: git config user.name 'John Doe' && git config user.email 'john.doe@example.com'"
