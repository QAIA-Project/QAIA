# Cahier de test US-002 — export de revue

> Projection de `.qaia/testbooks/US-002/`. **Aucun contenu n'est régénéré ni inventé** : tout vient des `.feature` et des points de reprise.

**28 scénarios** · export du 2026-08-10 · ordre : P1 d'abord, un échec y produit un faux laissez-passer.

| ID | AC | Cond. | Technique | Prio | Négatif | Confiance | Scénario |
|---|---|---|---|---|---|---|---|
| `@QAIA-US-002-002` | AC1 | C02 | error-guessing | P1 | oui | basse (Q7) | A drug with no reference record cannot be silently accepted |
| `@QAIA-US-002-008` | AC3 | C08 | boundary | P1 |  | basse (Q1) | A dose exactly at the maximum safe dose per intake is accepted |
| `@QAIA-US-002-009` | AC3 | C09 | boundary | P1 | oui | normale | A dose above the maximum safe dose per intake blocks the signature |
| `@QAIA-US-002-010` | AC4 | C10 | boundary | P1 |  | basse (Q1, Q3) | Intakes summing exactly to the cumulative ceiling are accepted |
| `@QAIA-US-002-011` | AC4 | C11 | boundary | P1 | oui | basse (Q3) | Intakes summing above the cumulative ceiling block the signature |
| `@QAIA-US-002-014` | AC5 | C14 | decision-table | P1 | oui | normale | A patient below the age floor is blocked for a non-pediatric prescribe |
| `@QAIA-US-002-017` | AC5 | C17 | decision-table | P1 | oui | normale | A pediatric override without justification is refused |
| `@QAIA-US-002-020` | AC6 | C20 | decision-table | P1 |  | basse (Q4) | A reduced maximum falling below the minimum effective dose does not si |
| `@QAIA-US-002-021` | AC5 | C21 | decision-table | P1 |  | basse (Q5) | The pediatric exception does not convert a renal threshold block into  |
| `@QAIA-US-002-022` | AC7 | C22 | boundary | P1 | oui | normale | An override justified with 19 characters is refused |
| `@QAIA-US-002-004` | AC2 | C04 | boundary | P2 |  | normale | A dose just below the minimum effective dose raises an overridable war |
| `@QAIA-US-002-005` | AC2 | C05 | boundary | P2 |  | normale | A dose exactly at the minimum effective dose raises no warning |
| `@QAIA-US-002-007` | AC3 | C07 | boundary | P2 |  | normale | A dose just below the maximum safe dose per intake is accepted |
| `@QAIA-US-002-012` | AC4 | C12 | domain-analysis | P2 |  | basse (Q3) | Intakes straddling midnight are counted against the same 24 h window |
| `@QAIA-US-002-013` | AC4 | C13 | domain-analysis | P2 | oui | basse (Q8) | Two prescriptions signed concurrently cannot together exceed the ceili |
| `@QAIA-US-002-015` | AC5 | C15 | boundary | P2 |  | normale | A patient exactly at the age floor is accepted |
| `@QAIA-US-002-016` | AC5 | C16 | decision-table | P2 |  | normale | A pediatric specialist gets an overridable warning instead of a block |
| `@QAIA-US-002-018` | AC6 | C18 | metamorphic | P2 |  | normale | A renal-flagged patient never gets a more permissive verdict than an u |
| `@QAIA-US-002-019` | AC6 | C19 | metamorphic | P2 |  | basse (Q6) | Halving an odd threshold does not admit a dose above the reduced ceili |
| `@QAIA-US-002-023` | AC7 | C23 | boundary | P2 |  | normale | An override justified with 20 characters is accepted |
| `@QAIA-US-002-028` | AC2 | C28 | error-guessing | P2 | oui | basse (Q2) | A dose expressed in a unit other than the reference record's is not co |
| `@QAIA-US-002-001` | AC1 | C01 | ep | P3 |  | normale | A drug with a complete reference record can be validated |
| `@QAIA-US-002-003` | AC1 | C03 | error-guessing | P3 |  | basse (Q7) | A reference record missing its age floor does not silently skip the ag |
| `@QAIA-US-002-006` | AC2 | C06 | ep | P3 |  | basse (Q9) | An overridden low-dose warning allows the prescription to be signed |
| `@QAIA-US-002-024` | AC7 | C24 | ep | P3 | oui | basse (Q10) | An override justified with 20 spaces is refused |
| `@QAIA-US-002-025` | AC7 | C25 | ep | P3 |  | normale | An accepted override records identity, timestamp and justification |
| `@QAIA-US-002-026` | AC8 | C26 | use-case | P3 |  | normale | A prescriber sees the verdict in the signing screen without a page rel |
| `@QAIA-US-002-027` | AC8 | C27 | ep | P3 |  | normale | A prescription breaking two rules at once reports both rule identifier |
