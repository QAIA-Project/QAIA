---
stepsCompleted: [00-ingest, 01-review, 02-understanding, 03-design, 04-priorities]
lastStep: 04-priorities
lastSaved: 2026-08-10
status: waived
---

# 04-priorities — US-002 : priorisation par le risque

**La source ne porte aucune priorité.** Ce qui suit est donc une **proposition**, pas une lecture
— et dans le parcours normal c'est le testeur qui arbitre. Ici l'arbitrage a été délégué
(waiver du 2026-08-10) : les priorités ci-dessous sont appliquées mais restent
`pending-validation`.

## Le principe qui ordonne tout le reste

Sur une validation de posologie, les deux modes de défaillance ne sont pas symétriques :

- **Faux blocage** — une dose licite refusée. Gênant, **visible immédiatement** par le
  prescripteur, contournable, sans conséquence patient.
- **Faux laissez-passer** — une dose dangereuse classée *pass*, ou un blocage converti en
  avertissement surchargeable. **Invisible**, et la conséquence est le patient.

Toute condition dont l'échec produit un faux laissez-passer est donc **P1**, même quand sa
probabilité est faible. C'est l'impact qui commande ici, pas le produit probabilité × impact —
et le dire est plus honnête que d'habiller un jugement de sécurité en arithmétique.

## Priorités

| Prio | Conditions | Raison |
|---|---|---|
| **P1** | C08, C09, C10, C11, C14, C17, C20, C21, C22 | Chacune, si elle échoue, produit un **faux laissez-passer** : une dose au-dessus du seuil acceptée, un cumul dépassé signé, un blocage d'âge contourné sans justification, ou un verdict indécidable tranché en silence du côté permissif |
| **P1** | C02 | Médicament sans fiche : si le défaut d'implémentation est « laisser passer quand on ne sait pas », **aucune** des autres règles ne s'applique. C'est la condition qui peut annuler les sept autres |
| **P2** | C04, C05, C07, C12, C13, C15, C16, C18, C19, C23, C28 | Défauts réels mais dont l'échec produit majoritairement un faux blocage, ou dont l'exploitation demande un enchaînement (concurrence, minuit, unités) |
| **P3** | C01, C03, C06, C24, C25, C26, C27 | Chemin nominal, traçabilité, restitution — vérifient que le système fait ce qu'il annonce, sans exposition patient directe en cas d'échec |

**Répartition : 10 P1, 11 P2, 7 P3.**

## Ce que la priorisation ne résout pas

**Six** des dix conditions P1 dépendent d'une question `[open]` non arbitrée — C02 (Q7), C08 (Q1),
C10 (Q1, Q3), C11 (Q3), C20 (Q4), C21 (Q5). Relevé sur le cahier émis, `@P1` croisé
`@low-confidence`. *(Cette ligne annonçait « neuf des dix » : un chiffre écrit avant génération et
jamais confronté au cahier. La règle 4bis du contrat partagé existe pour ça — la mesure remplace
l'estimation, et la trace de l'erreur reste.)*

**Les prioriser ne les rend pas décidables** : elles seront générées, exécutables, et marquées
`@low-confidence` avec leur question nommée. Une suite qui passerait au vert sur ces six-là ne
prouverait que la cohérence du système avec une supposition — la nôtre. Les quatre autres P1
(C09, C14, C17, C22) sont, elles, adossées à une règle explicite de la source : ce sont les seuls
scénarios critiques qui prouvent quelque chose aujourd'hui.

C'est le résultat le plus important de cette priorisation, et il va contre le confort : **la
partie la plus critique de cette US est celle qu'on sait le moins tester**, parce que le
propriétaire du produit n'a pas encore dit quelle est la règle.
