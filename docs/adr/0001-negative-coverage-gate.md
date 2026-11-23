# ADR 0001 — Replace the negative-ratio gate with a refusal-path coverage gate

- Status: **Accepted**
- Date: 2026-07-23
- Closes: #4 · Supersedes the hard part of decision D20
- *Since 2026-10-26 the two skills named below are steps of `qaia-core:generate` (`testbook-generate`
  → step 7, `references/07-emitting-the-test-book.md`; `istqb-design` → step 4,
  `references/04-choosing-techniques.md`). The decision is unchanged; since 2026-11-23 it is also
  checked per test level by `eval/tools/check_level_discharge.py` (#107).*

## Context

D20 required "≥ 40 % of scenarios are negative/boundary, verified". Across every gold-set run (US-001/002/003, versions 0.1.0-0.1.3) the measured ratio sat right on the floor: 40.6-41.7 %, dropping to 38.5 % when a human or the consolidation pass merged two scenarios. Three problems observed repeatedly by the evaluation harness:

1. **It is the wrong instrument.** A raw count ratio measures *proportion*, not *protection*. A test book can hit 40 % while leaving one rule's error path uncovered, and can fall below 40 % while covering every error path (because it also has many legitimate positive scenarios).
2. **It is mechanically fragile.** The denominator depends on scenario-splitting decisions (Outline vs unit, journey excluded or not). The same coverage yields different ratios — non-reproducible, and sensitive to review-time merges.
3. **It creates the wrong pressure.** Near the floor, reaching 40 % tempts fabrication of negatives not grounded in the source — which the skills explicitly forbid. A gate that fights its own anti-fabrication rule is mis-designed.

## Decision

**The gate becomes coverage-based, not ratio-based.**

- **New gate (blocking):** every rule that can *refuse, error, or deny* must have at least one scenario exercising that refusal/error/denial path. Concretely, for each acceptance criterion the design step (`istqb-design`) already enumerates conditions; each condition whose expected outcome is a refusal/error/denied-access is a **required negative condition**, and the book fails the gate if any required negative condition is uncovered (unless explicitly waived with user approval).
- **The 40 % ratio becomes a reported signal, not a gate.** It still appears in the synthesis and the rubric as a *happy-path-bias indicator* — a low value prompts review — but it never blocks generation and is never a target to pad toward.

## Consequences

- **Meaningful and reproducible:** the gate now tracks what negative testing is *for* (every failure mode has a check), and does not move when scenarios are split or merged.
- **Anti-fabrication preserved:** no incentive to invent ungrounded negatives; coverage is satisfied by the negatives the source actually implies.
- **Rubric change:** dimension 3 ("Negative/boundary ratio") is reframed to **"Negative-path coverage"** — 2 = every required negative condition covered; 1 = one uncovered; 0 = several uncovered. The ratio is reported alongside as context.
- **Skill change:** `testbook-generate` self-check replaces "ratio ≥ 40 %" with "every required negative condition covered or waived"; `istqb-design` marks required-negative conditions explicitly.
- **Backward note:** existing baselines (0.1.0-0.1.3) were scored under the ratio rubric; the 0.1.4+ baseline is scored under this one, noted in the baseline file so the transition is auditable.

## Alternatives considered

- *Lower the ratio to 30 %* — still the wrong instrument, just a lower floor.
- *Raise it to 50 %* — worse fabrication pressure.
- *Keep ratio as gate but exclude boundaries* — does not fix reproducibility or the coverage-blindness.
