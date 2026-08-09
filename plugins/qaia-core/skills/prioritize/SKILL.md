---
name: prioritize
description: Risk-based prioritization of derived test conditions - the skill proposes probability x impact scores, the human arbitrates. Use when there is more to test than time allows, when someone asks what to test first or what can be dropped, or before generating a test book so generation covers the right conditions. Fifth step of the QAIA journey, before test book generation.
---

# prioritize — risk-based, human-arbitrated

Follow the shared contract in `../README.md`. Prerequisite: `03-design.md` (else offer `istqb-design`). Risk-based testing needs inputs only a human has — how much a failure would actually cost this
business, and how fragile this part of the system really is: **the skill proposes, the user decides.**

## Steps

1. **Propose scores.** For each test condition of `03-design.md`:

   - **Impact (1-3)** — consequence if this behavior fails in production. Safety, regulatory or
     data-loss = 3; degraded service = 2; cosmetic = 1. Use `knowledge/` (criticality notes,
     anomaly history) when available, and cite what you used.
   - **Probability (1-3)** — likelihood of a defect. New, complex or concurrent logic and
     `[open]`-flagged conditions score higher; stable, well-understood rules lower.
   - **Optional git-history signal** — see `references/git-history-signal.md`. Only when the user
     has explicitly named a target repo path for this session.
   - **Priority = impact × probability** → **P1 (≥ 6) / P2 (3–5) / P3 (≤ 2)**.

2. **Show your reasoning compactly.** One table: condition, impact, probability, priority,
   one-line rationale.

   Flag every score resting on an `[assumption]` or `[open]` item, and every score whose
   probability the git-history signal nudged — citing the files and stat used
   (`@history(path, stat)`). Same visibility rule as `[assumption]`/`[open]`: **an uncited
   influence is not usable.**
3. ⚠ VALIDATION — present the score table with this callout, verbatim, above it:

   > **If you own the product rather than the tests, read this. You do not need the rest of
   > this page.**
   >
   > - **What you're being asked:** for each behaviour in the table, we guessed two things —
   >   how bad it would be if it broke in production, and how likely it is to break. Correct the
   >   first one. It is a business judgement, and you are the one who holds it.
   > - **Why it matters:** the two numbers multiply into a priority, and the priority decides
   >   what actually gets written and run. Rate something too low and it may never be tested at
   >   all; rate everything high and the important cases lose their place in the queue.
   > - **If you don't answer:** we keep our proposal and mark it *proposed, not arbitrated*.
   >   Nothing stops — but the test effort is then aimed by our guess at your business risk,
   >   and the story is not fit for a production go/no-go until someone has looked.
   >
   > You do not need to review every row. The ones worth your minutes are those we rated
   > **P1** — those we believe would hurt most — plus a scan of the titles of everything below — you are the only person who can spot a row we scored low that your business cannot afford. Reading the titles takes a minute; it is the minute this callout exists for.

   The user adjusts scores — their business knowledge overrides yours — or approves. Record each
   override with the user's stated reason: that reason is knowledge (offer `rag-build` capture
   when reusable).

   **In a non-interactive context with no user available, do NOT treat auto-acceptance as
   arbitration.** Output the scores explicitly as `proposed but not arbitrated`, with a
   disclaimer that they are unsuitable for a production Go/No-Go until a human reviews them. A
   `simulated: accepted-as-is` note is not a substitute for the arbitration this step exists to
   force.

   Marking the step done without a human having looked cancels the only control the skill
   provides: **a simulated acceptance is not an acceptance, and scores that were never
   contradicted are not scores that were validated** — nobody downstream can tell the difference
   once the note is written. Leave `04-prioritize` as `pending-validation` in `journey.md`,
   record the `simulated` entry in `openArbitrations[]`, and continue. `../README.md` rule 3 is
   the single arbitration; this step follows it verbatim.

4. **Checkpoint.** Write `04-priorities.md` — the arbitrated table. Update `journey.md`.

   Next step: `testbook-generate`. Tell the user generation covers P1 and P2 fully, and that
   **P3 coverage is their call**: generation costs real subscription quota, and P3 is where that
   budget stops paying for itself.

## Deliverable rule (rubric dim. 9)

The **one-line risk rationale of every priority assignment must reach the delivered book** — `testbook-generate` copies it into the coverage matrix (rationale column) and the synthesis, together with the list of assignments needing human arbitration. A priority whose rationale only lives in `04-priorities.md` (an internal state file the reviewer never sees) counts as unjustified.

## Guardrails

- **Never present your scores as final** — the arbitration step is the point of this skill.
- **A project under a traceability obligation treats traceability-relevant conditions as
  impact 3 by default.** Say so when applying it, and say *which* obligation — the user's, not
  ours. QAIA claims no regulatory coverage: the v1 "medical / regulated" niche framing was
  **retired (D114)**, and a rule that inflates priorities in the name of a withdrawn
  positioning is a rule nobody can defend to the person whose release it delays.
- **The git-history signal is an input to probability, never a verdict and never a shortcut
  around arbitration.** Bounds, citation rules and the "substance over raw count" test:
  `references/git-history-signal.md`. Read only the repo path the user explicitly gave for this
  session — no scanning other repos, no crawling beyond the files tied to the condition at hand
  (shared-contract rule 6: no side effects beyond what was requested).
