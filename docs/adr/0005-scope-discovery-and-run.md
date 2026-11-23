# ADR 0005 — Le périmètre s'étend à Discovery et à Run

- Statut : **REMPLACÉE le 2026-08-08 par [ADR 0007](0007-scope-delivery-and-maintenance.md)**
- Date : 2026-08-08
- Décidé par : le fondateur, arbitrage explicite
- Complète : [ADR 0004](0004-test-level-boundary.md), qui borne les *niveaux* de test et reste valable

> **Cette décision a été annulée le jour même de sa signature.** Une revue d'architecture menée
> sur le dépôt a infirmé son raisonnement : la capacité existante n'est pas prouvée (cinq juges à
> contexte vide, aucune suite ne franchit la porte), et les chiffres qui soutenaient le
> différenciateur « couverture du cycle » étaient faux dans des fichiers livrés. Élargir aurait
> ajouté de la surface non prouvée à de la surface non prouvée.
>
> Le texte est conservé intact : une décision annulée le même jour est un fait du projet, pas une
> erreur à effacer. Voir [ADR 0007](0007-scope-delivery-and-maintenance.md).

## Contexte

La carte de couverture ([`../archive/TEST-COVERAGE-MAP.md`](../archive/TEST-COVERAGE-MAP.md) §3bis) a établi, le
2026-08-08, une phrase que le projet n'avait jamais écrite :

> **QAIA vit entièrement dans Delivery et Maintenance.** Elle commence quand la discovery est
> finie et s'arrête quand le déploiement commence.

Deux constats en découlaient :

- **Discovery** — `us-ingest` et `need-understanding` reçoivent une user story **déjà écrite**. On
  ingère le produit de la discovery, on ne la fait pas. Or c'est là que se définissent les
  **exigences non-fonctionnelles**, et aucune skill n'en dérive une au moment où elle serait encore
  négociable : nos skills de performance et de sécurité s'exécutent contre une application qui
  tourne déjà.
- **Run** — sur les quatre pratiques du *shift-right* (monitoring synthétique, chaos, incident →
  test de non-régression, A/B), la couverture est de **zéro**. `traffic-replay` rejoue un fichier
  HAR que l'utilisateur fournit ; ce n'est pas du test en production.

L'objectif affiché du projet est de couvrir l'activité de test **tout au long du cycle**. Il ne
correspondait pas au produit.

## Décision

**On vise les deux bouts plutôt que de corriger l'objectif.**

Le périmètre devient : l'activité de test de **Discovery à Run**, en conservant intactes les
frontières déjà posées.

## Ce que la décision ne change pas

- **ADR 0004 tient.** On ne descend toujours pas sous le niveau système. Couvrir Discovery et Run
  ne rouvre pas le niveau unitaire — ce sont des questions orthogonales.
- **La contrainte d'autonomie tient.** Aucune skill de Run ne livrera d'agent, de collecteur ou de
  service qui s'exécute seul. Ce que le projet peut faire au Run, c'est **produire les artefacts**
  qu'un utilisateur branche sur l'outillage qu'il possède déjà.
- **La règle de l'oracle tient.** Une exigence non-fonctionnelle dérivée en Discovery est une
  **proposition à arbitrer**, pas un chiffre inventé. Si le contexte ne permet pas de fonder un
  budget de latence, la skill pose une question ouverte — elle n'écrit pas « 200 ms » parce que ça
  sonne bien.

## Conséquences

**Discovery** — deux manques nommés : dériver des exigences non-fonctionnelles au moment où elles
sont négociables, et évaluer la testabilité d'un besoin avant qu'il ne soit figé.

**Run** — quatre pratiques, dont deux entièrement absentes du dépôt (chaos, monitoring synthétique).
La plus utile n'est probablement aucune des deux : c'est **incident → test de non-régression**, qui
ferme la boucle entre la production et la suite, et qui utilise ce que le projet sait déjà faire.

**Le risque, écrit maintenant** : élargir le périmètre avec **zéro utilisateur** est exactement
l'ordre que ce dépôt s'est reproché toute la journée. La contrepartie assumée par le fondateur est
que la promesse « tout au long du cycle » est une promesse de positionnement, et qu'un produit qui
ne la tient pas ne se rattrape pas par la qualité de ce qu'il tient.

## Alternative considérée

**Corriger l'objectif** — écrire « QAIA couvre Delivery et Maintenance » et l'assumer, comme
[ADR 0004](0004-test-level-boundary.md) assume le niveau système. Écartée par le fondateur : le
différenciateur revendiqué est la couverture du cycle, et le réduire à sa moitié la mieux tenue
reviendrait à ressembler aux outils qui n'attaquent que l'exécution.
