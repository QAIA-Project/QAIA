---
name: traffic-replay
description: Ingest a user-provided HAR file (or equivalent captured HTTP traffic export) and derive non-regression test conditions -- observed status, response shape, significant headers, timing -- from real request/response pairs, with mandatory PII/secret masking before any write. Never captures live traffic, never runs a proxy, never sends a network request itself. Use when the user has a HAR export and wants what actually happened turned into regression conditions, not a coverage test book.
---

# traffic-replay — captured traffic → non-regression conditions

Shift-right gap this closes: `perf-check`/`security-surface`/`a11y-audit` are active checks run
against a live app; nothing else in QAIA derives test conditions from **real traffic that already
happened**. It works the way every analysis skill in this plugin works: read an artifact the user
already has and report only what it shows — the same anti-fabrication discipline as ingestion
(honest recall beats fabricated recall: never assert more than the artifact supports), and the
same mask-before-write discipline, extended here from user-story text to HTTP traffic.

Reference fixture: `fixture/` in this skill folder — a fully **synthetic** HAR
(`demo-traffic.har`) for a fictional app ("TaskFlow"), hand-built for this validation, never
real production data (the issue's own acceptance criterion). It deliberately contains an
`Authorization` header, a session cookie, a query-string token, an email, a phone number, a
full name and a card number, so the masking step has real sensitive-shaped values to catch.
See `fixture/VALIDATION.md` for the worked example and the grep proof that none of the
injected values leak into the output artifacts.

## Input

- A **HAR file (HAR 1.2)** the user provides — exported from a browser's DevTools Network
  panel, or an equivalent proxy/tool export the user already has. **Never captured live by
  this skill**: no proxy, no MITM, no browser automation to *generate* new traffic, no network
  call of any kind from the skill itself. If asked to "go capture what the app does," say
  plainly that is out of scope and point at exporting a HAR from the browser, or `automate` for
  generating new test traffic.
- Optionally, a target US-ID if the user wants the derived conditions merged into that story's
  manifest (see Output). Not required — captured traffic often spans more routes than one US.

## Masking (blocking, before any write — the ingestion masking discipline, extended to HTTP traffic)

Applied to **every** request and response in the HAR before any finding, table, or JSON file
is written — never after the fact, never partially. This parses naturally as a short-lived,
in-session script (skills ship no runtime code: executable code is generated and run in the
user's session, thrown away, never distributed in the plugin) that deterministically applies the rules below; `fixture/build-findings.py`
is the actual script used to produce this skill's own validation evidence, kept here for
transparency, not as runtime code the plugin auto-executes.

| Category | Rule | Placeholder |
|---|---|---|
| Auth headers | `Authorization` (any scheme), and any header name matching `/auth\|api.?key\|x-.*-token\|x-.*-secret/i` | `[REDACTED:auth-header]` |
| Cookies | `Cookie` request header and `Set-Cookie` response header, in full — a session cookie is itself a bearer credential | `[REDACTED:cookie]` |
| Query tokens | Query-string parameter **values** whose key matches `/token\|key\|secret\|session\|auth\|password/i` (the param *name* is kept — see grouping) | `[REDACTED:query-token]` |
| Email | Regex-matched email addresses anywhere in headers, query values, URLs, or bodies | `[REDACTED:email]` |
| Phone | Regex-matched phone numbers (international/local formats) in bodies | `[REDACTED:phone]` |
| Card number | Digit runs of 13-19 chars (separators stripped) that pass a **Luhn checksum** — a checksum beats a naive digit-count regex, same logic class `oracle-generate`'s Luhn oracle encodes | `[REDACTED:card]` |
| Name (heuristic) | String values under JSON keys matching `/name\|assignee\|author\|owner\|contact/i` | `[REDACTED:name]` |
| Password/secret/token body fields | String values under JSON keys matching `/password\|passwd\|pwd\|secret\|token\|api.?key/i` (a body carrying a login credential or a session/API token, even in a test/demo HAR, is never echoed — this is distinct from the header-level auth rule above, which only covers header values) | `[REDACTED:secret]` |

- **No redaction ledger** (mirrors the ingestion rule exactly): never persist a mapping from an original value
  to its placeholder. The only record kept is `type -> placeholder -> count` per HAR.
- **Independent second layer**: the response-shape fingerprint (Method, step 4) records
  **keys and value types only, never values** — so even a value the regex/heuristic list above
  misses cannot reach that fingerprint. It can still reach a header value or a body the skill
  quotes verbatim nowhere in its output (the skill never quotes raw bodies — see Output).

## Method

1. Parse the HAR's `log.entries[]`.
2. Apply Masking (above) to every header, query value, and body value on the in-memory parsed
   structure before touching anything else — never write an unmasked copy "for reference."
3. Group entries into **signatures**: `method` + `path` (no query string) + the **sorted set of
   query parameter names present** (names only, never values). Two calls to `/api/tasks/1` and
   `/api/tasks/2` are two different signatures — **never** collapsed into an inferred
   `/api/tasks/{id}` template; that generalization is not something the HAR itself asserts, and
   this skill does not make it on the user's behalf. Two calls to the same path with the same
   query-param-name-set but different values are the **same** signature (repeat samples) — a
   different param-name-set is a different signature (e.g. `GET /api/tasks` vs
   `GET /api/tasks?status&token` are two signatures, not one).
4. For each signature, derive a condition record:
   - **Observed status(es)**: exact HTTP status code(s) seen. A signature seen twice with two
     different statuses reports both, split honestly (e.g. "200 in 3/4, 500 in 1/4") — never
     averaged, never "the more common one" silently dropping the outlier.
   - **Response shape fingerprint**: for a JSON body, top-level keys and their type
     (`string`/`number`/`boolean`/`array`/`object`/`null`) — values never included, masked or
     not. For a non-JSON body: `content-type` and byte size only, stated as "not a JSON
     structure, no fingerprint" rather than guessed.
   - **Significant headers**: `content-type` and any cache/security headers actually present
     (`cache-control`, `content-security-policy`, `x-content-type-options`, etc.) — presence/
     value as observed. Absence in this capture is reported as absence **in this capture**,
     never generalized to "this app lacks X."
   - **Timing**, only if the entry carries `time`/`timings`: the observed total ms as a single
     measured sample — explicitly not a p95/budget. A signature with N>1 samples reports each
     observed time, never an average presented as a guarantee; point at `perf-check` for an
     actual latency budget (needs repeated, controlled samples, not opportunistic capture).
   - **Sample count** and an explicit `singleSample: true/false`.
5. **Honesty on N=1 (honest recall, applied to traffic).** A signature observed once is reported as
   "1 sample observed" and documents only what happened that one time — never implies the
   status/shape is guaranteed to recur. This is the default for most routes in any real HAR;
   say so rather than quietly treating a single capture as a stable contract.

## Output

- A findings table (Markdown) + the same data as JSON: one row per condition
  (`@QAIA-TRAFFIC-<NNN>` ID, method, path, query-param-name-set, sample count, observed
  status(es), response shape fingerprint, significant headers, timing if present, single-sample
  flag).
- `piiMasked`: `type -> placeholder -> count` summary for the whole HAR (no ledger).
- **If a US-ID is given/confirmed**: merge into `.qaia/reports/<US-ID>/manifest.json` under a
  new `trafficReplay` section — same discipline `flaky-detect` already applies (shared output
  contract, `../../OUTPUT-CONTRACT.md`, rule 2 — merge, never clobber):
  merge only this section, append to `producers[]`, extend `artifacts[]`, never touch
  `design`/`execution`/`gate`/`status`. **If no US-ID applies** (traffic spans routes from
  several stories, or none in particular), skip the manifest merge and say so explicitly —
  forcing an arbitrary US-ID onto cross-cutting traffic would be a fabricated association, not
  a real one; the findings still stand as a self-contained artifact.
- Never a `gate` verdict — this skill only surfaces evidence (contract rule 3, same as every
  producer in this plugin).

## Not a test book — complementary to `testbook-generate` / `automate`

This skill's output describes **what actually happened** on the routes the HAR captured — an
evidentiary record, not a coverage claim. It does not replace `qaia-core:generate`
(derives *what should be tested* from a user story's acceptance criteria) or
`qaia-playwright:automate` (turns a test book into runnable tests). A route that never appears
in the HAR is not "covered" by this skill in any sense — silence in the traffic is not evidence
of anything, and the output says so rather than implying completeness. Where a derived
condition looks worth locking in as a real regression check, the human's next step is to hand
it to `automate` or write it as a Playwright request test by hand — this skill neither
generates nor runs that test itself.

## Steps

1. Get the HAR path from the user; confirm it is a user-provided export, not something the
   skill is being asked to go capture.
2. Parse `log.entries[]`; apply Masking (blocking) before deriving anything else.
3. Apply the Method above; produce the findings table + JSON.
4. Ask whether to merge into a US-ID's manifest; do so per Output's rule, or skip and say why.
5. Present the findings. No test file is generated or run by this skill.

## Guardrails

- **Never capture live traffic.** No proxy, no MITM, no browser automation to generate new
  requests, no network call of any kind from this skill. Input is a HAR the user already has —
  full stop. Refuse and explain if asked to "watch the app and capture what happens."
- **Mask before any write, blocking, no exceptions, no ledger** (the ingestion masking rule,
  extended to HTTP traffic) — see Masking above. Applies to headers, query values, and bodies in both requests
  and responses; the response-shape fingerprint (keys/types only) is an independent second
  safety layer on top of the regex/heuristic list.
- **Never generalize beyond the sample.** No path-template inference, no averaging across
  differing statuses, no claim that an absent header means "insecure in general" — the report
  says what this capture showed, never what is structurally guaranteed true of the app.
- **No auto-replay, no auto-generated test execution.** A condition derived here is a candidate
  for a human (or a separate, explicit `automate` run) to turn into an actual test — this skill
  never sends a request, never runs anything against the app that produced the HAR or any other
  target.
- **Known masking limitations, stated not hidden**:
  - Name detection is heuristic and **key-based only** (`name`/`assignee`/`author`/`owner`/
    `contact` JSON keys) — a personal name sitting in an unrelated free-text field (a notes or
    description string) is **not** guaranteed to be caught.
  - Card-number detection (Luhn checksum + length) can rarely admit a non-card 13-19-digit
    number that happens to pass Luhn, or miss a real one stored with unusual separators.
  - National ID / SSN formats are locale-specific and **not** covered by a generic pattern in
    v1 — if the traffic is known to carry them, redact the HAR before handing it to this skill.
  - These gaps are reported in the findings output itself, not just here — never imply full PII
    coverage.
- **HAR only, nothing ever contacted.** Mirrors `security-surface`/`perf-check`'s
  "self-hosted/authorized targets only" rule in spirit; this skill goes one step further and contacts
  no target at all, live or otherwise.
