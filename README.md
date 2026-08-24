# QAIA — Agentic QA platform, open source

[![CI](https://github.com/QAIA-Project/QAIA/actions/workflows/ci.yml/badge.svg)](https://github.com/QAIA-Project/QAIA/actions/workflows/ci.yml)
[![Generated suite in CI](https://github.com/QAIA-Project/QAIA/actions/workflows/generated-suite.yml/badge.svg)](https://github.com/QAIA-Project/QAIA/actions/workflows/generated-suite.yml)
[![Release](https://img.shields.io/github/v/release/QAIA-Project/QAIA?include_prereleases&label=release)](https://github.com/QAIA-Project/QAIA/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Site](https://img.shields.io/badge/site-qaia--project.github.io-3b5bdb)](https://qaia-project.github.io/QAIA/)

> 🇫🇷 [Lire ce README en français](README.fr.md)

**A user story goes in. A traceable Gherkin test book and runnable Playwright tests come out** —
as Claude Code plugins that run inside *your* session. No API key, no backend, no data leaving
your session beyond what you already send to Claude.

## The whole product in one screen

One acceptance criterion from [`eval/gold-set/US-004-expense-approval.md`](eval/gold-set/US-004-expense-approval.md):

> A report under €500 total needs one approval (the employee's direct manager). €500–€5000 needs
> manager **then** finance.

*Under €500* and *€500–€5000* do not say what happens at **exactly €500.00**. Here is what came
out ([`approval-chain.feature`](examples/expense-demo/qaia-journey/testbooks/US-004/approval-chain.feature),
verbatim):

```gherkin
  @QAIA-US-004-009 @AC2 @P1 @boundary @low-confidence
  # condition: AC2-C2 — priority P1 — open: Q1 (exact-€500 boundary — read as inclusive
  # in band B: manager then finance)
  Scenario: A report of exactly €500.00 needs manager then finance
    Given a submitted report "R" by "employee@demo" totalling exactly 500.00 EUR
    When "manager@demo" approves report "R"
    Then report "R" still awaits approval from "finance"
```

The tool did not silently pick a reading of the boundary. It picked one, tagged it
`@low-confidence`, numbered the open question, and **wrote its assumption in the file** — so a
human can overturn it in one line instead of finding it in production. A stable ID that survives
regeneration, the criterion it came from, the technique that produced it, and the ambiguity
declared rather than guessed away.

38 scenarios came from that one story, 11 flagged low-confidence. **Disclosed, because a demo
should be:** that ticket is our own gold-set fixture with ambiguities planted on purpose, the run
was non-interactive (every human decision recorded as `simulated`), and the acting model had read
the file's sequestered judge section — all three stated in
[the run's own journey file](examples/expense-demo/qaia-journey/state/US-004/journey.md). It shows
the *shape* of the output, not that it works on your ticket.

## Two real defects, in software we did not write

Everything above is measured on code this project produced itself, which is the weakest kind of
evidence. So the pipeline was pointed at [`typicode/json-server`](https://github.com/typicode/json-server)
— 75,694 stars — and allowed to read **only its README**. Never the code, never the issues, never
the fix commits.

- **A one-character contract break.** The docs promised `_dependent`; the code read `dependent`.
  The endpoint answered success, deleted the post, and left every dependent record in place.
  **A suite written by reading the code cannot find this** — it copies the mistake. Filed by a
  real user as issue #1551; fixed in `1b7c0fb`.
- **Two filters that overwrote each other.** `views_gt=100&views_lt=300` returned everything.
  Fixed in `e6055e6`.
- **A third finding, refused.** `_start` alone returns an empty list — a fact — but the README
  only ever shows it *paired*. **Counted as contested. Two, not three.**

**And the part that goes against us.** Against the *current* version four tests fail and **three
are our fault**: those features left the documentation and the suite kept demanding retired
promises. Now detected by [`check_requirement_drift.py`](eval/tools/check_requirement_drift.py)
rather than quietly closed.

**This is not a pilot.** No human has used QAIA in their own work. One target, one API, no UI,
32 scenarios. [Full campaign, protocol and limits →](eval/external-application-2026-08-08/report.md)

## Install

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-core@qaia
```

`/qaia-core:hello` checks the install. Then describing what you want in plain language — *"work
with QAIA on this user story"* — is enough: the `qaia` meta-skill routes to the right step and
stops wherever a human has to decide.

```
/plugin install qaia-playwright@qaia      # runnable Playwright tests, a11y, perf, security, visual
/plugin install qaia-score@qaia           # scoring and release gate
/plugin install qaia-testdata@qaia        # synthetic test data
```

[`plugins/qaia-core/CATALOGUE.md`](plugins/qaia-core/CATALOGUE.md) maps *"I want to X → use Y"*
across all 33 skills. Worked examples with their real output are in [`examples/`](examples/).

## What separates it, and what does not

**Applying ISTQB techniques is no longer a differentiator** — [QASkills.sh](https://qaskills.sh/)
alone publishes ~380 competently written MIT skills, and Claude-Code-native competitors
([Agentic QE Fleet](https://github.com/proffesor-for-testing/agentic-qe),
[QA Orchestra](https://github.com/Anasss/qa-orchestra)) overlap directly. Three things do separate
QAIA, all verifiable by a stranger in five minutes:

- **No producer scores itself.** The structural score lives in a separate read-only plugin
  (`qaia-score`), apart from the semantic LLM judge, and since 2026-08-09 ships as **pinned Python
  you can read, diff or refuse** — not an algorithm the model rebuilds from prose each run. A score
  that is not reproducible is not a score ([ADR 0002](docs/adr/0002-code-and-optin-tier.md)).
- **Zero API key, nothing that auto-executes.** Skills are Markdown, invoked on demand. Installing
  QAIA registers no hook, no agent, no MCP server. The scorers run only when you invoke the scoring
  skill, with your permissions.
- **The failures are published too.** A generated suite runs on a GitHub Actions runner with **no
  Claude session and no skill loaded** ([run 30702503888](https://github.com/QAIA-Project/QAIA/actions/runs/30702503888));
  every number cited as measured points at the raw file it came from — including a benchmark that
  concludes QAIA costs ~2.9× a direct prompt and does not find more.

**The honest counterweight:** QAIA is younger and far less used than any of them, **no human pilot
has ever run it end to end**, and what it produces for a real user is unmeasured.
[Which tool should you install? We recommend others for 3 of 4 cases →](https://qaia-project.github.io/QAIA/compare.html)

## Status and limits

**Pre-alpha, in active development.** `qaia-core` 0.3.0 (17 skills), `qaia-playwright` 0.1.27
(14 skills), `qaia-score` 0.3.0 (**1 skill**, `judge`), `qaia-testdata` 0.1.3 (1 skill) — **33 skills** — all
validating `--strict`, proven end-to-end on two independent domains: healthcare
([`examples/medibook/`](examples/medibook), 26 tests / 32 executions, all green) and finance/HR
([`examples/expense-demo/`](examples/expense-demo), 56 green tests, real bugs found during
automation), plus a 24-case multi-model robustness corpus.

- **It runs on your Claude quota.** Per-command cost is published per plugin, measured, and higher
  than this project's own prior estimates on 13 of 14 commands.
- **"Learning" means local files.** Feedback enriches a git-versioned knowledge base in your repo.
  No model training, no central server.
- **Web-first.** Mobile coverage means browser emulation, not native iOS/Android.
- **Not a regulatory claim.** The original "medical software / regulated environments" framing was
  retired (D114): QAIA maps no actual framework — not IEC 62304, not 21 CFR Part 11, not ISO 13485.
  `examples/medibook/` is a healthcare-*shaped* demo, not a certified artifact.
- **What it deliberately does not do** ([ADR 0004](docs/adr/0004-test-level-boundary.md)): unit and
  component tests, internal integration, coverage-driven white-box testing. QAIA starts from a
  promise observable from the outside — a test written against a function is written against the
  implementation, which is the oracle it exists to avoid.

**Willing to be the first pilot?** [`docs/PILOT-KIT.md`](docs/PILOT-KIT.md) is a 15-minute guided
run on a ready-made story, and the only thing asked in return is where it went wrong.
Honest state: [`docs/STATUS-en.md`](docs/STATUS-en.md) (English) · [`docs/STATUS.md`](docs/STATUS.md) (full French record).

## Agents — an opt-in tier

[`agents-tier/`](agents-tier) ships eight named agents. It is **not installed by any plugin** and
is never a prerequisite — the 33 skills work without it. Only two earn their own context window
(`camille-judge`, `elian-refuter`), because a producer never grades its own output; the other six
group a phase behind one name — real ergonomics, no new capability. Two caveats the tier's own
README documents rather than hides: `tools:` is a request to the harness, not a capability
boundary, and a delegated agent runs the validation checkpoints with nobody in the room.

## Repository map

| Path | Content |
|---|---|
| [`plugins/`](plugins/) | The four plugins — core, playwright, score, testdata |
| [`examples/`](examples/) | Seven worked end-to-end examples with their real output |
| [`eval/`](eval/) | Evaluation harness: gold set, rubric, scored baselines, robustness campaigns |
| [`docs/STATUS.md`](docs/STATUS.md) | **Honest project state** (start here to continue the work) |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Every architectural decision with its rationale and reservations |
| [`docs/adr/`](docs/adr/) | The seven ADRs that fix the scope boundaries |
| [`docs/COMPETITIVE-ANALYSIS.md`](docs/COMPETITIVE-ANALYSIS.md) | Landscape review and QAIA's blind spots |
| [`docs/OUTPUT-CONTRACT.md`](docs/OUTPUT-CONTRACT.md) | The run manifest every plugin shares |
| [`docs/PILOT-KIT.md`](docs/PILOT-KIT.md) | 15-minute guided walkthrough for pilot testers |
| [`PROMPT.md`](PROMPT.md) | Founding prompt: vision, constraints, user journey |

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first. Every PR requires a DCO sign-off; PRs touching
skills additionally require a traced adversarial agent review — skills are prompts, and a malicious
instruction is invisible to linters. Security reports: [`SECURITY.md`](SECURITY.md).

License: [MIT](LICENSE).
