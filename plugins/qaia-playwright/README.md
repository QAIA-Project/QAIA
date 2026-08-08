# qaia-playwright

QAIA automation plugin: turn a Gherkin test book into **native Playwright tests** (Page Object Model as fixtures), with requirement traceability — plus accessibility, performance and security-surface coverage. **Web-first.**

**Status: 0.1.27, 14 skills.** The skills codify the patterns proven end-to-end in [`examples/medibook/`](../../examples/medibook) (26 tests across 7 project types, 32 executions — the e2e suite runs on desktop and mobile) and [`examples/expense-demo/`](../../examples/expense-demo) (56 tests, finance/HR domain).

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
| `a11y-audit` | axe-core / WCAG 2 A/AA, violations by severity |
| `visual-check` | Playwright screenshot regression, baselines + tolerance, per screen |
| `perf-check` | latency budgets + concurrency integrity; named CT-PT test types (load/stress/spike/soak/scalability), k6 for real load — **self-hosted only** |
| `security-surface` | risk-based (assets → threats → prioritized checks, CT-SEC): auth, IDOR, error handling, enumeration + ZAP baseline — **authorized self-hosted only** |
| `usability-heuristic-review` | Nielsen's 10 heuristics + one cognitive walkthrough (CT-UT), violations by severity — **self-hosted only** |
| `contract-probe` | Adversarial probing of a self-hosted app's real behavior against its own documented contract (README/help/spec) — findings converted to tagged Gherkin regression scenarios, never a live fix — **self-hosted only** |
| `run-report` | JUnit XML + Cucumber JSON + HTML, with traceability |
| `flaky-detect` | Detect pass/fail verdict variance across N ≥ 3 runs of the same code — flag with evidence only, never auto-retry/fix |
| `locator-repair` | Diagnose a test failing on a broken `getByRole`/`getByTestId` locator and propose a candidate fix as a reviewable diff — never applied automatically |
| `traffic-replay` | Derive non-regression conditions (status, response shape, headers, timing) from a user-provided HAR file — PII/secrets masked before any write, never a live capture |

## Design commitments

- **POM as fixtures** (D34): page objects hold selectors, tests hold assertions.
- **Native Playwright, no Cucumber layer** (D5): the Gherkin book is the human-readable source; tests reference its stable scenario IDs.
- **Web-first** (D100): mobile = browser emulation; native iOS/Android is out of scope (would need Appium).
- **Self-hosted for security & load** (D35): shared public demos forbid them.
- Generated tests are **autonomous outside the Claude session** — they run in the user's own CI.
- **`traffic-replay` never captures live traffic** (issue #39): input is a HAR the user already
  has, never a proxy/MITM/browser automation run by the skill; PII and secrets are masked
  before any write (D37 discipline extended to HTTP traffic).

See [`examples/medibook/`](../../examples/medibook) for the full worked reference.
