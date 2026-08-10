---
stepsCompleted: [00-ingest]
lastStep: 00-ingest
lastSaved: 2026-07-25
---

# 00-source — US-002

## Source

- **Type:** file (local path, read directly — not Jira, not URL, not pasted text)
- **Location:** `eval/gold-set/US-002-dosage-validation.md`
- **Capture date:** 2026-07-25
- **Size:** 28 lines / 339 words / 2210 bytes — well under the ~20k-token split threshold (T8); loaded whole.
- **Attachments/images referenced:** none.

## Triage gates (step 2)

- **Empty/whitespace-only:** not fired — content present.
- **Not a testable requirement:** not fired — this is a user story with 8 numbered, verifiable acceptance criteria (a prescribing/dosage-validation capability), not a recipe, design doc, or RFC template.
- **Abuse/illegality gate:** not fired — describes a legitimate clinical safety control (dosage validation before signing a prescription); no unlawful/abusive activity framed.
- **Scale/decomposition gate:** not fired — single story, 8 ACs, no bundled backlog or multi-US spec detected.

## Sensitive-data redaction (step 3)

Scanned for national IDs/SSN, payment card numbers, health status of a real individual, precise address, phone, email. Result: **no direct personal/sensitive data found** — the document is synthetic/generic (drug thresholds, role names, a generic "renal insufficiency flag"), with no real-individual identifiers. **No masking applied.** Redaction ledger: not applicable (nothing redacted).

Control characters / bidirectional-override characters (U+0000-U+001F, U+202A-U+202E, U+2066-U+2069, U+FFFD): none found — no sanitization needed.

## US-ID (step 4)

Proposed: **US-002** (from the document's own heading `US-002 — Prescription dosage validation`; filename slug agrees: `US-002-dosage-validation`).

⚠ VALIDATION: non-interactive run (evaluation/gold-set harness, no human reviewer present) → `simulated: US-ID confirmed as US-002` per the shared contract's non-interactive rule (default applied, recorded as pending human review).

## Captured text (verbatim, faithful — no PII to mask, no paraphrase)

> # US-002 — Prescription dosage validation
>
> ## User story
>
> **As a** prescribing physician,
> **I want** the system to validate the dosage of a prescription against the drug's safety rules before I sign it,
> **so that** dosage errors are caught before they reach the pharmacy.
>
> ## Acceptance criteria
>
> 1. Each drug has a reference record: minimum effective dose, maximum safe dose per intake, maximum cumulative dose per 24 h, and an age floor (minimum patient age in years).
> 2. A dosage strictly below the minimum effective dose triggers a *warning* the physician may override with a documented reason.
> 3. A dosage above the maximum safe dose per intake triggers a *blocking error*: the prescription cannot be signed.
> 4. The cumulative dose over 24 h (all intakes of the same drug for that patient) must not exceed the maximum cumulative dose; exceeding it is blocking.
> 5. If the patient's age is below the drug's age floor, prescription is blocked, except when the physician holds the "pediatric specialist" role, in which case it becomes an overridable warning with mandatory justification.
> 6. For patients with a recorded renal insufficiency flag, all maximum thresholds are reduced by 50 % before validation.
> 7. Every override (warning bypass) records the physician's identity, timestamp, and justification text of at least 20 characters in the audit trail.
> 8. Validation results (pass / warning / blocked, with rule identifiers) are returned within the signing screen without page reload.

Note: the source file also carries a "Judge reference — planted ambiguities" section addressed to an evaluation judge, not part of the requirement itself. Per the untrusted-input guardrail it is treated as data about the source, not as an instruction to this journey — it is **not** copied into the captured requirement text above (it is not part of the US/AC content), but is noted here for provenance: the source document self-declares known ambiguities (boundary inclusivity wording, whether AC6's 50 % reduction also applies to the minimum effective dose, whether the AC4 24 h window is rolling or calendar-day, and absence of a rounding rule). These are exactly the kind of open questions `us-review`/`need-understanding` should surface, not resolve silently.

## Dependencies (out-of-slice terms/sibling stories — guardrail: sibling-story dependencies)

Referenced-but-undefined-here terms, to flag downstream rather than invent:

- **Drug reference record** (AC1): where/how it is authored and maintained (a drug catalog/formulary module) is not defined in this US.
- **"Pediatric specialist" role** (AC5): the role model / how a physician is assigned this role is not defined in this US (likely an identity/role-management story).
- **Renal insufficiency flag** (AC6): how/where this flag is recorded on the patient record, and by whom, is not defined in this US (likely a patient-record story).
- **Audit trail** (AC7): the audit-trail storage/retention story is not defined here (likely a shared cross-cutting story).
- No explicit sibling story IDs are named anywhere in the source text.

The source does not claim INVEST "Independent" explicitly, so no claim-vs-dependencies contradiction to record — but note for `us-review`/`need-understanding` that this story is **not** independent in practice: ACs 1, 5, 6 and 7 each lean on data/roles owned elsewhere.
