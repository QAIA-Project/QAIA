# qaia-score skills — scoring only

Four portable skills that **score, and only score**. They read the QAIA artifacts and the
standardized run manifest (`../OUTPUT-CONTRACT.md`, D39), produce a verdict, and write it
back into the manifest's `gate` block. They never generate, edit, or delete a scenario — the
producer/consumer separation is the point: **no plugin scores itself** (qaia-core shared
contract, rule 3), so the judgment lives in a separate plugin.

```
testbook-score   quality score — the 10-dimension ISTQB rubric, /20, + top-3 fixes
aptitude-gate    release readiness — PASS / CONCERNS / FAIL / WAIVED over score + hard gates
```

## What "scoring only" means (guardrails shared by both skills)

1. **Read-only over content.** The only file these skills write is `.qaia/reports/<US-ID>/manifest.json`,
   and only its `gate` block. `.feature` files, checkpoints, synthesis and matrix are inputs,
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
5. **Portable.** No network, no API key, no runtime. The skills read markdown + JSON and write
   JSON. On a surface without file tooling, they emit the scorecard and the `gate` object as
   fenced blocks for the user to save.
6. **The human owns WAIVED.** A gate is never self-waived. Only a recorded human decision
   (`by`, `reason`, `at`) turns a CONCERNS/FAIL into WAIVED — the skill writes down the waiver,
   it does not grant it.

## Where the manifest comes from

`qaia-score` consumes the envelope that `qaia-core:report` (design) and
`qaia-playwright:run-report` (execution) produced. If no manifest exists yet, the skills say
so and offer to run `report` first — they never score against guessed counts.
