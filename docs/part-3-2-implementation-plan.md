# Assignment 3.2 Implementation Plan

## Status, scope, and evidence boundary

This plan is the implementation contract for the five-checkpoint Assignment 3.2
workflow. Checkpoint 1 establishes only a tested Vue/FastAPI foundation, safe
configuration, and the exact architecture below. The selected Direction A
experience, the five-table schema, persistence behavior, deterministic exercise,
static Support route, model request, and integrated evidence remain assigned to
later checkpoints until their tests are observed.

BreathBloom is a localhost coursework prototype for fictional scenarios. It is
not therapy, an emergency service, or a monitored service. It will not diagnose,
infer distress or emotion, provide medical advice, or claim clinical benefit.
Voice and audio are prohibited.

## Requirements traceability

| Required behavior | Frontend responsibility | Backend responsibility | Database responsibility | Verification method | Planned evidence | Implementation checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| Complete one paced-breathing skill | Own the 4-second inhale, 6-second exhale, six-cycle sequence; show phase, countdown, cycle, Stop, and Support in text | Validate session transitions and persisted timing; never drive the timer | Store one honest session outcome and timing snapshot | Fake-clock component tests plus browser observation of all 12 phases | Test output, timestamp log, narrow/wide screenshots | 2 |
| Keep intended exercise at 60 seconds and under 90 seconds | Measure active time from first inhale to final exhale with a monotonic clock; exclude setup, user pauses, and Support time | Reject inconsistent, negative, or out-of-range timing payloads | Store planned, observed-active, paused, and wall-clock integer milliseconds separately | Compare fake-clock result, API response, and row; measure a browser run | Automated timing results and measured-run table | 2–3 |
| Preserve user control | Require explicit Start and Resume; make Stop and Support continuously available; never auto-resume | Enforce allowed actions and immutable terminal states | Record completed, stopped, or interrupted without failure language | Keyboard/browser checks for Start, Stop, Support pause, Resume, visibility gap, refresh | Scenario log and screenshots/video segment | 2–3 |
| Keep Support independent | Provide reviewed static U.S. Support content in every view, including loading/failure; do not classify input | No dependency: API or model failure cannot remove Support | No dependency and no location/condition field | Disable backend/network and verify route/content; activate links only in a controlled check | Offline/browser screenshots and link/source review | 2 |
| Demonstrate a bounded model contribution | Offer only optional introduction, factual reflection, or factual-history answer; deterministic fallback remains usable | Make the only provider request using backend-only config, fixed model, validation, timeout, and request identity | Persist initiating request lifecycle before a call and validated assistant output afterward | Mock success, missing key, timeout, provider error, malformed output, stale response; one later authorized live case | Redacted mock tests and separately labeled live observation | 4 |
| Persist conversations and sessions in SQLite | Send validated user actions with client IDs; render save state honestly | Own parameterized writes, idempotency, transactions, concurrency versions, and bounded reads | Use exactly five related tables and foreign keys described below | Compare UI/API IDs and values with read-only database inspection | Test database extracts containing fictional-only records | 3–4 |
| Show useful saved history without a model | Render date, duration, cycles, outcome, and settings; text always carries meaning | Return ordered factual session summaries/details | Query allowed session/preference fields | Restart backend, reload frontend, compare history with API and rows | Browser/API/database comparison | 3 |
| Use saved settings transparently | Explain the remembered motion/guidance values before use; allow change, skip, and reset | Validate explicit settings and reset transaction | Store only explicit preference values, source, and version | Preference round trip, stale-version conflict, reset test | Mock/browser and database comparison | 3 |
| Handle model failure without blocking ordinary use | Show neutral deterministic copy and keep Practice, Stop, Support, and History available | Return stable safe error codes; never return credentials, provider headers, raw exceptions, or private paths | Preserve failed initiating lifecycle; do not create an assistant message | Mock every failure class and inspect response/log output for leakage | Automated test results and failure screenshot | 4 |
| Reject stale or duplicate asynchronous work | Attach request/session generation IDs and ignore responses after navigation, Stop, restart, or replacement | Enforce request/client idempotency and current versions | Unique client/request IDs and transaction constraints prevent duplicate rows | Deliver delayed responses and duplicate actions under fake/mock control | Deterministic stale-response and duplicate tests | 3–4 |
| Respect reduced motion and accessibility | Full, Gentle, and No motion all show phase/time/cycle text; semantic order, visible focus, restrained live region, 44px targets, narrow/zoom reflow | Return semantic values independent of visual mode | Store explicit preference only; never infer accessibility needs | Keyboard, screen-reader announcement review, contrast, 320px, 400% zoom, reduced-motion checks | Accessibility checklist and representative captures | 2–5 |
| Use only fictional evaluation data | Label fixtures/scenarios fictional and avoid real distress testing or personal data | Reject fields outside contracts; keep logs minimal | Fixed fictional demo profile only; reset removes its child data | Fixture/name scan and database audit | Curated redacted evidence log | 3–5 |
| Keep architecture reviewable and runnable from a clean checkout | Vue uses HTTP/JSON only and never receives a provider secret | FastAPI owns validation, SQLite, and Gemini access | SQLite stays at ignored `data/app.sqlite3` | Follow README setup in a clean environment; test/lint/build/import/health | Exact commands and observed results | 1 and 5 |
| Explain AI use and implementation changes honestly | No hidden runtime AI behavior | Fixed provider/model and safe configuration documented | No generated clinical inference fields | Review disclosure, prompt record, diffs, and claims against evidence | `AI-USE.md`, prompt record, verification log | Every checkpoint |

## Architecture and ownership

- `frontend/` is Vue 3, JavaScript, Composition API, Vite, semantic HTML, and
  CSS. It owns visible navigation, pacing state, monotonic active-time math,
  presentation preferences, accessibility behavior, stale UI-response guards,
  and HTTP/JSON calls. It never opens SQLite or receives a provider key.
- `backend/app/` is typed Python and FastAPI. It owns `/api`, input validation,
  state-transition validation, idempotent persistence, safe configuration,
  bounded read-only RAG retrieval, and the only future provider call.
- `data/app.sqlite3` is an ignored local SQLite file opened only by FastAPI. No
  database is created at Checkpoint 1; the explicit initializer is present for a
  later schema checkpoint.
- The static Support content is bundled in the frontend so it remains available
  if FastAPI, SQLite, or Gemini is unavailable.

The Checkpoint 1 application intentionally exposes only `GET /api/health` and a
minimal Practice/History/Support foundation screen. That screen is not the
selected Figma experience and does not claim implemented skill behavior.

## Provider and model decision

- Provider: **Google Gemini Developer API**.
- Fixed model identifier: **`gemini-3.5-flash-lite`**.
- Intended role: one optional brief introduction, factual reflection, or bounded
  factual-history answer. It never owns timing, sequence, persistence truth,
  navigation, Stop, Resume, or Support.
- Configuration: backend environment variable `GEMINI_API_KEY`, represented by a
  secret type and loaded lazily from process environment or ignored
  `backend/.env`. `backend/.env.example` contains only the blank setting name.
- No provider or model fallback. No automatic retry. One request attempt per
  explicit user action. The exact timeout and per-session live-call cap will be
  recorded before the later live-call checkpoint; routine tests use mocks.
- A missing key is an expected configuration state, not a crash. Health reports
  only `configured` or `not configured`.
- No live request is authorized at Checkpoint 1.

Official verification on October 27, 2026:

- Google's model page identifies `gemini-3.5-flash-lite` as the stable model code
  and lists its latest update as July 2026:
  https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite
- Google's release notes describe the July 21, 2026 generally available stable
  release: https://ai.google.dev/gemini-api/docs/changelog
- Google's pricing page lists standard free-tier input and output as free of
  charge; availability and quotas still depend on the user's Google AI Studio
  project and may change: https://ai.google.dev/gemini-api/docs/pricing
- Google's rate-limit page states actual limits vary by project/tier and are
  viewed in AI Studio: https://ai.google.dev/gemini-api/docs/rate-limits

## Final five-table SQLite schema

All timestamps are UTC ISO 8601 text with a `Z` suffix. Durations are
non-negative integer milliseconds. IDs are application-generated opaque text.
`PRAGMA foreign_keys = ON` is required on every connection. Schema migrations
will use `PRAGMA user_version`; schema creation and the fixed fictional profile
will be explicit later operations, not import-time side effects.

### `demo_profiles`

| Column | Constraint and purpose |
| --- | --- |
| `profile_id` | `TEXT PRIMARY KEY`; fixed fictional demo identifier |
| `display_label` | `TEXT NOT NULL`; clearly fictional label |
| `jurisdiction_scope` | `TEXT NOT NULL CHECK (... = 'US-DEMO')` |
| `reset_version` | `INTEGER NOT NULL DEFAULT 0 CHECK (reset_version >= 0)` |
| `created_at` | `TEXT NOT NULL` |
| `updated_at` | `TEXT NOT NULL` |

### `preferences`

| Column | Constraint and purpose |
| --- | --- |
| `preference_id` | `TEXT PRIMARY KEY` |
| `profile_id` | `TEXT NOT NULL UNIQUE REFERENCES demo_profiles(profile_id) ON DELETE CASCADE` |
| `motion_mode` | `TEXT NOT NULL CHECK` in `full`, `gentle`, `none` |
| `guidance_level` | `TEXT NOT NULL CHECK` in `minimal`, `standard`, `more` |
| `source` | `TEXT NOT NULL CHECK` in `explicit`, `default`, `reset` |
| `version` | `INTEGER NOT NULL CHECK (version >= 1)` for optimistic concurrency |
| `created_at` | `TEXT NOT NULL` |
| `updated_at` | `TEXT NOT NULL` |

### `exercise_sessions`

| Column | Constraint and purpose |
| --- | --- |
| `session_id` | `TEXT PRIMARY KEY` |
| `profile_id` | `TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE` |
| `client_session_id` | `TEXT NOT NULL UNIQUE`; duplicate-create prevention |
| `status` | `TEXT NOT NULL CHECK` in `active`, `paused`, `completed`, `stopped`, `interrupted` |
| `started_at` | `TEXT NOT NULL` |
| `ended_at` | nullable `TEXT`; required for terminal status |
| `planned_duration_ms` | `INTEGER NOT NULL DEFAULT 60000 CHECK (... = 60000)` |
| `observed_active_duration_ms` | `INTEGER NOT NULL DEFAULT 0 CHECK (... >= 0)` |
| `paused_duration_ms` | `INTEGER NOT NULL DEFAULT 0 CHECK (... >= 0)` |
| `wall_clock_duration_ms` | `INTEGER NOT NULL DEFAULT 0 CHECK (... >= 0)` |
| `completed_cycles` | `INTEGER NOT NULL DEFAULT 0 CHECK` from 0 through 6 |
| `ending_phase` | nullable `TEXT CHECK` in `setup`, `ready`, `inhale`, `exhale` |
| `phase_elapsed_ms` | `INTEGER NOT NULL DEFAULT 0 CHECK (... >= 0)` |
| `motion_mode` | `TEXT NOT NULL CHECK` in `full`, `gentle`, `none`; session snapshot |
| `guidance_level` | `TEXT NOT NULL CHECK` in `minimal`, `standard`, `more`; session snapshot |
| `next_time_setup` | nullable `TEXT CHECK` in `use_this_setup`, `change_motion`, `change_guidance`, `no_preference` |
| `persistence_status` | `TEXT NOT NULL CHECK` in `pending`, `saved`, `failed` |
| `version` | `INTEGER NOT NULL CHECK (version >= 1)` |
| `created_at` | `TEXT NOT NULL` |
| `updated_at` | `TEXT NOT NULL` |

Application validation additionally requires terminal sessions to have
`ended_at`, `wall_clock_duration_ms >= observed_active_duration_ms`, exactly six
cycles for `completed`, and fewer than six for `stopped` or `interrupted`.
Database checks support but do not replace those transition rules.

### `conversations`

| Column | Constraint and purpose |
| --- | --- |
| `conversation_id` | `TEXT PRIMARY KEY` |
| `profile_id` | `TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE` |
| `session_id` | nullable `TEXT REFERENCES exercise_sessions(session_id) ON DELETE SET NULL` |
| `client_conversation_id` | `TEXT NOT NULL UNIQUE`; duplicate-create prevention |
| `status` | `TEXT NOT NULL CHECK` in `open`, `closed` |
| `created_at` | `TEXT NOT NULL` |
| `updated_at` | `TEXT NOT NULL` |

### `messages`

| Column | Constraint and purpose |
| --- | --- |
| `message_id` | `TEXT PRIMARY KEY` |
| `conversation_id` | `TEXT NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE` |
| `client_message_id` | `TEXT NOT NULL`; unique with conversation |
| `ordinal` | `INTEGER NOT NULL CHECK (ordinal >= 0)`; unique with conversation |
| `role` | `TEXT NOT NULL CHECK` in `user`, `assistant` |
| `content` | `TEXT NOT NULL CHECK (length(trim(content)) BETWEEN 1 AND 2000)` |
| `request_id` | nullable `TEXT UNIQUE`; initiating user message only |
| `request_purpose` | nullable `TEXT CHECK` in `introduction`, `factual_reflection`, `history_question` |
| `request_status` | nullable `TEXT CHECK` in `pending`, `succeeded`, `failed`, `rejected`, `stale` |
| `safe_error_code` | nullable `TEXT CHECK` in `missing_configuration`, `timeout`, `provider_failure`, `malformed_output`, `out_of_scope`, `stale_response`, `persistence_failure` |
| `created_at` | `TEXT NOT NULL` |
| `updated_at` | `TEXT NOT NULL` |

Table constraints include `UNIQUE (conversation_id, client_message_id)` and
`UNIQUE (conversation_id, ordinal)`. Request lifecycle fields are all null for an
assistant message. The initiating user message is committed before provider work;
an assistant message is inserted only in the same transaction that marks a
validated request `succeeded`. No separate reflection or request-attempt table is
permitted. Optional factual reflection uses `messages`; optional Next-time setup
stays on `exercise_sessions`.

Reset is one backend transaction scoped to the fixed profile: delete child
messages/conversations/sessions/preferences, recreate default preferences, and
increment `demo_profiles.reset_version`. It never changes schema or accepts an
arbitrary profile identifier.

## Final API surface: 11 routes

All routes use JSON, strict request models that reject unknown fields, stable
opaque IDs, safe error bodies, and `/api`. There is deliberately no Support API:
Support is static frontend content and must not depend on the backend.

| # | Method and route | Purpose |
| --- | --- | --- |
| 1 | `GET /api/health` | Safe service/database/key configuration status only |
| 2 | `GET /api/preferences` | Read explicit/default fictional-demo settings |
| 3 | `PUT /api/preferences` | Save motion/guidance with expected version |
| 4 | `POST /api/sessions` | Start one session idempotently from client ID and setting snapshot |
| 5 | `PATCH /api/sessions/{session_id}` | Apply exactly one `pause`, `resume`, `stop`, `complete`, `interrupt`, or `save_next_time_setup` action |
| 6 | `GET /api/sessions` | Ordered factual history summaries with bounded pagination |
| 7 | `GET /api/sessions/{session_id}` | One factual session detail |
| 8 | `POST /api/conversations` | Create/reuse an idempotent fictional conversation |
| 9 | `GET /api/conversations/{conversation_id}/messages` | Ordered saved messages without a model request |
| 10 | `POST /api/conversations/{conversation_id}/messages` | Persist initiating message, perform one bounded model attempt when configured, validate, and persist result/lifecycle |
| 11 | `POST /api/demo/reset` | Atomically reset only the fixed fictional profile after explicit confirmation |

The session patch requires `expected_version`, an action-specific client action
ID, and only fields allowed for that action. It rejects stale versions, duplicate
actions, invalid transitions, inconsistent timing, terminal-state replacement,
and unknown fields with stable codes. The message POST uses `client_message_id`
and `request_id` for idempotency. No polling/status route, provider proxy, generic
SQL endpoint, location endpoint, classifier endpoint, authentication endpoint,
or separate reflection endpoint is planned.

## Exact top-level state machine

The planned top-level states are exactly:

`setup`, `ready`, `inhale`, `exhale`, `stopped`, `completed`, `model-loading`,
`model-failed`, `support-open`, and `history`.

| From | Event | To | Guard/effect |
| --- | --- | --- | --- |
| `setup` | valid choices confirmed | `ready` | No timer starts |
| `setup` | optional model introduction requested | `model-loading` | Create request identity; deterministic controls remain available |
| `model-loading` | current validated response | `ready` | Display bounded copy only |
| `model-loading` | missing key, timeout, provider/validation failure | `model-failed` | Display safe deterministic fallback |
| `model-failed` | continue | `ready` | No provider retry |
| `ready` | explicit Start | `inhale` | Set monotonic origin and begin cycle 1 |
| `inhale` | active elapsed reaches 4,000 ms | `exhale` | Derive from elapsed time, not callback count |
| `exhale` | active elapsed reaches 6,000 ms and cycle < 6 | `inhale` | Increment completed cycle exactly once |
| `exhale` | active elapsed reaches 6,000 ms and cycle = 6 | `completed` | Clear timing work and persist terminal snapshot |
| `inhale` or `exhale` | explicit Stop | `stopped` | Clear timing work and retain accurate partial progress |
| any nonterminal visible state | open Support | `support-open` | Save safe `return_state`; active timing freezes immediately; a loading request is cancelled/staled and returns through `model-failed` fallback |
| `support-open` | close after nonactive state | saved `return_state` | Return without hidden work |
| `support-open` | close after active state | saved active phase behind explicit Resume gate | No active time advances until Resume |
| `setup`, `ready`, `stopped`, `completed`, or `model-failed` | open History | `history` | Read factual history without a model call |
| `history` | Back | prior nonactive state | Restore navigation context only |

`support-open` is the top-level pause-bearing state, so `paused` is not an
additional top-level state. Its context stores the prior phase, monotonic
checkpoint, phase offset, cycle, `pause_reason`, and `resume_required`. A page
visibility gap uses the same internal pause context and explicit Resume gate
without adding a top-level view. The backend may persist session status `paused`
because database status and view state serve different purposes. Refresh or
browser close is not resumable and is reconciled as `interrupted` from the last
acknowledged snapshot.

Each timer/request run has a generation token. Callbacks and responses must match
the current token, session, expected state, and request ID. Stop, completion,
navigation, restart, and replacement invalidate the token. Therefore a late
model response cannot change an active, stopped, completed, Support, or History
state and cannot create duplicate messages.

## Timing, failure, and retrieval contracts

- Use `performance.now()` for in-page elapsed time and UTC ISO timestamps for
  persistence. Recompute phase/cycle from accumulated active milliseconds.
- Initial scheduler-gap threshold: 2,000 ms. A larger unexpected gap freezes at
  the last acknowledged monotonic checkpoint and requires explicit Resume.
- Cancel scheduled work on pause, Support, Stop, completion, unmount, and flow
  replacement. A single controller instance owns timing.
- Model requests never begin until the initiating message is committed.
- Routine tests mock the provider. A later live check is separately labeled and
  cannot exceed the course's 50-call session ceiling; this project will adopt a
  smaller explicit cap before that checkpoint.
- RAG accepts one backend-constructed parameterized `SELECT` over an allowlist of
  preference/session fields, `COUNT` as the only initial aggregate, at most 20
  rows and about 4 KB of context, with a proposed 100-ms local deadline. It
  rejects multiple statements, mutations, schema inspection, arbitrary
  functions, messages, and Next-time setup data. Empty results use fixed copy.

## Checkpoint order and verification gates

1. **Foundation (this checkpoint):** branch from the published Part 3.1 SHA;
   create pinned manifests, project-local environments, Vue/FastAPI foundations,
   safe lazy configuration, read-only health status, this plan, tests, lint/build
   evidence, and publication. Do not create a database or call Gemini.
2. **Deterministic interface:** implement the selected Direction A practice,
   exact state/timing controller, static Support, motion/guidance modes, and
   accessibility checks using mocks only.
3. **SQLite and API behavior:** create the five-table schema, transactional
   preferences/sessions/history/reset, idempotency, restart/interruption, and
   API/database comparison evidence with fictional fixtures.
4. **Bounded Gemini and RAG:** implement one backend-only attempt, lifecycle,
   validation, fallback, stale-response protection, and mocked failure matrix;
   then run only the separately authorized small live sample.
5. **Integration and submission:** perform at least 15 fictional scenarios and
   three cross-case behavior checks, clean-checkout verification, measured
   exercise duration, final report/evidence, and process/demo recordings.

At every checkpoint, inspect branch/diff/ignored files, scan for secrets/private
paths and prohibited voice/audio/provider alternatives, preserve `main`, and
report only behavior that the observed evidence establishes.
