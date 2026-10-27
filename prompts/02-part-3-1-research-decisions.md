# Prompt 02 — Assignment 3.1 Research and Design Decisions

- **Date:** October 27, 2026
- **Objective:** Resolve and document the major Part 3.1 design questions before
  application implementation.

## Read-only proposal checkpoint

The project was first inspected without modification. The continuity files were
read completely; `frontend/`, `backend/`, and `data/` were empty; Git was not
initialized; and no application, dependency, credential, database, provider,
Figma artifact, or report existed.

Official primary U.S. sources were reviewed for a proposed Support plan. The
proposal covered reviewed interface wording, Next-time setup choices,
interruption/visibility rules, monotonic timing and persistence, data
relationships, API contracts, bounded factual-history RAG, responsive/accessibility
decisions, and a later Figma comparison. The proposal itself changed no file.

## Human approval and refinements

The human approved the proposal with these material refinements:

- use a fixed national U.S. fictional-demo Support scope and exact verified-source
  record;
- keep static Support independent of backend, database, providers, models,
  classifiers, geolocation, and behavioral inference;
- consolidate the proposed seven record types into five: `demo_profiles`,
  `preferences`, `exercise_sessions`, `conversations`, and `messages`;
- store Next-time setup on the session rather than a reflection table;
- store bounded request lifecycle fields on the initiating user message rather
  than a request-attempt table;
- consolidate session changes into one strictly validated PATCH contract;
- omit a separate asynchronous status endpoint unless later evidence requires it;
- keep RAG neutral when a question is out of scope and retain a visible Support
  route without claiming why the question was rejected;
- separate semantic reading order from interactive keyboard focus order; and
- keep provider/model selection deferred and voice/audio prohibited.

## Authorized documentation result

Created:

- `docs/part-3-1-decisions.md`;
- `docs/support-resources.md`; and
- this curated Prompt 02 record.

Updated only the existing overview, agent rules, AI-use disclosure, design,
verification, handoff, and prompt index authorized for this checkpoint. No
application source, manifest, dependency, database, credential, environment file,
Git repository, Figma artifact, provider selection/call, report, voice feature, or
audio feature was created.

## Acceptance checks

- Confirm the final tree and exact created/modified file set.
- Confirm implementation directories remain empty and Git remains uninitialized.
- Confirm every Support source has an exact official direct URL and access date.
- Confirm approved/resolved decisions and the two remaining deferred areas agree
  across documents.
- Scan documentation for credentials, private absolute paths, unfinished markers,
  unsupported clinical/effectiveness claims, and false implementation claims.
- Keep every runtime behavior planned/unverified.

This is curated, repository-safe evidence, not raw chat text. It contains no
private absolute path, credential, environment content, or private course-page
content.
