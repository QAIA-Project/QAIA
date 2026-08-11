---
name: testbook-generate
description: Generate the atomic Gherkin test book from prioritized test conditions - stable scenario IDs, coverage matrix, negative-ratio check, confidence marking - or regenerate by scenario-level diff when the US evolved, preserving human edits. Use when asked to write test cases or scenarios from a specification, to produce a test book or feature files, or to refresh an existing one after the requirement changed without losing hand-written edits. Sixth step of the QAIA journey.
---

# testbook-generate — the test book

Follow the shared contract in `../README.md`. Prerequisites: `03-design.md` and
`04-priorities.md` (else offer the missing step). Output directory: `.qaia/testbooks/<US-ID>/`.

## Generation rules (non negotiable)

- **Gherkin, English keywords — always, whatever the project language**: `Feature / Background /
  Scenario / Scenario Outline / Given / When / Then / And / But`. Only the **prose inside a step**
  follows the project language. A French project still writes `Scenario:`, never `Scénario:`.
  This clause is explicit because the previous wording was not: a model given this skill emitted
  `Scénario:` and `Etant donné`, producing an unparsable file, having read "project language" as
  covering the keywords too. The ambiguity was ours.
- **Atomic** — one scenario verifies exactly one behavior. No UI-step chains covering several
  cases. **Exactly one `When` (the action) per scenario; outcomes live only in `Then`** — never
  bury the action in a `Given` or the outcome in the `When`.
  `Background` is for shared *state* setup only. `Scenario Outline` + `Examples` covers
  partitions or boundaries of the *same* behavior, **merged only when all example rows share
  the same priority and confidence** — otherwise split.
- **Journey exception**: at most one end-to-end scenario per US (use-case technique), tagged
  `@smoke`, single journey-level `Then`, excluded from atomicity accounting — see
  `istqb-design`.
- **Preconditions are declarative** ("Given a patient with 3 upcoming appointments"), never a
  click-path. Data seeding belongs to the automation layer: generated tests must run standalone
  outside the session, and environment or credential details never enter the test book.
- **Test level — exactly one tag per scenario, from the closed list `@e2e` / `@api`**
  ([ADR 0008](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0008-test-level-is-a-design-property.md)). The level is **read from the condition** in `03-design.md`, where
  `istqb-design` assigned and justified it — it is never re-derived here from the wording of the
  steps. The criterion, for reference: `@api` when the promise is a clause of the service
  contract, observable in HTTP without a browser; `@e2e` when it is only observable through the
  user interface. The `@smoke` journey scenario crosses the UI by definition and carries `@e2e`.
  **Never two level tags on one scenario** — a scenario needing both verifies two promises through
  two interfaces, which is an atomicity defect to split, not a tag to add.
- **Stable IDs** — every scenario tagged `@QAIA-<US-ID>-<NNN>`, NNN never reused even after
  deletion. Plus: `@AC<n>` (traceability), `@P1/@P2/@P3` (priority), `@negative` where
  applicable, the level tag above, and **exactly one** technique tag from the closed list:
  `@ep @boundary @domain-analysis @decision-table @state-transition @pairwise @crud
  @metamorphic @ai-feature @error-guessing`.
  The single journey scenario carries `@smoke` instead of a technique tag. `@use-case` is
  retired — the technique it named no longer exists in the reference taxonomy `istqb-design`
  follows, so it must not be emitted. Add `@low-confidence` when the scenario rests on an
  `[assumption]` or `[open]` item.
- **Every scenario cites its condition** (`AC2-C3`) in a comment line — the full chain
  US → AC → condition → scenario.
- **Negative coverage**: the blocking rule is the `[req-neg]` checklist of [ADR 0001](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0001-negative-coverage-gate.md) (the
  negative-path coverage gate) — every refusal, error or denial path has a scenario. The
  **negative ratio is reported as context, never a gate.** Full doctrine, and why this is
  laboured: `references/negative-ratio.md`.
- **Generating on `[open]` items.** A covered condition flagged `[open]` still gets its
  scenario, written with the *proposed safe default* from `02-understanding.md`, tagged
  `@low-confidence`, with an inline comment citing the question ID (`# open: Q5`). Never invent
  a different behavior, never skip silently. Waiving instead of generating is allowed only with
  the user's recorded approval. **Never pad the negative ratio with invented cases** — if
  reaching a target would need error-guessing scenarios not grounded in the source or knowledge
  base, flag the shortfall instead of fabricating.

## Emission contract — the shape of the file, not its content

Everything above says **what** to produce. This section says **under what form**, because that
half used to be implicit: it lived in the repository's linter configuration, which a host that
is not Claude Code inside this repository cannot read. Measured on 2026-08-08 (issue #84): of
four models given this skill and a real input, **two produced Gherkin that was correct on the
substance and rejected by the linter** — every cause was a convention this file never stated.

1. **Emit the file, nothing else.** No surrounding ``` fence, no preamble, no closing summary.
   The output IS the `.feature` file. *(Two models out of four wrapped it in a code fence.)*

2. **Exactly one real `Feature:` line, and it is not a comment.** A `# Feature: US-004` comment
   line above it is a QAIA habit for carrying the US reference — it is **not** the declaration.
   A file whose only `Feature` is commented out does not parse at all, and every scenario under
   it is lost. *(One model copied our comment convention and omitted the declaration; a second
   did the same after a first correction round — this is the most repeated failure of the four.)*

3. **Indentation is structural, not cosmetic — copy this shape exactly.** Column counts are
   absolute, not relative to whatever nesting you have in mind. The fence below belongs to *this
   document*; do not emit it (see rule 1).

   ```
   Feature: <name>                          <- column 0
                                            <- blank line
     # AC1 — <comment, optional>            <- column 2
     @QAIA-US-004-001 @AC1 @P1 @e2e @ep     <- column 2, tags on their own line
                                            <-   level tag (@e2e|@api) and technique tag
                                            <-   are both mandatory, exactly one each
     Scenario: <name>                       <- column 2
       Given <...>                          <- column 4
       When <...>                           <- column 4
       Then <...>                           <- column 4
                                            <- blank line between scenarios
     Scenario Outline: <name>               <- column 2
       Given <...>                          <- column 4
       Examples:                            <- column 4
         | header | header |                <- column 6
         | value  | value  |                <- column 6
   ```

   *(Measured twice: one model produced structurally valid Gherkin and failed on indentation
   alone; a second, given the rule in prose, indented one level short throughout — `Scenario:` at
   0 and steps at 2. Prose describing a shape gets interpreted; a shape gets copied.)*

4. **A `Background:` carries no tags.** Tags belong to scenarios. A `Background:` sits at column
   2 like a `Scenario:`, holds only shared *state* setup, and has nothing above it but a blank
   line or a comment. *(One model tagged its `Background:` and was rejected for that alone.)*

5. **English keywords, always** — already stated above, and restated here because it is part of
   the same contract: `Feature / Background / Scenario / Scenario Outline / Given / When / Then /
   And / But`, whatever the project language. Only the prose inside a step follows the project.

6. **No trailing whitespace, one space between tags, no duplicate tag on a line.**

### Who arbitrates

This section is the rule **in prose, for a host that cannot read our configuration**. The
repository's `gherkin-lint` configuration remains the **arbiter**: if the two ever disagree, the
linter is right and this text is stale — say so rather than reconciling them by hand. The rules
are deliberately *not* copied from that file. Two sources for one rule diverge; this project
spent 2026-08-09 correcting five separate cases of exactly that, and will not create a sixth
here.

## Steps — initial generation

1. **Scope check.** Confirm target coverage with the user: P1+P2 by default, P3 on request
   (quota trade-off).
2. **Duplicate scan.** Scan the project's committed `.feature` files (`.qaia/testbooks/` and any
   test directories the user designates — nothing outside the project). List any scenario
   already covering a condition and propose reuse. ⚠ VALIDATION on the reuse list.

   **Always record the scan's outcome** in `coverage-matrix.md`'s "Reuse notes" column,
   including "no duplicates found". A clean scan that leaves no trace is indistinguishable,
   afterwards, from a scan that never ran — the negative result is as much a deliverable as the
   positive one.
3. **Generate per AC.** In Claude Code you may parallelize with one sub-agent per AC, each given
   only: the AC, its conditions, relevant knowledge entries, and these generation rules. Each
   sub-agent writes structured JSON to a temp file; only the aggregation enters the main
   context — the sub-agents exist to keep raw material out of the main context, not merely to go
   faster. Elsewhere, generate sequentially against the same output contract.
4. **Consolidation pass** (mandatory, even sequential): unify vocabulary against
   `knowledge/glossary.md` where it exists, merge redundant scenarios across ACs, factor a
   common `Background`, verify every ID unique and every condition covered or explicitly waived.

   If the knowledge base is absent, unify internally and **record "knowledge base absent" in
   this skill's own `synthesis.md`**, not only by relying on an upstream checkpoint's note. The
   redundancy is deliberate: each deliverable stands on its own, and someone reading this
   synthesis alone would otherwise never learn the vocabulary was unified against nothing.
5. **Emission lints — run before showing anything.** Eleven checks, one of them blocking. Full
   list with the reasoning: `references/emission-lints.md`. In short: the [ADR 0001](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0001-negative-coverage-gate.md) negative-path
   gate blocks emission; one `When` per scenario; no compound `Then`; every asserted literal
   computed and grounded; `Background` holds only universal invariants; no silent ID gaps; the
   reported ratio matches a literal tag count in the emitted file.

   Then **write `state/<US-ID>/generated.snapshot.md`** — scenario IDs plus a content hash per
   scenario. This is the regeneration baseline; without it, regeneration cannot tell a
   hand-written correction from its own previous output.
### The emission contract — what a `.feature` file must look like

The rules below are **not style**. A file that breaks any of them does not parse, or fails the
project's Gherkin linter, and the rest of the chain never sees it. They are stated here because a
host other than Claude Code cannot read the linter's configuration.

- **A real `Feature:` line is mandatory**, once per file, at column 0, and it is the **first
  non-comment line**. A file whose feature title appears only inside a `#` comment has no feature
  at all and does not parse.

  *This rule is stated as a requirement and nothing more, on purpose. An earlier version also
  described the decorative `# …` comment this project writes above the declaration — and a model
  that had been emitting the declaration correctly started emitting the comment **instead**.
  Describing a house convention propagates it, including the confusion it carries.*
- **Indentation is significant**: `Feature` at column 0, `Background` and `Scenario` indented by 2,
  steps and `Examples` by 4.
- **Emit the file's content and nothing else.** No preamble, no explanation, and **never wrap the
  output in a code fence** — a leading ``` makes the first line invalid.
- **One `.feature` per functional area**, named after that area.

**If this prose and the linter ever disagree, the linter wins.** It is the arbiter, and it is what
CI runs. This section exists so a host that cannot read `.gherkin-lintrc` still knows the shape —
not to become a second source of truth for it.

6. **Write outputs.** `*.feature` (one per functional area); `coverage-matrix.md` (AC →
   condition → scenario ID → priority → **rationale** → confidence, the rationale column
   carrying `prioritize`'s one-line risk drivers); `synthesis.md` per the shared contract's
   deliverable section (`../README.md`), including the full inline question list and the
   arbitration list. All artifacts carry resume frontmatter (shared-contract rule 10).
7. ⚠ VALIDATION: present the **synthesis**, not the raw dump — counts, ratio, coverage gaps, and
   the `@low-confidence` list to review first. Update `journey.md`.
8. **Project the standardized manifest.** Run `report` (or its logic) to write or refresh
   `.qaia/reports/<US-ID>/manifest.json`, the shared output contract every plugin reads. Counts
   come from this generation, never re-estimated.

## Steps — regeneration mode (a test book is never write-once)

Trigger: the US changed, or the user asks to regenerate. The existing book may contain human
edits — **they win by default.**

1. **Detect human edits first.** Compare the current book against
   `state/<US-ID>/generated.snapshot.md` by hash; scenarios differing from the snapshot are
   human-edited. Snapshot absent (pre-0.1.2 book): treat **every** scenario as potentially
   human-edited, and say so.

   Re-run ingestion→design deltas as needed, writing new questions and conditions back into the
   `00-04` checkpoints — a regeneration that leaves the checkpoints describing the old
   requirement makes every later step work from a stale picture. Then compute a scenario-level
   diff: `unchanged / modified (show old vs new) / new / obsolete`.

   **Scan the whole book**, not just the ACs that visibly changed: a threshold change can touch
   scenarios tagged on other ACs, and a scoped diff misses them.
2. ⚠ VALIDATION per conflict: for each `modified` scenario that was human-edited, and each
   `obsolete` proposal, the user arbitrates. Never delete or overwrite a human-edited scenario
   without explicit approval.
3. Retired IDs are never reused. Matrix and synthesis are regenerated, and a `CHANGELOG` section
   in `synthesis.md` records the diff decisions.

## Guardrails

- A scenario must never assert behavior the source contradicts. When the source is silent, tag
  `@low-confidence` and record the assumption — plausible-but-wrong is the worst defect
  (rubric dim. 5).
- Respect the token budget: sub-agents receive digests from checkpoints, never the raw source or
  the full knowledge base.
