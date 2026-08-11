---
name: report
description: Project the QAIA journey into the standardized run manifest (.qaia/reports/<US-ID>/manifest.json) - the single machine-readable output contract every QAIA plugin shares, carrying normalized counts, coverage, confidence and provenance. Use after generating or exporting a test book, or when another plugin needs a uniform view of the run.
---

# report — the standardized run manifest

Follow the shared contract in `../README.md`. This skill produces the **one envelope every
QAIA plugin shares**: `.qaia/reports/<US-ID>/manifest.json`, defined by
`../../OUTPUT-CONTRACT.md` (that path is in the QAIA source repository, not in the installed plugin — the fields it defines are restated wherever this skill needs them). It never invents data — it *projects* the existing
journey artifacts into the common schema so `qaia-score`, an export, or CI can read any run
the same way.

## Prerequisite

A generated test book in `.qaia/testbooks/<US-ID>/` (with its `synthesis.md`,
`coverage-matrix.md`, and the `03-design.md` / `04-priorities.md` checkpoints). If it is
absent, say which step is missing and offer `testbook-generate` — never emit a manifest with
guessed counts.

## Steps

1. **Read the source artifacts**, never re-generate them:
   - the `.feature` files (count scenario blocks, priority/`@negative`/`@smoke`/Outline tags,
     technique tags, `@oracle:*` provenance);

   **`total` counts executable cases, not blocks.** A `Scenario Outline` with N `Examples` rows
   counts N — that is what a runner will execute, and what `testbook-export` already projects as
   N rows. `outlines` carries the number of un-expanded blocks. Counting blocks instead made a
   book of 10 Outlines × 6 examples read as 10 scenarios in the manifest and 60 rows in the
   reviewer's spreadsheet, with every ratio — negative, low-confidence, `byPriority` — computed
   on the wrong denominator, and `aptitude-gate` deciding a release on it (2026-08-10). The
   shipped scorer exposes both under `executableCases` and `scenarios`; when it has run, take
   `total` from `executableCases` rather than recounting.
   - `coverage-matrix.md` (AC covered, condition coverage);
   - `03-design.md` (`[req-neg]` conditions → `reqNegTotal`);
   - `synthesis.md` and `02-understanding.md` (open questions, assumptions, `simulated`,
     low-confidence);
   - `03-design.md` and the `# rule: BR-KB-nnn` scenario comments → `design.knowledgeApplied`
     (the knowledge-base rules that shaped the book — the provenance that shows the team's
     own rules were actually applied, not merely available).
1b. **Count the level tags → `design.byLevel`** (contract 1.1, [ADR 0008](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0008-test-level-is-a-design-property.md)). Closed keys
   `e2e` / `api`, counted on the **same denominator as `scenarios.total`** — an Outline with N
   `Examples` rows contributes N to its level, exactly as it contributes N to the total. The two
   must therefore sum to `total`; the shipped validator rejects a manifest where they do not.

   **Emit the block only if every scenario carries a level tag.** A book generated before
   2026-08-11, or hand-edited, may have scenarios without one: in that case **omit `byLevel`
   entirely** and say which scenarios lack the tag. The contract makes it optional precisely so
   that a partial count is never shipped — a `byLevel` covering 18 of 22 scenarios would read as
   a coverage-by-level statement that nobody established, which is worse than its absence.

2. **Compute the counts** — do not estimate. Every number in the manifest must equal what the
   artifacts contain: the negative ratio is `@negative` blocks / all blocks (the single
   definition given by `testbook-generate`), `reqNegCovered/reqNegTotal` is the negative-path
   coverage gate of [ADR 0001](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0001-negative-coverage-gate.md), `byPriority` sums to
   `total` minus the excluded `@smoke` journey per the counting rules of `testbook-generate`.
3. **Merge, don't clobber** (contract rule 2). If `manifest.json` already exists, load it,
   replace only the `design` section and `openArbitrations`, append this skill to
   `producers[]`, and add any new `artifacts[]` entries — leaving `execution`, `gate`, and a
   human-set `status` untouched. On a first-ever write, **omit `gate` entirely** (not
   `null`) — the schema treats its absence as "not yet scored"; only `qaia-score` ever writes
   this key (contract rule: no producer self-scores).
4. **Fill `openArbitrations`** from every still-pending `⚠ VALIDATION` point: `[open]`
   questions, `simulated` defaults, waivers awaiting confirmation — each with its
   `sourceCheckpoint`. A non-interactive run surfaces all its `simulated` entries here.
5. **Write** `.qaia/reports/<US-ID>/manifest.json` (create the directory). On a surface
   without file tooling, emit the JSON as a fenced block and tell the user where to save it.
6. **Report** the headline line to the user: US-ID, scenarios by priority, **by level**, AC coverage,
   negative-path gate (`reqNegCovered/reqNegTotal`), open arbitrations count — and remind
   them the `gate` verdict is filled by `qaia-score`, not here.

## Guardrails

- **Never self-score.** This skill writes `design`, `artifacts`, `openArbitrations`,
  provenance — never the `gate` block (shared contract rule 3: the skill never self-validates;
  scoring is a separate plugin).
- **No secrets, no PII, no raw source** in the manifest — counts, IDs, paths, verdicts only
  (contract principle 5). If a title or path would leak sensitive data, redact it.
- **Counts must match the book.** If the manifest and the artifacts disagree, the artifacts
  win: stop and surface the discrepancy rather than writing numbers that lie (same rule as
  `testbook-export`).
- **Contract version.** Always stamp `"contract": "1.0"`; if `../../OUTPUT-CONTRACT.md` has
  advanced, follow its current version and note the bump.
