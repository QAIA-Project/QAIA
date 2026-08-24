# QAIA catalogue — I want to X, which skill?

33 skills across 4 plugins.

**Out of scope, deliberately** ([ADR 0004](../../docs/adr/0004-test-level-boundary.md)): unit and component tests, integration between internal components, and coverage-driven white-box testing. QAIA starts from a promise observable from the outside — a test written against a function is written against the implementation, which is the oracle it exists to avoid. This page exists because a cold read by four business personas found
the boundary between three shift-right skills unreadable *without reading all three* — and a
skill that has to spend six lines explaining it is not a duplicate is a catalogue problem, not a
wording problem. The answer taken: **keep the skills distinct, publish the map.**

You do not have to read this. Describing what you want in plain language to the `qaia` meta-skill
routes you to the right step. This is for when you would rather look it up.

---

## The journey, in order

Each step reads the previous one's checkpoint and writes its own, so the journey survives an
interrupted session.

| I want to | Skill | Plugin |
|---|---|---|
| Bring a user story in (paste, file, URL, Jira) | `us-ingest` | core |
| Bring a formal API contract in (OpenAPI, Swagger) | `openapi-ingest` | core |
| Write the plan a manager signs, or the closure report they read | `test-plan-and-closure` | core |
| Check the extraction is faithful before building on it | `us-review` | core |
| Find what the story does *not* say — ambiguities, contradictions | `need-understanding` | core |
| Set up or enrich the team's shared knowledge base | `rag-build` | core |
| Choose and justify ISTQB techniques per acceptance criterion | `istqb-design` | core |
| Rank test conditions by risk, with a human arbitrating | `prioritize` | core |
| Produce the Gherkin test book with stable IDs and a coverage matrix | `testbook-generate` | core |
| Export it (`.feature`, XLSX, Xray/TestRail CSV) | `testbook-export` | core |
| Turn my corrections into rules the tool applies next time | `feedback` | core |
| Roll the whole journey into the standard run manifest | `report` | core |

**Not part of the sequence, usable at any point:**

| I want to | Skill | Plugin |
|---|---|---|
| Know where I am and what to do next | `qaia-help` | core |
| Check my install and see what is available | `hello` | core |
| Hand the whole thing to one conversational agent | `qaia` | core |
| Audit a test book I did **not** generate with QAIA | `testbook-validate` | core |
| Derive expected results from a known standard (ISO, RFC, OpenAPI…) | `oracle-generate` | core |
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

No producer scores its own output. These three live in a separate, read-only plugin for that
reason.

| I want to | Skill |
|---|---|
| Score a test book against its source story (10-dimension ISTQB rubric) | `testbook-score` |
| Score generated Playwright code (static pass + mutation pass, never summed) | `automation-score` |
| Get a release verdict — PASS / CONCERNS / FAIL / WAIVED | `aptitude-gate` |

## Two names that need explaining, which is itself a finding

`hello` and `aptitude-gate` were both flagged in the same cold read: *a name that needs explaining,
in a catalogue of thirty entries, will not be invoked.* Renaming them is a breaking change for
existing journeys, so it has not been done — the cost was judged disproportionate to the benefit
while the catalogue has no users. If that changes, they are the two to rename, and this line
exists so the decision is inherited rather than rediscovered.
