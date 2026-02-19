---
name: claude-code-bash-helper
description: 当用户需要在 Claude Code 中执行带环境变量和管道的 bash 命令时使用此技能，尤其是 token 正确但 API 调用因认证错误失败的情况。
---

# Claude Code Bash 最佳实践技能

## 工作流程

触发此技能时执行以下步骤：

### 1. 识别问题

- 检查用户的命令是否涉及环境变量（`$VAR`）与管道（`|`）
- 查找以下症状：
  - 尽管 token 正确但 API 认证失败
  - 管道命令中环境变量显示为空
  - 在终端中正常工作但在 Claude Code 中失败的命令
- 常见的问题模式：
  ```bash
  curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" | jq .
  ```
- 使用 AskUserQuestion 工具确认："你是否在 Claude Code bash 命令中遇到环境变量问题？"

### 2. 分析用户命令

- 解析用户现有的命令结构
- 识别组成部分：
  - 使用环境变量的命令
  - 管道操作
  - 使用 jq 的 JSON 处理
  - 复杂的引号场景
- 对用例进行分类：
  - 简单 API 调用
  - 带 JSON body 的 POST 请求
  - 从命令输出赋值变量
  - 包含 API 调用的循环
  - 文件上传或下载

### 3. 应用修复模式

根据命令类型应用相应的修复：

#### 简单 API 调用：
```bash
# 修复前（有问题）
curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" | jq .

# 修复后
bash -c 'curl -s "$API_URL" -H "Authorization: Bearer $TOKEN"' | jq .
```

#### 带 JSON Body 的 POST 请求：
```bash
# 修复前（有问题）
curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" -d '{"key": "value"}' | jq .

# 修复后 - 使用文件方式
echo '{"key": "value"}' > /tmp/request.json
bash -c 'curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" -d @/tmp/request.json' | jq .
```

#### 变量赋值：
```bash
# 修复前（有问题）
RESULT=$(curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" | jq -r '.data')

# 修复后
RESULT=$(bash -c 'curl -s "$API_URL" -H "Authorization: Bearer $TOKEN"' | jq -r '.data')
```

#### 循环：
```bash
# 修复前（有问题）
for id in $(curl -s "$API_URL/list" -H "Authorization: Bearer $TOKEN" | jq -r '.[]'); do
  echo $id
done

# 修复后
for id in $(bash -c 'curl -s "$API_URL/list" -H "Authorization: Bearer $TOKEN"' | jq -r '.[]'); do
  echo $id
done
```

### 4. 提供测试命令

生成验证修复是否有效的测试命令：

```bash
# 测试环境变量可见性
echo "Direct access: $YOUR_TOKEN"
echo "In pipe: $YOUR_TOKEN" | cat
bash -c 'echo "In bash -c: $YOUR_TOKEN"' | cat
```

### 5. 教学说明

解释技术背景：

- **根本原因**：Claude Code 的 bash 预处理在使用管道时会清除环境变量
- **解决方案**：`bash -c '...'` 创建一个保留变量的子 shell
- **最佳实践**：只包装需要变量的命令部分，将处理逻辑放在外面
- **相关 Issue**：参考 GitHub issues #11225 和 #8318

### 6. 生成完整解决方案

向用户提供：
- 修正后的命令
- 验证其有效性的测试步骤
- 类似未来命令的模板
- 可能需要的常见变体

## 关键规则

- 始终只将使用环境变量的命令部分包装在 `bash -c '...'` 中
- 将 `jq` 和其他处理保持在 `bash -c` 包装器之外以提高可读性
- 使用基于文件的 JSON 输入（`-d @file`）以避免复杂的引号转义
- 在提供给用户之前测试解决方案
- 解释修复的原因，而不仅仅是解决方案
- 使用 `--header` 代替 `-H` 以获得更好的兼容性
- 除非确实需要花括号，否则优先使用 `$VAR` 而非 `${VAR}`

## 常见修复模式

### 模式 1：基本 API 认证
```bash
# 输入: curl -s "$URL" -H "Authorization: Bearer $TOKEN" | jq .
# 输出: bash -c 'curl -s "$URL" -H "Authorization: Bearer $TOKEN"' | jq .
```

### 模式 2：复杂 JSON Body
```bash
# 输入: curl -s "$URL" -H "Auth: $TOKEN" -d '{"complex": "json"}' | jq .
# 输出:
# echo '{"complex": "json"}' > /tmp/data.json
# bash -c 'curl -s "$URL" -H "Auth: $TOKEN" -d @/tmp/data.json' | jq .
```

### 模式 3：多个变量
```bash
# 输入: curl -s "$BASE_URL/api" -H "Auth: $TOKEN" -H "X-User: $USER_ID" | jq .
# 输出: bash -c 'curl -s "$BASE_URL/api" -H "Auth: $TOKEN" -H "X-User: $USER_ID"' | jq .
```

### 模式 4：命令替换
```bash
# 输入: ID=$(curl -s "$URL" -H "Auth: $TOKEN" | jq -r '.id')
# 输出: ID=$(bash -c 'curl -s "$URL" -H "Auth: $TOKEN"' | jq -r '.id')
```

## 示例

### 示例 1：用户的 API 调用失败

**触发**："我的 curl 命令在 Claude Code 中使用 API key 时不工作"

**用户的命令**：
```bash
curl -s "https://api.github.com/user" -H "Authorization: token $GITHUB_TOKEN" | jq .login
```

**预期流程**：

1. 识别：环境变量 `$GITHUB_TOKEN` 与管道到 `jq`
2. 分析：带认证头的简单 GET 请求
3. 应用修复：将 curl 包装在 `bash -c` 中
4. 提供解决方案：
   ```bash
   bash -c 'curl -s "https://api.github.com/user" -H "Authorization: token $GITHUB_TOKEN"' | jq .login
   ```
5. 生成测试：`bash -c 'echo "Token: $GITHUB_TOKEN"' | head -c 10`

### 示例 2：用户的 POST 请求

**触发**："我的 POST 请求在 Claude Code 中使用 JSON 数据时失败"

**用户的命令**：
```bash
curl -s "https://api.example.com/data" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d '{"name": "test", "value": 42}' | jq .id
```

**预期流程**：

1. 识别：带 JSON body 和环境变量的复杂 POST
2. 分析：bash -c 中 JSON 的引号问题
3. 应用基于文件的方法：
   ```bash
   cat > /tmp/post_data.json << 'EOF'
   {"name": "test", "value": 42}
   EOF
   bash -c 'curl -s "https://api.example.com/data" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d @/tmp/post_data.json' | jq .id
   ```

### 示例 3：用户的循环和变量赋值

**触发**："我需要遍历 API 结果但变量不工作"

**用户的命令**：
```bash
for repo in $(curl -s "https://api.github.com/user/repos" -H "Authorization: token $GITHUB_TOKEN" | jq -r '.[].name'); do
  echo "Repository: $repo"
  STARS=$(curl -s "https://api.github.com/repos/$USER/$repo" -H "Authorization: token $GITHUB_TOKEN" | jq .stargazers_count)
  echo "Stars: $STARS"
done
```

**预期流程**：

1. 识别：循环中多处使用环境变量
2. 分析：循环迭代和变量赋值均受影响
3. 应用综合修复：
   ```bash
   for repo in $(bash -c 'curl -s "https://api.github.com/user/repos" -H "Authorization: token $GITHUB_TOKEN"' | jq -r '.[].name'); do
     echo "Repository: $repo"
     STARS=$(bash -c 'curl -s "https://api.github.com/repos/$USER/$repo" -H "Authorization: token $GITHUB_TOKEN"' | jq .stargazers_count)
     echo "Stars: $STARS"
   done
   ```

### 示例 4：教学请求

**触发**："为什么我的环境变量在 Claude Code 中使用管道时会消失？"

**预期流程**：

1. 解释 bug：Claude Code 预处理问题
2. 演示问题：
   ```bash
   # 这将展示问题
   export TEST_VAR="hello"
   echo "Direct: $TEST_VAR"
   echo "Piped: $TEST_VAR" | cat
   ```
3. 展示解决方案：
   ```bash
   bash -c 'echo "Fixed: $TEST_VAR"' | cat
   ```
4. 提供未来命令的通用指导

## 配置

此技能不需要持久化配置，但可以建议为常用模式创建别名：

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc 以便在 Claude Code 外使用
alias api-call='bash -c'
alias safe-curl='bash -c'
```

## 故障排除

常见问题及解决方案：

1. **bash -c 中的引号转义**：对复杂 JSON 使用基于文件的输入
2. **多个变量**：同一个 bash -c 中的所有变量都能正常工作
3. **命令替换**：应用相同的模式 `$(bash -c '...' | processing)`
4. **嵌套引号**：使用 heredoc 或临时文件避免引号嵌套问题

## 参考

- Claude Code GitHub Issues: #11225, #8318
- 相关文档：bash 子 shell、环境变量继承
- 替代方法：环境文件 sourcing、变量 export 模式