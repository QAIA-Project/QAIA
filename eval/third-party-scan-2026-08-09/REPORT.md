# Nine third-party Playwright suites scanned — 20 candidate findings, 0 filed

**Date** 2026-08-09 · **Tool** `eval/tools/automation_score.py --third-party --skip-mutation` ·
**Scope** 9 repositories, 271 Playwright tests

Follow-up to `eval/realworld-2026-08-09/`, where the same tool found one real defect in a
third-party suite and it was filed as
[realworld-apps/realworld#1718](https://github.com/realworld-apps/realworld/issues/1718).

## The rule this run was built around

The RealWorld scan returned **428 findings of which exactly 1 was real**. Filing automatically at
that precision means sending 427 false alarms to volunteer maintainers, which gets an account
restricted and burns a project's name permanently. So: **scan wide, file only what has been read by
eye and confirmed.**

That rule is the whole result below.

## What was scanned

| Repository | tests | high-precision candidates |
|---|---:|---:|
| `openplayerjs/openplayerjs` | 77 | 12 |
| `kurotu/vpm-catalog` | 35 | 0 |
| `vnglst/koenvangilst.nl` | 33 | 0 |
| `dbcls/sparqlist` | 31 | 0 |
| `mxfng/drumhaus` | 29 | 1 |
| `valhalla/web-app` | 22 | 7 |
| `accordproject/template-playground` | 20 | 0 |
| `kawalcovid19/wargabantuwarga.com` | 16 | 0 |
| `COVESA/ifex-viewer` | 8 | 0 |
| **total** | **271** | **20** |

"High-precision" means `single-sided-evidence`, `hollow-assertion` or `test-without-assertion` —
the three rules that are blocking, and the only ones considered filing-worthy.

## Every one of the 20 was false, and two were our fault

| Candidates | Cause | Verdict |
|---:|---|---|
| 7 | `valhalla/web-app` — **13 of its 15 `.spec.ts` files are Vitest unit tests.** The rule reads "`toBeDefined()` — a locator handle always exists", which is sound about a Playwright locator and simply wrong about a plain object, where `toBeDefined()` genuinely checks a key exists. | **tool defect** |
| 12 | `openplayerjs` and `drumhaus` — `expect.poll()` written as a chain over several lines left `expect` alone on its line, so the line-by-line detector saw no assertion at all. | **tool defect** |
| 1 | `openplayerjs/e2e/live.spec.ts:170` — `expect(text).not.toBe('0:00')`, genuinely one-sided. | **not filed**, see below |

Three of the twelve were compounded by a flaw in the *scan method* rather than the tool: only
`.spec.*` files were fetched, so `waitForPlayback()` — which holds the assertion — was absent from
the scan directory. Fetching `e2e/helpers/player.ts` showed a real
`expect.poll(...).toBeGreaterThan(...)` inside it.

### The one that was real but not worth filing

```js
test('current time value is non-zero during live playback', async ({ page }) => {
  const text = await page.locator(sel.currentTime).innerText();
  expect(text).not.toBe('0:00');
});
```

One-sided: `NaN:NaN` or `--:--` would pass. But the test's name says *non-zero*, and the assertion
says exactly that — unlike the RealWorld case, there is no single correct positive value for a live
stream's clock, and no sibling test demonstrating the intended shape. That makes it a **suggestion,
not a defect**, and the bar for opening an issue in someone else's repository is a defect.

**Issues filed: 0 of 20 candidates.**

## The two tool defects, fixed

**1. `.spec.ts` is not a Playwright marker.** Vitest, Jest and Mocha use the same suffix, and every
rule in this tool is Playwright-specific. `find_spec_files` now returns `(playwright, skipped)` and
says out loud which files it declined to judge.

**2. `expect.poll()` chains were invisible.** `test-without-assertion` is **blocking in default
mode**, so a QAIA-generated suite using a documented Playwright idiom would have been failed by its
own scorer. `join_chains()` rejoins a split chain onto the line where it starts, replacing the
continuation lines with placeholders so reported line numbers stay true.

### Verified in both directions

Both fixes are locked by assertions in `selfcheck_automation_score.py`, and each was checked by
reverting it:

```
EXPECT_CALL aveugle a expect.poll                    ATTRAPE
find_spec_files ne separe plus les runners etrangers ATTRAPE
```

The second assertion had to be rewritten first: its initial version only checked that
`find_spec_files` returned a 2-tuple, and **passed with the skip branch disabled outright**. It now
builds a temporary directory holding one Playwright spec and two foreign-runner specs and asserts
the split.

No regression on our own suites: the demo suite still scores 95.3 with 56 tests, and the reference
fixture reproduces its documented output finding-for-finding and line-for-line.

After the fixes, the same 271 tests yield **4 candidates instead of 20** — the three helper-delegated
ones and the one judged a suggestion.

## Honest limits

- **9 repositories is not "the maximum".** Bulk harvesting was refused by this environment's
  guardrail, which is the correct call for an operation shaped like mass-scanning with automated
  issue filing. Repositories were therefore taken one at a time from a single code search.
- **Static track only**; no application was stood up, no third-party host was contacted beyond
  reading files from the GitHub API.
- **Absence of findings is not proof of quality.** These suites were judged on assertion shape, not
  on whether they assert the right thing — the standing separation between this tool and the LLM
  rubric.
