# FocusBloom product pivot

## Decision and historical boundary

FocusBloom is the active product name for Assignment 3.2. It is a fictional
coursework prototype combining brief visual-attention activities, a structured
one-minute perspective exercise, optional user-authored next-step plans, factual
activity history, and a bounded Gemini assistant.

The submitted Part 3.1 work remains historical BreathBloom evidence. The report,
prompt records 01–06, assessed commits, original Figma comparison frames, and the
implemented version-1 breathing backend are not rewritten to imply FocusBloom
existed earlier.

> After Part 3.1 submission and a classroom comparison in which multiple projects centered paced breathing, the project was deliberately revised to explore a more distinctive attention-and-perspective interaction. This classroom observation is user-reported design input, not research evidence or proof of effectiveness.

The retained local repository folder name `breathbloom-skills` preserves tool and
project continuity; it is not the active product or public-repository name.

## Product boundary

FocusBloom is not therapy, diagnosis, crisis detection, a monitored service, a
validated attention-restoration intervention, a measure of anxiety, distress, or
improvement, or a substitute for professional or emergency support. It is tested
only with fictional scenarios. It does not infer emotion or crisis state from
text, clicks, timing, completion, or stored history.

The active experience has four related areas:

1. **Focus Garden:** optional, short visual-search and attention activities.
2. **Perspective Studio:** the formal one-minute cognitive-reframe skill.
3. **History Garden:** factual records with no scores, ranks, or interpretations.
4. **Garden Guide:** two bounded Gemini purposes: perspective alternatives and
   factual questions about saved FocusBloom history.

Static Support information remains continuously available and independent of the
backend, database, Gemini, classification, or user activity.

## Low-input interaction contract

- Present one primary action per screen and one instruction at a time.
- Use progressive disclosure; label every optional action as optional.
- Keep Skip, Stop, Back, and Support visible without penalty or failure language.
- Never force completion or require a response before a timer expires.
- Require no typing for Focus Garden and no personal input for the Perspective
  Studio fictional-example path.
- Keep current instructions visible; do not require memory of an earlier screen.
- Use short literal wording and ordinary semantic controls, not gesture-only or
  metaphor-only navigation.
- Do not ask for a questionnaire, mood score, or emotional label.
- Make difficulty changes explicit, reversible, and unscored.
- Make Standard and No-motion presentations equally understandable through text.
- Avoid flashing, surprise movement, competitive scoring, penalties, streaks,
  missed-day warnings, or stopped-as-failure language.
- Explain saved preferences before remembering them; keep them editable and
  resettable.

## Focus Garden

The initial activity catalog is application-owned and may include: identify a
differently shaped leaf; follow a ripple across several lily pads; match two
flower patterns; identify what changed among opened flowers; reconstruct a short
petal sequence; find an object from a small clue set; and connect two garden
locations with a visible path.

Each activity has a text-equivalent instruction, `Show me`, `Skip this`, `Stop`,
and Support. The application—not Gemini—owns task state, difficulty, answer
evaluation, completion, stopping, and persistence. These are attention and
visual-search activities, not breathing exercises, sensory grounding, treatment,
or clinically established calming interventions.

## Formal course skill: Perspective Studio

The required sequence is application-owned:

1. Identify an interpretation or thought.
2. Consider evidence that appears to support it.
3. Consider uncertainty or evidence that does not establish it.
4. Consider an alternative interpretation.
5. Accept, edit, reject, or create an alternative.

`Try a fictional example` is the lowest-input path. A custom path has at most one
short initial text field, followed primarily by selectable cards and optional
edits. The user sees exactly what would be sent to Gemini and may continue
without Gemini. Provider failure cannot erase entered work. Nothing is saved
unless the user explicitly selects Save; saved content can be previewed, deleted,
or reset.

**Perspective Lens** optionally reframes the same material through a fictional
observer, for example a fictional classmate named Alex. A real name is never
required. It is a perspective prompt, not an assessment.

## Next-Step Seed

This entirely optional, user-authored plan has the form: `If [situation], then I
will [small user-chosen action].` Neutral templates may reduce typing. Gemini may
format the user's own choice concisely but cannot select an action. The interface
previews exactly what will be saved. Part 3.2 does not schedule notifications or
reminders.

## History Garden

Readable cards and simple filters show factual activity type, UTC date/time,
completed/stopped/skipped status, duration, difficulty, motion and guidance
preferences, Perspective Studio progress, alternative/seed save state, and model
success/failure/skipped state. It never displays mental-health, distress,
improvement, treatment-effectiveness, adherence, rank, or streak measures.

Saved text may be deleted separately from non-sensitive activity metadata after
the interface explains what remains. Complete demo reset requires confirmation
and is transactional.

## Garden Guide

Suggested factual questions appear before the optional natural-language field.
Questions are limited to saved FocusBloom records and carry a visible reminder
not to enter private, identifying, medical, or crisis information. The assistant
is labeled as a bounded coursework feature. Out-of-scope questions receive a
fixed response. This is not crisis detection. Gemini never controls navigation,
activity state, saved status, or Support.

## Research findings and limits

- The review of visual search describes selective attention as influenced by
  bottom-up salience, top-down features, scene structure and meaning, search
  history, and value. It does not establish clinical effectiveness for this
  interface. [Wolfe, 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC9879335/)
- One laboratory study reported improved executive attention after viewing nature
  rather than urban images in its samples, while a later preregistered study of
  nature videos found no evidence for the expected effect and Bayesian support
  for the null. Digital-nature evidence is therefore mixed, not a product claim.
  [Berman et al., 2014](https://pubmed.ncbi.nlm.nih.gov/25321942/),
  [Stevenson et al., 2023](https://pubmed.ncbi.nlm.nih.gov/37132429/)
- Reappraisal training and distancing research informs the structured sequence,
  but laboratory findings do not prove that FocusBloom helps a particular user.
  Terminology and methods vary across studies.
  [Denny & Ochsner, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4096123/),
  [Powers & LaBar, 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6326885/)
- Preliminary third-person self-talk studies motivate an optional fictional-
  observer view, not a claim of outcome or neurological effect.
  [Moser et al., 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5495792/)
- A large review found a modest average planning effect with substantial
  heterogeneity and smaller bias-adjusted estimates. If–then plans are therefore
  optional and user authored. [Keller et al., 2024](https://doi.org/10.1080/10463283.2024.2334563)
- Recent work indicates affect labeling can sometimes hinder reappraisal; it is
  not a central or required interaction.
  [Affect Labeling and Reappraisal study](https://pmc.ncbi.nlm.nih.gov/articles/PMC13269579/)

FocusBloom behavior and usability must be evaluated directly through fictional
tests; they cannot be inferred from these studies.

## Figma evolution

The editable file is renamed **FocusBloom — Assignment 3 Design Evolution**.
Historical Part 3.1 sections remain unchanged. New section
`05 / FocusBloom Part 3.2 Pivot` extends Direction A's water-garden language with
low-input FocusBloom flows. All new narrow references are 390×844 and the wide
references are 1024×768. Static Figma inspection does not verify runtime behavior.

| Reference | Node | Size |
| --- | --- | --- |
| FocusBloom entry — narrow | `24:594` | 390×844 |
| FocusBloom entry — wide | `24:738` | 1024×768 |
| Focus Garden activity — narrow | `24:624` | 390×844 |
| Focus Garden activity — No motion — narrow | `24:666` | 390×844 |
| Focus Garden activity — wide | `24:780` | 1024×768 |
| Focus Garden completed — narrow | `24:708` | 390×844 |
| Perspective Studio fictional-example entry | `25:640` | 390×844 |
| Perspective Studio evidence cards | `25:668` | 390×844 |
| Perspective Studio alternative choices | `25:698` | 390×844 |
| Perspective Lens | `25:729` | 390×844 |
| Next-Step Seed | `25:757` | 390×844 |
| History Garden | `25:790` | 390×844 |
| Garden Guide suggested questions | `26:687` | 390×844 |
| Garden Guide grounded answer | `26:718` | 390×844 |
| Independent Support | `26:745` | 390×844 |
| Perspective/History/Guide composite | `26:778` | 1024×768 |

The section node is `21:594`; the selected overview is `27:719` at 2500×1160.
Reusable new components include question chip `21:598`, option card `21:601`, and
focus tile `21:604`.

## Implementation consequence

The Vue/Vite and FastAPI project foundations, backend-only lazy configuration,
sanitized errors, SQLite repository patterns, parameterized transactions,
idempotency concepts, ordered messages, dependency pins, and credential-free
test harness remain reusable.

The breathing-specific version-1 schema, five-table assumptions, session timing
rules, route surface, request kinds, model prompt/response contract, fixture
labels, and tests remain historical only. Prompt 08 deliberately replaced them
in active source with the version-2 FocusBloom backend. That checkpoint did not
create a runtime database, make a live provider call, change Figma, or implement
the new Vue interface.
