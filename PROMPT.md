# Prompt — QAIA : plateforme QA agentic open source

> Prompt fondateur du projet, **gardé tel qu'il a été écrit en juillet 2026**. Les décisions actées en discovery sont dans `docs/DECISIONS.md` (gelé depuis le 2026-11-23).
>
> **Ce qui a changé depuis, et qui l'emporte sur ce texte** :
> - la niche « logiciel médical / environnements réglementés » (§3) a été retirée (D114) : QAIA ne cartographie aucun référentiel réglementaire ;
> - le parcours en neuf étapes (§4) n'est plus une suite de skills : c'est une seule skill, `generate`, dont chaque étape est une page ; la construction du RAG et le mode feedback (étapes 4 et 9) ont été supprimés le 2026-10-26, faute d'avoir jamais été exercés par une vraie correction ;
> - « autant d'agents que nécessaire » (§3) a donné 37 skills, ramenées à 4 par la [refonte du 2026-08-24](docs/superpowers/specs/2026-08-24-qaia-refonte-design.md) ; performance, sécurité et accessibilité ont été retirées du produit ;
> - l'ordre des travaux est dans [`docs/ROADMAP.md`](docs/ROADMAP.md), l'état dans [`docs/STATUS.md`](docs/STATUS.md).

---

## 1. Qui je suis

Je suis **Cédric Moretti**, ancien directeur QA dans l'édition de logiciels de santé.

Dans une vie précédente, j'ai conçu et lancé en interne, avec une équipe de testeurs volontaires, une plateforme agentic de génération de tests construite **avec et pour les testeurs**. L'objectif : faire performer les testeurs grâce à l'IA, développer les pratiques **Shift-Left / Shift-Right**, retirer le répétitif et valoriser le jugement humain.

Cette expérience a montré qu'une chaîne complète est possible : de l'US au test automatisé, avec une base de connaissance métier (RAG), des gates qualité, une traçabilité réglementaire de bout en bout (contexte dispositif médical), un référentiel de contrôle hebdomadaire et une dette de test suivie — le tout piloté par des indicateurs d'adoption, de durée et de coût. Un cahier de test complet se génère en quelques minutes pour un coût token très faible.

Je ne suis plus sur ce projet. Je crée aujourd'hui un projet **entièrement nouveau et open source**, réécrit de zéro (clean-room), en capitalisant uniquement sur les leçons de méthode.

**Important : je ne sais pas coder.** Tout le projet sera réalisé en vibe-coding guidé — les livrables, la documentation et le processus doivent être pensés pour ça.

---

## 2. Les leçons de l'expérience précédente (principes non négociables)

1. **Outils d'abord, pipelines ensuite.** L'erreur classique est de vouloir scripter un maximum de choses. Ici, on commence par mettre à disposition une **boîte à outils : des skills et des commandes, empaquetées dans des plugins**. Les workflows orchestrés viendront après, composés à partir de ces briques.
2. **Public inconnu = standards de l'industrie.** Le projet étant open source, on ne sait pas qui l'utilisera. Il faut donc capitaliser sur un **maximum de connecteurs aux standards du marché** (gestion d'exigences, ALM, référentiels de test, CI/CD) — introduits progressivement, jamais avant que le cœur soit éprouvé.

---

## 3. Contraintes fortes

| Contrainte | Détail |
|---|---|
| **Distribution** | 100 % skills + commandes dans des plugins. **Aucune clé API embarquée** : tout s'exécute dans la session Claude de l'utilisateur. |
| **Format des tests** | Cahier de test en **Gherkin** (mots-clés anglais), scénarios strictement **atomiques** (1 scénario = 1 comportement vérifiable), IDs stables par scénario. Tests automatisés en **Playwright natif**, chaque test référençant l'ID de son scénario (décision D5 — pas de couche Cucumber). |
| **Automatisation** | **100 % Playwright**, en s'appuyant au maximum sur les **agents Playwright** (Playwright MCP). Positionnement **web-first** assumé. |
| **Couverture cible** | E2E, Mobile (émulation navigateur), API, Performance (via plugin), Sécurité, Accessibilité. |
| **Agents** | Autant d'agents que nécessaire, pattern **ReAct** (raisonnement + action + observation). |
| **Méthode de test** | Techniques **ISTQB** (partitions d'équivalence, valeurs limites, tables de décision, transitions d'état, tests basés sur le risque… — cf. syllabus), justifiées dans le cahier. |
| **Positionnement** | Niche v1 : **logiciel médical / environnements réglementés** (traçabilité exigence→test soignée), ouvert à toute la QA. |
| **Cible** | **Équipe QA** : RAG et conventions partagés via git. |
| **Hébergement** | **GitHub** (organisation dédiée) : Projects (Kanban), Issues (backlog), Actions (CI), Discussions (communauté), serveur MCP GitHub. Licence **MIT**. Bilingue **FR/EN**. |

---

## 4. Parcours utilisateur attendu (mode conversationnel)

L'outil dialogue avec le testeur et valide chaque étape avec lui, avec un **checkpoint fichier** entre chaque étape (reprise possible dans une nouvelle session) :

1. **Ingestion** — récupération de l'US (ou de tout autre type de document : spéc, ticket, page web) ; l'utilisateur **valide** que la source récupérée est la bonne.
2. **Contrôle du scraping** — vérification que le contenu a été correctement extrait et pris en compte.
3. **Compréhension du besoin** — reformulation, détection des ambiguïtés, questions à l'utilisateur.
4. **Construction du RAG** — constitution/enrichissement d'une base de connaissance projet (métier, règles, historique), partagée par l'équipe via git.
5. **Techniques de test ISTQB** — choix et application des techniques adaptées, justifiées.
6. **Priorisation** — gestion des priorités (risque, criticité métier) ; l'outil propose, l'humain arbitre.
7. **Génération du cahier de test** — en Gherkin atomique avec IDs stables ; l'utilisateur peut **récupérer le cahier pour le retravailler** (export éditable), et le **régénérer sans perdre ses retouches** quand l'US évolue.
8. **Reporting** — production de rapports et mise à disposition du cahier de test.
9. **Feedback** — un mode feedback permet à l'outil **d'apprendre** des corrections de l'utilisateur (enrichissement du RAG et des exemples des skills).

Ensuite, chantier d'**automatisation** : transformation des scénarios Gherkin en tests Playwright natifs (E2E, mobile-web, API), puis extension perf / sécurité / accessibilité.

---

## 5. Ce que j'attends de toi (l'agent)

1. **Discovery d'abord** : pose-moi **toutes** les questions nécessaires. Challenge mes hypothèses, cherche la petite bête — je préfère un désaccord argumenté qu'une validation polie.
2. Puis produis :
   - une **phase de discovery** structurée (questions, ateliers, livrables),
   - une **phase de delivery** (roadmap par incréments, avec critères de sortie),
   - un **découpage projet en Kanban** avec une liste de tâches **priorisées**,
   - un **backlog vivant** : possibilité d'ajouter des tâches et de les **challenger** (valeur/effort/risque).
3. Dis-moi **quels skills et plugins installer** pour travailler.
4. Utilise **toute la puissance de l'agentic** : sous-agents, workflows parallèles, revues croisées multi-personas.
