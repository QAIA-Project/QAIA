# QAIA agents — opt-in tier

**Seven named agents, one per SDLC phase. Not installed by `qaia-core`, `qaia-playwright`,
`qaia-score` or `qaia-testdata`, and never a prerequisite of any of them.**

## Why this lives outside `plugins/`

The project's supply-chain guard refuses `agents/` inside a plugin, and CI enforces it. That rule
was written against hooks and MCP servers, whose danger is auto-executed shell in the installer's
environment. An agent definition is a Markdown file and carries no such payload — but it **does**
widen what the model may reach for once invoked, through its `tools:` list. That is a smaller risk
than a hook and it is not zero, so the tier stays separate and explicit rather than being smuggled
into the core by re-reading a rule until it permits what we want.

Install it because you decided to, or do not install it at all. The 37 skills work without it.

## The honest part, before the list

**Only two of these seven have a genuine reason to be an agent.**

The design criterion is not importance, it is a **delegation boundary**: work that needs its own
context window. By that test:

- **Camille** and **Elian** earn it. The project's rule 3 says *a producer never grades its own
  output*, and a judge sharing the producer's context has already read the reasoning it is meant
  to check independently. A separate context is not decoration there — it is the whole point.
  A pilot run on 2026-08-09 failed for exactly this reason: the same party produced and graded.
- **The other five are a convenience layer over skills that already work.** They group a phase
  behind one name so you can say "ask Naïma" instead of remembering four skill names. That is a
  real ergonomic gain and it is *not* new capability. Said here so nobody discovers it later.

## The seven

| Agent | SDLC phase | Wraps | Own context earns it? |
|---|---|---|---|
| **Naïma** | Discovery — requirement capture and ambiguity | `us-ingest`, `us-review`, `need-understanding`, `openapi-ingest`, `signal-ingest` | no — ergonomics |
| **Théo** | Design — techniques, oracles, priorities | `istqb-design`, `oracle-generate`, `prioritize` | no — ergonomics |
| **Salim** | Test data | `dataset-generate` | no — ergonomics |
| **Elsa** | Test book | `testbook-generate`, `testbook-export`, `test-plan-and-closure` | no — ergonomics |
| **Marek** | Automation | `automate`, `a11y-audit`, `perf-check`, `security-surface`, `visual-check`, `traffic-replay`, `contract-probe` | no — ergonomics |
| **Yuki** | Execution and triage | `run-report`, `defect-report`, `flaky-detect`, `locator-repair`, `impact-select`, `confirm-fix` | no — ergonomics |
| **Camille** | Judgement and release readiness | `testbook-score`, `automation-score`, `aptitude-gate`, `spec-suite-drift`, `testbook-validate` | **yes — rule 3** |
| **Elian** | Adversarial second opinion | none: reads artefacts only | **yes — rule 3** |

That is eight rows for seven phases: **Elian** is not a phase. It is the refutation pass, and it
exists because a single judge that agrees with itself is not evidence.

## They are not people

Each agent carries a human first name because a named delegate is easier to reason about and to
address. **Every one of them states, in its own output, that it is an automated agent and not a
person.** A quality verdict signed with a human name on a regulated product could read as a human
sign-off; the name is an interface convenience and must never become an implied signature.

No agent approves a release. They produce evidence and a proposed verdict; a human decides.

## Tool scoping — and what it is NOT

The judges (**Camille**, **Elian**) declare `tools: Read, Glob, Grep`. The producers declare write
access scoped to what they generate, and only **Marek** and **Yuki** declare `Bash`, because
running a suite is their job.

**`tools:` is a request to the harness, not a capability boundary.** This paragraph previously
claimed the judges "cannot write a file, run a command or reach the network". That sentence was
false, and it was disproved by the first agent ever launched from this tier: running as
`elian-refuter` — whose frontmatter lists three read-only tools — it executed `python`, `git`,
`cp` and `rm -rf`, wrote files, and reached the network. It said so in its own report.

What the declaration actually buys you:

- **an audited intent** — the file states what the agent is supposed to need, so a reviewer can
  see a widening in a diff;
- **whatever the harness chooses to enforce**, which varies and which this repository does not
  control.

What it does not buy you: containment. **Treat an agent file as you would a dependency — read its
frontmatter and its body before installing it, and assume the tools listed are a floor, not a
ceiling.**

`eval/tools/check_agents_tier.py` guards the files in `agents-tier/agents/`. It cannot guard the
copies you make into `.claude/agents/`, which is what your harness actually loads — once copied,
they are yours and outside this repository's reach.

## Install

Copy the agent files into your project's `.claude/agents/`:

```
cp agents-tier/agents/*.md .claude/agents/
```

Nothing is auto-executed by copying them. Each file is a prompt with a tool allowlist; read the
frontmatter before you copy it, exactly as you would for any code you install.
