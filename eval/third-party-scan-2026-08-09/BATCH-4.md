# Fourth batch — 14 repositories, 1 011 tests, 0 filed, and the defect that would have made me file wrongly

**Cumulative: 62 repositories, 3 234 Playwright tests.**

This report exists because an adversarial review on 2026-08-09 pointed out that batch 4 was
recorded in the decision register (D178) and had **no report at all**, while the campaign's
headline figures — "490 false findings", "7 tool defects" — were being carried forward onto
"62 repositories and 8 defects". A three-batch number attached to a four-batch campaign.

| | batch 1 | batch 2 | batch 3 | **batch 4** |
|---|---:|---:|---:|---:|
| repositories | 9 | 18 | 21 | **14** |
| tests | 271 | 863 | 1 089 | **1 011** |
| confirmed defects | 0 | 2 findings / 19 tests | 0 | **0** |
| tool defects found | 2 | 3 | 2 | **1** |

## Defect 8 — `empty-test-body` fired on declared placeholders

Two repositories came back with empty test bodies: `solidcouch/solidcouch` (10) and
`Studio-Saelix/sencho` (6). The rule was written the day before and had just produced a real,
filed-worthy finding on a third repository, so the temptation to file was strong.

Reading the source first showed this:

```ts
test.fixme('give contacts access to my hospex', () => {})
test.fixme('allow removing other person from contacts', () => {})
```

**`test.fixme()` is exactly the mechanism the rule recommends.** Playwright reports those as
*skipped*, not passed — which is the entire remedy the finding proposes. `solidcouch/solidcouch`
was doing the right thing, and the rule was about to reproach it for that.

`TEST_DECL` captured the modifier but `empty-test-body` ignored it. Declared placeholders
(`fixme`, `skip`, `fail`) are now exempt; an *undeclared* empty body still blocks.

After the fix: `empty-test-body` drops to **0** on both repositories.

**Without the standing rule that every finding is read in the source before it leaves the machine,
a wrong issue would have been filed against a project for following the advice the finding gives.**

## The corrected campaign totals

| # | Defect | False findings |
|---|---|---:|
| 1 | `collect_feature_ids` returned one value where the caller unpacked two | crash |
| 2 | Three of four budget lines encode QAIA conventions | 408 |
| 3 | `.spec.ts` treated as a Playwright marker | 7 |
| 4 | `expect.poll()` chains split across lines | 12 |
| 5 | `toBeDefined()` flagged as hollow on any value | 24 |
| 6 | Verification delegated to a page object or helper not counted | 38 |
| 7 | Angular/Karma specs judged because they import no runner | 1 |
| **8** | **`empty-test-body` fired on `test.fixme()`** | **16** |

**506 false findings against 2 confirmed findings**, spanning 19 tests, across 62 repositories.

The ratio published earlier as "490 against 19" was wrong twice: it omitted batch 4's 16, and its
denominator was a **test** count standing in for a **findings** count. Both corrected here.

## What this batch says that the first three did not

Batch 1 found 20 candidates in 271 tests. Batch 4 found 40 in 1 011 — and **all 40 were false**,
16 of them from a rule written the previous day.

**A new rule is at its most dangerous on the day it is written**, when it has just been validated
on the one case it was built from and has not yet met a project that solves the problem differently.
Both batch-4 repositories were doing it right.

## Honest limits

- **0 issues filed.** The two written in batch 2 remain unfiled — the environment refused further
  third-party issue creation, and the block was not worked around.
- **Static track only**, as in every batch. No application was stood up.
- **Absence of findings is not proof of quality.** These suites were judged on assertion shape,
  not on whether they assert the right thing.
