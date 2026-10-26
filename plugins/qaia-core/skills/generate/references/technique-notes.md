# Technique palette — the notes behind the table

The palette in `SKILL.md` says *when* each technique fits. This file says how to apply the four
that are routinely applied wrongly, and records what was deliberately excluded.

## Classification provenance

The grouping follows the **official CTAL-TA v4.0 chapter 3 classification**, verified against the
primary syllabus PDF (`astqb.org`), not a secondary summary.

Foundation-level (CTFL) techniques are listed first because CTAL-TA v4.0's own chapter 3 **does
not re-classify them**: equivalence partitioning, boundary value analysis and error guessing are
prerequisite CTFL knowledge, not part of this syllabus's own data/behavior/rule/experience
scheme. Naming that honestly beats forcing them into a v4.0 category they do not officially
belong to.

---

## Domain Testing (§3.1.1) — not "domain analysis"

Fits when **several related variables each carry their own boundaries and need combined
coverage**. Not each variable's boundaries tested in isolation — that is plain BVA — but the
worst-case, best-case and single-variable-boundary combinations **across the set**.

Example: a shipping cost driven jointly by weight **and** distance bands, each with its own
thresholds.

Call it **"Domain Testing"**, the syllabus's own term. "Domain analysis" is a secondary-source
drift.

## State Transition Testing (§3.2.2) — build the table first

**Build the explicit state × event table before deriving anything** (model-based-testing
discipline): list every declared state against every declared event, mark each cell valid-target
or forbidden, *then* derive conditions from the completed table.

**Never pick transition pairs opportunistically straight from AC prose.** Prose only mentions the
transitions someone thought to write down — and the ones it omits are exactly the ones that end
up untested.

## Scenario-Based Testing (§3.2.3) — constrained on purpose

Fits end-to-end user goals crossing several rules. **At most one journey scenario per US**,
tagged `@smoke`, whose `Then` asserts the single journey-level outcome and never re-verifies
behaviors already covered atomically. Excluded from atomicity accounting.

Call it **"Scenario-Based Testing"**: v4.0 explicitly retired the term "use case testing"
(syllabus Appendix C).

## CRUD Testing (§3.2.1)

Fits the full entity lifecycle — create/read/update/delete plus inverses. Already derived by the
3c reflex patterns; tag `@crud` when the technique *driving* the scenario is the lifecycle pattern
itself, as distinct from a plain state transition on a single status field.

## Metamorphic Testing (§3.3.2, also CT-AI) — the alternative to inventing a number

Fits when **the exact expected output cannot be stated directly** — it depends on an external or
unsourced parameter such as an exchange rate, a ranking score or a model output — **but a
relation between two related inputs or outputs is known and checkable without knowing that
parameter**:

- double the input amount → the converted total is roughly double;
- the same input submitted twice → the same classification;
- reordering independent inputs → an unchanged aggregate.

Use this **instead of** asserting a fabricated precise value whenever the AC's real requirement is
the *relationship* rather than a specific number. An invented exact figure reads as rigorous while
being ungrounded, and it will fail against the real system for the wrong reason.

## AI/ML feature under test (CT-AI v2.0 — separate syllabus, never conflated with CTAL-TA)

Fits when the AC describes a feature **in the target application** backed by an AI/ML/GenAI model
— recommendation, classification, scoring, generation, ranking. **Never QAIA testing itself;
always the SUT's own AI feature.**

Derive as ordinary Gherkin scenarios — never a live attack, never executed against anything but
the self-hosted target:

- **adversarial-input robustness** — malformed or perturbed input degrades gracefully, with a
  documented fallback or error, not a silent wrong answer;
- **consistency / back-to-back** — the same input stays within a stated tolerance across re-runs
  or model versions;
- **the metamorphic relations** above.

Drift and monitoring needs are **flagged as an operational gap for the user**, never fabricated
as a test assertion.

---

## Deliberately not adopted

**From CTAL-TA v4.0**: Random Testing (§3.1.3), Test Charters / Session-Based Testing (§3.4.1),
Crowd Testing (§3.4.3). Confirmed to exist in the official syllabus and out of scope here — named
explicitly rather than silently omitted, so a reader can tell **"considered and excluded"** from
**"never looked at"**.

Session-based and exploratory testing are excluded for the reason given in the scope note at the
top of `SKILL.md`: QAIA stays script-derived-from-spec, and exploration remains a human
complement outside the tooling.
