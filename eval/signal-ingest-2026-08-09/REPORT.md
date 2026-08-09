# `signal-ingest` exercised for the first time

**Date** 2026-08-09 · Source `sources/access-log-extract.csv`, sha256 (LF-normalised)
`b1a67b375849d7693478e07433a147be…` · period **2026-07-01 → 2026-07-30** · 14 aggregated rows

`signal-ingest` was created earlier today and was the **only skill in the repository with no
execution trace at all**. This run exercises it against the open questions the RealWorld work left
behind this morning.

**The log is synthetic**, shaped to be realistic. That is stated first because it is the single
most important limit here: nothing below is evidence about RealWorld. It is evidence about
**whether the skill behaves as specified** when given a plausible artefact.

## Step 1 — freeze the source

Copied into `sources/`, sha256 recorded, period recorded. An evidence file whose provenance cannot
be re-read is an opinion.

## Step 2 — redact before writing anything

| kind | distinct values | placeholder |
|---|---:|---|
| client IP | 11 | `[REDACTED:ip]` |
| user email | 11 | `[REDACTED:email]` |

Masked before any derived artefact was produced. **No mapping from original value to placeholder is
kept anywhere** — a redaction ledger re-leaks exactly what the masking removed.

## Step 3 — the facts, with no interpretation

94 391 requests on `/articles` over 30 days. **Maximum `limit` observed: 1000.**

| operation | status | count |
|---|---|---:|
| `GET /articles` | 200 | 93 440 |
| `GET /articles` | **422** | **8** |
| `POST /articles` | 201 | 902 |
| `POST /articles` | 422 | 41 |
| `GET /articles/feed` | 200 | 4 210 |
| `POST /users` | 201 | 331 |
| `POST /users` | **422** | **58** |
| `POST /users` | **400** | **12** |

**A defect in the first aggregation, recorded rather than corrected silently:** the first pass
merged `GET` and `POST` on `/articles`, reporting `201: 902` under a path as if the method did not
matter. It does — the 422s split 8 (GET, all with `limit` ≥ 500) against 41 (POST, body validation).
Two completely different findings had been collapsed into one number.

## Step 4 — evidence attached to the open questions, which stay open

### Q1 — is `limit` bounded above?

The specification declares `minimum: 1` and **no maximum** (`eval/openapi-realworld-2026-08-09/`).

```
# open: Q1 — is `limit` bounded above?
#   evidence (signal-ingest, 2026-07-01..2026-07-30, access-log-extract.csv sha256 b1a67b37…):
#     values observed: 20, 50, 100, 500, 1000 across 94 391 requests.
#     every request with limit >= 500 answered 422 (8 occurrences); every request with
#     limit <= 100 answered 200.
#     Observed only. A bound appears to sit between 100 and 500 — the specification states none,
#     and this does not establish one.
```

**This is the most useful thing the skill produced**, and it still does not answer the question. It
narrows where a human should look.

### Q2 — does a duplicate registration return 409 or 400?

This morning's finding: the spec declares **409** on `POST /users`; the conformance suite mocks that
exact case as **400**; no test exercises 409.

```
# open: Q2 — 409 or 400 on a duplicate registration?
#   evidence (signal-ingest, same source):
#     POST /users over 30 days — 201: 331, 422: 58, 400: 12, 409: 0.
#     The specification declares 201, 409, 422 and never 400. Twelve 400s were observed on an
#     operation whose contract does not describe that status.
#     ZERO 409 observed. This does NOT show the 409 is unreachable: the case may not have
#     occurred, the client may prevent it, or the export may be filtered.
```

## Step 5 — what the evidence did NOT reach

**This list is the real output.** Open questions no signal informed:

- **Q3** — does `308` preserve the method as `307` does? *No redirect traffic in the export.*
- **Q4** — what happens to the body after a `POST → GET` conversion? *Not observable from status
  codes.*
- **Q5** — is the default `function` fixture scope displayed or omitted? *Unrelated domain.*

Three of five questions are untouched. A skill that reported only the two it informed would read
as far more useful than it is.

## Did the skill obey its own refusals?

| Refusal | Held? |
|---|---|
| Never close an open question | **yes** — both remain `# open` |
| Never connect to anything | **yes** — a file was read; no request left the machine |
| Never invent questions from data | **yes** — the 422/`limit` correlation is attached to Q1, not raised as a new finding |
| Treat absence as absence, never as a negative | **yes** — "ZERO 409 observed" carries its three alternative explanations |
| Mask personal data before writing | **yes** — 22 values, no mapping kept |
| Never generate tests directly | **yes** |

## Honest verdict on this validation

**What it proves:** the skill's steps are executable, its refusals are followed, and it produces
something a human can act on — narrowing Q1 from "unknown" to "between 100 and 500, observed".

**What it does not prove:** that it works on a real export. Real access logs are messy, partial,
and inconsistently formatted; a synthetic file shaped by the person testing the skill is the
friendliest possible input. **The first real log will find defects this run cannot.**

**And a defect it did find, in the operator rather than the skill:** merging methods on a path.
The skill says nothing about aggregating by method, and it should — filed as a gap.
