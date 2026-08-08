# QAIA pointed at a suite it did not write — `gothinkster/realworld`

**Date** 2026-08-09 · **Target** [`gothinkster/realworld`](https://github.com/gothinkster/realworld) `specs/e2e` (13 spec files, 128 tests, 84k stars) · **Tool** `eval/tools/automation_score.py`, static track only

## Why this target

RealWorld publishes a specification (`specs/api/openapi.yml`) *and* a shared Playwright conformance
suite that every implementation is expected to pass. That makes it the first external material this
project has had where the requirement and the automation both exist, in writing, from someone else.

Nothing was run against a hosted instance. The static track reads files; no third-party host was
contacted, probed or load-tested.

## What happened on the first run: it crashed

`--testbook` is documented as optional. Omitting it raised `ValueError: not enough values to unpack`
before a single line was scored. `collect_feature_ids` had gained a second return value and its
early return had not followed:

```python
if not testbook:
    return ids          # one value; the caller unpacks two
```

The tool had **only ever been run on QAIA's own output**, which always carries a test book. The very
first foreign suite took the untaken path immediately.

## What happened on the second run: 428 findings, one of them real

| Rule | Count | Verdict |
|---|---:|---|
| `fragile-selector` | 279 | **False positive.** RealWorld ships `specs/e2e/SELECTORS.md`, a *published contract* of every CSS class and `name` attribute an implementation must provide. Those selectors are the interface, not an accident. |
| `untraceable-test` | 128 | **Not applicable.** Fires when a test carries no `@QAIA-<ID>`. There is no QAIA test book, so every test in any foreign suite trips it. |
| `pom-missing` | 1 | **Not applicable.** Its own message cites "automate SKILL.md mandates" — QAIA's internal convention, applied to a third party. |
| `weak-assertion` | 11 | True per assertion, not a defect. Each `not.toBeNull()` inspected is a precondition followed by a real value assertion (`settings.spec.ts:52` → `.toBe(user.username)`). |
| `forbidden-wait` | 8 | Real but minor; `waitForTimeout` is discouraged by Playwright's own documentation. 6 of the 8 are in `xss-security.spec.ts`. |
| `single-sided-evidence` | 1 | **Confirmed defect.** See below. |

**1 real finding out of 428.** The other 427 are noise, and 408 of them are noise *by construction*.

### The confirmed defect — `specs/e2e/null-fields.spec.ts:117`

```js
test('setting then clearing bio should not show stale data', async ({ page, request }) => {
  ...
  const bioText = await page.locator('.user-info p').textContent();
  expect(bioText?.trim()).not.toBe(testBio);
  expect(bioText?.trim()).not.toBe('null');
});
```

Both assertions are negative. The test never asserts what the bio *is*. It passes if the profile
renders `undefined`, `[object Object]`, an error string, or another user's bio — every failure mode
the test exists to catch, except the two spelled out.

The sibling test four lines above does it correctly:

```js
expect(bioText?.trim()).not.toBe('null');
expect(bioText?.trim()).toBe('');        // <- the positive assertion, present here
```

One line fixes it: `expect(bioText?.trim()).toBe('');`

Same defect class as the `assert.ok(skills.length >= 29)` corrected in this project's own
`mcp-bridge` on 2026-08-08 — an assertion that constrains what a value is not, while the thing it
should pin down stays free.

## The finding that matters more, and it is about QAIA

The suite scored **30.0/100**. It had earned **30.0 out of the 30 points it could possibly earn.**

Three of the four budget lines encode QAIA's conventions: `pom_as_fixtures` (20) and `traceability`
(25) are mandated by `automate` SKILL.md, and `robust_selectors` (25) assumes CSS locators are
incidental. A mature third-party suite forfeits 70 points for reasons that are not defects, and the
resulting number reads as a quality verdict on someone else's work.

**Pointing QAIA at an existing suite is the most obvious thing a new user would try, and until today
it crashed — then, once fixed, returned a number that was false and 427 findings that were wrong.**

### Fix

`--third-party` rescales the budget onto the dimension that transfers and reports the other three as
**excluded, never scored zero** — a zero would read as a failing grade for declining to adopt our
conventions. The same idiom the tool already used for "no selector found: not applicable, not
penalised, said out loud".

| | findings | score |
|---|---:|---|
| default mode | 428 | 30.0/100 |
| `--third-party` | 21 | 100.0/100 (assertion substance, 128/128 tests) |

### Verified in both directions

A hollow assertion injected into `health.spec.ts` — the mode must not suppress real defects:

```
score    : 99.2
blocking : failed=True
  hollow-assertion: expect(true).toBe(true) (health.spec.ts:40)
  test-without-assertion: injected: decorative assertion... (health.spec.ts:38)
```

Blocking rules keep firing. Only the three convention rules are silenced.

Both defects are locked by assertions in `eval/tools/selfcheck_automation_score.py`. Reverting the
`collect_feature_ids` fix makes the selfcheck fail (`got: 0, want: 2`) — checked, not assumed.

## Honest limits

- **Static track only.** The mutation track needs the application running; RealWorld's suite targets
  a local frontend+backend pair that was not stood up.
- **`openapi-ingest` was not exercised.** `specs/api/openapi.yml` (24.9 KB) remains the obvious next
  target and would be the first external test of a skill written on 2026-08-08 and never used since.
- **The confirmed defect was not reported upstream.** Opening an issue on a third-party repository is
  the founder's call, not this tool's.
