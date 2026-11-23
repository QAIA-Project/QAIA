# Changelog

What changed in each version of the three plugins, newest first. The version a user gets is the
`version` field of each `plugins/<name>/.claude-plugin/plugin.json`; the plugins are versioned
independently (SemVer, pre-1.0: a minor bump may remove things). Dates are the commit dates on
`main`. The rationale behind each change is in the commit it cites, and before 2026-11-23 also in
[`docs/DECISIONS.md`](docs/DECISIONS.md) (frozen since).

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This file was
written on 2026-11-23 and reconstructed from the git history for earlier versions; versions before
the redesign of 2026-08-24 are summarised rather than itemised.

## 2026-11-23 — tag `v0.2.0-prealpha` · `qaia-core` 0.6.3 · `qaia-playwright` 0.3.2 · `qaia-score` 0.3.3

The second tag of the repository, and the first since the redesign: 4 skills in 3 plugins.

No behaviour change in any skill. Every document of the repository was re-read against the
product as it stands; what had gone stale was corrected or marked as dated.

### Changed
- **All plugins** — the shipped copy of the output contract (`OUTPUT-CONTRACT.md`) names the
  current skills (`generate`, `automate`, `judge`) instead of the ones merged since; it explains
  that `judge` still signs `scoredBy` with the former name of its step.
- **`qaia-core`** — the shared journey contract (`skills/README.md`) no longer describes a
  `feedback/` folder written by a skill deleted in 0.5.0, nor refers to the deleted `qaia` router
  or to the former step skills by name. The usage guidance of the README counts one `generate`
  journey instead of six commands, and says its token cost has not been re-measured (#96).
- **`qaia-score`** — the README and `skills/README.md` describe one skill and its five pages,
  not "four skills"; the universal-scale figure is the current one (104 PASS on the pinned
  244-file corpus), the former one (0 PASS on 257 files) dated.

### Fixed
- `eval/tools/validate_manifest.py` (maintainer tooling, not shipped) accepts `judge` as a
  checking skill: a manifest signed `qaia-score:judge` was refused as a producer scoring itself.

### Documentation, outside the plugins
- README (EN/FR), CONTRIBUTING, SECURITY (hardening table checked against the repository: branch
  protection and signed releases are **not** active), PILOT-KIT (it still told pilots to run
  `/qaia-core:hello` and `us-ingest`, both deleted), ROADMAP, DEMO-TARGETS, the competitive
  analysis, ADRs 0001/0003/0007, the site and `llms.txt`, the outreach drafts (three directory PRs
  reported "open" had been closed unmerged since August), and the example READMEs.
- The ~2.9× token-cost figure is now dated everywhere it appears: measured in July 2026 on the
  six-skill journey, not re-measured since the merge (#96).
- `mcp-bridge/README.md` states a real gap: the bridge serves `SKILL.md` files only, so a client
  receives none of the step pages the merged skills depend on (#122).
- New issues from the pass: #122 (the bridge), #123 (timing discipline, proportion against a
  capped deduction), #124 (branch protection and signed releases, a maintainer decision).
- This changelog.

### Repository
- The two branches that had never reached `main` are merged and every branch is deleted.
  `claude/iats-open-source-prompt-hf5d2j` was a second implementation of #112 (a capped
  deduction): its code was **not** kept, because the two rules merged without conflict and would
  have counted each wait twice; its report is kept as a trace and the choice is open in #123.
  `claude/ai-content-similarity-test-n9qghq` was an experiment unrelated to QAIA (similarity and
  NLI on AI-generated French text), moved to `eval/nli-similarity-2026-10-05/`.

## 2026-11-23 — product development resumes

### `qaia-score` 0.3.2 — `b2a79cb`
- **Changed** — the automation rubric gains a universal dimension, *timing discipline*: a test
  that waits a fixed time (`waitForTimeout`, `networkidle`) loses points, and a wait in a shared
  hook counts against every test of its file (#112). Measured first on six suites written by
  others: none scores 100 any more. A second rule ("every assertion is weak") was tried and
  withdrawn — its only hit on six suites was a false positive.

### `qaia-core` 0.6.2 — `842d578`, `72d5797`
- **Added** — emission rule 8: every scenario carries `# condition: ID` above its tags, so a
  refusal condition can be matched to the scenario that discharges it **at its level** (#107). A
  new check, `eval/tools/check_level_discharge.py`, enforces it on the reference pairs.
- **Fixed** — two pages of `generate` contradicted each other on when a text-field condition is a
  required refusal; the closed definition of `negative-ratio.md` now wins.

### `qaia-core` 0.6.1 · `qaia-playwright` 0.3.1 — `801c1eb`
- **Changed** — `probe` probes neighbouring promises *together*, by pairs: the defect it had missed
  on the first blind run was a composition of two (#120).
- **Changed** — `generate` no longer proves a partial update with a field the resource already
  carries, and treats a client-supplied id of another type as its own test class (#121).

### Repository, same day
- The foreign corpus behind the dashboard is pinned commit by commit — 15 of 15 digests identical
  to the freeze; the default rubric scores **104 / 244** on it (#119).
- The two shipped Playwright suites (`booking-api-demo`, `site-qa`) run in CI, against the site
  exactly as `pages.yml` publishes it (#108).
- Planning documents archived, `docs/STATUS.md` reduced to a two-number dashboard,
  `agents-tier/` deleted, `DECISIONS.md` frozen at D203.

## 2026-11-23 — `qaia-core` 0.6.0 · `qaia-playwright` 0.3.0 — `f45c004`

### Changed
- **`probe` absorbs four skills**: `contract-probe`, `traffic-replay`, `defect-report` and
  `signal-ingest` (the last from `qaia-core`) become its pages, moved rather than rewritten.
  **7 skills → 4** (#118).

## 2026-10-26 — `qaia-core` 0.4.0, 0.5.0 · `qaia-playwright` 0.2.0

### Changed
- **`qaia-core` 0.4.0 — `d13bbb1`** — ten journey skills (`us-ingest`, `openapi-ingest`,
  `us-review`, `need-understanding`, `istqb-design`, `oracle-generate`, `prioritize`,
  `testbook-generate`, `report`, `testbook-export`) become the steps of one skill, `generate`.

### Removed
- **`e2df967` — seventeen skills deleted in one commit.** `qaia-core` 0.5.0: `hello`,
  `qaia-help`, the `qaia` router, `rag-build`, `feedback`, `test-plan-and-closure`.
  `qaia-playwright` 0.2.0: `a11y-audit`, `security-surface`, `usability-heuristic-review`,
  `perf-check`, `visual-check`, `locator-repair`, `flaky-detect`, `run-report`, `confirm-fix`,
  `impact-select`. The `qaia-testdata` plugin and its `dataset-generate` skill go with them.
  Reasons per group are in [`plugins/qaia-core/CATALOGUE.md`](plugins/qaia-core/CATALOGUE.md).

## 2026-10-16 — `qaia-score` 0.3.1 — `c25b8dd`

### Security
- `judge` declares least-privilege permissions and an explicit boundary for injected
  instructions and external data (#114, gates 2 and 3).

## 2026-08-24 — the redesign begins · `qaia-core` 0.3.0 · `qaia-score` 0.3.0 — `e4fb308`

### Changed
- **`judge` absorbs five skills**: `testbook-validate` (from `qaia-core`), `testbook-score`,
  `automation-score`, `spec-suite-drift`, `aptitude-gate`, moved rather than rewritten.
- The structural scorer's default becomes the universal scale: books written outside QAIA are
  judged on Gherkin's own conventions, `--profile qaia` is the opt-in overlay. Plan:
  [`docs/superpowers/specs/2026-08-24-qaia-refonte-design.md`](docs/superpowers/specs/2026-08-24-qaia-refonte-design.md).

## Before the redesign — July and August 2026

Summarised; each line is one or more versions, the commit messages and `docs/DECISIONS.md` carry
the detail.

- **2026-08-09 — `qaia-score` 0.2.4** — `spec-suite-drift`, the 36th skill. The deterministic
  scorers start shipping as pinned Python in `plugins/qaia-score/scripts/` (ADR 0002) instead of
  being rebuilt from prose in each session.
- **2026-08-08 — `qaia-core` 0.2.31–0.2.35, `qaia-playwright` 0.1.21–0.1.27, `qaia-score`
  0.2.1–0.2.3** — the output contract ships with every plugin; an OpenAPI spec becomes a second
  entry point; test plan and closure report; `defect-report`, `impact-select`, `confirm-fix`.
- **2026-08-01 — `qaia-core` 0.2.27–0.2.30, `qaia-playwright` 0.1.18–0.1.20, `qaia-score`
  0.1.8–0.2.0** — oversized skills split into pages; the judge of generated test code reaches the
  product.
- **2026-07-28 to 2026-07-31 — `qaia-core` 0.2.18–0.2.26, `qaia-playwright` 0.1.11–0.1.17,
  `qaia-score` 0.1.5–0.1.7** — a real k6 load script; cold reviews by four business personas;
  the structural score gets its own block in the manifest; the benchmark against a direct prompt
  (~2.9× the tokens).
- **2026-07-25 to 2026-07-26 — `qaia-core` 0.2.9–0.2.17, `qaia-playwright` 0.1.2–0.1.10,
  `qaia-score` 0.1.1–0.1.4** — first public version, three plugins and 23 skills (`ec0529e`);
  then Xray and TestRail exports, `flaky-detect`, `locator-repair`, `traffic-replay`,
  `contract-probe`.
- **2026-08-07** — tag `v0.1.0-prealpha`, the first tag, published as a GitHub pre-release.
