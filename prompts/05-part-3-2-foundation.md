# Prompt 05 — Part 3.2 Foundation

## Human authorization and requested result

The human authorized Checkpoint 1 of a five-checkpoint Assignment 3.2 workflow on
`feature/assignment-3-part-2`, starting only from the exact published Part 3.1
SHA. The task requested a traceable implementation architecture, an officially
verified stable no-cost-suitable Google Flash-Lite identifier, exact five-table
and `/api` plans, an exact state machine, tested minimal Vue/FastAPI scaffolds,
safe backend-only configuration, documentation updates, one normal commit, and a
normal branch push.

The authorization explicitly excluded the full selected Figma experience, full
database/business behavior, database creation or records, a real credential,
live provider requests, provider/model fallback, voice/audio, authentication,
analytics, vector databases, changes to `main`, and replacement of the submitted
Part 3.1 `report.md`.

## Verified pre-change state

- Active branch was `main`; tree and index were clean.
- Local `main` and `origin/main` both resolved to
  `9f7a09d5ceb4fc50520e26ad6140103de3cc903e` after fetching.
- Assessed commit `aa41c3bda8680439f05fcb68bc6945dff6dbd515`
  remained in history.
- `frontend/`, `backend/`, and `data/` were empty; no application source or
  dependency manifest existed.
- Ignore and tracked-file scans passed for secrets, private paths, runtime
  database, local environments, dependencies, builds, caches, and logs.
- The feature branch was created at the exact verified start SHA; `main` was not
  changed.

## Decisions recorded

- Provider: Google Gemini Developer API.
- Model: stable `gemini-3.5-flash-lite`. Google's official model and release
  pages identify it as stable/GA, and the official pricing page lists free-tier
  standard input/output as free of charge. Account-specific access/limits may
  differ and require later checking.
- Role: optional brief introduction, factual reflection, or bounded factual
  history answer only. There is no fallback model or automatic retry.
- Data: exactly `demo_profiles`, `preferences`, `exercise_sessions`,
  `conversations`, and `messages`; optional Next-time setup stays on sessions and
  request/reflection lifecycle stays on messages.
- API: 11 final planned routes. Static Support deliberately has no API route.
- Top-level states: `setup`, `ready`, `inhale`, `exhale`, `stopped`, `completed`,
  `model-loading`, `model-failed`, `support-open`, and `history`.

The full constraints, relationships, transitions, timing/stale-response rules,
traceability matrix, and five-checkpoint order are in
`docs/part-3-2-implementation-plan.md`.

## Implemented foundation

- Typed FastAPI package with an application factory and only
  `GET /api/health` under `/api`.
- Lazy backend settings using secret-safe `GEMINI_API_KEY` loading from process
  environment or ignored `backend/.env`.
- Health returns only `service`, `database`, and `gemini_api_key` statuses.
- Explicit minimal SQLite initializer exists but is not invoked; no schema,
  database, or records were created.
- Blank `backend/.env.example`; no local `.env` was created.
- Minimal Vue 3 JavaScript/Composition API/Vite screen with an accurate fictional
  coursework boundary and visible Practice, History, and Support placeholders.
  It is intentionally not the selected Figma experience.
- Exact direct dependency pins, frontend lockfile integrity metadata, backend and
  frontend tests, lint configuration, and clean-checkout instructions.

## Observed verification

- Python 3.14.7 project-local environment installed all pinned packages;
  `pip check` found no broken requirements.
- Backend: three tests passed; app construction identified FastAPI; OpenAPI
  contained only `/api/health`; the observed health response was HTTP 200 with
  service `ok`, database `not initialized`, and Gemini key `not configured`.
- Node.js 24.20.0/npm 11.19.0 installed 189 frontend packages from the pinned
  manifest; the direct tree matched. One test file/two tests passed, ESLint passed
  with zero warnings, the production build passed, and production audit reported
  zero vulnerabilities.
- The first route-count assertion depended on an outdated route-object shape and
  the first lint pass found 15 formatting warnings. The assertion was changed to
  the generated OpenAPI path set, the component was formatted, and every check
  was rerun successfully.
- No credential, local `.env`, database operation, record, fictional scenario,
  provider request, Figma modification, voice/audio feature, alternate provider,
  authentication, analytics, or vector database was used.

The final commit uses the required subject **Establish Assignment 3 Part 2
foundation**. Its SHA and the final local/remote equality are reported outside
this file to avoid a self-referential commit.
