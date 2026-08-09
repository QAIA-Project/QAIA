# Oracles for testing QAIA's own skills — the landscape, and the corpus that can actually grade us

**Date** 2026-08-09 · Searched: GitHub (by keyword and by name) and the web

## The finding that reframes the search

**Almost every benchmark and leaderboard in this space ranks *models*, not *methods*.** MMLU-Pro,
GPQA, Chatbot Arena, LiveBench, Artificial Analysis — 300+ benchmarks, and not one of them can say
anything about a skill library. Feeding QAIA into them is a category error.

Only one family can grade us: benchmarks carrying **real defects together with the tests that
catch them**. There, the question *"does the condition QAIA derived cover what the oracle test
exercises?"* has an answer rather than an opinion.

## Candidates, verified to exist rather than recalled

| Repository | Stars | Licence | What it supplies |
|---|---:|---|---|
| [`SWE-bench/SWE-bench`](https://github.com/SWE-bench/SWE-bench) | 5 598 | MIT | issue text + patch + `FAIL_TO_PASS` tests |
| [`rjust/defects4j`](https://github.com/rjust/defects4j) | 985 | MIT | 835 real Java bugs, buggy/fixed pair, triggering tests |
| [`soarsmu/BugsInPy`](https://github.com/soarsmu/BugsInPy) | 149 | — | 493 real Python bugs, same shape |
| [`jkoppel/QuixBugs`](https://github.com/jkoppel/QuixBugs) | 145 | MIT | 40 small programs, one-line defects |
| `Tests4Py` | — | — | system-level testing benchmark (paper, arXiv 2307.05147) |

Agent-trajectory benchmarks were checked and set aside for now — [`sierra-research/tau-bench`](https://github.com/sierra-research/tau-bench) (1 367),
[`THUDM/AgentBench`](https://github.com/THUDM/AgentBench) (3 654), [`web-arena-x/webarena`](https://github.com/web-arena-x/webarena) (1 575),
[`ShishirPatil/gorilla`](https://github.com/ShishirPatil/gorilla) (12 989). They score an agent
*acting in an environment*; QAIA's skills produce **documents**, and no environment executes them.
Judging a test book by a trajectory metric would measure the wrong thing convincingly.

## Prior art on exactly our task

**"Otter: Generating Tests from Issues to Validate SWE Patches"** (arXiv 2502.05368) does what QAIA
claims: derive tests from a natural-language issue. That it exists is good news twice — the task is
recognised as real, and there is a published protocol to be compared against rather than a metric
of our own invention. **Reading it before designing our own measurement is the next step**, because
a home-made metric that flatters the tool is the failure mode this whole project exists to avoid.

## The corpus, frozen

`swebench-lite-extract.json` — 30 instances drawn from SWE-bench Lite, MIT, sha256 recorded.

| | |
|---|---:|
| instances | 30 of 300 |
| distinct projects | 9 |
| oracle tests (`FAIL_TO_PASS`) | 59 |

Each instance carries the three things needed to grade QAIA on what it actually promises:

- `problem_statement` — **the input**: a human-written defect report, no code;
- `fail_to_pass` — **the oracle**: the tests that fail before the fix and pass after;
- `test_patch` — **the strong oracle**: the test code that was really added.

**Sampling was wrong on the first attempt and is recorded rather than quietly fixed.** The dataset
is sorted by project, so the first 30 rows gave **2 projects out of 12**. A biased sample reads
like a corpus. Sampling now steps evenly across all 300 positions: 9 projects.

30 rather than 300 is deliberate: a corpus nobody can re-read by hand reads as proof when it is
only volume.

## What this does NOT yet establish

**Nothing about QAIA's quality.** This run found and froze an oracle; it did not run a single skill
against it. The measurement is the next piece of work, and the honest order is:

1. read the Otter protocol and adopt or explicitly reject its metric;
2. give `us-ingest` → `need-understanding` → `istqb-design` the `problem_statement` **alone**;
3. compare the derived conditions against `test_patch`;
4. publish the failures first.

The trap to name now, before any number exists: `problem_statement` in SWE-bench often **contains a
reproduction snippet**. Feeding it whole means QAIA is not deriving from a requirement but reading
a near-test. Any honest measurement must strip or flag that, or it will report a score it has not
earned.

## Sources

- [LLM Benchmarks complete guide 2026](https://www.aice-lab.org/posts/llm-benchmarks-complete-guide-2026/)
- [AI Benchmarks: 300+ LLM benchmarks](https://llm-stats.com/benchmarks)
- [Otter: Generating Tests from Issues to Validate SWE Patches](https://arxiv.org/pdf/2502.05368)
- [Tests4Py: A Benchmark for System Testing](https://arxiv.org/html/2307.05147)
- [BugsInPy (ESEC/FSE 2020)](https://dl.acm.org/doi/abs/10.1145/3368089.3417943)
- [Defects4J overview](https://www.emergentmind.com/topics/defects4j)
