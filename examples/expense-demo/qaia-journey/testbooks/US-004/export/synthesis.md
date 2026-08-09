---
stepsCompleted: [00-ingest, 01-review, 02-understanding, 03-design, 04-priorities, 05-testbook-generate]
lastStep: 05-testbook-generate
lastSaved: 2026-07-25
---

# Synthesis — US-004 (Expense report approval workflow)

- **US-ID**: US-004. **Date**: 2026-07-25. **Domain**: finance/HR (non-medical — companion
  cross-domain proof to `examples/medibook`, US-001, medical).
- **Scenarios**: 38 total (1 `@smoke` journey + 37 condition scenarios) across 4 feature files.
- **Priority split**: 19 `@P1` (incl. the smoke journey) / 15 `@P2` / 4 `@P3`.
- **Negative-path coverage (ADR 0001)**: 17/17 required-negative conditions from `03-design.md`
  have a covering `@negative` scenario — **gate satisfied**. Raw negative ratio (bias signal,
  never a threshold): 17/37 = **45.9 %**.
- **Open ambiguities**: 9 questions logged in `02-understanding.md` (5 `[open]`, 4
  `[assumption]`); all 9 have at least one scenario tagged `@low-confidence` citing the
  question ID. 0 questions left unresolved without a default (every one got a proposed default,
  per the "generate on `[open]` items" rule — never skip silently).

## Full question list (inline, per shared-contract deliverable rule)

1. **Q1** [open] — AC2/AC6 threshold boundary at exactly €500 and €5000 → default: band B
   inclusive both ends. Scenarios: 009, 010.
2. **Q2** [open] — AC3 "skip straight to the next level up": narrow the amount-chain or
   escalate to the next hierarchy role? → default: escalate/replace, drop if already required.
   Scenarios: 007 (interaction with Q3), 014, 015, 027.
3. **Q3** [assumption] — can a `changes-requested`-turned-`draft` report be rejected directly?
   → default: no, only `submitted` accepts a decision. Scenario: 007.
4. **Q4** [open: source / assumption: fallback] — AC6 rate source and missing-rate fallback →
   default: synthetic fixed table; last available prior rate + `rateStale` flag. Scenarios:
   025, 026, 027.
5. **Q5** [assumption] — AC4's 90-day window measured against which clock? → default:
   server/UTC clock. Scenario: 018.
6. **Q6** [open] — AC5's €25 threshold: face value or EUR-equivalent? → default:
   EUR-converted amount. Scenario: 023.
7. **Q7** [open] — triple intersection AC2×AC3×AC6: does a stale-rate total still drive both
   band and escalation? → default: yes, proceed and flag `rateStale`. Scenario: 027.
8. **Q8** [assumption] — does AC3's self-approval-skip rule generalize beyond the named
   manager case (finance, director submitters)? → default: yes, generalizes. Scenario: 016.
9. **Q9** [assumption] — does draft-creation count as a recorded AC8 transition? → default:
   yes, recorded (purely additive, no `@low-confidence` scenario needed — doesn't change
   accept/refuse behavior, verified in the audit-trail scenario 034's `create_draft` event).
10. **Q10** [assumption] — **no acceptance criterion states an HTTP status code for any
    refusal.** AC4, AC5, AC7 and AC8 promise that an action is *refused*; none says with
    which code. → default: assert the refusal, not the code. The status our SUT answers is
    recorded in each scenario's condition comment as an observation, never as an
    expectation — an implementation refusing with a different 4xx conforms to the same
    criteria. No `@low-confidence` scenario is needed (same reasoning as Q9: this does not
    change accept/refuse behaviour). Found on 2026-08-08 when a competitor's agent was run
    on the same story and two blind judges flagged the codes as invented expectations —
    the defect had survived because this project also wrote the application under test.

## Ratio explainer

The 45.9 % ratio sits comfortably above the 40 % signal threshold — this US is unusually
negative-heavy for a first read because 5 of its 8 AC are explicit refusal rules (AC1's
forbidden transitions, AC4's 90-day block, AC5's receipt block, AC7's terminal block, AC8's
comment-length block) and the decision-table/boundary-heavy AC2/AC3/AC6 cluster generates
several negative boundary cells on top of that. No AC in this book is a pure calculation with
no refusal path (unlike some medical scheduling ACs) — the ratio is high because the domain
genuinely is, not because of padding (no error-guessing scenario was added purely to inflate
the count; every `@negative` scenario traces to a `[req-neg]` condition in `03-design.md`).

## Out-of-slice dependencies

None. `00-source.md` recorded no sibling-story references and the INVEST "Independent" claim
held for the ingested slice.

## Review order

`@low-confidence` first (scenarios 007, 009, 010, 014, 015, 016, 018, 023, 025, 026, 027 — 11
scenarios; note 027 is `@low-confidence` for Q7 but structurally also depends on Q2/Q4, so it
is the single highest-review-priority scenario in the book), then P1 → P2 → P3.

## By-technique table

Verified by count against the `.feature` files (`grep -c @<tag>`); the six tags partition the
38 scenarios exactly (6+12+6+7+6+1 = 38 — every scenario carries exactly one technique tag,
confirmed by the structural scorer's `technique_tag_violations: []`).

| Technique | AC(s) | Scenario count | Justification |
|---|---|---|---|
| Use case | AC1, AC2, AC8 | 1 | Single end-to-end journey, `@smoke`, journey-level `Then`. |
| Equivalence partitioning | AC1, AC4, AC5, AC6, AC8, list | 6 | Input/state classes treated uniformly (complete draft, EUR class, comment-present class, empty-list class). |
| Boundary value analysis | AC2, AC4, AC5, AC8 | 12 | Explicit thresholds: €500/€5000, 90 days, €25, 10-char comment. |
| Decision table | AC2, AC3, AC6 | 6 | Role × chain-position × amount-band combinations. |
| State transition | AC1, AC7 | 7 | Lifecycle with a re-entrant loop and a terminal state. |
| Error guessing | AC6, AC8, auth | 6 | Unspecified/undefined behaviors anchored on the ambiguity log (Q4) and the 3c authorization checklist. |

## Priority rationale

Full one-line rationale per assignment lives in `coverage-matrix.md` (copied from
`04-priorities.md`, per the deliverable rule). No arbitration was needed beyond the recorded
scope decision (P1+P2+P3 all generated — full-breadth demo scope, `04-priorities.md`).

## Coverage matrix

See `coverage-matrix.md` (same directory).

## Regeneration changelog

None — first generation.
