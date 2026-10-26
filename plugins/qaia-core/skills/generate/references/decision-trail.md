# istqb-design — decision trail

Read this only if you need to know **where a rule in `SKILL.md` came from** — which project
decision or issue introduced it, and what evidence backed it. Nothing here is needed to *apply*
the skill: `SKILL.md` states every rule and its reason on its own. This file exists so the
traceability is not lost when the body drops internal codes.

Sources: `https://github.com/QAIA-Project/QAIA/blob/main/docs/DECISIONS.md`, `docs/adr/`, and the project issue tracker.

| Rule in `SKILL.md` | Project reference | What it recorded |
|---|---|---|
| Scope: black-box only, no structure-based/white-box technique | D110 (closes #54) | Named the exclusion explicitly after an external CTAL-TTA persona review found it undocumented; a structure-based technique would require reading the target's implementation, which the architecture forbids. |
| Scope: exploratory / session-based testing excluded | D111 (closes #55) | Same discipline, symmetric end of the scripted↔exploratory spectrum. A future "charter mode" was noted as a possible extension, deliberately not implemented. |
| The technique palette itself (Foundation + Test Analyst) | D24 | Original choice of syllabus scope, each technique choice justified in the book. |
| Palette extended with Domain Testing, Metamorphic, CT-AI techniques, explicit state model, `@crud` tag | D95 (closes #48) | Real review of every remaining ISTQB syllabus; also the origin of the "name what was excluded rather than silently omit it" discipline. |
| Palette regrouped by the CTAL-TA v4.0 chapter 3 taxonomy; "Domain Testing" and "Scenario-Based Testing" naming | D109 (closes #50) | Primary syllabus PDF read directly. Also found that equivalence partitioning, BVA and error guessing are CTFL prerequisites, not part of v4.0's own chapter 3 scheme. Presentation-only change, no derivation logic touched. |
| Step 3, required-negative conditions | ADR 0001 (`https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0001-negative-coverage-gate.md`) | Replaced a 40 % negative-ratio gate with a refusal-path coverage gate: a ratio measures proportion, not protection, is fragile to scenario splitting, and pressures fabrication near the floor. |
| Step 3c and its honest-recall ceiling | D38 | Systematic coverage expansion, validated on held-out cases (~93 % precision). The ceiling — config-driven and undescribed interactions are not hallucinated — is part of the same decision. |
| Metamorphic testing instead of a fabricated precise value | #46 | The defect this closed: a scenario asserting an exact figure the source never states. |
| Explicit state × event table before deriving transitions | #43 (surfaced by the expense-demo run, D68/D79) | A state machine over-generalized from AC prose. Same run produced the `[assumption]` vs `[open]` distinction: the "undeclared transition = forbidden" convention silently answered a business-policy question that should have stayed `[open]`. |
| "Never confidently assert an unspecified delete/inverse mechanism"; sibling-collection roll-ups | #24 (gap harness) | Three independent runs on the same hard case each confidently invented the same plausible-but-wrong deletion mechanism, and each missed every roll-up of a child entity's sub-collections. |
| Step 3d, decompose composite rules before deriving | #45 | Measured in [`eval/baselines/rag-recall-gain.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/baselines/rag-recall-gain.md): a rule bundling 7 tier sub-facts yielded conditions for only the 2 boundary-shaped ones. |
| Mobile = browser device emulation, native out of scope | D100 | Web-first architectural choice, retro-documented after an audit found it cited under a wrong decision number in five files. |
