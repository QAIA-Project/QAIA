# RAG-in-use demo — the knowledge base breaks the recall ceiling

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

An **illustrative** walk-through of "the RAG in real use" (D38, the retrieval protocol in
`plugins/qaia-core/skills/README.md`). It shows the one thing a thin US cannot give you and the
knowledge base can: **config-driven and segment-driven coverage**, retrieved and cited by rule
ID — not guessed.

Files here mirror a real project layout:

```
us.md                     # SHOP-412 — a thin 3-AC discount story (the ingested source)
knowledge/
├── index.md              # master index (D21) — every read routes through it
├── business-rules.md     # BR-KB-004/007/011/014 — project truths no single US states
└── application-map.md    # where the behavior lives (surfaces, endpoints, segments)
conditions.md             # the measurable diff: US-alone vs US + RAG
```

## The point: same US, two very different designs

`istqb-design` step 3c (systematic expansion) already adds reflex conditions. But it explicitly
**refuses to invent** config-driven and segment-driven behavior (the honest-recall ceiling).
Step 3d closes that gap by *retrieving* those rules from `knowledge/` instead of guessing them.

### Without the knowledge base — generation from the 3 ACs alone
Covers: valid code reduces total (AC1), expired/unknown rejected (AC2), total shown before pay
(AC3), plus reflex negatives (empty code, whitespace). **Misses**, because they are nowhere in
the US: single-use-per-customer, stacking behavior, the B2B cart-minimum waiver,
case-insensitive matching. A generation-from-AC run cannot know these exist.

### With the knowledge base — step 3d retrieves and applies the rules
Routing the AC entities (`discount`, `code`, `checkout`, `cart`) through `index.md` matches
`business-rules.md`. Each applicable rule becomes a cited condition:

| Derived condition | From rule | Kind |
|---|---|---|
| Re-applying an already-redeemed code is rejected | `BR-KB-004` | `[req-neg]` |
| Applying a second code **replaces** the first (stacking off) | `BR-KB-007` | functional (config-driven) |
| Stacking **on** (config) → both codes apply | `BR-KB-007` | functional, `@low-confidence` (config variant) |
| B2B customer below €20 is **accepted**; retail below €20 rejected | `BR-KB-011` | decision-table (segment) |
| `  save10 ` matches `SAVE10` (trim + case-insensitive) | `BR-KB-014` | boundary/EP |

Every one carries a `# rule: BR-KB-nnn` comment through to the `.feature` and the coverage
matrix, and the run manifest records them:

```jsonc
"design": { "knowledgeApplied": ["BR-KB-004", "BR-KB-007", "BR-KB-011", "BR-KB-014"] }
```

An **empty** `knowledgeApplied` on a domain this rich is itself the signal the shared contract
promises: the knowledge base is thin, not the feature simple.

## The learning loop, concretely

`BR-KB-004` shows the loop that makes this real (see its provenance line): a tester twice
corrected a generated book that let a code be reused. `feedback` stored both corrections,
promoted the pattern to `BR-KB-004` (≥ 2 recurrences, human-validated, D22), and `rag-build`
indexed it. The **next** `istqb-design` run on any discount story now retrieves `BR-KB-004` by
ID and emits the single-use negative condition — a measurable, cited improvement, not a hope
that raw examples re-apply themselves.

## What stays honest

- A rule that **contradicts** the US is raised as a question (`need-understanding`), never
  applied silently — the US wins unless a human overrides.
- A promoted, human-validated rule is **project truth**, not an `[assumption]`; only genuinely
  uncertain rules inherit `@low-confidence`.
- Nothing here needs a network or an API key: the knowledge base is git-versioned markdown the
  team owns (D23), retrieved with plain file reads.
