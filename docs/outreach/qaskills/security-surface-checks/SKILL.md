---
name: Security Surface Checks
description: The six passive security checks a QA engineer can own — auth boundaries, IDOR, error handling, user enumeration, headers, ZAP baseline — each with its fixture requirement and its well-known way of being run wrong. Use when security coverage must stop being a checkbox: a check that tests nothing stops looking like a pass. Authorized targets only.
version: 1.0.0
author: opaland
license: MIT
tags: [security, idor, authorization, user-enumeration, owasp, ct-sec]
testingTypes: [security, api, e2e]
frameworks: [playwright]
languages: [typescript, javascript]
domains: [web, api]
agents: [claude-code, cursor, github-copilot, codex]
---

# Security Surface Checks

> **Standalone adaptation.** Self-contained version of the `security-surface` skill from
> [QAIA](https://github.com/QAIA-Project/QAIA) (MIT). The canonical version and its `references/`
> live in that repository. QAIA is pre-alpha and says so.

## Scope, stated before anything else

**Passive: observation only.** No active exploitation, no payload fuzzing, no destructive
request. An unattended agent running active exploitation against someone's application is a
liability, not a test. An OWASP ZAP baseline scan is available as an opt-in extra.

**Self-hosted or explicitly authorised targets only.**

This is what a QA engineer can own without becoming a pentester. It does not replace one.

## Step 0 — Rank the assets before running the checklist

A fixed checklist run uniformly treats every application the same regardless of what it actually
protects.

1. **Name the sensitive assets the application actually holds** — from the story or the
   specification, never invented. Credentials, other users' personal data, payment data, admin
   functions, and anything whose breach is notably worse than a generic record: health data,
   financial totals, access tokens.
2. **Rank the threats per asset** by impact × probability. A payment-data asset raises IDOR and
   enumeration to the top; an admin-function asset raises the auth-boundary checks.
3. **Record the ranking**: asset → top-priority check → why. That record *is* the difference
   between a flat checklist and a risk-based one.
4. **Never skip a check because an asset looks low-risk.** Risk-based means *prioritised*, not
   *reduced coverage*. A quiet asset still gets the full pass, just not the first or deepest one.

Propose the ranking with your reasoning and let a human arbitrate. Never a silent verdict.

---

## S1 — Auth boundaries

**Four distinct cases, not one.** Protected endpoints must reject: a **missing** token, a
**malformed** token, an **expired** token, and a **foreign-signed** token — each with 401.

Testing only the missing-token case is the common shortcut, and it is the weakest of the four.

## S2 — IDOR / cross-tenant

**The most frequently mis-run check in this list, and the one with the highest hit rate on real
applications.**

**Fixtures — mandatory. The check is void without them.**
- **Two real accounts**, A and B, both valid, both authenticated, ideally in different tenants.
- **A resource created by A during the run**, so its id is known and its ownership certain.
- **B's genuine, valid token** — not an absent one, not an invalid one.

**Requests, with B's valid token, against A's resource id:**

| Case | Method | Expected |
|---|---|---|
| S2-a | `GET /resource/{A_id}` | 404 (or 403) |
| S2-b | `PUT`/`PATCH /resource/{A_id}` | 404 (or 403), **and A's resource unchanged** |
| S2-c | `DELETE /resource/{A_id}` | 404 (or 403), **and A's resource still exists** |
| S2-d | `GET /resources` | A's resource absent from B's list |

**Then repeat S2-a with A's own token and expect 200.** Without that control, a mistyped id or a
resource that never existed makes every 404 look like a pass — the check would "succeed" against a
completely broken endpoint.

**404 is preferred over 403** where the *existence* of the resource is itself sensitive: a 403
confirms *"this id exists, you just can't have it"*. Whichever you choose must be **consistent**
between existing-but-foreign and never-existed ids — an application answering 403 for one and 404
for the other has rebuilt the enumeration oracle it was trying to close.

**The usual mis-run, named because it is the whole point.** Testing with a **missing or invalid
token** instead of B's valid one. That is S1. It tests *authentication* and passes trivially. IDOR
is an **authorization** failure: the caller is perfectly authenticated and simply asks for
something that is not theirs.

**If there is no second account, it is not an IDOR test.** Report it as *blocked for want of a
second account* — never as passed.

**Second mis-run.** Checking read only. Write paths are frequently authorized separately from read
paths, and `DELETE` is regularly the one left unguarded. S2-b and S2-c must verify the **side
effect** by re-reading as A, not just the status code: an API can return 403 and still have
applied the change.

## S3 — Robust error handling

Malformed bodies, wrong content types, oversized payloads, unsupported methods. The application
must refuse without leaking a stack trace, a framework banner, a SQL fragment or an internal path.

**The honest boundary:** if the specification documents no error contract, an odd-but-harmless
response is an **observation**, not a defect. Record it so a human can decide whether to *add* the
promise — do not fill the gap with a guess about what the application should have done.

## S4 — User enumeration

**Fixtures.** One valid username, one certain not to exist.

**Requests.** Valid user + wrong password; non-existent user + any password; and where applicable,
a locked or disabled user + wrong password.

**Expected — identical on all three channels:**
- **Body**, same message byte for byte;
- **Status**, same code;
- **Timing**, no systematic difference. Send each case ~20 times and compare medians. A consistent
  gap — often ~100 ms, because a real user's password gets hashed while a non-existent one
  short-circuits — **is a working oracle even when the messages match**.

Check password reset and registration too. Reset flows are where enumeration usually survives
after the login form has been fixed (*"no account with that email"*).

**The usual mis-run.** Comparing only the message string. Timing and status are the channels that
stay open after someone has unified the copy.

## S5 — Headers and cookies

`Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`,
`Referrer-Policy`; and on session cookies: `Secure`, `HttpOnly`, `SameSite`.

Report what is absent. Do not present a missing header as an exploit.

## S6 — OWASP ZAP baseline (opt-in)

Passive spider and passive rules only. Never the active scanner without explicit written
authorisation for that specific target.

---

## Guardrails

- **Advisory only, never a gate.** These findings feed human review. A QA-owned passive pass is
  not a penetration test and must not be reported as one.
- **A blocked check is reported as blocked.** Never as passed. Most of the value of this list is
  in refusing to count a check that could not really run.
- **Never test a target you do not own or have not been explicitly authorised to test**, and keep
  every request non-destructive: single requests, no load shape, no data deletion outside
  fixtures you created.
