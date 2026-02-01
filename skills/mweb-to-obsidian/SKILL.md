---
name: mweb-to-obsidian
description: Use this skill to migrate MWeb data to Obsidian
---

## 工作前准备

* 确保在 MWeb 根目录作为 `<MWebRoot>` 开始工作（根目录下有 `mainlib.db` 文件和 `docs/` 目录）
* 迁移的目标目录 `<ObsidianRoot>` 为 `<MWebRoot>/Obsidian Vault`
* 创建 `<ObsidianRoot>/All Notes`、`<ObsidianRoot>/Attachments`、`<ObsidianRoot>/Migration Logs` 三个目录

## 工作流

扫描 `<MWebRoot>/docs` 下的每个 Markdown 文件（文件名如 `<NoteID>.md`），记住这个 NoteID 直到处理完这个文件相关的所有工作，对每个文件进行如下操作：

* 执行 `note_category.sh` 脚本，传入笔记文件 ID，获得笔记文件所有相关联的分类全名
    * 如果找到多个，默认选择第一个
    * 如果没找到，默认为 `/`
* 在 `<ObsidianRoot>/All Notes` 目录下创建分类全名对应的目录名，如果是多层目录要全部创建出来，然后将文件复制到其中，注意不要移动或删除原文件
* 查找新的笔记文件内容中是否包含本地文件引用（格式类似 `![..](media/<NoteID>/<文件名>)`）
    * 如有，在 `<MWebRoot>/docs/media/<NoteID>/` 目录下，找到所有引用的文件
    * 将这些文件复制到 `<ObsidianRoot>/Attachments/<NoteID>/` 下，注意不要移动或删除原文件
    * 在笔记文件内容中，替换文件引用的路径为 `![](Attachments/<NoteID>/<文件名>)`
* 在 `<ObsidianRoot>/Migration Logs` 中创建一个 `<NoteID>.txt` 的文件，记录：
    * 基于 `<MWebRoot>` 的原文件完整名、新文件完整名
    * 原文件的所有分类全名
    * 原文件的所有本地文件引用、新文件的所有文件引用

## 工作原则

* 不要修改原 MWeb 的任何文件