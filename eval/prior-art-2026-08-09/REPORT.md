# Art antérieur — `automation_score.py` contre `eslint-plugin-playwright`

**Date** 2026-08-09 · Découvert par une recherche de cibles, pas par une recherche d'art antérieur —
ce qui est en soi le constat.

## La question

Une recherche de dépôts à scanner a remonté [`mskelton/eslint-plugin-playwright`](https://github.com/mskelton/eslint-plugin-playwright)
(390★, MIT, maintenu, dernier push 2026-08-04) avec cette remarque :

> Ses règles recouvrent `automation_score.py` presque règle pour règle. À traiter comme un oracle
> à confronter, pas comme une cible à scanner — c'est la réponse à *« cet outil a-t-il réinventé
> un problème résolu, en moins bien ? »*

**59 règles publiées.** Voici la confrontation, faite en listant les leurs avant de regarder les
nôtres.

## Ce que nous avons réinventé

| Notre règle | La leur | Verdict |
|---|---|---|
| `test-without-assertion` | `expect-expect` | **réinventée** — et la leur est configurable par nom d'assertion, ce qui règle nativement le défaut 6 (vérification déléguée) qui nous a coûté 38 constats faux |
| `forbidden-wait` (`waitForTimeout`) | `no-wait-for-timeout` | **réinventée** |
| `forbidden-wait` (`networkidle`) | `no-networkidle` | **réinventée** |
| `fragile-selector` | `no-raw-locators` + `prefer-native-locators` + `prefer-locator` | **réinventée**, et en trois règles plus fines que la nôtre |
| `hollow-assertion` | `no-unnecessary-assertions` + `valid-expect` | **réinventée** |
| `single-sided-evidence` | `no-useless-not` | **partiellement** — la leur vise une assertion, la nôtre vise l'ensemble des assertions d'un test. Nuance réelle mais étroite |
| tests sous un garde `count() > 0` *(trouvé à la main sur TheCyberHub)* | `no-conditional-in-test` | **elle existait déjà** — nous l'avons trouvée à l'œil, eux l'ont outillée |
| `empty-test-body` | `no-commented-out-tests` | **proche**, pas identique |
| tags de traçabilité | `require-tags` + `valid-test-tags` | **réinventée** |

**Huit de nos douze règles statiques existent déjà**, dans un greffon maintenu, testé, installable
en une ligne, et que n'importe quelle équipe Playwright a probablement déjà.

Et le détail qui pique : **`expect-expect` accepte une liste de noms d'assertion**. Le défaut 6 —
« la vérification déléguée à un page object ne compte pas », 38 constats faux, deux correctifs
successifs en une journée — est un paramètre de configuration chez eux depuis des années.

## Ce qui reste réellement à nous

Trois choses, et elles ne sont pas dans les 59 :

**1. La piste de mutation.** Inverser la valeur attendue de chaque assertion, rejouer le test, et
exiger qu'il passe au rouge. **ESLint ne peut pas faire ça** — il est statique par construction. Une
assertion qui survit à son inversion est décorative, et c'est le seul de nos contrôles qui prouve
qu'un test *peut échouer* plutôt qu'il *ressemble à un test*.

**2. La traçabilité vers un cahier de test.** `flag-dropped` (un scénario reposant sur une question
ouverte dont le test ne porte aucune trace), `test-without-scenario`, `scenario-without-test`. Ces
règles exigent un artefact d'exigence en face du code. Un linter généraliste n'a pas cet artefact,
et ne peut pas l'avoir.

**3. Le mode tiers.** Exclure du barème les dimensions qui encodent nos propres conventions plutôt
que de les noter zéro. C'est une décision de mesure, pas une règle.

## Ce que ça change

**Le suivi.** Un utilisateur Playwright qui installe `eslint-plugin-playwright` obtient huit de nos
douze règles, mieux implémentées, dans son éditeur, à chaque frappe. Nous les lui redonnons dans un
script Python qu'il doit lancer à la main.

**Donc la proposition de valeur du volet statique n'est pas « nous trouvons ces défauts ».** C'est,
au mieux, « nous les trouvons **en les rattachant à une exigence** » — ce qui est vrai, et beaucoup
plus étroit que ce que le dépôt laisse croire.

**Et la campagne de 62 dépôts prend un autre sens.** Elle a produit 91 constats faux contre 2
réels — mais la moitié des règles qui les ont produits existaient déjà ailleurs, avec des années de
faux positifs déjà essuyés par quelqu'un d'autre. Nous avons repayé ce coût, seuls, en une journée.

## Ce qu'il faudrait faire, et que je ne fais pas ici

**Ne pas supprimer le volet statique** : il alimente la piste de mutation et le score, et il tourne
sans dépendance Node. Mais **cesser de le présenter comme la valeur**, et le dire dans le README de
`qaia-score`.

**Mesurer avant de décider.** Passer les deux outils sur le même corpus — les 62 dépôts sont encore
partiellement sur disque — et compter qui trouve quoi. Si `eslint-plugin-playwright` trouve nos huit
règles avec moins de faux positifs, la conclusion s'impose d'elle-même. **Cette mesure n'a pas été
faite ; rien ici ne la remplace.**

## Comment ce constat est arrivé, et pourquoi c'est le vrai sujet

Il n'est pas sorti d'une recherche d'art antérieur. Il est sorti d'une recherche de **cibles à
scanner**, où un agent a remarqué au passage que la cible ressemblait beaucoup à l'outil.

Le projet a écrit douze règles statiques, découvert neuf défauts dedans, construit deux
auto-contrôles et mené une campagne de 62 dépôts — **sans jamais chercher si le problème était
résolu**. Quinze jours d'existence, et la question n'a jamais été posée.
