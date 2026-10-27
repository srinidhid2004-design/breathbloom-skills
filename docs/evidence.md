# BreathBloom Curated Evidence Log

## Evidence boundary

This is a redacted, project-relevant evidence log rather than a chat transcript.
It contains no credentials, private filesystem paths, personal contact details,
research-participant information, or private account data. Planned behavior is
kept separate from observed static-design and publication checks.

## Prompt-to-result trace

| Prompt | Human authorization or decision | Files/artifacts produced | Checks actually performed |
| --- | --- | --- | --- |
| [`01-project-foundation.md`](../prompts/01-project-foundation.md) | Establish only the project foundation and durable boundaries | `README.md`, `AGENTS.md`, and six directories | Exact tree/count check; empty implementation directories; no Git, dependencies, database, credentials, provider, Figma, or application |
| [`02-part-3-1-research-decisions.md`](../prompts/02-part-3-1-research-decisions.md) | Approve paced 4–6 scope, fixed U.S. Support, five records, simplified API/RAG, accessibility rules, and deferred provider | Decision, Support, design-pipeline, verification, disclosure, and handoff records | Required records reread; official Support URLs checked; tree/content scans; implementation absence confirmed |
| [`03-direction-a-selection-and-figma-reference.md`](../prompts/03-direction-a-selection-and-figma-reference.md) | Human selected Direction A and supplied the selection rationale | Public editable comparison, selected section, 13 static reference frames, overview, and annotations | Historical-frame fingerprints; names/dimensions; controls, vectors, fonts, image fills, text coverage, contrast evidence, and screenshot review |
| [`04-part-3-1-submission-and-publication.md`](../prompts/04-part-3-1-submission-and-publication.md) | Create, audit, commit, publish, and publicly verify the Part 3.1 submission only | `report.md`, this evidence log, final publication records, and public Git history | Complete project/course reread; Figma metadata recheck; pre-Git and staged audits; local/remote SHA and unauthenticated public-link checks |
| [`05-part-3-2-foundation.md`](../prompts/05-part-3-2-foundation.md) | Authorize the Part 3.2 architecture and tested minimal Vue/FastAPI foundation on a feature branch | Implementation plan, pinned manifests, safe health/config backend, minimal accessible frontend, tests, and continuity updates | Exact Git/start gate; official Google model/pricing check; dependency integrity; backend tests/import/health; frontend tests/lint/build; safety and ignored-artifact audits |

## Consequential design comparison

Direction A emphasized a prominent central six-petal bloom and the water/leaf
atmosphere. Direction B emphasized timing clarity, explicit segmented progress,
organization, and accessibility cues. The human selected Direction A because it
communicated the intended identity more clearly and felt calmer, more immersive,
and more distinctive. The selected reference retained A as the direction while
adopting the named clarity features from B; no third direction was created.

## Failed or revised approaches

- The first Figma authentication later expired, so the connection check could
  not proceed. No design content was changed during that failure. After the human
  reauthenticated, the account/file read check succeeded and work resumed. No
  email or authentication value is retained here.
- The first selected-direction visual pass exposed malformed manually rotated
  bloom petals and clipped or overlapping completion/Support text. The affected
  blooms were replaced with editable SVG vectors, spacing was adjusted, overview
  previews were refreshed, and the visual and structural checks were repeated.
- The first data proposal used seven record types. Human review simplified it to
  five by storing Next-time setup on `exercise_sessions` and request lifecycle on
  the initiating `messages` record.
- The first foundation route-count assertion relied on route-object internals
  that changed in FastAPI 0.162, and the first Vue lint pass found 15 formatting
  warnings. The route assertion was changed to the generated OpenAPI path set,
  the component was formatted, and the complete checks then passed.

## Static Figma evidence

- File: https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx
- Selected section: https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=10-286
- Selected overview: https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=14-537
- Observed selected section name/dimensions: **04 / Selected Direction A**,
  2500×9200.
- Observed overview name/dimensions: **Selected Direction A / Overview**,
  2372×1650.
- Thirteen required selected frames were recorded at 390×844 or 1024×768,
  including standard inhale/exhale, No motion, completion, History, and Support.
- Final structural validation reported all 13 frames, zero image fills, zero
  missing fonts, 33 editable vector layers, and 48 control instances meeting the
  44×44 target minimum.

These are static design observations, not runtime evidence.

## Publication evidence

The substantive milestone was committed as
[`aa41c3bda8680439f05fcb68bc6945dff6dbd515`](https://github.com/srinidhid2004-design/breathbloom-skills/commit/aa41c3bda8680439f05fcb68bc6945dff6dbd515)
and pushed to the new public repository. At that checkpoint local `main` and
`origin/main` matched. Unauthenticated retrieval loaded the public repository,
commit, and raw report. Direct no-cookie HTTP retrieval returned status 200 for
the Figma file, selected section, and overview; the Figma browser view resolved
the named file and requested overview without a login or request-access screen.

The following documentation-only commit finalizes the public links and evidence.
Its SHA is intentionally reported outside its own content to avoid a self-
referential loop. The final response and public history identify it exactly. No
application, database, provider, credential, or runtime operation is part of this
evidence.

## Assignment 3.2 foundation evidence

- Feature branch start: `9f7a09d5ceb4fc50520e26ad6140103de3cc903e`.
- Approved provider/model: Google Gemini with stable
  `gemini-3.5-flash-lite`, confirmed against Google's official model, release,
  pricing, and rate-limit pages on October 27, 2026.
- Architecture decision: exactly five planned tables, 11 planned `/api` routes,
  and the exact ten-state top-level state machine recorded in
  `docs/part-3-2-implementation-plan.md`.
- Backend evidence: project-local Python 3.14.7 environment, `pip check` clean,
  three tests passed, FastAPI construction passed, only `/api/health` exposed,
  and the health response reported service `ok`, database `not initialized`, and
  Gemini key `not configured` without a secret/path/exception.
- Frontend evidence: two component tests passed, zero-warning lint passed,
  production build passed, direct dependency tree resolved, and production audit
  found zero vulnerabilities.
- Safety boundary: no credential, local environment file, database, record,
  live-model request, full selected UI, Figma edit, voice/audio feature, alternate
  provider, authentication, analytics, or vector database was added.

These results are local foundation evidence only. The later breathing sequence,
Support independence, persistence, history, model behavior, RAG, accessibility,
and integrated scenarios remain unverified.
