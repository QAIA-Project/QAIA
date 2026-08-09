---
name: need-understanding
description: Analyze a validated user story extraction - reformulate the need, detect ambiguities, contradictions and missing rules, ask the user targeted questions, and record answers or explicit assumptions. Use whenever a specification looks incomplete, contradictory or open to interpretation, when someone asks what to clarify with the product owner before testing, or before committing to test design on a story nobody has challenged yet. Third step of the QAIA journey.
---

# need-understanding — ambiguity hunt

Follow the shared contract in `../README.md`. Prerequisite: `01-extraction.md` (else offer `us-review`). Load relevant knowledge via `knowledge/index.md` — project rules may already answer some questions.

The open questions this skill raises are the ones a human later has to arbitrate, often blind. When production data for the same feature exists, `signal-ingest` attaches observed evidence to those questions — it never answers them, but it stops the arbitration from being a guess. Raise the question here regardless: a question that waits for evidence is still a question, and one never written down is never informed.

## Steps

0. **Nothing-to-understand check.** If `01-extraction.md` has no capability/behavior to test (a design doc, an RFC process, an empty template, a title with no ACs), do not fabricate requirements: say what the source actually is, and either ask the user for the missing acceptance criteria or stop. A reformulation of nothing is a defect.
1. **Reformulate.** State the need in 3-5 sentences: who, what, why, main risk if it misbehaves. This is the understanding the whole test design will rest on.
2. **Hunt ambiguities.** Systematically inspect each AC and rule for:
   - undefined terms and units ("soon", "recent", inclusive/exclusive thresholds)
   - **every duration or deadline: "measured against which clock/referential?"** (user timezone vs server vs counterpart — attach the question to the AC doing the *computation*, not the one doing the display)
   - contradictions between ACs, or between ACs and knowledge-base rules
   - missing behavior (error paths, empty states, concurrency, permissions)
   - unspecified data rules (formats, rounding, limits, uniqueness)
3. **Adversarial pass by AC type (mandatory).** Run the type-specific checklist on every AC:
   state machine/lifecycle, auth/tokens/permissions, sorting/pagination, thresholds/quantities.
   Checklists and the two hard rules that come with them — no test-data choice may sidestep an
   undefined case, and an unstated access boundary is a question, never an assumption:
   `references/ambiguity-passes.md`.
4. **Cross-AC interaction pass (mandatory).** For every pair of ACs sharing a resource, entity or
   time window, ask what happens when rule A's outcome feeds rule B at B's boundary. Log each as
   covered, `[assumption]` or `[open]` — intra-AC hunting alone misses exactly these.
4a. **Triple-AC contradiction pass (mandatory).** Some contradictions appear only when **three**
   rules meet — a protected-state rule, a scoping rule and an anti-disclosure rule on the same
   entity. Each is unambiguous alone, the pairs are consistent, and only the triple is undecided.
   Worked calibration example: `references/ambiguity-passes.md`.
5. **Ask, don't guess.** Present findings as numbered questions with stable IDs (`Q1, Q2…` —
   the numbering is cited by scenarios and must be complete and gap-free in the delivered
   synthesis), most impactful first, each with why it matters for testing and your proposed
   default answer.

   **Q-slots are for requirement ambiguity only** (step 2's categories), never for
   test-feasibility or flakiness questions — "is this independently re-verifiable live?", "is it
   scenario-testable without flakiness?". Those are automation-design concerns for `automate` and
   `testbook-generate`, not gaps in what the US specifies. The question budget is bounded, so
   every slot spent on feasibility is a requirement ambiguity that never gets asked — and the
   ambiguity is the one thing only the product owner can resolve, while feasibility is yours to
   solve later.

   **Sweep step 2's categories before closing the list.** Walk each in order and record either
   the question you are asking or an explicit "not applicable here: `<reason>`". A category
   absent from your output is indistinguishable from one you forgot. This is not a formality —
   `references/ambiguity-passes.md` carries the worked example of what one silent category cost:
   a false oracle shipped in a test book.
5a. **Classify each question** with the decision tree — answered / `[out-of-slice]` /
   `[open]` / `[assumption]` — applied in order, stopping at the first match, with its
   protected-domain rule and the money-mechanical vs money-policy exception. Tree and calibration
   examples: `references/ambiguity-passes.md`.
6. ⚠ VALIDATION — present the questions with this callout, verbatim, before the list:

   > **If you own the product rather than the tests, read this. You do not need the rest of
   > this page.**
   >
   > - **What you're being asked:** the specification does not say what should happen in the
   >   cases below. You are being asked what the *correct behaviour* is — not how to test it.
   > - **Why it matters:** every answer becomes a test that asserts that behaviour. Answer, and
   >   the test checks what you decided. Don't answer, and we write a test asserting our best
   >   guess — which will then pass, look green, and prove nothing about your actual rule.
   > - **If you don't answer:** for low-risk points we apply a stated default and mark it as an
   >   assumption. For anything touching money, safety, health data, minors or legal evidence we
   >   apply **no** default: those stay open, and every test that depends on them is flagged as
   >   resting on an unconfirmed guess. That flag follows the story to the release decision.
   >
   > "I don't know" is a useful answer, and it does one of two things depending on the subject:
   >   on a low-risk point it becomes a flagged assumption; on anything touching money, safety,
   >   health data, minors or legal evidence it leaves the question **open** and the scenario
   >   marked, because no default is safe there. Either way it beats inventing a certainty.
   >   The unusable answer is silence.

   For each question the outcome is exactly one of:
   - **answered** — the user states the rule → recorded as a decision;
   - **`[assumption]`** — the user accepts your proposed default, **or answers "not specified / I don't know" AND your default is a low-risk plausible behavior** → the default becomes a flagged working assumption;
   - **`[open]`** — no answer and the point is a genuine product decision (safety, money, compliance, user-visible policy) where any default would be a guess → stays open, caps confidence of affected scenarios.
   Record which of the three applies for every question; two skills executors must classify identically.
7. **Knowledge capture.** If an answer states a reusable business rule, offer to add it to `knowledge/` via `rag-build` (do not write knowledge files yourself).
8. **Checkpoint.** Write `02-understanding.md`: reformulation, complete Q&A log with status (`answered` / `assumption` / `open`), **plus an explicit `## Adversarial pass (by AC type)` section and an explicit `## Triple-AC contradiction pass` section** — each stating either its findings or "not applicable, no matching pattern in this US" with a one-line reason. Update `journey.md`. Next step: `istqb-design`.

## Guardrails

- Never silently resolve an ambiguity — it is the defect reviewers punish hardest, because it produces a test book that looks confident and asserts behavior the specification never promised (the *business correctness* and *ambiguity handling* dimensions of the review rubric, [`eval/RUBRIC.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/RUBRIC.md)).
- **Omitting the required trace of step 3 or step 4a from `02-understanding.md` is the same defect as silently resolving an ambiguity** — a mandatory pass that leaves no evidence it ran is indistinguishable from a skipped one. Touching on the pass inside some question's justification text does not count: the reader must be able to check that the pass happened without reconstructing it from prose, so each pass gets its own named section, even when its outcome is "nothing found".
- Bound the interrogation: maximum ~10 questions per pass, highest impact first; offer a second pass rather than overwhelming the user.
