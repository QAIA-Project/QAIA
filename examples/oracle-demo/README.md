# Oracle demo — standards as test-case generators

Demonstrates `qaia-core:oracle-generate` (issue #16, founder's idea): when a US touches a standardized domain, an **oracle** supplies grounded test cases *and* their correct expected results — instead of guessing.

Here the US only said "validate the card number". The **Luhn** oracle (ISO/IEC 7812) supplied:
- valid test PANs (accepted),
- checksum-failing numbers (rejected),
- wrong-length-for-network cases,
- malformed inputs,
- a Luhn-valid-but-unknown-issuer edge case (left `@low-confidence`, cites open question).

See [`card-validation.feature`](card-validation.feature). Every oracle-derived scenario is tagged `@oracle:luhn` with a `# oracle:` citation — provenance is explicit, and the case is never presented as a requirement of the US itself.

## Why this matters

- **Grounded, not guessed**: the expected `Then` comes from the standard. The oracle values are **verified by computation** (the valid PANs pass Luhn, the invalid ones fail — checked, not asserted), which also closes the earlier "literal values not verified" finding.
- **Negative-path coverage without fabrication** (ADR 0001): the oracle raises the refusal-path coverage with cases that are real, not padding.
- **Human still arbitrates**: the oracle *proposes*; if the US contradicts the standard, the US wins and the discrepancy is surfaced as a finding.

The oracle library is encoded (no network): Luhn, ISO 8601 dates, HTTP status semantics, RFC 5322 email, ISO 4217 currency, ISO 3166 country, IBAN mod-97 — see `plugins/qaia-core/skills/generate/oracles/library.md`.

## Project oracle — OpenAPI (issue #16, project-oracle half)

A project can designate ONE API contract as its oracle. [`booking-api.openapi.yaml`](booking-api.openapi.yaml)
is a small OpenAPI 3 excerpt; [`openapi-oracle.feature`](openapi-oracle.feature) is what
`oracle-generate` derives from it — grounded, cited conditions with the **documented** expected
status:

- documented `responses` → expected status per trigger (`201/400/401/409/422`);
- `security` → unauthenticated → `401`;
- `requestBody.required[]` → one missing-field negative per field → `400`;
- `enum` → an out-of-enum value → `400`; `maxLength` → a +1 boundary → `400`;
- `format: date-time` **chains into the ISO 8601 built-in oracle** (impossible date → `400`).

Rules stay strict: only the designated file is read (no live API, no external `$ref`), every case
is tagged `@oracle:openapi` with a `# oracle:` citation, an **undocumented** error path stays
`[open]` (never invented), and the US wins if the contract contradicts it. The extraction mapping
lives in `plugins/qaia-core/skills/generate/oracles/openapi.md`.
