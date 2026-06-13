---
name: markdown-article-for-wx
description: 当用户提供一个微信公众号文章 URL 时使用，将其转换为一个 GitHub issue。
---

将一篇微信公众号文章转换为格式良好的 GitHub issue。继承 [@markdown-article](../markdown-article/SKILL.md) 的全部规则，并附加以下微信特有的补充与覆盖项。

## 重要：URL 必须是静态短链

输入 URL **必须**是静态短链格式：

```
https://mp.weixin.qq.com/s/<sn_hash>
```

例如 `https://mp.weixin.qq.com/s/7FcavO7t_2zBhVZEWlfaxg`

如果用户提供的是带 query 参数的长 URL（例如 `__biz`、`mid`、`sn`、`chksm`），请要求用户改为提供短链。带动态参数的长 URL 可能过期或加载失败。

## 重要：必须使用 Playwright MCP

微信文章页有强烈的反爬措施（验证码校验）。`curl`、`WebFetch` 等静态抓取方式**无法**取到文章内容。**必须**使用 Playwright MCP 加载并提取页面。

如果出现验证页（「环境异常」），点击「去验证」按钮，等待跳转完成。

## 微信特有步骤

导航到页面之后：

1. 等待文章内容完全加载（检查文章标题）
2. 从页面中提取元数据：文章标题、公众号名称（`nickname`）
3. 移除微信特有的界面噪声：分享按钮、二维码、「今日好文推荐」段落、「会议推荐」段落、广告横幅、评论区、投票组件等
4. 对话/采访类文章中，把发言人姓名加粗（例如 `**Jeremy Howard：**`）

## 图片处理

- 用 `page.evaluate` 查询所有 `data-src` 或 `src` 包含 `mmbiz.qpic.cn` 的 `<img>` 元素，提取所有内容图——这些就是文章中的内联图片
- 跳过非内容图：头像、二维码、广告横幅、打赏按钮、表情图（`res.wx.qq.com`）、图标
- 用 `![](url)` 语法在文章正文中保留图片在原始位置
- 把 `data-src` 属性（不是 `src`）作为图片 URL，因为微信用了图片懒加载

## 输出结构

issue 标题就是文章标题。标签以 GitHub label 形式打上（见父技能）。正文使用标准的 metadata 块，含微信特有字段：

```markdown
> - 来源：<公众号名称>（微信公众号）
> - 原文链接：<短链 URL>

<带内联图片的 markdown 正文>

![](https://mmbiz.qpic.cn/...)

<更多文字和图片...>
```

## 示例

源 URL：`https://mp.weixin.qq.com/s/7FcavO7t_2zBhVZEWlfaxg`
结果：在 `highestop/nono` 仓库中创建一个 issue，标题与文章一致。
