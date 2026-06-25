---
name: markdown-article-for-x
description: Use when user provides an X (Twitter) Article URL to convert into a local markdown file.
---

Convert an X Article page into a well-formatted markdown file. Inherits all rules from [@markdown-article](../markdown-article/SKILL.md), with the following X-specific additions and overrides.

## IMPORTANT: Playwright MCP required

X pages are fully JavaScript-rendered. `curl`, `WebFetch`, and other static fetching methods **cannot** retrieve any article content. You **must** use Playwright MCP to load and extract the page.

## X-specific steps

After navigating to the page:

1. Extract metadata before entering Focus mode:
   - **Author display name**: from the page title (format `<name> on X: "..."`) or from the link text pointing to the author's profile
   - **Username**: from the URL path (e.g. `HiTw93` from `x.com/HiTw93/status/...`)
   - **Publish date**: from the `<time>` element's `datetime` attribute
2. If the page has a "Focus mode" link (`/article/` path), navigate to it for a cleaner layout
3. Remove X-specific UI noise: follower counts, "Sign up", "Log in", engagement metrics, "Want to publish your own Article?", etc.

## Image handling

- Extract all content images from the article using `page.evaluate` to query `img` elements whose `src` contains `pbs.twimg.com/media/`
- Replace `name=small` with `name=large` in image URLs for high resolution
- Skip non-content images: profile avatars, icons, emoji images, and UI decoration images
- Preserve images at their original positions in the article body using `![](url)` syntax

## File location override

The filename uses an `x-` prefix followed by the article ID:

- `x-<id>`: the `<id>` is extracted from the URL path (the last segment), e.g. for `https://x.com/HiTw93/status/2032091246588518683` the ID is `2032091246588518683`

```
<project_root>/articles/2026-03-14/x-2032091246588518683.md
```

## Output structure

```markdown
# <article title>

> - 作者：<author display name>（X @username）
> - 日期：<publish date>
> - 原文链接：<original URL>
> - 标签：<tag1>, <tag2>, <tag3>

---

<markdown body with inline images>

![](https://pbs.twimg.com/media/...)

<more text and images...>
```

## Example

Source URL: `https://x.com/HiTw93/status/2032091246588518683`
Output path: `<project_root>/articles/2026-03-14/x-2032091246588518683.md`

## IMPORTANT: Validation

Article constraints are enforced by CI via `articles/__tests__/test-articles-content.py`. When modifying this skill, review and update the validation script to keep it consistent with the skill's requirements.
