---
name: mweb-to-obsidian
description: 使用此技能将 MWeb 数据迁移到 Obsidian
---

## 前期准备

* 确保在 MWeb 根目录下工作，记为 `<MWebRoot>`（根目录包含 `mainlib.db` 文件和 `docs/` 目录）
* 迁移目标目录 `<ObsidianRoot>` 为 `<MWebRoot>/Obsidian Vault`
* 创建三个目录：`<ObsidianRoot>/All Notes`、`<ObsidianRoot>/Attachments`、`<ObsidianRoot>/Migration Logs`

## 工作流程

扫描 `<MWebRoot>/docs` 下的每个 Markdown 文件（文件名形如 `<NoteID>.md`），记住这个 NoteID 直到该文件的所有相关工作完成，对每个文件执行以下操作：

* 执行 `note_category.sh` 脚本，传入笔记文件 ID，获取该笔记文件所有关联的分类全名
    * 如果找到多个，默认选择第一个
    * 如果没有找到，默认为 `/`
* 在 `<ObsidianRoot>/All Notes` 目录下创建与分类全名对应的目录名，如果是多级分类则创建所有层级的目录，然后将文件复制进去，注意不要移动或删除原始文件
* 检查新笔记文件内容是否包含本地文件引用（格式如 `![..](media/<NoteID>/<filename>)`）
    * 如果包含，在 `<MWebRoot>/docs/media/<NoteID>/` 目录中找到所有被引用的文件
    * 将这些文件复制到 `<ObsidianRoot>/Attachments/<NoteID>/`，注意不要移动或删除原始文件
    * 在笔记文件内容中，将文件引用路径替换为 `![](Attachments/<NoteID>/<filename>)`
* 在 `<ObsidianRoot>/Migration Logs` 中创建 `<NoteID>.txt` 文件，记录：
    * 基于 `<MWebRoot>` 的原始文件全名、新文件全名
    * 原始文件的所有分类全名
    * 原始文件的所有本地文件引用、新文件的所有文件引用

## 工作原则

* 不修改任何原始 MWeb 文件