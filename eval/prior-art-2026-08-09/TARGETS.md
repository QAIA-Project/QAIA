# Cibles retenues pour les prochaines campagnes

Issu d'une recherche en profondeur (GitHub, GitLab, Codeberg, SourceHut) le 2026-08-09.

## Impasses, dites en premier

- **GitLab** : la recherche de code exige Advanced Search, non exposée sans compte. La recherche par nom plafonne à 17 étoiles. Inutilisable pour la découverte.
- **Codeberg** : renvoie du texte généré aux agents, avec la bannière *« si vous êtes un scraper IA, arrêtez de visiter Codeberg »*.
- **SourceHut** : aucun point d'entrée de recherche de code.

**L'hypothèse « autre hébergeur = autre population » n'est pas testable avec les accès disponibles.** C'est un résultat.

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
