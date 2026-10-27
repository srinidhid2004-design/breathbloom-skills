# BreathBloom — A Guided Paced-Breathing Skills Prototype

IST 402 — Assignment 3 coursework project

## Purpose and boundary

BreathBloom is a planned local application for practicing one short paced-breathing
skill through visible text and controls. It is intended to demonstrate interface,
backend, persistence, and bounded conversational-model design for coursework.

This is a coursework prototype tested only with fictional scenarios. It must not
diagnose, provide therapy, claim clinical effectiveness, give medical advice,
imply that a person is monitoring the user, or be offered as a real mental-health
support service. Activity, completion, and reflection data must never be treated
as evidence of a diagnosis, emotional state, or improvement.

## Current milestone

This repository contains the **completed Assignment 3.1 — Research and Design
milestone**. The authoritative decisions are recorded in
[`docs/part-3-1-decisions.md`](docs/part-3-1-decisions.md), with the fixed U.S.
fictional-demo Support plan in
[`docs/support-resources.md`](docs/support-resources.md). The human-selected
Direction A reference is available in the public Figma file, and the submitted
coursework summary is in [`report.md`](report.md). The repository contains no
dependencies, application source, credentials, database, or provider integration.

**No running application exists yet.** Every runtime behavior remains planned and
unverified even when its design decision is approved.

Public design references:

- [BreathBloom — Assignment 3.1 Design Comparison](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx)
- [Selected Direction A section](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=10-286)
- [Selected Direction A overview](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=14-537)

## Chosen skill and timing

The chosen skill is paced 4–6 breathing:

- inhale for 4 seconds;
- exhale for 6 seconds;
- repeat for six cycles; and
- finish after a planned 60 seconds of exercise time.

Application code—not a language model—will own the sequence, countdown, phase
changes, cycle progress, pause, resume, stop, and completed/stopped status. Entry
and setup time will be reported separately from the exercise. User-chosen pauses
and time spent viewing Support information will not be counted as planned exercise
time, and the interface will never force a person to finish.

## Planned experience

1. Show an accurate coursework label and a persistent route to Support information.
2. Offer **Begin a 60-second practice**, **Use my previous setup**, or
   **Review history**.
3. Let the user choose or confirm motion and guidance preferences.
4. Run the deterministic six-cycle exercise with visible phase, time, and cycle
   progress.
5. Keep **Stop** and **Support information** visible throughout the exercise.
6. Pause the exercise if Support information is opened.
7. Require an explicit **Resume practice** action after the user returns.
8. Save an accurate completed or stopped status and measured duration.
9. Offer optional Next-time setup and factual history controls.
10. Allow saved sessions to be reviewed without making a model request.

A stopped practice is a valid outcome. It retains its completed cycle count and
partial bloom and is never described as a failure.

## Visual and interaction direction

The human selected **Direction A — Focused central water garden** after reviewing
two alternatives. Its prominent central bloom and water/leaf atmosphere remain
primary because they communicate the visual identity clearly and feel calmer,
more immersive, and more distinctive. Direction B was not selected, but its
clearer timing language, explicit six-segment progress, organization, and
accessibility cues were incorporated without creating a third direction.

The interface will use a blue-and-green water-garden theme with flowers, water,
and leaves. A central **Breath Bloom** expands while the interface says **Inhale**
and settles while it says **Exhale**. Each completed cycle adds one petal; six
completed cycles create a six-petal bloom. A stopped session preserves an accurate
partial bloom. A subtle water ripple may mark a completed cycle if it remains
nondistracting.

The planned palette uses pale water and mist backgrounds, water blue, deep lake
blue, leaf green, light sage, and deep navy text. A distinct warm accent will make
important Stop and Support controls identifiable. Meaning will never depend on
color alone, and decorative imagery will never contain or obscure essential
instructions, Stop, or Support information. The project will make no claim that
its colors, imagery, or animation improve mental health.

The interface must support narrow screens, keyboard operation, visible focus,
readable contrast, and text labels for all visual status. Decorative motion must
not compete with the breathing cue.

### Motion choices

- **Full motion:** synchronized flower/orb expansion and contraction.
- **Gentle motion:** smaller size changes paired with a progress ring.
- **No motion:** a static flower with a large phase label, countdown, and cycle
  progress.

Reduced-motion preferences must be respected. Every mode must communicate the
current inhale/exhale phase, time, and cycle progress without requiring animation.

### Guidance choices

- **Minimal:** phase label and progress.
- **Standard:** phase label, countdown, and progress.
- **More guidance:** the same deterministic sequence with brief, reviewed text.

The user chooses the level. Guidance changes presentation only; it cannot alter
the 4-second inhale, 6-second exhale, or six-cycle sequence.

## Personalization and user control

BreathBloom will remember only understandable settings and factual session
history. **Use my previous setup** will state what was remembered before applying
it. Every saved preference can be skipped, rejected, reset, or changed.

The application will not infer distress, diagnosis, emotional state, or
improvement from clicking, timing, completion, duration, or a response. It will
not add streaks, rankings, scores, pressure to continue, or failure language.
After a session, the optional **Next-time setup** control may explicitly reuse or
change motion/guidance, record **No preference**, or be skipped. It is not an
emotional or clinical reflection and does not gate practice, history, or Support.

## Independent Support information

A clearly identified Support information route will remain available in entry,
setup, loading, failure, exercise, paused, stopped, completed, interrupted, and
history states. Its approved content has a fixed national U.S. fictional-demo
scope and separates 911 emergency information, 988 crisis support, and
FindTreatment.gov non-emergency treatment information. It will work as static
frontend content without FastAPI, SQLite, a model, classifier, questionnaire,
geolocation, behavioral inference, or successful provider request.

Opening Support during practice pauses the exercise; returning does not restart
time until the user explicitly chooses **Resume practice**. BreathBloom is not an
emergency service, is not monitored, cannot contact help, and does not infer a
user's location or condition. Exact reviewed wording, official source URLs, and
the manual re-verification procedure are in
[`docs/support-resources.md`](docs/support-resources.md).

## Planned model role and limits

A later conversational model may provide one brief introduction or factual
reflection grounded in reviewed skill material and fictional saved context. It
may also answer bounded questions about saved session history through the
course's reviewed SQL-based retrieval-augmented generation (RAG) pattern.

The model may not control or change the timer, 4–6 sequence, progress, stop,
pause, resume, saved status, or Support access. It may not invent therapeutic or
medical advice, diagnose, infer distress, or present activity as improvement.
Application-owned fallback text must keep the experience usable when a model is
missing, slow, malformed, stale, or fails. No provider or model is selected or
authorized at this milestone.

## Planned records and history

SQLite is planned to use exactly five record types:

- `demo_profiles`: one fixed fictional demo profile;
- `preferences`: explicit motion/guidance choices;
- `exercise_sessions`: UTC timestamps, planned/observed-active/paused/wall-clock
  integer milliseconds, status, cycles, setting snapshots, versions, and a
  nullable Next-time setup selection;
- `conversations`: stable fictional conversation/session relationships; and
- `messages`: stable IDs, roles, ordering, timestamps, and—in the initiating user
  message—bounded request lifecycle fields.

There is no separate reflection or request-attempt record. An assistant message
is created only after validated output is successfully persisted. This five-record
plan reduces implementation and testing scope without weakening honest failure
reporting.

History will show date, duration, cycle count, completion status, and chosen
settings in text. A completed session may also use a six-petal bloom, and a
stopped session may use an accurate partial bloom, but neither visual replaces
its text label. History must remain available without a model request and must
not interpret participation as mental-health improvement.

If RAG is implemented, FastAPI will validate and execute bounded, read-only SQL
retrieval against allowed records. The model will never connect directly to
SQLite, and retrieval will remain separate from parameterized application writes.

## Planned technology and separation

- **`frontend/`:** Vue 3 with JavaScript, HTML, and CSS. It will render the
  interface, own client interaction and deterministic pacing state, and call the
  backend over HTTP/JSON.
- **`backend/`:** typed Python with FastAPI. It will validate requests, enforce
  business rules, manage persistence, and make any later provider calls using
  backend-only configuration.
- **`data/`:** SQLite at `data/app.sqlite3`, accessed only by the backend.

The application is planned to run on localhost. Ordinary practice and history
browsing must not depend on provider availability.

## Research-informed rationale and tradeoffs

The assignment research reports attention loss beyond roughly 90–100 seconds
(R1). BreathBloom therefore selects a 60-second exercise and keeps entry/setup
outside that measurement. The tradeoff is a deliberately narrow practice rather
than a longer or user-composed sequence.

Class guidance emphasizes low reading, typing, and decision effort (D3) while
also preserving meaningful user choice (R4). The entry screen therefore offers a
small set of direct actions, and saved settings can reduce repeated setup. The
tradeoff is that motion and guidance choices still add a brief decision; applying
them automatically was rejected because it would weaken user control.

The personalization finding (D5) supports remembering transparent preferences
and factual history. BreathBloom gains convenience but limits personalization to
information the user can inspect, change, or reset. It gives up opaque adaptation,
prediction, streaks, and inferred recommendations.

The course warns that interface behavior does not reliably detect distress (D1).
BreathBloom therefore keeps self-report, observed interaction, and interpretation
separate and never adapts based on inferred emotion. This gives up automatic
"smart" intervention in exchange for honest evidence and user-directed choices.

Motion can carry a paced-breathing cue, but it may distract or be inaccessible.
The selected design pairs the bloom with phase text, time, and cycle progress and
offers gentle and no-motion alternatives. The water-garden metaphor makes
progress visible, while the tradeoff is additional decorative complexity that
must be constrained and tested for readability.

The model is bounded to optional language and history questions because generated
text may vary or fail. Deterministic application code and fallback copy provide
less conversational flexibility but preserve the exact skill, exits, persistence,
and Support route.

## Explicitly outside scope

Voice input, voice output, microphone access, WebRTC, audio recording, speech
recognition, speech synthesis, and live-audio models are prohibited for this
project. The complete experience must remain usable through visible text and
controls. No voice or audio functionality will be implemented or planned.

## Project structure at this checkpoint

```text
breathbloom-skills/
|-- .gitignore
|-- README.md
|-- AGENTS.md
|-- AI-USE.md
|-- report.md
|-- frontend/
|-- backend/
|-- data/
|-- docs/
|   |-- design-pipeline.md
|   |-- evidence.md
|   |-- part-3-1-decisions.md
|   |-- support-resources.md
|   `-- verification.md
|-- prompts/
|   |-- 01-project-foundation.md
|   |-- 02-part-3-1-research-decisions.md
|   |-- 03-direction-a-selection-and-figma-reference.md
|   |-- 04-part-3-1-submission-and-publication.md
|   `-- README.md
`-- handoffs/
    `-- current.md
```

`frontend/`, `backend/`, and `data/` are intentionally empty at this milestone.
The other directories now contain only the authorized continuity records shown
above. Application and runtime artifacts will be added only when a later milestone
authorizes them.

## Remaining unresolved work

Part 3.1 design work is complete. These later decisions and implementation tasks
remain unresolved and must not be silently invented:

- Which provider and model, if any, will be proposed and separately authorized,
  with what exact timeouts, retries, call budget, and malformed-output rules?
- What exact Part 3.2 implementation sequence will establish the Vue, FastAPI,
  SQLite, deterministic timing, Support, persistence, and verification foundation?
