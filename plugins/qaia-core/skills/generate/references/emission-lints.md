# Emission lints — the checks that run before anything is shown

Run all of these on the generated set **before** presenting the synthesis. One is blocking; the
rest are emission errors to fix in place.

---

## L1 — Negative-path coverage gate (ADR 0001) — **blocking**

Every `[req-neg]` condition from `03-design.md` has a covering `@negative` scenario, or an
explicit user-approved waiver. Every P1/P2 condition is covered. The Gherkin parses.

**Blocking means halt and ask *before* emission — not emit-then-flag.**

A P1/P2 `[req-neg]` condition generated *without* a true `@negative` outcome is **not** resolved
by adding it to step 7's arbitration list. That list is for decisions the user must weigh in on
— waivers, ambiguous defaults — not a catch-all for gate violations discovered after the fact.

A required-negative condition emitted with a positive or merely bounded assertion is **a defect
in the book**, not a decision the user was ever asked to make. Routing it to the arbitration
list converts a blocking check into a footnote and empties the gate of its effect.

(Priority-scoped waivers are a separate case and are not violations — see
`negative-ratio.md`.)

## L2 — Negative ratio computed and reported

Computed and reported in the synthesis as a happy-path-bias signal, using the single definition
in `negative-ratio.md`. Never a threshold, never padded toward.

## L3 — One `When` per scenario

Exactly one action. If a scenario needs two, it is two scenarios.

## L4 — No compound `Then`

A `Then` verifying a second behavior — typically an "…and no X happened" assertion about another
rule — becomes its own scenario. Compound outcomes are how a scenario stops being atomic without
looking like it.

## L5 — Every asserted literal is verified by computation

String lengths, sums, boundary ±1: count the characters, do the arithmetic. Do not assert a
number you did not compute.

## L6 — A computed value is only as grounded as its inputs

If the computation depends on an external parameter **not stated** in the source, design or
knowledge base — an exchange rate, a tax rate, a discount table — do not assert the resulting
precise literal as if it were sourced. Two acceptable outcomes:

- **Keep the assertion qualitative**: state the structural fact the AC actually requires ("the
  converted total falls in the band above €500"), not a fabricated exact figure.
- **Invent the input side instead**, when a concrete number is needed for boundary testing, and
  mark the derived parameter explicitly as a test fixture with an inline comment
  (`# rate-assumption: …` or equivalent).

Never a bare precise result with no traceable origin. A number that looks sourced and is not is
the highest-cost defect this lint prevents: it survives review precisely because it looks
computed.

## L7 — `Background` holds only universal invariants

Only facts true for **100 %** of the file's scenarios. Anything contradicted by even one
scenario moves to a local `Given`.

## L8 — `@negative` closed definition applied

A refusal, an error, or an explicitly denied access. List-exclusion and filtering scenarios are
**not** `@negative` — see `negative-ratio.md`.

## L9 — ID continuity

The scenario NNN sequence has no gap unless a `# retired: NNN` changelog line explains it. A
silent gap is an emission error.

## L10 — Re-check the ratio after any merge

The ratio is measured on the final block set. Recompute after merging; report the new figure,
not the pre-merge one. Re-check the `[req-neg]` checklist as a gate at the same time — a merge
that drops a required-negative scenario is blocking whatever the percentage says.

## L11 — Tag-versus-ratio audit

The `@negative` count used in the reported ratio must equal a literal count of `@negative` tags
in the emitted `.feature` file. Fix the tag or fix the ratio before showing the synthesis —
everything downstream counts tags, not intentions.

---

## After the lints

Write `state/<US-ID>/generated.snapshot.md`: scenario IDs plus a content hash per scenario.

This is the baseline regeneration compares against. Without it, regeneration cannot distinguish
a hand-written correction from its own previous output — and the default that human edits win
becomes unenforceable.
