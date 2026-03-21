---
name: article-tags-review
description: Analyze all article tags for consistency, find near-duplicate or overlapping tags, and suggest optimizations.
---

Review and optimize the tag system across all saved articles. This skill analyzes tag consistency, identifies near-duplicate tags, and suggests merges or renames.

## Steps

### 1. Collect all tags

Use Grep to search for `> - 标签：` lines across all articles in `<project_root>/articles/`. Parse each match to build:

- A **tag index**: tag name → list of article paths
- An **article index**: article path → list of tags

Skip `-en.md` files (bilingual English originals have no tags).

### 2. Identify near-duplicate or overlapping tags

Compare all tag pairs and flag groups that are potentially redundant:

- **Same concept, different wording**: e.g. `AI Agent` vs `Agent`, `软件工程` vs `工程实践`
- **Subset/superset**: e.g. `AI 编程` vs `Vibe Coding` (one is a subset of the other)
- **Language variants**: e.g. an English tag and its Chinese equivalent
- **Tags that always co-occur**: if two tags appear in exactly the same set of articles, they may be redundant

For each flagged group, note which articles are affected.

### 3. Read affected articles

For each flagged tag group, read the **full content** of all associated articles (not just titles). This is necessary to make informed decisions about whether tags should be merged, renamed, or kept separate.

Use the Agent tool to parallelize reading when there are many articles to review.

### 4. Present analysis

Output a structured report to the user:

```
## 标签分析报告

### 总览
- 文章总数：X
- 标签总数：X
- 仅出现 1 次的标签：X

### 发现的问题

#### 1. 近义标签：`AI Agent` vs `Agent`
涉及文章：
- article_1_title (当前标签: ...)
- article_2_title (当前标签: ...)

分析：<基于文章内容的分析>
建议：合并为 `Agent`

#### 2. ...

### 其他建议
- 文章 X 标签过少/过多
- 文章 X 缺少与同主题文章的关联标签
```

### 5. Wait for user confirmation

After presenting the report, **wait for user confirmation** before making any changes. The user may:

- Accept all suggestions
- Accept some and reject others
- Modify suggestions

### 6. Apply confirmed changes

For each confirmed change, edit the `> - 标签：` line in the affected article files. For bilingual pairs, only the main (Chinese) file has tags — `-en.md` files have no tags and should not be modified.

## User-requested tag changes

When the user explicitly requests to add, delete, or rename a tag:

1. **Collect scope**: Use Grep to find all potentially affected articles:
   - **Rename / delete**: find all articles currently using the tag
   - **Add**: search all articles (the tag doesn't exist yet, so any article could be a candidate)
2. **Read and analyze**: Read the full content of all affected articles, then evaluate whether the user's suggestion is reasonable
3. **Present assessment**:
   - If reasonable: list every affected article and the specific tag change for each
   - If not reasonable: explain why and suggest a better alternative
   - If partially reasonable: split into what works and what doesn't, with rationale
4. **Wait for confirmation**: Do not apply any changes until the user approves

## Important

- This skill only modifies the `> - 标签：` metadata line — never change article content
- Follow CJK spacing rules in tag names (e.g. `AI 编程` not `AI编程`)
- Use commas to separate tags (consistent with the article skill conventions)
- When merging tags, prefer the name that is more commonly used across articles
- A tag that only appears in one article is not necessarily a problem — it depends on whether it has filtering value
