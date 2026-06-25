---
name: markdown-article-for-xhs
description: Use when user provides a Xiaohongshu (小红书) note URL to convert into a local markdown file.
---

Convert a Xiaohongshu note page into a well-formatted markdown file. Inherits all rules from [@markdown-article](../markdown-article/SKILL.md), with the following Xiaohongshu-specific additions and overrides.

## IMPORTANT: URL must be a static short link

The input URL **must** be in the static short link format:

```
http://xhslink.com/o/<id>
```

e.g. `http://xhslink.com/o/8Z2fmYgDoWW`

If the user provides a full URL (e.g. `https://www.xiaohongshu.com/explore/...` or `https://www.xiaohongshu.com/discovery/item/...`), ask the user to provide the short link instead. Full URLs from redirects contain dynamic parameters that may expire or fail to load.

## IMPORTANT: Use xiaohongshu.day for content extraction

Xiaohongshu pages require login and have aggressive anti-scraping measures. Direct access via `curl`, `WebFetch`, or even Playwright will be blocked by login walls.

**You must use the third-party tool [xiaohongshu.day](https://xiaohongshu.day) via Playwright MCP** to extract note content:

1. Navigate to `https://xiaohongshu.day`
2. Type the user-provided URL into the input box (the textbox with placeholder "输入小红书笔记链接") and press Enter
3. Wait for the content to load (wait for "处理中..." text to disappear, timeout ~15s)
4. Extract from the loaded result:
   - **Author name**: from the author info section
   - **Publish date**: from the date display
   - **Title**: from the `<h1>` heading
   - **Body text**: from the note description area
   - **Images**: use `page.evaluate` to query all `img` elements whose `src` contains `ci.xiaohongshu.com/spectrum/` — these are the note's content images (skip avatar images from `sns-avatar`)

## File location override

The filename uses an `xhs-` prefix followed by the short link ID (the last path segment of the short link URL):

```
<project_root>/articles/2026-03-19/xhs-8Z2fmYgDoWW.md
```

## Output structure

```markdown
# <note title>

> - 来源：<author name>（小红书）
> - 日期：<publish date>
> - 原文链接：http://xhslink.com/o/<short_link_id>
> - 标签：<tag1>, <tag2>, <tag3>

---

<note body text>

![](image_1_url)

![](image_2_url)

...
```

## Image handling

- Image URLs are from `ci.xiaohongshu.com/spectrum/` domain, keep the full URL including query parameters
- Skip the author avatar image (from `sns-avatar-qc.xhscdn.com`)

### Text-heavy image detection

Many Xiaohongshu notes use images that are primarily text (e.g. slides, lists, tips). After collecting all content image URLs, **use the Read tool to view each image** and judge whether each image is predominantly text or visual content.

- For text-heavy images (text slides, bullet points, numbered lists, text screenshots): extract the text and insert it as markdown body content with proper formatting. Do not include the image reference.
- For visual images (photos, illustrations, charts, diagrams): keep the `![](url)` reference.
- Use your best judgement on a per-image basis — e.g. a cover photo followed by text slides is fine: keep the cover as an image, extract the rest as text.
- When extracting text, preserve the logical structure (headings, numbered lists, bullet points) and follow the same CJK spacing rules as the rest of the article.

## Example

Source URL: `http://xhslink.com/o/8Z2fmYgDoWW`
Output path: `<project_root>/articles/2026-03-19/xhs-8Z2fmYgDoWW.md`
