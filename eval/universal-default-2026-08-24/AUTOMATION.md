# Le budget d'automatisation devient conditionnel — mesuré sur 7 suites écrites ailleurs

**Date** 2026-08-24 · Phase 1b de la refonte · corpus reconstitué par `eval/tools/fetch_suites.py`

## Le même défaut, un étage plus haut — et il y était d'abord

`automation_score.py` a porté ce défaut **en premier** : corrigé le 2026-08-08 après 408 constats
faux, reproduit à l'identique dans `structural_score.py` le lendemain, avec la leçon écrite entre
les deux. Mais la correction de 2026-08-08 était elle-même la mauvaise : elle a créé un **mode
tiers derrière un drapeau**, c'est-à-dire une exception à demander, au lieu d'inverser le défaut.

Et elle jetait trop. Le mode tiers réduisait le barème à une seule ligne — la substance des
assertions — même pour une suite qui satisfait parfaitement les trois autres. **Une suite tierce
impeccablement tracée par ses propres identifiants n'en tirait aucun crédit.**

## Ce qui remplace les deux budgets figés

Chaque ligne porte désormais sa **condition d'applicabilité**, et le budget se remet à l'échelle
sur celles qui s'appliquent. Une dimension exclue est **nommée, jamais notée zéro**.

| Dimension | Notée si… | Pourquoi pas toujours |
|---|---|---|
| `substantive_assertions` | toujours | universelle : une assertion creuse est creuse chez tout le monde |
| `traceability` | au moins un test porte une référence d'exigence | 128 des 428 constats de `realworld` lui reprochaient de n'être pas tracée vers **un cahier de tests qui n'existe pas** |
| `pom_as_fixtures` | la suite montre une structure d'objets de page | POM est une architecture parmi d'autres ; l'exiger, c'est noter un choix de conception |
| `robust_selectors` | la suite emploie des localisateurs par rôle **quelque part** | `realworld` **publie** un contrat de sélecteurs CSS (`specs/e2e/SELECTORS.md`) que toute implémentation doit honorer. On ne peut pas distinguer « a choisi CSS délibérément » de « ne connaît pas mieux » |

**Deux corrections, pas une.** Exclure la dimension évite de punir ; encore fallait-il **créditer**.
La détection de traçabilité n'acceptait que `@QAIA-<ID>` : `REQ_REF` reconnaît maintenant
`JIRA-1234`, `REQ-77`, `PROJ-12` comme `QAIA-US-004-009`. Le séparateur avant les chiffres est
obligatoire, ce qui écarte `HTML5`, `CSS3`, `OAuth2` — des mots de titre, pas des références.
**Le recoupement avec le cahier reste réservé à nos identifiants** : sans cette séparation, noter
une suite tierce en fournissant un cahier aurait signalé chacun de ses identifiants comme inventé.

## La mesure

Sept suites Playwright réelles, récupérées depuis des dépôts nommés (`_manifest.json` avec une
empreinte par dépôt).

| Suite | universel | constats | dimensions notées | profil `qaia` | constats |
|---|---:|---:|---:|---:|---:|
| `realworld-apps/realworld` | **100,0** | 19 | 1 | 30,0 | **420** |
| `COVESA/ifex-viewer` | 98,3 | 1 | 2 | 54,1 | 14 |
| `mxfng/drumhaus` | 96,1 | 18 | 2 | 52,9 | 48 |
| `dbcls/sparqlist` | 87,0 | 8 | 2 | 47,9 | 16 |
| `solidcouch/solidcouch` | 86,9 | 24 | 2 | 47,8 | 88 |
| `accordproject/template-playground` | 79,4 | 36 | 2 | 43,7 | 57 |
| `vnglst/koenvangilst.nl` | 76,5 | 38 | 2 | 42,1 | 72 |
| **médiane / total** | **87,0** | **144** | | **47,8** | **715** |

**571 des 715 constats — 80 % — ne nommaient aucun défaut.** Ils constataient l'absence de nos
conventions. Les 144 qui restent sont des signaux qui transfèrent : sélecteurs fragiles là où la
suite emploie par ailleurs des rôles, attentes interdites, assertions faibles.

Non-régression sur notre propre suite : **95,3 dans les deux profils**, quatre dimensions
applicables — nos suites montrent les rôles, les objets de page et la traçabilité, donc rien ne
change pour elles.

## Le défaut que cette mesure a révélé, et qui n'est pas corrigé

`realworld` obtient **100,0 avec 19 constats au compteur**, dont **8 attentes interdites**. Le
score n'est pas faux : une seule dimension s'applique, et la suite y est parfaite. Mais un nombre
« sur 100 » qui couvre une dimension sur quatre se lit comme un satisfecit général.

Corrigé à moitié : le résultat porte désormais un champ `scoreScope` qui **nomme** les dimensions
évaluées, celles exclues, et marque `narrow: true` sous trois dimensions. **Ce n'est pas une
solution complète** — un lecteur pressé verra toujours 100,0 d'abord. Le vrai remède serait un
barème universel plus riche : les attentes interdites et les assertions faibles sont des défauts
chez tout le monde et ne pèsent aujourd'hui sur aucune ligne de budget. **Reste ouvert.**

## Limite honnête du corpus

Douze dépôts visés, **sept retenus** : cinq ont été écartés parce que le répertoire portant le
plus de fichiers `.spec.*` s'est avéré contenir du Jest ou du Vitest, que ce scoreur ne sait pas
lire. Les écarter est correct — noter un matériau qu'on ne sait pas lire fabrique un chiffre —
mais l'heuristique « le répertoire qui a le plus de specs » peut aussi **rater la vraie suite
Playwright** d'un dépôt qui en possède une ailleurs. Sept suites ne sont pas un échantillon ; ce
que la mesure établit, c'est l'ordre de grandeur du bruit retiré, pas une note du Playwright
mondial.

## Reproduire

```bash
python eval/tools/fetch_suites.py "realworld-apps/realworld,solidcouch/solidcouch,..." /tmp/suites
python eval/tools/automation_score.py --tests-dir /tmp/suites/<repo> --skip-mutation
python eval/tools/automation_score.py --tests-dir /tmp/suites/<repo> --skip-mutation --profile qaia
```

Campagne de mutation : **26 mutations, 26 tuées, 0 survivante** — dont cinq visant précisément
cette inversion (budget inconditionnel, détection réduite à la convention maison, bascule
silencieuse du profil par défaut, constats de convention remontant pour une dimension non évaluée,
portée du score tue).
