# QAIA catalogue — I want to X, which skill?

7 skills across 3 plugins.

**Out of scope, deliberately** ([ADR 0004](../../docs/adr/0004-test-level-boundary.md)): unit and component tests, integration between internal components, and coverage-driven white-box testing. QAIA starts from a promise observable from the outside — a test written against a function is written against the implementation, which is the oracle it exists to avoid.

QAIA is an engine for the gap between **a promise** and **what claims to keep it**. Its skills
follow three faces of that gap: write the tests a promise calls for (`generate`), judge tests that
already exist (`judge`), and confront a running system with its own documentation
(`contract-probe`).

---

## Writing the tests — `generate` (qaia-core)

One skill since 0.4.0; each step is a page of it. Each step reads the previous one's checkpoint
and writes its own, so the journey survives an interrupted session.

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

| I want to | Skill | Plugin |
|---|---|---|
| Attach production evidence (logs, error rates, HAR) to the open questions a book carries | `signal-ingest` | core |

## Turning a book into running tests (qaia-playwright)

| I want to | Skill |
|---|---|
| Generate native Playwright tests from the book, and merge their results into the run manifest | `automate` |
| Turn a red test into something a developer can act on | `defect-report` |

## Checking a running application (qaia-playwright)

**The distinction is not the tool, it is what plays the role of the oracle** — what each skill
compares observed behaviour *against*.

| I want to check | Skill | Its oracle is | Needs |
|---|---|---|---|
| That the app does what **its own documentation promises** | `contract-probe` | the target's written contract (README, API docs, acceptance criteria) — archived verbatim before probing | a self-hosted or explicitly authorised target |
| That **today's responses still match yesterday's**, on real captured traffic | `traffic-replay` | a HAR file *you* recorded | a captured traffic export |

A defect `contract-probe` reports is a broken promise; one `traffic-replay` reports is a change
since your capture, which may well be intended.

Corollary worth stating: **`contract-probe` can only find a defect the documentation makes
findable.** If the target documents nothing, it correctly reports nothing — and that is the
discipline it exists for, not a failure.

## Judging, and who is allowed to do it — `judge` (qaia-score)

No producer scores its own output. Judging lives in a separate, read-only plugin for that
reason — one skill, `judge`, since 0.3.0.

| I want to | `judge` page |
|---|---|
| Audit any Gherkin test book, QAIA or not | the skill itself |
| Score a test book against its source story (10-dimension ISTQB rubric) | `references/scoring-testbook.md` |
| Score generated Playwright code (static pass + mutation pass, never summed) | `references/scoring-automation.md` |
| Compare an OpenAPI spec with the suite that claims to cover it | `references/spec-vs-suite.md` |
| Get a release verdict — PASS / CONCERNS / FAIL / WAIVED | `references/release-gate.md` |

## What is no longer here, and why

On 2026-10-26 seventeen skills were deleted. Accessibility, security surface, usability,
performance and visual regression: five disciplines needing real expertise, none ever validated
by external evidence. Locator repair, flakiness detection, run reports, fix confirmation and
impact selection: CI tooling that belongs to whoever owns the runner. The knowledge-base builder
and the feedback loop: never once exercised by a real correction. The test plan and closure
report, the synthetic dataset generator: documents for a reader who does not exist yet. The
`qaia` router, `qaia-help` and `hello`: nothing left to route with three named entry points.

**No capability comes back without being measured on material QAIA did not write.**
