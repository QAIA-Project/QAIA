---
stepsCompleted: []
lastStep: 01-review (pending-validation)
lastSaved: 2026-07-31
status: unconfirmed
---

# 01-extraction — US-002 (status: **unconfirmed**, per us-review step 3)

> This file is deliberately NOT marked confirmed. `us-review` SKILL.md step 3: "In a
> non-interactive context with no user available, do NOT mark this step done — write the
> extraction with status `unconfirmed`, leave `01-review` as `pending-validation` in
> `journey.md`, and stop". No human was available in this evaluation session.

## Story

As a prescribing physician, I want the system to validate the dosage of a prescription against the
drug's safety rules before I sign it, so that dosage errors are caught before they reach the
pharmacy. (Present verbatim in the source — no `[reconstructed]` needed.)

## Acceptance criteria (stable numbering, never renumber after validation)

- **AC1** — drug reference record: min effective dose, max safe dose per intake, max cumulative
  dose per 24 h, age floor (years).
- **AC2** — dosage strictly below min effective dose → *warning*, overridable with documented reason.
- **AC3** — dosage above max safe dose per intake → *blocking error*, cannot be signed.
- **AC4** — cumulative dose over 24 h (all intakes, same drug, same patient) must not exceed max
  cumulative dose; exceeding = blocking.
- **AC5** — patient age below age floor → blocked, EXCEPT physician with role "pediatric
  specialist" → overridable warning with mandatory justification.
- **AC6** — renal-insufficiency flag → all *maximum* thresholds reduced by 50 % before validation.
- **AC7** — every override records physician identity, timestamp, justification ≥ 20 characters,
  in the audit trail.
- **AC8** — validation result (pass / warning / blocked + rule identifiers) returned in the
  signing screen without page reload.

## Business rules / constraints found outside the AC list

None: the source carries no separate rules section. All constraints are inside AC1-AC8.

## Referenced artifacts not analyzed

None referenced (no mockup, attachment or link).

## Present in the source but not classifiable as requirement

- Blockquote header: "Gold set item. Original synthetic content (clean-room), MIT-licensed.
  Domain: health, prescribing module. Rich in boundary values..." — provenance metadata.
- Section "Judge reference — planted ambiguities (do not feed to skills)" — evaluation-harness
  meta-content, kept visible here (never dropped) but excluded from the requirement set; see
  `00-source.md` untrusted-input finding.

## Diff mentality — what I did NOT find

- No inclusive/exclusive definition for any threshold: AC2 says "strictly below", AC3 says
  "above", AC4 says "exceed" — three different wordings, none defining the boundary at equality.
- No statement whether AC6's 50 % reduction applies to the *minimum* effective dose (AC6 says
  "all maximum thresholds" — so literally no, but AC2's interaction is unstated).
- No definition of the 24 h window in AC4 (rolling vs calendar day).
- No rounding rule for decimal dosages.
- No definition of the rule-identifier format of AC8.
- No non-functional criterion (latency of the AC8 round-trip), no error-message wording.
- No owner/source for the drug reference record (AC1) — CRUD is out of slice.

(These are recorded as *not found*, not resolved: resolving is `need-understanding`'s job, with
the user. They were derived from the AC text alone — the source's judge key was not consulted.)

## ⚠ VALIDATION — step 3

**pending-validation**. No human available. Per us-review step 3 the journey **stops here**; the
extraction is `unconfirmed` and step 4 (checkpoint "confirmed structure", `01-review = done`) was
deliberately NOT performed.
