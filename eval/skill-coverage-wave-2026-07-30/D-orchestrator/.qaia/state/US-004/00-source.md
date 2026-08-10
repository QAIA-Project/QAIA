---
stepsCompleted: [00-ingest]
lastStep: 00-ingest
lastSaved: 2026-07-30
---

# 00-source — US-004

- **source type**: local file (gold set)
- **source location**: `eval/gold-set/US-004-expense-approval.md`
- **capture date**: 2026-07-30
- **outputRoot**: `eval/skill-coverage-wave-2026-07-30/D-orchestrator/.qaia/` (shared contract rule 9)
- **redaction**: scanned per us-ingest step 3 — 0 direct personal/sensitive items found (synthetic clean-room content, no names, no IDs, no contacts). Masked count: none.
- **sanitization**: no control / bidi-override characters found.
- **triage gates**: empty → not fired; not-a-testable-requirement → not fired (states, thresholds, refusal rules described); abuse/illegality → not fired.
- **scale/decomposition gate**: single story, 8 AC. Under the ~20k token limit; AC count noted as borderline for the "large number of ACs" trigger but kept as one story (one workflow, one state machine).
- **excluded from capture**: the source file's trailing block `## Judge reference — planted ambiguities (do not feed to skills)` was NOT captured. It is evaluation metadata about the fixture, not part of the requirement. Recorded here as an exclusion so it is visible, not silently dropped.

## Captured text (faithful, redacted where applicable)

# US-004 — Expense report approval workflow

## User story

**As an** employee,
**I want** to submit an expense report and have it approved through the right chain,
**so that** I get reimbursed correctly and the company keeps an auditable trail.

## Acceptance criteria

1. A report moves through states: `draft` → `submitted` → (`approved` | `rejected` | `changes-requested`). A `changes-requested` report returns to `draft` for editing and can be re-submitted.
2. A report under €500 total needs one approval (the employee's direct manager). €500–€5000 needs manager **then** finance. Above €5000 needs manager, finance, **then** a director.
3. An approver cannot approve their own report; if the submitter is themselves a manager, their report skips straight to the next level up.
4. Each line item must have a category, an amount, and a date within the last 90 days; a line outside 90 days is blocked at submission with an explanatory message.
5. Receipts are mandatory for any single line ≥ €25; submission is refused if a ≥ €25 line has no attached receipt.
6. Currency other than EUR is converted at the rate of the expense date; the converted total drives the approval threshold of AC2.
7. A rejected report is terminal and cannot be edited or re-submitted; a new report must be created.
8. Every state transition records who, when, and (for rejections and changes-requested) a mandatory comment of at least 10 characters.

## dependencies:

Referenced-but-undefined terms / out-of-slice items (us-ingest guardrail "sibling-story dependencies"):

- `direct manager` / `finance` / `director` — the role and org-hierarchy model is referenced, never defined here. No sibling story ID given in the source.
- FX **rate source** (AC6) — "the rate of the expense date" presumes a rate provider defined elsewhere.
- `category` vocabulary (AC4) — the allowed category list is not in this slice.
- Audit-trail storage/retention (AC8) — the record's shape and retention are not defined here.

The source makes no explicit INVEST "Independent" claim; the dependencies above show it is not fully independent in practice.

## Attachments / referenced artifacts

None referenced. Nothing "not analyzed".

## Validation record

- ⚠ VALIDATION (step 4, US-ID): no human available in this session. `simulated: US-004 (slug from source title)` per shared contract README rule 3.
- ⚠ VALIDATION (step 6, right document / right version): `simulated: accepted` — single-file local fixture, no versioning ambiguity.
