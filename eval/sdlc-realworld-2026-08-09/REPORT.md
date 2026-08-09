# The whole SDLC on a reverse-engineered target — `realworld-apps/realworld`

**Date** 2026-08-09 · Target frozen at commit `98f29fb3` ·
Sources treated as *observable*: `specs/e2e/SELECTORS.md` (the published UI contract) and
`specs/e2e/*.spec.ts` (150 behaviours). Source treated as *ground truth to check against*:
`specs/api/openapi.yml`.

Everything before this ran one skill — `automation-score` — across 62 repositories. That measures
**one** phase. This run walks the chain, phase by phase, and states at each what QAIA covers, what
it found, and what it cannot do.

## Why reverse-engineering, and why this target

A real QA team rarely receives a clean specification. It receives a running product and has to
recover the requirement from it. So the requirement here is rebuilt **only** from what an outsider
can observe, and the published `openapi.yml` is then used as an oracle to grade the reconstruction.
That makes the exercise falsifiable instead of merely plausible.

---

## Phase 1 — Discovery: rebuilding the requirement

**QAIA skills:** `us-ingest`, `us-review`, `need-understanding`, `openapi-ingest`, `oracle-generate`

Recovered from the observable artefacts alone:

| | |
|---|---:|
| API endpoints named by the UI contract | 11 |
| page routes | 10 |
| observable behaviours (one per test title) | 150 |
| behavioural domains | 12 |

Checked against the specification: **11 of 12 declared paths were recovered.** The single apparent
divergence — `/articles*` present in the UI contract and absent from the spec — is an artefact of
the reconstruction, not a defect: it is a route-interception glob covering `/articles` and
`/articles/feed`. Recorded rather than filtered, because a reconstruction that quietly drops its
own misses is worthless.

**Reconstruction accuracy: 11/12, with the twelfth explained.**

## Phase 2 — Requirement analysis: the contradiction the reconstruction exposed

**QAIA skill:** `need-understanding` (ambiguity hunt, cross-AC interactions)

Crossing the *specification* against the *behaviours* produced one finding that neither source
shows on its own:

> `openapi.yml` declares **409 Conflict** on `POST /users` and `POST /articles`
> (`components/responses/ConflictError`).
> `error-handling.spec.ts:50` mocks that exact case — `email: ['is already taken']` — as a **400**.
> **No behaviour anywhere exercises a 409.**

Either the specification promises a status the API does not return, or the conformance suite
asserts against the wrong one. For a project whose entire purpose is that many implementations
conform to one contract, the two cannot both be right. Raised as an **open question**, not a defect:
deciding which is correct needs the maintainers.

This is the shape of finding that a scan of the automation layer **cannot produce**, because both
halves look self-consistent from inside.

Full trace of the specification's promised failure codes against observable behaviour:

| code | declared | traced in a behaviour |
|---|---:|---|
| 401 | 16× | yes |
| 422 | 19× | yes |
| 404 | 11× | yes |
| 403 | 3× | yes |
| 204 | 2× | yes |
| **409** | **2×** | **no** |

## Phase 3 — Test strategy

**QAIA skills:** `istqb-design`, `prioritize`, `test-plan-and-closure`

The reconstruction gives the strategy its shape rather than the other way round. Behaviour weight by
domain, recovered from the suite:

| domain | behaviours | reading |
|---|---:|---|
| error-handling | 37 | The suite's centre of gravity is failure, not success — unusual and good. |
| user-fetch-errors | 17 | |
| url-navigation | 16 | |
| null-fields | 12 | An entire domain devoted to absent values. |
| articles / comments / navigation | 31 | The nominal paths. |
| auth / settings / social | 24 | |
| xss-security | 8 | |
| health | 5 | |

**Observation for the strategy, not a defect:** 66 of 150 behaviours (44 %) exercise error paths,
while the specification's own material for deriving them is thin — no `enum`, and 16 of 22 required
text fields carry no constraint at all (`eval/openapi-realworld-2026-08-09/`). The suite is testing
failure modes the specification never describes. That is the correct instinct and an undocumented
contract at the same time.

## Phase 4 — Test data

**QAIA skill:** `qaia-testdata:dataset-generate` (synthetic only, never real data or PII)

What the specification affords for data design, measured:

| source | usable for data derivation |
|---|---|
| `enum` | **none in the whole document** |
| `maxLength` / `minLength` / `pattern` | **none** |
| `format: email` | **declared nowhere** — `email` is `type: string` |
| numeric bounds | 2 (`offset ≥ 0`, `limit ≥ 1`) |

`limit` declares a minimum and **no maximum**, so a conforming client may request
`limit=2000000000`. Per the skill's own rule this is an open question for a human, not a defect —
the specification does not say the server accepts it.

**Consequence:** almost every boundary value for this product would have to be invented. QAIA
forbids inventing them; they become `# open: Qn`. A test-data strategy here is therefore blocked on
a specification decision, and saying so is the deliverable.

## Phase 5 — Automation

**QAIA skills:** `automate`, `a11y-audit`, `perf-check`, `security-surface`, `visual-check`,
`traffic-replay`, `contract-probe`, `flaky-detect`, `locator-repair`, `impact-select`
**Scored by:** `automation-score`

Already measured: 128 tests, **100/100** on assertion substance in third-party mode, one confirmed
defect filed as [realworld-apps/realworld#1718](https://github.com/realworld-apps/realworld/issues/1718).

Coverage by test type, against what the suite actually contains:

| type | present in the target | QAIA skill exists |
|---|---|---|
| functional E2E | yes (128) | `automate` |
| security (XSS) | yes (8) | `security-surface` |
| API contract | yes (`specs/api`) | `contract-probe`, `openapi-ingest` |
| accessibility | **no** | `a11y-audit` |
| performance | **no** | `perf-check` |
| visual regression | **no** | `visual-check` |
| flakiness | **no** | `flaky-detect` |

**Four test types the target does not cover at all**, and QAIA has a skill for each. Not filed:
"you have no accessibility tests" is a product decision, not a defect.

## Phase 6 — Production weak signals

**QAIA skills:** `traffic-replay` (HAR → tests), `run-report`, `flaky-detect`, `confirm-fix`,
`impact-select`

**This is the thinnest phase, and the honest statement is that QAIA does not close it.** Every skill
listed reads an artefact a human hands over — a HAR file, a run, a diff. **Nothing ingests
production telemetry**: no log stream, no error-rate feed, no APM. `traffic-replay` is the closest
thing and it still waits for someone to export a capture.

`docs/adr/0007` scopes the project to Delivery + Maintenance, so this is a *known* edge rather than
an oversight — but "weak signals from production" is not covered today, and no amount of scanning
third-party repositories would have revealed that. Naming it is the result.

---

## The four feedback loops

Loops, not phases: each one carries a fact from a later stage back to an earlier one. QAIA has
material for three; the fourth does not exist yet.

### Loop A — Production → Discovery *(does not exist)*

A 409 the API actually returns, or a `limit` value a client actually sends, is the cheapest possible
answer to the open questions Phase 2 and Phase 4 could not resolve. Today those questions go to a
human and wait.

**What would close it:** an ingest that turns observed production responses into evidence attached
to the open question — *"Q3 asked whether `limit` is bounded; 30 days of traffic show a maximum
observed value of 100 and three 422s above it."* The question stays open, but it stops being blind.

**Why it is worth naming rather than building today:** it is the only loop that would let a
specification correct itself from reality, and ADR 0007 deliberately puts it out of scope. That
trade-off should be a decision, not an omission.

### Loop B — Automation → Requirement *(exists, unwired)*

The 409/400 contradiction was found by crossing the spec with the suite. Nothing does that crossing
on a schedule. `contract-probe` compares an app against its own documentation; the missing half is
comparing the **test suite** against the documentation — which is pure text analysis, needs no
running app, and would have caught this one.

**Cost:** a check in the same family as `check_schema_matches_validator.py`, which already exists
here for exactly this reason one level down.

### Loop C — Defect → Test data *(exists: `feedback` + `rag-build`)*

Every confirmed defect is evidence that a data partition was missing. `feedback` captures the
tester's correction and `rag-build` promotes it into a git-versioned knowledge base reused by the
next generation. **The loop is built; what is missing is the trigger** — nothing fires it when
`confirm-fix` closes a defect.

### Loop D — Scan → Tool *(the only one running, and it is this session's actual result)*

Pointing the tool at code it did not write produced **8 defects in the tool and 506 false findings**
across 62 repositories, against 2 confirmed findings spanning 19 tests — the "490 against 19" first published mixed a
findings count with a test count. Each fix was locked by a selfcheck assertion and verified by re-breaking it.

That loop is the one that worked, and it is worth stating why: **it is the only one where the
feedback was mechanical, immediate, and impossible to argue with.** The other three all route
through a human, which is why all three are stalled.

---

## What this run changes

**Answering the question directly: QAIA is not only E2E automation.** 35 skills span ingest →
design → data → automation → scoring → closure, and 4 of the 7 test types the target lacks have a
skill waiting.

**But the scan that ran for two days exercised exactly one of them.** The breadth was in the
repository and not in the measurement, and that gap was invisible until the phases were walked one
by one.

**Two things are genuinely missing**, and neither would have been found by more scanning:
a production-telemetry ingest (Loop A), and a scheduled spec-versus-suite comparison (Loop B).
