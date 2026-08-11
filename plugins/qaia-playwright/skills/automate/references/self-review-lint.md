# Step 5 — the self-review lint, in full

## What it is, and what it is carefully not

Before each `*.spec.js` is written to disk, re-scan the assertions it is about to contain and
fix what is hollow.

This is a **proofread inside generation**, not a score and not a gate. It is the same posture
`qaia-score` takes at the Gherkin level with its hollow- and vague-assertion detectors
([`eval/tools/structural_score.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/structural_score.py), checks C1/C2), one layer down in the generated code — run by
the producer on its own output **before delivery**, never as a validation of already-delivered
work.

That boundary matters and is not decorative: the shared rule is that **no producer scores
itself** (`https://github.com/QAIA-Project/QAIA/blob/main/plugins/qaia-core/skills/README.md`, rule 3). So this pass never touches
`.qaia/reports/**/manifest.json`'s `gate` field, and `qaia-score` still never reads generated
`.spec.js` files. The contract boundary is unchanged — a generator is allowed to proofread
itself, never to grade itself.

It runs on every generated spec and is silent when clean.

## The four hollow-assertion defects

### D1 — Tautological / reflexive comparisons

`expect(true).toBe(true)`, `expect(1).toBe(1)`, `expect(x).toBe(x)`, or any `expect(<literal>)`
compared against that same literal.

A constant asserted against itself. No SUT state is involved, so the test cannot fail for any
reason connected to the application.

### D2 — Contentless `expect()` calls

No argument, or an argument that is a hardcoded literal rather than something read from the page
or the response: `expect(true).toBeTruthy()`, `expect("ok").toBeTruthy()`.

Nothing about the app is being checked.

### D3 — Weak-by-construction matchers

`.toBeDefined()` or `.not.toBeNull()` **on a Playwright locator handle**.

This one is worth stating precisely because it looks like a real assertion. Playwright locators
are **lazy**: `page.getByTestId('nope')` returns a perfectly valid, truthy object whether or not
that element exists anywhere in the DOM. Asserting the handle is defined asserts that
`getByTestId` returned an object — which it always does.

The real check is **state**: `toBeVisible`, `toHaveText`, `toHaveCount`, `toHaveURL`, a response
status or body.

### D4 — Silent zero-assertion blocks

A test mapped from a scenario that *had* a `Then` in step 1, but whose generated body contains
zero `expect(...)` calls.

Coverage promised by the scenario, dropped in the code. The scenario still appears in the
traceability table, still counts as automated, and verifies nothing.

## Five more defects, measured rather than imagined

D1-D4 are shapes: an assertion that cannot fail whatever the application does. The five below are
different and were invisible to that reading — every one of them is a *real* assertion, on real
state, that a static reader accepts. They come from five independent judges applying
[`eval/AUTOMATION-RUBRIC.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/AUTOMATION-RUBRIC.md) to five generated suites, and every one was verified by hand against
the file before being written here. **None of the five suites passed the rubric's gate.**

### D5 — an assertion that contradicts its own `Then`

The severest defect found in the corpus, and the least visible.

One suite's book demanded, for an email that is *not* a registered account: *"the Security
Question field **is enabled, the same as for a registered email**"* — the scenario existing
precisely to check that a public endpoint does not leak account existence. The generated test
asserted `expect(enabled).toBe(false)`.

The consequence is not a false negative, it is worse: **the day that test runs green, it is green
because the application leaks.** The defect the scenario exists to detect has become its pass
condition, and CI will hold that line indefinitely. When the application is eventually fixed, the
test turns red and reads as a regression to revert.

**Check, per test:** re-read the scenario's `Then` and the assertion side by side, and ask whether
they agree in *polarity*, not merely in subject. `is enabled` → `toBe(true)`. `is refused` → an
assertion of refusal. `no distinguishable signal` → an assertion of *sameness between two cases*,
which usually means the test must exercise both.

**Why generation produces it:** when a `Then` states a safe default rather than the observed
behaviour, generating against what the app *does* is the path of least resistance. That is exactly
the moment the book is telling you the app may be wrong.

### D6 — the ambiguity flag dropped on the way to the code

Found in three suites of five. A scenario the book marked `@low-confidence` or `# open: Q…` whose
generated test carries no trace of it — no tag, no comment, no `test.fixme`.

The severity is in what happens later. When that test goes red, the reader **cannot tell "the open
question just got answered" from "the product regressed"**, and the cheapest resolution is to align
the expected value with the application — silently converting a finding into a specification. On
one suite this was armed on the run's own most contestable call, a P1 with no retries.

**Check, per test:** if its scenario carries a flag in the book, the generated test must carry it
too — in the title, and in a comment saying the expectation is unconfirmed and that a failure is an
answer rather than a bug. Carrying it on a neighbouring test does not count.

`automation_score.py` now flags this as `flag-dropped`, blocking. Do not rely on the tool to catch
it: by the time it runs, the file is on disk.

### D7 — a test whose whole evidence is one-sided

Found in two suites. Every assertion in the test says only what the result *is not*:
`expect(status).not.toBe(200)`, or `expect(alertText.length).toBeGreaterThan(0)` for a scenario
demanding a specific alert **and** the absence of a success message — a string like
`"Product added"` has a length greater than zero, so the test passes against the forbidden
behaviour.

Two things make it worse than it looks. Such an assertion cannot distinguish the refusal *under
test* from any other refusal — on a target that refuses everything for an unrelated reason, it is
green by accident. And **a negative test whose positive control is red proves nothing**: if the
success path for the same endpoint is blocked or failing, the negative has no meaning at all.

**Check, per test:** assert the refusal itself and make it *attributable* — the error message
naming the field under test, the state that did not change, the record that was not created. If
the scenario also claims an absence (*"and no invoice is created"*), that clause needs its own
assertion; dropping it is D9.

### D8 — a literal with no provenance

Found in three suites. A status code, a message, an amount or a name asserted as expected without
any source: not in the `Then`, not in the user story, not in observed behaviour.

The dangerous case is not a wrong value, it is a *plausible* one that becomes load-bearing:
"checkout success is HTTP 200" appeared in no source, was never observed passing, and six other
tests asserted `not.toBe(200)` against it. An assumption had been promoted to a requirement in
silence.

**Check, per literal:** every concrete value traces to the book, the story, or something the run
actually observed. If it was chosen for automation — a timeout, a seeded name — say so in a comment
next to it. A comment that explains *why polling* is not provenance for *why 8000*.

### D9 — a claim in the report that the code does not support

Found in two suites. A run report listing a test project as *"actually used"* whose `testMatch`
matches no file on disk. A page object citing `see automation/NOTES.md` where no such file was
ever written. A traceability row reporting `PASS` for a scenario whose second `Then` clause was
never asserted.

Every one of these is a citation nobody follows, which is exactly why it survives: it looks
authoritative and costs nothing to write.

**Check, at step 8:** every artefact the report names must exist; every row marked covered must
correspond to assertions covering **all** the clauses of its `Then`; every project or configuration
described as used must have run something. `automation_score.py` catches the dead file citation as
`dead-citation` — the other two need you.

## Why these live here rather than only in the scorer

Three of the nine are now machine-checked, and the scorer runs *after* delivery. The other six need
the `Then` in front of you, which is only true during generation. A defect caught here costs a line;
the same defect caught by a judge costs a campaign, and caught by nobody costs the credibility of
every green run in the suite.

## On a hit — self-correct before writing

Derive the real assertion from the scenario's `Then` text — the concrete value, status or
visible state it names — using the page object or response already in scope, and replace the
trivial assertion.

**If the `Then` itself names no concrete, assertable value, do not fabricate a plausible-looking
check to fill the gap.** Leave the marker in the file:

```js
// TODO(automate): "<Then text>" has no concrete assertable value — needs a human
```

and list the scenario as **blocked-for-assertion** in the traceability report (step 8). Same
honesty posture as a scenario that cannot run at all: a gap that is visible costs one line in a
report, a gap papered over with a plausible assertion costs the credibility of every green run
in the suite.

## Validated against a purpose-built fixture

The lint is not asserted to work — it is demonstrated on a case built for it:

- `fixture/scenarios.feature` — the source scenarios;
- `fixture/generated-before.spec.js` — three deliberately injected violations;
- `fixture/generated-after.spec.js` — the same file with the self-review applied;
- `fixture/VALIDATION.md` — the worked example, and how each fix was mechanically checked.

### D10 — the fixture that invalidates the assertion

**The nine classes above all look at the assertion. None looks at what the fixture does to the
state the assertion reads.** A test can be perfectly written and still prove nothing, because its
own setup keeps re-establishing the condition it is meant to observe changing.

Measured on 2026-08-11, on a suite generated by this very skill against SauceDemo. The generator
seeded the cart declaratively with `addInitScript` — the right instinct, and the one the
testability precheck asks for. But `addInitScript` runs on **every navigation**, so it re-created
the cart the application had just emptied:

- one scenario went **red for a false reason** (the emptying worked; the fixture undid it);
- two others went **green while proving nothing** — the state they asserted had been re-imposed
  between the action and the check.

**Two false greens, produced by a correct-looking fixture, invisible to all nine classes above and
to the reviewer's own reading.** They were found by *running* the suite and looking at a failure
that made no sense.

What to check, before a spec reaches disk:

1. **Does any setup hook re-run after the action?** `addInitScript`, `beforeEach` with navigation,
   route handlers that replay a response — each re-applies state mid-test.
2. **For every scenario whose `Then` asserts an absence or a decrease** (cart emptied, item
   removed, counter back to zero): is there a fixture that could re-create what the action
   removed? That is the shape most exposed to this class.
3. **Does a green here mean the action worked, or that the fixture won?** If you cannot answer
   from the code, the test does not answer it either.

*This class exists because the other nine did not catch it. A lint that only reads assertions
certifies the half of the file that is easiest to get right.*

## The hard rule

**Never let a trivial assertion reach disk.** A spec file is not "done generating" until its
`expect(...)` calls have been re-scanned and each one either fixed or explicitly marked
blocked-for-assertion.
