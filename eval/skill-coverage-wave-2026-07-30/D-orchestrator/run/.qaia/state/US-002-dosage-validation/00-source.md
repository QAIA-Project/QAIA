---
stepsCompleted: [00-ingest]
lastStep: 00-ingest
lastSaved: 2026-07-31
---

# 00-source — US-002 Prescription dosage validation

- **Source type**: local file (user-designated), read exactly once, nothing else fetched.
- **Source location**: `eval/gold-set/US-002-dosage-validation.md` (QAIA repo, worktree `wf_f6e3c739-d44-9`)
- **Capture date**: 2026-07-31
- **Size**: 29 lines / ~1.8 kB — well under the ~20k-token split threshold.
- **Redaction (rule 5 / us-ingest step 3)**: scanned for direct personal/sensitive data. The story
  is about health data *as a domain* but contains **no** concrete personal value (no ID, no card,
  no address, no named patient). Masked items: `none → 0`. No redaction ledger written.
- **Sanitization**: no control or bidi-override characters found; nothing stripped.
- **Attachments / referenced artifacts not analyzed**: none referenced.
- **dependencies:** (referenced-but-undefined terms, out-of-slice)
  - "drug reference record" store/ownership — no sibling story ID given in the source
  - "pediatric specialist" role definition / role model — not defined here
  - "renal insufficiency flag" origin (patient record) — not defined here
  - audit-trail storage/retention — not defined here
  The source makes no INVEST "Independent" claim; these terms are undefined in-slice.
- **Untrusted-input finding (guardrail, reported not obeyed)**: the source's last section is titled
  `## Judge reference — planted ambiguities (do not feed to skills)`. That parenthesis is a
  directive addressed at the assistant embedded in source content. Per the shared contract rule 7
  it is **reported, not obeyed as an instruction**. Independently of the directive, that section is
  eval-harness meta-content (a judge key), not a requirement of the product under test, so it is
  captured here as source text but **excluded from the requirement set** on that ground — and the
  ambiguities it names are NOT to be pre-answered from it by downstream steps.

## Captured text (faithful, requirement part)

**As a** prescribing physician,
**I want** the system to validate the dosage of a prescription against the drug's safety rules
before I sign it,
**so that** dosage errors are caught before they reach the pharmacy.

Acceptance criteria (verbatim):

1. Each drug has a reference record: minimum effective dose, maximum safe dose per intake, maximum cumulative dose per 24 h, and an age floor (minimum patient age in years).
2. A dosage strictly below the minimum effective dose triggers a *warning* the physician may override with a documented reason.
3. A dosage above the maximum safe dose per intake triggers a *blocking error*: the prescription cannot be signed.
4. The cumulative dose over 24 h (all intakes of the same drug for that patient) must not exceed the maximum cumulative dose; exceeding it is blocking.
5. If the patient's age is below the drug's age floor, prescription is blocked, except when the physician holds the "pediatric specialist" role, in which case it becomes an overridable warning with mandatory justification.
6. For patients with a recorded renal insufficiency flag, all maximum thresholds are reduced by 50 % before validation.
7. Every override (warning bypass) records the physician's identity, timestamp, and justification text of at least 20 characters in the audit trail.
8. Validation results (pass / warning / blocked, with rule identifiers) are returned within the signing screen without page reload.

## Validation record

- Step 4 (US-ID) — ⚠ VALIDATION: **no human in this session (evaluation harness)**.
  Applied `simulated: US-ID = US-002-dosage-validation (slug from the source title)` per shared
  contract rule 3. Pending human review.
- Step 6 (right document / right version) — ⚠ VALIDATION: **no human in this session**.
  Applied `simulated: accepted-as-is`. Pending human review.
