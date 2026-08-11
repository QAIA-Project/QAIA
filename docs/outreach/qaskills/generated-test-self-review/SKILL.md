---
name: Generated Test Self-Review
description: Re-scan a test you just generated before writing it to disk, against nine defect classes - four that make an assertion unable to fail, and five measured on real generated suites that a static reader accepts because every assertion is real.
version: 1.0.0
author: opaland
license: MIT
tags: [playwright, code-review, assertions, test-quality, generated-tests, anti-patterns]
testingTypes: [e2e, api, regression]
frameworks: [playwright]
languages: [typescript, javascript]
domains: [web, api]
agents: [claude-code, cursor, github-copilot, windsurf, codex]
---

# Generated Test Self-Review

> **Standalone adaptation.** This is a self-contained version of the self-review lint that ships
> with the `automate` skill of [QAIA](https://github.com/QAIA-Project/QAIA) (MIT). The canonical
> version, the before/after fixture that demonstrates it, and the five judge runs that produced
> classes D5-D9 live in that repository. QAIA is pre-alpha and says so.

## When to use this

**Before a generated spec file is written to disk**, not after. Every defect below costs one line
to fix during generation; the same defect caught later costs a review cycle, and caught by nobody
costs the credibility of every green run in the suite.

This is a **proofread inside generation**, not a score and not a gate.

## The two families

**D1-D4 are shapes**: an assertion that cannot fail whatever the application does. A static reader
catches them.

**D5-D9 are invisible to that reading.** Every one is a *real* assertion, on real state, that any
static tool accepts. They were found by five independent judges reading five generated suites
against their specifications — **none of the five passed the quality gate**.

---

## D1 — Tautological or reflexive comparisons

`expect(true).toBe(true)`, `expect(1).toBe(1)`, `expect(x).toBe(x)`.

A constant asserted against itself. No application state is involved.

## D2 — Contentless `expect()` calls

`expect(true).toBeTruthy()`, `expect("ok").toBeTruthy()` — an argument that is a hardcoded literal
rather than something read from the page or the response.

## D3 — Weak-by-construction matchers on a lazy locator

`.toBeDefined()` or `.not.toBeNull()` **on a Playwright locator handle**.

Worth stating precisely because it looks like a real assertion: Playwright locators are **lazy**.
`page.getByTestId('nope')` returns a perfectly valid, truthy object whether or not that element
exists anywhere in the DOM. The real check is state — `toBeVisible`, `toHaveText`, `toHaveCount`,
`toHaveURL`, a status or a body.

## D4 — Silent zero-assertion blocks

A test whose scenario *had* an expected outcome, and whose body contains zero `expect(...)` calls.
Coverage promised, dropped in the code — while still appearing in the traceability table.

---

## D5 — An assertion that contradicts its own expected outcome

The severest defect of the five, and the least visible.

**Measured case.** A specification demanded, for an email that is *not* a registered account:
*"the security question field is **enabled, the same as for a registered email**"* — the scenario
existing precisely to check that a public endpoint does not leak account existence. The generated
test asserted `expect(enabled).toBe(false)`.

The consequence is not a false negative, it is worse: **the day that test runs green, it is green
because the application leaks.** The defect the scenario exists to detect has become its pass
condition, and CI holds that line indefinitely. When the application is eventually fixed, the test
turns red and reads as a regression to revert.

**Check, per test:** read the expected outcome and the assertion side by side, and ask whether they
agree in **polarity**, not merely in subject.
`is enabled` → `toBe(true)`. `is refused` → an assertion *of the refusal*. `no distinguishable
signal` → an assertion of **sameness between two cases**, which usually means the test must
exercise both.

**Why generation produces it:** when an expected outcome states a *safe default* rather than the
observed behaviour, generating against what the application *does* is the path of least
resistance. That is exactly the moment the specification is telling you the application may be
wrong.

## D6 — The uncertainty flag dropped on the way to the code

**Measured in three suites of five.** A scenario the specification marked as resting on an
unanswered question, whose generated test carries no trace of it — no tag, no comment, no
`test.fixme`.

The severity is in what happens later. When that test goes red, the reader **cannot tell "the open
question just got answered" from "the product regressed"**, and the cheapest resolution is to align
the expected value with the application — **silently converting a finding into a specification**.
In one suite this was armed on the run's own most contestable call: a P1 test, no retries.

**Check:** if the scenario carries a flag, the test must carry it too — in the title, and in a
comment saying the expectation is unconfirmed and that a failure is an *answer* rather than a bug.
Carrying it on a neighbouring test does not count.

## D7 — A test whose whole evidence is one-sided

**Measured in two suites.** Every assertion says only what the result *is not*:

```js
expect(status).not.toBe(200);
expect(alertText.length).toBeGreaterThan(0);
```

The second one is the instructive case. Its scenario demanded a specific error alert **and** the
absence of a success message — and the string `"Product added"` has a length greater than zero, so
the test passes against the forbidden behaviour.

Two things make this worse than it looks:

- Such an assertion **cannot distinguish the refusal under test from any other refusal**. Against
  a target that refuses everything for an unrelated reason, it is green by accident.
- **A negative test whose positive control is red proves nothing.** If the success path for the
  same endpoint is blocked or failing, the negative has no meaning at all.

**Check:** assert the refusal itself, and make it *attributable* — the message naming the field
under test, the state that did not change, the record that was not created. If the scenario also
claims an absence, that clause needs its own assertion.

## D8 — A literal with no provenance

**Measured in three suites.** A status code, message, amount or name asserted as expected without
any source: not in the expected outcome, not in the story, not in observed behaviour.

The dangerous case is not a wrong value, it is a **plausible one that becomes load-bearing**:
*"checkout success is HTTP 200"* appeared in no source, was never observed passing, and six other
tests asserted `not.toBe(200)` against it. An assumption had been promoted to a requirement in
silence.

**Check:** every concrete value traces to the specification, the story, or something the run
actually observed. If it was chosen for automation — a timeout, a seeded name — say so in a comment
next to it. A comment explaining *why polling* is not provenance for *why 8000*.

## D9 — A claim in the report the code does not support

**Measured in two suites.** A run report listing a test project as "actually used" whose
`testMatch` matches no file on disk. A page object citing a `NOTES.md` that was never written. A
traceability row reporting PASS for a scenario whose second expected clause was never asserted.

Each is a citation nobody follows, which is exactly why it survives: it looks authoritative and
costs nothing to write.

**Check:** every artefact the report names exists; every row marked covered corresponds to
assertions covering **all** the clauses of its expected outcome; every configuration described as
used actually ran something.

---

## D10 — The fixture that invalidates the assertion

**D1 to D9 all look at the assertion. None looks at what the setup does to the state the
assertion reads.** A test can be perfectly written and still prove nothing, because its own
fixture keeps re-establishing the condition it is meant to observe changing.

Measured on 2026-08-11, on a generated suite. The cart was seeded declaratively with
Playwright's `addInitScript` — the right instinct, and the one a testability precheck asks for.
But `addInitScript` runs on **every navigation**, so it re-created the cart the application had
just emptied:

- one test went **red for a false reason** (the emptying worked; the fixture undid it);
- two others went **green while proving nothing** — the state they asserted had been re-imposed
  between the action and the check.

Two false greens, produced by a correct-looking fixture, invisible to the nine classes above and
to the author's own reading. Found by *running* the suite and looking at a failure that made no
sense.

Three questions, before a spec reaches disk:

1. **Does any setup hook re-run after the action?** `addInitScript`, a `beforeEach` that
   navigates, a route handler that replays a response — each can re-apply state mid-test.
2. **For every test whose expected outcome is an absence or a decrease** (a cart emptied, an item
   removed, a counter back to zero): could a fixture re-create what the action removed? That is
   the shape most exposed to this class.
3. **Does a green here mean the action worked, or that the fixture won?** If you cannot answer
   from the code, the test does not answer it either.

*This class exists because the other nine did not catch it. A review that only reads assertions
certifies the half of the file that is easiest to get right.*

## On a hit — self-correct before writing

Derive the real assertion from the expected outcome — the concrete value, status or visible state
it names — using the page object or response already in scope.

**If the expected outcome itself names no concrete assertable value, do not fabricate a
plausible-looking check to fill the gap.** Leave the marker:

```js
// TODO: "<expected outcome text>" has no concrete assertable value — needs a human
```

and list the scenario as blocked-for-assertion in the report. **A gap that is visible costs one
line; a gap papered over with a plausible assertion costs the credibility of every green run in
the suite.**

## The hard rule

**Never let a trivial assertion reach disk.** A spec file is not "done generating" until its
`expect(...)` calls have been re-scanned and each one either fixed or explicitly marked
blocked-for-assertion.

## What a static tool can and cannot take off your hands

Three of the nine — the dropped flag, the wholly one-sided test, the dead citation — are
mechanically checkable, and the source project checks them. **The other six need the expected
outcome in front of you**, which is only true during generation. That is the whole reason this is
a generation-time step and not a post-hoc lint.
