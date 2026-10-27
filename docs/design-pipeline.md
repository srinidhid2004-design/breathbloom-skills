# BreathBloom Design Pipeline

## Status and boundary

The current milestone is **Assignment 3.2 Checkpoint 1 foundation**, built from
the approved Assignment 3.1 decisions and human-selected Direction A reference.
The exact approved contracts are in
[`part-3-1-decisions.md`](part-3-1-decisions.md), and the static U.S. Support
content and official sources are in
[`support-resources.md`](support-resources.md). This file summarizes how those
decisions guide later design and implementation.

The minimal Vue page, FastAPI application, safe configuration, and health route
now exist and have local foundation checks. The selected interface and all skill,
Support, persistence, database, model, and integrated behavior below remain
planned and unverified. BreathBloom is a local coursework prototype for
fictional scenarios, not a mental-health or emergency service.

## Intended fictional user task

A fictional user chooses or confirms motion and guidance settings, explicitly
starts a paced-breathing practice, follows visible inhale/exhale cues, and either
completes or stops without penalty. Support information is available in every
state. A user who leaves the practice for Support or whose page becomes hidden
returns to a paused state and chooses Resume or Stop. Later, the user may review
factual saved history and make an optional non-clinical Next-time setup choice.

## Skill, timing, and interruption contract

The fixed skill is six cycles of a 4-second inhale and 6-second exhale: 60,000
milliseconds of planned active exercise. Entry, setup, pauses, and Support time
are separate. Application code—not a model—owns timing, phase, cycle, pause,
resume, Stop, completion, and persistence truth.

Use a monotonic browser clock and derive phase/cycle state from elapsed active
time rather than callback counts. Cycle boundaries are 10,000 through 60,000
active milliseconds in 10,000-ms increments. Store UTC timestamps and separate
non-negative integer values for planned, observed-active, paused, wall-clock,
and phase milliseconds.

The planned interruption behavior is:

- opening Support or hiding the page pauses at the last visible monotonic
  checkpoint and cancels pacing callbacks;
- returning never resumes automatically; only explicit Resume or Stop proceeds;
- refresh or browser closure ends resumability and produces Interrupted from the
  last acknowledged snapshot;
- unavailable persistence preserves an honestly labeled tab-scoped result and
  supports idempotent retry without claiming a save; and
- a visible scheduler sample delayed more than the initial 2,000-ms test constant
  pauses and requires Resume. The threshold changes only from recorded evidence.

The full timing, rounding, version, idempotency, and terminal-save rules are in
the authoritative decision record.

## Planned flow and states

1. Entry identifies the coursework boundary and offers Begin, Use my previous
   setup, Review history, and Support information.
2. Setup offers Full, Gentle, or No motion and Minimal, Standard, or More guidance.
3. An optional bounded introduction may load, fail, or be skipped without
   blocking the reviewed deterministic instructions.
4. Timing starts only after explicit **Start practice**.
5. Active practice shows phase, phase progress/time, cycle progress, Stop, and
   Support; it reaches Completed after six cycles or Stopped after explicit Stop.
6. Support/visibility changes lead to Paused; explicit Resume continues the frozen
   phase offset, while refresh/closure leads to non-resumable Interrupted.
7. The result offers factual history and optional Next-time setup choices: reuse
   the current setup, choose a different motion setting, choose a different
   guidance level, No preference, or Skip.

A stopped practice is a valid result. A partial bloom represents completed cycles
only and is always accompanied by text. The exact approved coursework, setup,
cue, pause, stopped, completed, interrupted, fallback, save-failure, history,
empty-result, and rejected-question wording is maintained in
`part-3-1-decisions.md`.

## Personalization boundary

Preferences are explicit, inspectable, changeable, rejectable, and resettable.
Use my previous setup states what will be reused before applying it. The optional
Next-time setup selection is stored on its exercise session and is not an
emotional or clinical reflection; Skip stores no selection.

BreathBloom never infers diagnosis, distress, emotion, improvement, urgency, or
treatment need from clicks, timing, duration, completion, questions, or settings.
It has no streaks, scores, rankings, failure language, or pressure to finish.

## Planned visual and responsive system

The human-selected visual direction is **Direction A — Focused central water
garden**. Its prominent six-petal central bloom and water/leaf atmosphere remain
primary because they communicate the intended identity most clearly and feel
calmer, more immersive, and more distinctive. Direction B was not selected, but
its clearer timing language, explicit six-segment progress, organized guidance,
and accessibility cues are incorporated into Direction A. No third direction was
created.

The candidate water-garden palette is pale mist `#F4FAF8`, white `#FFFFFF`, deep
navy `#16324A`, water blue `#276B8A`, leaf green `#2E6A52`, light sage `#D7E8DE`,
and warm Stop/Support accent `#9C3D2E`. It remains subject to measured contrast
verification; imagery and color carry no wellness claim.

Six equal petals surround a central orb. One petal appears only after each full
inhale/exhale cycle. Full motion uses the most visible synchronized scale change,
Gentle uses a smaller change and stronger progress ring, and No motion removes
scale, opacity, translation, and ripple animation while retaining all text.
System reduced motion defaults presentation to No motion without overwriting the
saved preference.

Narrow layouts from 320–767 CSS pixels use one column and stable text-labeled
Stop/Support controls. Wider layouts center the practice panel and may add a
factual side panel. Reflow must avoid horizontal scrolling at 320 CSS pixels and
400% zoom. Target sizes are at least 44 by 44 CSS pixels. Candidate text/UI/focus
contrast targets are 4.5:1 for normal text and 3:1 for large text, components,
and visible focus, subject to later measurement.

## Accessibility behavior

- Semantic headings and explanatory text follow logical DOM/reading order but
  are not ordinary Tab stops.
- Keyboard Tab order contains interactive controls only, and visual/DOM order
  agree.
- A major view change may deliberately focus its main heading using temporary
  `tabindex="-1"`; ordinary phase changes never move focus.
- A restrained live region communicates important phase/cycle changes without
  announcing each one-second countdown update.
- Active order begins Stop, Support; paused order is Resume, Stop, Support.
- Text communicates phase, progress/time, cycle, petals, result, and save status
  without requiring color, motion, shape, or imagery.
- Keyboard operation, visible focus, zoom/reflow, target size, contrast, reduced
  motion, and No motion all require later runtime verification.

## Independent Support information

Support is fixed national U.S. fictional-demo content available as static
frontend information in every state, independently of FastAPI, SQLite, models,
classifiers, questionnaires, geolocation, behavior, and network/provider success.
No resource is dynamically selected from user data.

The route clearly separates 911 for immediate danger or a medical emergency,
988 call/text/chat for crisis support, and FindTreatment.gov for non-emergency
treatment information. It states that BreathBloom is not an emergency service,
is not monitored, cannot contact help, and does not infer location or condition.
The exact wording, direct official URLs, source-check evidence, and manual review
procedure are in `support-resources.md`.

## Planned five-record data model

The approved record types are:

- `demo_profiles`: one fixed fictional profile and reset scope;
- `preferences`: explicit motion/guidance settings and version;
- `exercise_sessions`: timing/status/cycle/settings snapshots, persistence
  version/status, and nullable Next-time setup selection;
- `conversations`: stable fictional message grouping with an optional session
  relationship; and
- `messages`: stable role/order/timestamps/content plus request lifecycle fields
  on the initiating user message.

There is no separate session-reflection or request-attempt record. The initiating
user message holds `request_id`, `request_purpose`, `request_status`,
`safe_error_code`, `created_at`, and `updated_at`. Provider work cannot precede
its successful save, and an assistant message exists only after validated output
is successfully persisted. This simplifies implementation and testing without
weakening honest failure reporting.

## Planned API boundary

The proposed routes are `GET /api/health`, `GET` and `PUT /api/preferences`,
`POST /api/sessions`, `PATCH /api/sessions/{session_id}`, `GET /api/sessions`,
`GET /api/sessions/{session_id}`, `POST /api/conversations`, `GET` and `POST
/api/conversations/{conversation_id}/messages`, and `POST /api/demo/reset`.

`PATCH /api/sessions/{session_id}` accepts only one strictly validated `pause`,
`resume`, `stop`, `complete`, `interrupt`, or `save_next_time_setup` action with
action-specific fields. It rejects invalid transitions, stale versions, unknown
fields, duplicates, inconsistent timing, and attempts to overwrite terminal
states. No asynchronous request-status endpoint is planned unless later
implementation evidence demonstrates a need.

Only `GET /api/health` exists in code at Checkpoint 1. The final 11-route plan and
exact schema are in `part-3-2-implementation-plan.md`; the earlier request,
response, and failure proposal remains in `part-3-1-decisions.md`.

## Planned model, fallback, and RAG roles

The approved Google Gemini model `gemini-3.5-flash-lite` may later supply only an optional bounded
introduction, factual reflection, or answer about fictional saved history. It
cannot control the exercise or Support route, infer condition, diagnose, provide
therapy/medical advice, or claim improvement. Reviewed deterministic copy keeps
practice, exits, Support, and ordinary history usable through missing, slow,
invalid, stale, or failed model operations.

RAG is limited to allowed fields from `preferences` and `exercise_sessions` for
the fixed fictional profile. It permits one parsed, read-only `SELECT`, parameter
binding, `COUNT` as the initial aggregate, at most 20 rows, about 4 KB of context,
and a proposed 100-ms local deadline. It excludes conversation-message queries,
Next-time setup selections, mutations, multiple statements, schema inspection,
and arbitrary functions.

Every out-of-scope question receives the same neutral deterministic scope message
and visible Support link. Empty retrieval also uses fixed wording. BreathBloom
does not detect or classify crisis language. Provider/model choice is resolved;
credentials, exact timeout/call budget, implementation, and provider calls remain
deferred. No provider fallback or automatic retry is permitted.

## Research rationale and tradeoffs

The course finding about attention beyond roughly 90–100 seconds (R1) supports a
60-second practice. Low interaction effort (D3) supports direct choices; user
choice (R4) supports explicit Start, Stop, Resume, and preference decisions;
transparent personalization (D5) supports only inspectable settings/history; and
the warning about interpreting clicks (D1) rejects behavioral state inference.

Automatic behavioral adaptation was rejected. Longer/configurable sequences were
deferred in favor of one testable 4/6 skill. The garden metaphor is retained only
with text equivalents, optional motion, and measured accessibility checks. A
bounded model gives up open-ended flexibility so deterministic code preserves
timing, exits, Support, and stored truth.

## Figma comparison and selected reference — completed

The editable comparison and selected expansion are in:

`https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx`

The original A/B comparison remains unchanged as historical evidence. The human
selection is recorded in the comparison notes and overview, and the new Figma
section **04 / Selected Direction A** (`10:286`) contains 13 static references:
entry/setup, active inhale, active exhale, No motion, completion with optional
Next-time setup, factual history, and independent Support across narrow and wide
layouts where they differ materially. The selected overview is `14:537`; the
cross-state implementation annotations are `14:508`.

The selected frames reuse the comparison's variables, text styles, components,
and editable vector layers. They retain the central bloom, six-cycle 4/6 wording,
phase/cycle text, explicit six-segment progress, Stop and Support, focus intent,
44-pixel-minimum targets, non-color completion markers, reduced/No motion notes,
and the approved fixed Support content. Structural and visual Figma checks passed,
but a Figma frame does not prove application behavior.

## Planned responsibility separation

- **Vue 3 frontend:** semantic interface, static Support, deterministic pacing,
  motion/guidance presentation, and HTTP requests.
- **FastAPI backend:** the checked foundation exposes safe health/config status;
  later checkpoints add typed transitions, persistence, read-only RAG
  enforcement, and the separately authorized backend-only provider call.
- **SQLite:** planned at `data/app.sqlite3`, opened only by the backend for the
  five fictional-demo record types.

## Explicit exclusions

Voice input/output, microphone access, WebRTC, audio capture/recording, speech
recognition, speech synthesis, and live-audio models are prohibited. The complete
experience uses visible text and controls.

## Remaining implementation work

The next checkpoint must implement the selected Direction A deterministic
practice and static Support experience with mocked/local behavior only. Later
checkpoints add the exact five-table SQLite/API contracts, bounded Gemini/RAG,
and final integration/evidence. Before a live provider check, record the exact
timeout and a project call cap below the course's 50-call session maximum.
