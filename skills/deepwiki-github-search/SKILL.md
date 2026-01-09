---
name: deepwiki-github-search
description: This skill should be used when the user asks to "search GitHub repository documentation", "find API documentation for a GitHub project", "get deepwiki information", or mentions needing to search repository information through deepwiki.com.
version: 1.0.0
---

# Deepwiki GitHub Search Skill

Search GitHub repository information through deepwiki.com to quickly obtain detailed documentation, API descriptions, code examples, and usage guides for any GitHub repository.

## How It Works

1. **Validate Input**: Ensure repository name follows `owner/repo` format and query is provided
2. **Construct URL**: Generate `https://deepwiki.com/owner/repo?q=query`
3. **Retrieve Content**: Use WebFetch tool to get page content
4. **Parse Results**: Extract API documentation, configuration instructions, usage examples
5. **Organize Output**: Present structured search result summaries

Accept two required parameters:
- **Repository name**: Must be in `owner/repo` format
- **Search query**: Specific question, keywords, or topic

## Examples

### Basic Usage
- `facebook/react "how to use useState"`
- `vercel/next.js "API routes configuration"`
- `microsoft/typescript "interface definition"`
- `vuejs/vue "组件通信"` (Chinese query)

### Error Handling Examples
- **Input**: `react useState` → **Error**: Repository format invalid, use `facebook/react`
- **Input**: `nonexistent/repo` → **Error**: Repository not found, check spelling
- **Input**: `facebook/react "obscure-feature"` → **Suggestion**: Try broader terms like "hooks"

### Response Format
```markdown
## Search Results for facebook/react: "useState"

### Summary
Found comprehensive documentation for React's useState hook...

### Key Points
- Hook declaration syntax
- State update patterns
- Best practices for state management

### Code Examples
[Relevant code snippets extracted from documentation]

### Related Resources
- Official React documentation links
- Related hooks and patterns
```

## Supported Query Types
- API usage documentation
- Configuration parameters
- Code examples and patterns
- Installation and setup guides
- Best practices and recommendations
- Multi-language queries (Chinese/English)

## Error Handling
- **Invalid Repository Format**: Guide user to correct `owner/repo` format
- **Repository Not Found**: Suggest checking repository name or existence
- **No Search Results**: Recommend alternative query methods
- **Network Errors**: Provide retry suggestions with corrected parameters

Use the WebFetch tool exclusively to construct deepwiki URLs, retrieve content, and extract structured information. Organize results in user-friendly format and maintain context for follow-up questions.