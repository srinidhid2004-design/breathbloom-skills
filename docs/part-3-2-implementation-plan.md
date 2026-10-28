# FocusBloom Assignment 3.2 implementation contract

## Status and replacement boundary

This document is the authoritative contract for the active FocusBloom product as
of October 28, 2026. The nine-table version-2 backend, revised API, Perspective
adapter, and history RAG workflow are implemented on the Assignment 3.2 feature
branch and verified with temporary databases and mocked Gemini. The complete
FocusBloom Vue interface remains a later checkpoint. The prior version-1 backend
is preserved only in Git history and historical records.

FocusBloom is a fictional local coursework prototype, not therapy, diagnosis,
crisis detection, a monitored service, a validated intervention, or evidence of
attention, emotional state, or improvement. Tests and demonstrations use only
fictional input. Voice and audio remain prohibited.

## Layer responsibilities

- **Vue frontend:** renders Focus Garden, Perspective Studio, History Garden,
  Garden Guide, and static Support; owns interaction state, timers, visible
  instructions, answer evaluation for deterministic activities, focus,
  accessibility, request cancellation, and stale-response rejection.
- **FastAPI backend:** validates explicit contracts, enforces business rules,
  manages version-2 SQLite transactions, performs the only optional Gemini calls,
  validates model output and proposed SQL, and returns sanitized outcomes.
- **SQLite:** stores one fictional profile, transparent preferences, factual
  activity/session metadata, explicitly saved text, conversations/messages, and
  model-request lifecycle data. It is opened only by the backend.
- **Gemini:** may propose up to two perspective alternatives or participate in
  factual history RAG. It never controls activities, navigation, save state,
  support, or user action.
- **Static Support:** is frontend-owned and works without FastAPI, SQLite,
  Gemini, classification, geolocation, or user activity.

## Exact top-level state model

The frontend recognizes exactly these 17 major states:

1. `entry`
2. `focus-activity-ready`
3. `focus-activity-active`
4. `focus-activity-stopped`
5. `focus-activity-completed`
6. `perspective-entry`
7. `perspective-evidence`
8. `perspective-alternatives-loading`
9. `perspective-alternatives-ready`
10. `perspective-model-failed`
11. `next-step-seed`
12. `history`
13. `history-question-loading`
14. `history-answer-ready`
15. `history-no-match`
16. `history-query-rejected`
17. `support-open`

Support overlays the preceding state and returns to it. It never resumes an
activity or request automatically. Inhale, exhale, and breathing-cycle states
are historical version-1 concepts and are not active FocusBloom requirements.

## Interaction and asynchronous rules

- One primary action and one current instruction per screen.
- Focus Garden has a complete no-typing route with visible `Show me`, `Skip
  this`, `Stop`, and Support controls.
- The Perspective Studio fictional example requires no personal input. A custom
  path has at most one initial 280-character field.
- Inputs remain visible while they are needed; important state is not remembered
  only from a prior view.
- Each async request has a UUID, AbortController/cancellation boundary, originating
  screen/state version, and current-session identity. Late, cancelled, duplicate,
  prior-screen, or reset responses cannot alter current state or persistence.
- Entering Support cancels or suspends nonessential UI work; returning never
  restarts it automatically.
- Provider failure leaves user input in local state and offers a deterministic
  status message plus `Continue without Gemini`; it does not synthesize a model
  fallback.
- Standard and No-motion modes expose the same text, controls, task state, and
  results. No-motion uses no scale, ripple, fade, or translation.
- Significant view changes may focus a heading with temporary `tabindex="-1"`;
  ordinary text is not tabbable. Controls follow visual order and have visible
  focus. Status announcements are restrained.

## Implemented version-2 SQLite schema — nine tables

All IDs are application-generated UUID text. Timestamps use UTC ISO 8601 with
milliseconds. Boolean values are `INTEGER CHECK (value IN (0,1))`. Foreign keys
are enabled on every connection. Text limits are enforced in request validation
and repeated with database checks where practical. No table stores diagnosis,
inferred mood, crisis classification, location, authentication, API keys, hidden
scores, prompts, system instructions, raw provider output, or raw provider errors.

### 1. `demo_profiles`

`profile_id TEXT PRIMARY KEY`, `display_label TEXT NOT NULL`,
`schema_version INTEGER NOT NULL CHECK(schema_version = 2)`,
`reset_version INTEGER NOT NULL DEFAULT 0 CHECK(reset_version >= 0)`,
`created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`.

Exactly one fixed fictional profile is permitted.

### 2. `preferences`

`profile_id TEXT PRIMARY KEY REFERENCES demo_profiles(profile_id) ON DELETE CASCADE`,
`motion_mode TEXT NOT NULL CHECK(motion_mode IN ('standard','no_motion'))`,
`guidance_level TEXT NOT NULL CHECK(guidance_level IN ('minimal','standard','more'))`,
`difficulty TEXT NOT NULL CHECK(difficulty IN ('easy','standard','challenge'))`,
`remember_preferences INTEGER NOT NULL`, `version INTEGER NOT NULL CHECK(version >= 1)`,
`last_idempotency_key TEXT UNIQUE`, `updated_at TEXT NOT NULL`.

The UI explains what is stored before setting `remember_preferences=1`.

### 3. `activity_sessions`

`session_id TEXT PRIMARY KEY`, `profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE`,
`client_session_id TEXT NOT NULL UNIQUE`, `activity_type TEXT NOT NULL` checked
against the seven approved Focus Garden types plus `perspective_studio`,
`status TEXT NOT NULL CHECK(status IN ('active','completed','stopped','skipped','interrupted'))`,
`started_at TEXT NOT NULL`, `ended_at TEXT`,
`duration_ms INTEGER NOT NULL DEFAULT 0 CHECK(duration_ms >= 0)`,
`difficulty TEXT NOT NULL`, `motion_mode TEXT NOT NULL`,
`guidance_level TEXT NOT NULL`,
`perspective_progress TEXT NOT NULL DEFAULT 'none' CHECK(perspective_progress IN ('none','interpretation','evidence','alternative','reviewed'))`,
`alternative_save_state TEXT NOT NULL DEFAULT 'none' CHECK(alternative_save_state IN ('none','saved','deleted'))`,
`seed_save_state TEXT NOT NULL DEFAULT 'none' CHECK(seed_save_state IN ('none','saved','deleted'))`,
`model_status TEXT NOT NULL DEFAULT 'skipped' CHECK(model_status IN ('skipped','loading','succeeded','failed','no_match','query_rejected'))`,
`version INTEGER NOT NULL DEFAULT 1 CHECK(version >= 1)`,
`created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`.

No mental-health meaning is assigned to these factual fields.

### 4. `activity_events`

`event_id TEXT PRIMARY KEY`, `session_id TEXT NOT NULL REFERENCES activity_sessions(session_id) ON DELETE CASCADE`,
`client_event_id TEXT NOT NULL UNIQUE`, `ordinal INTEGER NOT NULL CHECK(ordinal >= 0)`,
`event_type TEXT NOT NULL` checked against an application allow-list,
`happened_at TEXT NOT NULL`, `elapsed_ms INTEGER NOT NULL CHECK(elapsed_ms >= 0)`,
`payload_json TEXT NOT NULL DEFAULT '{}' CHECK(length(payload_json) <= 2048)`,
`created_at TEXT NOT NULL`, `UNIQUE(session_id, ordinal)`.

Payload is schema-validated activity metadata, never arbitrary user text.

### 5. `perspective_artifacts`

`artifact_id TEXT PRIMARY KEY`, `profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE`,
`session_id TEXT REFERENCES activity_sessions(session_id) ON DELETE SET NULL`,
`client_artifact_id TEXT NOT NULL UNIQUE`,
`interpretation_text TEXT NOT NULL CHECK(length(interpretation_text) BETWEEN 1 AND 280)`,
`supporting_evidence_json TEXT NOT NULL CHECK(length(supporting_evidence_json) <= 2048)`,
`uncertainty_json TEXT NOT NULL CHECK(length(uncertainty_json) <= 2048)`,
`alternative_text TEXT NOT NULL CHECK(length(alternative_text) BETWEEN 1 AND 240)`,
`alternative_source TEXT NOT NULL CHECK(alternative_source IN ('user','gemini','fictional_example'))`,
`observer_mode TEXT NOT NULL CHECK(observer_mode IN ('none','fictional_alex'))`,
`saved_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`.

The row is created only after explicit preview and Save. Before that, perspective
text remains frontend memory only. Deleting the row removes saved text while the
session may retain only `alternative_save_state='deleted'`.

### 6. `next_step_seeds`

`seed_id TEXT PRIMARY KEY`, `profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE`,
`session_id TEXT REFERENCES activity_sessions(session_id) ON DELETE SET NULL`,
`client_seed_id TEXT NOT NULL UNIQUE`,
`situation_text TEXT NOT NULL CHECK(length(situation_text) BETWEEN 1 AND 180)`,
`action_text TEXT NOT NULL CHECK(length(action_text) BETWEEN 1 AND 180)`,
`formatted_plan TEXT NOT NULL CHECK(length(formatted_plan) <= 400)`,
`source TEXT NOT NULL CHECK(source IN ('user','template','gemini_format'))`,
`saved_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`.

The action is always user chosen. Deletion hard-deletes text and changes the
session's factual save state to `deleted` in the same transaction.

### 7. `conversations`

`conversation_id TEXT PRIMARY KEY`, `profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE`,
`client_conversation_id TEXT NOT NULL UNIQUE`,
`purpose TEXT NOT NULL CHECK(purpose IN ('history_guide'))`,
`created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`.

Perspective calls do not persist a conversation unless the resulting artifact is
explicitly saved.

### 8. `messages`

`message_id TEXT PRIMARY KEY`, `conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE`,
`ordinal INTEGER NOT NULL CHECK(ordinal >= 0)`,
`role TEXT NOT NULL CHECK(role IN ('user','assistant'))`,
`content TEXT NOT NULL CHECK(length(content) BETWEEN 1 AND 600)`,
`created_at TEXT NOT NULL`, `UNIQUE(conversation_id, ordinal)`.

Only bounded history questions and validated grounded answers are stored. An
assistant row is inserted only after validated output persists successfully.

### 9. `model_requests`

`request_id TEXT PRIMARY KEY`, `profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE`,
`conversation_id TEXT REFERENCES conversations(conversation_id) ON DELETE CASCADE`,
`initiating_message_id TEXT REFERENCES messages(message_id) ON DELETE CASCADE`,
`response_message_id TEXT REFERENCES messages(message_id) ON DELETE SET NULL`,
`idempotency_key TEXT NOT NULL UNIQUE`,
`purpose TEXT NOT NULL CHECK(purpose IN ('perspective_alternatives','history_sql','history_answer','seed_format'))`,
`status TEXT NOT NULL CHECK(status IN ('accepted','succeeded','failed','no_match','query_rejected','cancelled'))`,
`safe_error_code TEXT`, `input_hash TEXT NOT NULL`,
`model_name TEXT NOT NULL CHECK(model_name = 'gemini-3.5-flash-lite')`,
`attempt_count INTEGER NOT NULL CHECK(attempt_count IN (0,1))`,
`retrieved_row_refs_json TEXT CHECK(length(retrieved_row_refs_json) <= 4096)`,
`created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`.

This table stores lifecycle and idempotency facts, not raw provider errors or
unsaved Perspective Studio content. Related writes use explicit transactions.

Indexes cover profile/time session history, session event order, profile/time
saved artifacts and seeds, conversation message order, and request idempotency.

## Migration strategy

No runtime `data/app.sqlite3` existed at implementation, so version 2 was built
and tested as a clean schema rather than preserving breathing-specific runtime
compatibility. The initializer uses one transaction to create the nine version-2
tables, seed the one fictional profile and explained defaults, set
`PRAGMA user_version = 2`, and validate foreign keys before commit.

If a runtime version-1 file is unexpectedly found, migration must stop. The
developer must decide whether to export fictional data or reset it; code must not
silently translate, overwrite, or delete breathing rows. Tests use temporary
databases and must cover initialization rollback, reopen, reset, and constraints.

## Implemented exact `/api` surface — 22 operations

| # | Method and route | Responsibility |
| ---: | --- | --- |
| 1 | `GET /api/health` | Sanitized service/database/key configuration status only |
| 2 | `GET /api/preferences` | Read explained fictional-profile preferences |
| 3 | `PUT /api/preferences` | Versioned, idempotent preference update/reset choice |
| 4 | `GET /api/focus-activities` | Static allow-listed activity metadata and instructions |
| 5 | `POST /api/activity-sessions` | Idempotently create a factual activity session |
| 6 | `PATCH /api/activity-sessions/{session_id}` | Versioned stop/complete/skip/interrupt update |
| 7 | `POST /api/activity-sessions/{session_id}/events` | Append an allow-listed idempotent activity event |
| 8 | `GET /api/activity-sessions` | Bounded factual history with simple filters/cursor |
| 9 | `GET /api/activity-sessions/{session_id}` | One session plus bounded ordered events |
| 10 | `POST /api/perspective/alternatives` | Ephemeral bounded Gemini alternatives; no automatic save |
| 11 | `POST /api/perspective-artifacts` | Explicitly previewed/idempotent artifact save |
| 12 | `GET /api/perspective-artifacts` | Bounded saved-artifact list for current demo profile |
| 13 | `DELETE /api/perspective-artifacts/{artifact_id}` | Delete saved text; retain explained metadata state |
| 14 | `POST /api/next-step-seeds` | Explicitly previewed/idempotent seed save |
| 15 | `GET /api/next-step-seeds` | Bounded saved seed list |
| 16 | `DELETE /api/next-step-seeds/{seed_id}` | Delete saved seed text transactionally |
| 17 | `POST /api/conversations` | Create an idempotent history-guide conversation |
| 18 | `GET /api/conversations/{conversation_id}/messages` | Bounded ordered stored history questions/answers |
| 19 | `POST /api/conversations/{conversation_id}/messages` | Store a validated bounded history question request |
| 20 | `POST /api/garden-guide/history-questions` | Run the validated two-request history RAG workflow |
| 21 | `DELETE /api/demo/saved-text` | Confirmed deletion of saved artifacts, seeds, and messages while retaining explained session metadata |
| 22 | `POST /api/demo/reset` | Confirmed atomic reset of all fictional-profile children and preferences |

Support has no backend route. No generic provider proxy or arbitrary SQL route is
permitted.

## Gemini workflow A — perspective alternatives

Input is one interpretation (1–280 characters), zero to three supporting-evidence
cards (each at most 180 characters), zero to three uncertainty cards (each at
most 180 characters), and observer mode `none` or `fictional_alex`. The UI shows
the payload before submission. Unsaved text remains in memory and is not logged.

One request at most uses `gemini-3.5-flash-lite`, a 10-second deadline, 384 output
tokens, zero retries, and no provider/model fallback. Strict JSON output contains
one or two alternatives (each at most 240 characters), one factual basis for each
(at most 180 characters), and the exact limitation `Coursework prototype; not
therapy or medical advice.` Output may not include advice, diagnosis, emotion,
crisis inference, treatment, effectiveness, action selection, or navigation.

Missing configuration uses zero calls. Timeout, provider failure, malformed
output, cancellation, and stale response use a fixed application status message
and retain local work. They do not fabricate alternative content. Output is not
saved automatically.

## Gemini workflow B — history RAG

The natural-language question is optional, 1–300 characters, and limited to
saved FocusBloom records. Suggested factual questions precede the field. The UI
warns against private, identifying, medical, or crisis information.

### Request 1: SQL proposal

One Gemini request proposes exactly one parameterized `SELECT`. The validator
parses the statement and accepts only:

- tables: `activity_sessions`, `perspective_artifacts`, `next_step_seeds`, or
  `preferences`;
- explicitly enumerated non-content columns needed for each question, plus saved
  artifact/seed display columns only for requests that ask to show them;
- `WHERE`, `GROUP BY`, `ORDER BY`, and `LIMIT`;
- aggregate functions `COUNT`, `MIN`, and `MAX` only;
- bound parameter `:profile_id`, which must constrain the current fictional
  profile; and
- at most 8 selected columns and `LIMIT` no greater than 20.

It rejects mutation, DDL, PRAGMA, ATTACH, transaction commands, comments,
multiple statements, CTEs, subqueries, joins, UNION/INTERSECT/EXCEPT, window
functions, unlisted functions/tables/columns, literals substituted for profile
scope, and missing/oversized limits before execution.

SQLite runs through a read-only URI connection with `PRAGMA query_only=ON`, an
authorizer denying writes/schema/unsafe functions, parameter binding, and a
progress handler enforcing a 100-ms execution deadline. Serialized rows are at
most 20 rows, 8 columns, and 8 KiB. `PRAGMA data_version` is checked before and
after retrieval (or an equivalent consistent read transaction is used); a
changed snapshot fails safely. Mutation never executes.

Rejected or out-of-scope proposals produce `history-query-rejected` after one
provider request. Zero rows produce `history-no-match` after one request and no
answer-generation call.

### Request 2: grounded answer

Only validated rows, stable row references, the original bounded question, and
the factual-answer schema are sent. One Gemini request returns at most 600
characters plus row references. Every asserted stored fact must resolve to one of
the retrieved references; otherwise output is rejected. The answer acknowledges
missing information and cannot infer motivation, emotion, diagnosis,
effectiveness, improvement, treatment, or advice.

The successful maximum is two provider requests. A rejected/no-match outcome
uses one. Missing configuration uses zero. Timeout, provider failure, malformed
output, inconsistent snapshot, or invalid grounding produces no retry and no
model fallback. Safe error codes do not expose questions, prompts, SQL, rows,
provider errors, or system instructions.

## Verification required before implementation can be called complete

The backend portions below were completed in Prompt 08 with 52 passing tests.
Browser, cross-layer UI, and manual pre-demo Support checks remain outstanding:

- Temporary version-2 database tests for all constraints, transactions,
  idempotency, deletion, reset, migration stop, and reopen behavior.
- API contract tests for exactly 22 operations and every allowed/failure outcome.
- Property/adversarial SQL validator tests and observed read-only authorizer,
  deadline, payload, snapshot, zero-row, mutation, and grounding behavior.
- Mocked Gemini call-count tests: Perspective 0/1; history 0/1/2 by outcome; no
  retry or fallback.
- Browser tests for all 17 states, keyboard/focus, 390-pixel reflow, 200% zoom,
  Standard/No-motion equivalence, fictional no-input path, no-typing Focus Garden,
  stale/cancelled responses, Support independence, Delete, and Reset.
- API/SQLite agreement for stable IDs and factual History Garden fields.
- Manual source recheck for Support before submission. Software checks do not
  establish clinical safety or effectiveness.
