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

This feature branch implements the approved Assignment 3.2 FocusBloom backend
and Vue experience. It has the exact nine-table version-2 SQLite schema,
22-operation `/api` surface, factual activity/session persistence, explicitly
saved Perspective artifacts and Next-Step Seeds, ordered history conversations,
lifecycle-only model records, one-request Perspective alternatives, and the
bounded two-request history RAG workflow. The previous breathing-specific
version-1 implementation remains only in Git history and historical records.

The October 29 integrated checkpoint passed the complete automated regression
and exercised the running application at 390×844 and 1024×768. Two early
fictional Perspective submissions failed safely. A narrow provider-schema
correction then enabled one-request Perspective success while retaining
unchanged Pydantic validation. An instruction-only alignment to the unchanged
read-only SQL validator enabled the final two-request Garden Guide flow with two
bounded rows and references 1 and 2. One artifact and one user-authored Seed
were explicitly saved; the artifact was later deleted while the Seed remained.
Support stayed provider-independent, and the direct application console was
clean. The ignored runtime database is not tracked and is not used by final
regression.

Authoritative active records:

- [Product pivot](docs/focusbloom-pivot.md)
- [Assignment 3.2 implementation contract](docs/part-3-2-implementation-plan.md)
- [Design pipeline](docs/design-pipeline.md)
- [Support resources](docs/support-resources.md)
- [Verification record](docs/verification.md)
- [Assignment 3.2 report](reports/assignment-3-part-2/report.md)
- [Current handoff](handoffs/current.md)

The submitted Part 3.1 [report](report.md), prompt records 01–06, original Figma
comparison frames, and assessed commits remain historically accurate BreathBloom
evidence.

> After Part 3.1 submission and a classroom comparison in which multiple projects centered paced breathing, the project was deliberately revised to explore a more distinctive attention-and-perspective interaction. This classroom observation is user-reported design input, not research evidence or proof of effectiveness.

The retained local folder name `breathbloom-skills` preserves tool/project
continuity. The active product and public repository are named FocusBloom.

## Implemented experience

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

The backend tests initialize version-2 databases only in temporary test
directories. Prompt 10 separately initialized the approved ignored project
runtime database and made one bounded live request from the supplied fictional
Perspective example. The Vue application implements the selected FocusBloom
experience and the exact approved backend contracts.

## Technology and security boundary

- `frontend/`: Vue 3, JavaScript, HTML, and CSS; owns interaction and accessible
  visible state.
- `backend/`: typed Python/FastAPI; owns validation, persistence, and the only
  optional provider calls.
- `data/`: ignored runtime SQLite `data/app.sqlite3`, opened only by the backend
  when the server is deliberately started; the current file contains only this
  checkpoint's fixed fictional verification state and is not tracked.
- Google Gemini model is fixed to `gemini-3.5-flash-lite`; the key is backend
  only. No alternate provider/model or automatic retry is used by the adapter.
  The integrated checkpoint retained two earlier bounded Perspective failures,
  then verified one corrected Perspective call and one two-request Garden Guide
  flow. No key, raw provider payload, request header, or environment content was
  exposed.

Voice input/output, microphone use, WebRTC, recording, speech recognition,
speech synthesis, and live-audio models are prohibited. The complete application
must remain usable through visible text and controls.

## Implemented Vue experience

The frontend now provides the 17 named states, one-action/no-typing Focus Garden,
Standard and No-motion parity, fictional and optional custom Perspective paths,
Perspective Lens, explicit artifact and Next-Step Seed saves, factual History
Garden, bounded Garden Guide outcomes, and static independent Support. Major
state changes focus the new heading; Support traps and restores focus; controls
are at least 44 pixels; reduced motion removes transitions; and 390×844 and
1024×768 running viewports were inspected with no browser application errors.

Use the existing verified commands above for tests and builds. For runtime work,
set `DATABASE_PATH` to an explicit disposable or approved backend path before
starting Uvicorn; omitting it would create the planned project runtime database.
The Vite development server proxies `/api` to `http://127.0.0.1:8000`.

## Integrated verification status

Perspective generation, explicit artifact and Seed saves, the bounded Garden
Guide retrieval/grounding flow, targeted artifact deletion with Seed retention,
independent Support, focus restoration, and a clean direct Edge console are now
verified with fictional runtime data. One Prompt 10D diagnostic exposed an
instruction/validator mismatch; only the `history_sql` instruction was aligned
to the unchanged read-only validator and covered by focused tests. The fixed
model, zero-retry policy, two-request maximum, schema, API, SQL allow-lists, and
read-only protections remain unchanged.

The Canvas-ready Assignment 3.2 report is
[`reports/assignment-3-part-2/report.md`](reports/assignment-3-part-2/report.md).
Official Support sources were manually rechecked on October 29, 2026, and the
final feature regression passed without a provider request or runtime-database
access. Canvas upload remains a manual human action. No key is needed for
ordinary Focus Garden, History browsing, saved-text controls, or Support.
