# QAIA — tableau de bord

Deux nombres, et seulement deux : ceux que la [spec de refonte](superpowers/specs/2026-08-24-qaia-refonte-design.md)
(§3.3, §5) retient parce qu'aucun ne dépend de ce que QAIA a produit lui-même. L'ordre des travaux
est dans [`ROADMAP.md`](ROADMAP.md) ; l'ancien relevé chronologique (1 350 lignes, juillet à
novembre 2026) est archivé dans [`archive/STATUS.md`](archive/STATUS.md).

*Dernière mise à jour : 2026-11-23.*

## 1. Le taux de PASS sur des cahiers que QAIA n'a pas écrits

| | |
|---|---:|
| **PASS, barème par défaut** | **115 / 269 (42,8 %)** |
| CONCERNS / FAIL / non notables | 76 / 63 / 15 |
| corpus | les 15 dépôts gelés le 2026-08-09, **rejoués le 2026-11-23** |
| référence de la spec | 101 / 244 au 2026-08-24, cible ≥ 107 |

**Ces deux lignes ne se comparent pas.** Six des quinze dépôts ont bougé depuis le gel ; le corpus
rejoué compte 269 fichiers, pas 244. Tant que le corpus n'est pas re-figé, la cible ne peut être
déclarée ni atteinte ni manquée ([#119](https://github.com/QAIA-Project/QAIA/issues/119)).
Sur les neuf dépôts stables seuls (145 fichiers) : 47 PASS.

Rejouer :

```
python eval/tools/fetch_corpus.py eval/gherkin-external-2026-08-09/corpus.json <dossier>
python eval/tools/score_corpus.py <dossier>
```

Dernier mouvement : un docstring n'est plus lu comme des scénarios, PASS 109 → 115 sur le même
corpus ([rapport](../eval/corpus-remeasure-2026-11-23/REPORT.md)).

## 2. Le nombre d'utilisateurs réels

| | |
|---|---:|
| **pilotes humains ayant mené le parcours** | **0** |
| étoiles / forks / watchers GitHub | 0 / 1 / 0 |

C'est le nombre qui compte le plus et le seul qu'aucun commit ne peut faire bouger : il dépend
d'un tiers ([#89](https://github.com/QAIA-Project/QAIA/issues/89)). Le kit pilote est
[`PILOT-KIT.md`](PILOT-KIT.md).

## Ce que le produit est aujourd'hui

**4 skills, 3 plugins** : `qaia-core` 0.6.0 (`generate`), `qaia-playwright` 0.3.0 (`automate`,
`probe`), `qaia-score` 0.3.1 (`judge`). Pré-alpha.
