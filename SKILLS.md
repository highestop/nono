# Skills

| Skill | Description |
|------|------|
| [budget-export-csv-formatter](skills/budget-export-csv-formatter/SKILL.md) | Transform UTF-8, tab-separated CSV exports from the Shark Bookkeeping Pro App into categorized billing-analysis CSV files. Use when aggregating that app's transactions by type, category, and description; do not use for arbitrary CSV schemas or exports from other bookkeeping apps. |
| [mweb-db-exporter](skills/mweb-db-exporter/SKILL.md) | Export all tables from an MWeb mainlib.db SQLite database as JSON with schema and record summaries. Use for MWeb data analysis, backup, migration, integration, or integrity debugging; operate read-only and do not use for non-MWeb databases or requests that require export files. |
| [mweb-media-reference-checker](skills/mweb-media-reference-checker/SKILL.md) | Audit an MWeb document library for missing media references and unreferenced media files, then guide user-approved cleanup. Use for integrity checks, routine maintenance, or post-migration cleanup; do not modify documents or delete files without explicit confirmation. |
| [mweb-to-obsidian](skills/mweb-to-obsidian/SKILL.md) | Migrate an MWeb library to an Obsidian vault by copying notes and attachments, recreating category paths, rewriting copied media links, and recording migration logs. Use when converting an MWeb root containing mainlib.db and docs/; never modify, move, or delete the original MWeb files. |
| [open-meteo-forecast](skills/open-meteo-forecast/SKILL.md) | Query weather forecasts with the unauthenticated Open-Meteo Forecast API. Use for hourly or daily weather data such as temperature, precipitation, precipitation probability, and wind speed by coordinates or location; do not use for tasks requiring a commercial SLA, official weather alerts, or another specified weather provider. |
| [play-web-game](skills/play-web-game/SKILL.md) | Autonomously play a browser-based web game through rendered-page interaction while recording session logs and reusable strategy notes. Use when the user provides a game URL and wants the agent to play until success or failure; do not use scripted or fetch-based gameplay, saved states, or non-browser games. |
| [pr-commit](skills/pr-commit/SKILL.md) | Manage GitHub code changes from environment checks through conventional commits, push, pull-request creation and tracking, check or review remediation, and user-confirmed merge. Use when asked to commit or push changes, create or track a PR, address PR feedback, or merge a ready PR; never commit directly to main or merge without confirmation. |
| [skill-writer](skills/skill-writer/SKILL.md) | Create and revise Agent Skills-compliant skills, including metadata, directory structure, interaction design, preference configuration, and examples. Use when creating, converting, or editing a skill; do not use for general documentation, rules, or non-skill agent files. |

---

*This document was automatically generated based on commit [`c35c722f1662ab7c6e4b0be764cb6ac92283840a`](https://github.com/highestop/nono/commit/c35c722f1662ab7c6e4b0be764cb6ac92283840a).*
