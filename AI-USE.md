# AI Use Disclosure

## Current disclosure

- **Project:** BreathBloom
- **Current milestone:** Assignment 3.2 complete backend checkpoint
- **Tools used:** OpenAI Codex and the official Figma MCP integration
- **Specific model identifier:** A more specific Codex model identifier is not
  exposed in the task or project settings available for this record, so none is
  inferred or invented.
- **Role:** Brainstorming, requirements synthesis, proposal drafting, official
  source verification, project planning, Figma design creation/review, static
  design validation, publication preparation, backend architecture and code/test
  generation, dependency selection, and documentation review.

Google Gemini and fixed `gemini-3.5-flash-lite` are implemented behind a bounded
backend-only adapter. Codex generated the five-table SQLite repository, exact
11-route FastAPI service, strict structural input models, deterministic session
validation, provider adapter, and temporary-database/mock test suite. No real key
was added or read and no provider API call occurred. Only mocked provider results
and failures were used. Figma was used only for prior editable static design
evidence; it did not run or test backend or application behavior.

Human decisions selected the BreathBloom name, paced 4–6 breathing skill,
water-garden design direction, exclusion of voice and audio, transparent
personalization approach, and coursework/safety boundaries. The human also
approved the Part 3.1 proposal with the data, API, RAG, Support, timing,
accessibility, and Figma refinements recorded in the decision file. Codex helped
draft and reconcile the proposal and checked the named official public pages; it
did not replace human approval or clinically validate the product.

## Activity log

| Date | Tool/model | Role | Artifact or decision | Human review | Evidence |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | OpenAI Codex; specific model identifier unavailable | Requirements synthesis and documentation drafting/review | Foundation and continuity documents; no application implementation | Approved project decisions were supplied by the human and retained as constraints | `README.md`, `AGENTS.md`, `docs/design-pipeline.md`, `docs/verification.md`, and `prompts/01-project-foundation.md` |
| 2026-10-27 | OpenAI Codex; specific model identifier unavailable | AI-assisted research/design proposal drafting, official-source verification, and approved-decision documentation | Assignment 3.1 wording, Support plan, timing/state behavior, five-record data plan, simplified API/RAG scope, accessibility rules, and Figma comparison plan; no implementation | Human approved the proposal subject to explicit refinements, including consolidation from seven to five records and removal of separate reflection/request-attempt records | `docs/part-3-1-decisions.md`, `docs/support-resources.md`, `docs/verification.md`, and `prompts/02-part-3-1-research-decisions.md` |
| 2026-10-27 | OpenAI Codex with official Figma MCP; specific Codex model identifier unavailable | Created two editable static design directions, expanded the selected direction, inspected metadata/screenshots, and repaired visual defects | Direction A/B comparison, human-selected Direction A, 13 selected reference screens, overview, annotations, and static accessibility/contrast evidence | The human explicitly selected Direction A and supplied the rationale; Codex retained A's atmosphere while incorporating named clarity cues from B | Figma file and `prompts/03-direction-a-selection-and-figma-reference.md` |
| 2026-10-27 | OpenAI Codex; Git 2.45.1; GitHub API and web interface | Prepared the redacted Part 3.1 report/evidence package, audited content, and performed the authorized publication workflow | Public repository, assessed milestone commit, final documentation commit, and public-link checks; no application implementation | The human explicitly authorized repository creation, commits, publication, and read-only public verification | `report.md`, `docs/evidence.md`, `docs/verification.md`, and `prompts/04-part-3-1-submission-and-publication.md` |
| 2026-10-27 | OpenAI Codex; Google AI official documentation; Python 3.14.7; Node.js 24.20.0 | Verified the stable free-tier-suitable model, finalized Part 3.2 architecture, generated minimal Vue/FastAPI foundations and tests, installed pinned dependencies, and ran local checks | `gemini-3.5-flash-lite` decision, 11-route/five-table/state plan, safe health/config foundation, minimal UI, and verification records; no key, database, live model call, or full application behavior | The human explicitly authorized Checkpoint 1 implementation and publication on the named feature branch | `docs/part-3-2-implementation-plan.md`, `docs/verification.md`, and `prompts/05-part-3-2-foundation.md` |
| 2026-10-27 | OpenAI Codex; Python 3.14.7; FastAPI/SQLite; Google Gen AI SDK with mocked gateway only | Implemented and tested the complete Part 3.2 backend, reconciled the human-approved structural crisis/input boundary, and prepared publication | Five-table schema, 11-route API, deterministic session persistence, conversation lifecycle, reset, bounded structured Gemini adapter, failure matrix, and continuity records | The human explicitly authorized the backend checkpoint and then supplied the missing exact crisis/input decision; no live call or frontend work was authorized | `backend/app/`, `backend/tests/`, `docs/verification.md`, and `prompts/06-part-3-2-backend.md` |

Add later dated entries for material AI-assisted changes, including the tool or
model identifier when it is actually available, its role, the affected artifact
or decision, the human review performed, and the supporting evidence.

## Failed or revised approaches

The initial AI-assisted proposal separated session reflections and request
attempts into their own records. Human review replaced that seven-record design
with five planned record types: Next-time setup is nullable session data, and a
bounded model request's lifecycle belongs to its initiating user message. The API
proposal was also consolidated around one validated session-action endpoint, and
an asynchronous request-status endpoint was removed unless later evidence shows
it is needed. These were design revisions rather than implementation failures;
application implementation had not started at that Part 3.1 checkpoint.

The first foundation verification used FastAPI route-object introspection that
no longer matched FastAPI 0.162's included-router wrapper, and the initial Vue
component formatting produced ESLint warnings. The health request itself and
frontend tests/build worked. The test was revised to assert the generated OpenAPI
path, the component was formatted, and the complete backend/frontend checks were
rerun successfully. This failed first pass is retained as evidence rather than
reported as an initial success.

The backend implementation paused before model-boundary work because the prior
records did not define crisis-related input precisely enough. The human resolved
that gap by prohibiting free-form model text and every keyword/sentiment/classifier
approach, requiring strict structural fields and zero-write/zero-call HTTP 422
rejection. During the subsequent AutoLoop, one database constraint test attempted
its deliberate invalid write through a read-only connection. The constraint
assertion was retained, the connection mode was corrected, and both the focused
test and full suite passed.

The first Figma connection attempt later expired and could not access the design.
After the human reauthenticated the integration, a read-only account/file check
succeeded and the design work continued. A later visual review found malformed
bloom geometry and clipped or overlapping completion/Support text; the affected
editable vectors and spacing were revised, then the structural and visual checks
were repeated. These are recorded as revised approaches rather than hidden as
successful first attempts.

## Disclosure and redaction rules

- Record AI assistance honestly and distinguish planning, mock evidence, and
  observed live behavior.
- Do not include credentials, secret values, personal information, research
  participant information, or private third-party content.
- Do not store raw chat exports. Keep only curated, relevant, redacted evidence.
- Do not invent model identifiers, provider selections, tests, or outcomes.
- Link evidence only when it is safe and appropriate for coursework review.
