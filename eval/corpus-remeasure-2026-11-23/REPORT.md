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

## Suite, le même jour : le corpus re-figé, et la référence corrigée (#119)

### Quinze commits, quinze empreintes

`eval/tools/pin_corpus.py` cherche, pour chaque dépôt, le commit dont les premiers `.feature`
redonnent l'empreinte du gel, et l'inscrit dans le manifeste (`commit`). `fetch_corpus.py` lit
désormais ce commit, pas la branche. Résultat : **15 empreintes sur 15 identiques au gel,
244 fichiers sur 244.** La métrique n°1 est de nouveau strictement rejouable par un tiers.

En route, un défaut du fetcher : il prenait 25 fichiers par dépôt, alors que le champ `features`
du manifeste donne le nombre **retenu** au gel (leur somme vaut exactement 244). Pour
`brighton36/CoinPost`, 384 `.feature`, le gel n'en avait gardé que **12**. Le fetcher en prenait
25 et annonçait « a bougé » sur un dépôt **sans aucun push depuis 2015**. Corrigé : il prend
`min(25, features)`. Des six dépôts « ayant bougé » plus haut, cinq avaient vraiment bougé ;
le sixième était ce défaut.

### Ce qui change pour la référence

Rejoué sur le corpus figé, chaque version du noyau :

| noyau | PASS / 244 |
|---|---:|
| 2026-08-10 (`0fb509b`), option `--third-party` | **96** |
| 2026-08-24 (`7178da1`), barème universel par défaut, phase 1 | **96** |
| 2026-08-24 (`9f3302e`), après les deux corrections du détecteur de doublons | 98 |
| 2026-11-23 (`8c68c2d`), après le correctif des docstrings | **104** |

**Les chiffres 101 et 107 n'étaient pas mesurés sur le corpus gelé.** Le rapport du 2026-08-24
le disait lui-même : il avait été mesuré sur 257 fichiers, trois dépôts ayant « bougé », dont
CoinPost à tort. La cible de la spec (§7) se définissait comme **« le niveau que `--third-party`
atteint déjà en opt-in »** ; sur le corpus gelé, ce niveau est **96**.

**Cible restatée sur le corpus figé : ≥ 96, au sens de la spec. Mesuré : 104.** Elle est
atteinte, et ce n'est pas le même énoncé que « ≥ 107 atteint » : le nombre 107 lui-même n'est
plus un objectif, parce qu'il n'a jamais désigné ce corpus. La phase 1 avait bien fait ce
qu'elle annonçait (le défaut égalait l'opt-in, 96 = 96) ; les +8 depuis viennent de deux
corrections du noyau, chacune gardée par un invariant.

Prochaine cible chiffrée, s'il en faut une : elle se fixe sur **ce** corpus, en nombre de PASS
sur 244, et pas en écart à une référence d'un autre corpus.
