---
name: markdown-article-for-x
description: 当用户提供一个 X（Twitter）Article URL 时使用，将其转换为一个 GitHub issue。
---

将一篇 X Article 页面转换为格式良好的 GitHub issue。继承 [@markdown-article](../markdown-article/SKILL.md) 的全部规则，并附加以下 X 特有的补充与覆盖项。

## 重要：必须使用 Playwright MCP

X 页面完全由 JavaScript 渲染。`curl`、`WebFetch` 等静态抓取方式**无法**取到任何文章内容。**必须**使用 Playwright MCP 加载并提取页面。

## X 特有步骤

导航到页面之后：

1. 在进入 Focus mode 之前先提取元数据：
   - **作者显示名**：从页面 title（格式 `<name> on X: "..."`）或指向作者主页的链接文本中获取
   - **用户名**：从 URL 路径中获取（例如 `x.com/HiTw93/status/...` 中的 `HiTw93`）
2. 如果页面有「Focus mode」链接（`/article/` 路径），导航到它以获得更干净的版面
3. 移除 X 特有的界面噪声：粉丝数、「Sign up」、「Log in」、互动指标、「Want to publish your own Article?」等

## 图片处理

- 用 `page.evaluate` 查询所有 `src` 包含 `pbs.twimg.com/media/` 的 `<img>` 元素，提取所有内容图
- 把图片 URL 中的 `name=small` 替换为 `name=large` 以获得高分辨率
- 跳过非内容图：头像、图标、表情图、装饰用 UI 图
- 用 `![](url)` 语法在文章正文中保留图片在原始位置

## 输出结构

issue 标题就是文章标题。标签以 GitHub label 形式打上（见父技能）。正文使用标准的 metadata 块，含 X 特有字段：

```markdown
> - 来源：<作者显示名>（X @username）
> - 原文链接：<原文 URL>

<带内联图片的 markdown 正文>

![](https://pbs.twimg.com/media/...)

<更多文字和图片...>
```

## 示例

源 URL：`https://x.com/HiTw93/status/2032091246588518683`
结果：在 `highestop/nono` 仓库中创建一个 issue，标题与文章一致。
