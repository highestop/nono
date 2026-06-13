---
name: markdown-article-tags-review
description: 审查并维护 highestop/nono 仓库中文章 issue 的 GitHub label，识别近义/重复 label 并建议合并、重命名或拆分。
---

审查并优化 `highestop/nono` 仓库中所有由 [@markdown-article](../markdown-article/SKILL.md) 系列技能创建的文章 issue 的 label 体系。本技能分析 label 一致性、识别近义 label，并建议合并或重命名。

## 范围

- 操作对象：`highestop/nono` 仓库中带 `稍后阅读` label 的所有 issue（即由 markdown-article 系列技能创建的文章 issue）
- 不修改 issue 标题、正文或评论，**只**操作 label
- `稍后阅读` 是固定 label，不参与近义合并分析

## 步骤

### 1. 收集 label 并做结构化分析

直接运行同目录下的脚本——它会调用 `gh` 拉取所有带 `稍后阅读` 的 issue，并输出：

- 各 label 出现次数（按频次降序）
- 仅出现 1 次的 label 列表
- **始终共现**的 label 对（出现 issue 集合完全相同，候选合并）
- **子集关系**（A 的 issue 集合 ⊂ B 的 issue 集合，候选去重或泛化）
- issue → labels 一览

```bash
python3 ${SKILL_DIR}/analyze_labels.py
```

跳过 `稍后阅读` label 自身。

### 2. 在脚本输出之上识别其他近义/重叠

脚本已经覆盖共现/子集这两类机械可识别的关系。在此基础上，人工再看一遍以下两类：

- **同概念不同表述**：如 `AI Agent` vs `Agent`、`软件工程` vs `工程实践`
- **语言变体**：英文 label 和它的中文等价词

每组标记出受影响的 issue。

### 3. 读取受影响 issue 的内容

对每个被标记的 label 组，读取所有相关 issue 的**完整正文**（而不仅是标题），用于判断 label 是否应合并、重命名或保持独立：

```bash
gh issue view <number> --repo highestop/nono --json title,body
```

issue 数量较多时，使用 Agent 工具并行读取。

### 4. 输出分析报告

向用户输出结构化报告：

```
## 标签分析报告

### 总览
- issue 总数：X
- label 总数：X（不含「稍后阅读」）
- 仅出现 1 次的 label：X

### 发现的问题

#### 1. 近义 label：`AI Agent` vs `Agent`
涉及 issue：
- #N <issue 标题>（当前 label：...）
- #N <issue 标题>（当前 label：...）

分析：<基于 issue 内容的分析>
建议：合并为 `Agent`

#### 2. ...

### 其他建议
- issue #N label 过少/过多
- issue #N 缺少与同主题 issue 的关联 label
```

### 5. 等待用户确认

用 `AskUserQuestion` 让用户选择：

- **全部接受**：应用所有建议
- **仅部分接受**：由用户指定哪些应用、哪些跳过
- **全部拒绝**：放弃所有建议，不做修改

### 6. 应用确认过的变更

对每个确认的变更，操作 GitHub label：

- **重命名 label**（最佳方式，会自动迁移所有引用）：
  ```bash
  gh label edit "<旧名>" --repo highestop/nono --name "<新名>"
  ```
- **合并 label**（把 A 合并到 B）：对所有带 A 的 issue 移除 A、加上 B；最后删除 A
  ```bash
  gh issue edit <number> --repo highestop/nono --remove-label "<A>" --add-label "<B>"
  gh label delete "<A>" --repo highestop/nono --yes
  ```
- **新增 label**：
  ```bash
  gh label create "<名称>" --repo highestop/nono
  ```
- **给 issue 加/删 label**：
  ```bash
  gh issue edit <number> --repo highestop/nono --add-label "<名称>"
  gh issue edit <number> --repo highestop/nono --remove-label "<名称>"
  ```

## 用户主动请求的 label 变更

当用户明确要求新增、删除、重命名某个 label 时：

1. **确定范围**：用 `gh issue list --repo highestop/nono --label "<目标>" --state all --limit 500 --json number,title,body` 找到所有受影响的 issue
   - **重命名 / 删除**：找出当前使用该 label 的所有 issue
   - **新增**：扫描所有 `稍后阅读` issue（label 还不存在，所以任何 issue 都是潜在候选）
2. **阅读并分析**：读取受影响 issue 的完整正文，判断用户的建议是否合理
3. **给出评估**：
   - 合理：列出每个受影响的 issue 和具体的 label 变更
   - 不合理：解释原因，提出更好的替代方案
   - 部分合理：拆分成可行和不可行的部分，附带理由
4. **等待确认**：用户批准前不应用任何变更

## 重要

- 本技能**只**操作 GitHub label——不修改 issue 标题、正文或评论
- 遵循中英文间距规范（例如 `AI 编程` 而不是 `AI编程`、`AI 芯片` 而不是 `AI芯片`）
- 合并 label 时，优先保留在更多 issue 中出现的名字
- 仅出现在 1 个 issue 中的 label 不一定有问题——取决于它是否具有筛选价值
- `稍后阅读` 是基础 label，不参与近义分析或合并
