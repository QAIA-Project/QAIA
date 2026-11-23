# Security Policy

## Reporting a vulnerability

**Do not open a public issue for security problems.**

Report privately via **GitHub Security Advisories**: *Security* tab → *Report a vulnerability* on this repository. If that tab is unavailable, open a regular issue titled "Security contact request" **containing no vulnerability details** — the maintainer will reply with a private channel.

You should receive an acknowledgement within **7 days**. QAIA has a single maintainer; triage of complex reports may take longer — the acknowledgement will say so.

## Scope

Reports are especially welcome on:

- **Skill/command injection**: any way a skill, command, ingested document, or knowledge-base file can make the user's Claude session perform unintended actions (data exfiltration, unwanted tool calls, scope escalation);
- **Supply chain**: marketplace manifest tampering, CI workflow weaknesses, dependency risks;
- **Generated code**: patterns in generated Playwright tests that could leak secrets (credentials in code, `.env` mishandling).

## Out of scope

- Vulnerabilities in Claude Code, the Claude models, or third-party MCP servers (report to their vendors);
- Issues requiring a compromised user machine;
- The inherent fact that content sent to a Claude session is processed by Anthropic (documented in the README).

## Hardening commitments

State as of 2026-11-23, checked against the repository rather than copied from a plan (the original M0 checklist is archived in `docs/archive/M0-CHECKLIST.md`):

| Commitment | State |
|---|---|
| GitHub Actions pinned by commit SHA | **active** — every `uses:` in `.github/workflows/` |
| Scorers shipped as readable, pinned Python, identical to their tested source | **active** — checked in CI |
| Branch protection on `main` | **not active** (the API answers "Branch not protected") |
| Signed releases | **not active** — the tags (`v0.1.0-prealpha`, `v0.2.0-prealpha`) are annotated but not signed |
| 2FA for maintainers, a second administrator able to revoke access | not verifiable from the repository; do not assume them |

Do not assume a commitment marked "not active" protects you. Activating them is a decision for the maintainer, tracked in [#124](https://github.com/QAIA-Project/QAIA/issues/124).
