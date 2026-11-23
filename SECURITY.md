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

Branch protection on the default branch, 2FA for maintainers, pinned GitHub Actions, signed releases, and a second administrator able to revoke access **are being put in place as part of the M0 exit criteria** (the original checklist is archived in `docs/archive/M0-CHECKLIST.md`) — do not assume they are all active until that checklist says so.
