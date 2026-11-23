# qaia-playwright

QAIA automation plugin: turn a Gherkin test book into **native Playwright tests** (Page Object Model as fixtures), with requirement traceability — plus contract probing, captured-traffic regression and defect reports. **Web-first.**

**Status: 0.3.2, 2 skills.** The skills codify the patterns proven end-to-end in [`examples/medibook/`](../../examples/medibook) (26 tests across 7 project types, 32 executions — the e2e suite runs on desktop and mobile) and [`examples/expense-demo/`](../../examples/expense-demo) (56 tests, finance/HR domain).

## Install

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-playwright@qaia
/reload-plugins
```

## Skills

| Skill | Purpose |
|---|---|
| `automate` | Gherkin test book → native Playwright (POM-as-fixtures), E2E web + API, traceable to `@QAIA-*` IDs |
| `probe` | The app's own documentation against its real behaviour. Four pages: adversarial probing of a self-hosted app against its documented contract (findings become tagged Gherkin regressions, never a live fix — **self-hosted only**); non-regression conditions from a user-provided HAR (PII/secrets masked before any write, never a live capture); production signals attached as evidence to a book's open questions; and the defect report a developer can act on |

**Merged in 0.3.0 — four into one.** `contract-probe`, `traffic-replay`, `defect-report` and
`signal-ingest` (from `qaia-core`) became the pages of `probe`, under `skills/probe/references/`,
**moved rather than rewritten**; their fixtures are under `skills/probe/fixtures/`.

**Deleted in 0.2.0 — ten skills.** `a11y-audit`, `security-surface`, `usability-heuristic-review`,
`perf-check` and `visual-check`: five distinct disciplines, each needing real expertise, none ever
validated by external evidence. `locator-repair`, `flaky-detect`, `run-report`, `confirm-fix` and
`impact-select`: real needs, but CI tooling around Playwright that belongs to whoever owns the
runner. `automate` now merges the `execution` section of the run manifest itself (step 9).

## Design commitments

- **POM as fixtures** (D34): page objects hold selectors, tests hold assertions.
- **Native Playwright, no Cucumber layer** (D5): the Gherkin book is the human-readable source; tests reference its stable scenario IDs.
- **Web-first** (D100): mobile = browser emulation; native iOS/Android is out of scope (would need Appium).
- **Self-hosted for adversarial probing** (D35): shared public demos forbid it.
- Generated tests are **autonomous outside the Claude session** — they run in the user's own CI.
- **`probe` never captures live traffic** (issue #39): input is a HAR the user already
  has, never a proxy/MITM/browser automation run by the skill; PII and secrets are masked
  before any write (D37 discipline extended to HTTP traffic).

See [`examples/medibook/`](../../examples/medibook) for the full worked reference.
