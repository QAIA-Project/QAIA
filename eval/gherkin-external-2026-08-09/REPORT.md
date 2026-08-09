# 244 cahiers Gherkin écrits par d'autres — et le même défaut, un étage plus haut

**Date** 2026-08-09 · 15 dépôts, 244 fichiers `.feature`, tous runners confondus
(behave, TestCafe, Ruby, Selenium) · corpus gelé dans `corpus.json` avec un sha256 par dépôt

## Pourquoi cette campagne existe

Toute la journée a été consacrée à scanner des suites **Playwright** — c'est-à-dire *une skill sur
trente-sept*. Le fondateur l'a relevé en trois mots : **« on n'a pas que Playwright. »**

`testbook-validate` affirme auditer *« n'importe quel cahier Gherkin, généré par QAIA ou non »*, et
`structural_score.py` le note. **Cette affirmation n'avait jamais été éprouvée sur du Gherkin écrit
ailleurs.** La population disponible est de **624 640 fichiers `.feature`** sur GitHub — deux ordres
de grandeur au-dessus de ce qui avait été regardé.

Le corpus inclut `alphagov/whitehall` — du Gherkin de production du gouvernement britannique.

## Le résultat brut, avant correction

| | |
|---|---:|
| score médian | **57 / 100** |
| portes | **138 FAIL**, 106 CONCERNS, 0 PASS |
| arrêts forcés | 62 |
| constats | **622** |

Sur ces 622 constats, **463 portent sur nos propres conventions** :

| constat | occurrences | existe dans Gherkin ? |
|---|---:|---|
| `missing priority tag (@P1/@P2/@P3)` | 232 | **non** — convention QAIA |
| `technique tag count != 1 from the closed list` | 231 | **non** — convention QAIA |

Et le barème enfonçait le clou : **`traceability` valait 0 sur les 244 fichiers**, parce que
« traçable » signifie « porte un tag `@QAIA-<ID>` ». **25 points sur 100 perdus par construction.**

**C'est exactement le défaut corrigé la veille dans `automation_score.py`** — trois lignes de barème
encodant des conventions maison, une suite tierce notée 30/100 pour ne pas être QAIA — reproduit à
l'identique un étage plus haut, dans un outil que personne n'avait pensé à vérifier.

## Le signal réel était dessous

159 constats survivent au retrait des conventions, et ils sont indépendants de tout framework :

| constat | occurrences |
|---|---:|
| paradoxe du pesticide (scénarios quasi identiques) | 88 |
| aucun résultat attendu — *une question, pas un test* | 48 |
| `Then` vague ou non vérifiable | 15 |
| étapes tronquées | 4 |

### Un défaut confirmé dans la source, chez `alphagov/whitehall`

`features/admin-statistics-announcements.feature:26`

```gherkin
Scenario: searching for a statistics announcement
  Given I am a GDS editor in the organisation "Department for Beards"
  And a statistics announcement called "MQ5 statistics" exists
  And a statistics announcement called "PQ3 statistics" exists
  When I search for announcements containing "MQ5"
  And I should only see a statistics announcement called "MQ5 statistics"
```

L'étape d'assertion commence par **`And`**, qui prolonge le `When`. **Ce scénario ne contient aucun
`Then`.** Cucumber l'exécutera sans broncher — les mots-clés sont cosmétiques à l'exécution — mais
le scénario se lit comme s'il agissait sans jamais vérifier, et c'est ainsi qu'un relecteur humain
le lira aussi.

Modeste, réel, et trouvé dans une base de code gouvernementale.

## Le correctif

`--third-party` exclut les deux règles de convention **et les dit exclues**, et remet le barème à
l'échelle sur les trois dimensions qui transfèrent — lisibilité, complétude, cohérence.
`traceability` n'est pas notée zéro : elle est **retirée du calcul**.

| | par défaut | `--third-party` |
|---|---|---|
| score médian | 57 | **77** |
| portes | 138 FAIL / 106 CONCERNS / 0 PASS | **92 FAIL / 45 CONCERNS / 107 PASS** |
| constats | 622 | **159** |

**92 fichiers échouent encore**, et ceux-là échouent pour des raisons qui tiennent : pas de `Then`,
`Then` non vérifiable, scénarios dupliqués, étapes tronquées.

Aucune régression sur nos propres cahiers : la démonstration rend 76 / 80 / 90 / 77 à l'identique.

## Ce que cette campagne dit, et qui dépasse le Gherkin

**Le même défaut a été commis deux fois, dans deux outils, à un jour d'intervalle.** Corrigé le
2026-08-08 dans `automation_score.py` après 408 constats faux ; reproduit à l'identique dans
`structural_score.py`, qui n'avait jamais été pointé ailleurs que sur sa propre production.

La leçon avait pourtant été écrite ce jour-là, mot pour mot : *« corriger le cas devant moi plutôt
que la classe »*. Elle a été écrite, consignée, citée dans trois rapports — et **le deuxième outil
n'a pas été vérifié.**

**Un outil qui n'a jamais lu que sa propre production ne sait pas ce qu'il suppose.** C'est vrai du
scoreur d'automatisation, c'était vrai du scoreur structurel, et rien ne garantit que les dix autres
outils de `eval/tools/` soient différents — **aucun n'a été essayé sur du matériau étranger.**
