---
name: automation-score
description: Score QAIA-generated Playwright test code on two separate tracks - a deterministic static pass plus a mutation pass that inverts each assertion and requires it to go red, then a 6-dimension LLM rubric for what no machine can see. Read-only over code - it judges, it never edits. Use to review generated automation before it is trusted, or to check whether a suite's assertions are load-bearing at all.
---

# automation-score — the judge of generated test code

Applies to the Playwright code produced by `automate` (and its siblings `a11y-audit`,
`contract-probe`, `security-surface`) for **one** test book. It **scores only** — see the
scoring-only guardrails in `../README.md`.

**Why this skill exists.** Generated code was, for most of this project's life, the only QAIA
output reviewed solely by its own producer — `automate`'s self-review step — in direct exception
to rule 3, *a producer plugin never grades its own output*. The two defects a campaign found in
generated code (a missing blocking assertion; page-objects-as-fixtures bypassed) are exactly the
class of defect no judge was looking for. This skill is that judge.

## The three tracks, and why they are never summed

| Track | Answers | Can it be automated? |
|---|---|---|
| **Static** | Is the code shaped the way the rules require? | Fully — counts and patterns |
| **Mutation** | Is each assertion *load-bearing* — can it fail at all? | Fully — needs a runnable suite |
| **LLM rubric** | Does it assert **the right thing**? | No — this is the judgment call |

**Never add these numbers together.** A perfect static score does not make the code faithful; a
high rubric score does not cancel a blocking mutation survivor. Same separation, same reason, as
structural score versus rubric on the test book side: one measures form, the other substance, and
averaging them hides whichever is worse.

## Prerequisites

- The generated test directory (`*.spec.js`, `pages/`, `fixtures.js`, `playwright.config.js`).
- The source test book — `.feature`, `coverage-matrix.md`, `synthesis.md`. Without it, tracks 1
  and 2 still run; the rubric's fidelity dimensions cannot be scored, and you say so rather than
  scoring them anyway.
- For the mutation track only: a runnable suite (dependencies installed, target reachable).

> **Ce que cette skill ne peut pas promettre.** L'algorithme ci-dessous est **rejoue par le
> modele a chaque invocation**, pas charge depuis un fichier fige : deux passages sur le meme
> fichier peuvent diverger, et la note n'est pas comparable d'une semaine a l'autre. C'est le
> prix de l'ADR 0002 (aucun code livre dans les plugins), et il est assume -- mais il doit etre
> dit ici, pas seulement dans le depot. **Pour une note reellement deterministe et diffable,
> lancez l'outil fige du depot QAIA** plutot que cette skill. Releve par une revue
> « developpeur » independante le 2026-08-09.

## Track 1 — Static pass (deterministic, run first)

**In Claude Code**: materialize a throwaway script implementing the algorithm below and **run
it**, for true determinism. The script is generated in-session and never shipped — QAIA stays
100 % skill ([ADR 0002](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0002-code-and-optin-tier.md)). The maintainer's reference implementation is
[`eval/tools/automation_score.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/automation_score.py), which **lives in the QAIA source repository, not in the
installed plugin** — do not send a user looking for it in their own project.

**Without code execution**: apply the algorithm by hand and say so — it is weaker than running it.

**Budget /100:**

| Component | Points | Measured as |
|---|---:|---|
| Substantive assertions | 30 | share of tests containing at least one assertion on real SUT state |
| Robust selectors | 25 | `getByRole`/`getByTestId` versus raw CSS/XPath selectors |
| POM-as-fixtures | 20 | specs import the fixtures rather than driving `page` directly |
| Traceability | 25 | tests carrying a `@QAIA-<US>-<NNN>` tag, and test book scenarios having a test |

**Findings that are blocking regardless of score:**

- a test whose scenario has a `Then` but whose body contains **zero** assertions;
- a tautological or contentless assertion (`expect(true).toBe(true)`, a literal compared to
  itself);
- `.toBeDefined()` / `.not.toBeNull()` on a locator handle — always truthy, since locators are
  lazy;
- a forbidden fixed wait (`waitForTimeout`) standing in for a real condition;
- **a scenario the test book flagged as resting on an open question (`@low-confidence`,
  `# open: Q…`) whose test carries no trace of the flag.** The severity is not in the code, it is
  in what happens the day that test goes red: the reader cannot tell *the open question just got
  answered* from *the product regressed*, and the cheapest resolution is to align the expected
  value with the application — silently converting a finding into a specification.

**Findings reported but never blocking** — these are shape facts handed to a human or to the LLM
rubric, because deciding whether they matter needs the specification, which a static pass has not
read:

- **every assertion in a test being one-sided** (`not.toBe(x)`, `length > 0`): the test cannot
  distinguish the refusal under test from any other refusal, nor from the forbidden behaviour
  returning a different value. Only report it when *all* assertions in the test are one-sided —
  a test that asserts `not.toBe(200)` and then reads the error body has the attributable evidence.
- **a comment or report citing a file that does not exist**: a citation looks authoritative
  precisely because nobody follows it.

Report `scenarios_without_test` separately: a scenario the book demanded and the code never
automated is a coverage gap, not a code-quality one, and blending them hides it.

## Track 2 — Mutation pass (the one that proves assertions can fail)

For each assertion, **invert its expected value**, re-run the owning test, and require it to go
**RED**. An assertion that survives its own inversion is decorative: it cannot fail, so it tests
nothing.

- **The mutation is applied to the TEST, never to the system under test.** This is what makes the
  track usable against any target — including public sites nobody owns — and keeps the score
  comparable between runs. Never mutate the SUT.
- **Survivors are blocking.** Report each with `file:line` and the inversion applied.
- If the suite cannot run, report `mutation.status = blocked` and say plainly that **the
  assertions have not been shown to be load-bearing.** Do not let a good static score stand in
  for it, and do not present the run as scored. The same sentence is owed for **any** state that
  is not a completed mutation run — `skipped`, or the field missing altogether. `skipped` is the
  weaker of the two, not the safer one: `blocked` means it was attempted and could not run,
  `skipped` means nobody tried.

**The honest limit, stated rather than buried.** Mutating the test proves an assertion is
sensitive to *its own* expected value. It does **not** prove it asserts the *right* thing — a
test asserting the wrong message, consistently, kills its mutant perfectly. That second question
is track 3's, and the two numbers never merge.

## Track 3 — LLM rubric (6 dimensions, /12)

Scores **only** what tracks 1 and 2 cannot see. Read their output, **take their facts as given,
and do not re-score them.**

Judge in a **fresh context**: give the test book, the generated files and the tracks 1-2 output —
**never the generation session's reasoning.** A judge that saw the code being written scores the
intention rather than the artifact.

| # | Dimension | 2 | 1 | 0 |
|---|---|---|---|---|
| 1 | **Then-fidelity** | Every test asserts what its scenario's `Then` states — same observable, same expected value; a vague `Then` stays vague rather than inventing precision | One test asserts a neighbouring observable (the URL where the `Then` names a message) | A test asserts something the `Then` never claimed, or silently strengthens/weakens it |
| 2 | **No invented expectation** | Every concrete literal traces to the book, the US, or observed behaviour — and where chosen for automation, a comment says so | A literal appears without provenance but is plausible and harmless | A literal contradicts the source, or an assumption is encoded as a requirement (**plausible-but-wrong**) |
| 3 | **Negative tests really refuse** | Each negative scenario asserts the *refusal itself* — error shown, state unchanged, access denied | Asserts only "not redirected" or similar single-sided evidence | Would pass against an app that silently does nothing |
| 4 | **Ambiguity preserved, not resolved** | `[open]`/`@low-confidence` scenarios encoded as the book states them, with a comment saying the expectation is unconfirmed and a failure is an answer, not a bug | Flag carried, no explanation of what a failure would mean | The code quietly picks one reading and asserts it as settled |
| 5 | **Assertion strength matches the claim** | Where the scenario claims absence, the test distinguishes "hidden" from "not in the DOM"; where it claims a value, it asserts the value, not visibility | Weaker than the claim but still directional | Compatible with the very failure mode the scenario exists to catch |
| 6 | **Honest handling of what could not be automated** | Anything the book demanded but the code cannot verify is named explicitly — comment, `test.fixme` with a reason, or a note in the run report | Mentioned vaguely | Silently dropped: the scenario looks covered and is not |

**Rules**: justify every score in one sentence, cite a `file:line` for every claim — *a score
without a citation is invalid* — and when hesitating, take the **lower** score.

## Output

1. The **static** result: score /100, the budget breakdown, and every blocking finding.
2. The **mutation** result: `total / killed / survived`, each survivor with its `file:line`, or
   `blocked` with the reason.
3. The **rubric** table: dimension, score, one-line justification with `file:line`, and the total
   /12.
4. **Top-3 fixes** — the three changes that would most improve the code.
5. **What I could not verify** — anything unavailable from the files alone. *An empty list here
   is itself suspicious.*

**Release reading**: rubric ≥ 9, no dimension at 0, and **no blocking finding open in either
deterministic track.** A blocking finding is never outweighed by a rubric score.

Write the result next to the run evidence. Do **not** write the manifest's `gate` block — that
belongs to `aptitude-gate` (contract: no producer scores itself, and no scorer gates itself
either).

## Guardrails

- **Reads and scores; never edits code.** Proposing a diff is allowed; applying it is not.
- **Never fabricate a finding to look thorough, and never soften a real one to be agreeable.**
- **Never merge the three numbers**, and never let one substitute for another — least of all a
  static score standing in for a mutation run that never happened.
- If the suite could not run, the run is **not scored**; it is reported as unrunnable with what
  is missing.
