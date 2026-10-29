# Prompt 10 — Integrated and live FocusBloom verification

## Human-authorized objective

Verify the complete Assignment 3.2 FocusBloom stack without changing Figma,
dependencies, schema, API contracts, provider/model selection, retry behavior,
or safety boundaries. The approved live budget was one fictional Perspective
submission with at most one Gemini request and, only after that succeeded, one
suggested Garden Guide question with at most two Gemini requests.

The operator required zero retries and no provider/model fallback. A failed live
submission had to be recorded safely and end the live portion.

## Starting gate and regression result

- Feature branch and both feature refs matched
  `b6208388c7e79a71ed8a450c83af1c44697f2936`; local and remote `main`
  matched `9f7a09d5ceb4fc50520e26ad6140103de3cc903e`.
- The worktree/index were clean. The backend-local environment file was ignored
  and untracked; configuration presence was checked without displaying or printing
  a value.
- The model remained `gemini-3.5-flash-lite`; the configured gateway retained
  one attempt and no model/provider fallback.
- Backend: 52 tests passed with two known non-failing dependency warnings.
- Dependency integrity, 17 frontend tests, zero-warning lint, production build,
  and diff whitespace checks passed.
- OpenAPI exposed exactly 22 operations. SQLite initialized schema version 2
  with exactly the nine approved tables and zero foreign-key violations.
- Source/test inspection found no breathing runtime contract and confirmed that
  browser requests cannot supply a key, provider/model override, prompt
  override, database path, or raw SQL.

No correction cycle was used.

## Live result and request budget

The running application reported healthy backend/database state and only the
safe configuration label `configured`.

The supplied fictional Perspective example was submitted exactly once. The
loading state appeared. The fixed model made exactly one provider attempt and
returned the application's bounded Provider Unavailable result:

- purpose: `perspective_alternatives`;
- lifecycle status: `failed`;
- safe code: `provider_failure`;
- provider attempts: 1;
- persisted Perspective artifacts: 0; and
- persisted Next-Step Seeds: 0.

The request was not retried. The Garden Guide user submission was not made, so
its provider-request count was 0 and total live provider attempts were 1. No
proposed query, trusted parameters, retrieved records, row references, or
grounded answer exist for this run. These are incomplete verification items,
not empty successful results.

## Deterministic integrated observations

- At 390×844, the no-typing entry was understandable, one Focus Garden activity
  completed, and History displayed its factual completed record.
- Provider failure preserved the fictional Perspective work, did not save an
  alternative, did not control navigation, and offered only an explicit retry.
- Continue without Gemini displayed exactly two reviewed fictional alternatives;
  neither was selected or saved during the failed live checkpoint.
- Support opened from the provider-unavailable state without a model request;
  Escape closed it and restored focus to the Support trigger.
- No-motion retained literal instruction, choices, Stop, Show me, and Skip while
  stating that scaling, ripples, fades, and translation were disabled.
- An incorrect choice produced neutral retry text. Stop and Skip created factual
  terminal states without a score or penalty.
- Refreshing an active activity produced an Interrupted record and never a
  false completion or automatic resume.
- At an actual 1024×768 iframe viewport, the wide entry was readable and the
  keyboard order moved from the skip link through header controls to the primary
  action with visible focus.
- A clean direct application tab contained no browser console warning/error.
  MutationObserver messages seen only in the scaled iframe harness had no
  application URL and were isolated as harness/browser instrumentation noise.
- The stylesheet's `prefers-reduced-motion: reduce` rule disables animation and
  transition globally. This was source-level evidence; changing the operating-
  system preference was not part of the checkpoint.

## Read-only database evidence

Before the flow, table row counts in approved order were:

`demo_profiles=1`, `preferences=1`, and 0 for `activity_sessions`,
`activity_events`, `perspective_artifacts`, `next_step_seeds`, `conversations`,
`messages`, and `model_requests`.

After the flow:

`demo_profiles=1`, `preferences=1`, `activity_sessions=5`,
`activity_events=11`, `perspective_artifacts=0`, `next_step_seeds=0`,
`conversations=0`, `messages=0`, and `model_requests=1`.

The five sessions reflected exactly one completed Focus Garden, one active
unsaved Perspective session preserved after failure, one stopped activity, one
skipped activity, and one interrupted activity. The explicit display-preference
action set No motion with remember disabled. Schema version remained 2 and the
foreign-key check returned zero violations. History RAG mutation behavior was
not live-tested because Garden Guide was not submitted.

## Privacy, publication, and limitations

Screenshots retained only public-safe interface state. They contain no key,
environment content, authorization header, private path, real personal data, or
raw provider response. The local environment file and runtime database remained
ignored and untracked. No Figma, dependency, schema, API, credential, provider,
voice/audio, remote `main`, or tracked source state changed.

Because the successful live Perspective, saved artifact/Seed, Garden Guide,
grounding, and deletion checks could not run, the prompt's all-checks-passed
commit/push condition was false. No commit or push was made.

## Prompt 10A safe provider diagnosis

The follow-up read-only inspection confirmed that the application collapses all
provider errors except timeout, 401, 403, and 429 into `provider_failure`. The
official SDK receives the credential only from backend settings, sends the fixed
`gemini-3.5-flash-lite` identifier through GenerateContent, applies a 10-second
timeout and one total attempt, and supplies a nonempty Pydantic response schema.
The installed SDK supports all three configured generation fields. The fixed
fictional content was approximately 531 UTF-8 bytes plus a 791-byte schema,
within the documented model limits.

The authorized provider diagnostic used exactly one metadata call and one tiny
structured-generation call. Metadata was visible; the generation returned a
valid tiny object. Safe result: HTTP 200 / `OK`, category `success`, inference
permitted. No model catalog, credential, header, raw provider payload, raw
exception, or response text was displayed or recorded, and no application
database write occurred.

This proves that the credential, project access, fixed model, and minimal
structured inference were operational at diagnostic time. It does not reclassify
the earlier application submission as successful. Because that earlier raw error
was intentionally sanitized and not retained, its exact cause remains unknown;
the new evidence argues against a persistent key, project, model-visibility,
quota, or request-shape problem and is consistent with a temporary provider
condition. No Perspective retry or Garden Guide submission occurred, and no
source, test, commit, or remote state changed.

## Prompt 10B bounded application continuation

All repository, ignore, credential-presence, model, retry, fallback, and Prompt
10A gates passed. Before the new flow, schema version was 2, foreign-key
violations were zero, and the nine table counts were `1,1,5,11,0,0,0,0,1` in
approved order.

At 390×844, the supplied fictional Alex example and exact bounded preview were
used. The loading state appeared, and the single authorized application
submission made exactly one provider attempt. It returned the same bounded
Provider Unavailable state with lifecycle status `failed`, safe code
`provider_failure`, attempt count 1, and the fixed model. No retry, fallback,
separate diagnostic, or Garden Guide submission occurred.

Post-failure counts were `1,1,6,13,0,0,0,0,2`. The new rows were one active
unsaved Perspective session, two Perspective step events, and one failed model-
request lifecycle row. No artifact, Seed, conversation, message, alternative,
or grounded answer was persisted. Schema version remained 2 and foreign-key
violations remained zero.

The temporary viewport harness and services were stopped. No duplicate failure
screenshot was retained. Per the failure stop condition, save/delete, Support,
Garden Guide, final automated suites, commit, and push were not attempted. No
application source, test, dependency, Figma, schema, API, provider/model, retry,
credential, or remote state changed.

## Prompt 10C exact isolation and narrow correction

All repository and privacy gates passed. One OS-temporary script outside the
repository reproduced the exact full Perspective SDK call without database
access. Its first local launch failed before SDK construction because the project
working directory was not on the import path; it made zero provider calls. After
that temporary-only import correction, exactly one diagnostic generation call
returned HTTP 400, SDK class `ClientError`, safe category
`invalid_request_schema`, and the developer-authored cause that the provider
rejected the structured response schema. The script was immediately deleted;
no raw request, response, exception, header, environment content, or key was
printed or retained.

Comparison with Google's documented structured-output subset identified the
unsupported single-value `const` emitted for Pydantic `Literal` fields. The
smallest correction converts only `const` to the equivalent supported
`enum[value]` and sends the schema through `response_json_schema`; unchanged
Pydantic models still validate the parsed output, including the exact limitation
literal and maximum two alternatives. Safe numeric provider-status mapping was
also added without retaining provider-controlled text. The fixed model, one
attempt, timeout, MIME type, context, output cap, validators, and safety boundary
remain unchanged.

Focused tests reported 17 passed. The complete backend reported 61 passed with
the same two non-failing warnings, and `pip check` was clean. The single corrected
application Perspective request then succeeded with exactly one provider call
and two bounded alternatives. Nothing was saved automatically. One reviewed
technical/connectivity alternative was explicitly saved, followed by one
explicitly previewed and saved fictional user-authored Seed. History showed a
completed Perspective session, both saved indicators, and model `succeeded`.

Garden Guide used the suggested factual question about the most frequently
completed activity. Its single request-1 provider call produced a proposal that
the unchanged SQL validator rejected before execution. Status was
`query_rejected`, attempt count 1, and request 2 did not occur. No query ran, no
rows were retrieved, no assistant message or answer was created, and no retry
was made. Hashes of the profile, preference, activity-session, activity-event,
artifact, and Seed tables were identical before and after Garden Guide.

Prompt 10C provider-generation counts were: exact diagnostic 1, application
Perspective 1, Garden Guide request 1, Garden Guide request 2 zero; total 3 of 4
allowed. Database counts moved from `1,1,6,13,0,0,0,0,2` before the checkpoint to
`1,1,7,16,1,1,1,1,4` afterward. Schema version remained 2 and foreign-key
violations remained zero.

Because Garden Guide did not complete, artifact deletion, Seed-retention-after-
deletion, post-success Support/console checks, commit, and push were not
performed. Frontend checks remained 2 files/17 tests, zero-warning lint, and a
22-module production build. Public-safe screenshots retain the successful
alternatives, explicit artifact/Seed state, and bounded Garden query rejection.

## Prompt 10D validator alignment and completed flow

The exact existing validator grammar was audited without changing
`backend/app/rag.py`, any allow-list, trusted profile scoping, binding rule,
function boundary, final 1–20 limit, or read-only execution protection. One
OS-temporary diagnostic made exactly one fixed-model proposal request for the
approved factual question. The response was schema-valid with outcome `query`,
but the unchanged validator returned safe category
`unapproved_table_or_column`. The diagnostic made no database write or second
request, exposed no raw provider content or proposed SQL, and its script was
deleted immediately.

Only the production `history_sql` instruction changed. It now accurately lists
the approved schema and grammar, says `:profile_id` is required in SQL but
backend-owned, requires bound parameters for every other value, prohibits
quoted values and unsupported structures, and includes one validator-valid JSON
example. The validator and application execution path were not changed or
hard-coded. Focused instruction/validator checks passed 33 cases; the final full
backend passed 69 with two known non-failing warnings and `pip check` was clean.

One fresh Garden Guide UI submission then used exactly two provider requests,
one attempt each and zero retries. The proposal passed the unchanged validator,
read-only bounded retrieval returned two rows, and the grounded answer cited
rows 1 and 2 while factually reporting a one-session tie between the completed
fictional activities. No diagnosis, emotion inference, advice, or effectiveness
claim appeared, and the safe trace remained collapsed.

After explicit confirmation, UI deletion removed only the saved Perspective
artifact. History showed Perspective saved `no` and Seed saved `yes`; the Seed
row remained. Support opened without a provider request, Escape restored focus
to Support, and the restarted direct Edge tab showed a blank DevTools Console
with no warning or error.

Prompt 10D generation calls were diagnostic 1, application Garden request 1,
and application Garden request 2: total 3. Database provider rows remained 6.
Final counts were `1,1,7,16,0,1,2,3,6`; schema version remained 2, all nine
tables remained, integrity was `ok`, and foreign-key violations were zero. The
latest conversation was ordered user then assistant and both Garden lifecycle
rows succeeded with one attempt and two row references.

Final frontend checks passed 17 tests across two files, zero-warning ESLint, and
a 22-module production build. New public-safe evidence retains the successful
Garden answer/collapsed trace and the artifact-deleted/Seed-retained History
state without any credential, private path, raw SQL, database path, provider
payload, exception, or personal information.
