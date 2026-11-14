# App development workflow

This reusable workflow applies to developing a new app from an existing reference app or from screenshots, text and videos of a reference product.

**Mandatory order: (1) observe and record the reference product from the user's perspective, without reading implementation code or inferring features; stop to report the findings and evidence, revise the product feature list with the user, and obtain their explicit approval → (2) research implementation where useful and implement the approved product feature list → (3) write GWT cases against every feature and scenario in that approved list, with no omissions, and align every Then expected result with the Stage 1 evidence and any explicitly approved product adjustments; then implement automated acceptance and pass every case. Complete each stage before starting any work in the next stage. Do not overlap stages or treat partial completion as permission to proceed.**

## Stage 1 — Discover features and collect evidence

Act as a user or product practitioner exploring the reference app, or analyzing and consolidating the available valid material. This stage must produce a clear, concrete product feature list that meets the user's requirements. It is the foundation for all later development and acceptance, and requires the user's review and confirmation.

**Collect real, accurate information from the user's perspective. Do not inspect source code, decompiled bundles or internal implementation in this stage. Do not infer features, interactions or expected results from code, common conventions, prior experience or the new app's behavior.**

Choose the evidence method according to what is available:

| Available reference | Required work | What the evidence establishes |
|---|---|---|
| A runnable app | Actually operate the app through user-accessible entry points. Exercise normal paths, relevant states, boundaries, errors and interactions, including basic features. Record the actions and observed results for every scenario. | A scenario is collected only after its real user interaction and behavior evidence have been recorded. Documentation, supplied screenshots, direct calls to internal APIs and code analysis cannot substitute for operating the available app. |
| Screenshots, text or videos only | Inspect all supplied material from the user's perspective and record only features, interactions and results explicitly shown or described. Cite the relevant image, passage, frame or timestamp. | Evidence is limited to the supplied material. Mark anything not shown or described as unknown; do not invent missing behavior or claim to have operated an unavailable app. |

- Record the reference identity, version/environment where known, supplied materials, relevant settings, initial state, actions and outcomes. If references are mixed, record the evidence type per scenario and operate every applicable behavior available in the runnable app.
- Build the inventory through user-facing exploration of the requested product scope. Cover elementary functions as carefully as complex functions, including entry points, hover controls, selection and focus states, visual feedback, keyboard and pointer interactions, and resulting content changes. Expand observed features into concrete scenarios rather than listing only screens or feature names.
- For many scenarios or complex behavior, organize records by product area/module, feature and workflow, then by state, boundary condition or interaction variant where useful. Maintain an index and stable feature/scenario identifiers. Avoid one unstructured document or an unexplained pile of attachments.
- Record reproducible starting data, actions, intermediate checkpoints and observable expected outcomes. Preserve screenshots, recordings or structured data when they establish the result. Record performance baselines and extension behavior when they are part of the product requirements.
- Keep unverified questions and candidate scenarios separate from collected features. Every collected scenario must point to its actual interaction evidence or, for material-only references, the exact supporting material. A generated scenario list, inferred expected result or passing test in the new app does not establish reference behavior or discovery completeness.
- Prepare the proposed product feature list, interaction specification and acceptance expectations from this evidence for user review. Record gaps and unknowns explicitly; do not fill them with assumptions. Any change the user requests for the new product must be recorded separately from the reference behavior. Defer technical implementation research and planning to Stage 2.
- **Store all Stage 1 features and evidence inside the final app project.** Markdown documents with image/data attachments are an acceptable format. Use relative links and keep the files under version control so the delivered project retains the evidence independently of external issues or chats.

**Final step — stop and review with the user.** Report the analysis, observed behavior, evidence links, coverage and remaining uncertainties, and present the organized, concrete product feature list. Let the user decide which features to keep, remove or adjust. Revise the list, clarify expected behavior and collect further evidence where needed; repeat this review until the user explicitly confirms that the list meets their expectations. Do not start Stage 2, including implementation research or planning, while that confirmation is pending. Silence, elapsed time or approval of unrelated work is not approval of the feature list.

Keep the reference inventory and evidence intact. Save the reviewed product feature list, keep/remove/adjust decisions, final expected behavior, links to the reference scenarios, and the user's approval of that specific revision in the project. Mark approved deviations as product decisions, never as observed reference behavior. Removed features remain in the decision record but are outside implementation and acceptance scope. The approved list is the shared baseline for both later stages.

**Completion condition:** the full scoped reference inventory is reviewed and every collected scenario has a complete evidence-backed record. For a runnable reference, all required user interactions and evidence capture must be complete; unexecuted or partially observed scenarios remain incomplete. For material-only references, all supplied material must be reviewed, every recorded reference feature and result must have direct support, and unknowns and evidence limits must be explicit. Do not count inferred behavior as collected evidence or treat the number of proposed scenarios as proof of completeness. The final product feature list must have concrete expected behavior, no unresolved gap that prevents implementation or acceptance of its approved scope, and the user's explicit approval of its recorded revision. Evidence collection alone does not complete this stage.

## Stage 2 — Implement the app from the recorded specification

- Start only after Stage 1, including explicit user approval of the product feature list, is complete.
- At this stage, use all available implementation details as technical references. For locally installed apps, inspect their application packages or bundles, metadata, dependencies, bundled code, configuration and resources. For web apps and desktop apps that wrap web content, use developer tools to inspect their code, DOM and styles, available source maps, network behavior and runtime execution. Source repositories, technical documentation and other available implementation materials can also inform the work.
- Record the reference version, source locations, useful findings and any unavailable details. Use this research to prepare the implementation plan and guide architecture, dependency choices and implementation techniques. The approved product feature list remains the behavior baseline; implementation research does not establish or replace Stage 1 product behavior evidence.
- Implement every retained or adjusted feature and scenario against the approved Stage 1 list and its final expected behavior. Do not reintroduce removed features or change the approved scope on your own.
- Associate implementation work with the product feature/scenario identifiers. Meet the specified platform, integration, extension, performance and delivery requirements.
- Keep the Stage 1 documents and attachments in the app project throughout development. Keep implementation details separate from the evidence of what the reference does.
- If a missing scenario, ambiguous requirement or contradiction is discovered, return to Stage 1 and complete the affected discovery and specification before proceeding. Report any proposed scope or behavior change and obtain the user's approval of the revised list before implementing it. Do not invent acceptance expectations from the new app's current behavior.

**Completion condition:** every specified feature has a corresponding completed implementation, the app can run in its intended environment, and no required implementation work remains. Stage 3 provides the subsequent systematic automated acceptance; implementation completion alone is not final product acceptance.

## Stage 3 — Maintain GWT cases, implement automation and verify every case

Start only after Stage 2 is complete. Within this stage, complete and review the GWT case set and its fixture preparation before implementing the automated acceptance suite. Maintain the documents first when cases change later.

1. Maintain a categorized **Given–When–Then (GWT) case document set** in the app project. Cover every retained or adjusted feature and scenario in the user-approved Stage 1 list without omissions, and identify the approved revision. Every Then expected result must align with the corresponding Stage 1 evidence; where the user explicitly approved different product behavior, link that decision and assert its approved result without claiming reference parity. Each case must have a stable, unique `caseId`, a feature/scenario reference, evidence and applicable decision references, and explicit Given, When and Then statements. Record relevant environment, state, data and intermediate checkpoints. Preserve whether the evidence came from actual app interaction or supplied screenshots, text or video, including its limits; do not turn unknowns or inferred behavior into acceptance expectations. Removed features do not require acceptance cases.
2. Prepare fixture data in the GWT documents before writing the tests. Prefer machine-readable JSON/YAML blocks that tests can load directly. For large datasets, binary files or shared fixtures, keep one canonical data attachment in the project and reference it from the GWT case. Avoid separately maintained copies in documentation and test code.
3. Maintain a one-to-one mapping between **every GWT case** and its canonical automated acceptance test entry, with the exact `caseId` in the test name, for example `[TASK-CREATE-001] Create a task`. Each acceptance test must identify its corresponding GWT case unambiguously; unrelated case IDs must not be bundled into one aggregate passing test. Distinct acceptance scenarios need distinct case IDs. Repeated runs across environments are executions of the same case, with their environments reported separately.
4. Have tests load the documented fixture block or referenced data file, perform the GWT actions and assert the documented outcomes. A small project loader/parser may expose the data to the test framework. Derived data must be regenerated from that source; expected values must never be copied from the app's actual output to make a test pass.
5. Use the required interaction level: real app/browser/system interaction for user-facing behavior that depends on it, with supporting unit/API/component tests where useful. Supporting tests and large runner totals do not replace case-level acceptance coverage.
6. Run the complete acceptance suite for the delivered revision. Save results, case mappings and source/input identities in the project. Distinguish full-suite runs from focused reruns. Unexecuted, partial, skipped, stale or failing cases remain unaccepted. Verify applicable performance and integration requirements using the agreed conditions and available baseline.

**Completion condition:** every GWT case has its corresponding named automated acceptance test and passes for the delivered revision. The user-approved product feature list, feature coverage, reference evidence, approved adjustments, GWT expectations, shared fixture data, test names and result reports agree. No required case or unresolved failure is omitted from the final result.

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

`reference feature/scenario and evidence → user-approved product feature list and decision/revision → GWT caseId → documented fixture → named automated test → result for the delivered revision`

Consistency checks must detect unapproved scope changes, missing coverage of approved features/cases, duplicate case IDs, missing or unknown case IDs in acceptance test names, broken evidence/decision/fixture links, data divergence and stale results. Generated summaries must derive from the approved product feature list, maintained documents and actual reports.
