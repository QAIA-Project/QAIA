---
name: istqb-design
description: Choose and justify ISTQB test design techniques (Foundation + CTAL-TA v4.0 + CT-AI) per acceptance criterion of an understood user story - equivalence partitioning, boundary values, decision tables, state transitions, scenario-based testing, combinatorial testing, domain testing, metamorphic testing, CRUD, AI/ML-feature testing. Use when deciding which test technique fits a requirement, when asked to justify test coverage methodologically, or when a test set looks like it was written by intuition and needs a defensible technique behind each case. Fourth step of the QAIA journey.
---

# istqb-design — technique selection, justified

Follow the shared contract in `../README.md`. Prerequisite: `02-understanding.md` (else offer
`need-understanding`).

Every rule below states its own reason; you never need project history to apply this skill. To
find out *which* decision or measured failure introduced a given rule — to challenge it, or to
change it — see `references/decision-trail.md`.

**Scope: black-box only, by design.** No structure-based / white-box technique (statement,
branch, decision, MC-DC coverage) is in this palette or planned. QAIA proposes from the spec —
the acceptance criteria — never from the target application's implementation, which it never
reads; a structure-based technique would by construction require access to the target code, which
the architecture excludes. **Exploratory / session-based testing is the symmetric exclusion.**
Both are deliberate exclusions, not oversights — say so when a reader asks for them, rather than
treating them as gaps to fill.

## Technique palette — Foundation + Test Analyst + CT-AI

Grouped by the official **CTAL-TA v4.0 chapter 3** classification. Application notes for the four
techniques that are routinely applied wrongly, the classification's provenance, and the list of
what was considered and excluded: `references/technique-notes.md`.

### Foundation Level (CTFL) — prerequisite, outside CTAL-TA v4.0's own ch.3 taxonomy

| Technique | Fits when the AC involves |
|---|---|
| Equivalence partitioning | input/state classes treated the same way |
| Boundary value analysis | thresholds, limits, sizes, dates — test the exact wording, inclusive vs exclusive, using the answers recorded in step 02 |

### Data-Based (§3.1)

| Technique | Fits when the AC involves |
|---|---|
| Domain Testing (§3.1.1) | several **related** variables each carrying their own boundaries, needing *combined* coverage — not plain BVA per variable |
| Combinatorial Testing (§3.1.2, incl. pairwise) | many independent parameters where full combination explodes |

### Behavior-Based (§3.2)

| Technique | Fits when the AC involves |
|---|---|
| State Transition Testing (§3.2.2) | lifecycle rules — statuses, allowed/forbidden transitions, events. **Build the state × event table first** |
| Scenario-Based Testing (§3.2.3) | end-to-end user goals crossing several rules — **at most one per US**, tagged `@smoke` |
| CRUD Testing (§3.2.1) | full entity lifecycle, create/read/update/delete + inverses |

### Rule-Based (§3.3)

| Technique | Fits when the AC involves |
|---|---|
| Decision Table Testing (§3.3.1) | combinations of conditions → actions (roles × flags × states) |
| Metamorphic Testing (§3.3.2) | the exact expected output **cannot be stated** — it depends on an unsourced parameter — but a **relation** between two inputs/outputs is known and checkable. Use it **instead of** asserting a fabricated precise value |

### Experience-Based (§3.4)

| Technique | Fits when the AC involves |
|---|---|
| Error guessing / checklist | error handling, empty states, concurrency — anchored on the ambiguity log |

### CT-AI (separate syllabus — never conflated with CTAL-TA)

| Technique | Fits when the AC involves |
|---|---|
| AI/ML feature under test (CT-AI v2.0) | a feature **in the target application** backed by an AI/ML/GenAI model. Never QAIA testing itself |

## Steps

1. **Map AC → techniques.** For each AC from `01-extraction.md`, select the applicable
   technique(s) and write a one-sentence justification tied to the AC's shape — "AC2 sets a time
   threshold → boundary value analysis on the 2h limit, inclusive per the answer recorded in
   step 02".
2. **Derive the test conditions.** Per AC × technique, list the concrete conditions to cover:
   partitions with representative values, boundaries (value, value±1), decision-table columns,
   transition pairs (valid **and** at least one invalid). This list is the input contract of
   `testbook-generate` — conditions, not scenarios yet.
3. **Negative pressure — the refusal-path coverage gate.** For every rule that can refuse, error
   or deny, mark the corresponding condition as a **required-negative** (`[req-neg]` in
   `03-design.md`). These are what the coverage gate enforces downstream: **not a percentage, a
   checklist** — every refusal, error and denial path must end up with a scenario. Rationale:
   `https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0001-negative-coverage-gate.md`.

3b. **Standardized domains → oracle (optional).** If an AC touches a standardized domain
   (card/Luhn, dates/ISO 8601, HTTP status, email/RFC 5322, currency/ISO 4217, IBAN…), invoke
   `oracle-generate` to add grounded edge-case conditions with their correct expected results
   rather than guessing them. Oracle conditions are tagged `@oracle:<standard>` and cited — they
   strengthen negative-path coverage without fabrication.

3c. **Systematic coverage expansion (recall — do not skip).** Ten reflex patterns a mature
   tester applies beyond the literal ACs: list views, full CRUD lifecycle, sibling collections,
   conditional behavior, authorization and server-side enforcement, protocol surface, rendering
   surface, account recovery, enumerating *every* list rather than the first, and the
   **interaction surface** — double-submit, mid-flow navigation, two actors on one record,
   unexpected text content, a dependency removed mid-session. The tenth pattern exists because a
   competitor's design agent, run on the same story and judged blind, produced three classes none
   of the other nine named — the measurement is cited in the reference.
   Full patterns, their measured failures, and the **ceiling that forbids hallucinating to chase
   recall**: `references/coverage-expansion.md`.

3d. **Knowledge-driven conditions — the RAG in use.** This is what breaks 3c's honest-recall
   ceiling. Route through `knowledge/index.md`, **decompose composite rules into their sub-clauses
   before deriving**, and emit one cited condition per sub-clause. Protocol and the measured
   failure it closes: `references/knowledge-conditions.md`.

4. ⚠ VALIDATION: present the AC → technique map with its justifications; the user amends or
   approves.
5. **Checkpoint.** Write `03-design.md`: the approved map plus the derived conditions, each
   numbered (`AC2-C3`), with the applied `BR-KB-nnn` rule IDs listed. **Each of sub-steps 3b, 3c
   and 3d must appear in the checkpoint with its outcome** — applied, with what it derived, or
   explicitly waived ("pattern X of 3c not triggered by this US: reason"). Never silently absent.
   Update `journey.md`. Next step: `prioritize`.

## Guardrails

- **Every technique choice cites its justification.** An unjustified technique is a rubric defect
  (dim. 4).
- **Prose in a `description` or a `summary` is a hint for a human reader, never an assertion.** A
  specification that is *silent* on a rule is easy to handle — the gap becomes `# open: Qn`. The
  hard case is a specification that is **chatty in the wrong field**: the rule is written down, in
  English, somewhere no machine reads it. Deriving a condition from it produces a test that looks
  contract-grounded and is not.

  Measured on the RealWorld API (12 paths, 19 operations): applying this rule surfaced that the
  `Authorization` header's *value format* exists only in a `description`, which blocks **22 P1
  conditions** from being executable at all — a finding that reordered the whole priority list.
  Without the rule, the design asserts `Token <jwt>` and asserts `PUT /user {}` → 422, and both are
  fabrications dressed as derivations.

  The same applies to `default:` — it documents what a client library sends, not what the server
  does when the field is absent.
- **A sub-step of 3c with no mention at all in `03-design.md` is a defect, not a non-event.** A
  sub-step that genuinely does not apply costs one line to record as such; silence is
  indistinguishable from having forgotten it, and a reviewer cannot tell the two apart after the
  fact. The pattern a US triggers most directly is the easiest one to skip, precisely because it
  feels obvious — recording the others as not-applicable while leaving no trace of that one
  produces a design that looks more complete than it is.
- **Conditions built on `[open]` ambiguities inherit an `[open]` flag** — they surface in the
  confidence report rather than silently asserting behavior.
