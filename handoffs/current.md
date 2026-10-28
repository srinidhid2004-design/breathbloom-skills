# Current handoff

- **Date:** October 28, 2026
- **Project:** FocusBloom
- **Milestone:** Assignment 3.2 — version-2 backend implementation
- **Branch:** `feature/assignment-3-part-2`
- **Checkpoint start SHA:** `3f1ca4d3f7c4aa3c970a370925a8ab72915a5d75`
- **Unchanged main SHA:** `9f7a09d5ceb4fc50520e26ad6140103de3cc903e`
- **Public repository:** https://github.com/srinidhid2004-design/focusbloom
- **Publication:** commit subject `Implement FocusBloom activity and model
  backend`; use branch history and the checkpoint response for its exact SHA.

## Implemented backend

Active source is the FocusBloom version-2 backend. It initializes exactly nine
tables at SQLite `user_version=2`: `demo_profiles`, `preferences`,
`activity_sessions`, `activity_events`, `perspective_artifacts`,
`next_step_seeds`, `conversations`, `messages`, and `model_requests`. A detected
version-1 or unversioned existing schema stops initialization; it is never
silently migrated, overwritten, or deleted.

OpenAPI contains exactly the 22 approved `/api` operations. The implementation
supports:

- transparent versioned preferences;
- seven static Focus Garden activities plus Perspective Studio session records;
- completed, stopped, skipped, and interrupted outcomes and ordered events;
- explicit Perspective artifact and Next-Step Seed save/delete;
- factual bounded history and stable IDs across API/SQLite;
- ordered history-guide conversations/messages;
- separate saved-text deletion and complete fixed-profile reset; and
- lifecycle-only model request records with no prompt, SQL, row, raw response,
  provider error, credential, or unsaved Perspective text storage.

No breathing field/table/route remains in active runtime code. Historical Part
3.1 and version-1 records remain unchanged; the earlier implementation remains
available in Git history.

## Model and RAG boundary

Google Gemini is fixed to `gemini-3.5-flash-lite`, a 10-second timeout, 384
output tokens, one total attempt, zero retries, and no provider/model fallback.
Perspective alternatives use one call at most, return no more than two bounded
alternatives, and are not saved automatically.

History RAG uses one SQL-proposal call and only uses a second grounded-answer
call for validated nonempty retrieval. The validator rejects CTEs, mutation,
DDL, schema access, comments, multiple statements, joins/subqueries/set
operations, unapproved tables/columns/functions, literal profile scope,
parameter mismatches, and limits above 20. Execution adds a read-only URI,
`query_only`, `trusted_schema=OFF`, disabled extensions, default-deny authorizer,
100-ms deadline, 20-row/8-column/8-KiB bounds, and a snapshot check. Only valid
retrieved row references can be persisted with a grounded assistant answer.

Request-count contract observed with injected fakes:

- invalid input or missing configuration: zero provider calls;
- Perspective accepted outcome: one call;
- history malformed/rejected/out-of-scope/no-match/request-one failure: one call;
- history success/invalid grounding/request-two failure: exactly two calls; and
- duplicate completed requests: no additional call.

## Observed verification

- First focused version-2 cycle: **45 passed**.
- Final complete backend suite: **52 passed** in the observed 4.25-second run.
- `pip check`: **No broken requirements found.**
- Import/compile and exact 22-operation OpenAPI inspection passed.
- `git diff --check`, protected-file scope, credential-pattern, generated/private
  artifact, runtime-state, and branch-ref audits passed before commit.
- One hardening cycle tightened differing-content idempotency and WHERE grammar;
  tests were strengthened rather than weakened.
- Two known non-failing dependency warnings remain: Starlette TestClient/httpx
  transition and a Google Gen AI Python 3.14 type-alias deprecation.
- `backend/.env` and `data/app.sqlite3` are absent; `data/` is empty.
- No runtime database, real credential, live Gemini request, Figma change,
  frontend implementation, voice/audio feature, merge, rebase, amend, force
  push, or `main` change occurred.

## Exact next task

Implement the 17-state FocusBloom Vue interface and static independent Support
route from the selected Figma reference, then integrate the version-2 API. Verify
keyboard/focus, 390-pixel reflow, 200% zoom, Standard/No-motion parity,
fictional/no-typing routes, cancellation and stale-response protection,
explicit save/delete/reset, failure preservation, and API/SQLite/UI agreement.
Do not make a live Gemini call without separate authorization.

This remains a fictional coursework prototype, not therapy, diagnosis, crisis
detection, monitoring, clinical validation, or evidence of emotion, attention,
improvement, or effectiveness. Voice and audio remain prohibited.
