# Prompt 01 — Create the BreathBloom Project Foundation

- **Date:** October 27, 2026
- **Objective:** Establish the project structure and durable guidance without
  beginning implementation.

## Authorized folders and files

Create empty `frontend/`, `backend/`, `data/`, `docs/`, `prompts/`, and
`handoffs/` directories. Create only root `README.md` and `AGENTS.md`.

## Approved decisions supplied by the human

- Project: BreathBloom — A Guided Paced-Breathing Skills Prototype.
- Boundary: local coursework prototype using fictional scenarios only; no
  diagnosis, therapy, medical advice, monitoring implication, or effectiveness
  claim.
- Skill: paced 4–6 breathing for six cycles and a planned 60 seconds, controlled
  deterministically by application code.
- Visuals: accessible blue/green water garden, expanding/settling Breath Bloom,
  one petal per completed cycle, complete six-petal bloom, and accurate partial
  bloom after Stop.
- Choices: breathing/gentle/no-motion and minimal/standard/more-guidance modes,
  all retaining visible phase, time, and progress.
- Control: explicit Start/Stop, independent Support access, pause on Support, and
  explicit Resume; stopped sessions are not failures.
- Personalization: transparent, changeable preferences and factual history only;
  no behavioral inference, streaks, ranks, or pressure.
- Model boundary: optional bounded introduction/reflection/history answers only;
  no timer, skill, safety-route, diagnosis, or persistence control; deterministic
  fallback required.
- Planned separation: Vue frontend, typed FastAPI backend, and backend-only SQLite
  at `data/app.sqlite3` in a later milestone.
- Voice, microphone, WebRTC, recording, speech input/output, synthesis, and
  live-audio models are prohibited.

## Meaningful foundation instruction

Inspect the new project root before editing and stop if it is not empty. Use the
course starter only as structure; replace undecided placeholders with the supplied
BreathBloom decisions. Document the project purpose, skill, 60-second flow,
visual/accessibility direction, personalization, model limits, records/history,
technology separation, Support route, research rationale/tradeoffs, exclusions,
current milestone, and genuine open questions. Add durable agent rules for scope,
architecture, timing ownership, secrets, RAG, state behavior, safety access,
fictional tests, evidence, accessibility, workflow, documentation, and handoff.

## Explicit prohibitions

Do not install packages; create Vue/FastAPI source, manifests, virtual environments,
credentials, environment files, SQLite data, Git, remote repositories, Figma/MCP
work, provider calls, voice/audio plans, reports, disclosure/design/verification
notes, prompt records, or handoffs at the foundation milestone. Do not copy prior
travel-project source or add any file beyond the two authorized documents.

## Acceptance checks

- Show the resulting tree and confirm all six directories exist and are empty.
- Confirm exactly `README.md` and `AGENTS.md` exist.
- Confirm no dependency, credential, database, Git, Figma, model, voice/audio, or
  application work occurred.
- Summarize the captured decisions, list unresolved decisions, and report every
  created file.

## Recorded result

`README.md` and `AGENTS.md` were created, along with all six empty directories.
The final foundation inspection found exactly those two files, exactly six
directories, no unexpected item, and no Git or prohibited implementation
artifact. No application or external-service work occurred.

This is curated, redacted evidence rather than raw conversation text. It contains
no user-specific absolute path, credentials, environment contents, or unrelated
course-page material.
