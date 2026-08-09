---
name: Requirement Ambiguity Hunt
description: Find what a user story does not say before writing a single test - undefined terms, unstated clocks, cross-rule contradictions, missing error paths - and turn each into a numbered question for the product owner instead of a silent guess baked into an assertion.
version: 1.0.0
author: opaland
license: MIT
tags: [requirements, ambiguity, shift-left, test-design, bdd, istqb]
testingTypes: [strategy, acceptance, e2e]
frameworks: []
languages: [typescript, javascript, python]
domains: [web, api]
agents: [claude-code, cursor, github-copilot, windsurf, codex]
---

# Requirement Ambiguity Hunt

> **Standalone adaptation.** This is a self-contained version of the `need-understanding` skill
> from [QAIA](https://github.com/QAIA-Project/QAIA) (MIT), packaged as a single file for
> directories that expect one. The canonical version, its `references/`, and the evaluation
> evidence behind the claims below live in that repository. QAIA is pre-alpha and says so.

## When to use this

Before designing tests for any story, and whenever a specification looks incomplete,
contradictory, or open to interpretation. Also when someone asks *"what should I clarify with the
product owner?"*.

## The failure mode this exists to prevent

Almost any generator will produce a test for *"above €500 requires finance approval"*. The
question is what it does with **exactly €500**.

Pick silently and you ship a suite that looks complete and encodes a guess — at the boundary,
which is where the defects are. The test then passes, looks green, and proves nothing about the
actual rule. Worse, the guess is invisible: nothing in the output distinguishes an asserted fact
from an asserted assumption.

**Never silently resolve an ambiguity.** A surfaced question costs one line. A resolved one costs
the credibility of every green run in the suite.

## Steps

### 0. Nothing-to-understand check

If the source has no capability or behaviour to test — a design doc, an RFC process, an empty
template, a title with no acceptance criteria — **do not fabricate requirements**. Say what the
source actually is, and either ask for the missing criteria or stop. A reformulation of nothing is
a defect.

### 1. Reformulate

State the need in 3-5 sentences: who, what, why, and the main risk if it misbehaves. Everything
downstream rests on this.

### 2. Hunt ambiguities, by category

Inspect every acceptance criterion for:

- **undefined terms and units** — "soon", "recent", inclusive vs exclusive thresholds;
- **every duration or deadline: measured against which clock?** User timezone, server, or
  counterparty. Attach the question to the criterion doing the *computation*, never the one doing
  the display;
- **contradictions** between criteria, or between a criterion and a known project rule;
- **missing behaviour** — error paths, empty states, concurrency, permissions;
- **unspecified data rules** — formats, rounding, limits, uniqueness.

**Sweep every category before closing the list**, and record either the question you are asking or
an explicit *"not applicable here: `<reason>`"*. A category absent from the output is
indistinguishable from one you forgot. In a measured run of the source project, one silently
skipped category put a false oracle into a delivered test book.

### 3. Adversarial pass by criterion type

Run the type-specific checklist on every criterion — state machine or lifecycle, auth and tokens
and permissions, sorting and pagination, thresholds and quantities.

Two hard rules travel with it:

- **No test-data choice may sidestep an undefined case.** Choosing a value that avoids the
  boundary is not a test, it is an evasion.
- **An unstated access boundary is a question, never an assumption.** "Can a manager see another
  team's record?" is never answered by silence.

### 4. Cross-criterion interaction pass

For every pair of criteria sharing a resource, an entity or a time window, ask what happens when
rule A's outcome feeds rule B **at B's boundary**. Hunting inside a single criterion misses
exactly these.

### 4a. Triple-criterion contradiction pass

Some contradictions appear only when **three** rules meet — typically a protected-state rule, a
scoping rule and an anti-disclosure rule on the same entity. Each is unambiguous alone, every pair
is consistent, and only the triple is undecided. Check the triples on any entity carrying all
three.

### 5. Ask, do not guess

Present findings as numbered questions with stable IDs (`Q1`, `Q2`…), most impactful first, each
with **why it matters for testing** and **your proposed default answer**.

The numbering is cited by scenarios downstream, so it must be complete and gap-free.

**Question slots are for requirement ambiguity only.** Not for test feasibility, not for
flakiness — *"is this re-verifiable live?"*, *"is it testable without flakiness?"* are automation
concerns, yours to solve later. The budget is bounded, so every slot spent on feasibility is a
requirement ambiguity that never gets asked — and the ambiguity is the only one of the two that
**only the product owner can resolve**.

Bound the interrogation: **~10 questions maximum per pass**, highest impact first. Offer a second
pass rather than overwhelming the reader.

### 6. Present them with this, verbatim

Quote this block before the list. It is written for someone who owns the product and not the
tests, and its wording is deliberate — it names the risk of answering *and* the risk of silence.

> **If you own the product rather than the tests, read this. You do not need the rest of this
> page.**
>
> - **What you're being asked:** the specification does not say what should happen in the cases
>   below. You are being asked what the *correct behaviour* is — not how to test it.
> - **Why it matters:** every answer becomes a test that asserts that behaviour. Answer, and the
>   test checks what you decided. Don't answer, and we write a test asserting our best guess —
>   which will then pass, look green, and prove nothing about your actual rule.
> - **If you don't answer:** for low-risk points we apply a stated default and mark it as an
>   assumption. For anything touching money, safety, health data, minors or legal evidence we
>   apply **no** default: those stay open, and every test that depends on them is flagged as
>   resting on an unconfirmed guess. That flag follows the story to the release decision.
>
> "I don't know" is a useful answer, and it does one of two things depending on the subject:
> on a low-risk point it becomes a flagged assumption; on anything touching money, safety,
> health data, minors or legal evidence it leaves the question **open** and every dependent
> scenario marked, because no default is safe there. Either way it beats inventing a
> certainty. The unusable answer is silence.

### 7. Classify every question — exactly one of three

| Outcome | When | Effect |
|---|---|---|
| **answered** | the owner states the rule | recorded as a decision |
| **`[assumption]`** | the owner accepts your default, **or** says "not specified / I don't know" **and** your default is a low-risk plausible behaviour | the default becomes a *flagged* working assumption |
| **`[open]`** | no answer, and the point is a genuine product decision — safety, money, compliance, user-visible policy — where any default would be a guess | stays open and **caps the confidence** of every scenario that depends on it |

Record which applies for **every** question. Two people running this must classify identically.

## Guardrails

- **Never silently resolve an ambiguity.** It produces a test book that looks confident and
  asserts behaviour the specification never promised.
- **A mandatory pass that leaves no evidence it ran is indistinguishable from a skipped one.**
  Give each pass its own named section in the output, **even when the outcome is "nothing
  found"**. Touching on it inside some question's justification does not count: the reader must be
  able to check the pass happened without reconstructing it from prose.
- **Carry the flag downstream.** A scenario resting on an `[open]` question must say so in its
  tag and in a comment — otherwise, the day that test goes red, nobody can tell *"the question
  just got answered"* from *"the product regressed"*, and the cheapest fix is to align the
  expected value with the application. That silently converts a finding into a specification.

## Where the claims come from

Measured on real runs, kept in the source repository: on one expense-approval story, this pass
produced **9 questions from 8 acceptance criteria**, and **11 of the 38 scenarios** generated
downstream carry a named open question rather than a silent interpretation.
