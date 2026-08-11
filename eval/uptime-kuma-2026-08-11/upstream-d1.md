## Summary

`responseMaxLength = 0` stores **nothing** instead of storing everything, contradicting the field's own description.

The description shown next to the input reads:

> Maximum size of response data to store. **Set to 0 for unlimited.** Larger responses will be truncated. Default: 1024 (1KB)

The input is `type="number"` and accepts `0`, so this is a value the form invites you to enter.

## Steps to reproduce

Version: **2.5.0** (`d9a60dfc73140d15111752e4e8910ed4b54bd9a3`), self-hosted, SQLite, Node 24.13.

1. Run a local HTTP endpoint that returns a body of a known size with a 5xx status (so the body is stored via `saveErrorResponse`).
2. Create three HTTP monitors against it, all with `saveResponse` / `saveErrorResponse` enabled:
   - A: `responseMaxLength = 0`, response body 10 characters
   - B: `responseMaxLength = 0`, response body 5000 characters
   - C: `responseMaxLength = 1024`, response body 10 characters *(control)*
3. Wait for one beat each and read the stored response on the heartbeat.

## Expected

With `0`, the description promises **unlimited** — the full body should be stored. At minimum, a 10-character body should survive.

## Actual

| Monitor | `responseMaxLength` | Body sent | Stored |
|---|---|---|---|
| A | 0 | 10 chars | `... (truncated)` — **0 characters kept** |
| B | 0 | 5000 chars | `... (truncated)` — **0 characters kept** |
| C (control) | 1024 | 10 chars | `xxxxxxxxxx` — correct |

So `0` is not treated as "unlimited" but as a literal truncation length of zero: **every** response is reduced to the truncation marker alone, regardless of size.

Reproduced 3× on this version, and independently on a second clean clone of the same tag.

## Why it is worth a line

The failure is silent and it destroys the data the setting exists to keep. Someone who reads the description and sets `0` in order to *keep more* ends up keeping **less than the default** — the exact opposite of the intent — and only discovers it when they need the stored response to debug an incident.

## Possible fix

Treat `0` as "no truncation" before applying the slice, rather than passing it through as a length. (I have not sent a PR; happy to if that reading of the intent is right.)

<sub>Found while using Uptime Kuma as a target for an open-source QA tooling project. Everything ran locally on `127.0.0.1`; the monitored endpoint was a small HTTP server written for the exercise, never a third-party service. Thanks for the project — the rest of what we exercised (retries, retryInterval, timeout, resendInterval, upside-down, keyword matching, maintenance timezones) matched its documentation exactly.</sub>
