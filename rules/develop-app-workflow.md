# App development workflow

This reusable workflow applies to developing a new app from an existing reference app or from screenshots, text and videos of a reference product.

**Mandatory order: (1) discover and record the reference product → (2) implement the new app → (3) write GWT cases against every feature and scenario recorded in Stage 1, with no omissions, and align every Then expected result with the evidence collected in Stage 1; then implement automated acceptance and pass every case. Complete each stage before starting any work in the next stage. Do not overlap stages or treat partial completion as permission to proceed.**

## Stage 1 — Discover features and collect evidence

Choose the evidence method according to what is available:

| Available reference | Required work | What the evidence establishes |
|---|---|---|
| A runnable app | Actually operate the app and complete feature and scenario discovery. Exercise normal paths, relevant states, boundaries, errors and interactions, including basic features. Record the actions and observed results for every scenario. | Behavior directly observed in the reference app under the recorded conditions. Source inspection, documentation or screenshots alone cannot replace operating an available app. |
| Screenshots, text or videos only | Inspect all supplied material and derive the closest supported feature descriptions, interaction flows and expected behavior. Cite the relevant image, passage, frame or timestamp. | Only what the material shows or describes. Explicitly distinguish supported observations from inferred behavior, proposed product decisions and details that the material cannot establish. Do not claim to have operated or verified an unavailable app. |

- Record the reference identity, version/environment where known, supplied materials, relevant settings, initial state, actions and outcomes. If references are mixed, record the evidence type per scenario and operate every applicable behavior available in the runnable app.
- Build a complete inventory for the requested product scope. Cover elementary functions as carefully as complex functions. Expand features into concrete scenarios rather than listing only screens or feature names.
- For many scenarios or complex behavior, organize records by product area/module, feature and workflow, then by state, boundary condition or interaction variant where useful. Maintain an index and stable feature/scenario identifiers. Avoid one unstructured document or an unexplained pile of attachments.
- Record reproducible starting data, actions, intermediate checkpoints and observable expected outcomes. Preserve screenshots, recordings or structured data when they establish the result. Record performance baselines and extension behavior when they are part of the product requirements.
- Where implementation code is available, inspect it and record useful dependencies, source locations and implementation details. Use these findings to support the product specification; they do not replace required app interaction evidence. When code is unavailable, record that limitation.
- Produce the product feature descriptions, interaction specification, acceptance expectations and implementation plan from this evidence. With material-only references, define the closest supported behavior and explicitly document the assumptions needed to make it implementable and testable.
- **Store all Stage 1 features and evidence inside the final app project.** Markdown documents with image/data attachments are an acceptable format. Use relative links and keep the files under version control so the delivered project retains the evidence independently of external issues or chats.

**Completion condition:** the full scoped inventory is reviewed, every scenario has a complete record and the product specification is ready to implement. For a runnable reference, all required scenario operations and evidence capture must be complete. For material-only references, all available material must be analyzed, evidence limits and inferred decisions must be explicit, and expected behavior must be sufficiently concrete for implementation and later testing. Unfinished runnable-app verification cannot be relabeled as inference to pass this condition.

## Stage 2 — Implement the app from the recorded specification

- Start only after Stage 1 is complete. Implement every recorded feature and interaction against the documented behavior, using reference implementation evidence where available.
- Associate implementation work with the product feature/scenario identifiers. Meet the specified platform, integration, extension, performance and delivery requirements.
- Keep the Stage 1 documents and attachments in the app project throughout development. Keep implementation details separate from the evidence of what the reference does.
- If a missing scenario, ambiguous requirement or contradiction is discovered, return to Stage 1 and complete the affected discovery and specification before proceeding. Do not invent acceptance expectations from the new app's current behavior.

**Completion condition:** every specified feature has a corresponding completed implementation, the app can run in its intended environment, and no required implementation work remains. Stage 3 provides the subsequent systematic automated acceptance; implementation completion alone is not final product acceptance.

## Stage 3 — Maintain GWT cases, implement automation and verify every case

Start only after Stage 2 is complete. Within this stage, complete and review the GWT case set and its fixture preparation before implementing the automated acceptance suite. Maintain the documents first when cases change later.

1. Maintain a categorized **Given–When–Then (GWT) case document set** in the app project. Cover every product feature and scenario from Stage 1 without omissions. Every Then expected result must align with the corresponding evidence collected in Stage 1. Each case must have a stable, unique `caseId`, a feature/scenario reference, evidence references, and explicit Given, When and Then statements. Record relevant environment, state, data and intermediate checkpoints. Preserve whether the expected behavior was observed or inferred from limited reference material.
2. Prepare fixture data in the GWT documents before writing the tests. Prefer machine-readable JSON/YAML blocks that tests can load directly. For large datasets, binary files or shared fixtures, keep one canonical data attachment in the project and reference it from the GWT case. Avoid separately maintained copies in documentation and test code.
3. Maintain a one-to-one mapping between **every GWT case** and its canonical automated acceptance test entry, with the exact `caseId` in the test name, for example `[TASK-CREATE-001] Create a task`. Each acceptance test must identify its corresponding GWT case unambiguously; unrelated case IDs must not be bundled into one aggregate passing test. Distinct acceptance scenarios need distinct case IDs. Repeated runs across environments are executions of the same case, with their environments reported separately.
4. Have tests load the documented fixture block or referenced data file, perform the GWT actions and assert the documented outcomes. A small project loader/parser may expose the data to the test framework. Derived data must be regenerated from that source; expected values must never be copied from the app's actual output to make a test pass.
5. Use the required interaction level: real app/browser/system interaction for user-facing behavior that depends on it, with supporting unit/API/component tests where useful. Supporting tests and large runner totals do not replace case-level acceptance coverage.
6. Run the complete acceptance suite for the delivered revision. Save results, case mappings and source/input identities in the project. Distinguish full-suite runs from focused reruns. Unexecuted, partial, skipped, stale or failing cases remain unaccepted. Verify applicable performance and integration requirements using the agreed conditions and available baseline.

**Completion condition:** every GWT case has its corresponding named automated acceptance test and passes for the delivered revision. Feature coverage, reference evidence, GWT expectations, shared fixture data, test names and result reports agree. No required case or unresolved failure is omitted from the final result.

## GWT and shared fixture example

The following is a case inside a project's GWT Markdown document. The evidence identifier is illustrative; a real case must point to an actual Stage 1 record.

### TASK-CREATE-001 — Create a task

- Feature: `TASK-CREATE`
- Evidence: Stage 1 record `TASK-CREATE-OBS-001`
- Given: the task list equals `fixture.initialState.tasks`.
- When: the user enters `fixture.input.title` and confirms task creation.
- Then: the task list equals `fixture.expected.tasks`, including task count, title and completion state.

```json
{
  "caseId": "TASK-CREATE-001",
  "fixture": {
    "initialState": { "tasks": [] },
    "input": { "title": "Buy milk" },
    "expected": {
      "tasks": [{ "title": "Buy milk", "completed": false }]
    }
  }
}
```

The test named `[TASK-CREATE-001] Create a task` loads this block by `caseId` and uses its initial state, input and expected data directly. Editing the fixture updates the data consumed by the test; there is no second handwritten fixture object in the test file.

## Repository organization and consistency

Use a structure appropriate to the product's size. For example:

```text
docs/
  reference/
    index.md
    <module>/features.md
    <module>/evidence/
  product/specification.md
  acceptance/
    index.md
    <module>.md
    fixtures/
tests/
  acceptance/
verification/
```

Maintain traceability in both directions:

`product feature/scenario → reference evidence → GWT caseId → documented fixture → named automated test → result for the delivered revision`

Consistency checks must detect missing feature/case coverage, duplicate case IDs, missing or unknown case IDs in acceptance test names, broken evidence/fixture links, data divergence and stale results. Generated summaries must derive from the maintained documents and actual reports.
