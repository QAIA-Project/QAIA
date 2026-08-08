# Issue filed with `realworld-apps/realworld` — PUBLISHED

Published on 2026-08-09 on the founder's explicit instruction, after being held back one turn for
that decision. The text below is what went out, verified against the live issue by
`eval/tools/gh_comment.py`, which re-reads from the API after posting.

**Filed as** https://github.com/realworld-apps/realworld/issues/1718
**Title** `e2e: "setting then clearing bio" asserts only what the bio is not, never what it is`

---

In `specs/e2e/null-fields.spec.ts`, the test `setting then clearing bio should not show stale data`
ends with two assertions that are both negative:

```js
const bioText = await page.locator('.user-info p').textContent();
expect(bioText?.trim()).not.toBe(testBio);
expect(bioText?.trim()).not.toBe('null');
```

Neither assertion pins down what the bio should be. The test passes if the profile page renders
`undefined`, `[object Object]`, an error message, or another user's bio — states the test's own name
says it exists to catch.

The sibling test a few lines above, `null bio should not render as literal "null" on profile page`,
already has the shape that closes this:

```js
expect(bioText?.trim()).not.toBe('null');
expect(bioText?.trim()).toBe('');        // the positive assertion
```

Suggested fix, one line:

```js
expect(bioText?.trim()).not.toBe(testBio);
expect(bioText?.trim()).toBe('');
```

Since these specs are the shared conformance suite, an implementation that leaves stale bio text in
place — anything other than the cleared value — currently passes this test.

Found while running a static analysis of assertion shape over the suite; happy to open a PR if
useful.

---

## Notes for the founder, not for the issue

- The finding was verified by reading the file, not only from the tool's output.
- It is a **test-quality** issue, not a product bug: no claim is made that any RealWorld
  implementation is broken.
- Tone is deliberately plain and offers a PR rather than asserting one is owed. No mention of QAIA
  by name — the finding should stand on its own, and a first contact that reads as promotion is
  worth less than one that reads as help.
