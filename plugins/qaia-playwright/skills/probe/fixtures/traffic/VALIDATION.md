# traffic-replay validation — real run, synthetic data (2026-07-25)

Honest record of validating `../../references/02-replaying-captured-traffic.md` against a purpose-built fixture, per issue #39's own
acceptance criterion: a demo HAR, **entirely synthetic**, never real production traffic.

## What was built

- `demo-traffic.har` — a hand-built HAR 1.2 file (not exported from a real browser session,
  since no real target exists for this fictional app) for **"TaskFlow"**, a fictional
  task-tracker API. 8 entries across 7 routes: login, list tasks, list tasks filtered by query,
  create a task, read one task (captured twice, to exercise the multi-sample path), delete a
  missing task (404), and a checkout call. Deliberately seeded with one instance of every
  masking category the skill claims to handle:
  - an `Authorization: Bearer <jwt>` request header (entries 2–8)
  - a `Set-Cookie`/`Cookie` session cookie (entries 1–3)
  - a query-string token (`?status=done&token=qk_live_8271abf`, entry 3)
  - an email address, in both a request body and a response body (entry 1)
  - a password field in a login request body (entry 1)
  - a phone number in a request body (entry 4)
  - a full name under an `assignee` key, in both a request and a response body (entry 4)
  - a JWT-shaped `token` field inside a **response body** (entry 1) — distinct from the
    `Authorization` header case, to exercise the body-level secret/token key rule
  - a Luhn-valid 16-digit card number in a request body (entry 8, the standard `4111...1111`
    test Visa number)
- `build-findings.py` — the reference implementation of `SKILL.md`'s Method and Masking
  sections: parses the HAR, applies every masking rule from the table, groups entries into
  signatures, and writes `output/traffic-findings.json` + `.md`. This is the same D42 tier-1
  pattern the rest of QAIA uses for determinism (a script generated and run in-session, never
  shipped as plugin runtime code) — kept here as a transparent, reproducible record of how this
  evidence was produced, not as something the plugin auto-executes.

## What was actually run

```
python build-findings.py demo-traffic.har output
```

Real output, not summarized secondhand — `PII masked (type -> count):
{'auth-header': 7, 'card': 1, 'cookie': 3, 'email': 2, 'name': 2, 'phone': 1,
'query-token': 1, 'secret': 2}`.

## Ground truth vs. what the skill derived

| Signature | Expected | Derived (`output/traffic-findings.json`) |
|---|---|---|
| `POST /api/login` | 1 sample, 200 | ✅ 1 sample, 200 (1/1) |
| `GET /api/tasks` (no query) | 1 sample, 200 | ✅ 1 sample, 200 (1/1) |
| `GET /api/tasks?status&token` | 1 sample, 200 — **different signature** from the row above (different query-param-name-set) | ✅ separate condition `@QAIA-TRAFFIC-003`, never merged with `-002` |
| `POST /api/tasks` | 1 sample, 201 | ✅ 1 sample, 201 (1/1) |
| `GET /api/tasks/1` (captured twice) | **2 samples of the same signature** — the multi-sample path | ✅ `@QAIA-TRAFFIC-005`, `sampleCount: 2`, `singleSample: false`, both timings kept (`40, 250`) — **not** averaged into one number |
| `GET /api/tasks/1` vs `DELETE /api/tasks/999` | different paths → never templated into `/api/tasks/{id}` | ✅ two separate conditions, `999` never abstracted away |
| `DELETE /api/tasks/999` | 1 sample, 404 | ✅ 1 sample, 404 (1/1) |
| `POST /api/checkout` | 1 sample, 200 | ✅ 1 sample, 200 (1/1) |

**8 entries → 7 conditions** (the one genuine repeat collapses to one condition with
`sampleCount: 2`; every other route stays a `singleSample: true` condition, reported honestly
as "documents what happened this one time," never generalized).

## PII/secret masking — verified, not just claimed

Every value seeded above has a corresponding masking-category hit in `piiMasked`:

| Seeded value | Category | Count contribution |
|---|---|---|
| `Authorization: Bearer …` (entries 2–8, 7 requests) | `auth-header` | 7 |
| `Set-Cookie` (entry 1) + `Cookie` (entries 2, 3) | `cookie` | 3 |
| `token=qk_live_8271abf` query param | `query-token` | 1 |
| `alice.johnson@example.com` (request body entry 1 + response body entry 1) | `email` | 2 |
| `password: Sunshine!42` (request body entry 1) + `token: eyJ…` (response body entry 1) | `secret` | 2 |
| `phone: +33 6 12 34 56 78` (request body entry 4) | `phone` | 1 |
| `assignee: Bob Dupont` (request body entry 4 + response body entry 4) | `name` | 2 |
| `cardNumber: 4111111111111111` (request body entry 8) | `card` | 1 |

**Leak check.** Grepped every seeded raw value — the email, the JWT and its two component
substrings, the raw cookie value, the query token, the name, the card number, and the login
password — against every file under `output/` (`traffic-findings.json`,
`traffic-findings.md`, `manifest-before.json`, `manifest-after.json`). **Zero matches.** The
`responseShape`/`requestShape` fields carry keys and types only (e.g. `"email": "string"`,
never the address itself) — an independent second layer on top of the regex/heuristic masking,
so even a value the masking rules missed could not reach those fields regardless.

## Manifest merge (contract D39, rule 2)

`output/manifest-before.json` is a plausible manifest as `run-report`/`automate` would have
already written it for a fictional `US-DEMO-TRAFFIC` story (`gate` here is an illustrative
placeholder, not really scored by `qaia-score`, since this fixture is not a real QAIA user
story). `output/manifest-after.json` is the same file with **only** `trafficReplay` added,
`producers[]` appended, and `artifacts[]` extended — `execution`, `gate`, and `status` are
unchanged. `trafficReplay` itself carries no PII (same keys/types-only shapes as the standalone
findings, confirmed by the same grep above).

**Corrected 2026-07-31 (skill-eval wave A, pattern P1 — found by the new CI job, not by the
wave itself).** Both files failed [`eval/tools/validate_manifest.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/validate_manifest.py) with 20 errors: a partial
`design` block (`scenarios` only) on a fixture that has no upstream user story, and
`kind: "trafficReplay"` which no enum and no contract line ever declared, although the skill
has emitted it since D88. The `design` block was **removed rather than completed** — inventing
coverage and confidence numbers to satisfy a validator is the fabrication D38 forbids — and the
kind was added to `ARTIFACT_KIND_ENUM` and to `../../../OUTPUT-CONTRACT.md`, because the kind was
real and the contract was silent. The same defect existed in `flaky-detect`'s fixture; a CI
step now validates every `plugins/**/manifest*.json` so a shipped example can no longer
contradict the contract it demonstrates.

## Honest limitations surfaced by this exercise

- **Name detection is genuinely weak.** It only catches a name sitting under a matched JSON
  key (`assignee`, `name`, `author`, `owner`, `contact`). A name embedded in a free-text field
  (e.g. a `notes: "assigned to Bob Dupont"` string) would **not** be caught — this fixture does
  not exercise that case, and `SKILL.md` says so rather than implying broader NLP-based
  detection exists.
- **This fixture's only repeated signature returned the same status (200) both times.** The
  Method section's "split honestly across differing statuses" behavior (e.g. `200 in 3/4, 500
  in 1/4`) is implemented in `build-findings.py` (`observedStatuses` is always a list, built
  from real per-sample counts) but is **not exercised by any row in this fixture** — flagged
  here rather than silently claimed as tested.
- **National ID / SSN patterns are not covered.** Deliberately out of scope for v1, named as a
  gap in `SKILL.md`'s Guardrails rather than silently absent.
- **The Luhn-based card check is a heuristic, not a guarantee**: a non-card 13–19-digit number
  that happens to pass Luhn would be masked unnecessarily (false positive, safe direction); a
  real card number split across a body with unusual separators the parser does not normalize
  could be missed (false negative, the actually risky direction) — not exercised by this
  fixture, stated as a known gap.
- **Grouping by exact path (no template inference) is a deliberate, and sometimes noisy,
  choice.** A HAR with many numeric-ID routes (`/api/tasks/1`, `/api/tasks/2`, …) will produce
  one `singleSample: true` condition per ID rather than one grouped condition — correct per
  D38 (never infer a template the HAR does not assert), but a human reviewing a large HAR
  should expect a longer, more repetitive findings table than a schema-aware tool would
  produce. This is called out in `SKILL.md`'s Method section, not discovered only here.

## Result

The skill's Method and Masking rules, applied to real (executed, not hand-waved) parsing of a
seeded HAR, correctly derived 7 conditions from 8 entries, correctly distinguished a genuine
2-sample repeat from 6 single-sample routes, correctly kept `/api/tasks/1` and
`/api/tasks/999` as separate conditions instead of inferring a shared template, and — the
acceptance criterion that matters most for this issue — **masked every seeded credential/PII
value with zero leakage into any output artifact**, verified by direct grep, not by trusting
the masking code's own claim about itself.
