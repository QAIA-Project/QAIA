---
stepsCompleted: [00-ingest, 01-review, 02-understanding, 03-design, 04-priorities, 05-generate]
lastStep: 05-generate
lastSaved: 2026-08-10
status: waived
---

# Matrice de couverture — US-002

**Relevé sur les fichiers émis** (`.qaia/testbooks/US-002/*.feature`, 4 fichiers, linter Gherkin
du dépôt passé) : **28 scénarios, 28 identifiants uniques**.

| AC | Condition | Scénario | Prio | Technique | Confiance |
|---|---|---|---|---|---|
| AC1 | C01 | `@QAIA-US-002-001` | P3 | Partition | normale |
| AC1 | C02 `[req-neg]` | `@QAIA-US-002-002` | P1 | Partition / erreur | **basse (Q7)** |
| AC1 | C03 | `@QAIA-US-002-003` | P3 | Partition / erreur | **basse (Q7)** |
| AC2 | C04 | `@QAIA-US-002-004` | P2 | Valeurs limites | normale |
| AC2 | C05 | `@QAIA-US-002-005` | P2 | Valeurs limites | normale |
| AC2 | C06 | `@QAIA-US-002-006` | P3 | Partition | **basse (Q9)** |
| AC2 | C28 `[req-neg]` | `@QAIA-US-002-028` | P2 | Partition / erreur | **basse (Q2)** |
| AC3 | C07 | `@QAIA-US-002-007` | P2 | Valeurs limites | normale |
| AC3 | C08 | `@QAIA-US-002-008` | P1 | Valeurs limites | **basse (Q1)** |
| AC3 | C09 `[req-neg]` | `@QAIA-US-002-009` | P1 | Valeurs limites | normale |
| AC4 | C10 | `@QAIA-US-002-010` | P1 | Valeurs limites | **basse (Q1, Q3)** |
| AC4 | C11 `[req-neg]` | `@QAIA-US-002-011` | P1 | Valeurs limites | **basse (Q3)** |
| AC4 | C12 | `@QAIA-US-002-012` | P2 | Test de domaine | **basse (Q3)** |
| AC4 | C13 `[req-neg]` | `@QAIA-US-002-013` | P2 | Test de domaine | **basse (Q8)** |
| AC5 | C14 `[req-neg]` | `@QAIA-US-002-014` | P1 | Table de décision | normale |
| AC5 | C15 | `@QAIA-US-002-015` | P2 | Valeurs limites | normale |
| AC5 | C16 | `@QAIA-US-002-016` | P2 | Table de décision | normale |
| AC5 | C17 `[req-neg]` | `@QAIA-US-002-017` | P1 | Table de décision | normale |
| AC5 | C21 | `@QAIA-US-002-021` | P1 | Table de décision | **basse (Q5)** |
| AC6 | C18 | `@QAIA-US-002-018` | P2 | Métamorphique | normale |
| AC6 | C19 | `@QAIA-US-002-019` | P2 | Métamorphique | **basse (Q6)** |
| AC6 | C20 | `@QAIA-US-002-020` | P1 | Table de décision | **basse (Q4)** |
| AC7 | C22 `[req-neg]` | `@QAIA-US-002-022` | P1 | Valeurs limites | normale |
| AC7 | C23 | `@QAIA-US-002-023` | P2 | Valeurs limites | normale `[assumption Q10]` |
| AC7 | C24 `[req-neg]` | `@QAIA-US-002-024` | P3 | Partition | **basse (Q10)** |
| AC7 | C25 | `@QAIA-US-002-025` | P3 | Partition | normale |
| AC8 | C26 | `@QAIA-US-002-026` | P3 | Scénario `@smoke` | normale |
| AC8 | C27 | `@QAIA-US-002-027` | P3 | Partition | normale |

## Couverture des critères d'acceptation

**8 AC sur 8 couverts.** Aucun critère orphelin, aucun scénario sans critère.

| AC1 | AC2 | AC3 | AC4 | AC5 | AC6 | AC7 | AC8 |
|---|---|---|---|---|---|---|---|
| 3 | 4 | 3 | 4 | 5 | 3 | 4 | 2 |

## Porte de couverture des chemins de refus (ADR 0001)

| Règle capable de refuser | Scénario qui l'exerce |
|---|---|
| AC3 — dose > max par prise | `@QAIA-US-002-009` |
| AC4 — cumul 24 h dépassé | `@QAIA-US-002-011` |
| AC5 — âge sous le plancher | `@QAIA-US-002-014` |
| AC5 — surcharge sans justification | `@QAIA-US-002-017` |
| AC7 — justification sous 20 caractères | `@QAIA-US-002-022` |

**Porte franchie : 5 règles de refus, 5 exercées.** C'est ce qui gate — pas le ratio.

## Signal de biais happy-path

**18 scénarios sur 28 (64 %)** portent `@negative` ou `@boundary` — dont 9 `@negative` et 13
`@boundary`. **Rapporté comme signal, jamais comme seuil** (ADR 0001) : un ratio ne se remplit
pas, il se lit.

## Confiance

**13 scénarios sur 28 (46 %) sont marqués `@low-confidence`**, chacun nommant sa question
ouverte. Répartition par question : Q1 (2), Q2 (1), Q3 (3), Q4 (1), Q5 (1), Q6 (1), Q7 (2),
Q8 (1), Q9 (1), Q10 (1).

**Six des dix scénarios P1 sont dans ce lot** — `002`, `008`, `010`, `011`, `020`, `021`. Les
quatre autres (`009`, `014`, `017`, `022`) s'adossent à une règle explicite de la source : ce
sont les seuls scénarios critiques qui prouvent quelque chose en l'état.

Autrement dit : **la majorité de ce qui compte le plus dans cette US ne peut pas encore être
vérifiée** — non par manque de technique, mais parce que le propriétaire du produit n'a pas dit
quelle est la règle.
