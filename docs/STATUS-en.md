# QAIA — dashboard

Two numbers, and only two: the ones the [redesign spec](superpowers/specs/2026-08-24-qaia-refonte-design.md)
keeps because neither depends on anything QAIA produced itself. Work order is in
[`ROADMAP.md`](ROADMAP.md) (French); the former chronological record is archived in
[`archive/STATUS-en.md`](archive/STATUS-en.md).

*Last updated: 2026-11-23.*

## 1. PASS rate on test books QAIA did not write

| | |
|---|---:|
| **PASS, default rubric** | **104 / 244 (42.6 %)** |
| CONCERNS / FAIL / not scoreable | 72 / 58 / 10 |
| corpus | the 15 repositories frozen on 2026-08-09, **each pinned to a commit**: 15 of 15 digests identical to the freeze |
| spec reference, replayed on this corpus | 96 (the level of the `--third-party` opt-in); target: the default at least that high |

**Target met: 104 ≥ 96.** The former figures 101 and 107 were measured on a corpus that had
already drifted (257 files); they do not describe this one
([#119](https://github.com/QAIA-Project/QAIA/issues/119),
[report](../eval/corpus-remeasure-2026-11-23/REPORT.md), French).

Replay:

```
python eval/tools/fetch_corpus.py eval/gherkin-external-2026-08-09/corpus.json <dir>
python eval/tools/score_corpus.py <dir>
```

Latest changes, on the frozen corpus: a docstring is no longer read as scenarios (98 → 104),
after the two duplicate-detector fixes of 2026-08-24 (96 → 98).

## 2. Number of real users

| | |
|---|---:|
| **human pilots who ran the journey** | **0** |
| GitHub stars / forks / watchers | 0 / 1 / 0 |

The number that matters most, and the only one no commit can move: it depends on someone else
([#89](https://github.com/QAIA-Project/QAIA/issues/89)). The pilot kit is
[`PILOT-KIT.md`](PILOT-KIT.md).

## What the product is today

**4 skills, 3 plugins**: `qaia-core` 0.6.3 (`generate`), `qaia-playwright` 0.3.2 (`automate`,
`probe`), `qaia-score` 0.3.3 (`judge`). Pre-alpha.
