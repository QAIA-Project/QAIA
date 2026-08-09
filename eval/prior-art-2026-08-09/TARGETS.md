# Cibles retenues pour les prochaines campagnes

Issu d'une recherche en profondeur (GitHub, GitLab, Codeberg, SourceHut) le 2026-08-09.

## Impasses, dites en premier

- **GitLab** : la recherche de **code** exige Advanced Search, fermée sans compte — mais ce n'est pas la seule porte, et la conclusion « inutilisable » était trop rapide.

  **Un chemin de découverte fonctionne en anonyme**, testé le 2026-08-09 : `GET /projects?topic=<sujet>` puis `GET /projects/<id>/repository/tree?path=<dir>`. On cherche par **sujet et par arborescence** au lieu de chercher par contenu.

  Résultat après avoir balayé les sujets `playwright`, `cypress`, `test-automation`, `e2e-testing`, `testing` — **101 projets distincts** :

  | | |
  |---|---|
  | suites Playwright substantielles | **aucune** |
  | ce qu'on trouve à la place | des outils de test Python, Ruby, Crystal (`expliot`, `spectator`, `plom`, `fabrication`) |
  | la seule cible réelle | `gitlab-org/gitlab-ui` — `cypress/e2e` confirmé dans l'arborescence, 232★ |
  | `gitlab-org/gitlab` lui-même | `qa/` est Ruby (`gems`, `knapsack`, `allure`) — Capybara, hors de portée de l'outil |

  **Donc : la porte s'ouvre, et la pièce est vide.** C'est une conclusion plus forte que « inutilisable », parce qu'elle a été vérifiée au lieu d'être déduite d'un 401.
- **Codeberg** : renvoie du texte généré aux agents, avec la bannière *« si vous êtes un scraper IA, arrêtez de visiter Codeberg »*.
- **SourceHut** : aucun point d'entrée de recherche de code.
- **SourceForge** : testé le 2026-08-09 en réponse à la question directe. La recherche fonctionne et la population n'y est pas — **zéro projet** sur `playwright`, un seul sur « end-to-end testing », et les langages dominants sont Java, Python et C++. SourceForge héberge une autre époque du logiciel ; les suites e2e JavaScript modernes n'y sont pas.

**L'hypothèse « autre hébergeur = autre population » n'est pas testable avec les accès disponibles** — et là où elle l'est, la population n'existe pas. C'est un résultat, pas un échec.

### Sur Codeberg, et pourquoi on n'y retourne pas par un navigateur

La bannière de Codeberg est une **demande explicite de l'exploitant** adressée aux agents automatiques. Y accéder par un navigateur piloté pour la contourner, c'est faire exactement ce qu'ils ont demandé qu'on ne fasse pas — même catégorie que forcer un `robots.txt`.

Et c'est sans objet : **leur API publique fonctionne et a été utilisée** — c'est le chemin sanctionné. Elle rend un premier dépôt Playwright à **3 étoiles**. Il n'y a rien derrière la porte qu'on envisagerait de forcer.

## La correction que cette recherche impose

**Les 62 dépôts déjà scannés viennent tous d'une seule recherche de code GitHub, et sont tous petits ou amateurs.** Aucun n'est un outil de test, une suite de conformité, ou un projet à spécification publiée.

Les 2 % de précision mesurés sont donc **en partie une propriété de cet échantillonnage**, pas seulement de l'outil. Le chiffre a été publié comme un jugement sur l'outil ; il est aussi un jugement sur la façon dont les cibles ont été choisies.

## Les trois qui répondent à une question plutôt que de chasser des bugs

| Cible | ★ | La question qu'elle tranche |
|---|---:|---|
| [`evcc-io/evcc`](https://github.com/evcc-io/evcc) | 7 060 | La forme RealWorld — OpenAPI + suite dans le même dépôt — mais **8× la taille** (97 fichiers de spec), backend Go, et des fixtures YAML/SQL par test qui mettent l'étape *arrange* **hors** du fichier de spec. C'est la moitié non testée du correctif du défaut 6. |
| [`microsoft/playwright`](https://github.com/microsoft/playwright) `tests/playwright-test/` | 94 238 | Construit **par conception** de corps vides délibérés, d'assertions qui doivent échouer et de `test.fixme` volontaires. Le défaut 8 a été trouvé sur deux dépôts amateurs ; **ce dépôt dira en une exécution s'il a été corrigé pour sa classe ou pour son instance.** |
| [`cypress-io/cypress-example-kitchensink`](https://github.com/cypress-io/cypress-example-kitchensink) | 1 246 | Catalogue exhaustif de Cypress, dont le modèle porte l'assertion **dans la chaîne** (`cy.get().should()`), sans jamais un `expect(`. Si l'outil rapporte « test sans assertion » sur les 20 fichiers, la réponse à « dégrade-t-il proprement ? » est **non**, sans ambiguïté. |

## Les autres, par catégorie

**Spécification + suite de conformité** : `n8n-io/n8n` (et son propre linter de qualité de suite, avec fichier de référence — un adversaire direct), `graphql/graphql-http`, `apollographql/apollo-federation-subgraph-compatibility`, `cucumber/compatibility-kit`, `BerriAI/litellm`.

**La suite est le produit** : `serenity-js/serenity-js` (le patron Screenplay met **toute** assertion derrière `actor.attemptsTo(Ensure.that(...))` — la délégation poussée à sa limite), `checkly/checkly-cli`, `mswjs/msw`, `storybookjs/storybook`, `allure-framework/allure-js`.

**Autres styles** : `cypress-io/cypress-realworld-app`, `webdriverio/webdriverio`, `DevExpress/testcafe`, `puppeteer/puppeteer`, et surtout **`dequelabs/axe-core-npm`** — les mêmes assertions d'accessibilité implémentées contre Playwright, Puppeteer, WebdriverIO et Selenium **dans un seul dépôt**, donc les différences de sortie sont imputables au style seul.

**GitLab** : `gitlab-org/gitlab-ui` (232★, Cypress) est le seul atteignable. `gitlab-org/gitlab` lui-même est en Ruby/Capybara, hors de portée de l'outil.

## Écartées après vérification, pour ne pas les re-trouver

`tastejs/todomvc` (runner maison, 1 fichier), `krausest/js-framework-benchmark` (aucun bloc `test()`), `qawolf` (**issues désactivées**), `matrix-org/matrix-react-sdk` (archivé), `web-platform-tests/wpt` / `tc39/test262` / `JSON-Schema-Test-Suite` (forme parfaite, mais harnais maison sans surface Playwright — l'outil n'y produirait **rien**, pas du non-sens, donc ils n'enseignent rien).
