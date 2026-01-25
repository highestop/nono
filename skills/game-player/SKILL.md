---
name: game-player
description: This skill tells you how to play a game properly
---

## Game Parameters

- Before playing, you need to know the `<game-url>`, and give a `<game-name>`.
- `<game-cache-directory>` defaults to `~/.game-cache/`, unless explicitly told to use another directory

## Game Launch

- Use Playwright MCP to open browser and visit the `<game-url>` page to play this game.
  - First ensure MCP service is available. If Playwright MCP service is not installed, you can install it via `claude mcp add playwright npx '@playwright/mcp@latest'`.
  - You should play like a human by opening browser, observing and operating real browser pages, rather than writing scripts or using fetch tools to access pages.
- You must understand how to play this game based on page content, make decisions at each step yourself, don't ask me. You also need to judge whether the game succeeds or fails in the end, and exit the game when encountering success or failure.

## Process Recording and Experience Summary

- Create a directory named `<game-name>` under `<game-cache-directory>` as the main directory for this game.
- For each game session, create a `game-<index>` subdirectory in the main directory to store detailed process of this game session.
  - Game log file is `session.txt`, each line is a record, each line starts with `[timestamp]`.
  - You should record logs at each decision and action, including your current status, your thinking, your decisions.
  - After the game ends, whether successful or failed, you should create a `summary.txt` file in this game session directory to summarize the experience of this game.
- After the game ends, you should also iterate your knowledge and experience of this game in `game-guide.txt` in the main directory, helping you become a more experienced player.
- Before starting a new game, you should review summaries from all previous game sessions, learn from successful experiences and failed lessons, and enter the game with your latest and most advanced understanding and experience of this game.

### session.txt Reference

```txt
[2026-01-12 00:00:00] ..
[2026-01-12 00:00:01] ..
[2026-01-12 00:00:02] ..
[2026-01-12 00:00:03] ..
[2026-01-12 00:00:04] ..
```

### summary.txt Reference

```txt
Game Result: xx
Game Duration: xx
Game Token Consumption: xx

[Success Experience]:
(list them)

[Failure Experience/Improvement Suggestions]:
(list them)
```

### game-guide.txt Reference

```txt
[What kind of game is this]: (one sentence summary)
[What is the game objective]: (one sentence summary)

[What stages does the game have/what to do in each stage]:
(list them)

[Key decisions in different game stages/their importance estimation on game results]:
(list by groups, if there are decision factors of different dimensions, you can use tables to express their relationships, importance estimation should preferably be quantitative indicators)
```

## Other Rules

- Game log recording uses language consistent with the game. For example, if the game interface is in Chinese, then logs are in Chinese.
- Game cannot save/load, if encountering unexpected exit during gameplay, can only start over.
