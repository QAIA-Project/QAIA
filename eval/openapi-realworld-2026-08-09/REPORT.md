# `openapi-ingest` on a second real specification — RealWorld API

**Date** 2026-08-09 · **Source** `realworld-apps/realworld` `specs/api/openapi.yml` at commit `98f29fb3` ·
**sha256** (LF-normalised) `227d6983874850d35a883f4486b455cedbb272a0c103008595873c94ae1600ac` ·
24 935 bytes, 922 lines

Second application of `qaia-core:openapi-ingest`, after the Swagger Petstore
(`eval/openapi-ingest-2026-08-08/`). No request was sent to any RealWorld server: the skill reads a
document, and the host is not ours.

## Inventory

| | |
|---|---:|
| paths | 12 |
| operations | 19 |
| schemas | 11 |
| declared response codes (distinct) | 8 — `200 201 204 401 403 404 409 422` |
| operations requiring a credential | 12 / 19 |

`$ref` resolution was necessary and not optional: every request body is a `$ref` into
`components/requestBodies`, wrapping a second `$ref` into `components/schemas`, itself wrapping the
real fields in an envelope (`{"user": {...}}`). A first pass that stopped at the envelope reported
**0 refusal paths**, then **6** — both wrong. The skill's step 3 ("a condition that depends on an
unresolved reference is not a condition") is the whole reason the third pass is right.

## Contradiction pass — the result is zero, and that is the finding

| Class | Petstore (2026-08-08) | RealWorld |
|---|---|---|
| 1. required parameter carrying a `default` | present | **none** |
| 2. same field constrained in one place, not another | present | **none** |
| 3. `security` declared with no failure code declared | present — 9 ops, no 401 anywhere | **none** — all 12 secured operations declare `401` |
| 4. constraint in prose, absent from schema | present | **none** |

**All four classes fired on Petstore. None fires here.** A pass that finds something everywhere
finds nothing at all; this one discriminates, and that is worth more than a long list would have
been.

Two candidate findings were raised by the extraction and **killed on inspection before reaching
this report**:

- **"9 secured operations declare no `403`."** False. `403` is declared on exactly
  `PUT /articles/{slug}`, `DELETE /articles/{slug}` and `DELETE /articles/{slug}/comments/{id}` —
  precisely the three operations with an ownership rule. The other nine have no forbidden-but-
  authenticated state to describe. Its absence is correct design, not an omission.
- **"10 descriptions carry a constraint the schema does not enforce."** False. The regex matched the
  word *required* inside "Auth is required". Cross-checking every operation's prose against its
  `security` block gives **0 disagreements** in 19 operations.

## What the specification does not constrain

This is the substantive observation, and it is about the material available for test design rather
than about a defect:

- **16 of the 22 required text fields carry no constraint whatsoever** — no `maxLength`, `minLength`,
  `pattern`, `enum` or `format`. Username, title, description, body, bio, image are all unbounded
  strings as far as the specification is concerned.
- **`format: email` is declared nowhere.** `email` is required on `LoginUser` and `NewUser` and typed
  only as `string`.
- **No `enum` anywhere in the document**, so equivalence partitioning derives nothing from it.
- **`limit` declares `minimum: 1` and no `maximum`** (`default: 20`). A conforming client may request
  `limit=2000000000`. Per the skill's own rule this is an **open question for a human**, not a defect:
  the specification does not say the server accepts it.

Consequence for a derived test book: almost every boundary condition on a text field would have to
be invented. The skill forbids that — an unstated bound becomes `# open: Qn`, never a test.

## Conditions mechanically derivable

| Source | Conditions |
|---|---:|
| declared response codes (one per code per operation) | 70 |
| absent / invalid credential (12 secured operations × 2) | 24 |
| `required` body fields, omitted in turn | 11 |
| schema bounds (`offset ≥ 0`, `limit ≥ 1`) | 2 |
| `enum` partitions | 0 |
| **total** | **107** |

Against 19 operations — and every one of them derived from the document, none from the
implementation. Per the skill's standing rule, each is of the form *"the spec promises X"*, never
*"the API does X"*. Confirming or refuting them is `contract-probe`'s job.

## Honest limits

- **No test book was generated.** This run exercised `openapi-ingest` only — ingestion, `$ref`
  resolution, derivation and the contradiction pass. `istqb-design` and `testbook-generate` were not
  run, so nothing here has been through prioritisation or scoring.
- **The 107 conditions are counted, not written.** The count is what the specification affords; it is
  not a claim that 107 scenarios exist.
- **`format: password` and `format: date-time` were treated as constraints** for the purposes of the
  "unconstrained" tally, which is generous: neither bounds a value in a way a test can exercise.
