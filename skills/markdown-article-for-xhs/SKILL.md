---
name: markdown-article-for-xhs
description: 当用户提供一个小红书笔记 URL 时使用，将其转换为一个 GitHub issue。
---

将一篇小红书笔记转换为格式良好的 GitHub issue。继承 [@markdown-article](../markdown-article/SKILL.md) 的全部规则，并附加以下小红书特有的补充与覆盖项。

## 重要：URL 必须是静态短链

输入 URL **必须**是静态短链格式：

```
http://xhslink.com/o/<id>
```

例如 `http://xhslink.com/o/8Z2fmYgDoWW`

如果用户提供的是完整 URL（例如 `https://www.xiaohongshu.com/explore/...` 或 `https://www.xiaohongshu.com/discovery/item/...`），请要求用户改为提供短链。完整 URL 中的重定向参数是动态的，可能过期或加载失败。

## 重要：使用 xiaohongshu.day 提取内容

小红书页面要求登录、且有强烈的反爬措施。直接通过 `curl`、`WebFetch` 甚至 Playwright 访问都会被登录墙拦下。

**必须通过 Playwright MCP 使用第三方工具 [xiaohongshu.day](https://xiaohongshu.day)** 来提取笔记内容：

1. 导航到 `https://xiaohongshu.day`
2. 在输入框（placeholder 为「输入小红书笔记链接」的 textbox）中粘贴用户给的 URL，按回车提交
3. 等待内容加载完成（等待「处理中...」文本消失，超时约 15 秒）
4. 从加载后的结果中提取：
   - **作者名**：从作者信息区域
   - **标题**：从 `<h1>` 标题
   - **正文文字**：从笔记描述区域
   - **图片**：用 `page.evaluate` 查询所有 `src` 包含 `ci.xiaohongshu.com/spectrum/` 的 `<img>` 元素——这些就是笔记的内容图（跳过来自 `sns-avatar` 的头像图）

## 输出结构

issue 标题就是笔记标题。标签以 GitHub label 形式打上（见父技能）。正文使用标准的 metadata 块，「来源」写为 `<作者名>（小红书）`，原文链接使用短链：

```markdown
> - 来源：<作者名>（小红书）
> - 原文链接：http://xhslink.com/o/<short_link_id>

<笔记正文>

![](image_1_url)

![](image_2_url)

...
```

## 图片处理

- 图片 URL 来自 `ci.xiaohongshu.com/spectrum/` 域名，保留完整 URL，包括 query 参数
- 跳过作者头像图（来自 `sns-avatar-qc.xhscdn.com`）

### 单张图片处理（文字优先）

收集到全部内容图 URL 后，**用 Read 工具逐张查看图片**，把每张图归入下面两种类别中的**唯一一种**。每张图只按一种方式处理——绝不两种都做。

- **含任何文字**（标题叠层、说明字幕、幻灯片文字、要点列表、截图、手写笔记等）：把文字提取出来作为 markdown 正文内容，**不**保留这张图的 `![](url)` 引用。
- **纯视觉**（无可读文字的照片、插图、图表、示意图）：只保留 `![](url)` 引用。

文字优先——如果一张图既有视觉元素又有文字（例如带说明字幕的卡通画格、带叠加标题的照片），按文字图处理，只提取文字。

提取文字时，保留逻辑结构（标题、有序列表、无序列表）并遵循与文章其他部分一致的中英文间距规则。

## 示例

源 URL：`http://xhslink.com/o/2W8WlPz9aDE`
结果：在 `highestop/nono` 仓库中创建一个 issue，标题与笔记一致。参考：<https://github.com/highestop/nono/issues/4>
