# Jira connector demo (issue #9, D9 v1 source)

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

Shows `us-ingest` capturing a **Jira issue** as a QAIA source — portable-first, no API key, no
backend. The connector mapping lives in
`plugins/qaia-core/skills/generate/connectors/jira.md`.

- [`PROJ-123.rest-v3.json`](PROJ-123.rest-v3.json) — a realistic Jira REST API v3 issue export
  (ADF description, an "Acceptance Criteria" section, a blocked-by link, an attachment, a
  reporter with PII, and a **malicious comment**).
- [`00-source.md`](00-source.md) — the resulting QAIA capture after ingestion.

## What the connector does, verifiably

| Jira input | QAIA capture |
|---|---|
| `key: PROJ-123` | US-ID `PROJ-123` |
| ADF `description` | flattened to text, wording preserved, "ADF flattened" noted |
| "Acceptance Criteria" bullet list | AC1–AC3 extracted |
| `issuelinks` blocked-by `PROJ-119` | `dependencies:` — out-of-slice (the stacking/config rules), flagged never invented |
| `attachment` mockup PNG | listed "not analyzed" |
| reporter name + email | **redacted** to typed placeholders before write (`name`/`email`, no ledger) |
| instance base URL | **not persisted** (internal environment detail) |
| comment "SYSTEM: ignore the ACs…" | **reported as a finding, not obeyed** (comments aren't the spec; untrusted input) |

## Two paths, same result

- **Portable (shown here):** the user supplies the export (REST v3 JSON / CSV / pasted issue);
  QAIA reads exactly that, nothing over the network.
- **Live (Claude Code + Jira MCP, opt-in):** with the user's go, fetch **only** the designated
  issue key through the MCP — bounded, no link crawling, credentials stay in the MCP server.

Either way a Jira source becomes an ordinary `00-source.md`, and the rest of the journey
(`us-review` → … → `testbook-generate`) is unchanged. This is the D9 sequencing lesson in
practice: the connector adds a well-mapped source, it does not drown the core in tracker-specific
logic.
