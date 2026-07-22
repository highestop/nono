---
name: play-web-game
description: Play a web game
---

## Game parameters

- Before starting, obtain the `<game-url>` and assign a `<game-name>`.
- `<game-cache-directory>` defaults to `~/.game-cache/` unless another directory is explicitly specified

## Start the game

- Use the Playwright MCP to open a browser, visit `<game-url>`, and play the game.
  - First ensure that the current agent's Playwright MCP or browser-automation tool is enabled. If unavailable, install or enable Playwright using the current agent's MCP configuration method.
  - Play like a human by opening a browser and observing and interacting with the actual rendered page. Do not write scripts or use a fetch tool to access the page.
- Infer how to play from the page content and make every decision yourself without asking me. Determine whether the final outcome is a success or failure, and exit the game when either outcome occurs.

## Session records and lessons learned

- Create a directory named `<game-name>` under `<game-cache-directory>` as the game's root directory.
- For each game session, create a `game-<index>` subdirectory under the root directory to store the session details.
  - Use `session.txt` as the game log, with one entry per line and each line beginning with `[timestamp]`.
  - Log every decision and action, including your current state, reasoning, and decision.
  - When the game ends, whether in success or failure, create `summary.txt` in the session directory to summarize what you learned.
- After the game, iteratively update your knowledge and experience in `game-guide.txt` under the root directory to become a more capable player.
- Before starting a new game, review the summaries of all previous sessions. Learn from successful strategies and failed attempts, then begin with your latest and deepest understanding of the game.

### `session.txt` reference format

```txt
[2026-01-12 00:00:00] ..
[2026-01-12 00:00:01] ..
[2026-01-12 00:00:02] ..
[2026-01-12 00:00:03] ..
[2026-01-12 00:00:04] ..
```

### `summary.txt` reference format

```txt
Game Result: xx
Game Duration: xx
Game Token Consumption: xx

[Successful Strategies]:
(List each item)

[Failed Attempts/Improvement Suggestions]:
(List each item)
```

### `game-guide.txt` reference format

```txt
[What Kind of Game Is This]: (One-sentence summary)
[What Is the Goal]: (One-sentence summary)

[Game Stages/What to Do in Each Stage]:
(List each item)

[Key Decisions by Game Stage/Estimated Importance to the Outcome]:
(List by group. If decisions have multiple dimensions, use a table to show their relationships. Prefer quantitative importance estimates.)
```

## Additional rules

- Write game logs in the same language as the game. For example, if the game interface is in Chinese, write the logs in Chinese.
- Do not save or load game state. If the game exits unexpectedly, restart from the beginning.
