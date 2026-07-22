## 示例 1：默认行为（无配置文件）

**触发**："帮我提交变更"

**场景**：

- 不存在 `.agents/config/commit.config.json`（项目配置和全局配置均无）
- 修改的文件：`src/auth.js`、`tests/auth.test.js`
- 所有变更都与修复登录验证相关

**预期流程**：

1. 加载默认配置
2. 分析变更：单个逻辑组（认证修复 + 测试）
3. 自动暂存文件并直接提交到 main 分支
4. 创建提交：`fix(auth): resolve login validation logic`
5. 推送到远程

## 示例 2：Feature 分支策略

**配置**（`.agents/config/commit.config.json`）：

```json
{
  "strategy": "feature"
}
```

**预期流程**：

1. 创建 feature 分支：`fix/auth-validation`
2. 将变更提交到 feature 分支
3. 推送 feature 分支到远程

## 示例 3：禁用提交拆分

**配置**（`.agents/config/commit.config.json`）：

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

## 示例 4：禁用自动推送

**配置**（`.agents/config/commit.config.json`）：

```json
{
  "autoPush": false
}
```

**预期流程**：

1. 在本地创建提交
2. 不自动推送到远程
3. 用户需要稍后手动推送

## 示例 5：启用自动创建 PR

**配置**（`.agents/config/commit.config.json`）：

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

## 示例 6：添加共同作者标签

**预期流程**：

1. 创建提交时在正文最后添加当前 agent 的 `Co-Authored-By` trailer
2. 提交消息使用 conventional commit 格式

## 示例 7：自定义提交类型

**配置**（`.agents/config/commit.config.json`）：

```json
{
  "types": ["feat", "fix", "docs", "refactor"]
}
```

**预期流程**：

1. 分析变更时仅使用指定的提交类型
2. 使用有限的类型集对变更进行分类
3. 其他标准类型如 "chore"、"test" 将不会使用

## 示例 8：自定义作用域

**配置**（`.agents/config/commit.config.json`）：

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

## 示例 9：命令行覆盖并保存配置

**触发**："commit with feature branch and create PR"

**场景**：

- 用户已有配置：`{"strategy": "main", "createPullRequest": false}`
- 用户想要为本次提交覆盖

**预期流程**：

1. 分析用户意图：从 "with feature branch" 推断 strategy="feature"，从 "create PR" 推断 createPullRequest=true
2. 为本次提交应用覆盖的值
3. 按请求创建 feature 分支和 PR
4. 通过当前 agent 的结构化询问工具询问："是否保存这些设置以供将来使用？"，选项 ["是，保存设置"、"否，仅用于本次提交"]
5. 如果是，通过当前 agent 的结构化询问工具询问："设置应保存在哪里？"，选项 ["项目配置（仅当前项目）"、"全局配置（所有项目）"]
6. 用新值更新配置文件

## 示例 10：无已有配置时的命令行覆盖

**触发**："commit without push"

**场景**：

- 不存在已有配置文件
- 用户只想在本地提交

**预期流程**：

1. 分析用户意图：从 "without push" 推断 autoPush=false
2. 应用默认值并覆盖：autoPush=false
3. 创建提交但不推送到远程
4. 通过当前 agent 的结构化询问工具询问："是否保存这些设置以供将来使用？"，选项 ["是，保存设置"、"否，仅用于本次提交"]
5. 如果是，通过当前 agent 的结构化询问工具询问："设置应保存在哪里？"，选项 ["项目配置（仅当前项目）"、"全局配置（所有项目）"]
6. 用覆盖值创建新配置文件
7. 如果是首次创建项目配置，通过当前 agent 的结构化询问工具询问："是否将配置文件添加到 .gitignore？"，选项 ["是，仅本地保留"、"否，与团队共享"]

## 示例 11：Fork 项目（强制 feature 分支）

**触发**："commit"

**配置**（`.agents/config/commit.config.json`）：

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

## 示例 12：使用 feature 策略的 fork 项目

**触发**："commit with create PR"

**配置**（`.agents/config/commit.config.json`）：

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

## 示例 13：推送冲突时的线性历史维护

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

## 示例 14：Feature 分支 PR 的线性历史设置

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

## 示例 15：Main 策略不创建 PR

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

## 示例 16：Git 用户身份验证

**配置**（`.agents/config/commit.config.json`）：

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
