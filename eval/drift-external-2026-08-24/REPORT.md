# `spec_suite_drift` pointé ailleurs — 11 constats sur 11 étaient vides

**Date** 2026-08-24 · Phase 2 de la refonte · 12 dépôts visés, 4 analysés

## Pourquoi cette campagne existe

`eval/lint-external-2026-08-09/REPORT.md` se termine par une phrase qui n'a jamais été suivie
d'effet : *« aucun [des dix autres outils] n'a été essayé sur du matériau étranger »*.

`spec_suite_drift.py` était le dernier scoreur du noyau dans ce cas. Il est né d'un projet tiers
— `realworld-apps/realworld` — mais **d'un seul**, celui qui a servi à l'écrire. Un outil validé
sur l'exemple qui l'a fait naître ne prouve rien : il prouve qu'on a su décrire un cas.

## Le résultat brut

| Dépôt | fichiers de test | code de sortie | constats |
|---|---:|---:|---:|
| `wikimedia/mediawiki-services-cxserver` | 19 | 1 | 5 |
| `wikimedia/mediawiki-services-push-notifications` | 3 | 1 | 3 |
| `jhalter/mobius` | 57 | 1 | 3 |
| `ScottyLabs/cmueats` | 7 | 0 | 0 |
| | | | **11** |

Onze constats, **tous de la règle R2** (`unexercised-status`). Aucun R1, aucun R3, sur quatre
projets. Une distribution aussi propre est un signal, pas un résultat.

## Ce que le compteur disait, et que personne ne lisait

```
"counts": { "spec_paths": 9, "path_status_pairs_in_suite": 0, "distinct_status_in_suite": 0 }
```

**Zéro paire chemin↔code extraite. Sur les quatre projets.** Et zéro code HTTP reconnu sur trois
d'entre eux.

Les règles R1 (`undeclared-status`) et R3 (`path-not-in-spec`) ont besoin de paires : elles ne
pouvaient **physiquement pas** se déclencher. R2, elle, dit *« la spécification promet 400 et
aucun test ne mentionne ce code »* — une phrase qui reste vraie quand l'outil n'a rien lu du
tout. **Les onze constats mesuraient la cécité de l'outil, pas les suites.**

## La preuve, en une commande

```
$ mkdir vide && echo "rien" > vide/README.md
$ python eval/tools/spec_suite_drift.py --spec mobius/spec.yaml --tests-dir vide
3 ecart(s) entre la specification et la suite :
  unexercised-status  la specification promet 400 sur 3 chemin(s) -- ; aucun test ne mentionne ce code
  unexercised-status  la specification promet 401 sur 9 chemin(s) -- ; aucun test ne mentionne ce code
  unexercised-status  la specification promet 500 sur 4 chemin(s) -- ; aucun test ne mentionne ce code
```

**Un répertoire vide produit trois constats affirmatifs.** L'outil ne sait pas distinguer « la
suite ne teste pas ça » de « il n'y a pas de suite ».

C'est exactement l'invariant que `structural_score.py` applique déjà — `UNSCORED` plutôt qu'un
20/100 muet sur un parse vide, ajouté en juillet après le même genre de constat (#105). Le second
outil ne l'avait pas, **parce qu'il n'avait jamais lu qu'un seul projet**. Troisième occurrence
de ce mécanisme dans ce dépôt, après `automation_score` et `structural_score`.

## Le correctif

Un verdict `UNCOMPARABLE`, et le refus de rendre le moindre écart :

- **zéro fichier lisible** → « aucun fichier de test lisible par cet outil (N ignoré(s) : il ne
  lit que le JS/TS nommé `.spec.`/`.test.`/`.e2e.`) » ;
- **des fichiers lus, aucun code HTTP reconnu** → « la suite emploie vraisemblablement une autre
  façon d'affirmer un statut que celles que cet outil sait lire ».

Les deux motifs sont distincts **et le contrôle l'exige** : « il n'y a pas de suite » et « la
suite parle une langue que je ne lis pas » appellent deux actions différentes chez le lecteur.
Deux compteurs nouveaux — `suite_files_read`, `suite_files_skipped_unreadable` — rendent l'écart
visible dans le JSON, ce qui manquait pour que quiconque s'en aperçoive. Code de sortie **3**,
distinct du vert (0) comme du rouge (1) : une CI ne doit pas lire un refus comme un succès.

## Après correctif — et la première version du correctif était fausse

**Première version, publiée puis réfutée le jour même.** Le seuil avait été posé sur
`all_status` — « au moins un code HTTP vu **quelque part** » — et laissait donc
`push-notifications` comparable avec 3 constats. Une passe de réfutation en contexte vierge a
montré que ces 3 constats sont **de la même espèce que les 11** :

```
"counts": { "spec_paths": 8, "suite_files_read": 3,
            "path_status_pairs_in_suite": 0, "distinct_status_in_suite": 2 }
```

`path_status_pairs_in_suite: 0` — c'est-à-dire **le symptôme exact que ce rapport identifie
comme la définition de la cécité**, deux sections plus haut. Les « 2 codes reconnus » sont un
`418` et un `500` littéraux dans un test unitaire du formateur de log `errForLog`, qui n'émet
aucune requête vers aucun des huit chemins de la spécification. Retirer ce seul fichier faisait
basculer le dépôt en `UNCOMPARABLE`.

**La garde avait été posée sur la mauvaise grandeur.** Le diagnostic désignait `pairs` — R1 et R3
en ont besoin, et R2 n'a de sens que si la suite exerce réellement l'API. Un seuil franchi par du
bruit lexical n'est pas une preuve d'exercice.

| | avant | 1er correctif | **correctif tenu** |
|---|---:|---:|---:|
| constats rendus | 11 | 3 | **0** |
| dépôts comparables | 4 | 1 | **0** |
| dépôts incomparables | 0 | 3 | **4** |

**Le verdict honnête sur cette campagne est donc : quatre dépôts, quatre `UNCOMPARABLE`, zéro
constat.** L'outil n'a rien trouvé — parce qu'il ne sait pas lire ces suites, et il le dit
désormais au lieu de rendre onze phrases vraies et vides.

*Défaut mineur également relevé* : « 11 constats sur 4 projets » — `cmueats` en rendait 0. C'était
11 sur 3.

**Et la campagne elle-même confondait les deux.** `drift_campaign.py` lisait `findings` sans
jamais regarder `verdict` : un dépôt illisible entrait dans le total au même titre qu'un dépôt
sans dérive — **la confusion exacte que cette campagne existe pour trouver ailleurs, commise sur
elle-même**. Corrigé : le résumé distingue désormais comparés / incomparables / erreurs d'outil,
et le total des constats porte explicitement sur les seuls dépôts comparables.

## Ce que la campagne a coûté en méthode, et qui est à moi

Sur 12 dépôts visés, **8 ont été écartés** : *aucun fichier de test* dans le dépôt. C'est correct,
et c'est dit plutôt que fondu dans le dénominateur — un dénominateur qui perd ses exclusions
transforme « 2 constats sur 3 projets » en « 2 sur 20 ».

En revanche j'ai téléchargé des tests **Go et Python** vers un outil qui ne lit que le JS/TS, et
je ne l'ai su qu'en lisant les compteurs. C'est la même faute de méthode que dans la campagne
d'automatisation du même jour, où cinq dépôts ont été écartés pour du Jest servi à un lecteur
Playwright. **Nourrir un outil d'un matériau qu'il ne sait pas lire produit un résultat, et un
résultat n'est pas une mesure.** Que l'outil le dise désormais est le vrai acquis de la journée ;
que je continue à le faire est le vrai coût.

## Garde et mutation

Le refus est éprouvé par quatre cas dans `selfcheck_spec_suite_drift.py` — répertoire vide,
tests dans un langage non lu, fichiers lus sans idiome reconnu, et **la contre-épreuve** : une
suite lisible doit toujours être comparée, sinon la garde a simplement éteint l'outil au lieu de
le rendre honnête.

Campagne de mutation : **30 mutations, 30 tuées, 0 survivante.** Une survivante intermédiaire
mérite d'être notée : neutraliser la condition « zéro fichier lu » ne changeait rien, parce que
la condition « aucun code reconnu » rattrapait le cas et rendait le même verdict **sous un motif
faux**. La garde ne vérifiait que le verdict. Elle vérifie maintenant le motif.

## Reproduire

```bash
python eval/tools/drift_campaign.py "wikimedia/mediawiki-services-cxserver,jhalter/mobius,..." /tmp/drift
```
