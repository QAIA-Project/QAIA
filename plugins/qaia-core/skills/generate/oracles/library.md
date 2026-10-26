# Oracle library — encoded standards (no network)

Canonical test cases and expected results per standard. All values below are public, standard, synthetic test data (never real credentials or PANs tied to real accounts).

## Luhn (payment card number validation) — ISO/IEC 7812

The check digit satisfies the Luhn mod-10 algorithm.

**Valid test PANs (Luhn-valid, industry-standard test numbers):**
- `4111 1111 1111 1111` (Visa, 16) · `4012 8888 8888 1881` (Visa) · `5555 5555 5555 4444` (Mastercard, 16) · `3782 822463 10005` (Amex, 15) · `6011 1111 1111 1117` (Discover)

**Invalid (Luhn-fails):** `4111 1111 1111 1112`, `1234 5678 9012 3456`, `0000 0000 0000 0001`

**Boundary/negative conditions to generate:** empty, non-digit chars, too short (15 for a 16-net), too long (17), all-zeros, valid-Luhn-but-unknown-IIN. Expected `Then`: accept only Luhn-valid AND length-valid-for-network; otherwise reject with a validation error.

## ISO 8601 (dates & times)

**Edge cases to generate:** `2024-02-29` (leap, valid) vs `2023-02-29` (invalid) vs `2100-02-29` (century non-leap, invalid) · month 30/31 boundaries (`2023-04-31` invalid) · `2023-01-01T00:00:00Z` vs `+02:00` offset (timezone) · week date `2023-W01-1` · midnight `24:00` handling · ordinal `2023-366` (non-leap invalid). Expected `Then`: reject impossible dates; preserve/normalize timezone explicitly (this is where the "which clock?" ambiguity of `need-understanding` is anchored).

## HTTP status semantics (RFC 9110)

Correct expected status per condition — use as the `Then` oracle for API scenarios:
- unauthenticated → `401` · authenticated but not allowed → `403` · resource not found OR not visible (privacy) → `404` · malformed body/params → `400` · conflict / already exists / race lost → `409` · validation rule violated → `422` · rate limited → `429`.

## RFC 5322 (email)

**Valid:** `user@example.com`, `first.last@sub.example.co.uk`, `user+tag@example.com`
**Invalid:** `plainaddress`, `@no-local.com`, `user@`, `user@@example.com`, `user@.com`

**"Valid" is not one category, and this is where email oracles go wrong.** A quoted local part
such as `"test"@iana.org` is *syntactically valid* — and rejected by a large share of production
systems, deliberately. Asserting that it must be accepted generates a failing test against a
system that is not wrong. It belongs in a **third bucket**, never in the plain-valid list:

| Bucket | Example | Expected `Then` |
|---|---|---|
| valid | `user@example.com` | accept |
| invalid | `user@.com` | reject with a format error |
| **valid but commonly refused** | `"test"@iana.org` (quoted), `test . test@iana.org` (obsolete syntax) | **`[open]` — ask the product what it does.** Never assert either way. |

Canonical corpus, when more than a handful of cases is needed: **`dominicsayers/isemail`,
`test/tests.xml`** (BSD-3-Clause) — 163 addresses with an authoritative verdict each, and the
distinction above baked into its categories (`ISEMAIL_ERR` = invalid; `RFC5321`, `DEPREC`, `CFWS`
= valid at *different* titles, not interchangeable). Cite the case id when a scenario uses one.

## ISO 4217 (currency codes)

**Valid:** `EUR`, `USD`, `JPY` (0 minor units), `BHD` (3 minor units). **Invalid:** `EU`, `EURO`, `US$`. Minor-unit rule drives rounding: JPY has no decimals, BHD has 3 — generate rounding boundary cases accordingly.

**`XXX` is a trap, and it is registered.** ISO 4217 assigns `XXX` to *"transactions where no currency is involved"* — so a validator checking membership of the standard must **accept** it, while a payment flow almost certainly must **reject** it. The two answers are both right and they are not the same question. Emit `[open]`: *does this field mean "a registered code" or "a currency you can charge in"?* Never classify `XXX` as simply invalid — that is the error this line used to carry.

## ISO 3166 (country codes)

**Valid alpha-2:** `FR`, `US`, `JP`. **Valid alpha-3:** `FRA`, `USA`. **Invalid:** `UK` (it's `GB`), `XX`, `F`. 

## IBAN (ISO 13616, mod-97)

**Valid example:** `FR14 2004 1010 0505 0001 3M02 606` (mod-97 == 1). **Invalid:** wrong check digits, wrong length for country, lowercase, spaces-only. Expected `Then`: accept only mod-97-valid AND correct per-country length.

---

**Usage note:** these are *oracles*, not requirements. A generated scenario using them is tagged `@oracle:<standard>` and cites the reference. If a US contradicts a standard (e.g. "accept any 16-digit number"), the US wins but the discrepancy is surfaced as a finding — the oracle never silently overrides the requirement.
