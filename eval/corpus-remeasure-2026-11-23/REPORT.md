# Le corpus étranger remesuré, et un défaut du noyau qui y fabriquait des FAIL

**Date** 2026-11-23 · Point B1 de la [feuille de route](../../docs/ROADMAP.md) · corpus
reconstitué par `eval/tools/fetch_corpus.py` depuis le manifeste gelé du 2026-08-09

## Le corpus gelé ne se reconstitue plus à l'identique

La spec de refonte fixe une cible, **≥ 107 PASS sur les 244 cahiers gelés**, et la phase 1 avait
atteint 101. Rejoué trois mois plus tard :

| | |
|---|---:|
| dépôts du manifeste | 15 |
| empreinte identique au gel | **9** |
| dépôts ayant bougé | 6 (`Automattic/wpcom-legacy-redirector`, `IfcOpenShell/IfcOpenShell`, `LarsBerberich/Binokel_Score_Tracker_BDD`, `alphagov/whitehall`, `asok/projectile-rails`, `brighton36/CoinPost`) |
| fichiers récupérés | 269 (gel : 244) |

**Le chiffre 101 n'est donc plus rejouable par un tiers.** `fetch_corpus.py` le dit au lieu de
rendre un autre corpus sous le même nom, ce qui est son travail. Mais une métrique dont le
corpus de référence dérive ne peut plus juger une cible fixe : il faudra soit **figer le contenu**
(et non plus seulement son empreinte), soit mesurer sur les 9 dépôts stables seulement. Décision à
prendre avant toute nouvelle cible chiffrée.

## Le défaut trouvé : un docstring lu comme du Gherkin

`behave/behave` se teste en écrivant des features entières **dans des docstrings** :

```gherkin
Scenario: Run behave with feature directory
  Given a file named "features/alice.feature" with:
    """
    Feature: Alice
      Scenario: A1
        Given a step passes
    """
  When I run "behave -f progress features/"
  Then it should pass with: ...
```

`structural_score.parse_scenarios` ne distinguait pas le contenu d'un docstring du reste. Chaque
`Scenario:` imbriqué devenait un scénario du fichier, en général sans `Then` puisque coupé de son
contexte, et le fichier prenait un FAIL « no expected result (C2 — a question, not a test) » pour
un test **qu'il n'avait pas écrit**. C'est le défaut corrigé la même session dans
`check_nl_projection.py` (#106), un étage plus bas : dans le noyau, sur le chemin par défaut.

## Mesure, même corpus, avant et après

| | avant | **après** |
|---|---:|---:|
| PASS | 109 | **115** |
| CONCERNS | 71 | 76 |
| FAIL | 74 | **63** |
| non notables | 15 | 15 |
| scénarios « sans `Then` » | 188 | **48** |
| constats « no expected result » | 50 | 41 |
| constats « pesticide paradox » | 24 | **7** |
| constats au total | 112 | **86** |

Sur les **9 dépôts stables seuls** (145 fichiers) : PASS 41 → **47**, FAIL 60 → **49**.

**Chaque fichier dont la porte ou le score a changé contient un docstring** (vérifié fichier par
fichier, aucune exception). Aucune porte n'a baissé. Six scores ont baissé **sans changer de
porte**, tous en FAIL avant comme après, et la baisse est juste : les scénarios imbriqués, qui
portaient leur propre `Then`, gonflaient la note ; le vrai scénario de mise en place
(`Setup directory structure`, sans `Then`) pèse maintenant seul.

## Ce qui reste dans les 48 « sans `Then` »

Une lecture des cas restants trouve **3 scénarios** qui portent une assertion sous `And` après un
`When` (`And I should only see …`). Ils ont un résultat attendu, mal étiqueté ; « a question, not
a test » les décrit mal. Mais trois cas ne justifient pas une règle lexicale (`should`, `must`…)
dans le barème universel, d'autant que ce dépôt a déjà payé trois fois une règle lexicale qui
pénalisait une formulation plutôt qu'une lacune. **Laissé en l'état, signalé ici.** Les 45 autres
n'ont effectivement pas de résultat attendu.

## Garde

- `check_universal_default.py`, **I11** : un docstring reste une donnée, jamais un scénario.
  Vérifié rouge sur l'ancien `structural_score.py`, vert sur le nouveau.
- `mutate_guards.py` : la mutation qui réactive la lecture des docstrings est tuée par I11
  (39 tuées, 0 survivante).
- `plugins/qaia-score/scripts/structural_score.py` recopié par `ship_scorers.py` : le plugin
  publié porte la correction.

Rejouer : `python eval/tools/fetch_corpus.py eval/gherkin-external-2026-08-09/corpus.json <dir>`
puis `python eval/tools/score_corpus.py <dir>`.
