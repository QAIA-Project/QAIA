---
name: ISTQB Technique Selection, Justified
description: Pick the test design technique each acceptance criterion actually calls for and write the one-sentence reason next to it, then derive the concrete conditions to cover - including the refusal paths that a percentage-based negative target lets you skip.
version: 1.0.0
author: opaland
license: MIT
tags: [istqb, test-design, boundary-value-analysis, decision-table, state-transition, ctal-ta]
testingTypes: [strategy, acceptance, regression]
frameworks: []
languages: [typescript, javascript, python, java]
domains: [web, api]
agents: [claude-code, cursor, github-copilot, windsurf, codex]
---

# ISTQB Technique Selection, Justified

> **Standalone adaptation.** This is a self-contained version of the `istqb-design` skill from
> [QAIA](https://github.com/QAIA-Project/QAIA) (MIT), packaged as a single file for directories
> that expect one. The canonical version, its `references/`, and the measured failures behind
> several rules below live in that repository. QAIA is pre-alpha and says so.

## When to use this

After the ambiguities in a story have been surfaced, before writing any scenario. Also whenever
someone asks *which* technique applies to a requirement, or asks you to justify a test design to a
reviewer.

## The rule that makes this useful

**Every technique choice carries its reason, in one sentence, tied to the shape of the criterion.**

> "AC2 sets a time threshold at 2 hours → boundary value analysis on that limit, inclusive per the
> answer recorded during the ambiguity pass."

A technique named without a reason is decoration. It cannot be reviewed, cannot be challenged, and
gives no signal about whether the *right* one was picked.

## Scope, and two deliberate exclusions

**Black-box only.** Techniques are chosen from the specification, never from the target
application's implementation — which this skill never reads. Structure-based coverage (statement,
branch, decision, MC-DC) is therefore excluded by construction, not by oversight.

**Exploratory and session-based testing is the symmetric exclusion.** It is a human practice this
does not attempt to automate.

Say both plainly when someone asks for them, rather than treating them as gaps to fill.

## The palette, by CTAL-TA v4.0 chapter 3 classification

### Foundation (CTFL) — prerequisite, outside chapter 3's own taxonomy

| Technique | Fits when the criterion involves |
|---|---|
| Equivalence partitioning | input or state classes treated identically |
| Boundary value analysis | thresholds, limits, sizes, dates — test the **exact wording**, inclusive vs exclusive, using the answer recorded in the ambiguity pass |

### Data-based (§3.1)

| Technique | Fits when the criterion involves |
|---|---|
| Domain testing (§3.1.1) | several **related** variables each carrying boundaries, needing *combined* coverage — not plain BVA per variable |
| Combinatorial testing, incl. pairwise (§3.1.2) | many independent parameters where full combination explodes |

### Behaviour-based (§3.2)

| Technique | Fits when the criterion involves |
|---|---|
| State transition testing (§3.2.2) | lifecycle rules — statuses, allowed and forbidden transitions, events. **Build the state × event table first** |
| Scenario-based testing (§3.2.3) | an end-to-end goal crossing several rules — **at most one per story**, tagged as smoke |
| CRUD testing (§3.2.1) | a full entity lifecycle, create/read/update/delete and their inverses |

### Rule-based (§3.3)

| Technique | Fits when the criterion involves |
|---|---|
| Decision table testing (§3.3.1) | combinations of conditions producing actions — roles × flags × states |
| Metamorphic testing (§3.3.2) | an exact expected output that **cannot be stated** because it depends on an unsourced parameter, but where a **relation** between two inputs and their outputs can be |

### Experience-based (§3.4)

| Technique | Fits when the criterion involves |
|---|---|
| Error guessing / checklist | error handling, empty states, concurrency — anchored on the ambiguity log, not on inspiration |

### CT-AI (separate syllabus, never conflated with CTAL-TA)

| Technique | Fits when the criterion involves |
|---|---|
| AI/ML feature under test (CT-AI v2.0) | a feature **in the target application** backed by a model — adversarial input, back-to-back consistency, metamorphic relations |

## Steps

1. **Map criterion → technique(s)**, one justification sentence each, tied to the criterion's
   shape.
2. **Derive the conditions**, not the scenarios: partitions with representative values, boundaries
   at value and value ± 1, decision-table columns, transition pairs (valid **and** at least one
   invalid). This list is the contract handed to whatever writes the scenarios.
3. **Mark the required negatives.** For every rule that can refuse, error or deny, mark the
   corresponding condition as required-negative.

   **This is a checklist, not a percentage** — and the distinction is the point. A raw ratio
   measures *proportion*, not *protection*: a suite can hit 40 % negatives while leaving one
   rule's error path uncovered, and near the floor a ratio target tempts fabricating negatives
   that are not grounded in the source. Every refusal, error and denial path must end up with a
   scenario; the ratio is a bias signal to report, never a threshold to pad toward.

4. **Standardised domains → grounded oracles.** If a criterion touches a standardised domain —
   Luhn, ISO 8601, HTTP status, RFC 5322, ISO 4217, IBAN — derive the edge cases and their
   *correct* expected results from the standard rather than guessing, and cite it. This
   strengthens negative coverage without fabrication.

5. **Systematic coverage expansion — the recall step, and the one most often skipped.** Beyond the
   literal criteria, run these reflex patterns:

   list views · full CRUD lifecycle · sibling collections · conditional behaviour · authorization
   and server-side enforcement · protocol surface · rendering surface · account recovery ·
   enumerating *every* list rather than the first · **interaction surface**

   The last one is the one teams discover late, because the criteria describe a *transaction*
   while the user performs a *session*: the same submit dispatched twice before the first
   answers; browser back after a state change; two authorised actors deciding the same record —
   not protocol idempotence, both calls are valid and only their interleaving is the defect;
   text carrying Unicode, right-to-left script or markup, whose expected result is almost always
   *stored and rendered as data, never interpreted*; and a dependency deleted while someone is
   still holding it.

   **The ceiling that comes with it: never invent a requirement to improve recall.** A pattern
   that does not apply costs one line to record as not applicable. Recall bought with fabrication
   is worse than the gap it fills.

## Guardrails

- **A pattern with no mention at all is a defect, not a non-event.** A reviewer cannot tell
  silence from forgetting after the fact — and the pattern a story triggers most directly is the
  easiest to skip, precisely because it feels obvious.
- **Prose in a `description` or a `summary` is a hint for a human reader, never an assertion.** A
  specification that is *silent* on a rule is the easy case: the gap is visibly a gap. The hard
  case is a specification that is **chatty in the wrong field** — the rule is written down, in
  English, somewhere no machine reads it. A condition derived from it looks contract-grounded and
  is not.

  Measured on a public API specification (12 paths, 19 operations): applying this rule surfaced
  that the `Authorization` header's *value format* existed only in a `description`, which blocks
  **22 high-priority conditions** from being executable at all — and reordered the entire priority
  list. Without the rule, the design asserts a header shape and an error status that were never
  promised, and both read as derivations.

  The same applies to `default:` — it documents what a client library sends, not what the server
  does when the field is absent.
- **Derivation attention follows shape, not substance.** Measured on a real composite rule: a
  paragraph containing seven sub-facts yielded only the **two shaped like boundaries** on an
  unguided pass. The five flat ones were dropped — not because they mattered less, but because
  they did not *look* like test cases. Decompose composite rules into sub-clauses **before**
  deriving, and emit one condition per sub-clause.
- **Test the wording, not your reading of it.** "Above €500" and "€500–€5000" are two different
  phrasings whose complementarity is an assumption. If the ambiguity pass left it open, the
  condition inherits that flag rather than resolving it.
