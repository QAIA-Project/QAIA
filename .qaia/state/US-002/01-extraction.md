---
stepsCompleted: [00-ingest, 01-review]
lastStep: 01-review
lastSaved: 2026-08-10
status: waived
---

# 01-extraction — US-002

> **Statut : `waived`, pas `confirmed`.** Le testeur était joignable le 2026-08-10 et a
> explicitement délégué l'arbitrage (« fait tout toi-même je te l'autorise »). C'est une décision
> humaine enregistrée, et elle autorise la suite du parcours — mais elle **ne satisfait pas** le
> contrôle que la porte impose, qui est « un humain a confronté cette extraction à la source ».
> Personne ne l'a fait. Waiver : approbateur *Moretti Cédric*, date *2026-08-10*, raison
> *délégation explicite pour exercer le parcours et les skills installées*, portée *US-002
> uniquement*.

## Story

Présente dans la source, citée — **non reconstruite**.

> **As a** prescribing physician,
> **I want** the system to validate the dosage of a prescription against the drug's safety rules
> before I sign it,
> **so that** dosage errors are caught before they reach the pharmacy.

## Critères d'acceptation

Numérotation reprise de la source. **Ces numéros sont l'ancrage de la traçabilité aval et ne
seront plus renumérotés.**

| ID | Critère (paraphrase fidèle) | Nature |
|---|---|---|
| AC1 | Chaque médicament porte une fiche de référence : dose minimale efficace, dose maximale sûre par prise, dose cumulée maximale sur 24 h, âge plancher (âge patient minimal en années) | donnée de référence |
| AC2 | Dose **strictement inférieure** à la dose minimale efficace → *avertissement*, surchargeable par le prescripteur avec motif documenté | avertissement |
| AC3 | Dose **au-dessus** de la dose maximale sûre par prise → *erreur bloquante*, la prescription ne peut pas être signée | blocage |
| AC4 | La dose cumulée sur 24 h (toutes prises du même médicament pour ce patient) ne doit pas dépasser la dose cumulée maximale ; le dépassement est bloquant | blocage |
| AC5 | Âge patient sous l'âge plancher → blocage, **sauf** si le prescripteur porte le rôle « pediatric specialist », auquel cas cela devient un avertissement surchargeable avec justification obligatoire | blocage + exception de rôle |
| AC6 | Pour un patient portant un drapeau d'insuffisance rénale, **tous les seuils maximaux** sont réduits de 50 % avant validation | modificateur transversal |
| AC7 | Chaque surcharge (contournement d'avertissement) enregistre l'identité du prescripteur, l'horodatage et un texte de justification d'**au moins 20 caractères** dans la piste d'audit | traçabilité |
| AC8 | Les résultats de validation (pass / warning / blocked, avec identifiants de règle) sont rendus dans l'écran de signature **sans rechargement de page** | restitution |

## Règles métier hors liste des AC

Aucune. Tout le contenu normatif de la source est porté par les huit critères.

## Artefacts référencés non analysés

Aucun : ni maquette, ni pièce jointe, ni lien externe.

## Contenu présent mais non classable

Aucun. Rien de la source n'est écarté.

## Ce que la source ne contient pas — constaté, non inventé

- **Aucune priorité ni criticité.** La priorisation de l'étape 04 sera une décision, pas une lecture.
- **Aucun budget de latence** alors qu'AC8 promet « sans rechargement ».
- **Aucun critère de non-régression ni de performance.**
- **Aucune définition des données dont dépendent AC1, AC5, AC6 et AC7** — fiche médicament, modèle
  de rôle, drapeau rénal, piste d'audit. Cette story **n'est pas indépendante** : quatre critères
  sur huit s'appuient sur des données possédées ailleurs. Aucun identifiant de story sœur n'est
  nommé dans la source.

## Porte « non-spec »

**Ne tire pas.** Exigence testable, huit critères vérifiables décrivant une capacité réelle.
