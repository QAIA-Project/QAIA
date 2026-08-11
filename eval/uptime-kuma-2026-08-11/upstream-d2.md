## Summary

A **recurring** maintenance window never activates on its first occurrence when the *Effective Date Range* starts on the same day — which is what the form fills in by default. No error is raised, the status stays `Scheduled`, and notifications are **not** suppressed during the intervention the user believes is covered.

## Steps to reproduce

Version: **2.5.0** (`d9a60dfc73140d15111752e4e8910ed4b54bd9a3`), self-hosted, SQLite, Node 24.13.

Two maintenances side by side, same daily window (say `14:55`), same monitors, differing only in the start of the effective date range:

| | Effective range starts | Status at 14:55:00 | Monitors |
|---|---|---|---|
| A | **yesterday** | `under-maintenance` | suppressed, as expected |
| B | **today** | still `scheduled` | **UP — beats continue, notifications fire** |

B is the one the UI produces if you accept the default range.

## The mechanism, isolated outside the product

`startAt` is built from the effective range's start date plus the window's time, so it lands **exactly** on the first occurrence — and `croner` treats that bound as strict:

```js
const { Cron } = require("croner");            // croner 8.1.2, as shipped

new Cron("55 14 * * *", { startAt: new Date("2026-08-11T14:55:00") })
  .nextRun(new Date("2026-08-11T14:54:00"));   // -> 2026-08-12T14:55  (today is skipped)

new Cron("55 14 * * *", { startAt: new Date("2026-08-10T14:55:00") })
  .nextRun(new Date("2026-08-11T14:54:00"));   // -> 2026-08-11T14:55  (fires today)
```

Three lines, no Uptime Kuma involved. The A/B above is the same thing observed end to end.

## Expected

A maintenance whose effective range starts today, with a window later today, should run **today**.

## Why it matters more than the one skipped run

The failure mode is silent and it points the wrong way: the UI says `Scheduled`, so the operator believes the window is in place and proceeds with the intervention — while alerts keep firing. Someone creating a maintenance for *this evening* on the morning of the same day gets no window at all, and no indication of why.

## Possible fix

Set `startAt` to the beginning of the effective start date (or one second earlier) rather than to the first occurrence itself, so the bound cannot swallow it.

## Prior art I checked before filing

#4738, #4939, #5872 / #5903 / #5914 and #6118 are neighbouring maintenance-scheduling fixes; none of them describes the first occurrence being skipped. #6360 and #4930 are different symptoms. If this is a known duplicate I missed, close it without ceremony.

<sub>Found while using Uptime Kuma as a target for an open-source QA tooling project. Everything ran locally on `127.0.0.1`; the monitored endpoint was a small HTTP server written for the exercise, never a third-party service.</sub>
