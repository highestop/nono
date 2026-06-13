---
name: markdown-article
description: 当用户提供一个网页文章 URL 时使用，将其转换为一个 GitHub issue。
---

将一个网页文章转换为格式良好的 GitHub issue。

## 输入

一个有效的文章 URL，例如 `https://example.com/blog/some-article`

## 步骤

1. 抓取页面内容（优先使用 Playwright MCP；不可用时回退到 `curl` + Python `markdownify` / `BeautifulSoup`）
2. 从 `<article>`、`<main>` 或最相关的内容容器中提取文章正文
3. 将提取出的 HTML 转换为格式良好的 markdown：
   - 识别章节标题，设置正确的 `##` / `###` 级别
   - 用带语言提示的代码围栏包裹代码片段（` ```bash`、` ```json`、` ```yaml` 等）
   - 正确格式化列表、引用、表格、粗体/斜体
   - **重要**：保留所有图片在其原始位置，使用 `![](url)` 语法——不要跳过图片，文章必须包含插图
   - 移除界面噪声（导航、侧边栏、页脚、广告、分享按钮、评论区等）
   - **重要**：确保中文与英文/数字之间留有正确的空格（例如 `使用 Claude 编写代码` 而不是 `使用Claude编写代码`、`共 15 个功能` 而不是 `共15个功能`）
4. 如使用了 Playwright，关闭浏览器标签页
5. 创建 GitHub issue（见下文「输出」）

## 输出

通过 `gh issue create` 在目标仓库创建一个 GitHub issue：

- **仓库**：`highestop/nono`
- **标题**：与文章标题一致（即原本会作为 `# <文章标题>` 的那个标题——不要在 `--title` 中包含 `# ` 前缀）
- **正文**：

```markdown
> - 来源：<来源>
> - 原文链接：<原文 URL>

<markdown 正文>
```

标签**不**写入正文——它们以 GitHub label 的形式打在 issue 上（见下文「标签」）。

使用 heredoc 把正文传给 `gh issue create --body` 以保留格式，并通过 `--label` 传递标签（每个标签一个 flag）：

```bash
gh issue create --repo highestop/nono --title "<文章标题>" \
  --label "<tag1>" --label "<tag2>" --label "<tag3>" \
  --body "$(cat <<'EOF'
> - 来源：...
...
EOF
)"
```

创建完成后，把 issue URL 报告给用户。

### 翻译

如果原文是非中文（英文、日文等），**只创建一个 issue**：issue 正文使用**中文译文**（含 metadata 块），标签作为 label 打上；然后把**原文作为一条 comment 追加到这个 issue 上**。

```bash
gh issue comment <issue-url> --repo highestop/nono --body-file <path>
```

不要为原文单独建 issue。

## 标签

正文起草完后，生成最能代表文章核心主题的关键词标签。数量按文章而定——主题集中的文章 2–3 个即可，跨领域的文章可能需要 4–5 个。优先选择真正具有筛选价值的标签，而不是凑够固定数量。

标签以 **GitHub label** 形式打在 issue 上（不写入正文）。

规范：
- 标签是简洁的名词或名词短语（例如 `AI 编程`、`开源`、`数据中心`）
- 遵循同样的中英文间距规则（例如 `AI 芯片` 而不是 `AI芯片`）
- **必带标签**：所有由本技能创建的 issue 都必须打上 `稍后阅读` 标签（与生成的主题标签一起传入）。如果该标签不存在，按下文流程创建。
- 翻译类文章只给主 issue 打 label——译文以 comment 形式追加，不再单独打 label

### 把标签应用到 issue

1. 运行 `gh label list --repo highestop/nono --limit 200` 获取现有 label。
2. 对每个选定的标签，检查是否已存在（区分大小写完全匹配）。
3. 如果存在缺失的标签，先用 `AskUserQuestion` 列给用户确认；确认后用 `gh label create "<名称>" --repo highestop/nono` 创建（不传颜色/描述参数——交给 GitHub 用默认值）。
4. 把全部标签（已有 + 新建）通过重复的 `--label` 标志传给 `gh issue create`。

## 重要：长文章

`gh issue create --body` 可以接受较大的正文，单次调用一般足够。如果正文超出 CLI 参数大小或调用失败，回退到 `--body-file <path>`，使用 `/tmp/` 下的临时文件。**不要**把一篇文章拆成多个 issue。

## 重要：多篇文章

当一次请求里包含多个 URL 时，**串行处理**——一次创建一个 issue。**不要**使用并行 agent 或并发 Playwright 会话，会导致浏览器超时和失败。

## 终止条件

当 issue（以及翻译类文章对应的副 issue）创建完成、并把 URL 报告给用户后，任务结束。
