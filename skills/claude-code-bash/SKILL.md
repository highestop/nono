---
name: claude-code-bash
description: This skill should be used when users need to execute bash commands with environment variables and pipes in Claude Code, especially when API calls fail with authentication errors despite correct tokens.
---

# Claude Code Bash Best Practices Skill

## Workflow

Execute the following steps when this skill is triggered:

### 1. Identify the Problem

- Check if the user's command involves environment variables (`$VAR`) with pipes (`|`)
- Look for symptoms:
  - API authentication failures despite correct tokens
  - Environment variables appearing empty in piped commands
  - Commands that work in terminal but fail in Claude Code
- Common problematic patterns:
  ```bash
  curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" | jq .
  ```
- Use AskUserQuestion tool to confirm: "Are you experiencing environment variable issues in Claude Code bash commands?"

### 2. Analyze User's Command

- Parse the user's existing command structure
- Identify components:
  - Commands that use environment variables
  - Pipe operations
  - JSON processing with jq
  - Complex quoting scenarios
- Categorize the use case:
  - Simple API calls
  - POST requests with JSON bodies
  - Variable assignments from command output
  - Loops with API calls
  - File uploads or downloads

### 3. Apply Fix Pattern

Based on the command type, apply the appropriate fix:

#### For Simple API Calls:
```bash
# Before (problematic)
curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" | jq .

# After (fixed)
bash -c 'curl -s "$API_URL" -H "Authorization: Bearer $TOKEN"' | jq .
```

#### For POST with JSON Body:
```bash
# Before (problematic)
curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" -d '{"key": "value"}' | jq .

# After (fixed) - using file approach
echo '{"key": "value"}' > /tmp/request.json
bash -c 'curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" -d @/tmp/request.json' | jq .
```

#### For Variable Assignment:
```bash
# Before (problematic)
RESULT=$(curl -s "$API_URL" -H "Authorization: Bearer $TOKEN" | jq -r '.data')

# After (fixed)
RESULT=$(bash -c 'curl -s "$API_URL" -H "Authorization: Bearer $TOKEN"' | jq -r '.data')
```

#### For Loops:
```bash
# Before (problematic)
for id in $(curl -s "$API_URL/list" -H "Authorization: Bearer $TOKEN" | jq -r '.[]'); do
  echo $id
done

# After (fixed)
for id in $(bash -c 'curl -s "$API_URL/list" -H "Authorization: Bearer $TOKEN"' | jq -r '.[]'); do
  echo $id
done
```

### 4. Provide Testing Commands

Generate test commands to verify the fix works:

```bash
# Test environment variable visibility
echo "Direct access: $YOUR_TOKEN"
echo "In pipe: $YOUR_TOKEN" | cat
bash -c 'echo "In bash -c: $YOUR_TOKEN"' | cat
```

### 5. Educational Explanation

Explain the technical background:

- **Root Cause**: Claude Code's bash preprocessing clears environment variables when pipes are used
- **Solution**: `bash -c '...'` creates a subshell that preserves variables
- **Best Practice**: Only wrap the command that needs variables, keep processing outside
- **Related Issues**: Reference GitHub issues #11225 and #8318

### 6. Generate Complete Solution

Provide the user with:
- The corrected command
- Testing steps to verify it works
- Template for similar future commands
- Common variations they might need

## Critical Rules

- Always wrap only the part of the command that uses environment variables in `bash -c '...'`
- Keep `jq` and other processing outside the `bash -c` wrapper for better readability
- Use file-based JSON input (`-d @file`) to avoid complex quote escaping
- Test the solution before providing it to the user
- Explain the reasoning behind the fix, not just the solution
- Use `--header` instead of `-H` for better compatibility
- Prefer `$VAR` over `${VAR}` unless braces are specifically needed

## Common Fix Patterns

### Pattern 1: Basic API Authentication
```bash
# Input: curl -s "$URL" -H "Authorization: Bearer $TOKEN" | jq .
# Output: bash -c 'curl -s "$URL" -H "Authorization: Bearer $TOKEN"' | jq .
```

### Pattern 2: Complex JSON Body
```bash
# Input: curl -s "$URL" -H "Auth: $TOKEN" -d '{"complex": "json"}' | jq .
# Output:
# echo '{"complex": "json"}' > /tmp/data.json
# bash -c 'curl -s "$URL" -H "Auth: $TOKEN" -d @/tmp/data.json' | jq .
```

### Pattern 3: Multiple Variables
```bash
# Input: curl -s "$BASE_URL/api" -H "Auth: $TOKEN" -H "X-User: $USER_ID" | jq .
# Output: bash -c 'curl -s "$BASE_URL/api" -H "Auth: $TOKEN" -H "X-User: $USER_ID"' | jq .
```

### Pattern 4: Command Substitution
```bash
# Input: ID=$(curl -s "$URL" -H "Auth: $TOKEN" | jq -r '.id')
# Output: ID=$(bash -c 'curl -s "$URL" -H "Auth: $TOKEN"' | jq -r '.id')
```

## Examples

### Example 1: User with failing API call

**Trigger**: "My curl command with API key isn't working in Claude Code"

**User's command**:
```bash
curl -s "https://api.github.com/user" -H "Authorization: token $GITHUB_TOKEN" | jq .login
```

**Expected flow**:

1. Identify: Environment variable `$GITHUB_TOKEN` with pipe to `jq`
2. Analyze: Simple GET request with authentication header
3. Apply fix: Wrap curl in `bash -c`
4. Provide solution:
   ```bash
   bash -c 'curl -s "https://api.github.com/user" -H "Authorization: token $GITHUB_TOKEN"' | jq .login
   ```
5. Generate test: `bash -c 'echo "Token: $GITHUB_TOKEN"' | head -c 10`

### Example 2: User with POST request

**Trigger**: "My POST request with JSON data fails in Claude Code"

**User's command**:
```bash
curl -s "https://api.example.com/data" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d '{"name": "test", "value": 42}' | jq .id
```

**Expected flow**:

1. Identify: Complex POST with JSON body and environment variable
2. Analyze: Quoting issues with JSON in bash -c
3. Apply file-based approach:
   ```bash
   cat > /tmp/post_data.json << 'EOF'
   {"name": "test", "value": 42}
   EOF
   bash -c 'curl -s "https://api.example.com/data" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" -d @/tmp/post_data.json' | jq .id
   ```

### Example 3: User with loop and variable assignment

**Trigger**: "I need to loop through API results but variables aren't working"

**User's command**:
```bash
for repo in $(curl -s "https://api.github.com/user/repos" -H "Authorization: token $GITHUB_TOKEN" | jq -r '.[].name'); do
  echo "Repository: $repo"
  STARS=$(curl -s "https://api.github.com/repos/$USER/$repo" -H "Authorization: token $GITHUB_TOKEN" | jq .stargazers_count)
  echo "Stars: $STARS"
done
```

**Expected flow**:

1. Identify: Multiple environment variable usage in loop
2. Analyze: Both loop iteration and variable assignment affected
3. Apply comprehensive fix:
   ```bash
   for repo in $(bash -c 'curl -s "https://api.github.com/user/repos" -H "Authorization: token $GITHUB_TOKEN"' | jq -r '.[].name'); do
     echo "Repository: $repo"
     STARS=$(bash -c 'curl -s "https://api.github.com/repos/$USER/$repo" -H "Authorization: token $GITHUB_TOKEN"' | jq .stargazers_count)
     echo "Stars: $STARS"
   done
   ```

### Example 4: Educational request

**Trigger**: "Why do my environment variables disappear when I use pipes in Claude Code?"

**Expected flow**:

1. Explain the bug: Claude Code preprocessing issue
2. Demonstrate the problem:
   ```bash
   # This will show the problem
   export TEST_VAR="hello"
   echo "Direct: $TEST_VAR"
   echo "Piped: $TEST_VAR" | cat
   ```
3. Show the solution:
   ```bash
   bash -c 'echo "Fixed: $TEST_VAR"' | cat
   ```
4. Provide general guidance for future commands

## Configuration

This skill doesn't require persistent configuration but may suggest creating aliases for commonly used patterns:

```bash
# Add to ~/.bashrc or ~/.zshrc for convenience outside Claude Code
alias api-call='bash -c'
alias safe-curl='bash -c'
```

## Troubleshooting

Common issues and solutions:

1. **Quote escaping in bash -c**: Use file-based input for complex JSON
2. **Multiple variables**: All variables in the same bash -c work fine
3. **Command substitution**: Apply the same pattern `$(bash -c '...' | processing)`
4. **Nested quotes**: Use heredoc or temporary files to avoid quote hell

## Reference

- Claude Code GitHub Issues: #11225, #8318
- Related documentation: bash subshells, environment variable inheritance
- Alternative approaches: environment file sourcing, variable export patterns