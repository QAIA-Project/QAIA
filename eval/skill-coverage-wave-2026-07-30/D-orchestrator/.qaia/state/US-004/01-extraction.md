---
stepsCompleted: []
lastStep: 01-review
lastSaved: 2026-07-30
status: unconfirmed
---

# 01-extraction — US-004 (status: **unconfirmed**, `pending-validation`)

Written per `us-review` steps 1-2. Step 3 (⚠ VALIDATION) is **not** satisfied: no human in session,
and us-review step 3 explicitly forbids marking the step done via a simulated acceptance.

## Story

> **As an** employee, **I want** to submit an expense report and have it approved through the right
> chain, **so that** I get reimbursed correctly and the company keeps an auditable trail.

Quoted verbatim. Not `[reconstructed]`.

## Acceptance criteria (stable numbering — never renumber after validation)

| ID | Criterion |
|---|---|
| AC1 | State machine: `draft` → `submitted` → (`approved` \| `rejected` \| `changes-requested`); `changes-requested` returns to `draft` and can be re-submitted. |
| AC2 | Approval chain by total: < €500 → manager only; €500–€5000 → manager then finance; > €5000 → manager, finance, then director. |
| AC3 | An approver cannot approve their own report; a manager-submitter's report skips straight to the next level up. |
| AC4 | Each line item requires category, amount, and a date within the last 90 days; a line outside 90 days is blocked at submission with an explanatory message. |
| AC5 | Receipt mandatory for any single line ≥ €25; submission refused if such a line has no receipt. |
| AC6 | Non-EUR converted at the rate of the expense date; the converted total drives AC2's threshold. |
| AC7 | A `rejected` report is terminal: not editable, not re-submittable; a new report must be created. |
| AC8 | Every state transition records who + when; rejections and changes-requested also require a comment ≥ 10 characters. |

## Business rules / constraints found outside the AC list

None — the source carries no prose outside the story and the numbered AC list.

## Referenced artifacts not analyzed

None referenced.

## Present in the source but not classifiable

None (the fixture's trailing "Judge reference" block was excluded at ingestion and recorded there).

## Diff mentality — what was NOT found

- No non-functional requirements (no latency, volume, retention, concurrency).
- No definition of the role model (`direct manager`, `finance`, `director`) or how the chain is
  resolved for an employee with no manager.
- No allowed `category` vocabulary (AC4).
- No FX rate provider, and no rule for a date with no published rate (AC6).
- No statement of boundary inclusivity for €500 / €5000 (AC2) or for €25 (AC5 says "≥", AC2 does not say).
- No statement of whether a `changes-requested` report can be rejected directly from `draft` (AC1 × AC7).
- No error/refusal message content, only "an explanatory message" (AC4).
- No AC covers what happens when an approver is absent/unavailable.

The not-a-spec gate does **not** fire: this is a real, testable (if under-specified) requirement.

## ⚠ VALIDATION (step 3) — NOT satisfied

`pending-validation`. Required human action: confirm or correct this extraction (missing AC, wrong
split, misread rule). Nothing downstream (`need-understanding`, `istqb-design`, `prioritize`,
`testbook-generate`) may run against an unconfirmed extraction.
