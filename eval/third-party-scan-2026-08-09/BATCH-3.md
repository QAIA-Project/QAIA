# Third batch — 21 more repositories, 1 089 tests, 0 new confirmed findings, 2 more tool defects

**Cumulative: 48 repositories, 2 223 Playwright tests.**

| | batch 1 | batch 2 | batch 3 |
|---|---:|---:|---:|
| repositories | 9 | 18 | 21 |
| tests | 271 | 863 | 1 089 |
| candidates, first pass | 20 | 77 | 26 |
| candidates after fixes | 4 | 45 | **6** |
| confirmed third-party defects | 0 | 2 findings / 19 tests | **0** |
| tool defects found | 2 | 3 | **2** |

The candidate rate collapsed — **26 on 1 089 tests, against 77 on 863** in the previous batch. That
is the earlier fixes working, not the code being better.

## The two tool defects

**6. Assertion helpers are as often free functions as methods.** Batch 2 taught the tool that
`await loginPage.expectVisible()` is a verification. It still required a dot in front, so a *free*
helper was invisible:

```ts
test("renders audit heading", async ({ page }) => {
  await expectHeading(page, /audit/i);
});

test("open art renders the art gallery in-shell", async ({ page }) => {
  await openAndAssertHeading(page, "open art", /\/art/, "Art");
});
```

**22 false blocking findings** — `labsai/EDDI-Manager` (17) and `chicio/chicio-blog` (5). Two shapes
are now accepted, both requiring a capital so `checkbox(` and `should(` do not qualify: a name that
*starts* with the intent (`expectHeading`) and one that *carries* it in camelCase
(`openAndAssertHeading`).

This is the same root cause as batch 2's defect, one shape over. The lesson recorded then —
"verification delegated elsewhere is still verification" — was fixed for the case in front of me
rather than for the class.

**7. Angular and Karma specs declare no runner at all.** `describe` and `it` are globals injected
by Jasmine, so there is no import to recognise, and the "no runner found, judge it anyway" branch
let them through. `scaljeri/oh-my-mock` was scored on `src/app/app.component.spec.ts`, producing a
`hollow-assertion` on a file this tool has no business reading.

Playwright's block is `test(`, never `it(`. A file built from `it(` with no Playwright import is now
skipped. Suites importing a local fixtures module are unaffected — they use `test(`.

## The six survivors, and why none was filed

| Repository | Finding | Verdict |
|---|---|---|
| `labsai/EDDI-Manager` ×2 | body is `test.skip(!(await x.isVisible()), 'MSW too slow')` and nothing else | Deliberate: skips when data does not load, passes when it does. Visibility *is* the check. Thin, not broken. |
| `chicio/chicio-blog`, `dasunNimantha/tablio`, `klinnex/bellepoule-modern`, `sawtdakhili/Thoughts-Time` | one test each, verification inside a local helper not present in the fetched slice | Unverifiable from what was fetched — **not a finding**, and recorded as such rather than counted. |

**Issues filed this batch: 0.**

## Cumulative tool defects — all seven

| # | Defect | False findings |
|---|---|---:|
| 1 | `collect_feature_ids` returned one value where the caller unpacked two — crashed on any run without a test book | crash |
| 2 | Three of four budget lines encode QAIA conventions, scoring foreign suites 30/100 | 408 |
| 3 | `.spec.ts` treated as a Playwright marker (Vitest/Jest share it) | 7 |
| 4 | `expect.poll()` chains split across lines read as no assertion | 12 |
| 5 | `toBeDefined()` flagged as hollow on any value, not only on a locator | 24 |
| 6 | Verification delegated to a page object or a helper function not counted | 38 |
| 7 | Angular/Karma specs judged because they import no runner | 1 |

**490 false findings against 2 confirmed findings** (3 counting `realworld#1718`), spanning **19 tests** — cumulative *through batch 3*; batch 4 adds 16 more, see `BATCH-4.md`.
The figure first published — "490 against 19" — mixed its units: **19 was batch 2's TEST count**,
promoted to the campaign's finding total in a sentence whose numerator counts findings. That is the
same "30/100 where only 30 points were reachable" error this report names elsewhere; found by an
adversarial review on 2026-08-09. The numerator checks out: 408 + 7 + 12 + 24 + 38 + 1 = 490.

Every defect was invisible while the tool only ever read its own output.

## What did not change

No regression at any step: the demo suite scores 95.3 on 56 tests, and the reference fixture
reproduces its documented output finding-for-finding and line-for-line, after each of the seven
fixes.
