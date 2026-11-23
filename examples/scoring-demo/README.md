# Scoring demo — the output contract and `qaia-score` end to end

> **Read with the current names (note added 2026-11-23).** This example was produced when each step
> was a separate skill, and its text keeps the names of the time. Since then the journey skills
> (`us-ingest`, `us-review`, `need-understanding`, `istqb-design`, `oracle-generate`,
> `openapi-ingest`, `prioritize`, `testbook-generate`, `report`, `testbook-export`) are the steps of
> `qaia-core:generate`; the scorers (`testbook-validate`, `testbook-score`, `automation-score`,
> `spec-suite-drift`, `aptitude-gate`) are pages of `qaia-score:judge`; `contract-probe`,
> `traffic-replay`, `signal-ingest` and `defect-report` are pages of `qaia-playwright:probe`.
> `rag-build`, `feedback`, `run-report`, `a11y-audit`, `security-surface`, `perf-check`,
> `visual-check`, `usability-heuristic-review` and `flaky-detect` were deleted on 2026-10-26. The
> artifacts below are kept exactly as they were produced. Map: [`CATALOGUE.md`](../../plugins/qaia-core/CATALOGUE.md).

An **illustrative** walk-through of the standardized run manifest (`docs/OUTPUT-CONTRACT.md`,
D39) and the `qaia-score` plugin (D40). The numbers here are representative, not a fresh
measurement of a specific run — they exist to show the shape of the contract and how the two
scoring skills read and annotate it. Real manifests are produced by `qaia-core:report` (design)
and `qaia-playwright:run-report` (execution) from actual artifacts.

## 1. The shared envelope — `manifest.json`

Every QAIA plugin projects its work into one file, `.qaia/reports/<US-ID>/manifest.json`. See
[`manifest.json`](./manifest.json) in this folder. Note:

- **`producers[]`** is an append-only provenance chain: `testbook-generate` → `report` →
  `testbook-score` → `aptitude-gate`. Each skill merges its own section and leaves the rest
  untouched (contract rule 2).
- **`design`** carries normalized counts — scenarios by priority, the ADR 0001 negative-path
  gate (`reqNegCovered/reqNegTotal`, the one that blocks) and the D20 `negativeRatio` (a
  reported signal, never a threshold).
- **`openArbitrations`** lists every pending human decision, including `simulated` defaults
  from non-interactive runs.
- **`gate`** is written **only** by `qaia-score`. No producer scores itself.

## 2. `qaia-score:testbook-score` — the quality scorecard (/20)

Reads the test book + source US (fresh eyes, without the generation session's context) and
scores the 10 rubric dimensions. Illustrative scorecard for this manifest:

| # | Dimension | Score | Justification (cites the artifact) |
|---|---|---|---|
| 1 | Atomicity | 2 | one `When` per scenario; the single `@smoke` journey is exempt |
| 2 | AC coverage | 2 | 8/8 ACs covered; matrix has no gaps |
| 3 | Negative-path (ADR 0001) | 2 | all 7 required-negative conditions covered |
| 4 | ISTQB technique fit | 1 | AC7 decision-table justification is generic |
| 5 | Business correctness | 2 | no scenario contradicts the US; extrapolations flagged |
| 6 | Ambiguity handling | 2 | Q5 surfaced as an open question, not silently resolved |
| 7 | Stable IDs & traceability | 2 | every scenario `@QAIA-US-001-NNN`, unique, AC-linked |
| 8 | Gherkin form | 2 | valid, English keywords, consistent vocabulary |
| 9 | Prioritization | 2 | every scenario carries a priority + one-line rationale |
| 10 | Review support | 1 | synthesis present but 3 low-confidence scenarios not flagged review-first |
| | **Total** | **18 / 20** | |

**Top-3 fixes** (advice handed to `qaia-core`, never applied by the scorer):
1. Justify the AC7 decision-table choice against its condition types (dim 4).
2. Mark the 3 `@low-confidence` scenarios "review first" in the synthesis (dim 10).
3. Resolve Q5 (cancellation < 4h) so the AC6 scenarios drop their `@low-confidence` tag.

`testbook-score` writes `gate.score`, `gate.max`, and the below-2 `dimensions` into the
manifest — never the verdict.

## 3. `qaia-score:aptitude-gate` — release readiness

Applies the deterministic verdict bands to the manifest:

- No hard gate is broken (AC coverage full, ADR 0001 met, no dimension at 0, valid Gherkin,
  stable IDs) → **not FAIL**.
- Total is 18 (≥ 16) → clears the score band **but** `openArbitrations` is non-empty (Q5 open,
  AC7-C2 simulated) → **capped at CONCERNS**.

**Verdict: `CONCERNS`** — shippable with caveats, a human resolves the two arbitrations first.
The gate records the reasons; it does not release anything.

### The WAIVED path

If the team lead explicitly accepts the candidate despite the open items, `aptitude-gate`
records a waiver — it is **never** self-granted:

```jsonc
"gate": {
  "verdict": "WAIVED",
  "score": 18, "max": 20,
  "reasons": [ "2 open arbitrations pending (Q5, AC7-C2)" ],
  "waiver": { "by": "team-lead", "reason": "Q5 tracked in PROJ-241, ship the rest", "at": "2026-07-23T11:00:00Z" }
}
```

## Why a separate plugin

`qaia-core` generates; `qaia-score` judges. Keeping the judgment in its own read-only plugin
enforces the shared-contract rule that **no skill self-validates** (qaia-core `skills/README.md`,
rule 3): the scorer cannot edit the book it scores, only name the fixes and record a verdict.
