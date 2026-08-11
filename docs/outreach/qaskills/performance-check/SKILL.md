---
name: Performance Budget Check
description: Set a latency budget and say where the number came from, prove a limited resource cannot be oversold under concurrency, and pick the CT-PT test type the question actually calls for. Use when a performance number needs a justification — spike and soak change what green means and are not load with different numbers. Self-hosted targets only.
version: 1.0.0
author: opaland
license: MIT
tags: [performance, k6, load-testing, concurrency, ct-pt, latency]
testingTypes: [performance, api]
frameworks: [k6, playwright]
languages: [typescript, javascript]
domains: [web, api]
agents: [claude-code, cursor, github-copilot, codex]
---

# Performance Check

> **Standalone adaptation.** Self-contained version of the `perf-check` skill from
> [QAIA](https://github.com/QAIA-Project/QAIA) (MIT). QAIA is pre-alpha and says so.

## Before anything: self-hosted targets only

**Load-testing a shared public demo is forbidden and usually against its terms.** Refuse a public
shared target and require a self-hosted URL — Docker, VPS or local. This is not a formality; it is
the difference between a test and an incident on someone else's infrastructure.

## 1. Latency budget — and say where both numbers came from

Fire N concurrent requests at a key endpoint, assert p95 below budget, log p50 / p95 / max.

**N and the budget decide whether the test passes, so leaving them implicit means two runs of the
same skill disagree.**

- If the project states a budget — an SLO, a ticket, a documented rule — **use it and cite it**.
- Absent that, start from **N = 10** concurrent virtual users and **p95 < 500 ms** for a
  server-rendered page or a JSON endpoint, **say explicitly that these are defaults and not a
  project commitment**, and offer to replace them before the run.

**A "key endpoint" is the one the highest-priority scenarios actually exercise most.** Name it.
Do not pick the homepage by reflex.

## 2. Concurrency integrity — the check that is not about speed

Race N clients on a limited resource — one bookable slot, one unit of stock, one coupon — and
assert **exactly one succeeds**. No oversell, no double-spend.

This finds a class of defect a latency budget never will, and it is usually the more expensive
one in production.

## 3. Pick the CT-PT type the question calls for

Ask which type applies. Default to **load** — the cheapest and most broadly relevant. Then
generate a script matching *that* type's shape, never a one-size-fits-all script.

| Type | `stages` | What it must assert **beyond** the budget |
|---|---|---|
| **load** | `[{duration:'30s',target:VUS},{duration:'2m',target:VUS},{duration:'30s',target:0}]` | the budget holds during the steady stage |
| **stress** | ramp past the expected peak in steps: `VUS`, `VUS*2`, `VUS*4`, … | **where it breaks and how** — graceful 5xx and backpressure, or crash and hang. Not a fixed threshold |
| **spike** | `[{duration:'10s',target:VUS},{duration:'10s',target:VUS*10},{duration:'10s',target:VUS},{duration:'1m',target:VUS}]` | **recovery** — errors and latency return to baseline *after* the spike passes |
| **soak** | one long steady stage — 30 min, or the longest available | **drift** — compare p95 of the first fifth against the last fifth |
| **scalability** | the stress shape, measured per step | a **capacity curve** (concurrency → p95), not a verdict |

**Two of these change what "green" means, so do not treat them as load with different numbers.**
*Spike* can only be judged **after** the load drops. *Soak* needs **two** measurements to compare.
A single aggregate p95 over the whole run hides exactly the defect each one exists to find.

The other CT-PT types are named rather than scripted: **volume** folds into the
concurrency-integrity check with a large N, and **configuration** and **baseline** are a
documentation concern — record the environment the numbers were measured against.

## 4. Tag and report

Tag `@PERF-<NNN>` plus the type: `@perf:load`, `@perf:stress`, `@perf:spike`, `@perf:soak`,
`@perf:scalability`.

## Guardrails

- **Report measured latencies. Never assert a budget you did not actually measure.** A threshold
  in a script that never ran against the target is a number with no evidence behind it.
- **A soak the session was too short to run is a short proxy, and must be reported as one.** Half
  an hour is not a soak window; saying so costs one line and keeps the number honest.
- **Never load-test a target you do not own.**
