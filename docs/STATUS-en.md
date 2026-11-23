# QAIA — dashboard

Two numbers, and only two: the ones the [redesign spec](superpowers/specs/2026-08-24-qaia-refonte-design.md)
keeps because neither depends on anything QAIA produced itself. Work order is in
[`ROADMAP.md`](ROADMAP.md) (French); the former chronological record is archived in
[`archive/STATUS-en.md`](archive/STATUS-en.md).

*Last updated: 2026-11-23.*

## 1. PASS rate on test books QAIA did not write

| | |
|---|---:|
| **PASS, default rubric** | **115 / 269 (42.8 %)** |
| CONCERNS / FAIL / not scoreable | 76 / 63 / 15 |
| corpus | the 15 repositories frozen on 2026-08-09, **replayed on 2026-11-23** |
| spec reference | 101 / 244 on 2026-08-24, target ≥ 107 |

**These two rows are not comparable.** Six of the fifteen repositories have moved since the
freeze; the replayed corpus holds 269 files, not 244. Until the corpus is re-frozen, the target
can be declared neither met nor missed ([#119](https://github.com/QAIA-Project/QAIA/issues/119)).
On the nine stable repositories alone (145 files): 47 PASS.

Latest change: a docstring is no longer read as scenarios, PASS 109 → 115 on the same corpus
([report](../eval/corpus-remeasure-2026-11-23/REPORT.md), French).

## 2. Number of real users

| | |
|---|---:|
| **human pilots who ran the journey** | **0** |
| GitHub stars / forks / watchers | 0 / 1 / 0 |

The number that matters most, and the only one no commit can move: it depends on someone else
([#89](https://github.com/QAIA-Project/QAIA/issues/89)). The pilot kit is
[`PILOT-KIT.md`](PILOT-KIT.md).

## What the product is today

**4 skills, 3 plugins**: `qaia-core` 0.6.1 (`generate`), `qaia-playwright` 0.3.1 (`automate`,
`probe`), `qaia-score` 0.3.1 (`judge`). Pre-alpha.
