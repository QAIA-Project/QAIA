# Coverage matrix — US-004

AC → condition → scenario ID → priority → rationale → confidence. Rationale copied from
`04-priorities.md` (deliverable rule, rubric dim. 9 — rationale must reach the delivered book,
not stay only in internal state).

| AC | Condition | Scenario ID | Priority | Rationale | Confidence |
|---|---|---|---|---|---|
| AC1,AC2,AC8 | journey | @QAIA-US-004-001 | P1 | End-to-end demonstration, excluded from atomicity/negative accounting (@smoke). | normal |
| AC1 | AC1-C1 | @QAIA-US-004-002 | P2 | Core transition, foundational; simple logic. | normal |
| AC1 | AC1-C2 | @QAIA-US-004-003 | P2 | Re-entrant loop adds state complexity. | normal |
| AC1 | AC1-C3 | @QAIA-US-004-004 | P2 | Edit-then-resubmit exercises the loop's exit path. | normal |
| AC1 | AC1-C4 [req-neg] | @QAIA-US-004-005 | P2 | Guards against double-submission. | normal |
| AC1 | AC1-C5 [req-neg] | @QAIA-US-004-006 | P2 | Guards against editing in-flight reports. | normal |
| AC1,AC7 | AC1-C6 [req-neg] | @QAIA-US-004-007 | P1 | Q3-flagged; wrong behavior breaks AC7's terminality guarantee. | **low (Q3)** |
| AC2 | AC2-C1 | @QAIA-US-004-008 | P1 | Financial-control boundary. | normal |
| AC2 | AC2-C2 | @QAIA-US-004-009 | P1 | Q1-flagged; exact-€500 planted-ambiguity boundary. | **low (Q1)** |
| AC2 | AC2-C3 | @QAIA-US-004-010 | P1 | Q1-flagged; exact-€5000 boundary. | **low (Q1)** |
| AC2 | AC2-C4 | @QAIA-US-004-011 | P1 | Full 3-level chain, highest-stakes band. | normal |
| AC2 | AC2-C5 [req-neg] | @QAIA-US-004-012 | P1 | Out-of-order approval breaks chain integrity. | normal |
| AC3 | AC3-C1 [req-neg] | @QAIA-US-004-013 | P1 | Classic internal-control defect class. | normal |
| AC3 | AC3-C2 | @QAIA-US-004-014 | P1 | Q2-flagged escalation semantics; approval-bypass risk if wrong. | **low (Q2)** |
| AC3 | AC3-C3 | @QAIA-US-004-015 | P1 | Q2-flagged, larger-band variant. | **low (Q2)** |
| AC3 | AC3-C4 | @QAIA-US-004-016 | P1 | Q8-flagged generalization beyond the named example. | **low (Q8)** |
| AC4 | AC4-C1 [req-neg] | @QAIA-US-004-017 | P3 | Basic input-completeness validation. | normal |
| AC4 | AC4-C2 | @QAIA-US-004-018 | P2 | Q5-flagged clock reference; boundary logic. | **low (Q5)** |
| AC4 | AC4-C3 [req-neg] | @QAIA-US-004-019 | P2 | Boundary logic, moderate complexity. | normal |
| AC5 | AC5-C1 | @QAIA-US-004-020 | P2 | Boundary just below the receipt threshold. | normal |
| AC5 | AC5-C2 [req-neg] | @QAIA-US-004-021 | P1 | Financial-control boundary at the exact threshold. | normal |
| AC5 | AC5-C3 | @QAIA-US-004-022 | P3 | Straightforward positive case. | normal |
| AC5,AC6 | AC5-C4 [req-neg] | @QAIA-US-004-023 | P1 | Q6-flagged cross-AC basis; real bypass risk if wrong. | **low (Q6)** |
| AC6 | AC6-C1 | @QAIA-US-004-024 | P1 | Conversion feeds AC2's threshold — high blast radius. | normal |
| AC6 | AC6-C2 [req-neg] | @QAIA-US-004-025 | P1 | Q4-flagged (rate source); undefined external dependency. | **low (Q4)** |
| AC6 | AC6-C3 | @QAIA-US-004-026 | P1 | Q4-flagged (fallback); silently wrong total mis-routes approval. | **low (Q4)** |
| AC2,AC3,AC6 | AC6-C4 | @QAIA-US-004-027 | P1 | Q7-flagged triple intersection; highest combined complexity. | **low (Q7)** |
| AC7 | AC7-C1 [req-neg] | @QAIA-US-004-028 | P2 | Terminal-state guard, compliance-relevant. | normal |
| AC7 | AC7-C2 [req-neg] | @QAIA-US-004-029 | P2 | Same class as AC7-C1. | normal |
| AC8 | AC8-C1 [req-neg] | @QAIA-US-004-030 | P2 | Compliance evidence requirement. | normal |
| AC8 | AC8-C2 [req-neg] | @QAIA-US-004-031 | P2 | Same class as AC8-C1. | normal |
| AC8 | AC8-C3 | @QAIA-US-004-032 | P2 | Exact boundary at the 10-character minimum. | normal |
| AC8 | AC8-C4 | @QAIA-US-004-033 | P3 | Confirms an absence of a constraint. | normal |
| AC8 | AC8-C5 | @QAIA-US-004-034 | P1 | Audit-trail completeness — the AC8 core promise. | normal |
| (auth) | AC-auth-C1 [req-neg] | @QAIA-US-004-035 | P2 | Standard auth gate. | normal |
| (auth) | AC-auth-C2 [req-neg] | @QAIA-US-004-036 | P2 | Same class as AC-auth-C1. | normal |
| (auth) | AC-auth-C3 [req-neg] | @QAIA-US-004-037 | P1 | IDOR class; sequential IDs raise real exposure. | normal |
| (list) | AC-list-C1 | @QAIA-US-004-038 | P3 | Cosmetic empty state. | normal |

**Coverage**: all 8 AC have ≥ 2 scenarios each; all `[req-neg]` conditions from `03-design.md`
have a covering `@negative` scenario (17/17 — gate satisfied, ADR 0001); every P1/P2 condition
covered; all 4 P3 conditions also covered (full-breadth scope decision, `04-priorities.md`).
Negative ratio: 17/37 = **45.9 %** (reported signal only — since ADR 0001 the ratio is a happy-path-bias indicator, not a gate). 11 scenarios carry `@low-confidence`
(Q1×2, Q2×2, Q4×2, then Q3, Q5, Q6, Q7 and Q8 once each — 2+2+2+5 = 11. Three questions anchor two boundary scenarios, not two
boundary scenarios).

## Gaps (not generated, ceiling rule 3c — explicit, not silently dropped)

- No delete/discard mechanism for a draft — not named in the source.
- No sort/filter/pagination on the "mine"/"inbox" lists — not named or implied.
- No notification mechanism (email/in-app) to submitters/approvers — not named.

## ID continuity

Sequence 001–038 (38 scenarios: 1 journey + 37 condition scenarios), no gaps, no retired IDs
(first generation).
