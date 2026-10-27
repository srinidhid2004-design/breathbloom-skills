# Assignment 3.1 — Research and Design

## Project identity

**BreathBloom** is a coursework prototype for paced breathing. Its intended
sequence is a four-second inhale followed by a six-second exhale, repeated for six
cycles and approximately 60 seconds of guided active practice. Entry, setup,
voluntary pauses, and time viewing Support are separate from that planned active
duration.

BreathBloom is evaluated only with fictional scenarios. It is not therapy,
diagnosis, medical advice, crisis monitoring, or a monitored service, and it must
not be offered as a real mental-health support tool.

## Public submission references

- **Public repository:** https://github.com/srinidhid2004-design/breathbloom-skills
- **Assessed milestone commit:**
  [`aa41c3bda8680439f05fcb68bc6945dff6dbd515`](https://github.com/srinidhid2004-design/breathbloom-skills/commit/aa41c3bda8680439f05fcb68bc6945dff6dbd515)
- **Public Figma file:** https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx
- **Selected Direction A section:** https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=10-286
- **Selected overview:** https://www.figma.com/design/L09m1XZX6fNEmR2dqrBkcx?node-id=14-537

Public project records:

- [README.md](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/README.md)
- [AI-USE.md](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/AI-USE.md)
- [Approved decisions](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/docs/part-3-1-decisions.md)
- [Support resources](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/docs/support-resources.md)
- [Design pipeline](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/docs/design-pipeline.md)
- [Verification record](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/docs/verification.md)
- [Curated evidence log](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/docs/evidence.md)
- [Current handoff](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/handoffs/current.md)
- [Prompt 01 — foundation](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/prompts/01-project-foundation.md)
- [Prompt 02 — research decisions](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/prompts/02-part-3-1-research-decisions.md)
- [Prompt 03 — Direction A selection](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/prompts/03-direction-a-selection-and-figma-reference.md)
- [Prompt 04 — submission and publication](https://github.com/srinidhid2004-design/breathbloom-skills/blob/main/prompts/04-part-3-1-submission-and-publication.md)

The assessed milestone commit above identifies the substantive Part 3.1 project
state. The following documentation-only commit, titled **Finalize Assignment 3
Part 1 report**, is the submitted report version. Its exact SHA is reported with
the Canvas artifact and remains visible in the public repository history; placing
that commit's own SHA inside itself would create a self-referential commit loop.

## Research and design summary

Paced 4–6 breathing was selected because its sequence is concrete, can be timed
deterministically, and fits the assignment's attention constraint within a short
60-second practice. R1 supported staying below 90–100 seconds; D3 supported low
reading and decision effort; R4 supported explicit Start, Stop, Resume, and
preference choices; D5 supported transparent, reusable preferences; and D1 led
the project to reject emotional-state inference from clicks or completion.

Two editable Figma directions were compared. The human selected **Direction A —
Focused central water garden** because the prominent central bloom communicates
the flower, leaf, and water identity more clearly and feels calmer, more
immersive, and more distinctive. Direction B's advantage was clearer timing,
segmented progress, organization, and accessibility cues. Those clarity features
were incorporated into A without creating a third direction.

The selected experience reduces effort through a small set of entry actions,
short reviewed instructions, visible phase/cycle status, and an option to reuse
explicit settings. The person retains control through Start, Stop, Support, Full/
Gentle/No motion, guidance choices, and inspectable preferences that can be
changed, skipped, or reset. Support remains fixed static content independent of
any model, classifier, database, geolocation, behavior, or provider response.

## Proposed model role

A later model may provide only a brief optional introduction, a bounded factual
reflection, or a grounded answer about allowed fictional session history. The
deterministic application controls breathing timing, skill order, navigation,
persistence truth, Stop, and Support. A model will not invent therapeutic or
medical advice, infer distress, or control the exercise.

The exact provider/model, timeouts, retries, and call budget remain unresolved
until separately proposed and human-approved. No live model integration or
provider request exists at this milestone.

## Proposed data and personalization

The design proposes five record types: `demo_profiles`, `preferences`,
`exercise_sessions`, `conversations`, and `messages`. They would store a fixed
fictional profile scope; explicit motion/guidance settings; factual session
timestamps, duration fields, cycle count, status, settings snapshot, and optional
Next-time setup selection; conversation grouping; and actual ordered messages
with bounded request status.

Saved settings and factual history could reduce repeated setup. The person would
be able to inspect, change, reject, or reset preferences and fictional records.
BreathBloom will not collect a real identity, real location, diagnosis, mood,
distress score, biometric/audio data, or inferred emotional state. This is a
proposal only: no database or persistence has been implemented.

## Figma design evidence

The public Figma file preserves the two compared directions and the human
selection of Direction A. The selected section contains 13 editable static
references: entry/setup; standard inhale and exhale; No motion; completion and
optional Next-time setup; factual History; and independent Support, with narrow
and wide versions where layout materially differs.

Static checks confirmed the intended frame dimensions, editable layers, Inter
text, no image-fill substitutes or missing fonts, 44-pixel-minimum control
targets, text-backed status, six-segment progress, and recorded contrast ratios
from 5.90:1 to 13.21:1 for the approved tested color pairs. These checks establish
static structure and composition only. They do not establish runtime timing,
motion, keyboard/focus behavior, reflow, persistence, or link activation.

## Part 3.1 completion status

Part 3.1 completed the product concept and scope; research-grounded decisions;
Support-resource research; architecture and data/API proposals; bounded model and
RAG proposal; Figma A/B comparison; human direction selection; static selected-
direction reference; AI-use disclosure; verification notes; curated evidence;
and continuity documentation.

## Unresolved and unimplemented work

The Vue frontend, FastAPI backend, SQLite database, provider integration, runtime
timing, animation, keyboard/focus behavior, responsive browser reflow, pause and
interruption handling, persistence, API behavior, error handling, and clean-
checkout setup remain unimplemented or unverified. Part 3.2's working-application
requirements have not started.

## Recordings

No recording is relevant to this Part 3.1 milestone because no running
application exists. The public editable Figma reference and documented checks are
the design evidence for this submission.
