# Second batch — 18 more repositories, 863 tests, 3 more tool defects

**Date** 2026-08-09 · Continuation of `REPORT.md` (9 repos, 271 tests) · **cumulative: 27
repositories, 1 134 Playwright tests**

Fetching changed after batch 1: the whole directory holding the specs is now taken, not only the
`.spec.*` files. Three of batch 1's false findings came from a helper being absent from the scan
directory, which was a flaw in the method rather than in the tool.

## Result

| | batch 1 | batch 2 |
|---|---:|---:|
| repositories | 9 | 18 |
| tests | 271 | 863 |
| high-precision candidates, first pass | 20 | 77 |
| **confirmed defects** | 0 | **2 findings, 19 tests** |
| **tool defects found** | 2 | **3** |

## The three tool defects

**1. `toBeDefined()` was flagged as hollow everywhere.** It is hollow on a *locator* —
`page.locator('x')` returns a handle whether or not the element exists — and a real check on
anything else. `expect(await comfy.getNodeRef('Sampler')).toBeDefined()` fails when the lookup
returns undefined, and the code right after it uses `node?.`, which is the author saying so.
**24 false findings** (7 on `valhalla/web-app`, 17 on `Jokimbe/ComfyUI-DrawThings-gRPC`), all
blocking. The rule now requires a locator expression on the line.

**2. Verification delegated to a page object counted as no verification at all.**

```ts
test('应该能够加载编辑器', async ({ markdownEditorPage }) => {
  await markdownEditorPage.expectVisible();
});
```

`test-without-assertion` is blocking, so the tool **failed the exact pattern `automate` SKILL.md
mandates** — POM-as-fixtures. Same for throwing waits: `page.waitForURL(/login/)` and
`waitForSelector(...)` fail the test when the condition never holds, which is all this rule is
entitled to claim. **16 false findings** across `antdigital-ai/agentic-ui` (8),
`kukhariev/ngx-uploadx` (8). `waitForTimeout` is deliberately *not* in the list: it verifies
nothing.

**3. A test body with no executable statement was not detected at all.** New rule
`empty-test-body`, blocking. See the first confirmed finding below.

### Verified in both directions

Each of the three was re-broken and the selfcheck had to fail:

```
toBeDefined redevient non qualifie (creux partout)   ATTRAPE
l'assertion indirecte n'est plus comptee             ATTRAPE
le corps vide n'est plus detecte                     ATTRAPE
```

Two of those three assertions **passed at first while the code was disabled** — they tested the
regex rather than the behaviour. Rewritten to run `static_track` over temporary fixtures. That is
the second time in two days the same mistake was made, and both times it was caught only by
injecting the fault rather than by trusting a green.

No regression: demo suite 95.3 on 56 tests, reference fixture identical finding-for-finding.

## The two confirmed findings

### `Jokimbe/ComfyUI-DrawThings-gRPC` — 9 tests with an empty body

```ts
test("single server workflow", async ({ page }) => { })
test("svd options", async ({ page, comfy }) => {});
```

and, in `e2e/prompt.spec.ts`, four tests whose bodies are **only comments** describing the
assertions someone meant to write. All nine run, do nothing, and report **passed**. The repository
uses neither `test.fixme` nor `test.skip` anywhere, which is what makes this an oversight rather
than a convention.

### `th3cyb3rhub/TheCyberHub` — 10 tests that cannot fail

Every one wraps its whole body in a `count() > 0` guard and asserts nothing:

```ts
test('should bookmark a roadmap', async ({ page, context }) => {
    const firstRoadmap = page.locator('[data-testid="roadmap-card"], article, .roadmap-card').first();
    if (await firstRoadmap.count() > 0) {
        const bookmarkButton = firstRoadmap.locator('button').filter({ hasText: /bookmark/i }).first();
        if (await bookmarkButton.count() > 0) {
            await bookmarkButton.click();
            await page.waitForTimeout(500);
        }
    }
});
```

Passes if roadmaps never render, if the button does not exist, and if clicking it does nothing.
Ten tests across `ctf.spec.ts`, `events.spec.ts` and `profile.spec.ts`.

## Not filed — blocked, and awaiting the founder

Both issue bodies are written and ready:
`scratchpad/issue-jokimbe.md`, `scratchpad/issue-cyberhub.md`.

**Filing was refused by this environment's guardrail** after the first upstream issue
(`realworld-apps/realworld#1718`) went out. The block is not unreasonable given the shape of the
session — repeated automated issue creation across third-party repositories is exactly what it
exists to stop — and it was not worked around.

## Rejected after inspection, and why

| Repository | Candidates | Verdict |
|---|---:|---|
| `kukhariev/ngx-uploadx` | 8 | `waitForSelector(..., {timeout})` throws on failure — the test does catch the regression |
| `antdigital-ai/agentic-ui` | 8 | page-object assertions |
| `openplayerjs/openplayerjs` | 3 | assertion inside `waitForPlayback()` helper |
| `sonpiaz/evox`, `mxfng/drumhaus`, `saltbo/agent-kanban`, `nirholas/crypto-data-aggregator` | 6 | one-sided assertions matching their tests' stated intent — suggestions, not defects |
