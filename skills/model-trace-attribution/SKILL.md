---
name: model-trace-attribution
description: Identify a language model with the ModelTrace web challenge by running each displayed prompt in an isolated subagent, pasting complete outputs, and reading the final attribution. Use when a user asks to test or attribute a model through ModelTrace; do not use for general model comparison without the page.
---

# ModelTrace Attribution

Use <https://xqy2006.github.io/ModelTrace/> to attribute a model from its response fingerprints. The page is the source of truth for the current challenge prompts, requested counts, input fields, and candidate model names.

The method uses several semantically empty integer-selection challenges as behavioral samples. ModelTrace compares the resulting number distributions with its fingerprint library and displays a ranked attribution probability. The sequences must remain independent and complete because editing or combining them changes the fingerprint being measured.

## Workflow

1. Open the page in a browser session and inspect the complete page. Read each challenge's `发送给待测模型` text and its matching `粘贴完整输出` textbox. Do not hardcode challenge prompts or counts.
2. Create one isolated subagent per challenge. Start each from a clean context; do not reuse the parent conversation, another challenge's output, or shared state. Send that subagent the exact challenge text. It must follow every constraint in that prompt, especially direct model completion without tools, code, calculators, search, APIs, or external random generators, and must produce the requested count, range, and format. Run similar-looking challenges independently.
3. Collect each subagent's complete raw response. Do not summarize, reorder, edit, deduplicate, or combine it. Validate the response as a complete numeric output: it must contain the requested number of integers and every integer must be in the stated range. Do not silently extract numbers from surrounding prose. If a response is invalid, rerun only that challenge in a fresh isolated subagent with the same prompt.
4. Paste the complete response into the textbox matching the same challenge index. Preserve the returned separators and line breaks when the page permits them. Confirm that no output was pasted into another challenge. Do not calculate until every challenge is populated and valid.
5. Click `计算归因概率`.
6. Read the result area. Report the exact `最可能模型`; include its displayed attribution probability, model family, and `有效查询` when available. If the result is incomplete or an error is shown, report that state instead of inferring a model.
7. State the page's limitation when relevant: the result ranks only models in the fingerprint library, so an out-of-library model can receive an arbitrary attribution. Preserve any additional caveat shown by the page.

## Browser and subagent constraints

- Prefer accessible labels and visible text over fragile element references. When using Okou Browser, initialize the session with `okou browser use --agent-session okou-browser`, then use `agent-browser --session okou-browser`; use the equivalent browser operations in other environments.
- Keep the three subagent conversations independent. Do not pass one challenge's answer, a previous attempt, or hidden parent context into another challenge. If the environment cannot create isolated subagents, explain that the required independent run cannot be completed rather than simulating independence in one context.
- Keep the raw responses only as long as needed for validation and pasting. Do not publish large numeric sequences in the final report unless requested.
