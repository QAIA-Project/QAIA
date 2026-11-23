# QAIA — tableau de bord

Deux nombres, et seulement deux : ceux que la [spec de refonte](superpowers/specs/2026-08-24-qaia-refonte-design.md)
(§3.3, §5) retient parce qu'aucun ne dépend de ce que QAIA a produit lui-même. L'ordre des travaux
est dans [`ROADMAP.md`](ROADMAP.md) ; l'ancien relevé chronologique (1 350 lignes, juillet à
novembre 2026) est archivé dans [`archive/STATUS.md`](archive/STATUS.md).

*Dernière mise à jour : 2026-11-23.*

## 1. Le taux de PASS sur des cahiers que QAIA n'a pas écrits

| | |
|---|---:|
| **PASS, barème par défaut** | **104 / 244 (42,6 %)** |
| CONCERNS / FAIL / non notables | 72 / 58 / 10 |
| corpus | les 15 dépôts gelés le 2026-08-09, **épinglés chacun à un commit** : 15 empreintes sur 15 identiques au gel |
| référence de la spec, rejouée sur ce corpus | 96 (le niveau de l'opt-in `--third-party`) ; cible : le défaut au moins à ce niveau |

**Cible atteinte : 104 ≥ 96.** Les anciens chiffres 101 et 107 avaient été mesurés sur un corpus
qui avait déjà dérivé (257 fichiers) ; ils ne désignent pas celui-ci
([#119](https://github.com/QAIA-Project/QAIA/issues/119),
[rapport](../eval/corpus-remeasure-2026-11-23/REPORT.md#suite-le-même-jour--le-corpus-re-figé-et-la-référence-corrigée-119)).

Rejouer :

```
python eval/tools/fetch_corpus.py eval/gherkin-external-2026-08-09/corpus.json <dossier>
python eval/tools/score_corpus.py <dossier>
```

Derniers mouvements, sur le corpus figé : un docstring n'est plus lu comme des scénarios
(98 → 104), après les deux corrections du détecteur de doublons du 2026-08-24 (96 → 98).

## 2. Le nombre d'utilisateurs réels

| | |
|---|---:|
| **pilotes humains ayant mené le parcours** | **0** |
| étoiles / forks / watchers GitHub | 0 / 1 / 0 |

C'est le nombre qui compte le plus et le seul qu'aucun commit ne peut faire bouger : il dépend
d'un tiers ([#89](https://github.com/QAIA-Project/QAIA/issues/89)). Le kit pilote est
[`PILOT-KIT.md`](PILOT-KIT.md).

## Ce que le produit est aujourd'hui

**4 skills, 3 plugins** : `qaia-core` 0.6.3 (`generate`), `qaia-playwright` 0.3.2 (`automate`,
`probe`), `qaia-score` 0.3.3 (`judge`). Pré-alpha.
