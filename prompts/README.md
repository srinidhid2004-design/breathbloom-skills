# Curated Prompt Evidence

## Purpose

This directory keeps concise evidence of significant project instructions,
decisions, acceptance criteria, and observed results. It supports later review of
how AI-assisted work affected BreathBloom without storing full conversations.
The current project milestone is the **Assignment 3.2 backend checkpoint**.
The five-table FastAPI/SQLite backend and bounded mocked Gemini path are
implemented and tested. The selected frontend experience and any live provider
verification remain later work.

## Redaction and safety rules

- Do not include credentials, secret values, environment contents, personal
  information, research-participant information, private filesystem paths, or
  private third-party content.
- Do not paste raw chat exports. Summarize only project-relevant instructions and
  outcomes.
- Distinguish human-approved decisions, AI contributions, planned work, and
  observed results.
- Never record a planned check as passed or a mock as live evidence.
- Link only repository-safe artifacts and public-safe evidence.

## Index

| Prompt | Date | Objective | Result |
| --- | --- | --- | --- |
| [`01-project-foundation.md`](01-project-foundation.md) | 2026-10-27 | Create the two foundation documents and six empty directories while preserving the approved BreathBloom direction and prohibitions | `README.md`, `AGENTS.md`, and six empty directories created; no application or external-service work occurred |
| [`02-part-3-1-research-decisions.md`](02-part-3-1-research-decisions.md) | 2026-10-27 | Record the human-approved Assignment 3.1 research/design decisions and refinements without implementation | Exact decisions, official Support sources, five-record/API/RAG plans, accessibility rules, and the next Figma comparison were documented; no application, provider, database, Git, or Figma work occurred |
| [`03-direction-a-selection-and-figma-reference.md`](03-direction-a-selection-and-figma-reference.md) | 2026-10-27 | Record the human selection of Direction A and expand it into an editable implementation-ready static Figma reference | Direction A selection, rationale, 13 selected reference frames, preserved comparison evidence, accessibility/layout validation, targeted visual repairs, and runtime limitations were documented; no application, Git, dependency, database, credential, or provider work occurred |
| [`04-part-3-1-submission-and-publication.md`](04-part-3-1-submission-and-publication.md) | 2026-10-27 | Create, audit, commit, publish, and publicly verify the self-contained Assignment 3.1 submission | `report.md`, curated evidence, publication verification, and public Git history were created without starting Part 3.2 implementation |
| [`05-part-3-2-foundation.md`](05-part-3-2-foundation.md) | 2026-10-27 | Verify the published handoff, finalize Part 3.2 architecture/model decisions, create and test the minimal Vue/FastAPI foundation, and publish it on the feature branch | Exact five-table/11-route/state plan, safe Google Gemini configuration, pinned foundations, passing local checks, and updated continuity records; no database, key, live provider call, or full selected interface |
| [`06-part-3-2-backend.md`](06-part-3-2-backend.md) | 2026-10-27 | Implement, verify, audit, and publish the complete five-table backend and structurally bounded optional Gemini path | Exact 11-route API, deterministic session validation, SQLite persistence/reset, mocked success/failure matrix, and structural crisis-input boundary; no live provider, real credential, runtime database, frontend, or Figma change |

## Future numbering

Use two-digit sequential names with a short purpose, such as
`05-part-3-2-foundation-plan.md`. Add one index row per curated prompt record.
Prompt records are curated evidence, not full chat exports.
