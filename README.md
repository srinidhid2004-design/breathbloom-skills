# FocusBloom — An Attention-and-Perspective Garden Prototype

IST 402 — Assignment 3 coursework project

## Purpose and boundary

FocusBloom is a fictional local coursework prototype that combines brief
visual-attention activities, a structured one-minute perspective exercise,
optional user-authored next-step plans, factual activity history, and a bounded
Gemini assistant.

It is not therapy, diagnosis, crisis detection, a monitored service, a validated
attention-restoration intervention, a measure of anxiety, distress, or
improvement, or a substitute for professional or emergency support. It is tested
only with fictional scenarios and must not infer emotion or crisis state from
text, clicks, timing, completion, or history.

## Current milestone

This feature branch records the approved Assignment 3.2 product pivot and design
contract. It includes editable FocusBloom Figma references, a proposed nine-table
version-2 schema, an exact 22-operation `/api` plan, two bounded Gemini workflows,
and basic scaffold branding. It does **not** implement the complete revised
frontend, database, API, Perspective Studio backend, or RAG layer.

The existing FastAPI/SQLite code is the tested version-1 BreathBloom backend. It
is preserved for history and reusable engineering patterns, but its five-table
schema, 11-route surface, breathing session rules, and model contract are legacy
and must be replaced before the backend represents FocusBloom. No runtime
database, local environment file, real key, or live Gemini request is part of
this pivot.

Authoritative active records:

- [Product pivot](docs/focusbloom-pivot.md)
- [Assignment 3.2 implementation contract](docs/part-3-2-implementation-plan.md)
- [Design pipeline](docs/design-pipeline.md)
- [Support resources](docs/support-resources.md)
- [Verification record](docs/verification.md)
- [Current handoff](handoffs/current.md)

The submitted Part 3.1 [report](report.md), prompt records 01–06, original Figma
comparison frames, and assessed commits remain historically accurate BreathBloom
evidence.

> After Part 3.1 submission and a classroom comparison in which multiple projects centered paced breathing, the project was deliberately revised to explore a more distinctive attention-and-perspective interaction. This classroom observation is user-reported design input, not research evidence or proof of effectiveness.

The retained local folder name `breathbloom-skills` preserves tool/project
continuity. The active product and public repository are named FocusBloom.

## Planned experience

### Focus Garden

The entry screen offers a one-tap **Start a Focus Garden** path. Each optional
activity presents one visual-search task and one visible instruction at a time,
requires no typing, and keeps **Show me**, **Skip this**, **Stop**, and Support
available. Activities are unscored and cannot be described as treatment,
grounding, or clinically effective.

### Perspective Studio

The formal course skill is a one-minute cognitive reframe controlled by the
application and user:

1. identify an interpretation;
2. consider supporting evidence;
3. consider uncertainty or evidence that does not establish it;
4. consider an alternative; and
5. accept, edit, reject, or create an alternative.

**Try a fictional example** completes the demonstration without personal input.
A custom path uses at most one short initial field. Optional Perspective Lens
uses a fictional observer. The user sees what would be sent to Gemini, may
continue without it, and saves nothing without explicit preview and Save.

### Next-Step Seed

An entirely optional, user-authored if–then plan uses `If [situation], then I
will [small user-chosen action].` Gemini may format the user's choice but cannot
choose an action. Part 3.2 has no notifications or reminders.

### History Garden and Garden Guide

History Garden shows factual activity type, date/time, status, duration,
difficulty, settings, Perspective Studio progress, saved-artifact state, and
model outcome. It has no mood, diagnosis, improvement, effectiveness, rank,
streak, or failure measure.

Garden Guide provides suggested factual questions before an optional text field.
Its history feature uses a two-request flow: Gemini proposes one read-only query,
the backend validates and executes it through a bounded read-only SQLite
connection, then Gemini may answer only from returned rows. Zero rows produce a
no-match response; unsafe SQL is rejected; there are zero retries and no
provider/model fallback.

## Low-input rules

- One primary action per screen and progressive disclosure.
- Optional actions are visibly optional; Skip, Stop, Back, and Support carry no
  penalty.
- No questionnaire, mood score, forced completion, timed response, or remembered
  instruction from an earlier screen.
- Focus Garden has a no-typing route; Perspective Studio has a fictional no-input
  route.
- Current instructions stay visible in short literal language.
- Difficulty changes are explicit and reversible.
- Standard and No-motion modes communicate the same information without relying
  on color, shape, or animation.
- Saved preferences are explained, editable, and resettable.

## Figma reference

- [FocusBloom — Assignment 3 Design Evolution](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx)
- [FocusBloom pivot section](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=21-594)
- [Selected FocusBloom overview](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=27-719)

The new section contains 14 narrow 390×844 references, two wide 1024×768
references, reusable editable components, and a 2500×1160 overview. Historical
Part 3.1 sections remain. Static Figma inspection is not runtime verification.

## Existing foundation and local checks

Prerequisites used by the preserved scaffold are Python 3.14 and Node.js 24.
From the repository root in PowerShell:

```powershell
backend/.venv/Scripts/python.exe -m pip check
Push-Location backend
.venv/Scripts/python.exe -m pytest -q
Pop-Location
Push-Location frontend
npm test
npm run lint
npm run build
Pop-Location
```

Starting the existing backend would initialize the legacy version-1 database, so
it is not part of this planning checkpoint. The tests use temporary databases.
The visible Vue screen is only a branded foundation scaffold, not the Figma
experience.

## Technology and security boundary

- `frontend/`: Vue 3, JavaScript, HTML, and CSS; owns interaction and accessible
  visible state.
- `backend/`: typed Python/FastAPI; owns validation, persistence, and the only
  optional provider calls.
- `data/`: future SQLite `data/app.sqlite3`, opened only by the backend.
- Google Gemini model is fixed to `gemini-3.5-flash-lite`; the key is backend
  only. No alternate provider/model, automatic retry, or live request is
  authorized by this checkpoint.

Voice input/output, microphone use, WebRTC, recording, speech recognition,
speech synthesis, and live-audio models are prohibited. The complete application
must remain usable through visible text and controls.

## Next implementation checkpoint

Replace the legacy version-1 schema/routes with the tested version-2 contract in
small reviewable layers, using temporary databases and mocked Gemini only. Then
implement the FocusBloom Vue states and static Support experience, integrate
them, and verify keyboard, reflow, No-motion, cancellation, persistence, and
factual history behavior. A live provider check requires separate authorization.
