Ten e2e tests wrap their entire body in an `if (await locator.count() > 0)` guard and make no assertion. They pass when the element they look for is absent, so they cannot fail — including when the feature they are named after is broken or missing.

`e2e/profile.spec.ts:267`:

```ts
test('should bookmark a roadmap', async ({ page, context }) => {
    await page.goto(`${BASE_URL}/roadmaps`);
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

This passes if roadmaps never render, if the bookmark button does not exist, and if clicking it does nothing. It never checks that a bookmark was created.

The same shape appears in:

| File | Line | Test |
|---|---|---|
| `e2e/ctf.spec.ts` | 35 | should filter challenges by difficulty |
| `e2e/ctf.spec.ts` | 104 | should show validation for empty flag submission |
| `e2e/ctf.spec.ts` | 256 | should show loading indicator during filter changes |
| `e2e/events.spec.ts` | 26 | should filter events by category |
| `e2e/events.spec.ts` | 148 | should show confirmation after RSVP |
| `e2e/events.spec.ts` | 199 | should navigate between months |
| `e2e/profile.spec.ts` | 217 | should display bookmarks page |
| `e2e/profile.spec.ts` | 267 | should bookmark a roadmap |
| `e2e/profile.spec.ts` | 290 | should remove bookmark |
| `e2e/profile.spec.ts` | 362 | should access settings page |

Two options depending on intent:

- If the element is expected to exist, drop the guard and assert — `await expect(bookmarkButton).toBeVisible()` then assert the state after the click. A missing element then fails, which is the point.
- If it is genuinely optional, `test.skip(await firstRoadmap.count() === 0, 'no roadmap rendered')` reports as skipped rather than passed, so the dashboard stops showing green for something that was never exercised.

Found with a static analysis of assertion shape across the suite; happy to open a PR if useful.
