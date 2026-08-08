# qaia-testdata

QAIA test data plugin: generates **rich, business-coherent synthetic datasets** — never real
data, never PII — from a QAIA user story or test book, covering realistic distributions and the
boundary/edge cases the acceptance criteria demand, in a format directly injectable as a
Playwright fixture. Separate plugin by design (decision D16): `qaia-core` only ever produces
small inline examples inside a scenario; this plugin is the standalone dataset producer.

**Status: 0.1.3, 1 skills.** One skill, portable Markdown only — nothing in this plugin auto-executes on install: no hooks, no agents, no MCP server, and the CI fails if any appear. The `fixture/` directory does contain a Playwright spec and config; they are the recorded proof that the skill was exercised, never run by the plugin itself (ADR
0002/D42). The only files it writes are the dataset file(s), a traceability `dataset-map.md`,
and — optionally — the `producers[]`/`artifacts[]` entries of the standard run manifest
(`./OUTPUT-CONTRACT.md`, D39); it never edits `.feature` files or another producer's section.

## Install

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-testdata@qaia
/reload-plugins
```

## Skills

| Skill | Purpose |
|---|---|
| `dataset-generate` | Generate a synthetic, business-coherent dataset (entities + boundary-focused cases) from a US/test book, with an anti-fabrication discipline on invented values, and a documented Playwright fixture-injection pattern |

## Design commitments

- **Never real data, never PII.** Every person-like entity gets a synthetic identity (name
  pattern, `.invalid`-TLD email, `synthetic: true` flag) — a reviewer can tell at a glance this
  is fixture data. Applies with extra weight in the health/regulated niche (D2), identically
  elsewhere.
- **Business coherence, checked not claimed.** Foreign keys resolve, computed totals match the
  rows they summarize, no two facts about the same entity contradict each other — verified, not
  eyeballed.
- **Anti-fabrication (D38) applied to data.** A value the source is silent on is invented for
  fixture purposes only and flagged `synthetic: true`; a genuine ambiguity in the source is
  never resolved silently — it is recorded as a named assumption or, where there is no
  defensible default, built as an explicit `"[open]"` case exposing both interpretations.
- **Injectable via fixtures, no shipped code.** Output is plain JSON (+ optional CSV), consumed
  by a documented `testData` Playwright fixture pattern matching the POM-as-fixtures convention
  (D34) already used by [`examples/medibook/tests/fixtures.js`](https://github.com/QAIA-Project/QAIA/blob/main/examples/medibook/tests/fixtures.js) — the plugin ships the pattern as
  documentation, never as a script it runs itself.
- **Portable.** No network, no API key, no runtime dependency to generate a dataset.

## Worked example

[`fixture/`](fixture/) builds and validates a full synthetic dataset for
[[`eval/gold-set/US-002-dosage-validation.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/gold-set/US-002-dosage-validation.md)](../../eval/gold-set/US-002-dosage-validation.md)
(prescription dosage validation, health domain — no dataset example existed for this US
elsewhere in the repo): 4 synthetic drugs, 3 synthetic physicians, 11 synthetic patients, 20
intake records and 17 boundary-focused cases covering all 8 acceptance criteria — including one
case that deliberately surfaces a genuine AC ambiguity as `"[open]"` instead of resolving it
silently. A real Playwright spec (`fixture/dataset.spec.js`) loads the dataset through a
`testData` fixture and asserts its structure, referential integrity, AC coverage and PII safety
— see [`fixture/VALIDATION.md`](fixture/VALIDATION.md) for what was actually run.
