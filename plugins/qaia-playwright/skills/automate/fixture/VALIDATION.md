# automate self-review lint — validation (issue #41, 2026-07-25)

Honest record of validating the step 5 self-review added to `../SKILL.md` against a
purpose-built case, following the same fixture discipline as
`flaky-detect`'s fixture (that skill was deleted on 2026-10-26; its record is in git history).

## What was built

- `scenarios.feature` — 3 minimal scenarios (not a real product US), each with a
  concrete, assertable `Then`, chosen so the "naive" generation below can be made to
  violate exactly one of step 5's three flagged classes per scenario.
- `generated-before.spec.js` — a **deliberately naive** generation output: syntactically
  valid Playwright (`node --check` passes), each test built to demonstrate one violation:
  - `@QAIA-FIXTURE-041-001`: **tautological/reflexive comparison** —
    `expect(true).toBe(true)` in place of the concrete refusal message the `Then` names.
  - `@QAIA-FIXTURE-041-002`: **weak-by-construction matcher** —
    `expect(cancelBtn).toBeDefined()` on a `getByRole()` locator handle, which is always
    a defined object regardless of whether the button is actually visible/enabled
    (Playwright locators are lazy) — proves nothing about the `Then`.
  - `@QAIA-FIXTURE-041-003`: **silent zero-assertion block** — the action runs
    (`filterBy('dermatology')`) but no `expect(...)` follows, dropping the coverage the
    scenario's `Then` promised.
- `generated-after.spec.js` — the same three tests with step 5's self-review applied:
  each trivial/missing assertion replaced by one derived from its scenario's `Then`,
  reusing the page-object API already established in [`examples/medibook/tests/e2e.booking.spec.js`](https://github.com/QAIA-Project/QAIA/blob/main/examples/medibook/tests/e2e.booking.spec.js)
  (`bookingPage.message`, `bookingPage.slots`, `bookingPage.appointments`) rather than
  inventing a new one.

## What was actually checked (mechanical, not narrated)

1. **Syntax**: `node --check` on both files — both parse cleanly (real command run,
   output captured, not asserted from memory).
2. **The violations are real code, not just described in comments** — grepped
   `generated-before.spec.js` for `expect(true).toBe(true)` and `toBeDefined()`: both
   hits land on live statement lines (17 and 28), not inside a comment.
3. **The fixes are real code, not just described in comments** — the same grep against
   `generated-after.spec.js` returns **zero** live-code hits for either pattern; the only
   occurrences are inside `// Was: ...` explanatory comments.
4. **The zero-assertion violation and its fix, counted precisely** — a small Node script
   isolated the `@QAIA-FIXTURE-041-003` test body in each file, stripped `//` comments
   (the first pass without stripping comments false-positived on the word "expect(...)"
   inside the explanatory comment itself — a real miss worth recording, not smoothed
   over), then counted real `expect(` call sites:
   - `generated-before.spec.js`: **0** real assertions in that test body.
   - `generated-after.spec.js`: **2** real assertions in that test body
     (`toHaveCount(1)` for dermatology present, `toHaveCount(0)` for cardiology absent —
     both halves of "only dermatology slots are displayed").

## Applying step 5's method (SKILL.md) to this data

| Scenario | Violation class (step 5 bullet) | Before | After | Derived from |
|---|---|---|---|---|
| FIXTURE-041-001 | tautological comparison (bullet 1) | `expect(true).toBe(true)` | `expect(bookingPage.message).toContainText('less than 4 hours')` | `Then` names the exact string |
| FIXTURE-041-002 | weak-by-construction matcher (bullet 3) | `expect(cancelBtn).toBeDefined()` | `expect(cancelBtn).toBeVisible()` + `.toBeEnabled()` | `Then`: "visible and enabled" |
| FIXTURE-041-003 | silent zero-assertion block (bullet 4) | *(no expect)* | `toHaveCount(1)` dermatology / `toHaveCount(0)` cardiology | `Then`: "only dermatology slots are displayed" |

Each fix reuses a value or state the `Then` text names explicitly — none of the three
corrections required inventing a plausible-looking check the scenario didn't already
specify, which is the honesty condition step 5 sets for when a fix is safe to make
automatically (vs. leaving a `// TODO(automate): ...` marker and reporting the scenario
blocked-for-assertion, for a `Then` that names nothing concrete).

## Honest limitation

`../SKILL.md` step 5 is a **behavioral instruction for the generating agent**, not a
standalone executable linter shipped with the plugin — there is no `lint.py` this
validation ran against, unlike [`eval/tools/structural_score.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/structural_score.py) for the Gherkin layer.
This validation therefore hand-applies the three bullet patterns to a constructed case
(same posture flaky-detect's fixture used: hand-apply the documented method to real,
inspectable data) and verifies mechanically (grep + a counting script, not narration)
that the violating code is genuinely present in `generated-before.spec.js` and genuinely
absent from `generated-after.spec.js`. It demonstrates the method is well-specified and
discriminates correctly on a case built to exercise it; it is not a claim that every
future `automate` run will catch every trivial assertion a model could produce — the
same caveat any instruction-only (non-code) gate carries.

## Result

All three deliberately injected violations (tautological comparison, weak-by-construction
matcher, silent zero-assertion block) are distinguishable from their corrected form by
mechanical inspection (grep, syntax check, assertion count), and each correction is
traceable to concrete text in the scenario's `Then` rather than fabricated. This matches
the intended behavior of `SKILL.md` step 5.

## Extended 2026-08-08 — three measured classes, and two defects the extension found

The fixture originally exercised the three trivial-assertion classes. Five more classes were
added to the lint after five blank-context judges applied
[`eval/AUTOMATION-RUBRIC.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/AUTOMATION-RUBRIC.md)
to five real generated suites — none of which passed its gate. Three of those five are visible to
a static reader, so they belong here:

| Scenario | Defect committed in `generated-before` | Fixed in `generated-after` |
|---|---|---|
| `041-004` | **D5** — asserts `toBe(false)` where the `Then` demands the field be *enabled, the same as for a registered address*: the inverse. Plus **D6** on the same test — the book flags the scenario as resting on an open question, the code says nothing | Polarity restored, and the test now exercises **both** cases because the `Then` claims *sameness*. Flag carried in the title and in a comment saying a failure is the answer arriving, not a regression |
| `041-005` | **D7** — sole assertion `not.toBe(200)`, and the `Then`'s second clause (*no cancellation appears in the history*) never asserted | Status and error message asserted so the refusal is attributable to the field under test, plus the absence clause |

### Discrimination, measured

```
before  {hollow-assertion: 2, test-without-assertion: 3, flag-dropped: 1, single-sided-evidence: 1}
after   {}
```

Every class fires on the naive file and **nothing at all fires on the corrected one**. The second
half is the half that matters: a lint that flags both files discriminates nothing.

### Two defects the extension found in the project's own tooling

Neither was the point of the exercise, and both were there before today.

1. **`automation_score.py` matched assertion patterns inside `//` comments.** `generated-after`
   documents each fix with a line like `// Was: expect(true).toBe(true)` — and was reported as
   containing two hollow assertions *because it explains what it fixed*. Any suite that documents
   its own corrections was being penalised for the documentation. Comments are now stripped before
   pattern matching (block comments and `//` inside string literals are deliberately left alone:
   the cheap version is right far more often, and a clever parser that mangles a URL is worse).
2. **This fixture's own header cited `../VALIDATION.md`**, one directory too high — the file is
   `./VALIDATION.md`. Written long before today, never noticed, and caught on the first run of the
   `dead-citation` check by the tool it was added to. A citation looks authoritative precisely
   because nobody follows it.

### What the fixture still cannot show

**D8** (a literal with no provenance) and **D9** (a report claiming what the code does not support)
are not committed here. Both need context this fixture does not carry — the source a literal should
trace to, and the run report itself. They stay judge-only, and that is stated rather than papered
over with a case that would only look like a demonstration.
