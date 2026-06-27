# Nono

My personal momo (claw/claude/codex agent).

## Usage

Recommended setup:

- Clone this project under `~/` and name the directory `.agents`, so global agent environments such as claw, claude, and codex can all pick it up.
- In the directory where you usually keep projects, such as `~/Workspace`, create a `nono` symlink that points to `~/.agents` for quick access to the Git project.
- If you use zsh, add commonly used agent and workspace shortcuts to `~/.zshrc`:

  ```zsh
  # claude
  alias cc="claude --dangerously-skip-permissions"
  alias ccu="npm i -g @anthropic-ai/claude-code@latest"

  # codex
  alias cdx="codex --sandbox danger-full-access --ask-for-approval never"
  alias cdxu="npm i -g @openai/codex@latest"

  # zsh
  alias zshrc="code ~/.zshrc"

  # workspace
  alias ws="cd ~/Workspace"
  ```
