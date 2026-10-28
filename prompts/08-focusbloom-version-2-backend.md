# Prompt 08 — FocusBloom version-2 backend

**Date:** 2026-10-28
**Status:** requested work and observed results are separated below

## Human-approved instruction

Replace the obsolete active breathing backend with the complete approved
FocusBloom version-2 backend on `feature/assignment-3-part-2`. Implement the
exact nine-table schema and 22-operation API, Focus Garden persistence,
Perspective explicit-save behavior, Next-Step Seeds, factual History Garden,
ordered conversations/messages, lifecycle-only model requests, one-request
Perspective alternatives, and two-request read-only history RAG.

Use temporary databases, fictional inputs, and mocked Gemini only. Do not create
the runtime database or local environment file, use a real credential, make a
live provider request, implement the Vue interface, change Figma, add voice/
audio, modify `main`, or preserve obsolete breathing compatibility behavior.

## Required boundaries

- Fixed Google model `gemini-3.5-flash-lite`, 10-second deadline, 384 output
  tokens, one attempt, zero retries, and no provider/model fallback.
- No automatic Perspective save; explicit preview/save/delete/reset boundaries.
- History SQL limited to approved version-2 data, trusted profile binding,
  read-only SQLite, 100-ms/20-row/8-column/8-KiB bounds, and grounded row refs.
- Zero provider calls for invalid input or missing configuration; one for
  rejected/no-match/request-one failures; two only when answer generation begins.
- Sanitized responses with no submitted-value echo, raw SQL/rows/errors, secrets,
  prompts, system instructions, or database paths.
- Preserve historical Part 3.1/pivot evidence and publish only the feature branch
  using commit subject `Implement FocusBloom activity and model backend`.

## Observed implementation result

- Active source contains the exact nine tables at SQLite `user_version=2` and
  the exact 22 documented API operations. Version-1 files stop initialization;
  there is no automatic migration or breathing compatibility route.
- Activity sessions/events, transparent preferences, Perspective artifacts,
  Next-Step Seeds, conversations/messages, saved-text deletion, and complete
  reset use parameterized transactions and stable identifiers.
- Perspective and history adapters enforce the approved output shapes and
  request-count boundaries. Perspective output remains ephemeral until a
  separate explicit save call.
- The history validator deliberately follows the authoritative implementation
  contract and rejects CTEs. Retrieval adds defense in depth with a read-only
  URI, query-only/trusted-schema settings, disabled extensions, a default-deny
  authorizer, execution deadline, snapshot check, and payload limits.
- One review-driven correction cycle tightened differing-content idempotency and
  WHERE predicates. The final backend suite reported 52 passed; dependency
  integrity was clean. These are mocked/local results, not live-provider or
  frontend evidence.
