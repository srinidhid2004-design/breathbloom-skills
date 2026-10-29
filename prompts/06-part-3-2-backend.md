# Prompt 06 — Complete Part 3.2 Backend

## Authorization and scope

On October 27, 2026, the human authorized implementation, automated verification,
commit, and publication of the complete Assignment 3.2 FastAPI, SQLite, and
bounded Gemini backend on `feature/assignment-3-part-2`. The selected Vue/Figma
interface remained out of scope. No live Gemini call, real credential, runtime
database, or Part 3.1 report change was authorized.

The implementation started from published feature SHA
`55371b8576a5174ab5a026763f1d11374234cb1c`; local and remote feature refs matched,
the worktree/index were clean, and `main`/`origin/main` remained
`9f7a09d5ceb4fc50520e26ad6140103de3cc903e`.

## Human-approved crisis/input boundary

The initial implementation prompt was paused because the earlier project records
did not define crisis-input handling precisely enough. The human then supplied
this exact implementation decision:

- do not implement keyword matching, sentiment analysis, a crisis classifier, or
  model-based crisis detection;
- accept no arbitrary free-form model text;
- accept only `request_kind` (`introduction`, `reflection`, or
  `history_summary`), a session ID and approved reflection choice where required,
  and a UUID idempotency key;
- reject unknown or structurally invalid fields with HTTP 422 and the exact safe
  message recorded in `backend/app/errors.py`;
- make zero provider calls and zero database writes for such rejected requests;
  return API outcome `invalid_request` and persist no database outcome;
- keep static Support access entirely outside FastAPI, SQLite, and Gemini; and
- state the limitation exactly as
  `Coursework prototype; not therapy or medical advice.`

This deterministic structural boundary cannot detect or classify crisis content.
That is intentional. It prevents free-form content from entering this optional
model path and does not replace the independent static Support interface.

## Implemented result

The backend now initializes exactly five SQLite tables during application
lifespan: `demo_profiles`, `preferences`, `exercise_sessions`, `conversations`,
and `messages`. It uses `PRAGMA user_version = 1`, foreign keys on every
connection, a 5,000-ms busy timeout, explicit write transactions, parameterized
values, one fixed fictional profile, optimistic versions, unique client/request
identifiers, deterministic message ordinals, and an atomic profile reset.

The exact API surface is:

1. `GET /api/health`
2. `GET /api/preferences`
3. `PUT /api/preferences`
4. `POST /api/sessions`
5. `PATCH /api/sessions/{session_id}`
6. `GET /api/sessions`
7. `GET /api/sessions/{session_id}`
8. `POST /api/conversations`
9. `GET /api/conversations/{conversation_id}/messages`
10. `POST /api/conversations/{conversation_id}/messages`
11. `POST /api/demo/reset`

Session validation preserves the fixed 4-second inhale, 6-second exhale,
six-cycle, 60-second contract. Pause, resume, stop, complete, interrupt, and
optional Next-time setup are explicit versioned actions. Completion requires at
least 60,000 observed-active milliseconds, exactly six cycles, and the completed
6,000-ms exhale boundary. Stop and interrupted states remain distinct terminal
facts with fewer than six cycles.

The optional model path uses only Google Gemini model
`gemini-3.5-flash-lite`. Limits are one total SDK attempt (zero retries), no
fallback, a 10,000-ms timeout, at most five recent session rows, at most 4,096
serialized context characters, at most 256 output tokens, and at most 600
validated response characters. The structured response has exactly
`response_text`, `response_kind`, and `limitation`; unknown fields, blank/trimmed
text, mismatched kinds, HTML, URLs, and prohibited claims fail safely. Raw
provider responses and errors are never stored or returned.

## Verification and AutoLoop

All backend checks use temporary databases, fake keys, and injected mocked
gateways. The success case makes exactly one mocked provider call. Every accepted
provider-failure case makes exactly one mocked call. Missing configuration and
structurally invalid requests make zero calls. Reusing a request ID makes no
second call and creates no duplicate message.

The focused and complete backend suite finished with 32 passing tests. It covers
schema/constraints, foreign keys, preferences/reset, session state and timing,
idempotency, reopen persistence, ordered messages, model success, malformed
output, all six provider failure classes, the structural input boundary, SDK
attempt configuration, failed-attempt persistence, safe errors, health, and
construction without database/config access. `pip check`, import/construction,
and Git whitespace checks also passed.

One bounded AutoLoop correction was needed: the first schema-constraint test
attempted its deliberate invalid write through a read-only connection. The
constraint assertion was preserved and moved to a normal repository connection;
the affected test and full suite then passed. An earlier command-path typo looked
for a root `.venv`; it did not reach test collection and was corrected to the
existing `backend/.venv` path.

## Evidence boundary

No live Gemini request occurred. No real key or local `backend/.env` was read or
created. Tests created only operating-system temporary databases; the ignored
runtime `data/app.sqlite3` was not opened or mutated. No frontend/Figma, voice,
audio, authentication, analytics, alternate provider, or vector-database work
occurred. `report.md` remained unchanged.
