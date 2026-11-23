# Validation — contract-probe on `fixture/taskapi/` (2026-07-26)

Worked example following `../../references/01-probing-a-live-app.md` step by step against a small, purpose-built fixture SUT
(`fixture/taskapi/`) with one defect injected on purpose (see `server.js`'s own comment) — a
minimal but real running app, not a hypothetical.

## Step 1 — Contract extracted from `fixture/taskapi/README.md`

| # | Promise | Source |
|---|---|---|
| P1 | `POST /tasks` creates a task with a positive integer id and a trimmed title | README §"What this API promises", item 1 |
| P2 | `GET /tasks/:id` returns 404 for any nonexistent/malformed id, **never a 5xx** | item 2 |
| P3 | `POST /tasks` with a missing/empty title is refused with 422 | item 3 |

## Step 2-3 — Probes and verdicts (real requests against `node server.js`, port 4600)

| Promise | Probe input | Observed | Verdict |
|---|---|---|---|
| P1 | `{"title":"  clean me  "}` | `201 {"id":1,"title":"clean me"}` | **Kept** |
| P3 | `{"title":""}` | `422 title is required` | **Kept** |
| P3 | `{}` (missing field) | `422 title is required` | **Kept** |
| P3 | `{"title":"   "}` (whitespace-only, adversarial) | `422 title is required` | **Kept** |
| P3 | `{"title":12345}` (non-string, type-confusion adversarial) | `422 title is required` | **Kept** |
| P2 | `GET /tasks/1` (existing) | `200` | **Kept** |
| P2 | `GET /tasks/999` (nonexistent, plain integer) | **`500 {"error":"internal error"}`** | **BROKEN** |
| P2 | `GET /tasks/1e2` (scientific notation, adversarial) | **`500`** | **BROKEN** (same root cause) |
| P2 | `GET /tasks/1.5` (decimal, adversarial) | **`500`** | **BROKEN** (same root cause) |
| P2 | `GET /tasks/99999999999999999999` (out-of-range, adversarial) | **`500`** | **BROKEN** (same root cause) |

**Honest note on what "adversarial" actually caught here**: the root-cause defect
(`server.js`'s `Number(raw)` guard not checking `Number.isInteger`/array-bounds before use)
is triggered by *any* nonexistent numeric id, including the plain, unremarkable `999` — not
only the more exotic adversarial variants. A happy-path-only test suite that only ever checks
the *one* id it just created would never notice; the defect surfaces the moment anything probes
"what if the resource doesn't exist," adversarial or not. Reported exactly as found, not
inflated into a more exotic-sounding defect than it is.

## Step 4 — Reproduction

Confirmed on 2 independent runs (same 4 inputs, fresh server restart between runs) — not a
one-off flake. Root cause traced by reading `server.js`: `Number(raw)` passes the `!id` guard
for any truthy non-zero result, then `tasks[id].title` throws when `id` is not a valid,
populated array index — an unhandled rejection caught only by the process-level `.catch()`
added around `route()`, which returns 500 rather than crashing the whole server (see that
file's own comment on why the catch exists without being the fix).

## Step 5 — Regression scenario generated

`fixture/generated-regression.feature` — one scenario, `@QAIA-CP-001 @negative`, citing
`README.md`'s promise P2 in a `# contract:` comment, reproducing the minimal triggering input
(`GET /tasks/999`). **No fix was applied to `server.js`'s defect** — the injected defect is
left in place on purpose, since this fixture's job is to prove the skill *finds and reports*,
not to demonstrate a fix workflow (that discipline is already proven separately by
`locator-repair`'s fixture, #37).

## Step 6 — Report (as the skill would present it)

2 of 3 documented promises hold under adversarial probing (P1, P3 — including 3 adversarial
sub-probes each survived cleanly). 1 of 3 is broken (P2): `GET /tasks/:id` returns 500 instead
of the documented 404 for any nonexistent numeric id. 1 regression scenario generated,
`@QAIA-CP-001`.
