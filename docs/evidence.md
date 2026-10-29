# FocusBloom Curated Evidence Log

## Evidence boundary

This is a redacted, project-relevant evidence log rather than a chat transcript.
It contains no credentials, private filesystem paths, personal contact details,
research-participant information, or private account data. Planned behavior is
kept separate from observed static-design, local mocked implementation, and
publication checks.

## Prompt-to-result trace

| Prompt | Human authorization or decision | Files/artifacts produced | Checks actually performed |
| --- | --- | --- | --- |
| [`01-project-foundation.md`](../prompts/01-project-foundation.md) | Establish only the project foundation and durable boundaries | `README.md`, `AGENTS.md`, and six directories | Exact tree/count check; empty implementation directories; no Git, dependencies, database, credentials, provider, Figma, or application |
| [`02-part-3-1-research-decisions.md`](../prompts/02-part-3-1-research-decisions.md) | Approve paced 4–6 scope, fixed U.S. Support, five records, simplified API/RAG, accessibility rules, and deferred provider | Decision, Support, design-pipeline, verification, disclosure, and handoff records | Required records reread; official Support URLs checked; tree/content scans; implementation absence confirmed |
| [`03-direction-a-selection-and-figma-reference.md`](../prompts/03-direction-a-selection-and-figma-reference.md) | Human selected Direction A and supplied the selection rationale | Public editable comparison, selected section, 13 static reference frames, overview, and annotations | Historical-frame fingerprints; names/dimensions; controls, vectors, fonts, image fills, text coverage, contrast evidence, and screenshot review |
| [`04-part-3-1-submission-and-publication.md`](../prompts/04-part-3-1-submission-and-publication.md) | Create, audit, commit, publish, and publicly verify the Part 3.1 submission only | `report.md`, this evidence log, final publication records, and public Git history | Complete project/course reread; Figma metadata recheck; pre-Git and staged audits; local/remote SHA and unauthenticated public-link checks |
| [`05-part-3-2-foundation.md`](../prompts/05-part-3-2-foundation.md) | Authorize the Part 3.2 architecture and tested minimal Vue/FastAPI foundation on a feature branch | Implementation plan, pinned manifests, safe health/config backend, minimal accessible frontend, tests, and continuity updates | Exact Git/start gate; official Google model/pricing check; dependency integrity; backend tests/import/health; frontend tests/lint/build; safety and ignored-artifact audits |
| [`06-part-3-2-backend.md`](../prompts/06-part-3-2-backend.md) | Authorize the complete backend and supply the exact structural crisis/input decision after the initial safety stop | Five-table SQLite repository, 11-route FastAPI API, deterministic session validation, bounded Gemini adapter, 32-test suite, and continuity updates | Branch/start gate; focused/full tests; temporary-row snapshots; mocked call counts and failure matrix; dependency/import/diff and credential/generated-state audits |
| [`07-focusbloom-design-pivot.md`](../prompts/07-focusbloom-design-pivot.md) | Preserve Part 3.1 evidence while pivoting the active product, design, architecture, data, API, and model contract to FocusBloom | Editable FocusBloom Figma evolution, exact version-2 plan, low-input boundaries, scaffold branding, and continuity updates | Exact Git/start gate; Figma structure/screenshots; research sources; tests/build; repository rename and feature-branch publication |
| [`08-focusbloom-version-2-backend.md`](../prompts/08-focusbloom-version-2-backend.md) | Replace the legacy active backend with the complete approved FocusBloom version-2 backend | Nine-table schema, 22 API operations, explicit-save persistence, bounded Gemini adapter, read-only history RAG, 52-test suite, and continuity updates | Exact Git/start gate; schema/route inspection; focused and complete tests; mocked 0/1/2 call matrix; adversarial SQL/read-only checks; dependency and artifact audits |

## Consequential design comparison

Direction A emphasized a prominent central six-petal bloom and the water/leaf
atmosphere. Direction B emphasized timing clarity, explicit segmented progress,
organization, and accessibility cues. The human selected Direction A because it
communicated the intended identity more clearly and felt calmer, more immersive,
and more distinctive. The selected reference retained A as the direction while
adopting the named clarity features from B; no third direction was created.

## Failed or revised approaches

- The first Figma authentication later expired, so the connection check could
  not proceed. No design content was changed during that failure. After the human
  reauthenticated, the account/file read check succeeded and work resumed. No
  email or authentication value is retained here.
- The first selected-direction visual pass exposed malformed manually rotated
  bloom petals and clipped or overlapping completion/Support text. The affected
  blooms were replaced with editable SVG vectors, spacing was adjusted, overview
  previews were refreshed, and the visual and structural checks were repeated.
- The first data proposal used seven record types. Human review simplified it to
  five by storing Next-time setup on `exercise_sessions` and request lifecycle on
  the initiating `messages` record.
- The first foundation route-count assertion relied on route-object internals
  that changed in FastAPI 0.162, and the first Vue lint pass found 15 formatting
  warnings. The route assertion was changed to the generated OpenAPI path set,
  the component was formatted, and the complete checks then passed.

## Static Figma evidence

- File: https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx
- Selected section: https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=10-286
- Selected overview: https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=14-537
- Observed selected section name/dimensions: **04 / Selected Direction A**,
  2500×9200.
- Observed overview name/dimensions: **Selected Direction A / Overview**,
  2372×1650.
- Thirteen required selected frames were recorded at 390×844 or 1024×768,
  including standard inhale/exhale, No motion, completion, History, and Support.
- Final structural validation reported all 13 frames, zero image fills, zero
  missing fonts, 33 editable vector layers, and 48 control instances meeting the
  44×44 target minimum.

These are static design observations, not runtime evidence.

## Publication evidence

The substantive milestone was committed as
[`aa41c3bda8680439f05fcb68bc6945dff6dbd515`](https://github.com/srinidhid2004-design/breathbloom-skills/commit/aa41c3bda8680439f05fcb68bc6945dff6dbd515)
and pushed to the new public repository. At that checkpoint local `main` and
`origin/main` matched. Unauthenticated retrieval loaded the public repository,
commit, and raw report. Direct no-cookie HTTP retrieval returned status 200 for
the Figma file, selected section, and overview; the Figma browser view resolved
the named file and requested overview without a login or request-access screen.

The following documentation-only commit finalizes the public links and evidence.
Its SHA is intentionally reported outside its own content to avoid a self-
referential loop. The final response and public history identify it exactly. No
application, database, provider, credential, or runtime operation is part of this
evidence.

## Assignment 3.2 foundation evidence

- Feature branch start: `9f7a09d5ceb4fc50520e26ad6140103de3cc903e`.
- Approved provider/model: Google Gemini with stable
  `gemini-3.5-flash-lite`, confirmed against Google's official model, release,
  pricing, and rate-limit pages on October 27, 2026.
- Architecture decision: exactly five planned tables, 11 planned `/api` routes,
  and the exact ten-state top-level state machine recorded in
  `docs/part-3-2-implementation-plan.md`.
- Backend evidence: project-local Python 3.14.7 environment, `pip check` clean,
  three tests passed, FastAPI construction passed, only `/api/health` exposed,
  and the health response reported service `ok`, database `not initialized`, and
  Gemini key `not configured` without a secret/path/exception.
- Frontend evidence: two component tests passed, zero-warning lint passed,
  production build passed, direct dependency tree resolved, and production audit
  found zero vulnerabilities.
- Safety boundary: no credential, local environment file, database, record,
  live-model request, full selected UI, Figma edit, voice/audio feature, alternate
  provider, authentication, analytics, or vector database was added.

These results are local foundation evidence only. The later breathing sequence,
Support independence, persistence, history, model behavior, RAG, accessibility,
and integrated scenarios remain unverified.

## Assignment 3.2 backend evidence

- Implemented exactly five tables and 11 `/api` operations without adding a
  Support, classifier, authentication, location, provider-proxy, or generic SQL
  route.
- The accepted model body is structural only. Unknown/free-form fields produce
  the approved HTTP 422 message with no row mutation and no provider call. There
  is no keyword matching, sentiment inference, classifier, or crisis detection.
- Temporary-database tests observed preference update/reset, deterministic
  start/stop/complete, invalid no-mutation transitions, reopen persistence,
  foreign-key/identity constraints, ordered messages, duplicate prevention, and
  atomic fixed-profile reset.
- Injected mocks observed one call for success and each accepted provider failure;
  zero for missing configuration and invalid input; no second call for duplicate
  or failed-request reuse. Valid success stored two ordered rows. Accepted failure
  stored one failed user row and no assistant. Malformed output was not stored or
  returned as assistant text.
- SDK seam inspection observed fixed model `gemini-3.5-flash-lite`, 10-second
  timeout, one total attempt, and 256-token output cap. Application constants and
  tests establish five history rows, 4,096 context characters, and 600 validated
  response characters.
- Focused tests: 28 passed. Complete tests: 32 passed. `pip check`, application
  construction/11-operation inspection, and `git diff --check` passed. Two
  dependency deprecation warnings were recorded without changing dependencies.
- AutoLoop used one correction cycle for a test connection-mode error; it did not
  weaken the constraint assertion.

This is mocked/local backend evidence only. No live Gemini request, real key,
runtime SQLite database, frontend/Figma implementation, or real-distress testing
occurred. Static Support and ordinary exercise controls remain independent by
contract, but their frontend rendering is not yet implemented or verified.

## FocusBloom design-pivot evidence

### Decision and scope

The active product is FocusBloom. The original BreathBloom decision remains
visible in the submitted Part 3.1 report, prompt records 01–06, original Figma
sections, and Git history. The pivot motivation is recorded as user-reported
classroom differentiation input, not research evidence or an effectiveness claim.

The active scope is a low-input fictional coursework prototype with optional
Focus Garden attention activities, the formal one-minute Perspective Studio
cognitive reframe, optional fictional Perspective Lens, optional user-authored
Next-Step Seed, factual History Garden, bounded Garden Guide, and static
independent Support.

### Research evidence and limitations

Eight named primary sources were reviewed. Visual-search research concerns
selective attention rather than clinical outcomes. Digital-nature findings were
mixed across the reviewed studies. Reappraisal, distancing, and preliminary
third-person self-talk findings do not prove a benefit for this interface.
Implementation-intention evidence had heterogeneous and bias-sensitive effects,
so if–then planning remains optional and user authored. Affect labeling is not a
central/required step because its interaction with reappraisal is uncertain. The
full citations and product implications are in `docs/focusbloom-pivot.md`.

### Design evidence

- Existing Figma file key: `L09m1XZX6fNEmR2dqrBkcx`.
- Visible file name: **FocusBloom — Assignment 3 Design Evolution**.
- Historical top-level sections observed before the pivot remained in place.
- New section `21:594`, selected overview `27:719`, 16 required screen frames,
  and three reusable components were created as editable Figma content.
- Structural checks covered exact narrow/wide dimensions, overflow, fonts,
  placeholder text, 44×44 controls, primary-action count, and Support presence.
- Final visual review followed a targeted overview-note overlap repair.

This evidence establishes static editable-reference content only.

### Architecture evidence

The active plan defines exactly 17 major states, nine proposed version-2 tables,
and 22 proposed `/api` operations. Perspective alternatives are limited to one
Gemini request; factual history uses a maximum two-request read-only RAG flow.
The plan specifies allow-listed SQL, parameter binding, read-only enforcement,
20-row/8-column/8-KiB limits, 100-ms execution deadline, snapshot validation,
row-reference grounding, zero retries, no provider/model fallback, safe no-match,
and mutation rejection.

These are reviewed design contracts, not implemented behavior.

### Basic branding and local verification evidence

- Vue metadata/scaffold and frontend package metadata now use FocusBloom.
- FastAPI display title and sanitized public error messages use FocusBloom.
- Legacy breathing schema/routes/services were not rewritten or presented as the
  new implementation.
- Backend: `pip check` clean; 32 tests passed with two known non-failing dependency
  warnings.
- Frontend: 2 tests passed; zero-warning lint passed; production build passed.
- No runtime database, local environment file, credential value, live Gemini
  request, full product implementation, voice/audio change, or generated tracked
  artifact occurred.

### Repository continuity evidence

The existing public repository was renamed in place from `breathbloom-skills` to
`focusbloom`. The old URL visibly redirected to the new public URL, while main
remained at `9f7a09d5ceb4fc50520e26ad6140103de3cc903e`. The feature branch started
at `68d96d7f241184a062878a510132e911b67e4694`. The pivot commit SHA is reported
by the final response and public branch history to avoid a self-referential
documentation edit.

## FocusBloom version-2 backend evidence

- Active source now contains exactly the nine contracted version-2 tables and 22
  API operations. No breathing table, field, timing rule, or compatibility route
  remains in the runtime implementation.
- Temporary SQLite evidence covers schema/version/foreign-key checks, refusal to
  migrate version 1 implicitly, lifecycle states, ordered events, optimistic
  preferences, explicit artifact/seed save and deletion, reopen persistence,
  saved-text deletion, duplicate prevention, and atomic reset.
- The Gemini seam fixes `gemini-3.5-flash-lite`, a 10-second deadline, 384 output
  tokens, one attempt, and no alternate provider/model. Mock evidence distinguishes
  zero-, one-, and two-request outcomes; no generated Perspective text is saved
  without a separate explicit save request.
- History retrieval uses a strict non-CTE SELECT grammar, trusted profile binding,
  approved tables/columns/functions, read-only URI, query-only/trusted-schema
  pragmas, disabled extensions, default-deny authorizer, 100-ms progress deadline,
  snapshot check, and 20-row/8-column/8-KiB bounds. Mutation and schema-access
  cases were rejected before or by read-only execution.
- Only a validated grounded answer with valid returned row numbers creates an
  assistant message. Rejected SQL and zero-row retrieval stop after request one;
  invalid grounding and answer failure stop after request two without retry.
- Focused tests first reported 45 passing cases. After one hardening cycle and
  expanded lifecycle/call-count/output-safety coverage, the complete suite reported **52
  passed**. `pip check` reported no broken requirements.

This evidence is local and mocked. No runtime database, environment file, real
credential, live Gemini request, Figma change, frontend implementation, voice/
audio capability, or real-distress testing was created or performed.

## FocusBloom Vue experience evidence

- The active Vue source now implements the complete named state set and exact
  version-2 browser contracts. No React, Tailwind, TypeScript, state-management
  package, provider SDK, or new dependency was added.
- Focus Garden offers all seven backend activities without required typing. The
  runtime writes allow-listed events and terminal states, prevents repeated
  terminal actions, and records refresh/Support interruption without silently
  completing or resuming.
- Perspective work remains local until explicit save. Missing configuration and
  provider-safe failures preserve work; the user may continue with reviewed
  fictional alternatives. Lens and Next-Step Seed are optional and user
  controlled.
- History displays only factual records and saved indicators. Garden Guide uses
  suggested questions, exact two-step request fields, bounded result states, and
  a collapsed trace. SQL/parameters/retrieved rows are not fabricated because
  the approved public API intentionally withholds them.
- Static U.S. Support rendered from reviewed project wording without calling the
  API and remained available during active and failed states.
- Frontend checks reported **16 passed**, zero-warning lint, and a successful
  production build. The unchanged backend reported **52 passed** and a clean
  `pip check`.
- Automated browser inspection observed exact 390×844 and 1024×768 running
  frames, no application console warnings/errors, one-tap Focus behavior,
  neutral retry, Support interruption/focus restoration, missing-configuration
  fallback, and terminal Perspective history.

The browser backend used only a unique disposable database outside the project
and no Gemini key. No screenshot was retained, no project runtime database was
created or mutated, no real credential was read, no live Gemini request occurred,
and no Figma or historical Part 3.1 artifact changed.
