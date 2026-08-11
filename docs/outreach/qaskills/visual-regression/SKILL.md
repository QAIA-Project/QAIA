---
name: Visual Regression Baselines
description: Playwright screenshot tests scoped to stable containers with an explicitly chosen tolerance, dynamic content frozen rather than masked, and a first run treated as baseline creation. Use when screenshot tests need to survive a second week — an unstated tolerance and a first run counted as green are why most visual suites get deleted.
version: 1.0.0
author: opaland
license: MIT
tags: [visual-regression, screenshots, playwright, baselines, ui]
testingTypes: [visual, e2e]
frameworks: [playwright]
languages: [typescript, javascript]
domains: [web]
agents: [claude-code, cursor, github-copilot, codex]
---

# Visual Regression

> **Standalone adaptation.** Self-contained version of the `visual-check` skill from
> [QAIA](https://github.com/QAIA-Project/QAIA) (MIT). QAIA is pre-alpha and says so.

## 1. One snapshot per key screen, with the tolerance stated

```js
await expect(locator).toHaveScreenshot('<screen>.png', { maxDiffPixelRatio: 0.002 });
```

**That number decides pass or fail, so it is stated rather than left blank.** `0.002` — 0.2 % of
pixels — absorbs anti-aliasing and font-hinting differences between runs on the same machine
without hiding a real change: a moved button, a wrong colour or a shifted layout each move far
more than 0.2 % of a screen.

Raise it only with a stated reason — a target rendering text differently across OS versions, say
— and **never to make a failing test pass**. Prefer masking or freezing the unstable region. If a
screen genuinely needs a different tolerance, record **which screen and why**.

## 2. The first run is not a pass

The first run **creates** the baselines. It will report failures, and that is correct behaviour,
not a problem to work around.

**State this explicitly in the report.** A reader who sees only the green second run learns the
wrong thing about what a first run means. Commit the baselines deliberately, after looking at
them — they are now the definition of correct.

## 3. Scope each snapshot to a stable container

A container, not the whole viewport. Whole-page snapshots fail on a footer counter and teach the
team to raise the tolerance.

## 4. Freeze dynamic content — do not rely on tolerance

**An unmasked dynamic region is not only a flake risk: it silently eats the tolerance budget.**

An unmasked clock changes real pixels on every run and can still stay under `maxDiffPixelRatio`
and pass — **not by protection, by luck of the margin**. It passes today and absorbs the budget a
real regression would need tomorrow.

**Prefer freezing to masking.** A frozen value — a fixed date filled into the field, a seeded id —
gives an exact, provable **0-pixel** diff. A mask only hides the region, and what is hidden is no
longer checked.

Reset or seed the data before each snapshot, and set `workers: 1` against a shared mutable target.

## 5. Baselines are platform-specific

Playwright writes `*-linux.png`, `*-win32.png`, `*-darwin.png`. **Generate them in the same
environment CI runs, or the diff is meaningless.** If your baselines are `-win32` and CI is Linux,
the honest move is to say the visual project is not wired into CI rather than to ship a
comparison that cannot mean anything.

## 6. Tag, run, and report real diffs

Tag `@VIS-<NNN>`. A diff is a **finding for a human to accept or reject** — never suppressed to
force green.

## Prove the snapshots can fail

Snapshots that pass are worthless as evidence unless something shows they can fail. Mutate the
application deliberately — change a primary colour, add 3 px of padding — and check which
snapshots go red. **Report it per mutation rather than as one aggregate number**, because the
useful result is *which* snapshots reacted:

> Measured on a real suite of six snapshots: a button-colour change killed **5 of 6** — the
> survivor scoped a list containing no button. A `.card` padding change of ~3 px killed **2 of 6**
> — the only two scoping card lists.

Each mutation caught by exactly the snapshots whose scope contains the mutated element, and by no
others. That is the property scoping is supposed to have, and a summed "kill rate" would hide it.

The subtle mutation matters more than the colour one: **3 pixels of padding is what a human
reviewer waves through and no functional test can see.**

## Guardrails

- **Never suppress a real visual diff to force green.**
- **Determinism first.** A flaky visual test is worse than none — it trains people to ignore red.
- **Web-first.** Mobile visuals are browser-emulation screenshots via device descriptors, never
  native captures, and must be reported as such. **A device-emulated screenshot is not evidence
  about a native app.**
