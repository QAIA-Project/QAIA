---
stepsCompleted: [00-ingest, 01-review, 02-understanding, 03-design, 04-priorities, 05-generate]
lastStep: 05-generate
lastSaved: 2026-08-10
status: waived
---

# Synthèse de revue — US-002 (validation de posologie)

**Ce que vous tenez :** 28 scénarios Gherkin, 4 fichiers, tous les critères d'acceptation
couverts, linter du dépôt passé. **Ce que vous ne tenez pas :** une suite qui prouve que le
système est correct. La différence est l'objet de cette page.

## À lire en premier, dans cet ordre

1. **Les 10 questions ouvertes** (`../../state/US-002/02-understanding.md`) — neuf n'ont **aucun
   défaut appliqué** parce que tout ce qui touche à une dose est en domaine protégé. Sans réponse,
   13 scénarios sur 28 affirment notre lecture et non votre règle.
2. **Les 4 scénarios P1 à confiance nominale** — `009` (dose > max), `014` (âge sous plancher),
   `017` (surcharge sans justification), `022` (justification < 20 caractères). Ce sont les seuls
   scénarios critiques adossés à une règle explicite de la source. Si vous ne relisez que quatre
   choses, relisez celles-là.
3. **La triade indécidable Q4** — `020`. Un médicament dont le maximum réduit de 50 % tombe sous
   le minimum efficace rend toute dose simultanément « sous le minimum » et « au-dessus du
   maximum ». Le cas est atteignable dès que max < 2 × min. Aucune des huit règles ne dit qui
   gagne.

## Par technique

| Technique | Scénarios | Ce qu'elle apporte ici |
|---|---|---|
| Valeurs limites | 13 | Les seuils : min, max, cumul, âge, 20 caractères — chacun testé à la borne et de part et d'autre |
| Table de décision | 5 | AC5 et son exception de rôle, plus l'interaction AC5 × AC6 que seule une table rend visible |
| Partitionnement | 7 | Classes de fiche médicament, de contenu de justification, de restitution |
| Test de domaine | 2 | Le cumul 24 h, qui lie dose et instant — une AVL par variable les manquerait |
| Métamorphique | 2 | AC6, dont la **valeur attendue ne peut pas être énoncée** faute de règle d'arrondi : on vérifie une relation au lieu d'affirmer un chiffre inventé |
| Scénario `@smoke` | 1 | Un seul par US, le parcours saisie → verdict → restitution |

## Ordre de revue par le risque

| Prio | Scénarios | |
|---|---|---|
| **P1** | `002` `008` `009` `010` `011` `014` `017` `020` `021` `022` | 10 — échec = faux laissez-passer |
| **P2** | `004` `005` `007` `012` `013` `015` `016` `018` `019` `023` `028` | 11 |
| **P3** | `001` `003` `006` `024` `025` `026` `027` | 7 |

## Ce qui est mesuré, et d'où le chiffre vient

Tous relevés sur `.qaia/testbooks/US-002/*.feature` :

- **28 scénarios**, 28 identifiants uniques, linter Gherkin du dépôt : passé
- **8 AC sur 8 couverts** — aucun critère orphelin, aucun scénario sans critère
- **5 règles de refus, 5 exercées** — porte ADR 0001 franchie
- **18 / 28 (64 %)** portent `@negative` ou `@boundary` — signal de biais, pas un seuil
- **13 / 28 (46 %)** sont `@low-confidence`, **chacun nommant sa question** — vérifié, aucun orphelin

## Les arbitrages en attente

**Dix questions, toutes `pending-validation`.** Neuf sans défaut (domaine santé), une hypothèse
appliquée (Q10, comptage des 20 caractères).

**Et une réserve qui porte sur la mesure, pas sur le produit :** le point de reprise
`00-source.md`, écrit le 2026-07-25, avait recopié la substance de la section juge séquestrée du
document source. Q1, Q3, Q4 et Q6 y figuraient déjà. **Ces quatre questions ne démontrent donc
rien sur la capacité de QAIA à trouver une ambiguïté** — les réponses étaient sous ses yeux. Q2,
Q5, Q7, Q8, Q9 et Q10 ont été dérivées du seul texte des critères et sont les seules dont la
découverte soit défendable.

## Statut du parcours

`waived` — le testeur était joignable le 2026-08-10 et a délégué l'arbitrage. Aucune étape n'est
`done` ; `status` ne peut pas atteindre `validated` tant qu'une question reste `pending-validation`.
Le cahier est exploitable. Il n'est pas validé.
