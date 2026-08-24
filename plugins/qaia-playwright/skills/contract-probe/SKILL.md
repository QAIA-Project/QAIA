---
name: contract-probe
description: Probe a self-hosted or explicitly authorized app's real behavior against its own documented contract (README, help text, spec) with bounded, non-destructive adversarial inputs, judging deviation from what is promised rather than only crash-vs-no-crash - convert each confirmed defect into a tagged Gherkin regression scenario. Never applies a fix. Use for shift-right coverage complementary to the spec-first journey.
---

# contract-probe — adversarial contract probing

Reference: `fixture/taskapi/` (a deliberately defective toy API + its own README as the
"documented contract") — see `fixture/VALIDATION.md` for the worked example.

**Direction.** The rest of QAIA's journey is spec-first: US → AC → Gherkin → automation,
generated *before* the app necessarily exists in its final form. This skill runs the other way: a
system already runs, it already documents what it promises, and the question is whether it keeps
those promises under conditions a happy-path test never tries. **Its oracle is the target's own
documentation** — that is what separates it from the other skills that touch a running app, and
the one-line-per-skill comparison lives in the catalogue map rather than here.

**Its other half is `qaia-score:judge`** (its `references/spec-vs-suite.md` step, formerly the standalone `spec-suite-drift` skill)**.** This skill asks whether the *application*
keeps the documented promises; that one asks whether the *test suite* even mentions them. The two
questions look alike and fail apart: a suite can be perfectly green against an application that
honours a contract neither of them has read the same way. Run the drift check first — it is pure
text, needs nothing running, and costs nothing — then probe what it leaves open.

## Steps

1. **Extract the contract.** Read the target's own documentation — README, `--help` output,
   an OpenAPI/JSON-Schema spec, inline doc comments — and list its concrete, checkable promises
   (a status code for a case, an invariant, a format guarantee). A vague marketing claim
   ("fast", "reliable") is not a checkable promise; skip it. Cite each promise's source
   (file/section) — never invent one the docs don't actually state.
2. **Probe with bounded, non-destructive adversarial input (authorized-target posture, same as
   `security-surface`).** For each promise, construct inputs designed to break it specifically:
   boundary/malformed values, unexpected types, extreme sizes, unusual encodings — the same
   adversarial mindset as ISTQB error-guessing, aimed at a documented promise rather than a
   generic crash. **Never**: a DoS-shaped load, destruction of real data, or any target not
   self-hosted and authorized (identical guardrail to `security-surface`).
3. **Judge against the contract, not just "did it crash."** A 500 where the docs promise a 4xx
   is a defect even though the process kept running. A field silently dropped, a documented
   invariant silently violated, an error message that leaks more than promised — all defects,
   independent of whether anything visibly broke. A response that merely differs from what you
   personally expected, with no promise contradicted, is **not** a finding — cite the specific
   broken promise or drop it.
4. **Reproduce and prioritize.** Confirm each candidate defect with a minimal, repeatable
   request (not a one-off fluke) before reporting it; rank by the same impact-driven spirit as
   `prioritize` (a defect on a promise the app's own docs mark as important outranks a footnote).
5. **Convert into a regression scenario — never a live fix.** For each confirmed defect, write
   one atomic Gherkin scenario reproducing the exact triggering input and the actual vs.
   promised behavior, tagged `@QAIA-CP-<NNN>` and `@negative`, with a `# contract:` comment
   citing the exact promise it violates (source + line, from step 1). **Never** patch the
   target's code — same posture as `locator-repair`: propose evidence, a human decides
   the fix. If the user wants automation, hand the scenario to `automate` afterward as normal.
6. **Report.** One table per probed promise: promise → probe input → observed → verdict
   (kept/broken) → scenario ID if broken. A clean pass (no defect on a given promise) is
   reported as such, not omitted.

## Guardrails

- **Authorized targets only** (identical to `security-surface`). State in the report which
  authorization applies, in this order: (a) an in-repo app under `examples/` — self-hosted and owned
  by definition; (b) a target listed in `https://github.com/QAIA-Project/QAIA/blob/main/docs/DEMO-TARGETS.md` — cite its golden rule; (c) a third
  party whose own documentation or owner explicitly authorizes probing — quote that authorization
  verbatim and archive it (see the traceability rule below). If none of the three applies, do not
  probe. *Self-hosted is the nominal case, not the only lawful one: an owner's explicit
  authorization is equally valid legitimacy. Say that plainly rather than titling the rule
  "self-hosted only" and leaving the agent to arbitrate between the title and the clause that
  admits an authorized third party — a guardrail that contradicts itself is a guardrail that gets
  resolved in whichever direction is convenient.*
- **Bounded and non-destructive**: no load/DoS shape, no destructive payload against real data.
  This skill probes for *logic* contract violations, not availability attacks.
- **No fabricated promises**: every probed "contract" item must be traceable to an actual line
  in the target's own documentation — if the target has no documented behavior for a given
  angle, that angle is out of scope here, not filled in with a guess. **Archive the quoted line
  next to the run** (`contract-source.md`: the promise verbatim, its URL and the capture date).
  A live page is not a citation: a third party can redesign, relicense or retire its
  documentation at any moment, and an evidence trail that only works while the page still exists
  is not an evidence trail. Same rule for the authorization quote above — it is the sole legitimacy of
  probing a third party, and it must survive the target's next redesign.
- **Disclose every probe that did not run as designed.** A batch that failed to construct (empty
  variable, unresolved path, wrong shell) belongs in the report, not only in a comment inside the
  script. Otherwise a boundary the run never actually honoured gets reported as honoured: a
  misconstructed batch still elicits *some* response — often a plausible-looking one, sometimes one
  that only accidentally stayed inside the intended bounds — and the report then presents that
  accident as a deliberate observation. A near-miss written up as an intention is worse than a
  stated failure: it makes an untested boundary look tested.
- **Advisory only, never a gate**: findings feed `prioritize`/human review, same as every other
  producer skill (rule 3, `https://github.com/QAIA-Project/QAIA/blob/main/plugins/qaia-core/skills/README.md`: no producer scores itself).
