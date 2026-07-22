# Format

- Keep documentation content and structure as concise as possible to reduce context usage
    - Use lists instead of sections when the structure is simple
    - Avoid separate sections or files when an inline example is sufficient
- Use spaces to improve readability
    - Add spaces between Chinese and English text or numbers, such as `格式 Markdown` and `编号 1.0`
    - Add spaces inside full-width parentheses and around full-width dashes, such as `（ xx ）` and `xx —— xx`
- Use `<angle brackets>` or `{curly braces}` for placeholders and variables
- Use `inline code` syntax for technical terms, file names, and command names
- Use Markdown tables that adapt to content width; do not align columns vertically
- **Do not** include absolute paths that expose system paths or usernames
- Prefer `~/` or `$HOME` for home-directory references
- Choose project-file link targets according to the rendering context
    - In project-aware content, use `[@{file_path}](/{file_path})`, where `{file_path}` is relative to the project root
    - In external content, such as a `GitHub issue`, `PR`, `release`, chat, or email, use `[@{file_path}](https://github.com/{owner}/{repo}/blob/{ref}/{file_path})`
    - For `{ref}`, use the default branch for current links and a `commit SHA` for immutable links
