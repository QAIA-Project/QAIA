---
name: defect-report
description: Turn a failing test into a defect report a developer can act on - minimal reproduction, expected vs actual traced to its requirement, evidence-bounded severity, and the scenario ID that found it. Use when a run is red and someone has to fix it, when a finding must reach a tracker (GitHub, Jira, Azure DevOps), or when asked to write up an anomaly.
---

# defect-report — the anomaly, written so it can be acted on

A red test says *something is wrong*. A defect report says *what is wrong, how to see it again,
and against which promise*. QAIA produced the first and never the second, which is the gap this
skill closes ([#75](https://github.com/QAIA-Project/QAIA/issues/75), the backlog entry that named it).

## The rule that governs everything here

**Never state a cause you have not observed.**

A report that asserts an unverified diagnosis is worse than no report: it sends a developer down
a path chosen by a model, and it costs more than the defect. Every sentence of the output must be
readable in the attached evidence — the trace, the response body, the screenshot, the diff of
expected vs actual. Where the cause is unknown, the report says so, in those words.

This is the same rule as everywhere else in QAIA (`references/evidence-discipline.md`), and it is
the one that most often gets bent under pressure to sound useful.

## Inputs

| Input | Required | Where it comes from |
|---|---|---|
| The failing test's output | yes | Playwright reporter, `results.json`, terminal |
| The scenario it implements | yes | the `@QAIA-xxx` tag in the test title → the `.feature` |
| The requirement behind it | yes | the test book's stated source (see `REQUIREMENT-SOURCE.json` if present) |
| Trace, screenshot, HAR | if produced | `test-results/`, `trace.zip` |
| The system under test's version | yes | commit, tag, or build identifier |

If the scenario ID is missing from the test title, **stop and say so**. A defect that cannot be
traced back to a promise is an observation, not a defect, and it will be argued away.

## Steps

1. **Reproduce, minimally.** Re-run the single failing test in isolation, not the suite. A defect
   that only appears inside a full run is a different defect — an isolation or ordering problem —
   and must be reported as that instead. Note which of the two you have.
2. **Establish the promise.** Quote the requirement the scenario derives from, verbatim, with its
   location. Not a paraphrase: the argument about whether this is a defect will be won or lost on
   that quote.
3. **Separate expected from actual.** Expected comes from the requirement. Actual comes from the
   run. If you cannot state expected without reading the code, **the requirement is silent** and
   this is an ambiguity to raise (`# open: Qn`), not a defect to file.
4. **Reduce the reproduction.** Strip every step the failure does not need. The target is the
   shortest sequence that still fails, expressed in what a user or a client does — not in test
   framework calls.
5. **Argue the severity.** See the table below. A severity without its reason is a number someone
   will change.
6. **Attach the evidence** and reference it by name in the text.
7. **Write it out** in the target format (`references/tracker-formats.md`).

## Severity, and how to argue it

Severity is about **consequence**, priority is about **schedule**. Do not merge them; teams that
merge them argue about the wrong thing.

| Severity | Criterion | It must be readable in the evidence that... |
|---|---|---|
| Critical | data loss, corruption, or an authorization boundary crossed | the wrong actor obtained data, or the data is gone |
| Major | a documented promise is not kept, no workaround | the promised behaviour is absent |
| Minor | promise not kept, workaround exists | the workaround is *named*, not assumed |
| Cosmetic | no functional consequence | the function is intact |

A silent failure — the application answers `200` and does nothing — is at least **Major** even
when nothing looks broken, because nothing downstream can detect it. That case is the reason this
table exists.

## Output shape

```
Title      one line: what is not kept, where. Not "bug in X".
Severity   + one sentence of argument
Version    the exact SUT identifier the run was against
Scenario   @QAIA-xxx, and the .feature it lives in
Promise    verbatim quote of the requirement + location
Steps      the minimal reproduction, numbered, in user or client terms
Expected   from the promise
Actual     from the run, quoted from the evidence
Evidence   named files, each referenced above
Cause      "not established" unless observed. If observed, say what you observed.
Scope      what else you checked and found intact -- this is what makes the report trustworthy
```

The last two lines are the ones that separate a defect report from a complaint. `Cause: not
established` is a complete and honest answer. `Scope` tells the developer how far you looked, so
they know what you did *not* check.

## What this skill must refuse

- **Filing against a promise that does not exist.** If the requirement is silent, the output is an
  ambiguity, not a defect. Section 3 above.
- **Guessing the fix.** Suggesting a patch means asserting a cause. If the cause is not observed,
  there is no fix to suggest.
- **Reporting a flaky test as a defect.** A verdict that varies across runs of unchanged code is a
  test problem until proven otherwise — re-run it on unchanged code and show the verdicts vary first.
- **Merging several defects into one report.** One promise not kept, one report. A report that
  lists three problems gets closed when one is fixed.

## Verified against a real one

Applied to the first defect QAIA ever found in software it did not write — `_dependent` in
`typicode/json-server`, `eval/external-application-2026-08-08/`. That defect has a **human-written
upstream ticket** (issue #1551) to compare against, which is a rarer yardstick than any rubric:
the comparison is in `references/verified-against-1551.md`.

The short version, and **neither report dominates**. The human named the cause exactly — *"the
parameter in the document is `_dependent`, but in the code it is `dependent`"* — because they read
the source and linked the line. Reading the source **is** observing, so that report obeys the rule
above; it does not break it. Ours, written without ever opening the code, says `Cause: not
established` — honest, and weaker.

What ours has that the human ticket does not: a **re-runnable test** that fails on demand, the
promise quoted verbatim from the README, expected and actual as text rather than inside a
screenshot, and a severity with an argument.

The lesson is not "we won". It is that a report written from the contract and a report written
from the code are **complementary**, and that the cheap half — reproduction, traceability,
expected vs actual — is the half a machine can do reliably.
