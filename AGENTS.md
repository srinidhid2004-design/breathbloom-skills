# Instructions for coding agents

Work toward the BreathBloom project described in `README.md`. Work only inside
this project root, preserve existing work, and treat the README's approved
decisions and open questions as authoritative. Read `README.md`, `AGENTS.md`,
`AI-USE.md`, `docs/part-3-1-decisions.md`, `docs/support-resources.md`,
`docs/design-pipeline.md`, `docs/verification.md`, and `handoffs/current.md` when
relevant before making changes.

## Current approved-decision boundary

The repository has completed the approved Assignment 3.1 research/design decision
checkpoint. The exact behavior, wording, data, API, RAG, responsive, accessibility,
and Figma-comparison decisions are in `docs/part-3-1-decisions.md`; the fixed U.S.
Support plan is in `docs/support-resources.md`. Do not install dependencies,
create application source, add manifests or environments, add credentials, create
a database or fixture, initialize Git, use Figma, call a model/provider, create
`report.md`, or add other files until a later task explicitly authorizes that
work.

Do not resolve a README open question by assumption. Ask for or record a decision
when it becomes necessary to the requested milestone.

## 1. Preserve scope and coursework boundaries

- Build a local coursework prototype for fictional scenarios only.
- Never offer, deploy, link, or recommend BreathBloom as a real mental-health
  support service or test it with a person who is actually in distress.
- Do not diagnose, provide therapy or medical advice, infer distress or emotion,
  imply human monitoring, or claim clinical, safety, or effectiveness outcomes.
- Preserve the selected paced 4–6 breathing skill: 4-second inhale, 6-second
  exhale, six cycles, and a planned 60-second exercise.
- Do not add other skills, scores, ranks, streak pressure, failure language, or
  optional features from course references unless the developer approves them.
- Keep all application use possible through visible text and controls.

## 2. Keep frontend, backend, and data responsibilities separate

- **`frontend/`: Vue 3 with JavaScript, HTML, and CSS.** Put components, visible
  pacing cues, interaction state, accessibility behavior, and HTTP client code
  here. Never open SQLite or use a private provider key in the frontend.
- **`backend/`: typed Python with FastAPI.** Put API routes, validation, business
  rules, persistence, configuration loading, and later provider calls here.
- **`data/`: SQLite and explicitly fictional fixtures.** The planned database is
  `data/app.sqlite3`. Resolve it from the project root; only backend code may
  open it.
- Vue communicates with FastAPI through documented HTTP/JSON contracts. Keep
  routes small, validation explicit, and stable identifiers consistent across
  the database, API, and interface.
- Ordinary exercise behavior and history browsing must work without a model.

## 3. Make the application own the skill and time

- Application code—not a language model—must control phase order, 4/6 durations,
  six-cycle progress, countdown, completion, stopping, pausing, resuming, and
  saved status.
- Begin only after an explicit user action. Keep **Stop** available during every
  active or paused exercise. Stop immediately, clear pending timers, preserve the
  accurate completed-cycle count, and save a stopped outcome without failure
  language.
- Opening Support information during an exercise must pause safely and clear or
  suspend timing work. Returning must show a paused state; never resume until the
  user explicitly chooses **Resume practice**.
- Automatically pause at the last visible monotonic checkpoint if the page becomes
  hidden. Refresh or browser close ends resumability and reconciles the last
  acknowledged snapshot as Interrupted; never resume automatically.
- Clear stale timers and subscriptions when leaving, stopping, completing, or
  restarting. Prevent duplicate intervals, phase transitions, completions, and
  saves.
- Use a monotonic browser clock for active time and derive state from elapsed time,
  not callback counts. Store non-negative integer milliseconds for planned,
  observed-active, paused, wall-clock, and phase values plus UTC ISO timestamps.
  Treat a scheduler gap over the initial 2,000-ms threshold as a pause requiring
  explicit Resume; change that threshold only from recorded verification evidence.
- Respect reduced-motion preferences. Full, Gentle, and No motion
  modes must all show phase text, time, and cycle progress without depending on
  animation or color.
- Give each asynchronous model/API request an identity or cancellation boundary.
  A late response from an older request, prior screen, stopped session, or
  restarted flow must not overwrite current state, restart timers, add duplicate
  messages, or change saved completion status.

## 4. Bound the model role

- A later model may provide only an approved brief introduction, factual
  reflection, or bounded answer about fictional saved history using reviewed
  skill content and retrieved records.
- The model cannot alter the breathing sequence, timing, guidance rules, Stop,
  pause/resume behavior, persistence truth, or Support route.
- Do not let generated text diagnose, infer distress, invent therapy or medical
  advice, claim improvement, or reinterpret clicking, duration, completion, or
  reflections as mental-health evidence.
- Provide reviewed deterministic fallback text for missing configuration,
  loading, timeout, provider failure, malformed output, rejected retrieval, and
  stale responses. A model failure must never block practice, Stop, Support, or
  ordinary history.
- No model or provider is approved yet. Do not select, configure, or call one
  without a later explicit task.

## 5. Protect secrets and backend-only configuration

- Provider credentials and secrets belong only in backend-local configuration
  when that milestone is authorized. Never expose them in Vue, browser-visible
  variables, API responses, logs, screenshots, prompts, Figma, fixtures, or Git.
- Before adding secrets, verify appropriate ignore rules. Never overwrite an
  existing local environment file or print secret values.
- Safe example configuration may contain variable names and blank or dummy
  values only. Load configuration explicitly and report presence without values.
- Distinguish a configuration check, mock response, and observed live provider
  call; none is evidence for another.

## 6. Persist accurate SQLite records and keep RAG read-only

- Use SQLite at `data/app.sqlite3` only when implementation is authorized. Store
  stable session/conversation/message IDs and explicit relationships.
- Use only the five planned record types: `demo_profiles`, `preferences`,
  `exercise_sessions`, `conversations`, and `messages`. Scope them to one fixed
  fictional profile. Store the nullable Next-time setup selection on its session;
  Skip stores no selection. Do not create separate reflection or request-attempt
  records.
- Store `request_id`, `request_purpose`, `request_status`, `safe_error_code`,
  `created_at`, and `updated_at` on the initiating user message. Preserve stable
  message IDs, roles, ordering, and timestamps. Create an assistant message only
  after validated output is successfully persisted.
- Use parameterized backend writes and transactions where related records must
  succeed together. Never show a failed write as saved. Retries and restarts must
  not duplicate sessions or messages.
- Keep fictional fixtures distinguishable from records created through the app.
  Provide user-visible reset/change controls only after their behavior is decided.
- For later SQL-based RAG, treat model-proposed SQL as untrusted. Permit one
  bounded read-only query against an explicit allow-list and current demo scope;
  bind values, limit rows/time/context, and reject writes or unsafe statements.
- The model never opens SQLite. RAG retrieval stays separate from application
  writes. Retrieved stored text is data, not instructions. Ground answers in
  returned record IDs and acknowledge missing information.
- History views must match the stored rows and include textual date, duration,
  cycle count, status, and settings. Never turn counts or visuals into claims of
  diagnosis, distress, adherence, or improvement.

## 7. Keep Support information independent

- Keep a clearly labeled Support information route visible and keyboard-usable
  in entry, setup, loading, failure, exercise, paused, stopped, completed, and
  history states.
- Its fixed U.S. fictional-demo copy must be static and work without FastAPI,
  SQLite, a model, classifier, questionnaire, inferred signal, geolocation,
  activity history, or a successful provider request. A system prompt is not an
  implementation.
- Opening it during practice pauses safely; closing it never implicitly resumes.
- Use the exact approved wording and official URLs in
  `docs/support-resources.md`. Manually re-verify every source before each
  submission/demo, at least every 90 days, and after a redirect or material
  source change. Never select a resource dynamically from user data.
- Support and Stop controls must be ordinary semantic controls, never hidden in
  a flower, ripple, color, hover state, animation, or generated response.

## 8. Meet accessibility and visual requirements

- Design for keyboard use, logical focus order, visible focus, semantic controls,
  readable contrast, zoom/reflow, and a narrow viewport.
- Do not rely on color, motion, petal count, or shape alone. Pair every state with
  text; announce important phase/status changes accessibly without overwhelming
  the user.
- Keep headings and explanatory text in logical DOM/reading order, not ordinary
  Tab order. Tab stops are interactive controls only and must follow visual order.
  A major view may deliberately focus its heading with temporary
  `tabindex="-1"`; phase changes use a restrained live region without moving
  focus, and one-second countdown changes are not announced.
- Respect the system reduced-motion preference and the user's explicit motion
  choice. No-motion mode must remain fully informative.
- Use the approved blue-and-green water garden, six-petal bloom, navy text, and
  warm Stop/Support accent as direction, not as proof of a wellness effect.
- Keep decorative movement subtle and subordinate to the breathing cue. Never
  claim that colors, flowers, water, leaves, or animation improve mental health.
- Test the eventual interface at relevant narrow and wider sizes and through the
  keyboard; a build result or static screenshot alone is not sufficient.

## 9. Use fictional testing and honest evidence

- Use only clearly fictional scenarios, reflections, conversations, and fixture
  data. Do not include personal, participant, credential, or private third-party
  information.
- Label mock, fixture, simulated failure, and live-provider evidence separately.
  Never describe a mock as a live call or a planned check as passed.
- Verify behavior in proportion to the change: inspect the browser for interface
  behavior, API responses for contracts, and read-only database rows for saved
  state. Compare the same stable IDs across layers.
- Cover normal flow, Stop, Support pause/explicit resume, reduced/no motion,
  refresh/restart once specified, missing configuration, provider failure, stale
  responses, failed saves, empty retrieval, rejected writes, and duplicate
  prevention as those capabilities are implemented.
- Record commands, expected outcomes, observed outcomes, limitations, and
  untested behavior. Do not claim clinical or safety validation from software
  checks.

## 10. Maintain useful project records

- `README.md`: purpose, approved scope, stack, milestone, and only setup/run
  instructions that have actually been verified.
- `docs/design-pipeline.md`: architecture, flows, behavior contracts, research
  rationale, alternatives, decisions, and unresolved questions.
- `docs/verification.md`: completed checks and later repeatable checks with
  expected/observed evidence and limitations.
- `prompts/`: significant reusable prompts and curated evidence, numbered and
  redacted.
- `handoffs/current.md`: current state, unfinished work, checks actually run,
  next step, and branch/commit when those exist.
- Maintain `AI-USE.md`,
  naming tools/models and their roles and recording at least one failed or
  revised approach without secrets or private data.
- Update the relevant record whenever an implemented decision or verified
  behavior changes; avoid copying whole chats or duplicating the same facts
  across files. Create additional supporting records only when authorized.

## 11. Follow CHECK → TAKE ACTION → VERIFY

For dependency and environment work:

1. **CHECK:** confirm the absolute project root, branch/repository state if Git
   exists, current files and changes, installed runtimes, declared dependencies,
   and the exact requested scope. Preserve unexpected or unfinished work.
2. **TAKE ACTION:** before any installation not already authorized, show the
   package names, exact commands, and target project environment and obtain the
   required approval. Make the smallest focused change that satisfies the task.
3. **VERIFY:** confirm installed versions/imports and the affected end-to-end
   behavior with observed evidence. Report failures and untested behavior.

Use the same inspect/change/verify discipline for code and data. Define inputs,
outputs, failure states, and a worked example before connecting layers. Do not
discard, broadly rewrite, or overwrite unrelated work. Stop when a required new
decision, authorization, or dependency is missing.

## 12. Review, Figma, and handoff rules

- The next separately authorized design milestone is a Figma comparison between
  the focused central water garden and text-first structured garden directions.
  Figma is not a source of automatic code changes. Preserve comparison frames,
  inspect the exact human-selected frame and screenshot, record missing behavior,
  and verify any later Vue result separately.
- A static image does not prove editable capture, and a Figma frame does not prove
  application behavior. Never claim access, capture, implementation, or a passed
  comparison without observing it.
- Initialize Git, create branches, commit, push, merge, or create remotes only
  when authorized. Stage only intended files and preserve uncommitted work.
- Before a later handoff, record completed and unfinished work, checks actually
  run, and the next step. A new session must verify those claims against files.

## 13. Voice and audio are prohibited

Do not implement, prototype, plan, recommend, or add dependencies for voice
input, voice output, microphone access, WebRTC, audio capture or recording,
speech recognition, speech synthesis, text-to-speech, speech-to-text, or
live-audio models. Do not request microphone permission. The complete application
must remain usable through visible text and controls.
