---
stepsCompleted: [00-ingest, 01-review, 02-understanding, 03-design, 04-priorities, 05-generate]
lastStep: 05-generate
lastSaved: 2026-08-10
status: waived
---

# journey — US-002

> **Aucune étape n'est `done`, et c'est délibéré.** Le testeur était joignable le 2026-08-10 et a
> explicitement délégué l'arbitrage. Une délégation est une décision humaine enregistrée — elle
> autorise le parcours — mais elle ne satisfait pas le contrôle que chaque porte impose, qui est
> qu'un humain ait *regardé*. Statut `waived` : approbateur **Moretti Cédric**, date
> **2026-08-10**, raison *délégation explicite pour exercer le parcours et les skills installées*,
> portée *US-002 uniquement*. `status` ne peut pas atteindre `validated` tant qu'il reste une
> étape `pending-validation`.

| Étape | Statut | Notes |
|---|---|---|
| 00-ingest | pending-validation | Source : `eval/gold-set/US-002-dosage-validation.md`. Aucune porte n'a tiré. Redaction : scannée, aucune PII. **Marqué `done` le 2026-07-25 alors que deux validations étaient `simulated`** (identifiant US-ID, exactitude du document) — corrigé le 2026-08-10 : l'arbitrage du 2026-07-31 (contrat partagé, règle 3) interdit `done` sur un pas portant une validation simulée. L'artefact précédait la règle de six jours. |
| 01-review | pending-validation | 8 AC numérotés AC1→AC8, ancrage définitif. Story citée, non reconstruite. Aucune règle hors liste. Story **non indépendante** : AC1, AC5, AC6, AC7 s'appuient sur des données possédées ailleurs, aucune story sœur nommée. Waiver. |
| 02-understanding | pending-validation | 10 questions Q1→Q10. **Neuf `[open]` sans défaut** (domaine protégé santé), une `[assumption]` (Q10). Passes croisée et triple exécutées : la triade AC2 × AC6 × AC3 est indécidable (Q4). Base de connaissance **absente** — mode QAIA Solo, consigné. Waiver. |
| 03-design | pending-validation | 28 conditions C01→C28. Techniques : AVL, table de décision, partition, domaine, métamorphique, scénario. Métamorphique choisi sur AC6 **parce que la valeur attendue ne peut pas être énoncée** (arrondi absent). Porte ADR 0001 : 5 règles de refus, 5 exercées. Waiver. |
| 04-priorities | pending-validation | 10 P1, 11 P2, 7 P3. Ordonnées par mode de défaillance (faux laissez-passer avant faux blocage), pas par produit probabilité × impact — dit tel quel. **La source ne porte aucune priorité** : c'est une proposition. Waiver. |
| 05-generate | pending-validation | 28 scénarios, 4 fichiers, 28 identifiants uniques, linter Gherkin du dépôt passé. 8 AC sur 8 couverts. 18/28 `@negative` ou `@boundary`. 13/28 `@low-confidence`, chacun nommant sa question. Waiver. |

## Dette nommée à la clôture

**Six arbitrages simulés ou délégués**, aucun satisfait :

1. `00-ingest` — identifiant `US-002` (`simulated`, 2026-07-25)
2. `00-ingest` — exactitude du document et de sa version (`simulated`, 2026-07-25)
3. `01-review` — fidélité de l'extraction à la source (`waived`, 2026-08-10)
4. `02-understanding` — dix questions, neuf sans défaut (`waived`, 2026-08-10)
5. `04-priorities` — priorités proposées, non arbitrées (`waived`, 2026-08-10)
6. `05-generate` — cahier émis, non relu par un humain (`waived`, 2026-08-10)

## Réserve sur la valeur de mesure de ce parcours

`00-source.md` avait recopié la substance de la section juge séquestrée du document source. Q1,
Q3, Q4 et Q6 y figuraient. Ce parcours **exerce les skills** — c'était sa raison d'être — mais il
**ne mesure pas** la capacité à trouver une ambiguïté. Une mesure qui vaudrait quelque chose
demande une US dont personne n'a écrit les réponses à côté.

Étape suivante possible : **`report`** (manifeste normalisé), **`testbook-export`** (`.feature` +
XLSX/Markdown), ou **`testbook-score`** du plugin `qaia-score` — qui notera ce cahier sans l'avoir
produit.
