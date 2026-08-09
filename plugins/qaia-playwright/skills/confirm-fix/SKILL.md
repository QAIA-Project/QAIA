---
name: confirm-fix
description: Close the loop on a defect - re-run the exact test that proved it, decide between closed, still open, and closed-but-something-else-broke, and never let the third verdict be reported as the first. Use after a fix is claimed, before closing a defect, or when asked whether a correction actually worked.
---

# confirm-fix — the half of the loop nobody runs

A tester's cycle is: a test goes red → a defect is written → someone fixes it → **the exact test
that proved the defect is re-run** → and then it is checked that nothing else moved. QAIA could do
the first half. This skill does the second.

Inputs come from `defect-report`: the scenario ID, the minimal reproduction, and the SUT version
the defect was observed against. Without a scenario ID there is nothing to re-run, and the honest
answer is that the defect was never reproducible.

## Three verdicts, and only three

| Verdict | What was observed | What it means |
|---|---|---|
| **Closed** | the proving test is green, and every other test holds its previous result | the fix works and cost nothing |
| **Still open** | the proving test is still red | the fix does not address what the defect described |
| **Closed with collateral** | the proving test is green, **and something that used to pass now fails** | the defect is fixed and the change broke something else |

**The third verdict must never be reported as the first.** That is the entire reason this skill
exists. "Fixed" said about a change that broke two other tests is not a summary — it is a false
statement that the next person inherits.

## Two runs, not one

A confirmation needs a **before** and an **after** on the same suite. Without the before, "this
test is green" says nothing about what the change cost: it may have been green already, and two
other tests may have died unnoticed.

1. **Before** — the suite against the SUT version the defect was observed on. If the defect report
   recorded it, that run may be reused; if it is older than the change, re-run it.
2. **After** — the same suite, unchanged, against the fixed version.
3. **Compare per test, not in aggregate.** "48 green before, 48 green after" hides one test dying
   while another recovers. Compare the verdicts test by test.

## The comparison, and the four transitions

| Before | After | Reading |
|---|---|---|
| red | green | the fix, if this is the proving test — otherwise a **side effect to explain**, not a bonus |
| red | red | still open |
| green | red | **collateral** — the finding that governs the verdict |
| green | green | unchanged |

A `red → green` on a test that is *not* the proving one deserves as much suspicion as a
`green → red`. Something changed that the defect report did not describe, and nobody asked for it.

## The trap that makes the whole exercise worthless

**A test that goes green because its requirement changed is not a fixed defect.**

Measured on a real case ([the campaign](https://github.com/QAIA-Project/QAIA/tree/main/eval/external-application-2026-08-08)): between two versions of the same
project, three tests went from green to red — and **none of them was a regression**. The features
they asserted had been removed from the documentation in the meantime. The code was right; the
tests were stale.

So before any `green → red` is reported as collateral, check that the requirement did not move:
`check_requirement_drift.py` answers exactly that question. A drifted source turns a confirmation
run into noise, and the noise reads like a regression.

## Steps

1. **Take the scenario ID** from the defect report. No ID, no confirmation.
2. **Re-run the proving test alone first.** It is the cheap answer: if it is still red, stop —
   verdict *still open*, and running the full suite proves nothing more.
3. **Check the requirement source** for drift before running the full suite.
4. **Run the full suite** on both versions and compare test by test.
5. **State the verdict**, one of the three, with the transitions that support it.
6. **Report every collateral by name.** A count is not a finding.
7. **Hand the closed defect to `rag-build`** — this step is the one people skip, and skipping it is
   why the same defect class comes back.

   A defect that reached production is evidence that a **test condition was missing**, not merely
   that a line of code was wrong. Ask the single question that generalises it: *what class of input
   or state would have caught this before?* — a boundary nobody bounded, a partition nobody
   enumerated, an interaction between two acceptance criteria nobody crossed.

   Hand that answer over as a candidate entry for `knowledge/anomaly-history.md`, carrying the
   scenario ID, the US-ID and the date. `rag-build` arbitrates duplicates and contradictions; the
   user validates promotion, as always.

   **Only on verdict *closed* or *closed with collateral*.** A defect that is still open has taught
   nothing yet, and writing it down as a lesson would be recording a guess.

   If no generalisable class can be named, say so and write nothing. *"This one was a typo"* is an
   honest outcome; inventing a rule to have something to store is not.

## What this skill must refuse

- **Reporting "closed" when a test went green→red.** The verdict is *closed with collateral*, and
  the collateral is named.
- **Confirming from a single run.** Without a before, there is nothing to compare.
- **Confirming a defect that has no proving test.** It was an observation, not a defect.
- **Treating a stale test as a regression.** Check drift first; the code may be right and the test
  out of date.
- **Re-running only the proving test and calling it a confirmation.** That step decides *still
  open*; it cannot decide *closed*.

## Measured on a real defect

The `_dependent` defect of `typicode/json-server` — found by QAIA from documentation alone, fixed
by the maintainer in commit `1b7c0fb`. Both versions are public, so the confirmation is
reproducible by anyone: [the measurement](https://github.com/QAIA-Project/QAIA/tree/main/eval/confirm-fix-2026-08-08).

The result is the interesting part. The proving test closes, a second defect closes with it — and
**three tests go green→red without a single regression among them**. That case is why step 3 exists.
