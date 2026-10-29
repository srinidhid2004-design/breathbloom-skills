# Prompt 09 — FocusBloom Vue experience

## Authorized objective

Implement and publish the complete Vue 3 FocusBloom experience from the approved
editable Figma references on `feature/assignment-3-part-2`. The checkpoint was
limited to frontend code, tests, public-safe documentation, temporary-database
integration checks, and read-only Figma inspection. It prohibited a real
credential, live Gemini request, project runtime database, Figma modification,
voice/audio, and changes to historical Part 3.1 evidence or `main`.

## Implemented result

- Replaced the foundation screen with the 17 named interface states: entry;
  Focus ready, active, stopped, and completed; Perspective entry, evidence,
  alternative loading, ready, and model-failed; Next-Step Seed; History; Garden
  Guide loading, answer, no-match, and query-rejected; and independent Support.
- Added one-action Focus Garden start and functional keyboard-operable
  presentations for all seven backend activities. Each has literal instructions,
  three text-equivalent choices, neutral retry feedback, Show me, Skip, Stop,
  Support interruption, and accurate terminal writes without scores or streaks.
- Added the fictional and optional custom Perspective paths, evidence and
  uncertainty cards, exact request preview, explicit Gemini request, deterministic
  continue-without-model path, alternative accept/edit/reject/create controls,
  optional fictional Perspective Lens, and explicit artifact save/delete.
- Added previewed, explicitly saved, editable/deletable user-authored Next-Step
  Seeds; factual History cards and filters; saved-text deletion and confirmed
  reset; suggested Garden Guide questions; grounded answers, no-match and
  rejected-query states; and a collapsed safe trace disclosure.
- Added static U.S. Support wording and controls from
  `docs/support-resources.md`. Support has no API, model, database, location,
  classifier, or saved-history dependency.
- Added a single normalized API service and stale/cancellation composable. The
  browser sends only approved fields and never selects a provider, model, key,
  prompt, SQL, profile, or database path.

## Figma-to-code observations

Read-only inspection covered overview `27:719`; entry `24:594`; No-motion Focus
Garden `24:666`; completion `24:708`; Perspective evidence, alternatives, and
Lens `25:668`, `25:698`, `25:729`; Next-Step Seed `25:757`; History `25:790`;
Garden Guide answer `26:718`; Support `26:745`; and wide composite `26:778`.
No external Figma library was attached. The runtime reuses deep navy text, water
blue borders, leaf-green primary actions, pale mist/sage surfaces, a warm
Stop/Support accent, rounded cards, literal status pills, and 48-pixel controls.

Narrow screens use one column; wide entry and history use space-efficient grids.
The implementation fixes static-frame text collisions, permits content height to
grow, and uses semantic HTML rather than absolute positioning. The approved API
intentionally does not return proposed SQL, bound parameters, or retrieved rows
to the browser, so the trace names that privacy boundary and displays only
returned row references and safe lifecycle facts. It never fabricates hidden
trace data.

## Verification evidence

- Frontend: 2 files, 17 tests passed; ESLint passed with zero warnings; Vite
  production build passed with 22 modules transformed.
- Backend regression: 52 tests passed using temporary databases; two known
  dependency warnings remained. `pip check` reported no broken requirements.
- Automated browser: exact 390×844 and 1024×768 iframe viewports rendered the
  running interface against a disposable temporary SQLite database and a missing
  Gemini key. One-tap Focus start, neutral retry, Support interruption/return,
  missing-configuration preservation, continue-without-model, and factual
  terminal History status were observed. Browser warning/error logs were empty.
- The disposable viewport harness was deleted after inspection. No screenshot
  file was retained because the observed states are already described here and
  contained no unique cross-layer evidence.
- Static scans found no provider endpoint, authorization header implementation,
  database path, credential value, voice/audio implementation, or `v-html` in
  production frontend source/build. Negative assertions contain the searched
  terms only in tests.

## Bounded AutoLoop corrections

Three correction cycles were used. The first applied existing ESLint formatting
rules and corrected test setup expectations without weakening assertions. The
second fixed a live-browser-discovered lifecycle gap: leaving Perspective after
a missing-configuration/continue-without-model path now terminalizes the session
before History or Next-Step Seed, so History never mislabels it as active. The
third acceptance audit made all seven implemented activity renderers reachable
through an optional chooser while preserving the one-action default start.

## Remaining work

A real Gemini key is not needed for this checkpoint. A separately authorized
live-provider verification remains, as does final full cross-layer evidence for
successful generated alternatives and successful two-request grounded answers.
Official Support sources must be manually rechecked immediately before the next
graded submission or demonstration.
