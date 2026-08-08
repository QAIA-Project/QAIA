Nine e2e tests have an empty body — either literally `{}` or nothing but comments. They run, do nothing, and report **passed**, so the run shows green for features that are not exercised at all.

`e2e/models.spec.ts:107`:

```ts
test("single server workflow", async ({ page }) => { })

test("multiple server workflow", async ({ page }) => { })
```

`e2e/prompt.spec.ts:3`:

```ts
test("prompts colors", async ({ page }) => {
    // load prompt workflow
    // assert prompt node is uncolored
    // connect to positive, assert green
    // disconnect, assert uncolored
    ...
})
```

The full list:

| File | Line | Test |
|---|---|---|
| `e2e/models.spec.ts` | 107 | single server workflow |
| `e2e/models.spec.ts` | 109 | multiple server workflow |
| `e2e/models.spec.ts` | 169 | lora model filtering |
| `e2e/models.spec.ts` | 181 | multiple lora node filtering |
| `e2e/prompt.spec.ts` | 3 | prompts colors |
| `e2e/prompt.spec.ts` | 21 | prompts colors option |
| `e2e/prompt.spec.ts` | 39 | textual inversion insertion/removal |
| `e2e/prompt.spec.ts` | 51 | textual inversion options |
| `e2e/widgets.spec.ts` | 210 | svd options |

`test.fixme()` is Playwright's mechanism for exactly this: the test is reported as **skipped** with its name preserved, so the intent stays visible in the file and in the report without counting as a pass.

```ts
test.fixme("single server workflow", async ({ page }) => { })
```

The repository currently uses neither `test.fixme` nor `test.skip` anywhere, so this looks like an oversight rather than a deliberate choice.

Found with a static analysis of assertion shape across the suite; happy to open a PR if useful.
