# The negative ratio: reported, never a gate

## The single definition

- **Numerator** — executable cases tagged `@negative`.
- **Denominator** — all generated executable cases.
- A `Scenario Outline` counts as **N cases** for N `Examples` rows — the denominator the output
  contract fixes for every ratio.
- The `@smoke` journey scenario is **excluded** from both.

> **Corrigé le 2026-08-11.** Ce paragraphe disait « scenario **blocks** » et « a `Scenario Outline`
> counts as **1 block** », pendant que [`docs/OUTPUT-CONTRACT.md`](https://github.com/QAIA-Project/QAIA/blob/main/docs/OUTPUT-CONTRACT.md) tranchait
> l'inverse le 2026-08-10, explicitement : *« `total` = les cas exécutables … tout ratio (négatif,
> confiance) se calcule sur ce dénominateur »*. Deux sources pour une règle, et elles avaient
> divergé — sur le cahier `booking-api-demo` l'écart valait 0,63 contre 0,61. Le contrat arbitre,
> parce que c'est lui que le validateur exécute. Trouvé en calculant le ratio d'un vrai cahier
> plutôt qu'en relisant les deux textes.

Boundary coverage is reported **separately** in the synthesis and never blended into this ratio.

## What actually blocks

The gate is **ADR 0001**, the required negative-path coverage rule: every refusal, error or
denial path identified as `[req-neg]` in `03-design.md` has a covering scenario, or an explicit
user-approved waiver.

**And the covering scenario carries the condition's level** ([ADR 0008](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0008-test-level-is-a-design-property.md), 2026-08-11).
A `[req-neg]` condition marked `[level: api]` is covered by an `@api` scenario; a `@e2e` scenario
displaying an error message does not discharge it, because the refusal was promised in the
contract and nothing exercised it there. This is not a second gate and it cannot be padded — it
adds no number and no threshold. It closes the one way the existing gate could be satisfied
without verifying the promise it exists to protect.

The ratio is a **happy-path-bias signal**, nothing more. 40 % is the indicative order of
magnitude a healthy book usually lands on — an observation, not a bar.

The two cases that make the distinction concrete:

- A book at **30 %** with every `[req-neg]` condition covered is **fine**.
- A book at **50 %** with one `[req-neg]` missing is **not**.

## Why this is spelled out so insistently

The ratio is the one number a reader instinctively converts into a target. The moment it becomes
a bar to clear, it creates pressure to pad it with invented cases — which the generation rules
forbid outright, and which produces the exact defect the book exists to avoid: scenarios that
test nothing the source ever required, written to move a percentage.

A padded ratio is worse than a low one. A low ratio is a visible signal that someone can act on.
A padded ratio is the same signal, hidden, with fabricated scenarios attached.

`../../../OUTPUT-CONTRACT.md`, [`eval/RUBRIC.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/RUBRIC.md) and `istqb-design` all state the same thing:
reported, never a threshold. If you find yourself reasoning about how to *reach* a ratio, the
reasoning itself is the error.

## `@negative` — the closed definition

A scenario whose outcome is **a refusal, an error, or an explicitly denied access**.

List-exclusion and filtering scenarios are **not** `@negative`. A search returning no results, a
filter hiding rows, a paginated list ending — these are normal outcomes of a working feature, not
refusals. Counting them is the most common way a ratio inflates without anyone intending to
cheat.

## Two recomputation rules

1. **Re-check after any scenario merge.** The ratio is measured on the final block set, so a
   merge changes it: recompute and report the new figure, never the pre-merge one. What must be
   re-checked as a *gate* is the `[req-neg]` checklist — a merge that drops a required-negative
   scenario is blocking, whatever the resulting percentage.
2. **Tag-versus-ratio audit.** The `@negative` count used in the reported ratio must equal a
   **literal count of `@negative` tags in the emitted `.feature` file.** A scenario counted in
   the numerator without the tag physically present is an emission error, not a rounding nuance:
   fix the tag or fix the reported ratio before showing the synthesis.

   Applying the closed definition in your head tells you what a scenario *is*; only reading the
   emitted file tells you what it *says* — and everything downstream (the manifest, the score,
   the export) counts tags, not intentions.

## Priority-scoped waivers are not gate violations

A `[req-neg]` condition left at P3 by the scope the user chose in step 1 is a **standing,
priority-scoped waiver** — provided it still appears in the coverage matrix and synthesis with
its condition ID and the reason (`deferred, P3, not requested`) rather than vanishing from the
count.

Only a **P1/P2** `[req-neg]` condition with no scenario and no cited reason is a real gate
failure.

The distinction matters because the gate and step 1's scope default otherwise read as
contradicting each other on any US whose `[req-neg]` conditions span more than one priority
band. The rule is short: **a scope the user chose is not a violation; a condition that silently
disappeared is.**
