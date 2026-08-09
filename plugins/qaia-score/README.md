# qaia-score

QAIA scoring plugin: **read-only** quality scoring and release-readiness gating of a QAIA test book or run. Applies the ISTQB-grounded 10-dimension rubric and a PASS/CONCERNS/FAIL/WAIVED aptitude gate over the standardized run manifest (`./OUTPUT-CONTRACT.md`, D39). Scores only — never generates or edits test content (no producer scores itself, rule 3).

**Status: 0.2.4, 4 skills.** Read-only over content: the only file these skills write is `.qaia/reports/<US-ID>/manifest.json`, and only its `gate` block.

## Install

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-score@qaia
/reload-plugins
```

## Skills

| Skill | Purpose |
|---|---|
| `testbook-score` | ISTQB 10-dimension rubric, /20, + top-3 fixes — plus a deterministic structural pass (step 0) separate from the LLM judge |
| `aptitude-gate` | Release readiness verdict — PASS / CONCERNS / FAIL / WAIVED over the score + hard gates |

See [`skills/README.md`](skills/README.md) for the full shared guardrails (read-only, evidence-not-vibes, default-low, human-owns-WAIVED, portability).

## Design commitments

- **No self-scoring** (rule 3): a producer plugin never grades its own output — judgment lives here, separate from `qaia-core`/`qaia-playwright`.
- **Deterministic score, separate from the LLM judge**: `testbook-score` step 0 is a reproducible structural pass (readability, completeness, coherence, traceability, anti-fabrication sniffer, hollow/vague `Then` detectors) — never confused with the semantic LLM verdict.
- **Human owns WAIVED**: a gate is never self-waived; only a recorded human decision (`by`/`reason`/`at`) turns CONCERNS/FAIL into WAIVED.
- **Portable**: no network, no API key, no runtime — reads Markdown/JSON, writes JSON.

See [`examples/scoring-demo/`](../../examples/scoring-demo) for a worked example.
