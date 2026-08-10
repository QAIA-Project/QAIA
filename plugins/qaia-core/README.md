# qaia-core

QAIA core plugin: from user story to prioritized, traceable, atomic Gherkin test books.

**Status: 0.2.35, 18 skills.** Proven end-to-end on two independent domains — a healthcare-*shaped*
demo (`examples/medibook/`) and finance/HR (`examples/expense-demo/`) — plus a 24-case multi-model robustness corpus ([`eval/baselines/corpus-24-depth.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/baselines/corpus-24-depth.md)). See `eval/` at the repo root for the full evaluation trail.

## Install

From Claude Code:

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-core@qaia
/reload-plugins
```

## Skills

| Skill | Journey step | Indicative token budget* |
|---|---|---|
| `/qaia-core:hello` | Installation check (read-only) | minimal (< 1k) |
| `qaia-help` | "What now?" — journey status per US + recommended next step (read-only) | small |
| `testbook-validate` | Audit any Gherkin test book (even non-QAIA) → scored report + PASS/CONCERNS/FAIL gate | medium |
| `qaia` | The Test Architect — one conversational agent carrying the whole journey, step by step, with the human validating each one | varies |
| `openapi-ingest` | Ingest an OpenAPI/Swagger spec as the requirement — derives partitions, boundaries, refusal paths and the four contradictions a spec carries | medium |
| `signal-ingest` | Attach exported production evidence to the open questions a test book already carries — informs them, never answers them | small |
| `test-plan-and-closure` | The two artefacts a test manager signs — plan derived from what the run will actually cover, and closure report | medium |
| `us-ingest` | 1. Capture and validate the source | small |
| `us-review` | 2. Extraction check, AC numbering | small |
| `need-understanding` | 3. Ambiguity hunt, Q&A, assumptions | medium |
| `rag-build` | 4. Team knowledge base (index + focused files) | small |
| `istqb-design` | 5. Techniques chosen and justified per AC | medium |
| `prioritize` | 6. Risk scores proposed, human arbitrated | small |
| `testbook-generate` | 7. Atomic Gherkin book, stable IDs, matrix, ratio check; diff-based regeneration | large |
| `testbook-export` | 8. `.feature` + XLSX + Markdown synthesis; opt-in Xray or TestRail CSV export (git-master, file-only — issue #35) | medium |
| `feedback` | 9. Corrections captured, validated promotion to rules | small |
| `oracle-generate` | Standards as generation oracles (Luhn, ISO 8601, HTTP, RFC 5322…) → grounded cases + expected results, tagged `@oracle:*` | small |

\* Orders of magnitude — never promises. The journey state lives in `.qaia/` (see `skills/README.md` for the full contract): every step checkpoints to disk, so an interrupted session resumes where it left off.

## Token budget — orders of magnitude

**Version 0.2.35 — measured 2026-07-25, and partial.** The table covers **14 of the 18 skills**: `test-plan-and-closure`, `openapi-ingest`, `signal-ingest` and `qaia` carry **no published cost**. Calling this "fully instrumented" while four skills were unmeasured is exactly the class of claim this project exists to refuse. The 14 measured commands in the table below
carry a real measurement, taken by the method described here.

**How they were measured.** Each command was applied faithfully, start to finish, by a dedicated
agent on a gold-set user story — no shortcuts. The figure is the total tokens that agent actually
consumed for the complete task (input + output, as reported by the orchestration layer). It is
**not** a self-report: an agent has no reliable access to its own counter, which was confirmed
repeatedly — no environment variable and no tool available to a delegated agent exposes its own
total. The number is read one level above the agent, where it is exposed. **One run per command,
so there is no average and no variance yet.**

| Command | Tokens, round trip | Measured? | What moves it |
|---|---|---|---|
| `hello` | **39.1k** | ✅ | read-only, one turn — well above the old ~1-5k estimate |
| `qaia-help` | **56.3k** (US-004 fixture) | ✅ | read-only, one turn, but reads a full 7-step journey state — above the old ~1-5k estimate |
| `us-ingest` | **44.9k** (US-002) | ✅ | size of the story, gates — **the measurement far exceeds the old ~5-20k estimate; reported as measured, not smoothed** |
| `us-review` | **73.8k** (US-002) | ✅ | size of the story, gates — above the old ~5-20k estimate |
| `prioritize` | **84.7k** (US-004) | ✅ | number of conditions to score (37 here) — above the old ~5-20k estimate |
| `feedback` | **88.5k** (US-004) | ✅ | corrections captured (4 here, 2 promoted to rules) — above the old ~5-20k estimate |
| `istqb-design` | **40.1k** (US-004) | ✅ | number of acceptance criteria, coverage expansion — consistent with the old estimate |
| `rag-build` | **67.6k** (new knowledge base, carpooling domain) | ✅ | full initialisation (5 files) vs. incremental addition to an existing base, number of business rules — above the old ~20-60k estimate, consistent with an initialisation run being the most expensive case |
| `need-understanding` | **91.1k** (US-002) | ✅ | ambiguity, number of criteria (8 questions over 8 criteria here), Q&A turns — above the old ~20-60k estimate |
| `oracle-generate` | **67.1k** (US-004) | ✅ | oracle domains detected (2 here: ISO 4217, ISO 8601) — above the old ~20-60k estimate |
| `testbook-generate` | **112.5k** (US-005), indicative range ~40-150k+ | ✅ | criteria × techniques; sub-agent parallelisation raises throughput **and** cost |
| `testbook-export` | **77.6k** (US-004 book, 4 files / 38 scenarios) | ✅ | book volume, deliverables produced (XLSX adds real cost) — above the old ~10-40k estimate |
| `testbook-validate` | **107.1k** (US-004) | ✅ | volume audited (4 files / 38 scenarios) plus the deterministic structural score replayed alongside the LLM judge |
| `report` | **139.7k** (US-004) | ✅ | volume of the full 7-step journey to consolidate — above the old ~10-40k estimate |

**The finding that runs across the table: 13 of the 14 measured commands cost more than the
expert estimate that preceded them**, several of them by a wide margin (`report` 139.7k against a
~10-40k estimate, `need-understanding` 91.1k against ~20-60k). Only `istqb-design` landed inside
its range. Nothing was adjusted downwards after the fact — the signal is that the old ranges, none
of which were ever instrumented, were **systematically optimistic**, rather than that one
particular command misbehaves.

The cost lands on your **subscription quota**, not an API bill. For context on the maintainer
side: evaluation campaigns consume ~115k to 1.76M tokens because they are multi-agent workflows —
that is **not** representative of a single user command.

## What that means against the subscription tiers

**The honest limit first.** Anthropic no longer publishes an exact, guaranteed figure of
messages or hours per tier — checked directly against the official help page (support.claude.com,
2026-07-28): *"Both Pro and Max plans offer usage limits that are shared across Claude and Claude
Code"*, with no quantification. The numbers below are **third-party estimates, unofficial**,
dated and sourced. Check them against your own account before committing a team to them; they are
not a contractual guarantee from Anthropic.

| Tier | 5-hour window (third-party, 2026-07-28) | Weekly cadence (third-party) |
|---|---|---|
| Pro (~$20/month) | ~45 prompts / 5h | no published range; usage judged suited to 2-5h a week of Claude Code on contained tasks |
| Max 5× (~$100/month) | ~225 prompts / 5h | ~140-280h of Claude Code per week |
| Max 20× (~$200/month) | ~900 prompts / 5h | ~240-480h of Claude Code per week |

**Why the measured token budget does not convert 1:1 into "journeys per week".** The subscription
quota is counted in **prompts and session time**, not raw tokens. A skill invocation that consumes
133k tokens internally (agent plus tools) generally counts as **one prompt** in the 5-hour window,
exactly like a short message. So the real limiting factor for a team is not the token volume
measured per command — it is the **number of skill invocations** (≈ one prompt each) and the
cumulative session time.

**Usage guidance, with that caveat attached.** A full QAIA journey — the six core commands
`us-ingest` → `us-review` → `need-understanding` → `istqb-design` → `testbook-generate` →
`report` — costs on the order of **6 to 12 prompts** (a command may be re-run once when a human
arbitrates), comfortably inside the 5-hour window of even the Pro tier (~45 prompts). For team
use, the real constraint is cumulative session time rather than an isolated prompt count: a team
of 3-5 developers running 1-2 full journeys a day stays in the order of magnitude of "contained"
individual usage per person, which the third-party sources above already call adequate for Pro.
Heavier use — several stories in parallel, frequent regeneration, optional commands such as
`oracle-generate` or `testbook-validate` — pushes toward Max 5×. **Neither profile requires
Max 20×** on the basis of what QAIA consumes; that tier stays relevant for Claude Code usage
wider than QAIA alone.

**Not done, and said plainly: no real pilot team has yet reported its quota consumption over
several weeks.** This whole section is a **projection from the measured token budget**, not a
measurement of quota actually exhausted, and it is to be corrected the moment pilot feedback
exists.

## Portability

Skills are plain Markdown following the shared contract in `skills/README.md` — designed to work in any Claude surface with file access (decision D29). Claude Code adds comfort (sub-agent parallelization in `testbook-generate`, XLSX tooling in `testbook-export`); the skills degrade gracefully and honestly without it.
