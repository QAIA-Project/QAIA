# Le barème universel d'automatisation gagne une dimension, et en refuse une autre (#112)

**Date** 2026-11-23 · [#112](https://github.com/QAIA-Project/QAIA/issues/112) · suites
reconstituées par `eval/tools/fetch_suites.py` depuis les dépôts de
`eval/universal-default-2026-08-24/suites-manifest.json`

## Le défaut

`automation_score.py`, profil universel : `realworld-apps/realworld` affichait **100,0** avec ses
attentes fixes au compteur. Une seule dimension s'appliquait (`substantive_assertions`) et la suite
y était parfaite ; `scoreScope.narrow` le disait, mais un lecteur pressé voyait 100,0 d'abord.

## Ce qui entre : la discipline temporelle

Une attente fixe (`waitForTimeout`, `networkidle`) est une fragilité **chez tout le monde**, sans
rien emprunter aux conventions de QAIA ; la documentation de Playwright la déconseille elle-même.
Nouvelle dimension `timing_discipline`, poids 15, **toujours évaluée** comme
`substantive_assertions` : la part des tests qu'aucune attente fixe ne touche, dans leur corps ou
dans un hook de leur fichier (un `beforeEach` touche chacun des tests du fichier).

Mesurée sur les six suites étrangères avant d'entrer (porte d'entrée de la refonte) :

| Suite | tests | touchés par une attente fixe | avant | **après** |
|---|---:|---:|---:|---:|
| `realworld-apps/realworld` | 129 | 8 | 100,0 | **98,0** |
| `solidcouch/solidcouch` | 63 | 13 | 86,9 | **85,3** |
| `vnglst/koenvangilst.nl` | 83 | 4 | 78,0 | 81,7 |
| `mxfng/drumhaus` | 29 | 0 | 96,1 | 97,0 |
| `dbcls/sparqlist` | 7 | 0 | 87,0 | 89,9 |
| `COVESA/ifex-viewer` | 12 | 0 | 98,3 | 98,7 |
| suite vitrine `expense-demo` (profil par défaut) | — | 0 | 95,3 | 95,9 |

Les deux suites qui ont des attentes fixes sur une part notable de leurs tests baissent ; celles qui
n'en ont pas montent légèrement, parce qu'elles sont créditées d'une propriété qu'elles ont
réellement. `vnglst` monte malgré 4 tests touchés : 79 sur 83 ne le sont pas. **Plus aucune suite
étrangère n'affiche 100,0.**

(Le `realworld` d'aujourd'hui n'est pas octet pour octet celui du 2026-08-24 : son empreinte a
changé, 9 constats d'attente au lieu de 8. Les colonnes « avant » et « après » sont mesurées sur la
même récupération.)

## Ce qui est essayé et refusé : « toutes les assertions sont faibles »

Idée : ne pas créditer comme substantiel un test dont **toutes** les assertions sont faibles
(`toBeTruthy()`, `not.toBeNull()`). Mesurée sur les six suites : **un seul cas**, et c'est un faux
positif — `expect(response.ok()).toBeTruthy()` vaut `toBe(true)` sur un booléen. Une règle lexicale
qui punit un idiome est exactement ce que la porte d'entrée existe pour arrêter. **Retirée** ; la
tentative est laissée en commentaire dans le code, à l'endroit où elle aurait été.

## Les deux autres signaux de l'issue

- **Absence totale d'assertion** : déjà budgétée. Un test sans assertion ne compte pas dans
  `substantive_assertions` (et lève un constat bloquant) ; l'issue la croyait seulement détectée.
- **Citations mortes** : zéro occurrence sur les six suites étrangères. Sans matériau étranger qui
  la montre, la mesure d'entrée ne peut rien établir ; la règle reste un constat non bloquant.

## Gardes

- `selfcheck_automation_score.py` : une attente dans un test touche ce test et pas son voisin ;
  une attente dans un hook touche chaque test de son fichier, et lui seul ; une suite à attente
  fixe ne peut plus afficher 100.
- `mutate_guards.py` : deux mutations nouvelles (la dimension neutralisée ; le hook qui n'atteint
  plus ses tests), toutes deux tuées. **44 tuées, 0 survivante, 0 non exécutable.**
  Les 3 « non exécutables » relevées plus tôt dans la journée n'étaient pas anciennes : c'étaient
  des motifs multilignes qui ne se trouvent pas dans une copie de travail en fins de ligne CRLF
  (Windows). En LF, elles s'exécutent et sont tuées.

Rejouer :

```
python eval/tools/fetch_suites.py "realworld-apps/realworld,solidcouch/solidcouch,mxfng/drumhaus,dbcls/sparqlist,vnglst/koenvangilst.nl,COVESA/ifex-viewer" <dir>
python eval/tools/automation_score.py --tests-dir <dir>/<repo> --skip-mutation
```
