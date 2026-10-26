# QAIA catalogue — I want to X, which skill?

24 skills across 4 plugins.

**Out of scope, deliberately** ([ADR 0004](../../docs/adr/0004-test-level-boundary.md)): unit and component tests, integration between internal components, and coverage-driven white-box testing. QAIA starts from a promise observable from the outside — a test written against a function is written against the implementation, which is the oracle it exists to avoid. This page exists because a cold read by four business personas found
the boundary between three shift-right skills unreadable *without reading all three* — and a
skill that has to spend six lines explaining it is not a duplicate is a catalogue problem, not a
wording problem. The answer taken: **keep the skills distinct, publish the map.**

You do not have to read this. Describing what you want in plain language to the `qaia` meta-skill
routes you to the right step. This is for when you would rather look it up.

---

## The journey, in order

Since 0.4.0 the journey is **one skill, `generate`**, and each step is a page of it. Each step
reads the previous one's checkpoint and writes its own, so the journey survives an interrupted
session.

| I want to | `generate` step | Page under `skills/generate/references/` |
|---|---|---|
| Bring a user story in (paste, file, URL, Jira) | 1 | `01-ingesting-a-requirement.md` |
| Bring a formal API contract in (OpenAPI, Swagger) | 1b | `01b-ingesting-an-api-spec.md` |
| Check the extraction is faithful before building on it | 2 | `02-verifying-the-extraction.md` |
| Find what the story does *not* say — ambiguities, contradictions | 3 | `03-understanding-the-need.md` |
| Choose and justify ISTQB techniques per acceptance criterion | 4 | `04-choosing-techniques.md` |
| Derive expected results from a known standard (ISO, RFC, OpenAPI…) | 5 | `05-grounded-oracles.md` |
| Rank test conditions by risk, with a human arbitrating | 6 | `06-prioritising-by-risk.md` |
| Produce the Gherkin test book with stable IDs and a coverage matrix | 7 | `07-emitting-the-test-book.md` |
| Roll the whole journey into the standard run manifest | 8 | `08-the-run-manifest.md` |
| Export it (`.feature`, XLSX, Xray/TestRail CSV) | 9 | `09-exporting.md` |

Around the journey:

| I want to | Skill | Plugin |
|---|---|---|
| Write the plan a manager signs, or the closure report they read | `test-plan-and-closure` | core |
| Set up or enrich the team's shared knowledge base | `rag-build` | core |
| Turn my corrections into rules the tool applies next time | `feedback` | core |

**Not part of the sequence, usable at any point:**

| I want to | Skill | Plugin |
|---|---|---|
| Know where I am and what to do next | `qaia-help` | core |
| Check my install and see what is available | `hello` | core |
| Hand the whole thing to one conversational agent | `qaia` | core |
| Audit a test book I did **not** generate with QAIA | `judge` | score |
| Get a realistic synthetic dataset, never real data | `dataset-generate` | testdata |

## Turning a book into running tests

| I want to | Skill |
|---|---|
| Generate native Playwright tests from the book | `automate` |
| Fix a test failing because a locator broke | `locator-repair` |
| Produce an execution report in a format the profession consumes | `run-report` |
| Turn a red test into something a developer can act on | `defect-report` |
| Work out what a diff puts at risk in an existing suite | `impact-select` |
| Decide whether a claimed fix actually closed the defect | `confirm-fix` |

## Checking a running application

This is where the boundary was unreadable. **The distinction is not the tool, it is what plays the
role of the oracle** — what each skill compares observed behaviour *against*.

| I want to check | Skill | Its oracle is | Needs |
|---|---|---|---|
| That the app does what **its own documentation promises** | `contract-probe` | the target's written contract (README, API docs, acceptance criteria) — archived verbatim before probing | a self-hosted or explicitly authorised target |
| That the app does not leak or over-trust, by **risk-ranked security angles** | `security-surface` | known defect classes (CT-SEC: auth, IDOR, error disclosure) | two real accounts for the IDOR pass |
| That **today's responses still match yesterday's**, on real captured traffic | `traffic-replay` | a HAR file *you* recorded | a captured traffic export |
| That a verdict is stable across identical runs | `flaky-detect` | the same test, run repeatedly against unchanged code | a suite that already runs |
| That the app is usable | `usability-heuristic-review` | Nielsen's 10 heuristics (CT-UT) | a running UI |
| That it is accessible | `a11y-audit` | WCAG 2 A/AA — automated pass **plus a mandatory manual pass** | a running UI |
| That it stays fast enough | `perf-check` | latency budgets you state, CT-PT test types | a running app |
| That it still **looks** right | `visual-check` | committed screenshot baselines | a running UI, stable data |

Read the middle column downwards and the overlap disappears: four skills touch a running HTTP app
and **no two of them compare it to the same thing**. A defect `contract-probe` reports is a broken
promise; one `security-surface` reports is a known-dangerous pattern the documentation may never
mention; one `traffic-replay` reports is a change since your capture, which may well be intended.

Corollary worth stating: **`contract-probe` can only find a defect the documentation makes
findable.** If the target documents nothing, it correctly reports nothing — and that is the
discipline it exists for, not a failure.

## Scoring, and who is allowed to do it

No producer scores its own output. Judging lives in a separate, read-only plugin for that
reason — one skill, `judge`, since 0.3.0.

| I want to | `judge` page |
|---|---|
| Audit any Gherkin test book, QAIA or not | the skill itself |
| Score a test book against its source story (10-dimension ISTQB rubric) | `references/scoring-testbook.md` |
| Score generated Playwright code (static pass + mutation pass, never summed) | `references/scoring-automation.md` |
| Compare an OpenAPI spec with the suite that claims to cover it | `references/spec-vs-suite.md` |
| Get a release verdict — PASS / CONCERNS / FAIL / WAIVED | `references/release-gate.md` |

## Two names that need explaining, which is itself a finding

`hello` and `aptitude-gate` were both flagged in the same cold read: *a name that needs explaining,
in a catalogue of thirty entries, will not be invoked.* `aptitude-gate` no longer exists as a
skill — it is `judge`'s release-gate page since 0.3.0. `hello` remains, and is the one to rename
if the catalogue ever has users; this line exists so the decision is inherited rather than
rediscovered.
