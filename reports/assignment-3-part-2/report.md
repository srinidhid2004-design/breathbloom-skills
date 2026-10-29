# Assignment 3.2 — FocusBloom

## Project boundary

FocusBloom is a fictional, local coursework prototype for brief visual-attention
activities and a structured perspective exercise. It is not therapy, diagnosis,
medical advice, crisis detection, monitoring, clinical validation, or evidence
that attention or well-being improved. All implementation and verification
scenarios used fictional records.

## Public submission references

- [Public repository](https://github.com/srinidhid2004-design/focusbloom)
- [Assessed implementation commit `1bcc8acafdfd6c69d0566b27fd83eb22e6001006`](https://github.com/srinidhid2004-design/focusbloom/commit/1bcc8acafdfd6c69d0566b27fd83eb22e6001006)
- [Assignment 3.2 report](https://github.com/srinidhid2004-design/focusbloom/blob/main/reports/assignment-3-part-2/report.md)
- [Public Figma file](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx)
- [FocusBloom pivot section](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=21-594)
- [Selected FocusBloom overview](https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=27-719)
- [Product pivot](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/focusbloom-pivot.md), [implementation plan](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/part-3-2-implementation-plan.md), [verification record](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/verification.md), and [curated evidence log](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence.md)

## Design evolution

Part 3.1's BreathBloom paced-breathing direction remains historical evidence; it
was not rewritten for this submission. After that submission, a classroom
comparison showed that multiple projects used paced breathing. The human owner
approved a pivot to a more distinctive attention-and-perspective interaction.
That classroom observation is design input, not research evidence or proof of
effectiveness. FocusBloom retains the selected direction's pale blue/green
water-garden language, navy text, rounded cards, leaf green, and warm accents
for Stop and Support without claiming that the imagery changes mental health.

## Implemented experience

The entry view has one low-input primary action and optional, explained
preferences. Focus Garden offers seven unscored, no-typing visual activities,
each with one visible instruction plus **Show me**, **Skip this**, **Stop**, and
Support. Standard and No-motion expose the same text and controls. Stopped,
skipped, interrupted, and stale-request states remain factual and carry no
penalty.

Perspective Studio implements an interpretation → supporting evidence →
uncertainty → alternative → accept/edit/reject/create sequence. **Try a
fictional example** completes the path without personal input. Perspective Lens
uses an optional fictional observer, never a required real name. No Perspective
artifact exists until the user reviews an alternative and explicitly saves it;
the saved artifact can be deleted independently.

Next-Step Seed is an optional, user-authored if–then plan. Gemini may format the
chosen action but cannot select it. History Garden shows factual metadata and
explicit saved/deleted states. Garden Guide answers only bounded factual-history
questions. Static U.S. demo Support remains visible and works independently of
FastAPI, SQLite, Gemini, classification, geolocation, history, or network
success.

## Formal course skill

The formal course skill is the one-minute cognitive-reframe sequence implemented
by Perspective Studio. Focus Garden is an optional visual-attention activity; it
is not described as therapy, grounding, treatment, or a clinically validated
intervention.

## Architecture

The Vue 3 frontend owns interaction state, visible activity evaluation, focus,
cancellation, and stale-response guards. The typed FastAPI backend owns
validation, transactions, persistence, and the only provider calls. SQLite
schema version 2 contains the nine approved tables: `demo_profiles`,
`preferences`, `activity_sessions`, `activity_events`,
`perspective_artifacts`, `next_step_seeds`, `conversations`, `messages`, and
`model_requests`. The documented HTTP/JSON surface has exactly 22 operations.
The Gemini adapter is backend-only.

## Model role and safe RAG

Gemini is fixed to `gemini-3.5-flash-lite`, with zero automatic retries and no
provider or model fallback. Perspective alternatives permit one request and at
most two validated alternatives. Garden Guide permits two requests: first a
bounded read-only SQL proposal, then—only after validated, nonempty
retrieval—a grounded answer. Navigation, activity rules, saving, deletion,
reset, and Support remain application-owned. Model output is never saved
automatically and cannot provide advice, diagnosis, action selection, emotional
or crisis inference, or an effectiveness claim.

For history RAG, the model proposes a narrow `SELECT`; it never executes SQL.
The unchanged validator enforces approved tables, columns, functions, grammar,
trusted backend binding of the fictional profile, bound non-profile values, and
one limit. Execution uses a read-only SQLite URI, query-only protections, a
default-deny authorizer, a snapshot check, and limits of 20 rows, 8 columns,
8 KiB, and 100 ms. A second request occurs only for valid nonempty rows, and the
answer must cite valid row references. Mutations, unsafe proposals, no-match
results, and invalid grounding cannot produce a grounded assistant message.

## Persistence and user control

History stores factual states such as activity type, time, duration, difficulty,
motion setting, completion state, saved-text state, and model outcome. Artifacts
and Seeds require explicit preview and Save. Targeted deletion and a confirmed
complete fictional-profile reset are separate operations. The prototype stores
no real identity and has no streaks, rankings, missed-day pressure, mood score,
or inferred user state.

## Accessibility and low-input design

Views use one primary action, progressive disclosure, literal current
instructions, optional typing, a fictional-example path, semantic controls,
logical keyboard order, and visible focus. Escape closes overlays and restores
focus. The running interface was checked at 390×844 and 1024×768. Explicit
No-motion and system reduced-motion rules preserve the same information while
removing scale, ripple, fade, and translation. Visual states have text
equivalents, and Support is independent of application services.

## Verification

Final feature-branch regression on October 29, 2026 observed:

- backend: **69 passed**, with two known non-failing dependency deprecation
  warnings; `pip check` found no broken requirements;
- frontend: **17 passed**; ESLint passed with zero warnings; the production build
  transformed **22 modules**;
- OpenAPI: exactly **22 operations**;
- a clean disposable schema: version **2**, exactly **9 tables**,
  `integrity=ok`, and **0** foreign-key violations;
- focused SQL-validator, request-count, and grounding checks: **50 passed**;
- credential-marker, token, private-path, tracked-runtime/generated-file,
  `v-html`, and ignore-rule audits passed.

Earlier bounded integrated verification used the supplied fictional example.
Perspective succeeded with one request and no automatic save. Garden Guide used
exactly two requests, retrieved two bounded rows, and produced a factual answer
with references 1 and 2. There was no retry or fallback. The artifact was then
deleted while its Seed remained. Support opened without adding a provider row,
and a clean direct application tab showed no console warning or error. The six
recorded provider lifecycle rows were not changed during finalization.

These are software observations, not clinical or effectiveness validation.
Official Support sources were manually rechecked on October 29, 2026; titles,
organizations, HTTPS destinations, purposes, and the 988 chat redirect matched
the documented three-category boundary.

## Public-safe evidence

Successful flow evidence:

- [Perspective alternatives succeeded](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-perspective-success.jpg)
- [Artifact and user-authored Seed explicitly saved](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-saved-artifact-seed.jpg)
- [Garden Guide grounded answer with collapsed trace](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-garden-guide-success.png)
- [Artifact deleted while Seed remained](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-artifact-deleted-seed-retained.png)
- [Focus Garden completion](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-focus-complete.jpg) and [factual History](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-focus-history.jpg)
- [Independent Support](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-support-independent.jpg), [No-motion](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-no-motion.jpg), and [1024×768 keyboard/focus view](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-responsive-keyboard-1024.jpg)

The [provider-unavailable](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-perspective-provider-unavailable.jpg)
and [query-rejected](https://github.com/srinidhid2004-design/focusbloom/blob/main/docs/evidence/10-garden-guide-query-rejected.jpg)
screenshots document safe failure handling from earlier attempts; they are not
presented as final success evidence. Public evidence contains no credential,
environment content, private path, raw SQL, database, provider payload, or real
personal information.

## AI-use disclosure

Codex assisted with planning, code, tests, documentation, audits, and browser
verification. The Figma integration created and inspected editable static design
references. Mock gateways verified deterministic failure and boundary cases.
Gemini was used only for separately authorized bounded diagnostics and live
fictional Perspective/Garden checks. The [full AI-use record](https://github.com/srinidhid2004-design/focusbloom/blob/main/AI-USE.md)
and [curated prompts](https://github.com/srinidhid2004-design/focusbloom/tree/main/prompts)
distinguish mocks, live calls, and limitations. The human made the product
selection, pivot, targeted-deletion, and publication decisions.

## Safety and limitations

FocusBloom remains a local fictional coursework prototype—not therapy,
diagnosis, medical advice, crisis detection, monitoring, clinical validation, or
proof of attention or effectiveness. Support is a static United States demo.
There is no authentication, deployment, analytics, voice, audio, reminders,
real-user study, or collection of real identity. Provider availability and
generated output remain bounded external dependencies.

## Submission status

The Assignment 3.2 implementation and required verification are complete. This
report is ready for manual Canvas upload. No Canvas submission or recording/video
link is claimed.
