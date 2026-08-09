# QAIA — Agentic QA platform, open source

[![CI](https://github.com/QAIA-Project/QAIA/actions/workflows/ci.yml/badge.svg)](https://github.com/QAIA-Project/QAIA/actions/workflows/ci.yml)
[![Generated suite in CI](https://github.com/QAIA-Project/QAIA/actions/workflows/generated-suite.yml/badge.svg)](https://github.com/QAIA-Project/QAIA/actions/workflows/generated-suite.yml)
[![Release](https://img.shields.io/github/v/release/QAIA-Project/QAIA?include_prereleases&label=release)](https://github.com/QAIA-Project/QAIA/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Site](https://img.shields.io/badge/site-qaia--project.github.io-3b5bdb)](https://qaia-project.github.io/QAIA/)

> 🇫🇷 [Version française ci-dessous](#-français)

**One user story in, this out** — copied verbatim from [`examples/expense-demo/qaia-journey/`](examples/expense-demo/qaia-journey), where the whole run is kept:

```gherkin
@QAIA-US-004-021 @AC5 @P1 @negative @boundary
# condition: AC5-C2 [req-neg] — priority P1
Scenario: A line at exactly the receipt threshold without a receipt is refused
  Given "employee@demo" has a draft report with one EUR line "gear" of 25.00 dated today, no receipt attached
  When "employee@demo" submits the report
  Then the attempt is refused with a message mentioning "receipt"
```

38 scenarios from that one story, each traced back to an acceptance criterion in a coverage matrix. **11 of them are flagged low-confidence with the open question named** — because the story didn't say, and quietly picking an interpretation is how a suite ends up looking complete while encoding a guess at exactly the boundary where bugs live.

*Disclosed, because a demo should be:* that ticket is our own gold-set fixture with ambiguities planted in it on purpose, the run was executed **non-interactively** (every human decision point recorded as `simulated: <default applied>`), and the acting model had read the file's sequestered judge section beforehand — all three stated in [the run's own journey file](examples/expense-demo/qaia-journey/state/US-004/journey.md). It shows the *shape* of the output. It is not evidence that it works on your ticket.

[See real input and output side by side →](https://qaia-project.github.io/QAIA/) · [Which tool should you install? (we recommend others for 3 of 4 cases) →](https://qaia-project.github.io/QAIA/compare.html)

**Status: pre-alpha, in active development.** Core (`qaia-core` 0.2.35, 18 skills), automation (`qaia-playwright` 0.1.27, 14 skills), scoring (`qaia-score` 0.2.4, 4 skills) and test-data (`qaia-testdata` 0.1.3, 1 skill) plugins exist — **37 skills** — validate `--strict`, and are proven end-to-end on **two independent real domains** — healthcare ([`examples/medibook/`](examples/medibook), 26 Playwright tests / 32 executions across projects, all green — re-run 2026-07-31, raw output in [`examples/medibook/tests/run-log.txt`](examples/medibook/tests/run-log.txt)) and finance/HR ([`examples/expense-demo/`](examples/expense-demo), 56 green Playwright tests, real bugs found and fixed during automation) — plus a 24-case multi-model robustness corpus ([`eval/baselines/corpus-24-depth.md`](eval/baselines/corpus-24-depth.md)). Formal human-pilot validation hasn't happened yet — see [`docs/STATUS-en.md`](docs/STATUS-en.md) for the honest state in English (the full French record is [`docs/STATUS.md`](docs/STATUS.md)). **Willing to be the first?** [`docs/PILOT-KIT.md`](docs/PILOT-KIT.md) is a 15-minute guided run on a ready-made story, and the only thing asked in return is where it went wrong.

QAIA turns user stories into prioritized, traceable **Gherkin test books** and then into **native Playwright tests** — distributed as **skills and plugins** that run inside *your* Claude session. No API key, no backend, no data leaves your session beyond what you already send to Claude.

Built with and for testers: ISTQB techniques applied and justified, requirement→test traceability that works as well for ordinary business workflows (proven on finance/HR) as for domains with higher documentation rigor (demonstrated on a healthcare-shaped example), and a conversational workflow where the tester validates every step. Goal: let teams use AI for test activities **from the specification to the maintenance of a live suite** — starting at the user story, before code exists, and continuing through impact selection, defect reporting and fix confirmation. Not isolated test-case generation, and **not the whole lifecycle**: discovery and production testing (synthetic monitoring, chaos) are deliberately out of scope — [ADR 0007](docs/adr/0007-scope-delivery-and-maintenance.md) says why.

**Not a claim of regulatory readiness.** QAIA's original v1 niche framing (`docs/DECISIONS.md`, D2) named "medical software / regulated environments" specifically — retired (D114) after an honest gap check: QAIA has no mapped coverage of the actual regulatory frameworks that govern that space (IEC 62304, 21 CFR Part 11, ISO 13485) and no real medtech pilot deployment. `examples/medibook/` is an internal demo proving traceability and technique quality on a healthcare-*shaped* domain, not a certified or regulator-reviewed artifact — if your context requires actual regulatory conformance, treat QAIA as unproven there until that gap is closed.

## What it actually produces, before you install anything

One acceptance criterion in, one scenario out. **Verbatim, truncated but not retouched** — both
files are in this repository.

The requirement ([`eval/gold-set/US-004-expense-approval.md`](eval/gold-set/US-004-expense-approval.md)):

> 2. A report under €500 total needs one approval (the employee's direct manager). €500–€5000 needs manager **then** finance. Above €5000 needs manager, finance, **then** a director.

*(Quoted verbatim; the emphasis is the source's own.)*

Read it twice. *Under €500* and *€500–€5000* do not say what happens at **exactly €500.00** — and
that ambiguity was planted on purpose, in a section of the file the skills were never given.

What came out ([`examples/expense-demo/qaia-journey/testbooks/US-004/approval-chain.feature`](examples/expense-demo/qaia-journey/testbooks/US-004/approval-chain.feature)):

```gherkin
  @QAIA-US-004-008 @AC2 @P1 @boundary
  # condition: AC2-C1 — priority P1
  Scenario: A report just under €500 needs only the manager's approval
    Given a submitted report "R" by "employee@demo" totalling exactly 499.99 EUR
    Then report "R" awaits approval from "manager" only

  @QAIA-US-004-009 @AC2 @P1 @boundary @low-confidence
  # condition: AC2-C2 — priority P1 — open: Q1 (exact-€500 boundary — read as inclusive
  # in band B: manager then finance)
  Scenario: A report of exactly €500.00 needs manager then finance
    Given a submitted report "R" by "employee@demo" totalling exactly 500.00 EUR
    When "manager@demo" approves report "R"
    Then report "R" still awaits approval from "finance"
```

**The second scenario is the point.** The tool did not silently pick a reading of the boundary: it
picked one, tagged the scenario `@low-confidence`, numbered the open question, and **wrote its
assumption in the file** — so a human can overturn it in one line instead of discovering it in
production.

That is the whole product in one screen: a stable ID that survives regeneration, the criterion it
comes from, the technique that produced it (`@boundary`), and the ambiguity declared rather than
guessed away.

## Two real defects, in software we did not write

Everything above is measured on code this project produced itself, which is the weakest kind of
evidence. So the pipeline was pointed at a stranger's repository:
[`typicode/json-server`](https://github.com/typicode/json-server) — 75,694 stars (measured
2026-08-08), chosen because it has a **public contract that predates us**: its README.

The rule: the test book was written from **that README alone**. Never the code, never the issues,
never the fix commits. Then the same suite ran against two versions of the same software.

- **A one-character contract break.** The documentation promised `_dependent`; the code read
  `dependent`. The endpoint answered success, deleted the post, and silently left every dependent
  record in place. **A suite written by reading the code cannot find this** — it copies the mistake.
  A real user had filed it as issue #1551; the maintainer merged the fix in `1b7c0fb`.
- **Two filters that overwrote each other.** `views_gt=100&views_lt=300` returned everything:
  conditions were stored in a map keyed by field name, so the second replaced the first. Fixed in
  `e6055e6`.
- **A third finding, refused.** `_start` alone returns an empty list — a fact — but the README only
  ever shows it *paired*, so the test extrapolated a promise the document does not make. **Counted
  as contested. Two, not three.**

**And the part that goes against us.** Against the *current* version, four tests fail and **three of
them are our fault** — those features were removed from the documentation in the meantime, and the
suite kept demanding retired promises. That gap is now detected
([`check_requirement_drift.py`](eval/tools/check_requirement_drift.py)) rather than quietly closed.

**This is not a pilot.** No human has used QAIA in their own work. One target, one API, no user
interface, 32 scenarios rather than full coverage. [The full campaign, protocol and
limits →](eval/external-application-2026-08-08/report.md)

## Install and try it

QAIA is a set of Claude Code plugins. There is nothing to build and no API key to provide — the
skills run inside your own Claude Code session, using your own model.

**Two lines is the whole install.** `qaia-core` alone takes a user story all the way to a Gherkin
test book — that is the part worth judging first.

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-core@qaia
```

Then `/qaia-core:hello` checks the install, and describing what you want in plain language — *"work with
QAIA on this user story"* — is enough: the `qaia` meta-skill routes to the right step and stops
wherever a human has to decide.

Add the rest only when you need them:

```
/plugin install qaia-playwright@qaia      # runnable Playwright tests, a11y, perf, security, visual
/plugin install qaia-score@qaia           # scoring and release gate
/plugin install qaia-testdata@qaia        # synthetic test data
```

**What QAIA deliberately does not do** ([ADR 0004](docs/adr/0004-test-level-boundary.md)): unit and component tests, integration between internal components, coverage-driven white-box testing. QAIA starts from a promise observable from the outside — a test written against a function is written against the implementation, which is the oracle it exists to avoid. If you want unit tests, your IDE already generates better ones.

**Which skill for what?** [`plugins/qaia-core/CATALOGUE.md`](plugins/qaia-core/CATALOGUE.md) is a one-page “I want to X → use Y” map of all 37 skills — including the four that all probe a running app, laid out by *what each one uses as its oracle*, which is the only thing that tells them apart.

Worked examples with their real output are in [`examples/`](examples/).


## Why not just another agentic QA tool?

The AI-for-testing space is crowded in 2026, and **it is now crowded inside Claude Code itself**: SaaS platforms (testRigor, Mabl, Applitools, Tricentis), open-source LLM-driven browser agents (BrowserUse, Stagehand, Skyvern), and Claude-Code-native competitors that overlap with QAIA directly — [Agentic QE Fleet](https://github.com/proffesor-for-testing/agentic-qe) (a 60-agent autonomous swarm), [QA Orchestra](https://github.com/Anasss/qa-orchestra) (10 QA agents, spec review to Playwright/Cypress/Selenium/Gherkin), [neonwatty/qa-skills](https://github.com/neonwatty/qa-skills) (E2E generation pipeline, 6 agents), and curated skill marketplaces like [QASkills.sh](https://qaskills.sh/).

**Applying ISTQB techniques is no longer a differentiator.** QASkills.sh alone publishes ~380 MIT skills including `istqb-test-design-techniques`, `test-case-generator-user-stories`, `bdd-gherkin-patterns`, `risk-based-testing` and `boundary-value-generator` — and they are competently written. The difference is not the technique, it is the shape: **those are single-file prompt enhancers; QAIA is a pipeline that produces artifacts and then gates them** — stable scenario IDs, a requirement coverage matrix, a validated manifest per run, a refusal-path coverage gate (every rule that can refuse or deny must have a scenario exercising it — [ADR 0001](docs/adr/0001-negative-coverage-gate.md)), and a scorer that lives outside the producer. If you want a better prompt, install one of theirs — it is one command and it works. If you want output you can hand to an auditor, that is a different tool. Three things actually separate it, and all three are verifiable by a stranger in five minutes:

- **No producer scores itself.** The structural score is specified as a deterministic algorithm and lives in a separate, read-only plugin (`qaia-score`), kept apart from the semantic LLM judge. Caveat worth stating: that plugin ships no code — the algorithm is materialised as a throwaway in-session script each run (ADR 0002), so the algorithm is fixed while its implementation is regenerated. None of the competitors above documents a separation between the component that produces and the one that assesses — we looked and could not find one; if it exists, tell us and this sentence changes. This is the project's hardest rule and it has repeatedly caught defects its own authors could not see.
- **Zero API key in the shipped product, zero auto-executed hooks/agents/MCP servers.** 100% Markdown skills, invoked on demand inside your own Claude session — a portability and supply-chain posture, not a missing feature. Installing QAIA does not put anything in your repo that runs by itself.
- **The failures are published, not just the successes.** Skills carry verdicts from real runs, including unfavourable ones (`docs/STATUS.md`, `eval/`); a generated suite is executed **on a GitHub Actions runner with no Claude session and no skill loaded** ([run 30702503888](https://github.com/QAIA-Project/QAIA/actions/runs/30702503888), raw log kept in `eval/ci-proof-2026-08-01/`); every number cited as measured points at the raw file it came from. Check any of it against the repository.

And the honest counterweight: QAIA is younger and far less used than the projects above, **no human pilot has ever run it end to end**, and the quality of what it produces for a real user is still unmeasured. See [`docs/COMPETITIVE-ANALYSIS.md`](docs/COMPETITIVE-ANALYSIS.md) for the full landscape review and QAIA's blind spots, and [`docs/STATUS.md`](docs/STATUS.md) for what is proven and what is not.

## Honest positioning (read this first)

- **Runs on your Claude subscription.** Every generation consumes your own session quota. Indicative cost per command is published per plugin, measured on our gold set.
- **"Learning" means local knowledge.** The feedback mode enriches a versioned, file-based knowledge base (`.qaia/knowledge/`) in your repo — there is no model training and no central server.
- **Claude Code first, portable by design.** The core (US → test book) is written as portable skills; automation (Playwright) requires Claude Code + Playwright MCP.
- **Web-first automation.** Mobile coverage means browser emulation, not native iOS/Android.

## What QAIA does today

1. Ingest a user story (file, URL, Jira) — you validate the source
2. Verify extraction, reformulate the need, surface ambiguities
3. Build a shared, git-versioned project knowledge base
4. Apply and justify ISTQB test design techniques (Foundation + Test Analyst)
5. Prioritize by risk — the tool proposes, the human arbitrates
6. Generate an **atomic Gherkin test book** with stable scenario IDs (`@QAIA-xxx`), a requirement coverage matrix, and a refusal-path coverage gate (the negative/boundary ratio is reported as a bias signal, not enforced as a threshold — [ADR 0001](docs/adr/0001-negative-coverage-gate.md))
7. Export (`.feature` + XLSX/Markdown), report, and **regenerate by scenario-level diff** when the US evolves — your manual edits are preserved
8. Learn from your corrections (validated promotion of recurring feedback into rules)
9. Turn the test book into **native Playwright automation** (E2E, API, mobile-web emulation, accessibility, visual, performance, security-surface) — real code, runs in your own CI, no QAIA dependency at runtime
10. **Score, separately**: a deterministic structural pass + an ISTQB rubric judged fresh, gating PASS/CONCERNS/FAIL/WAIVED — the generator never grades its own output

Proven twice end-to-end, on two unrelated domains (see [`examples/`](examples/)) — not just measured in the abstract.

## Agents — an opt-in tier, and what it is not

`agents-tier/` ships **eight named agents**, one per SDLC phase plus an adversarial refuter. It is
**not installed by any plugin** and is never a prerequisite: copy the files into `.claude/agents/`
if you decide to, or ignore it entirely — the 37 skills work without it.

**Only two of the eight earn their own context window.** The design criterion is a *delegation
boundary*, not importance: `camille-judge` and `elian-refuter` need a context the producer never
touched, because this project's rule 3 says a producer never grades its own output. The other six
group a phase behind one name — real ergonomics, **no new capability**, and the tier's README says
so in its own opening paragraph.

Two things worth reading before you install:

- **`tools:` is a request to the harness, not a capability boundary.** The first agent ever launched
  from this tier ran as a read-only judge and executed shell commands. The README documents this
  rather than hiding it.
- **A delegated agent runs the skills' validation checkpoints with nobody in the room.** Two agents
  independently reported that they had substituted written disclaimers for a human decision. Use
  the agents to explore; use the skills interactively when the output will be trusted.

## Repository map

| Path | Content |
|---|---|
| [`PROMPT.md`](PROMPT.md) | Founding prompt (vision, constraints, user journey) |
| [`docs/DISCOVERY.md`](docs/DISCOVERY.md) | Discovery v2: 3 gates, 88 questions, 12 hard objections |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | 196 decisions, one row each |
| [`docs/DELIVERY.md`](docs/DELIVERY.md) | Roadmap M0→M5, plugin architecture |
| [`docs/KANBAN.md`](docs/KANBAN.md) | Board structure + prioritized backlog |
| [`docs/STATUS.md`](docs/STATUS.md) | **Honest project state + resume prompt** (start here to continue) |
| [`docs/M0-CHECKLIST.md`](docs/M0-CHECKLIST.md) | M0 progress and pending owner actions |
| [`docs/PILOT-KIT.md`](docs/PILOT-KIT.md) | 15-minute guided walkthrough for pilot testers |
| [`plugins/qaia-core/`](plugins/qaia-core/) | Core plugin: US → prioritized Gherkin test book (18 skills, incl. oracle-generate + signal-ingest) |
| [`plugins/qaia-playwright/`](plugins/qaia-playwright/) | Automation plugin: test book → native Playwright + CI pipeline (E2E/API/a11y/perf/security) |
| [`plugins/qaia-score/`](plugins/qaia-score/) | Scoring plugin (read-only): 10-dimension rubric (/20) + PASS/CONCERNS/FAIL/WAIVED gate |
| [`plugins/qaia-testdata/`](plugins/qaia-testdata/) | Test-data plugin: rich, business-coherent synthetic datasets injectable via fixtures (never real data) |
| [`docs/OUTPUT-CONTRACT.md`](docs/OUTPUT-CONTRACT.md) | Standardized run manifest every plugin shares (D39) |
| [`eval/`](eval/) | Evaluation harness: gold set + rubric + scored baselines + robustness campaign |
| [`examples/medibook/`](examples/medibook/) | Worked end-to-end example: real app + POM Playwright automation (26 tests, 32 executions — see `tests/run-log.txt`) |
| [`examples/oracle-demo/`](examples/oracle-demo/) | Standards as test-case generators (Luhn oracle, computationally verified) |
| [`examples/scoring-demo/`](examples/scoring-demo/) | Output contract + qaia-score walk-through (manifest, scorecard, gate) |
| [`examples/rag-demo/`](examples/rag-demo/) | The RAG in use: a knowledge base breaking the recall ceiling on a thin US (D38) |
| [`examples/jira-demo/`](examples/jira-demo/) | Jira connector: a REST v3 issue export → validated QAIA capture (D9, #9) |
| [`examples/expense-demo/`](examples/expense-demo/) | Worked end-to-end example, non-medical: real finance/HR app + Playwright automation (56 green Playwright tests, 3 real bugs found during automation) |
| [`docs/COMPETITIVE-ANALYSIS.md`](docs/COMPETITIVE-ANALYSIS.md) | Landscape review (2026): where QAIA sits vs SaaS and open-source agentic QA tools |
| [`eval/baselines/corpus-24-depth.md`](eval/baselines/corpus-24-depth.md) | 24-case statistical depth study across 5 LLM providers and 8 business domains |
| [`docs/DEMO-TARGETS.md`](docs/DEMO-TARGETS.md) | Vetted catalog of demo/practice apps to exercise QAIA on |

## Contributing

Contributions are welcome — read [`CONTRIBUTING.md`](CONTRIBUTING.md) first. Every PR requires a DCO sign-off; PRs touching skills additionally require a traced adversarial agent review (skills are prompts: a malicious instruction is invisible to linters). Security reports: see [`SECURITY.md`](SECURITY.md).

License: [MIT](LICENSE).

---

## 🇫🇷 Français

**Une user story en entrée, ceci en sortie** — copié verbatim de [`examples/expense-demo/qaia-journey/`](examples/expense-demo/qaia-journey), où la totalité du parcours est conservée :

```gherkin
@QAIA-US-004-021 @AC5 @P1 @negative @boundary
# condition: AC5-C2 [req-neg] — priority P1
Scenario: A line at exactly the receipt threshold without a receipt is refused
  Given "employee@demo" has a draft report with one EUR line "gear" of 25.00 dated today, no receipt attached
  When "employee@demo" submits the report
  Then the attempt is refused with a message mentioning "receipt"
```

38 scénarios tirés de cette seule histoire, chacun tracé à son critère d'acceptation dans une matrice de couverture. **11 sont marqués « confiance basse » avec la question ouverte nommée** — parce que l'histoire ne disait pas, et que trancher en silence, c'est produire une suite qui a l'air complète tout en encodant une supposition exactement à la frontière où vivent les défauts.

*Divulgué, parce qu'une démo doit l'être :* ce ticket est notre propre fixture de gold set, avec des ambiguïtés plantées exprès ; le parcours a été exécuté **en non-interactif** (chaque point de décision humaine consigné `simulated: <default applied>`) ; et le modèle avait lu la section juge séquestrée du fichier avant de commencer — les trois sont écrits dans [le journal du parcours](examples/expense-demo/qaia-journey/state/US-004/journey.md). Ça montre la *forme* de la sortie. Ce n'est pas une preuve que ça marche sur votre ticket.

[Voir entrée réelle et sortie réelle côte à côte →](https://qaia-project.github.io/QAIA/) · [Quel outil installer ? (on en recommande d'autres dans 3 cas sur 4) →](https://qaia-project.github.io/QAIA/compare.html)

**Statut : pré-alpha, en développement actif.** Les plugins cœur (`qaia-core` 0.2.35, 18 skills), automatisation (`qaia-playwright` 0.1.27, 14 skills), score (`qaia-score` 0.2.4, 4 skills) et jeux de données (`qaia-testdata` 0.1.3, 1 skill) existent — **37 skills** —, valident `--strict`, et sont prouvés bout-en-bout sur **deux domaines réels indépendants** — santé ([`examples/medibook/`](examples/medibook), 32 tests Playwright, tous verts — rejoués le 2026-07-31, sortie brute dans [`examples/medibook/tests/run-log.txt`](examples/medibook/tests/run-log.txt)) et finance/RH ([`examples/expense-demo/`](examples/expense-demo), 56 tests verts, vrais bugs trouvés et corrigés pendant l'automatisation) — plus un corpus de robustesse multi-modèles à 24 cas ([`eval/baselines/corpus-24-depth.md`](eval/baselines/corpus-24-depth.md)). La validation par de vrais pilotes humains n'a pas encore eu lieu — voir [`docs/STATUS.md`](docs/STATUS.md) pour l'état honnête. **Envie d'être le premier ?** [`docs/PILOT-KIT.md`](docs/PILOT-KIT.md) est un parcours guidé de 15 minutes sur une histoire toute prête, et la seule chose demandée en retour, c'est de dire où ça a raté.

## Ce que ça produit vraiment, avant d'installer quoi que ce soit

Un critère d'acceptation en entrée, un scénario en sortie. **Verbatim, tronqué mais non retouché** —
les deux fichiers sont dans ce dépôt.

L'exigence ([`eval/gold-set/US-004-expense-approval.md`](eval/gold-set/US-004-expense-approval.md)) :

L'original est en anglais ; **ceci est une traduction**, le texte exact est dans le fichier lié :

> 2. Un rapport sous 500 € au total demande une approbation (le manager direct).
> 500–5000 € demande le manager **puis** la finance. Au-dessus de 5000 €, manager, finance,
> **puis** un directeur.

Relisez. *Sous 500 €* et *500–5000 €* ne disent pas ce qui se passe à **exactement 500,00 €** — et
cette ambiguïté était plantée exprès, dans une section du fichier que les skills n'ont jamais reçue.

Ce qui est sorti ([`approval-chain.feature`](examples/expense-demo/qaia-journey/testbooks/US-004/approval-chain.feature)) :

```gherkin
  @QAIA-US-004-008 @AC2 @P1 @boundary
  # condition: AC2-C1 — priority P1
  Scenario: A report just under €500 needs only the manager's approval
    Given a submitted report "R" by "employee@demo" totalling exactly 499.99 EUR
    Then report "R" awaits approval from "manager" only

  @QAIA-US-004-009 @AC2 @P1 @boundary @low-confidence
  # condition: AC2-C2 — priority P1 — open: Q1 (exact-€500 boundary — read as inclusive
  # in band B: manager then finance)
  Scenario: A report of exactly €500.00 needs manager then finance
    Given a submitted report "R" by "employee@demo" totalling exactly 500.00 EUR
    When "manager@demo" approves report "R"
    Then report "R" still awaits approval from "finance"
```

**Le second scénario est tout l'intérêt.** L'outil n'a pas choisi silencieusement une lecture de la
borne : il en a choisi une, a marqué le scénario `@low-confidence`, numéroté la question ouverte, et
**écrit son hypothèse dans le fichier** — pour qu'un humain la renverse en une ligne au lieu de la
découvrir en production.

C'est le produit entier en un écran : un identifiant stable qui survit à la régénération, le critère
dont il vient, la technique qui l'a produit (`@boundary`), et l'ambiguïté déclarée plutôt que devinée.

## Deux vrais défauts, dans un logiciel que nous n'avons pas écrit

Tout le reste est mesuré sur du code que ce projet a lui-même produit, ce qui est la preuve la plus
faible qui soit. La chaîne a donc été pointée sur le dépôt d'un inconnu :
[`typicode/json-server`](https://github.com/typicode/json-server) — 75 694 étoiles (mesurées le
2026-08-08), choisi parce qu'il a un **contrat public antérieur** : son README.

La règle : le cahier a été écrit depuis **ce README seul**. Jamais le code, jamais les tickets,
jamais les correctifs. Puis la même suite a tourné sur deux versions du même logiciel.

- **Une rupture de contrat d'un caractère.** La documentation promettait `_dependent` ; le code
  lisait `dependent`. L'endpoint répondait en succès, supprimait le post, et laissait silencieusement
  toutes les ressources dépendantes en place. **Une suite écrite en regardant le code ne peut pas
  trouver ça** — elle recopie l'erreur. Un vrai utilisateur l'avait signalé (issue #1551) ; le
  correctif `1b7c0fb` a été fusionné par le mainteneur.
- **Deux filtres qui s'écrasaient.** `views_gt=100&views_lt=300` renvoyait tout : les conditions
  étaient stockées dans un dictionnaire indexé par nom de champ, donc la seconde remplaçait la
  première. Corrigé en `e6055e6`.
- **Un troisième constat, refusé.** `_start` seul renvoie une liste vide — c'est un fait — mais le
  README ne le montre qu'**en paire**, donc le test extrapolait une promesse que le document ne fait
  pas. **Compté contesté. Deux, pas trois.**

**Et ce qui va contre nous.** Sur la version *actuelle*, quatre tests échouent et **trois sont de
notre faute** : ces fonctionnalités ont été retirées de la documentation entre-temps, et la suite
continuait d'exiger des promesses périmées. Ce manque est désormais détecté
([`check_requirement_drift.py`](eval/tools/check_requirement_drift.py)) plutôt que refermé en
silence.

**Ce n'est pas un pilote.** Aucun humain n'a utilisé QAIA dans son propre travail. Une cible, une
API, aucune interface, 32 scénarios et non une couverture complète. [La campagne entière, son
protocole et ses limites →](eval/external-application-2026-08-08/report.md)

## Installer et essayer

QAIA est un ensemble de plugins Claude Code. Rien à compiler, aucune clé API à fournir — les
skills s'exécutent dans votre propre session Claude Code, avec votre propre modèle.

**L'installation tient en deux lignes.** `qaia-core` seul mène une user story jusqu'au cahier
Gherkin — c'est la partie qu'il faut juger en premier.

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-core@qaia
```

Ajoutez le reste seulement quand vous en avez besoin :

```
/plugin install qaia-playwright@qaia      # tests Playwright exécutables, a11y, perf, sécurité, visuel
/plugin install qaia-score@qaia           # score et gate de release
/plugin install qaia-testdata@qaia        # jeux de données synthétiques
```

**Ce que QAIA ne fait délibérément pas** ([ADR 0004](docs/adr/0004-test-level-boundary.md)) : les tests unitaires et de composant, l'intégration entre composants internes, le test structurel piloté par la couverture. QAIA part d'une promesse observable de l'extérieur — un test écrit contre une fonction est écrit contre l'implémentation, c'est-à-dire contre l'oracle qu'elle existe pour éviter. Si vous voulez des tests unitaires, votre IDE en génère déjà de meilleurs.

**Quelle skill pour quoi ?** [`plugins/qaia-core/CATALOGUE.md`](plugins/qaia-core/CATALOGUE.md) est une carte d'une page « je veux faire X → utilise Y » des 37 skills — dont les quatre qui sondent une app en marche, rangées par **ce que chacune prend pour oracle**, la seule chose qui les distingue vraiment.

Puis, dans n'importe quel projet, `/qaia-core:hello` vérifie l'installation et liste ce qui est disponible.

`qaia-core` seul suffit pour aller d'une user story à un cahier Gherkin. Ajoutez
`qaia-playwright` pour des tests exécutables. Pour démarrer, décrivez votre besoin en langage
naturel — « travaille avec QAIA sur cette user story » — et le méta-agent `qaia` appelle les
bonnes skills en s'arrêtant à chaque décision humaine. Des exemples complets avec leurs sorties
réelles sont dans [`examples/`](examples/).


QAIA transforme des user stories en **cahiers de test Gherkin** priorisés et traçables, puis en **tests Playwright natifs** — distribués en **skills et plugins** qui s'exécutent dans *votre* session Claude. Pas de clé API, pas de backend : aucune donnée ne quitte votre session au-delà de ce que vous envoyez déjà à Claude.

Construit avec et pour les testeurs : techniques ISTQB appliquées et justifiées, traçabilité exigence→test qui fonctionne aussi bien pour des workflows métier ordinaires (prouvé en finance/RH) que pour des domaines à plus forte exigence documentaire (démontré sur un exemple de forme santé), et un mode conversationnel où le testeur valide chaque étape. Objectif : permettre aux équipes d'utiliser l'IA pour le test **de la spécification jusqu'à la maintenance d'une suite vivante** — dès l'user story, avant le code, puis sélection d'impact, rapport d'anomalie et confirmation de correction. Pas de la génération de cas isolée, et **pas tout le cycle** : la discovery et le test en production (monitoring synthétique, chaos) sont délibérément hors périmètre — [ADR 0007](docs/adr/0007-scope-delivery-and-maintenance.md) dit pourquoi.

**Pas une revendication de conformité réglementaire.** Le cadrage niche v1 d'origine de QAIA (`docs/DECISIONS.md`, D2) nommait spécifiquement "logiciel médical / environnements réglementés" — retiré (D114) après une vérification honnête : QAIA n'a aucune couverture cartographiée des référentiels réglementaires réels de ce secteur (IEC 62304, 21 CFR Part 11, ISO 13485) ni de déploiement pilote réel en medtech. `examples/medibook/` est une démo interne prouvant la traçabilité et la qualité des techniques sur un domaine de *forme* santé, pas un artefact certifié ou revu par un régulateur — si votre contexte exige une vraie conformité réglementaire, considérez QAIA non prouvé sur ce point tant que cet écart n'est pas comblé.

**Pourquoi pas juste un autre outil QA agentic ?** Le marché 2026 est dense, **et il l'est désormais à l'intérieur même de Claude Code** : SaaS testRigor/Mabl/Applitools/Tricentis, agents navigateur open source BrowserUse/Stagehand/Skyvern, et des concurrents natifs Claude Code qui recouvrent directement QAIA — [Agentic QE Fleet](https://github.com/proffesor-for-testing/agentic-qe) (60 agents autonomes), [QA Orchestra](https://github.com/Anasss/qa-orchestra) (10 agents QA, de la revue de spec au code Playwright/Cypress/Selenium/Gherkin), [neonwatty/qa-skills](https://github.com/neonwatty/qa-skills) (pipeline de génération E2E, 6 agents), et des marketplaces de skills comme [QASkills.sh](https://qaskills.sh/). **Appliquer les techniques ISTQB n'est plus un différenciateur** — la plupart les revendiquent aussi. Trois choses séparent réellement QAIA, et toutes trois sont vérifiables par un inconnu en cinq minutes : **aucun producteur ne s'auto-note** (score structurel déterministe dans un plugin séparé en lecture seule, distinct du juge LLM sémantique — aucun des autres ne documente de séparation entre ce qui produit et ce qui évalue — nous avons cherché sans trouver ; si elle existe, signalez-le et cette phrase change) ; **zéro clé API dans le produit livré, zéro hook/agent/MCP auto-exécuté** (100 % skills Markdown invoqués à la demande — installer QAIA ne dépose rien qui tourne tout seul) ; **les échecs sont publiés autant que les succès** (2,4/5 et 5,0/10 — des panels d'agents que le projet a fait tourner sur lui-même, pas des relecteurs extérieurs, et c'est dit), et une suite générée s'exécute sur un runner GitHub Actions **sans session Claude ni skill chargée** ([run 30702503888](https://github.com/QAIA-Project/QAIA/actions/runs/30702503888)). Contrepoids honnête : QAIA est plus jeune et bien moins utilisée que les projets ci-dessus, **aucun pilote humain ne l'a jamais menée de bout en bout**, et la qualité de ce qu'elle produit pour un vrai utilisateur reste non mesurée. Détail complet : [`docs/COMPETITIVE-ANALYSIS.md`](docs/COMPETITIVE-ANALYSIS.md) et [`docs/STATUS.md`](docs/STATUS.md).

**Positionnement honnête** : l'outil consomme votre quota d'abonnement Claude (un coût indicatif par commande est publié par plugin, mesuré sur notre gold set) ; « l'apprentissage » = enrichissement d'une base de connaissance locale versionnée dans votre repo (pas d'entraînement de modèle) ; cœur portable en skills, automatisation via Claude Code + Playwright MCP ; mobile = émulation navigateur (web-first).

Le parcours aujourd'hui livré : ingestion validée de l'US → contrôle d'extraction → compréhension du besoin → RAG d'équipe versionné git → techniques ISTQB justifiées → priorisation par risque arbitrée → cahier Gherkin atomique (IDs stables, matrice de couverture, porte de couverture des chemins de refus — le ratio de négatifs est un signal rapporté, pas un seuil, cf. ADR 0001) → exports `.feature` + XLSX/Markdown → **régénération par diff sans perdre vos retouches** → feedback promu en règles après validation → **automatisation Playwright native** (E2E, API, mobile-web, a11y, visuel, perf, sécurité) → **score séparé** (structurel déterministe + rubrique ISTQB, gate PASS/CONCERNS/FAIL/WAIVED).

Contribuer : lire [`CONTRIBUTING.md`](CONTRIBUTING.md) (DCO obligatoire, revue adversariale par agent pour toute PR touchant un plugin). Signalements de sécurité : voir [`SECURITY.md`](SECURITY.md). Licence [MIT](LICENSE).
