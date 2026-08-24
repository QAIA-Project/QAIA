# Ce que QAIA couvre du métier de test, et ce qu'elle ne couvre pas (2026-08-08)

Établi en cartographiant les **skills réellement présentes** dans `plugins/` — 30 le matin du
2026-08-08, **35** le soir, les cinq ajoutées étant précisément cinq trous de cette carte — contre le
processus de test ISTQB (CTFL ch. 1 et 5), les **niveaux** de test (ch. 2.2) et les **types** de
test (ch. 2.3). Aucune case n'est cochée sur une intention : une case est verte quand une skill
existe et porte le sujet.

## 1. Le processus de test

| Phase ISTQB | Couverture | Skills |
|---|---|---|
| Planification | **couverte** | `test-plan-and-closure` — dérivé des artefacts, jamais d'un gabarit |
| Pilotage et contrôle | partielle | `report`, `run-report`, `aptitude-gate` |
| Analyse | **couverte** | `us-ingest`, `openapi-ingest`, `us-review`, `need-understanding`, `istqb-design` |
| Conception | **couverte** | `istqb-design`, `testbook-generate`, `oracle-generate`, `prioritize` |
| Implémentation | **couverte** | `automate`, `dataset-generate` |
| Exécution | **couverte** | `automate`, `a11y-audit`, `perf-check`, `visual-check`, `security-surface` |
| Clôture | **couverte** | `test-plan-and-closure` + `report` — le bilan nomme d'abord ce qui reste ouvert |

**Le trou le plus visible était aux deux bouts** — QAIA commençait à la user story et s'arrêtait
au rapport d'exécution, alors qu'un responsable de test commence par un **plan** et finit par un
**bilan**. `test-plan-and-closure` couvre les deux depuis le 2026-08-08, avec une réserve qui
compte : **seule la moitié « bilan » a été appliquée pour de vrai**, sur une campagne déjà
terminée. La moitié « plan » n'a encore jamais servi.

## 2. Les niveaux de test

| Niveau | Couverture | Commentaire |
|---|---|---|
| Composant (unitaire) | **hors périmètre, décidé** | [ADR 0004](adr/0004-test-level-boundary.md) : QAIA part d'une promesse observable de l'extérieur. Un test unitaire s'écrit contre une fonction, donc contre l'implémentation — c'est abandonner l'oracle qui fait la valeur du reste. |
| Intégration | **absente en tant que telle** | `contract-probe` en approche une partie par le contrat, sans jamais nommer l'intégration |
| Système | **couverte** | c'est le cœur du produit |
| Acceptation | partielle | on produit le cahier ; personne ne pilote une recette humaine |

## 3. Les types de test

| Type | Couverture | Skills |
|---|---|---|
| Fonctionnel | **couvert** | toute la chaîne |
| Performance | partiel | `perf-check` (budgets de latence, CT-PT) — pas de charge réelle |
| Sécurité | partiel | `security-surface` (passif, CT-SEC) |
| Accessibilité | **couvert** | `a11y-audit` (WCAG 2 A/AA) |
| Utilisabilité | **couvert** | `usability-heuristic-review` (CT-UT) |
| Visuel | **couvert** | `visual-check` |
| Compatibilité (navigateurs, appareils) | **couvert, sans skill dédiée** | `automate` → `references/compatibility-selection.md`. La mécanique existe nativement dans Playwright ; ce qui manquait était le **choix** de ce qu'on rejoue |
| Structurel (boîte blanche, couverture de code) | **absente** | aucune skill ne part de la couverture |
| Confirmation (re-test après correction) | **couvert** | `confirm-fix` — trois verdicts, et le troisième jamais rapporté comme le premier |
| Régression | **couvert** | `traffic-replay`, `flaky-detect`, `impact-select` (depuis un diff) |

## 3bis. Le cycle de vie produit — Discovery / Delivery / Run

Les sections 1 à 3 croisent le catalogue avec le **processus de test ISTQB**. Elles ne disent rien
d'une autre question, posée le 2026-08-08 : *à chaque étape du cycle il y a une activité de test —
est-ce qu'on la couvre ?*

Le SDLC canonique compte **sept phases** (planification, analyse des besoins, conception,
implémentation, test, déploiement, maintenance), et le modèle produit les regroupe en
**Discovery / Delivery / Run**. Le Run, c'est le *shift-right* : tests en production, monitoring
synthétique, chaos, A/B — l'observabilité y étant traitée comme une extension du test, pas comme
un sujet d'exploitation.

| Phase | L'activité de test qui s'y joue | Couverture |
|---|---|---|
| **Discovery** | besoins, faisabilité, **définition des exigences non-fonctionnelles** | **faible** |
| Delivery — conception | stratégie, techniques, risque | **forte** |
| Delivery — implémentation | revue de code, analyse statique, unitaire | **absente** |
| Delivery — test système | fonctionnel et non-fonctionnel | **forte — le cœur** |
| Delivery — déploiement | smoke, prêt-à-livrer, rollback | partielle (`aptitude-gate`) |
| **Run** | monitoring synthétique, chaos, incident → test, A/B | **quasi absente** |
| Maintenance | régression, impact, santé de la suite | **forte** |

**QAIA vit entièrement dans Delivery et Maintenance.** Elle commence quand la discovery est finie
et s'arrête quand le déploiement commence.

**Arbitré le 2026-08-08, puis retourné le même jour : Discovery et Run sont HORS PÉRIMÈTRE**
([ADR 0007](adr/0007-scope-delivery-and-maintenance.md), qui remplace
[ADR 0005](adr/0005-scope-discovery-and-run.md)). Ce ne sont donc ni des trous, ni des chantiers :
ce sont des frontières. Les issues ouvertes par ADR 0005 sont fermées — [#85](https://github.com/QAIA-Project/QAIA/issues/85) (exigences non-fonctionnelles dérivées quand elles sont encore négociables), [#86](https://github.com/QAIA-Project/QAIA/issues/86) (incident de production → test de non-régression), [#87](https://github.com/QAIA-Project/QAIA/issues/87) (chaos, différé et argumenté).

Deux précisions qui corrigent une lecture trop favorable :

- **Discovery.** `us-ingest` et `need-understanding` prennent une user story **déjà écrite** : on
  ingère le *produit* de la discovery, on ne la fait pas. Et c'est là que se définissent les
  exigences non-fonctionnelles — or nos skills de performance et de sécurité s'exécutent contre une
  application qui tourne. **Aucune ne dérive une exigence au moment où elle serait encore
  négociable.**
- **Run.** `traffic-replay` rejoue un fichier HAR que l'utilisateur fournit. Ce n'est pas du
  monitoring de production. Sur les quatre pratiques du shift-right, la couverture est de **zéro**.

Et une nuance sur notre propre décision : [ADR 0004](adr/0004-test-level-boundary.md) exclut le
**niveau** unitaire, pas le **test statique**. La revue de code contre l'exigence part du même
oracle que le reste de la chaîne — elle n'est ni couverte, ni interdite.

## 3ter. Les outils, face aux leaders du marché

L'architecture d'automatisation est un **Page Object Model exposé en fixtures Playwright** (pas un
POM par héritage), et ce n'est pas déclaratif : `automation-score` refuse une suite dont le dossier
`pages/` est absent.

| Type | Ce que QAIA génère | Leaders du marché | Verdict |
|---|---|---|---|
| E2E | Playwright (JS) | Playwright, Cypress, Selenium | un sur trois |
| API | `request` de Playwright | Postman/Newman, REST Assured, Karate | **aucun leader** |
| Performance | **script k6 réel** + variante légère | k6, JMeter, Gatling | **le leader OSS** |
| Sécurité | passif + **baseline OWASP ZAP** en option | ZAP, Burp, Snyk | partiel, bon outil |
| Accessibilité | **axe-core** | axe-core, Pa11y, Lighthouse | **le standard** |
| Visuel | snapshots Playwright | Applitools, Percy | pas de moteur perceptuel |
| Chaos | — | Gremlin, Litmus, Toxiproxy | **rien, nulle part** |
| Contrat | sonde HTTP maison | **Pact**, Spring Cloud Contract | aucun standard |

Trois catégories sont au niveau du marché : performance, accessibilité, sécurité passive. Trois
passent toutes par Playwright — défendable en E2E, **beaucoup moins en API**, où personne ne teste
sérieusement avec `request` quand Karate ou REST Assured existent. Deux sont vides.

*(Vérification faite en cherchant `Pact` dans le dépôt : les premières occurrences étaient le mot
**impact**. Il n'y a aucun support Pact, et il s'en est fallu d'un `grep` mal écrit pour l'annoncer.)*

## 4. Les trous, classés par ce qu'ils coûtent à un vrai utilisateur

**1. ~~Le rapport de défaut.~~** **Comblé le 2026-08-08** — `qaia-playwright:defect-report`,
éprouvée contre un ticket écrit par un humain sur le même défaut
([#1551](https://github.com/typicode/json-server/issues/1551)). Aucun des deux rapports ne domine :
l'humain gagne sur la cause parce qu'il a lu le code, la machine sur la reproduction et la
traçabilité.

**2. ~~La sélection des tests à partir d'un diff.~~** **Comblé le 2026-08-08** —
`qaia-playwright:impact-select`, avec sa mesure : sur une faute injectée pour de vrai dans
`examples/expense-demo`, la lecture naïve rate **6 impacts sur 10** et la lecture transitive n'en
rate aucun (`eval/impact-select-2026-08-08/`).

**3. ~~OpenAPI / Swagger comme source d'exigence.~~** **Comblé le 2026-08-08** —
`qaia-core:openapi-ingest`, deuxième porte d'entrée de la chaîne. Appliquée à une vraie
spécification, elle y a trouvé **les quatre classes de contradiction** qu'elle cherche
(`eval/openapi-ingest-2026-08-08/`).

**4. ~~Le niveau composant.~~** Tranché le 2026-08-08 : hors périmètre, [ADR 0004](adr/0004-test-level-boundary.md). Ce n'est plus un trou, c'est une frontière déclarée.

**5. ~~Le plan de test et le bilan.~~** **Comblé le 2026-08-08** — `test-plan-and-closure`, appliquée à une campagne *déjà terminée* pour qu'aucune section ne puisse être ajustée pour bien paraître (`eval/external-application-2026-08-08/closure-report.md`). *(Le test de confirmation, qui figurait aussi dans cette liste, est comblé : `confirm-fix`.)*

**6. ~~L'anonymisation de données réelles.~~** **Écartée le 2026-08-08** ([#81](https://github.com/QAIA-Project/QAIA/issues/81)),
et c'est une frontière, pas un trou. Le critère est la **vérifiabilité**, pas la difficulté : toutes
les autres skills produisent quelque chose qu'un tiers peut recouper, alors qu'une anonymisation ne
se vérifie qu'en tentant de ré-identifier — ce qui demande le jeu d'origine, des données
auxiliaires et une méthode, dont QAIA ne dispose d'aucun. Une skill qui anonymise mal est pire
qu'aucune skill : elle donne la confiance sans la propriété.

**7. ~~Compatibilité navigateurs et appareils.~~** **Traité le 2026-08-08 — et délibérément sans
skill nouvelle.** Multiplier une suite par un tableau de navigateurs est une ligne de
configuration, pas une compétence ; la compétence est de choisir quoi rejouer. C'est donc une note
de raisonnement dans `automate`, pas une 36ᵉ entrée au catalogue.

## 5. Ce que cette carte ne dit pas

Elle mesure la **présence** d'une skill, pas sa **qualité**. Une case verte veut dire « le sujet
est porté », pas « c'est bien fait ». Sur les 37 skills du 2026-08-11 (le dépôt en compte 33
depuis la fusion du 2026-08-24), **cinq** ont été exercées sur un logiciel
ou un document que nous n'avons pas écrit — `automate`, `defect-report` et `confirm-fix` sur
json-server, `openapi-ingest` sur la spécification Petstore, `test-plan-and-closure` sur le bilan
de la campagne — et **aucune n'a jamais été utilisée par un humain dans son travail réel**. C'est
toujours l'inconnue n°1, et cinq skills de plus n'y changent rien.
