# Approved Assignment 3.1 Research and Design Decisions

## Status and coursework boundary

These decisions were approved on October 27, 2026. They remain contracts for a
later implementation, not evidence that an interface, API, database, provider
connection, or running application exists. The later Figma comparison was
completed, and the human selected Direction A on October 27, 2026; the resulting
editable Figma frames are static design evidence only and do not verify runtime
behavior.

BreathBloom remains a local coursework prototype evaluated only with fictional
scenarios. It must not diagnose, provide therapy or medical advice, claim clinical
effectiveness, imply human monitoring, infer distress, or be offered as a real
mental-health support service. Voice and audio are prohibited.

## Approved product direction

- Paced 4–6 breathing: 4-second inhale and 6-second exhale.
- Six cycles and exactly 60,000 planned active milliseconds.
- Application code owns timing, state, Stop, pause, resume, and persistence truth.
- Entry/setup and voluntary pauses are separate from active exercise time.
- Explicit Start, Stop, Support, Return, and Resume controls.
- Static national U.S. fictional-demo Support information independent of backend,
  database, provider, model, classifier, geolocation, or behavioral inference.
- Six-petal, text-backed water-garden bloom with Full, Gentle, and No motion.
- Transparent Minimal, Standard, and More guidance choices.
- Optional **Next-time setup** choices, not an emotional/clinical reflection.
- Factual history without scores, streaks, pressure, or improvement claims.
- Human-selected Figma Direction A: the focused central water garden, with
  Direction B's timing, segmented-progress, organization, and accessibility
  clarity incorporated without creating a third direction.
- Runtime provider/model selection remains deferred.

## Main planned flow

1. Entry shows the coursework notice and Support route.
2. The user begins, confirms a previous setup, or reviews factual history.
3. The user chooses motion and guidance presentation.
4. An optional bounded introduction may load; deterministic wording remains
   available and the user need not wait.
5. The ready state requires explicit **Start practice**.
6. The application runs six deterministic inhale/exhale cycles.
7. Support or page hiding pauses automatically; return requires Resume or Stop.
8. Stop, completion, or interruption produces an accurate factual result and
   honest save status.
9. The optional Next-time setup choice may explicitly update preferences.
10. History remains usable without a model request.

## Exact reviewed interface wording

| State or element | Approved wording |
| --- | --- |
| Coursework notice | **Coursework prototype · Fictional scenarios only. BreathBloom is not therapy, medical advice, emergency help, or a monitored service.** |
| Entry heading | **BreathBloom** |
| Entry description | **Practice six cycles of a 4-second inhale and 6-second exhale. Planned active time: 60 seconds. You can stop at any time.** |
| Entry actions | **Begin a 60-second practice** · **Use my previous setup** · **Review history** |
| Setup heading | **Choose your practice display** |
| Setup explanation | **Choose how the Breath Bloom moves and how much guidance appears. These choices change presentation only—not the 4–6 timing. You can change or skip them.** |
| Optional-introduction loading | **Preparing an optional introduction… You do not need to wait. Continue with the reviewed instructions whenever you are ready.** |
| Practice introduction | **BreathBloom will guide six cycles. Each cycle uses a 4-second inhale and a 6-second exhale. Stop and Support information remain available throughout.** |
| Ready state | **Ready for a 60-second practice? Timing starts only when you choose Start practice.** |
| Ready actions | **Start practice** · **Back to setup** · **Support information** |
| Inhale cue | **Inhale · 4-second phase** |
| Exhale cue | **Exhale · 6-second phase** |
| Minimal mode description | **Show the phase, labeled phase progress, and cycle progress without a large countdown.** |
| Minimal active text | **Inhale** / **Exhale** · **Cycle [n] of 6** · **[n] cycles complete** |
| Standard mode description | **Show the phase, countdown, and cycle progress.** |
| Standard active text | **Inhale · [4…1]** / **Exhale · [6…1]** · **Cycle [n] of 6** |
| More-guidance description | **Show the same phase, countdown, and progress with brief instructions. Timing does not change.** |
| More-guidance inhale | **Inhale — breathe in while the 4-second phase is shown.** |
| More-guidance exhale | **Exhale — breathe out while the 6-second phase is shown.** |
| More-guidance persistent note | **The next phase starts automatically. Stop remains available.** |
| Pause state | **Practice paused at [phase], cycle [n] of 6. Time is not advancing. Choose Resume practice or Stop.** |
| Pause actions | **Resume practice** · **Stop** · **Support information** |
| Stop confirmation | **Stop this practice? BreathBloom will end the timer and try to save completed cycles and measured active time as Stopped. Stopping is not a failure.** |
| Stop actions | **Continue practice** · **Stop practice** |
| Stopped result | **Practice stopped. [n] of 6 cycles were completed. Measured active time: [duration]. The partial bloom represents completed cycles only.** |
| Completed result | **Practice complete. 6 of 6 cycles were completed. Measured active time: [duration].** |
| Interrupted result | **Practice interrupted. The last saved snapshot contains [n] of 6 completed cycles and [duration] of acknowledged active time. This practice cannot resume.** |
| Model unavailable/invalid | **The optional introduction is unavailable or could not be checked. Continue with the reviewed instructions; the 4–6 timing is unchanged.** |
| Fallback actions | **Continue with reviewed instructions** · **Retry optional introduction** |
| Save failure | **This session is not saved yet. Its result remains available in this tab. Retry saving or continue without saving.** |
| Save failure actions | **Retry save** · **Continue without saving** |
| Local-only practice notice | **Running locally—not saved yet.** |
| History explanation | **History contains fictional practice records: date, measured active duration, completed cycles, status, and selected settings. It does not measure mood, diagnosis, distress, or improvement.** |
| Empty history | **No fictional practice sessions have been saved yet.** |
| Rejected history question | **That question is outside BreathBloom's factual history scope. You can review saved session dates, durations, cycles, statuses, and explicitly selected settings.** |
| Empty history-question result | **No saved fictional sessions match that question.** |

The rejected-question view must retain a visible Support link and must not claim
why the question was outside scope or infer the user's condition.

## Next-time setup

Approved prompt:

> **For a future fictional practice, what would you prefer?**

| Choice | Planned effect |
| --- | --- |
| **Use this setup next time: [motion] + [guidance]** | Save the current motion/guidance only because the label makes that change explicit. |
| **Choose a different motion setting** | Record the selection on the session and open motion choices; do not change preferences until the user saves one. |
| **Choose a different guidance level** | Record the selection on the session and open guidance choices; do not change preferences until the user saves one. |
| **No preference** | Store `no_preference` on the session and leave preferences unchanged. |
| **Skip** | Store no Next-time setup selection and change nothing. |

The nullable selection is stored on `exercise_sessions`; there is no separate
reflection record. Session status, duration, completion, and interaction behavior
must never preselect a choice or be interpreted as emotion or effectiveness.

## Interruption and visibility behavior

| Event | Approved planned behavior |
| --- | --- |
| Support opens during exercise | Freeze active monotonic time immediately, cancel pacing callbacks, retain phase offset and completed cycles, enter a Support-pause state, and attempt an honest save without making the pause depend on it. |
| Page becomes hidden | Automatically pause at the last visible monotonic checkpoint. Do not continue silently in the background. |
| Return from Support or hidden page | Show a paused state. Only explicit Resume or Stop changes it. |
| Resume | Continue the same phase from the frozen active offset with a new monotonic anchor; exclude paused time. |
| Refresh while active or paused | End resumability and produce Interrupted from the last acknowledged snapshot. Never resume automatically. |
| Browser closes | Attempt a best-effort interruption update, but do not depend on unload delivery. Reconcile a remaining open record as Interrupted from its last acknowledged snapshot. |
| Backend is unavailable | Continue deterministic frontend pacing, label the record unsaved, and keep a tab-scoped pending snapshot/idempotency key. Pending local state is not history. |
| Persistence fails | Preserve the last acknowledged record, show **Not saved yet**, and allow an idempotent retry. Never claim a failed write was saved. |
| Stale model response arrives | Discard it by request/conversation/state identity. It cannot alter navigation, timers, session outcome, messages, or persistence. |
| Visible scheduler sample is delayed more than 2,000 ms | Freeze at the last confirmed active checkpoint and require Resume. The 2,000-ms threshold is an initial testable application constant and may change only from recorded verification evidence. |

## Timing and persistence rules

- Use a monotonic browser clock for active duration. UTC wall-clock timestamps do
  not control phase transitions.
- Maintain accumulated active milliseconds, a current monotonic anchor, and
  paused milliseconds separately.
- Animation frames/timeouts request updates only. Derive state from elapsed time,
  never callback counts.
- Cumulative cycle-completion boundaries are 10,000, 20,000, 30,000, 40,000,
  50,000, and 60,000 active milliseconds.
- A cycle/petal completes only at the end of its six-second exhale.
- Partial progress is stored as active milliseconds, ending phase, phase elapsed
  milliseconds, and completed cycle count; it never adds a petal.
- Store timestamps in UTC ISO 8601 form with millisecond precision and `Z`.
- Store planned, observed-active, paused, phase, and wall-clock durations as
  non-negative integer milliseconds. Display durations rounded to one decimal
  second; display rounding never drives behavior.
- Create the session at explicit **Start practice**, with a stable client session
  ID, idempotency key, planned duration `60000`, and preference snapshot.
- Update the session at each completed cycle, pause, resume, terminal outcome,
  and detectable interruption, using an expected record version.
- Completed saves six cycles and final observed-active time. Stopped saves the
  explicit outcome and accurate partial snapshot. Interrupted saves only the last
  acknowledged snapshot and cannot resume.
- `planned_duration_ms` remains 60,000. `observed_active_duration_ms` measures
  actual active time and may be slightly above 60,000 due to callback latency.
  Paused and wall-clock durations remain separate.
- A model never participates in any timing or persistence calculation.

## Simplified five-record data relationships

This is a planned record design, not executable SQL.

| Record type | Purpose and primary identifier | Important fields and relationships | Retention/reset | Must never be interpreted as |
| --- | --- | --- | --- | --- |
| `demo_profiles` | Fixed fictional owner scope; `profile_id` | Demo label, `US-DEMO` jurisdiction code, created/updated UTC, reset version | One fixed profile; explicit reset removes children and restores defaults | A real person, real location, diagnosis, or risk |
| `preferences` | Explicit presentation settings; `preference_id` | `profile_id`, motion mode, guidance level, explicit source, version, updated UTC | One current record; user may change/reset it | Emotion, distress, ability, or treatment need |
| `exercise_sessions` | Factual practice record; `session_id` | `profile_id`; active/paused/completed/stopped/interrupted status; UTC timestamps; planned, observed-active, paused, wall-clock, and phase milliseconds; completed cycles; ending phase; motion/guidance snapshots; nullable `next_time_setup_selection`; version/persistence status | Retained until explicit reset; open records reconcile honestly | Improvement, worsening, adherence, emotion, or clinical outcome |
| `conversations` | Group ordered fictional messages; `conversation_id` | `profile_id`, optional `session_id`, created/updated UTC, lifecycle status | Retained until explicit reset | Therapy, monitoring, or a clinical relationship |
| `messages` | Actual stored user/assistant messages and bounded request lifecycle; `message_id` | `conversation_id`, stable ordinal, role, content, UTC timestamps. Initiating user message may also have `request_id`, `request_purpose` (`introduction`, `factual_reflection`, or `history_question`), `request_status`, `safe_error_code`, `created_at`, and `updated_at`. | Retained until reset; assistant row only after validated output is successfully persisted | Diagnosis, verified truth, distress, or urgency merely because text exists |

The initiating user message carries bounded request status, so separate reflection
and request-attempt records are unnecessary. This reduces implementation and test
scope without weakening honest failure reporting. If the initiating user-message
write fails, provider work must not begin. If provider output or assistant-message
persistence fails, no assistant message is fabricated and the user message's
request status records the safe failure when persistence is available.

## Simplified API proposal

All writes use stable idempotency keys. Session updates include an expected record
version. No endpoint or code exists yet.

| Method and route | Purpose | Essential request | Essential response | Important failure behavior |
| --- | --- | --- | --- | --- |
| `GET /api/health` | Report service/configuration state without secrets | None | Service status, database-available boolean, runtime-model-configured boolean, schema version | Never expose keys/values; report components separately |
| `GET /api/preferences` | Read demo preferences | Fixed profile scope | Motion, guidance, version, updated UTC | Return documented defaults if no record exists |
| `PUT /api/preferences` | Explicitly change/reset preferences | Motion, guidance, expected version, idempotency key | Saved values, new version, persistence status | Reject invalid modes/stale version; never claim a failed save |
| `POST /api/sessions` | Begin at explicit Start | Client session ID, preference snapshot, `60000`, start UTC, idempotency key | Session ID, active status, version, persistence status | On failure return typed error; local practice may continue only with an unsaved label |
| `PATCH /api/sessions/{session_id}` | Apply one strictly validated action: `pause`, `resume`, `stop`, `complete`, `interrupt`, or `save_next_time_setup` | Action; only its allowed fields; expected version; idempotency key | Acknowledged factual snapshot, status, version, persistence status | Reject unknown fields, invalid transitions, stale versions, duplicates, inconsistent timing, and attempts to overwrite terminal states |
| `GET /api/sessions` | Read paginated factual history | Cursor/limit and permitted factual status filter | Ordered sessions and next cursor | No model call; honest bounded empty result |
| `GET /api/sessions/{session_id}` | Read one factual session | Session ID | Session fields/persistence status | 404 outside the fixed demo scope |
| `POST /api/conversations` | Create a fictional conversation | Optional session ID, client conversation ID | Conversation ID, timestamps, persistence status | Creating it does not require a provider call |
| `GET /api/conversations/{conversation_id}/messages` | Read ordered messages | Cursor/limit | Stable IDs, roles, ordinal order, timestamps, next cursor | Never return a fabricated assistant reply |
| `POST /api/conversations/{conversation_id}/messages` | Save a user message and later perform an approved bounded purpose | Client message ID, content, request ID, bounded purpose, idempotency key | Stored user-message ID, request status, assistant message only if validated and persisted | Persist user message before provider work; on failure record safe status and create no assistant row |
| `POST /api/demo/reset` | Reset fictional demo data | Exact phrase `RESET FICTIONAL BREATHBLOOM DATA` and current reset version | New reset version and deletion counts | Atomic or no change; reject missing confirmation/stale version |

`PATCH /api/sessions/{session_id}` action fields are allow-listed per action; the
request cannot send arbitrary record fields. No separate asynchronous request
status endpoint is planned unless implementation evidence later demonstrates a
need.

## Bounded RAG scope

Permitted questions are limited to factual preferences/session history, such as
recent settings, counts by completed/stopped/interrupted status, or recent dates,
durations, cycles, statuses, and explicit settings.

Reject diagnosis, clinical interpretation, improvement/worsening claims,
emotional-state inference, treatment/emergency advice, arbitrary database access,
conversation analysis, and mutations. BreathBloom does not claim to detect or
classify crisis language. The history-question view always shows Support.

Only approved `preferences` and `exercise_sessions` fields may be queried.
Conversation/message text and Next-time setup selections are excluded. Enforcement
requires one parsed read-only `SELECT`, a read-only connection/authorizer,
parameter-bound fixed profile scope and filters, `COUNT` as the initial and only
aggregate, a maximum of 20 rows, approximately 4 KB of serialized context, and a
short proposed 100-ms local execution deadline. Writes, multiple statements,
schema inspection, arbitrary functions, and unsafe syntax are rejected.

Empty retrieval uses the approved deterministic empty message. Every rejected
question uses the same neutral deterministic scope message and visible Support
route. A grounded answer cites supporting session IDs/dates and states when
records are insufficient. Provider/model selection and SQL/model calls remain
deferred.

## Responsive visual decisions

Candidate palette, subject to measured contrast verification:

- pale mist `#F4FAF8`;
- white surface `#FFFFFF`;
- deep navy `#16324A`;
- water blue `#276B8A`;
- leaf green `#2E6A52`;
- light sage `#D7E8DE`; and
- warm Stop/Support accent `#9C3D2E`.

Normal text targets at least 4.5:1 contrast; large text/UI and visible focus target
at least 3:1. Controls target at least 44 by 44 CSS pixels. Actual combinations
remain unverified until measured in the later interface.

Narrow layouts from 320–767 CSS pixels use a single column and a stable utility
bar for text-labeled Stop/Support. Wide layouts center a 640–720-pixel practice
panel with an optional 260–300-pixel factual side panel. Reflow must avoid
horizontal scrolling at 320 CSS pixels and 400% zoom.

Use a system sans-serif stack, at least 16-pixel body text, a 32–48-pixel title,
a 48–72-pixel phase label, and a 32–48-pixel countdown. Six equal petals sit at
60-degree intervals around a central orb. Approximate bloom diameter is 180
pixels narrow and 240 pixels wide. Completed petals use a non-color marker and
the text **[n] of 6 cycles complete**.

Full motion scales approximately 82%–100%; Gentle approximately 96%–100% with a
stronger progress ring; No motion has no scale, opacity, translation, or ripple
animation. The ring displays but never controls active time. A cycle ripple may
last up to about 400 ms in Full/Gentle only. System reduced motion renders No
motion by default without silently overwriting the saved preference.

### Reading order and keyboard focus

- Headings and explanatory text stay in logical DOM/reading order but are not
  ordinary Tab stops.
- Interactive Tab order contains controls only, with visual and DOM order aligned.
- A major view change may programmatically focus the main heading using temporary
  `tabindex="-1"`.
- Ordinary inhale/exhale/cycle changes use a restrained live region and never
  move keyboard focus.
- Do not announce every one-second countdown change.
- During practice, interactive order is Stop, Support information, then any
  nonessential detail control.
- During pause, order is Resume practice, Stop, Support information.
- Text always communicates phase, phase progress/time, cycle, completed petals,
  outcome, and save status without relying on color, motion, or shape.

## Selected Figma direction and static reference

The authorized comparison was completed in the editable Figma Design file
**BreathBloom — Assignment 3.1 Design Comparison**:

`https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx`

The human selected **Direction A — Focused central water garden**. Its prominent
central six-petal bloom communicates the flower, leaf, and water identity more
clearly and provides the calmer, more immersive, more distinctive atmosphere.
Direction A remains the design direction; this is not a third or merged
direction. The selected reference borrows Direction B's clearer timing language,
explicit six-segment progress, guidance organization, and accessibility cues.

The original comparison remains historical evidence. These required Direction A
frames were fingerprinted before and after expansion and remained unchanged:

| Historical comparison frame | Node ID | Dimensions |
| --- | --- | --- |
| A — Entry and setup — Narrow | `3:8` | 390×844 |
| A — Active inhale — Standard — Cycle 3 — Narrow | `3:51` | 390×844 |
| A — Active inhale — No motion — Cycle 3 — Narrow | `3:110` | 390×844 |
| A — Active inhale — Standard — Cycle 3 — Wide | `3:170` | 1024×768 |

The selected expansion is the Figma section **04 / Selected Direction A**
(`10:286`). It contains these implementation-ready static references:

| Selected reference | Node ID | Dimensions |
| --- | --- | --- |
| Entry and setup — Narrow | `11:351` | 390×844 |
| Entry and setup — Wide | `11:372` | 1024×768 |
| Active inhale — Standard — Cycle 3 — Narrow | `11:437` | 390×844 |
| Active exhale — Standard — Cycle 3 — Narrow | `11:461` | 390×844 |
| Active inhale — No motion — Cycle 3 — Narrow | `11:504` | 390×844 |
| Active inhale — Standard — Cycle 3 — Wide | `11:529` | 1024×768 |
| Active exhale — Standard — Cycle 3 — Wide | `11:558` | 1024×768 |
| Practice complete and Next-time setup — Narrow | `12:408` | 390×844 |
| Practice complete and Next-time setup — Wide | `12:454` | 1024×768 |
| History — Narrow | `13:416` | 390×844 |
| History — Wide | `13:448` | 1024×768 |
| Support information — Narrow | `14:428` | 390×844 |
| Support information — Wide | `14:460` | 1024×768 |

The selected overview is node `14:537`, and cross-state implementation
annotations are node `14:508`. The frames reuse the established variables, text
styles, and controls; retain the central bloom, blue/green water-garden palette,
4/6 timing language, six cycles, visible phase/cycle text, explicit segments,
Stop and Support, non-color completion markers, 44-pixel-minimum targets, focus
intent, contrast evidence, and a fully understandable No motion state.

The Figma reference is static. It does not verify timing, motion, pause/resume,
keyboard operation, focus movement, live announcements, responsive reflow,
persistence, API/database behavior, model/provider behavior, or Support-link
activation in a running application.

## Assignment 3.1 requirement mapping

| Requirement | Approved coverage |
| --- | --- |
| Chosen skill | Fixed six-cycle 4/6 breathing, 60,000 planned active ms |
| Model contribution | Optional bounded introduction/factual reflection/history answer with deterministic fallback; no skill/state/safety ownership |
| Personalization | Explicit, inspectable motion/guidance preferences and Next-time setup choices |
| User control | Start, Stop, Support, Return, Resume, preference change/reset, retry, Skip, and explicit demo reset |
| Planned saved records | Five record types with stable relationships and honest lifecycle fields |
| Main interaction flow | Entry through factual history with loading, failure, pause, stopped, completed, and interrupted states |
| Research findings | R1 supports 60 seconds; D3 low effort; R4 explicit choice; D5 transparent personalization; D1 rejects behavioral inference |
| Alternatives/tradeoffs | Behavioral adaptation rejected; longer/configurable sequence deferred; visual complexity constrained; central/text-first comparison planned |
| Support requirement | Fixed verified-source U.S. plan, static route in every state, pause and explicit resume |
| Accessibility | Responsive structure, semantic reading/focus rules, keyboard, text equivalents, contrast targets, reduced/no motion |

## Deferred and pending work

Runtime provider/model selection, credentials, exact provider timeouts/retries/call
budgets, implementation, Git initialization, database creation, report creation,
and runtime verification remain deferred. The Figma comparison, human selection,
and selected static Direction A reference are complete. The next concrete task is
to plan the Part 3.2 implementation foundation without beginning implementation.
