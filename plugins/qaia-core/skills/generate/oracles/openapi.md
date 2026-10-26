# Project oracle — OpenAPI / Swagger / JSON Schema extraction (issue #16)

The bounded procedure for turning a **single user-designated** API contract into grounded test
conditions with their correct expected results. Read only that file; never fetch external
`$ref`s or the live API. Every derived case cites its origin (`@oracle:openapi`,
`# oracle: openapi <operationId> <detail>`). If the contract is silent on a point, it stays
`[open]`; if it contradicts the US, raise a question (the US wins on business intent).

## Step 0 — spec-health check (mandatory, before extraction) — issue #25

Measured on 3 real specs ([`eval/baselines/connectors-real-data.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/baselines/connectors-real-data.md)): 2 of 3 degenerate to
**≈0 grounded negatives**, and a naive reader that skips `$ref` resolution silently loses every
required-field negative. Both failures are silent — the user sees "oracle applied" with nothing
to show for it. Run this check first, every time:

1. **Resolve internal `$ref`s before reading any schema.** `#/components/schemas/<Name>` (OAS
   3.x) and `#/definitions/<Name>` (Swagger 2.0) are followed **in the local document only** —
   never an external file or URL (an unresolvable `$ref` is reported as unresolved, never
   fetched). Reading `required`/`enum`/`minLength`/etc. from an *unresolved* `$ref` node reads as
   "no constraints" and silently drops every field-level negative derived from that schema —
   this is the single most common way the oracle under-produces without any signal.
2. **Count, across the whole document**: mutating operations (`POST`/`PUT`/`PATCH`/`DELETE`),
   documented `4xx`/`5xx` responses, and any declared `security`/`securitySchemes`.
3. **Fire the under-documented-spec warning when EITHER holds** (verified against 3 real specs —
   a read-only, zero-error-path directory API and a mutating, zero-error-path product API both
   need the warning; a well-documented mutating API with real error/auth coverage must not):
   - **documented 4xx/5xx count = 0 across the entire spec** (a spec with genuinely no error path
     anywhere — even on GETs with a path parameter that can 404 — is under-documented regardless
     of whether it mutates data), **or**
   - **mutating operations > 0 AND no security declared anywhere** (a spec that lets you write
     data with no documented auth is either wide open or, far more likely, under-documented).

   When either fires, **say so explicitly to the user before presenting the (near-empty) oracle
   output**: name the operation count, the mutating-operation count, the 4xx/5xx count, and the
   auth-declaration count, and state plainly that most endpoints will stay `[open]` because the
   contract itself does not document enough to ground them — never let a near-zero result
   silently read as "oracle passed, API covered."
4. Only after 1-3 does step-by-step extraction (below) begin.

## Per operation (`paths.<path>.<method>`)

| Spec element | Derive | Expected `Then` (from the spec) | Kind |
|---|---|---|---|
| `responses` keys | one condition per documented status trigger | that status (`200/201/204/400/401/403/404/409/422/429`) | positive for 2xx, `[req-neg]` for 4xx/5xx |
| `security` present | request without / with wrong-scope credentials | `401` (missing), `403` (scope mismatch) | `[req-neg]` |
| `requestBody.content.<mt>.schema.required[]` | one condition per required field omitted | the documented rejection status (usually `400`/`422`) | `[req-neg]` |
| `parameters[].required: true` | required query/path/header param omitted | documented rejection status | `[req-neg]` |
| `deprecated: true` | note it; do not build new positive coverage around a deprecated op | — | flag |

## Per schema property (request or response body)

**Resolve `$ref` first (step 0.1) — a schema node that is still `{"$ref": "..."}` at this point
has no `required`/`enum`/`minLength`/etc. to read; treating it as constraint-free is the bug,
not a valid "no constraints declared" reading.**

| Constraint | Derive | Notes |
|---|---|---|
| `enum: [...]` | valid = each listed value; invalid = one out-of-enum value → rejection | closed set — an out-of-enum value is a grounded negative |
| `minLength` / `maxLength` | value at, ±1 around each bound | boundary value analysis, cited |
| `minimum` / `maximum` (+ `exclusiveMinimum`/`Maximum`) | at bound, ±1 | respect inclusive/exclusive exactly as declared |
| `multipleOf` | a conforming and a non-conforming value | |
| `pattern` | one matching, one non-matching string | |
| `format: date`/`date-time` | **chain to the ISO 8601 built-in oracle** | project oracle gives the field+status; ISO 8601 gives the value edge cases |
| `format: email` | **chain to the RFC 5322 built-in oracle** | same composition |
| `format: uuid`/`uri`/`ipv4` | one valid, one malformed | |
| `nullable: false` (required) | explicit `null` → rejection | distinct from "omitted" |
| `additionalProperties: false` | an unexpected extra field → rejection (if the API validates it) | mark `@low-confidence` if the spec does not state the behavior |

## Composition & bounds

- **One condition per documented fact**, not per imagined one. The spec is an oracle of *what is
  documented*; undocumented behavior is a coverage gap to flag, not to fabricate.
- **Chaining**: a `format` field pulls the matching built-in oracle's value set, so an API date
  field inherits the leap-year / impossible-date / timezone cases with the endpoint's own status
  as the expected outcome.
- **Provenance both ways**: the condition cites the operation and the constraint; the synthesis
  records "negative cases X, Y grounded in the OpenAPI contract, not fabricated".
- **Security**: never read secrets, server URLs, or example credentials from the spec into any
  `.qaia/` file — extract structure (operations, statuses, constraints) only.
- **Version tolerance**: OpenAPI 3.x (`requestBody`, `components.schemas`) and Swagger 2.0
  (`parameters` with `in: body`, `definitions`) are both accepted; JSON Schema alone yields the
  property-constraint rows without the operation rows.
