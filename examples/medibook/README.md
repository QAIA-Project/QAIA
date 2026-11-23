# Example — MediBook: full QAIA chain against a real running app

This is an **end-to-end worked example** (Sprint 5, July 2026): a small but real teleconsultation booking app (the SUT — System Under Test), the QAIA-designed test book, and the executable Playwright automation that runs against it — proving requirement → scenario → automated test traceability on live software, not just on paper.

The SUT implements the acceptance criteria of `eval/gold-set/US-001-appointment-booking.md`, so the generated Gherkin scenarios (`@QAIA-US-001-xxx`) map to real, executable behavior.

## Why a local app instead of a public demo site

Public demo sites (OpenEMR, Practice Software Testing, SauceDemo…) are excellent QA practice targets — see `docs/DEMO-TARGETS.md` for a vetted catalog. But shared public demos forbid load and security testing, and a sandboxed/offline CI cannot reach them. **Self-hosting the target** (Docker, npm, a VPS such as OVH, or a local server like this one) lifts both limits and is the recommended setup for perf/security work.

## Run it

```bash
# 1. start the SUT
cd app && node server.js          # http://localhost:4400

# 2. in another shell, run the automation
cd tests && npm install
npx playwright test               # 26 tests, 32 executions: e2e desktop + mobile, api, security, perf, a11y, visual
```

## What it demonstrates

| Test type | File | Coverage |
|---|---|---|
| E2E web (IHM) | `tests/e2e.booking.spec.js` | Booking journey via the UI, desktop **and** Pixel 7 emulation |
| API | `tests/api.booking.spec.js` | REST-level AC checks (filters, 2h/4h/3-cap boundaries, race → 409, minor rules, auth, audit) |
| Accessibility | `tests/a11y.booking.spec.js` | axe-core, WCAG 2 A/AA, zero serious/critical violations |
| Visual | `tests/visual.booking.spec.js` | Screenshot baselines (login, booking) |
| Security surface | `tests/security.booking.spec.js` | Missing / forged token → 401, IDOR on cancellation, malformed body does not 500, no user enumeration at login |
| Performance | `tests/perf.slots.spec.js` | p95 latency budget on `GET /slots`, consistency of concurrent bookings — self-hosted only |
| Mobile | `e2e-mobile` project | Browser emulation (Pixel 7) — **native iOS/Android is out of scope, honest per decision D100** |

## Design notes

- **POM as fixtures** (modern Playwright, project decision): one page object per screen (`pages/`), selectors by role / `data-testid` only (T2), **no assertions inside page objects** — assertions live in tests. Page objects are exposed as fixtures (`fixtures.js`) so every test gets fresh instances and a reset SUT.
- **Traceability**: every test title carries its stable scenario ID (`@QAIA-US-001-003`) and AC tag (`@AC5`) — the same IDs the QAIA test book uses, so requirement → Gherkin scenario → automated test is one continuous chain.
- **Atomic preconditions**: each test resets the SUT and establishes its own state declaratively (no UI-chained setup) — the automation-layer counterpart of the atomic-scenario rule.

## Real findings from this sprint (the automation earning its keep)

1. **Flaky test → shared-state race**: the booking test failed intermittently (desktop, then mobile). Root cause was not the app but the **test infra**: parallel workers hitting one SUT with global in-memory state, each `/api/reset` stomping another test. Fix: `workers: 1` (serialize) — documented in `playwright.config.js`. Lesson: a mutable shared SUT requires serial execution or per-test isolation.
2. **Browser version pinning**: the preinstalled Chromium (build 1194) mismatched the freshly installed Playwright's expectation → `executablePath` pinned in config.
3. After both fixes: **24/24 green, deterministic across repeated runs** (the count at the time; the security and performance files were added later, bringing the suite to 26 tests and 32 executions).
