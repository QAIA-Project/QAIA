# qaia-mcp-bridge (opt-in, not installed by any qaia-* plugin)

**Read this before installing.** This is a standalone MCP server that lets a non-Claude MCP
client (Cursor, GitHub Copilot, or any other MCP-capable assistant) read QAIA's skill content
and call two of QAIA's deterministic scoring tools. It is **never** installed automatically by
`qaia-core`, `qaia-playwright` or `qaia-score`, is not listed in
`.claude-plugin/marketplace.json`, and CI explicitly forbids anything like it from living under
`plugins/` (see `.github/workflows/ci.yml`). You choose to install and run this, or you don't.

Origin and design rationale: `docs/adr/0003-mcp-bridge-scoping.md` (issue #42). Governed by
ADR 0002's opt-in-tier rules: separate package, documents what it executes (this file), and is
subject to the same adversarial-review discipline as every other opt-in component (`#29`,
`#30`).

## What it actually does — the full list, nothing implicit

| Tool | Reads/writes | Network | Notes |
|---|---|---|---|
| `list_skills` | Reads `plugins/*/skills/*/SKILL.md` frontmatter | none | Read-only enumeration |
| `get_skill_content` | Reads one `SKILL.md`, by an id `list_skills` returned | none | Path is re-validated to stay inside `plugins/`; a client cannot supply an arbitrary path |
| `get_output_contract` | Reads `docs/OUTPUT-CONTRACT.md` | none | Read-only |
| `score_feature` | Writes the Gherkin **content you pass in** to a fresh temp dir, runs `eval/tools/structural_score.py` on it, deletes the temp dir | none | Never reads a path you supply — content in, content out |
| `validate_manifest` | Same pattern, wraps `eval/tools/validate_manifest.py` | none | Content in, content out |

It never reads `.env`, credentials, or anything outside this repo checkout. It never writes
anywhere except its own short-lived temp directory (created and deleted per call). It never
opens a network connection.

## Install

Not published to npm. Point your MCP client's config at this checkout directly:

```json
{
  "mcpServers": {
    "qaia-bridge": {
      "command": "node",
      "args": ["/absolute/path/to/QAIA/mcp-bridge/src/server.js"]
    }
  }
}
```

(Cursor: Settings → MCP → add server. Copilot: check your client's current MCP config location
— this project does not track editor-specific instructions that change independently of QAIA.)

Requires Node.js ≥18 and a `python3`/`python` on PATH (used only for the two wrapped scripts;
override with the `QAIA_PYTHON` environment variable if neither name resolves on your system).

```
cd mcp-bridge
npm install
npm start   # or point your MCP client at src/server.js directly, per the config above
```

## What this is NOT

- Not a replacement for using QAIA inside Claude Code — the skills are still designed and
  proven there first (D29). This bridge is a secondary access path for a different assistant,
  not the primary product.
- Not an autonomous agent. It never decides anything, never chains tool calls on its own —
  every call is one request from the MCP client (Cursor/Copilot's own model), one response.
- Not a guarantee of identical behavior to Claude Code. The two tools it wraps
  (`structural_score.py`, `validate_manifest.py`) are deterministic and behave identically
  everywhere; the *skill content* served by `get_skill_content` is the same Markdown Claude
  Code reads, but how faithfully a different model follows it is untested and unverified by
  this project (see `docs/adr/0003-mcp-bridge-scoping.md` for the honest scope of that claim).

## Development

```
npm install
npm test     # eval/tools/structural_score.py and validate_manifest.py fixtures round-tripped through the wrappers
```
