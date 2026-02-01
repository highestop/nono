---
name: mweb-to-obsidian
description: Use this skill to migrate MWeb data to Obsidian
---

## Pre-work Preparation

* Ensure working in MWeb root directory as `<MWebRoot>` (root directory contains `mainlib.db` file and `docs/` directory)
* Migration target directory `<ObsidianRoot>` is `<MWebRoot>/Obsidian Vault`
* Create three directories: `<ObsidianRoot>/All Notes`, `<ObsidianRoot>/Attachments`, `<ObsidianRoot>/Migration Logs`

## Workflow

Scan each Markdown file under `<MWebRoot>/docs` (filename like `<NoteID>.md`), remember this NoteID until all related work for this file is completed, perform the following operations for each file:

* Execute `note_category.sh` script, pass in note file ID, get all associated category full names for the note file
    * If multiple are found, select the first one by default
    * If none are found, default to `/`
* Create directory name corresponding to category full name under `<ObsidianRoot>/All Notes` directory, create all directories if it's multi-level, then copy the file into it, be careful not to move or delete the original file
* Check if the new note file content contains local file references (format like `![..](media/<NoteID>/<filename>)`)
    * If so, find all referenced files in `<MWebRoot>/docs/media/<NoteID>/` directory
    * Copy these files to `<ObsidianRoot>/Attachments/<NoteID>/`, be careful not to move or delete the original files
    * In the note file content, replace file reference paths to `![](Attachments/<NoteID>/<filename>)`
* Create a `<NoteID>.txt` file in `<ObsidianRoot>/Migration Logs`, record:
    * Original file full name based on `<MWebRoot>`, new file full name
    * All category full names of the original file
    * All local file references of the original file, all file references of the new file

## Work Principles

* Do not modify any original MWeb files