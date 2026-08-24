# qaia-score

QAIA scoring plugin: **read-only** quality scoring and release-readiness gating of a QAIA test book or run. Applies the ISTQB-grounded 10-dimension rubric and a PASS/CONCERNS/FAIL/WAIVED aptitude gate over the standardized run manifest (`./OUTPUT-CONTRACT.md`, D39). Scores only — never generates or edits test content (no producer scores itself, rule 3).

**Status: 0.3.0, 1 skill.** Read-only over content: the only file these skills write is `.qaia/reports/<US-ID>/manifest.json`, and only its `gate` block.

## Install

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-score@qaia
/reload-plugins
```

## Skills

| Skill | Purpose |
|---|---|
| `judge` | **The single entry point.** Judges a test book, a Playwright suite, or a specification against the suite that claims to cover it — whoever wrote them. Runs the pinned deterministic scorers first, then the semantic checklist, and returns a PASS/CONCERNS/FAIL gate **with its reason named**. Never edits what it judges. |

`judge` absorbed four skills of this plugin plus `testbook-validate` from `qaia-core` on
2026-08-24 — `testbook-score`, `automation-score`, `spec-suite-drift`, `aptitude-gate`. **Their
bodies were moved, not rewritten**, into `skills/judge/references/`: what had been proven stayed
proven. They were pipeline stages, not separate competences, and nothing was gained by making a
reader discover five names to answer one question.

| Ce que vous cherchiez | Où c'est maintenant |
|---|---|
| `testbook-score` | `judge` → `references/scoring-testbook.md` |
| `automation-score` | `judge` → `references/scoring-automation.md` |
| `spec-suite-drift` | `judge` → `references/spec-vs-suite.md` |
| `aptitude-gate` | `judge` → `references/release-gate.md` |
| `testbook-validate` (was in `qaia-core`) | `judge` → `references/auditing-a-test-book.md` |

See [`skills/README.md`](skills/README.md) for the full shared guardrails (read-only, evidence-not-vibes, default-low, human-owns-WAIVED, portability).

## Design commitments

- **No self-scoring** (rule 3): a producer plugin never grades its own output — judgment lives here, separate from `qaia-core`/`qaia-playwright`.
- **The universal scale is the default, and this is the plugin's whole point.** Judging books this project did not write is first-class, not a mode. Pointed at 257 Gherkin books written elsewhere, the old default returned **0 PASS** because 493 of its 666 findings were about conventions that do not exist in Gherkin; the universal default returns **102 PASS, median 77, 150 findings** on the same corpus. `--profile qaia` is the opt-in overlay, for books that carry `@QAIA-*` tags.
- **Deterministic score, separate from the LLM judge**: `judge` step 1 is a reproducible structural pass (readability, completeness, coherence, traceability, anti-fabrication sniffer, hollow/vague `Then` detectors) — never confused with the semantic LLM verdict.
- **Human owns WAIVED**: a gate is never self-waived; only a recorded human decision (`by`/`reason`/`at`) turns CONCERNS/FAIL into WAIVED.
- **Portable**: no network, no API key, no runtime — reads Markdown/JSON, writes JSON.

See [`examples/scoring-demo/`](../../examples/scoring-demo) for a worked example.
