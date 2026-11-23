# QAIA evaluation harness

Built **before** any generation skill (decision T10). No skill change ships without running this harness.

## Why it exists

Skills are LLM prompts: their behavior is non-deterministic and drifts with every model release. CI validates form only (manifests, Gherkin syntax); this harness is the only thing that measures **quality** — and quality regressions are otherwise silent.

## Contents

| Path | Content |
|---|---|
| `gold-set/` | Original, synthetic user stories (clean-room, MIT-licensed) used as fixed inputs |
| `RUBRIC.md` | The scoring rubric an LLM-judge applies to a generated test book |
| `baselines/` | Scored reference runs per release (created from M1 onward) |
| `tools/` | The deterministic checks and scorers — `structural_score.py`, `automation_score.py` (shipped copies in `plugins/qaia-score/scripts/`, synced by `ship_scorers.py`), the `check_*.py` gates and their `selfcheck_*.py`, run by `make check` and the CI |
| `gherkin-external-2026-08-09/` | The foreign corpus behind the dashboard's first number: 244 `.feature` files from 15 repositories, each pinned to a commit (`fetch_corpus.py`, `score_corpus.py`) |
| `<campaign>-<date>/` | One folder per measurement campaign, each with its `REPORT.md` — dated, kept as measured, never rewritten |

## Release ritual (runs in the maintainer's Claude session — decision D6)

1. For each gold set US, run the generation journey end-to-end with the candidate skills — **3 independent runs per US** (non-determinism: we score the median, and flag any dimension with a spread > 1 point).
2. Score each generated test book with `RUBRIC.md` using an LLM-judge in a **fresh session** (no context from the generation session).
3. Compare medians to the previous baseline in `baselines/`. Any dimension dropping ≥ 1 point blocks the release.
4. Commit the new scores to `baselines/` with the plugin versions and model used.

**Honest state (2026-11-23): this ritual has not been run since July 2026** — the last baseline
added to `baselines/` is dated 2026-07-29. The versions since `qaia-core` 0.3.0 (the merges into
`generate`, `judge` and `probe`) were guarded by the deterministic gates of `make check`, the
foreign-corpus measure of the dashboard, and targeted campaigns, not by three runs per gold-set
story. The skills were moved rather than rewritten, which is why that was judged acceptable; it
is still a gap, and re-running the ritual on the merged `generate` belongs with the cost
measurement of [#96](https://github.com/QAIA-Project/QAIA/issues/96).

## Contributing to the gold set

New gold set US are very welcome (easier to review than skills — see `CONTRIBUTING.md`). Requirements: original content (no material from an employer or a copyrighted spec), realistic acceptance criteria (6+), at least one deliberately ambiguous point (to exercise step 3 of `generate`, understanding the need), and domain variety. (The "regulated-health niche" this line used to ask for was retired, D114.)
