---
name: mweb-to-obsidian
description: Migrate an MWeb library to an Obsidian vault by copying notes and attachments, recreating category paths, rewriting copied media links, and recording migration logs. Use when converting an MWeb root containing mainlib.db and docs/; never modify, move, or delete the original MWeb files.
---

## Preparation

* Work from the MWeb root directory, represented by `<MWebRoot>`, which contains the `mainlib.db` file and the `docs/` directory
* Set the migration target directory `<ObsidianRoot>` to `<MWebRoot>/Obsidian Vault`
* Create three directories: `<ObsidianRoot>/All Notes`, `<ObsidianRoot>/Attachments`, and `<ObsidianRoot>/Migration Logs`

## Workflow

Scan every Markdown file under `<MWebRoot>/docs`, with filenames in the form `<NoteID>.md`. Retain the NoteID until all work related to that file is complete, and perform the following actions for each file:

* Run the `note_category.sh` script with the note file ID to retrieve the full names of all categories associated with that note file
    * If multiple categories are found, choose the first one by default
    * If none are found, default to `/`
* Under `<ObsidianRoot>/All Notes`, create a directory whose name corresponds to the full category name. For nested categories, create every level, then copy the file there. Do not move or delete the original file
* Check whether the new note file contains local file references in a form such as `![..](media/<NoteID>/<filename>)`
    * If it does, find every referenced file in `<MWebRoot>/docs/media/<NoteID>/`
    * Copy those files to `<ObsidianRoot>/Attachments/<NoteID>/`. Do not move or delete the original files
    * In the note content, replace each file-reference path with `![](Attachments/<NoteID>/<filename>)`
* Create `<NoteID>.txt` in `<ObsidianRoot>/Migration Logs` and record:
    * The full original and new filenames relative to `<MWebRoot>`
    * The full names of all categories for the original file
    * All local file references in the original file and all file references in the new file

## Working principle

* Do not modify any original MWeb files
