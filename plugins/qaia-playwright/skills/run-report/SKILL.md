---
name: run-report
description: Produce an execution report from a Playwright run in the formats the QA profession consumes - JUnit XML, Cucumber JSON, and a self-contained HTML summary - with requirement traceability. Use after running an automated suite, when a CI dashboard or an ALM needs the results, or when someone asks what the last run actually produced.
---

# run-report — execution reporting

The three reporting formats real QA toolchains actually ingest, plus requirement traceability.

## Outputs

- **JUnit XML** — for CI dashboards and most ALMs. Native Playwright reporter.
- **Cucumber JSON** — for import into Xray (git-master mode: the repo is the source of truth)
  and BDD reporters. **Playwright has no Cucumber JSON reporter**; this is a conversion QAIA
  performs from the native `json` reporter. Procedure and field mapping:
  `references/cucumber-json.md`.
- **Self-contained HTML** — human-readable summary: pass/fail by scenario ID, per-type breakdown
  (e2e/api/a11y/perf/security), and the AC → scenario → test → result traceability table.
  Structure: `references/html-summary.md`.
- **Standardized run manifest** — merge the results into `.qaia/reports/<US-ID>/manifest.json`
  per the shared output contract ([`docs/OUTPUT-CONTRACT.md`](https://github.com/QAIA-Project/QAIA/blob/main/docs/OUTPUT-CONTRACT.md)), so scoring and dashboards read
  execution the same way they read the test book.

## Steps

1. Configure the reporters in `playwright.config.js`, and map test titles' `@QAIA-*` tags to
   requirement IDs:

   ```js
   reporter: [
     ['list'],
     ['junit', { outputFile: 'junit.xml' }],
     ['json',  { outputFile: 'results.json' }],  // source for the Cucumber conversion
   ],
   ```

2. After a run, produce the three outputs. **Never fabricate a result the run did not
   produce** — a report is downstream of an execution, and a report written without one is the
   single most damaging artifact this skill can emit.
3. **Merge the `execution` section** into `.qaia/reports/<US-ID>/manifest.json` (contract 1.0).
   Exact shape below. Load the existing manifest, replace **only** the `execution` section,
   append this skill to `producers[]`, add the JUnit/Cucumber/HTML files to `artifacts[]`, and
   leave `design`, `gate` and a human-set `status` untouched (contract rule 2 — merge, never
   clobber). If no manifest exists yet, create one with just the shared header + `execution` and
   note that `qaia-core:generate` (step 8) will fill `design`.
4. If a publication target is configured (Xray), offer to publish — with the user's go, in
   git-master mode (the repo is the source of truth).

## The `execution` block this skill owns

```json
"execution": {
  "total": 31, "passed": 31, "failed": 0, "blocked": 0,
  "byType": { "e2e-desktop": 12, "e2e-mobile": 8, "api": 6, "a11y": 3, "perf": 1, "security": 1 },
  "traceability": { "scenariosAutomated": 18, "scenariosTotal": 22 }
}
```

- `total` = `passed + failed + blocked`. If it does not, the report is wrong — check that
  skipped tests were counted as `blocked` and not silently dropped.
- `blocked` covers skipped, fixture-failed and did-not-run. A test that never executed is
  **never** a pass, and Playwright's `skipped` maps here rather than disappearing.
- `byType` keys come from the Playwright **project** names, so the split is read from the run
  rather than guessed. Its values sum to `total`.
- `traceability.scenariosTotal` is the count from the test book, not from the spec files —
  the whole point of the pair is to expose the gap between what was designed and what was
  automated. `scenariosAutomated` counts distinct `@QAIA-<US>-<NNN>` ids seen in the run, so a
  Scenario Outline with 2 examples counts as **one** scenario, matching how the test book counts
  it — otherwise automating a single outline would inflate the ratio.

## Guardrails

- Distinguish clearly: generation report (coverage) ≠ execution report (this) ≠
  requirement-coverage matrix.
- Blocked/skipped tests are reported as such, never as passed — in the HTML and in the manifest's
  `blocked` count alike.
- A flaky test (passed on retry) is reported as **passed with a flake flag**, never as a clean
  pass. Where the run used `retries: 0`, say so — "no flakes" from a suite that never retried is
  an absence of measurement, not a result.
- **Never write the `gate` block** — the manifest's verdict is owned by `qaia-score` (contract:
  no producer scores itself). The manifest carries counts and paths only: no secrets, no
  environment URLs, no PII.
