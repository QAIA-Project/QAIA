# qaia-score skills — scoring only

One portable skill, `judge`, that **scores, and only scores**. It reads the QAIA artifacts (or
anyone else's test book or Playwright suite) and the standardized run manifest
(`../OUTPUT-CONTRACT.md`, D39), produces a verdict, and writes it back into the manifest's
`structural` and `gate` blocks. It never generates, edits, or deletes a scenario — the
producer/consumer separation is the point: **no plugin scores itself** (qaia-core shared
contract, rule 3), so the judgment lives in a separate plugin.

Its pages, under `judge/references/` (each was a separate skill until 2026-08-24):

```
auditing-a-test-book.md   audit any Gherkin book, QAIA or not            (was testbook-validate)
scoring-testbook.md       the 10-dimension ISTQB rubric, /20, + top-3 fixes (was testbook-score)
scoring-automation.md     generated Playwright code: static + mutation pass (was automation-score)
spec-vs-suite.md          an OpenAPI spec against the suite that covers it (was spec-suite-drift)
release-gate.md           PASS / CONCERNS / FAIL / WAIVED over score + hard gates (was aptitude-gate)
```

## What "scoring only" means (guardrails shared by every page)

1. **Read-only over content.** The only file `judge` writes is `.qaia/reports/<US-ID>/manifest.json`,
   and only its `structural` and `gate` blocks. `.feature` files, checkpoints, synthesis and matrix are inputs,
   never outputs. If a fix is needed, the skill *names* it (top-3, gate reasons) and hands
   back to `qaia-core` — it does not apply it.
2. **Evidence, not vibes.** Every dimension score and every gate reason cites the artifact it
   came from (a scenario ID, a matrix row, a manifest count). A score without a one-line
   justification is invalid (rubric protocol).
3. **Fresh eyes.** The rubric is meant to be applied without the generation session's context
   (LLM-judge protocol). When scoring a book this session generated, say so — a self-review is
   weaker evidence than a fresh-session judge, and the skill flags that limitation rather than
   hiding it.
4. **Default low, be honest.** When hesitating between two scores, take the lower one. Never
   inflate a verdict to be encouraging; never fabricate an execution result. `simulated` and
   `[open]` items pending human arbitration cap the verdict at CONCERNS until resolved.
5. **Portable.** No network, no API key, no server. The deterministic passes are the pinned Python
   scorers shipped in `../scripts/`, run in the user's session only when `judge` is invoked; the
   rest is Markdown and JSON. On a surface without file tooling, the scorecard and the `gate`
   object are emitted as fenced blocks for the user to save.
6. **The human owns WAIVED.** A gate is never self-waived. Only a recorded human decision
   (`by`, `reason`, `at`) turns a CONCERNS/FAIL into WAIVED — the skill writes down the waiver,
   it does not grant it.

## Where the manifest comes from

`qaia-score` consumes the envelope that `qaia-core:generate` (design, step 8) and
`qaia-playwright:automate` (execution) produced. If no manifest exists yet, `judge` says
so and offers to run `generate`'s step 8 (the run manifest) first — they never score against guessed counts.
