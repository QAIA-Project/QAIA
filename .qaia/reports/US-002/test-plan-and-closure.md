---
stepsCompleted: [00-ingest, 01-review, 02-understanding, 03-design, 04-priorities, 05-generate, 06-plan-closure]
lastStep: 06-plan-closure
lastSaved: 2026-08-10
status: waived
---

# US-002 — plan de test et rapport de clôture

> **Règle appliquée sans exception : rien ici n'est écrit qui ne soit dérivable d'un artefact.**
> Chaque section nomme sa source. Là où l'artefact n'existe pas, la section le dit — « pas
> d'analyse de risque disponible » est une phrase utile ; un risque inventé ne l'est pas.

---

# Partie 1 — Plan de test

## Périmètre

**Source : `01-extraction.md`.** Huit critères d'acceptation, AC1→AC8, couvrant la validation
d'une posologie avant signature : fiche de référence, seuil bas surchargeable, seuil haut
bloquant, cumul 24 h, âge plancher avec exception de rôle, modificateur rénal, piste d'audit,
restitution sans rechargement.

**Hors périmètre, et la source le dit elle-même** : la fiche médicament, le modèle de rôle
« pediatric specialist », l'enregistrement du drapeau rénal et le stockage de la piste d'audit
sont référencés sans être définis. **Aucune story sœur n'est nommée dans la source** — ces quatre
dépendances n'ont pas de propriétaire identifié dans ce périmètre.

## Approche de test

**Source : `03-design.md`.** Six techniques, chacune justifiée par la forme de l'AC :

| Technique | Nombre de scénarios | Pourquoi elle |
|---|---|---|
| Valeurs limites | 13 | Cinq seuils numériques distincts |
| Table de décision | 5 | AC5 croise deux conditions vers trois actions |
| Partitionnement | 7 | Classes de fiche, de justification, de restitution |
| Test de domaine | 2 | Le cumul 24 h lie dose et instant |
| Métamorphique | 2 | AC6 n'a **pas** de valeur attendue énonçable |
| Scénario `@smoke` | 1 | Un seul par US |

**Boîte noire exclusivement**, par conception : aucune technique structurelle, aucune lecture de
l'implémentation. Test exploratoire exclu symétriquement.

## Critères d'entrée

**Source : `journey.md`.** L'ingestion est faite ; les portes vide / non-spec / abus / échelle
n'ont pas tiré ; aucune donnée personnelle n'a été trouvée.

**Non satisfait :** aucune validation humaine n'a eu lieu. Les critères d'entrée d'un plan qui se
respecte incluraient « extraction confirmée par un humain » — elle ne l'est pas.

## Critères de sortie proposés

**Source : `04-priorities.md` + ADR 0001.** Aucun critère de sortie n'est écrit dans la source ;
ce qui suit est **proposé**, pas lu :

1. Les 10 scénarios P1 exécutés, verdict enregistré.
2. Les 5 règles capables de refuser exercées — porte ADR 0001, aujourd'hui franchie au niveau du
   cahier, jamais à l'exécution.
3. **Les 9 questions `[open]` arbitrées par le propriétaire du produit.** Sans cela, 13 scénarios
   sur 28 affirment notre lecture. Ce critère est le seul qui ne puisse pas être remplacé par du
   travail de test.

## Analyse de risque

**Source : `04-priorities.md`.** Les priorités sont ordonnées par **mode de défaillance**, pas par
produit probabilité × impact — et le plan le dit plutôt que d'habiller un jugement de sécurité en
arithmétique. Le faux laissez-passer (dose dangereuse acceptée) prime sur le faux blocage
(visible, corrigeable, sans conséquence patient).

Répartition : **10 P1, 11 P2, 7 P3**.

## Environnement, données, outillage

**Données : `.qaia/testdata/US-002/dataset.json`** — 5 médicaments, 5 patients, 3 prescripteurs,
3 lignes d'historique de prise, 11 cas chiffrés. Deux réserves écrites dans le fichier :
l'unité de dose n'est licenciée par aucun AC (Q2), et l'historique présume une fenêtre glissante
(Q3), donc le jeu n'est valide que pour une des deux lectures.

**Environnement : aucun.** Aucune application cible n'existe pour cette US. C'est le fait le plus
structurant de ce plan et il doit être en tête : **rien de ce qui suit n'a été exécuté.**

---

# Partie 2 — Rapport de clôture

## Ce qui a été produit

**Source : `coverage-matrix.md`, relevé sur les fichiers émis.**

| | |
|---|---|
| Scénarios | **28**, identifiants uniques, linter Gherkin du dépôt passé |
| Couverture des AC | **8 sur 8** — aucun critère orphelin, aucun scénario sans critère |
| Chemins de refus | **5 règles, 5 exercées** (ADR 0001) |
| Signal négatif/limite | 18/28, soit 64 % — rapporté, jamais un seuil |
| Confiance | **13/28 `@low-confidence`**, chacun nommant sa question |

## Ce qui a été exécuté

**Rien.** Aucun scénario n'a été joué contre une application. Le cahier est un artefact de
conception, pas un résultat de test. Toute lecture de ce rapport qui conclurait à une qualité du
produit serait fausse.

## Ce qui reste ouvert à la livraison

**Source : `journey.md`, section « dette nommée ».**

| # | Arbitrage | État |
|---|---|---|
| 1 | Identifiant `US-002` | `simulated` (2026-07-25) |
| 2 | Exactitude du document et de sa version | `simulated` (2026-07-25) |
| 3 | Fidélité de l'extraction | `waived` (2026-08-10) |
| 4 | Dix questions, neuf sans défaut | `waived` |
| 5 | Priorités proposées | `waived` |
| 6 | Cahier non relu par un humain | `waived` |

**Neuf questions `[open]` sans défaut appliqué**, parce que l'US est intégralement en domaine
protégé (santé). Une seule hypothèse appliquée (Q10, comptage des 20 caractères).

## Verdict

**Source : `manifest.json`, bloc `gate`.** **CONCERNS**, `blocksRelease: true`.

Note structurelle **86/100** (programme, indépendant) ; rubrique **19/20** — produite par le même
contexte que le cahier, donc **la règle 3 n'est pas satisfaite sur cette seconde note**, et l'écart
entre les deux est le constat, pas un arrondi.

## La réserve qui prime sur tout le reste

Le point de reprise `00-source.md` du 2026-07-25 avait recopié la substance de la section juge
séquestrée du document source. **Q1, Q3, Q4 et Q6 y figuraient avant que la chasse aux ambiguïtés
ne commence.** Ce parcours démontre la mécanique de la chaîne ; il ne mesure pas la capacité à
trouver une ambiguïté. Un manager qui signerait ce rapport doit savoir que c'est le cas.
