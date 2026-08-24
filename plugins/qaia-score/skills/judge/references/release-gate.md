<!-- Absorbé le 2026-08-24 : cette page était la skill `aptitude-gate`.
     Elle n'est plus une unité installable — elle est une étape de `judge`.
     Le contenu est DÉPLACÉ, pas récrit : ce qui a été éprouvé le reste. -->

> **Ce que cette étape fait.** Decide release readiness of a QAIA test book or run - PASS / CONCERNS / FAIL / WAIVED - from the rubric score, hard coverage gates (AC, ADR 0001 negative-path), pending human arbitrations, and any execution results, recording the verdict and reasons in the standardized run manifest. Scores only - it judges readiness, it never edits test content. Use to gate a candidate before hand-off or CI.

# aptitude-gate — release-readiness verdict

Turns evidence into a single decision — **PASS / CONCERNS / FAIL / WAIVED** — and writes it to
the `gate` block of the standardized run manifest (shared output contract,
[`docs/OUTPUT-CONTRACT.md`](https://github.com/QAIA-Project/QAIA/blob/main/docs/OUTPUT-CONTRACT.md)) — that path is in the QAIA source repository, **not in the installed plugin**, so rely on the field names restated below when you do not have the repo.. It combines
the quality score (`testbook-score`), the hard coverage gates, the pending human arbitrations,
and — when present — the execution results. It **scores only**: it decides readiness and names
what blocks it; it never edits a scenario (guardrails in `../README.md`).

## Prerequisite

`.qaia/reports/<US-ID>/manifest.json` must **exist**. If the manifest itself is absent — no
`report`/`run-report` has run yet — say so and offer to run `qaia-core:report` first instead of
gating on nothing; do not invent a manifest or a verdict. If the manifest exists but
`gate.score` is empty, that is a lesser gap: ideally `testbook-score` has already filled it; if
not, run that first (or score inline using its rubric) — a verdict without a quality score is
only a hard-gate check, and the skill says so.

## Verdict rules (deterministic — apply in order)

Evaluate top to bottom; the **first** matching band is the verdict.

1. **FAIL** — any hard gate is broken (release-blocking):
   - `structural.forcedStop` is true, or `structural.gate` is `FAIL` — the deterministic pass
     found a scenario that cannot be evaluated at all (a `Then` whose only evidence is an image,
     no verifiable expected result, fabricated technical literals). **No rubric total overrides
     this**: a 20/20 on a book containing a hollow scenario means the judge scored something the
     machine already proved unassessable. Read the `structural` block; if it is absent, say the
     deterministic pass has not run rather than assuming it passed;
   - an acceptance criterion is uncovered (`design.coverage.acCovered < acTotal`, rubric dim 2 = 0);
   - a **required** negative condition is uncovered (`reqNegCovered < reqNegTotal`, dim 3 = 0) —
     the governing decision is ADR 0001, the required negative/refusal-path coverage gate
     ([`docs/adr/0001-negative-coverage-gate.md`](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0001-negative-coverage-gate.md));
   - a scenario contradicts the source US (dim 5 = 0 — plausible-but-wrong);
   - invalid Gherkin (dim 8 = 0) or no stable IDs / broken traceability (dim 7 = 0);
   - **any** rubric dimension scored 0;
   - an execution suite reports `failed > 0` while being presented as green.
2. **CONCERNS** — nothing blocks, but the candidate is not clean:
   - rubric total `< 16` (below the release gate) with no dimension at 0;
   - unresolved `openArbitrations` — `[open]` questions or `simulated` defaults still pending
     human decision (these **always** cap the verdict at CONCERNS until resolved);
   - a dimension dropped ≥ 1 versus a provided baseline (regression signal);
   - execution present with `blocked > 0`, or automation coverage materially below the book
     (`traceability.scenariosAutomated` ≪ `scenariosTotal`) when a run was expected;
   - a `flakiness` section (from `qaia-playwright:flaky-detect`) lists any `@P1` scenario
     whose verdict varied across runs — a P1 that sometimes fails isn't release-clean even if
     its last run was green. `@P2`/`@P3` flaky scenarios are named in `reasons` but don't by
     themselves force CONCERNS (report them; don't over-block on low-priority instability).
3. **PASS** — rubric total `≥ 16`, no dimension at 0, all hard gates met, no pending
   arbitration, and (if execution is present) `failed = 0` and `blocked = 0`.
**WAIVED is not a fourth band — it is an overlay, and it is decided before the bands are read.**
A human explicitly accepts a candidate that the bands above already classified CONCERNS or FAIL.
So: evaluate the bands first, publish the verdict they produce, and only then record a waiver on
top of it if a human granted one. **Never self-granted** — only a recorded human decision produces
it, carrying `waiver: { by, reason, at }`; `validate_manifest.py` rejects a WAIVED verdict with no
waiver object. The underlying band verdict and its reasons stay listed and stay true: a waiver
accepts a risk, it never erases the finding. *Never number WAIVED as a fourth band: listing it
alongside FAIL/CONCERNS/PASS makes it read as an outcome the skill can reach by evaluating
evidence, which is the exact opposite of the rule — a waiver has no evidential trigger, only a
human one.*

## Steps

1. **Read the manifest** — `design`, `structural` (the deterministic /100 pass), `execution`
   (if any), `gate.score`/`dimensions`, `openArbitrations`, and `flakiness` (if present). Note the `contract` major version;
   treat any absent field as absent, not as a failure (degraded mode).
   **Recompute the rubric total from the 10 `dimensions` scores yourself — never trust
   `gate.score` as given.** A judge's listed dimension scores and its recorded total can
   disagree by one, and at the release threshold a single point silently flips CONCERNS to PASS
   — invisibly, because nothing downstream recomputes it. The rule generalizes: any
   self-reported number that decides a release is verified, not assumed (the same reason the
   negative-coverage count is recomputed independently of the file's own `@negative` tags, in
   [`eval/tools/structural_score.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/structural_score.py)). If the recomputed total disagrees with `gate.score`, use the
   recomputed value for every band comparison below and add a `reasons` line naming the
   discrepancy (`"score mismatch: dimensions sum to 15, manifest said 16 — using 15"`).
2. **Apply the verdict rules** above, in order. Collect the concrete `reasons` — one line each,
   each citing the evidence (`"AC4 uncovered (matrix row 4)"`,
   `"open arbitration: cancellation < 4h"`,
   `"dim 3 = 1: req-neg AC4-C2 uncovered"`). A PASS lists the gates it cleared.
3. **Handle a waiver only on explicit human input.** If — and only if — the user states they
   accept the candidate despite the reasons, set `verdict: "WAIVED"` and record
   `waiver: { by, reason, at }`. Absent that, never write WAIVED. Never turn a FAIL into PASS.

   When a verdict is not PASS and a human is being asked whether to proceed anyway, present the
   reasons with this callout, verbatim:

   > **If you own the product rather than the tests, read this. You do not need the rest of
   > this page.**
   >
   > - **What you're being asked:** the checks below did not come out clean. You are being asked
   >   whether to ship anyway. Saying yes is called a *waiver*: it means the problem is real,
   >   you have seen it, and you accept it.
   > - **Why it matters:** a waiver does not fix or delete anything. The finding stays recorded,
   >   with your name and your reason next to it, and it stays visible on this story afterwards.
   >   That is the point — it makes accepting a risk a decision someone made rather than
   >   something that quietly happened.
   > - **If you don't answer:** nothing ships on our say-so. The verdict stands as it is, no
   >   waiver is recorded, and the story stays flagged as not release-clean. This tool never
   >   releases anything by itself.
   >
   > The most common reasons here are worth telling apart. **"A question was never answered"**
   > means some tests rest on our guess — the fix is usually five minutes of your time, not a
   > waiver. **"A required failure case is untested"** means nobody checked that the system
   > refuses what it should refuse, which is where the expensive defects live.


4. **Write `gate`** into the manifest (merge, contract rule 2): `verdict`, keep `score`/
   `dimensions` from `testbook-score`, `reasons`, `waiver` (or `null`), `scoredBy:
   "qaia-score/aptitude-gate"`, `at`. Do **not** touch `design`, `execution`, or the
   human-owned `status`. A gate verdict never flips `status` — only a human validation does.
5. **Report** the verdict, the reasons, and the single most valuable next action (which fix
   clears the gate, or which arbitration to resolve) — then stop. The verdict is advice to a
   human, not an automatic release.

## Guardrails

- **The gate never releases anything.** It records a verdict; a human (or a CI rule they
  configured) acts on it. PASS is not a merge, WAIVED is not an approval — both are recorded
  judgments a person owns.
- **No self-waiver, no inflation, default low.** When the evidence is between two bands, choose
  the stricter one and say why. Pending `simulated`/`[open]` items keep it at CONCERNS.
- **Read-only over test content**; the only write is the manifest `gate` block. Name the
  blocking fix — hand it to `qaia-core`, never apply it.
- **Portable** — markdown + JSON in, JSON out; no network, no API key. Without file tooling,
  emit the `gate` object as a fenced block for the user to save.
