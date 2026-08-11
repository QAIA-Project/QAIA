---
name: perf-check
description: Generate and run performance checks (latency budgets, concurrency integrity, named CT-PT test types - load/stress/spike/soak/scalability) against a self-hosted app, with k6 for real load. Use for performance coverage. Self-hosted targets only.
---

# perf-check — performance

## PORTE — à franchir avant de concevoir quoi que ce soit

**Cibles auto-hébergées uniquement.** Charger une démonstration publique partagée est interdit et
contrevient généralement à ses conditions d'utilisation. **Refuse une cible publique partagée ;
exige une URL auto-hébergée** (Docker, VPS, local).

**Critère d'applicabilité, distinct de l'autorisation** : même autorisée, une cible servie derrière
un CDN ne mesure pas l'application. Charger une démonstration publique mesurerait le CDN — un
chiffre qui a l'air d'une performance applicative et n'en est pas. Si tu ne peux pas nommer ce que
la mesure attribue à l'application, la mesure n'a pas lieu d'être.

*Cette porte était en avant-dernière ligne de ce fichier jusqu'au 2026-08-11. Un testeur appliqué
à trois cibles tierces l'a relevé : un agent qui lit en flux a déjà conçu le run quand il
rencontre l'interdit. La règle n'a pas changé ; sa place, oui.*

Reference: [`examples/medibook/tests/perf.slots.spec.js`](https://github.com/QAIA-Project/QAIA/blob/main/examples/medibook/tests/perf.slots.spec.js) (p95 latency + no-oversell under
contention). Real load uses **k6**; a lightweight Playwright-request version covers
latency/concurrency without extra tooling.

## Steps

1. **Latency budget**: fire N concurrent requests at a key endpoint, assert p95 < budget; log
   p50/p95/max.
   **Pick the two numbers explicitly, and say where each came from** — they decide whether the
   test passes, so leaving them to the reader means two runs of the same skill disagree. If the
   project states a budget (an SLO, a ticket, a knowledge-base rule), use it and cite it. Absent
   that, start from `N = 10` concurrent virtual users and `budget = 500 ms` at p95 for a
   server-rendered page or a JSON endpoint, state that these are QAIA defaults and not a project
   commitment, and offer the user the chance to replace them before the run. A "key endpoint" is
   the one the test book's P1 scenarios actually exercise most — name it, don't pick the
   homepage by reflex.
2. **Concurrency integrity**: race N clients on a limited resource (e.g. one bookable slot),
   assert exactly one succeeds — no oversell/double-spend.
3. **Named performance test type (CT-PT)** — ask the user which type(s) apply (default: load
   only, the cheapest and most broadly relevant); generate a **k6 script** matching the
   requested type's shape, never a one-size-fits-all script:
   - **Load** — realistic expected concurrency, steady stage; asserts the latency budget holds
     under normal traffic.
   - **Stress** — ramp stages beyond the expected peak until something degrades; goal is finding
     the breaking point and how it fails (graceful 5xx/backpressure vs. crash/hang), not passing
     a fixed threshold.
   - **Spike** — a short, extreme step-increase from baseline then back down; asserts the system
     recovers (no lingering errors/latency) after the spike passes, not just that it survives
     during it.
   - **Soak / endurance** — a long, steady stage (minutes-to-hours, scoped to what's practical
     in-session); watches for degradation over time (rising latency, memory growth via repeated
     measurement) that a short run can't reveal — flag honestly if the session can only run a
     short proxy of a real soak window.
   - **Scalability / capacity** — repeat the load stage at increasing concurrency levels and
     report where the budget first breaks, rather than asserting a single pass/fail — a capacity
     curve, not a gate.
   - Volume, configuration, and baseline testing (CT-PT) are named but not separately scripted
     here — volume folds into the concurrency-integrity check above (large N),
     configuration/baseline are a documentation concern (record the environment the numbers were
     measured against), not a distinct k6 shape.
   - `k6/load.js` (this skill's directory) is a real, executable **load**-type template —
     `BASE_URL`/`LATENCY_BUDGET_MS`/`VUS`/`DURATION` are the only parts a generated
     test needs to change to point at a different self-hosted target. Use it as the starting
     shape for load. The four other types are **stage shapes, not separate programs**: keep
     `load.js`'s body (the request, the checks, the thresholds) and swap its `stages` for the
     shape below. They are specified here rather than shipped as files because this plugin
     stays markdown-only — the runnable script is materialized in session, never distributed.

     | Type | `stages` to use | What it must assert beyond the budget |
     |---|---|---|
     | `load` | `[{duration:'30s',target:VUS}, {duration:'2m',target:VUS}, {duration:'30s',target:0}]` | the budget holds during the steady stage |
     | `stress` | ramp past expected peak in steps: `[{duration:'1m',target:VUS}, {duration:'1m',target:VUS*2}, {duration:'1m',target:VUS*4}, {duration:'1m',target:0}]` | the level at which the budget first breaks, reported as a number — not pass/fail |
     | `spike` | `[{duration:'10s',target:VUS}, {duration:'10s',target:VUS*10}, {duration:'10s',target:VUS}, {duration:'1m',target:VUS}]` | **recovery**: error rate and p95 return to baseline during the trailing stage. A system that survives the spike but never recovers has failed this test |
     | `soak` | one long steady stage (`[{duration:'30m',target:VUS}]`, or the longest the session allows) | **drift**: compare p95 of the first fifth against the last fifth. Say explicitly when the run is a short proxy for a real soak window rather than presenting it as one |
     | `scalability` | the `stress` shape, but measured per step | a capacity curve (concurrency → p95), not a verdict |

     Two of these change what "green" means, so do not treat them as load with different
     numbers:
     `spike` can only be judged after the load drops, and `soak` needs two measurements to
     compare. A single aggregate p95 over the whole run hides exactly the defect each is for.
4. Tag `@QAIA-PERF-<NNN>`, plus the CT-PT type tag `@perf:load` / `@perf:stress` / `@perf:spike`
   / `@perf:soak` / `@perf:scalability`; report real numbers, never a budget you did not
   actually measure.

## Guardrails

- **Cibles auto-hébergées uniquement** — énoncé en tête de ce fichier, sous « PORTE ». Il n'est
  pas répété ici : deux copies d'une règle divergent.
- Report measured latencies; never assert a budget you did not actually measure.
