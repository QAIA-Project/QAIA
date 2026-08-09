---
name: feedback
description: Capture the tester's corrections on a generated test book, store them as examples, and propose validated promotion of recurring corrections into knowledge-base rules so future generations improve. Use after someone has reviewed or reworked generated tests, when the same correction keeps coming back run after run, or when asked to make QAIA learn a project's own conventions instead of repeating the same mistake. Final step of the QAIA journey.
---

# feedback — learn from corrections, honestly

Follow the shared contract in `../README.md`. "Learning" here means enriching the local knowledge base and example store (README's honest positioning) — nothing else. Promotion is **always human-validated**.

## Prerequisite

A generated test book to compare against (`.qaia/testbooks/<US-ID>/`, from `testbook-generate`). If none exists — no checkpoint, no test book — say so and offer `us-ingest` to start the journey instead of asking for corrections that have nothing to be diffed against.

## Steps

1. **Collect.** Ask what the user changed or rejected in the test book (or diff the edited `.feature` files against the generated version if both exist). For each correction, capture: scenario ID, what was wrong, the corrected form, and **why** — the why is the valuable part.
2. **Classify.** Each correction is one of:
   - `business-rule` — the generation contradicted or missed a domain rule → candidate for `knowledge/`;
   - `style` — wording, structure, granularity preference → candidate for a project convention entry;
   - `one-off` — specific to this US, not generalizable → example only.
3. **Store examples.** Write each correction to `.qaia/feedback/examples/<US-ID>-<n>.md` with its classification and provenance.
4. **Propose promotions**: only when the same pattern appears in **≥ 2** stored examples, or the user explicitly asks for immediate promotion (single-criterion — the "states a reusable rule" shortcut promoted everything and filtered nothing). Rules get stable IDs `BR-KB-nnn` (counter persisted in `rules.md` frontmatter); examples get `<US-ID>-<nnn>` with the counter in `examples/`. When a promoted rule shapes a generated scenario, the scenario carries a `# rule: BR-KB-nnn` comment and the coverage matrix lists applied rules — flagging sibling scenarios of the same AC for regeneration. ⚠ VALIDATION: present the proposed promotion with this callout, verbatim; on approval, hand the rule to `rag-build` (which handles contradiction checks and the index); record the promotion in `feedback/rules.md` with links to its source examples.

   > **If you own the product rather than the tests, read this. You do not need the rest of
   > this page.**
   >
   > - **What you're being asked:** a correction is being proposed as a permanent rule — either
>   because it has come up more than once, or because someone asked for it directly. Which of
>   the two is stated above this box. It
   >   looks like a standing rule of your business rather than a one-off fix. You are being
   >   asked to confirm that it is — in the wording below.
   > - **Why it matters:** a confirmed rule is reused on every future story, automatically, by
   >   everyone on the team. That is the payoff. It is also the risk: a rule that is *almost*
   >   right, or true only for one product line, quietly propagates into stories nobody
   >   connected it to. Read the wording, not just the idea — especially any "always" or
   >   "never".
   > - **If you don't answer:** nothing is promoted. The corrections stay as isolated examples
   >   attached to their own story, and future generations may repeat the same mistake — which
   >   is the safe outcome, not the harmful one.
   >
   > Confirming a rule here changes future tests, never past ones, and it can be withdrawn later — by deleting its entry from `feedback/rules.md` and the corresponding line in `knowledge/index.md`, which is a two-line edit a human makes; there is no automated revoke, and saying otherwise would be a promise nothing keeps.
5. **Prune.** When promoting, mark source examples `promoted`; offer to archive examples older than ~6 months that never recurred — the store must not grow unbounded, or retrieval degrades and the signal drowns.
6. **Close the loop.** Tell the user which promoted rules will affect future generations, and remind them the effect is measured — not guaranteed — via the gold set: reapplication of a raw stored example is probabilistic, a promoted rule is the reliable path, and promising more than that would be the dishonest version of "learning".

## Guardrails

- Never promote without explicit validation, even for "obvious" corrections.
- Contradiction between a new correction and an existing rule → surface it (via `rag-build`'s arbitration), never store both silently — two contradictory rules in the base make every later generation a coin toss.
- Feedback content follows knowledge rules: no secrets, no personal data, provenance mandatory.
