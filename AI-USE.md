# AI use record

## Boundary

AI tools assisted with research synthesis, architecture planning, editable Figma
construction, safe scaffold branding, tests, and documentation. Human-approved
decisions define the active FocusBloom scope. AI output is not evidence of
clinical safety, effectiveness, user benefit, or crisis detection. Only fictional
examples and credential-free mocks are permitted.

## Tools and roles

- **OpenAI Codex:** inspected the repository, maintained project records, applied
  basic branding, designed the proposed state/data/API/model contracts, ran local
  checks, and managed the authorized feature-branch publication. It did not make
  clinical decisions.
- **Figma integration:** inspected the existing editable design, reused the water-
  garden variables/styles, created the new FocusBloom section and editable frames,
  and ran programmatic structural checks. Browser control was used only for the
  file-level rename that the integration did not expose.
- **Internet research/search:** opened the eight named primary research sources
  and recorded limited findings. Studies were not treated as proof of FocusBloom
  outcomes.
- **Google Gemini (`gemini-3.5-flash-lite`):** is the fixed backend adapter model
  for two bounded purposes. Version-2 tests used an injected fake gateway only;
  no live request or real credential was used.
- **Git/GitHub:** verified branch/history state, retained the existing repository,
  and published only the authorized feature-branch pivot. No second repository,
  history rewrite, force push, or `main` change is permitted.

No voice, audio, microphone, speech, biometric, geolocation, participant, or
private third-party tool/data was used.

## Human-approved product decisions

- Rename the active product to FocusBloom and preserve historical BreathBloom
  evidence.
- Make Focus Garden the primary no-typing experience.
- Use Perspective Studio's five-step one-minute cognitive reframe as the formal
  course skill, with fictional-example and optional fictional-observer paths.
- Keep Next-Step Seed optional and user authored.
- Keep History Garden factual and unscored.
- Bound Gemini to perspective alternatives and read-only factual history RAG.
- Keep Support static and independent.
- Retain the local folder name for tool/project continuity while renaming the
  public repository.

## Figma construction and validation

The integration reused existing editable visual foundations and created section
`05 / FocusBloom Part 3.2 Pivot`, 16 required product frames, three reusable
components, and a selected overview. It checked dimensions, overflow, fonts,
placeholder copy, control sizes, primary-action count, and Support availability.
A screenshot review found an overview design note overlapping the legend; the
note positions were revised and the screenshot was reviewed again.

One early scripted construction approach tried to reuse component-property keys
and ellipse-node construction assumptions that were not valid for the available
Figma Plugin API context. The approach was revised to set supported node
properties directly and create fresh editable shape nodes. The rejected approach
was not kept in the design. This is a tooling correction, not a design outcome.

Static Figma validation does not prove keyboard behavior, reflow, persistence,
provider behavior, or runtime accessibility.

## Research assistance and limits

AI summarized visual-search, digital-nature, reappraisal/distancing,
third-person self-talk, implementation-intention, and affect-labeling research.
The active pivot record links the primary sources and states their limitations.
The research supports questions and design rationale, not claims that FocusBloom
calms, treats, restores attention, or improves a user.

## Runtime model contract (implemented and mocked)

Perspective alternatives use at most one request, strict bounded JSON, no advice,
no automatic save, zero retries, and no provider/model fallback. History RAG uses
at most two requests: one SQL proposal followed by one grounded answer only when
validated rows exist. The backend validates a deliberately small SELECT grammar,
uses a read-only URI, default-deny authorizer, bound execution/payloads, snapshot
check, and row-reference validation, and rejects mutations before execution.
Application-owned fixed status messages handle missing configuration or failure
without fabricating model content.

The first complete version-2 test cycle passed, but review found two boundaries
that were correctable before publication: reused idempotency keys needed to
conflict when content differed, and the SQL WHERE grammar was initially broader
than necessary. The implementation was revised to compare stored input hashes/
content and to accept only allow-listed bound comparison predicates. The full
suite passed again. This is mocked adapter evidence, not a live-provider result.

## Evidence integrity

Prompt records distinguish requested work from observed results. The submitted
Part 3.1 report and prompts 01–06 are unchanged. Tests, Figma checks, Git checks,
and repository-redirect checks are recorded only after observation. A mock is
never described as a live call. Version-2 backend behavior is described as
implemented only where temporary-database and fake-gateway tests observed it;
frontend behavior is now implemented and locally verified; live-provider
behavior remains unverified.

## Prompt 09 frontend implementation

Codex used the mandatory Figma design-to-code workflow for read-only inspection
of the approved overview and representative narrow/wide frames, then translated
the static React/Tailwind-like context into the repository's Vue 3 Composition
API and plain CSS. No Figma content was modified and no temporary Figma asset URL
was used at runtime.

Codex created focused Vue components, a normalized API service, a stale-request
guard, deterministic visual-activity data, and contract/UI tests. Automated
browser control exercised the running app only against a disposable temporary
database and missing-key configuration. The browser produced no warning/error
logs. No live Gemini request or real credential was used.

The first implementation pass passed the build but exposed existing ESLint
formatting expectations and two test setup assumptions; formatting and test
fixtures were corrected. A later live browser pass exposed an active Perspective
session when the user left after continuing without Gemini. The lifecycle was
revised to persist stopped or completed status before navigation, and the full
frontend checks passed again. These were tooling/runtime corrections, not claims
of clinical benefit.
