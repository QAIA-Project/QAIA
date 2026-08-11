# site-qa — QAIA appliquée au site de QAIA

Le parcours complet, exécuté sur notre propre vitrine : une user story, sept critères
d'acceptation, quatorze conditions réparties sur **deux niveaux**, un cahier Gherkin, sa
projection en langage naturel, une suite Playwright à deux projets, et **un défaut réel trouvé
au premier passage**.

## Pourquoi ce dossier n'est pas dans `site/`

`.github/workflows/pages.yml` copie **tout** `site/` vers la racine publiée. Y déposer un
`node_modules` de test aurait publié des milliers de fichiers tiers sans que personne ne le
décide. Les artefacts QA vivent donc à côté, et `site/` reste exactement ce qui est en ligne.

## Ce qui a été trouvé

| | |
|---|---|
| Premier passage | **26 tests, 1 échec** — `evidence/junit-run-1-red.xml` |
| Le défaut | `/walkthrough.html`, **la page la plus persuasive du site**, ne portait le statut pré-alpha nulle part. Les deux autres pages, oui. |
| Après correction | **26 tests, 0 échec** — `evidence/junit-run-2-green.xml` |

Rapport complet, avec sa reproduction minimale et l'argumentaire de sévérité :
[`defect-001`](qaia-journey/reports/US-SITE-001/defect-001-walkthrough-omits-pre-alpha.md).

**Le troisième verdict a été vérifié, pas supposé.** `confirm-fix` impose de distinguer *corrigé*,
*toujours ouvert*, et *corrigé mais autre chose a cassé*. Les 25 tests qui passaient avant passent
toujours : la correction n'a rien emporté avec elle. C'est vérifié dans le second JUnit, pas
déduit du fait que le test visé est devenu vert.

**Ce que ce défaut dit du dispositif** : le site avait été relu plusieurs fois, par plusieurs
revues, et personne ne l'avait vu — parce que **personne ne lit trois pages en se demandant ce qui
est vrai sur les trois**. Et le cahier l'a trouvé parce qu'un critère d'acceptation disait
« chaque page ». Ce n'est pas l'outil qui a été malin, c'est l'exigence qui a été écrite.

## Les deux niveaux, décidés à la conception

[ADR 0008](../docs/adr/0008-test-level-is-a-design-property.md) : le niveau est une propriété de
la condition. Ici il se lit sans effort et c'est ce qui le rend démonstratif.

| Niveau | Conditions | Ce que ça vérifie |
|---|---|---|
| `api` (15 cas) | C1-C7 | statuts HTTP, types de contenu, `robots.txt` → `sitemap.xml`, **le sitemap liste exactement l'ensemble publié**, `/demo/` servi depuis la seconde source d'assemblage |
| `e2e` (11 cas) | C8-C14 | première fenêtre, statut pré-alpha sur chaque page, bloc d'installation copiable, ancres de navigation, langue déclarée, titres distincts |

Le projet Playwright `api` est déclaré **sans moteur de navigateur** : aucune de ces promesses ne
change selon le moteur de rendu.

## Le cahier, dans les deux formes

- **Gherkin** : [`landing-and-navigation.feature`](qaia-journey/testbooks/US-SITE-001/landing-and-navigation.feature) · [`published-contract.feature`](qaia-journey/testbooks/US-SITE-001/published-contract.feature)
- **Langage naturel** : [`testbook.en.md`](qaia-journey/testbooks/US-SITE-001/testbook.en.md) — mêmes 26 cas, `Preconditions / Action / Expected result`, étiquettes en mots, `Scenario Outline` éclatés avec leurs valeurs.

`eval/tools/check_nl_projection.py` compare les deux **étape par étape** : une seule divergence
fait échouer la CI. Le rendu n'est pas une reformulation, c'est une projection contrôlée.

## Le relancer

```bash
cd site-qa/tests && npm install && npx playwright test
```

Le serveur (`serve.js`) assemble `_site` comme le fait le workflow Pages : `site/` à la racine,
`examples/expense-demo/static-demo/` sous `/demo/`. **C'est une duplication de règle assumée** —
on ne peut pas appeler un workflow depuis un test. Ce qui la garde honnête est le scénario
`QAIA-US-SITE-001-004` : si les deux assemblages cessent de coïncider, le sitemap et l'ensemble
publié divergent, et le test le dit.

## Les trois questions ouvertes, non tranchées

1. **« Sans faire défiler » n'a pas de définition.** Défaut sûr : 1280×720. Le scénario qui en
   dépend porte `@low-confidence`.
2. **Quels fichiers comptent comme « points d'entrée publiés » ?** Défaut sûr : les pages HTML de
   premier niveau plus `/demo/` ; `robots.txt`, `sitemap.xml` et `llms.txt` ne s'indexent pas.
3. **Les liens externes.** Hors périmètre **par décision**, pas par oubli : un lien qui répond 403
   à un robot et 200 à un humain est un vrai sujet, pas une case à cocher.

## Ce que cette campagne ne prouve pas

Que le site convertit. Aucun scénario ne mesure si un visiteur installe QAIA après l'avoir lu —
c'est la seule question qui compte pour cette page, et elle demande des visiteurs, pas des tests.
