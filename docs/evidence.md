# Assignment 3.1 Curated Evidence Log

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

The assessed milestone and final documentation commit identifiers, remote SHA
comparison, public document checks, and Figma public-access result are finalized
in `docs/verification.md` after publication. No application, database, provider,
credential, or runtime operation is part of this evidence.
