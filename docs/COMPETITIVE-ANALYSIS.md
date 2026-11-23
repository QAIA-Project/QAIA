# Veille concurrentielle — QAIA (2026-07-25)

> **Ce document est un journal de veille : chaque section porte sa date et décrit QAIA tel qu'il
> était ce jour-là.** Depuis, la [refonte du 2026-08-24](superpowers/specs/2026-08-24-qaia-refonte-design.md)
> a changé le produit ; là où une section datée dit autre chose, ceci l'emporte (état au
> 2026-11-23) :
>
> - **4 skills, 3 plugins** (`generate` ; `automate`, `probe` ; `judge`), pas 23, 30 ou 37 ; trois
>   commandes d'installation, pas quatre. Accessibilité, sécurité, performance, utilisabilité et
>   régression visuelle ont quitté le produit le 2026-10-26.
> - **Pas « 100 % Markdown »** : depuis le 2026-08-09, `qaia-score` livre ses scoreurs en Python
>   lisible et épinglé, qui ne s'exécute que lorsque l'utilisateur invoque `judge`. Rien ne
>   s'exécute à l'installation ; aucun hook, agent ou serveur MCP.
> - **Le coût** (~2,9× un prompt direct) a été mesuré sur le parcours à six skills, avant la
>   fusion ; il n'a pas été remesuré ([#96](https://github.com/QAIA-Project/QAIA/issues/96)).
> - **Toujours 0 étoile et 0 pilote** ([`STATUS.md`](STATUS.md)).

Demande fondateur (D67, mandat élargi post-M0) : regarder ce qui existe déjà sur le marché
dans l'espace "IA agentic pour le test logiciel" avant de remodeler le backlog. Recherche web
réelle (WebSearch/WebFetch, ~10 sources), pas de mémoire — le terrain évolue vite.

**Limites assumées** : plusieurs sources sont des articles de blog marketing (TestQuality,
Shiplight AI, QASkills.sh, Agensi.io) dont l'indépendance éditoriale n'est pas vérifiée — à
lire comme indicatif, pas comme benchmark neutre.

**Vérification (2026-07-25, sprint 20)** : le chiffre `~421★` cité pour `agentic-qe` avait été
noté comme non revérifié avant citation publique (`README.md` le cite). Re-fetch direct de
`github.com/proffesor-for-testing/agentic-qe` : **421 étoiles, 75 forks, licence MIT confirmée**
— le chiffre initial était exact, pas une fabrication. Fork count (75) ajouté ici car jamais
publié avant.

## Paysage concurrentiel

1. **Agentic QE Fleet** (`proffesor-for-testing/agentic-qe`, MIT, ~421★) — le concurrent le
   plus direct trouvé. Open source, natif Claude Code (+ 11 plateformes dont Cursor, Copilot,
   Cline), génère des tests multi-frameworks (Jest, Playwright, pytest…), inclut un
   générateur BDD, une détection de flaky tests, un "quality-gate" anti-sycophantie (rejette
   les assertions creuses type `expect(true).toBe(true)`), et un orchestrateur "Queen
   Coordinator" à 60 agents spécialisés qui s'exécutent automatiquement. Nécessite une clé
   API LLM (Claude/OpenAI/Gemini/Ollama), avec un mode "free-tier" vers des modèles locaux.
   Auto-enregistre un serveur MCP. Revendique explicitement le shift-left, touche aussi au
   shift-right (load/chaos testing).
2. **TestQuality / TestStory.ai** — SaaS, convertit des user stories en scénarios Gherkin,
   intégration native GitHub/Jira, positionné "agentic QA" vs les "anciens outils IA
   autocomplete".
3. **SaaS IA-natifs établis** (testRigor, Mabl, Functionize, Applitools, ACCELQ, Tricentis
   Tosca) — DSL en anglais courant ou low-code, self-healing de locators, visual AI
   (Applitools), model-based testing (Tosca). Tous SaaS/cloud, pricing $60-300/mois en entrée
   ou vente enterprise.
4. **Frameworks OSS d'automatisation navigateur pilotés par LLM** (BrowserUse, Stagehand,
   Skyvern — AGPL-3.0, Midscene.js, Shortest, Magnitude, Passmark) — tous nécessitent une clé
   API LLM au runtime, "OSS-client-only" : les données transitent vers un fournisseur externe.
   Aucun ne fait de Gherkin/BDD ni de scoring séparé selon la synthèse trouvée.
5. **Écosystème Playwright officiel** — Playwright MCP (Microsoft, open source, primitives de
   navigation) et Playwright Test Agents (planification + génération + réparation de
   sélecteurs), self-hosted, aucun mécanisme de scoring propre.
6. **Marketplaces de skills Claude Code génériques** (QASkills.sh, Agensi.io) — dizaines de
   skills étroits et indépendants (playwright-e2e, vitest, pytest, a11y, k6,
   contract-testing…), sans clé API mentionnée, mais **aucun ne fait Gherkin/BDD depuis des
   US ni de scoring** — des générateurs de tests techniques, pas un parcours métier complet.
7. **Outsourcing managé** (QA Wolf) et **outils API/backend** (Keploy — Apache-2.0, tests
   depuis du trafic réel enregistré ; EvoMaster — LGPL, tests évolutionnaires sans LLM).
8. **ISTQB CT-GenAI** (certification, pas un outil) — cadre normatif "Testing with Generative
   AI" (v1.1, avril 2026) qui légitime les techniques de conception assistées par IA et la
   gestion des risques (hallucination, biais) — un référentiel auquel QAIA pourrait se
   rattacher explicitement.

Sources : [Agentic QE Fleet](https://github.com/proffesor-for-testing/agentic-qe),
[TestQuality — Claude Code pour QA](https://testquality.com/agentic-testing-qa-claude-code/),
[TestQuality — Agentic QA](https://testquality.com/the-shift-to-agentic-qa-beyond-automated-testing-to-autonomous-ai-generation-in-2026/),
[Shiplight — 8 plateformes comparées](https://www.shiplight.ai/blog/best-agentic-qa-tools-2026),
[Autonoma — outils OSS de génération de tests](https://getautonoma.com/blog/open-source-ai-test-generation-tools-2026),
[QASkills.sh](https://qaskills.sh/blog/best-claude-code-skills-for-testing-2026),
[Agensi.io](https://www.agensi.io/learn/best-qa-testing-skills-claude-code-2026),
[ISTQB CT-GenAI](https://istqb.org/istqb-certified-tester-specialist-level-testing-with-generative-ai-ct-genai-press-release/),
[Gherkin guidelines for AI](https://github.com/AutomationPanda/gherkin-guidelines-for-ai).

## Angles morts de QAIA (vérifiés contre `plugins/qaia-*/skills/`)

- **Détection de flaky tests** : absente chez QAIA, présente chez Agentic QE Fleet et évoquée
  comme catégorie de skills chez QASkills.sh.
- **Priorisation risque data-driven** : `prioritize` est un score probabilité×impact arbitré
  par l'humain, sans ingestion automatique d'historique de défauts/changements de code.
- **Génération depuis trafic de production réel** (shift-right "fort", type Keploy) :
  `perf-check`/`security-surface`/`a11y-audit` sont des vérifications actives, pas une
  capture-rejeu de trafic réel.
- **Self-healing de sélecteurs / correctifs proposés en diff PR** (Shiplight, Playwright Test
  Agents) : aucun mécanisme de réparation automatique de locators cassés.
- **Round-trip avec outils de gestion de tests** (Jira, TestRail, Xray) : `testbook-export`
  produit `.feature` + XLSX + Markdown, pas de push API direct.
- **Orchestration multi-agents parallèle** (Queen Coordinator à 60 agents) : QAIA reste un
  parcours de skills séquentiel invoqué par l'utilisateur/agent, pas un essaim autonome —
  choix assumé (D33), pas un manque.
- **Visual AI perceptuelle** (Applitools) : `visual-check` existe mais rien ne confirme un
  moteur de diff perceptuel équivalent — à vérifier en interne.

## Différenciation réelle de QAIA (pas juste marketing)

- **Zéro clé API dans le produit livré, zéro exécution automatique de hooks/agents/MCP** — la
  différence structurelle la plus nette. Tous les concurrents OSS trouvés exigent une clé LLM
  au runtime et/ou auto-enregistrent un serveur MCP qui s'exécute. QAIA en 100% skills
  Markdown invoqués à la demande est une posture de sécurité/portabilité distincte, pas
  retrouvée ailleurs dans le paysage exploré.
- **Score déterministe séparé du générateur, "aucun producteur ne s'auto-note"** : Agentic QE
  Fleet a un quality-gate qui s'en rapproche, mais c'est un agent parmi d'autres dans le même
  essaim, pas un plugin isolé et optionnel.
- **Shift-left + shift-right combinés dans un même parcours skill-first, humain-arbitré** :
  Agentic QE Fleet le revendique aussi mais via exécution agentique autonome ; QAIA le fait
  via un parcours explicite US → Gherkin → automatisation → score, plus proche de l'esprit
  ISTQB CT-GenAI ("l'IA propose, l'humain décide" — cf. `prioritize`).

## Pistes de backlog (classées par valeur probable, converties en issues GitHub)

1. Doc de positionnement explicite vs Agentic QE Fleet et le paysage concurrentiel.
2. Détection de flaky tests (post-hoc, sur logs CI).
3. Export natif vers formats de gestion de tests (Xray/Jira, TestRail).
4. Priorisation risque enrichie par historique (git blame / fréquence de modification),
   restant "propose, humain décide".
5. Suggestion de réparation de locators cassés en diff proposé (jamais auto-appliqué).
6. Mapping explicite des skills vers le syllabus ISTQB CT-GenAI.
7. Skill de capture/rejeu de trafic réel → conditions de test (shift-right fort).
8. Vérifier/renforcer `visual-check` face au standard "visual AI perceptuel".
9. Lint anti-assertions-creuses dans `qaia-playwright` — à garder strictement séparé de
   `qaia-score` pour ne pas contredire "aucun producteur ne s'auto-note".
10. Bridge MCP optionnel pour Cursor/Copilot, sans casser "zéro clé API dans le cœur".

## Veille élargie hors médical, recherche globale (2026-07-26)

Demande fondateur : sortir explicitement du seul angle médical/réglementé et regarder plus large
— GitHub (recherche directe de dépôts, pas seulement les noms déjà connus) et le web en général.

**GitHub — recherche directe** (`search_repositories`, plusieurs requêtes : génération Gherkin/BDD
depuis des US, générateurs de cas de test LLM, marketplaces de plugins Claude Code pour la QA) :
aucun concurrent à l'échelle d'Agentic QE Fleet (421★, déjà connu) n'est apparu. En revanche,
**l'écosystème de plugins Claude Code dédiés QA s'est nettement densifié depuis la veille du
2026-07-25** : une douzaine de petits dépôts (0-2★, tous créés/mis à jour en 2026), par exemple
`orbit` (équipe QA WordPress à 10 agents, 116 skills), `testforge` (génération de cas de test
Azure DevOps, 3 agents, Gherkin via Claude/Gemini/Ollama), `quality-engineering-skills`
(marketplace groupant qavajs/Vividus/Tosca/ServiceNow ATF), `web-tester-marketplace` (Playwright
E2E + hooks de sécurité). Aucun ne combine génération Gherkin-depuis-US **et** score déterministe
séparé **et** preuve multi-domaine comme QAIA — mais le signal de marché est clair : la niche se
peuple vite, pas seulement chez les gros acteurs SaaS.

**Web — recherche générale** : le marché confirme sa taille (test automation ~24 Mds$ en 2026,
IA de test ~687 M$ en 2025→3,8 Mds$ visés en 2035) et une poignée de nouveaux entrants financés
(Ranger, Drizz, Skyramp) — tous des SaaS cloud nécessitant une clé API/compte, aucun ne reprend
la posture "zéro clé API, 100 % skills" de QAIA. Différenciation D67 toujours tenable.

**Une trouvaille distincte, `chaos-qa`** (`keithalindsay/chaos-qa`, très récent — créé
2026-07-21, 2 commits, 0★, vérifié directement plutôt que pris au mot d'un résumé de recherche) :
suite de skills Claude Code qui **sonde adversarialement** un projet en confrontant son
comportement réel au contrat documenté (README/aide), pas seulement « est-ce que ça plante » —
puis **convertit chaque défaut trouvé en test de régression** dans le framework existant du
projet. Aucune clé API, aucune exécution non contrôlée (skills Claude Code classiques). Angle
**complémentaire, pas concurrent direct** : QAIA part de la spécification (US → Gherkin →
automatisation, en amont), `chaos-qa` part du comportement observé d'un système déjà vivant (en
aval) — les deux directions sont utiles et ne se recouvrent pas. QAIA n'a aujourd'hui aucune
skill qui sonde activement un système en confrontant son comportement à son contrat documenté
(`security-surface` est passif/ciblé auth-erreurs, `flaky-detect` détecte la variance entre runs,
pas la conformité au contrat) — gap réel, converti en piste de backlog ci-dessous.

11. **Sondage adversarial de contrat** (README/aide → comportement réel, jamais destructif,
    self-host uniquement comme le reste du shift-right — cf. `security-surface`/D26/D35) →
    conversion des défauts trouvés en scénarios de régression Gherkin taggués. Complémentaire au
    parcours spec-first existant, pas un remplacement. Voir issue GitHub correspondante.

Voir les issues GitHub correspondantes pour le détail et le suivi.

## Veille 2026-08-08 — le marché est entré dans Claude Code, et la veille précédente ne l'a pas vu

Cette passe corrige d'abord une **erreur de méthode** de la veille du 2026-07-26 (D94), qui
concluait « aucun nouveau concurrent sérieux ». Elle cherchait des concurrents *par domaine
métier* (QA hors médical). Elle n'a pas cherché dans **le canal de distribution de QAIA** —
l'écosystème de plugins et de skills Claude Code. C'est précisément là qu'ils étaient, et
plusieurs existaient déjà quand la conclusion a été écrite.

**Règle qui en découle : une veille doit couvrir le canal autant que le domaine.**

### Ce qui recouvre QAIA directement

| Projet | Nature | ★ au 2026-08-08 | Créé |
|---|---|---|---|
| [QA Orchestra](https://github.com/Anasss/qa-orchestra) ([site](https://qa-orchestra.com/)) | Plugin Claude Code MIT, 10 agents QA en 3 tiers, sans clé API | 11 | 2026-04 |
| [QASkills.sh](https://qaskills.sh/) | Annuaire/marketplace de skills QA (`npx qaskills add`), 420+ skills listées, blog SEO actif | n/a | — |
| [neonwatty/qa-skills](https://github.com/neonwatty/qa-skills) | Pipeline de génération E2E Playwright, 6 agents QA | 23 | 2026-01 |
| [darcyegb/ClaudeCodeAgents](https://github.com/darcyegb/ClaudeCodeAgents) | Agents QA pour Claude Code | 756 | 2025-07 |
| [proffesor-for-testing/agentic-qe](https://github.com/proffesor-for-testing/agentic-qe) | Essaim autonome 60 agents (déjà cité) | 435 | 2025-09 |
| [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | Skill unique d'automatisation navigateur | **2994** | 2025-10 |

QA Orchestra est le plus proche jamais observé : même canal, même promesse bout-en-bout, même
posture « pas de clé API, pas de compte SaaS ». Ses 10 agents couvrent la validation des critères
d'acceptation, la conception de scénarios (happy/negative/boundary/edge), la sélection des tests
impactés, le rapport de bug, le déploiement et la santé de l'app, la validation navigateur via
Chrome DevTools, l'orchestration, l'analyse d'impact multi-dépôts, la conversion des scénarios en
**Playwright/Cypress/Selenium/Gherkin**, et la validation manuelle guidée.

### Le différenciateur qui tombe

Le README revendiquait « ISTQB appliqué et justifié » comme argument de choix. Les descriptions
publiques de QA Orchestra et des skills QASkills nomment explicitement **partitions
d'équivalence, valeurs limites, tables de décision, transitions d'états, error guessing** — la
palette même d'`istqb-design`. Que ce soit bien fait chez eux est une question ouverte ; ce qui
est certain, c'est qu'**un visiteur ne peut pas faire la différence depuis une page d'accueil**.
L'ISTQB reste un argument de qualité. Il n'est plus un argument de choix.

### Le différenciateur qui tient

Trois points, qu'aucun des six ci-dessus ne revendique, et qui ont la propriété d'être
**vérifiables par un tiers** plutôt que d'être des affirmations :

1. **Aucun producteur ne s'auto-note.** Score structurel déterministe dans un plugin séparé en
   lecture seule (`qaia-score`), distinct du juge LLM sémantique. Chez tous les autres, le même
   essaim produit *et* évalue. C'est la règle la plus dure du projet et elle a répétitivement
   attrapé des défauts que les auteurs ne pouvaient pas voir (D136).
2. **Zéro clé API livrée, zéro hook/agent/MCP auto-exécuté.** Installer QAIA ne dépose rien qui
   s'exécute seul. QA Orchestra installe 10 agents.
3. **Les échecs sont publiés.** Verdicts défavorables conservés, suite générée exécutée sur un
   runner GitHub Actions sans session Claude ni skill chargée, tout nombre mesuré pointant son
   fichier brut (règle 4bis). **Aucun concurrent observé ne publie ses échecs.**

### Le contrepoids, à ne pas omettre

QAIA a **0 étoile** et environ **9 visiteurs uniques sur 14 jours**, contre 11 à 2994 pour les
projets ci-dessus. Aucun pilote humain ne l'a menée de bout en bout ; la qualité de ce qu'elle
produit pour un vrai utilisateur reste non mesurée. Le différenciateur le plus solide du monde ne
sert à rien s'il n'est lu par personne — c'est le sujet des issues #69 (distribution), #70
(positionnement) et #72 (preuve visible sans installer).

### Correction du même jour : QASkills.sh n'est pas qu'un annuaire, et le recouvrement est nominatif

Première lecture (« marketplace de skills, 420+ listées ») : trop douce. Lecture du dépôt
[`PramodDutta/qaskills`](https://github.com/PramodDutta/qaskills) (MIT, 197 ★, poussé le
2026-08-07) — `seed-skills/` contient **~380 skills**, et la liste recouvre le catalogue QAIA
**nom par nom** :

`istqb-test-design-techniques` · `test-case-generator-user-stories` · `bdd-gherkin-patterns` ·
`risk-based-testing` · `boundary-value-generator` · `negative-test-generator` ·
`pairwise-test-generator` · `state-machine-test-generator` · `test-plan-generation` ·
`mutation-testing` · `flaky-test-doctor` · `test-data-generation` · `test-data-anonymization` ·
`visual-regression` · `wcag-accessibility-testing` · `contract-first-testing` ·
`xray-zephyr-jira-testing` · `session-based-exploratory-testing` · `k6-performance` ·
`owasp-security` · `regression-test-selection` · `test-coverage-gap-finder`…

Il n'existe pratiquement pas une skill QAIA sans homologue de nom dans cette liste.

**Et elles ne sont pas mauvaises.** `istqb-test-design-techniques` (6,8 ko, un seul `SKILL.md`)
est lue en entier : partitions d'équivalence avec tableau de classes, BVA à deux et trois
valeurs avec le bug d'off-by-one nommé, tables de décision, transitions d'états, pairwise. Cinq
principes en tête dont « nomme la technique dans le titre du test » et « les partitions
invalides sont la moitié du travail ». C'est du travail compétent, pas du remplissage généré.

**Ce que ça change au positionnement — et c'est plus net qu'avant.** La différence n'est pas la
technique, c'est **la forme du produit** :

| | QASkills et assimilés | QAIA |
|---|---|---|
| Unité livrée | un `SKILL.md` qui améliore un prompt | un pipeline qui produit des **artefacts** |
| Sortie | du texte dans la conversation | `.feature` à IDs stables, matrice de couverture, manifeste validé, export XLSX |
| Contrôle | aucun | porte de couverture des chemins de refus (ADR 0001 — le ratio négatifs/limites n'est qu'un signal rapporté), manifestes validés en CI, score dans un plugin séparé |
| Coût d'entrée | **une commande** (`npx @qaskills/cli add …`), agent auto-détecté | marketplace + 4 installs |
| Largeur | ~380 skills, 27+ agents | 30 skills, Claude Code |

**La largeur est chez eux, la profondeur et la preuve sont ici.** Formulation à tenir : « si tu
veux un meilleur prompt, prends la leur, c'est une commande et ça marche ; si tu veux une sortie
présentable à un auditeur, c'est un autre outil ». Prétendre couvrir plus qu'eux serait faux et
vérifiable en une minute.

### Ce qui est récupérable — et c'est beaucoup

Le dépôt est MIT et **son go-to-market entier est public** : `SEO-STRATEGY.md`,
`SEO-RESEARCH-100-KEYWORDS-2026.md` (100 mots-clés avec titres proposés et sources),
`CONTENT-CALENDAR.md`, `COMPETITOR-ANALYSIS.md`, `SITE-STRUCTURE.md`,
`IMPLEMENTATION-ROADMAP.md`, et un dossier `learnings/` de rétrospectives datées (publication au
registre MCP, génération en lot, capture d'e-mails…). C'est exactement ce que QAIA n'a jamais
écrit une ligne.

Quatre choses à en tirer, par ordre d'effet :

1. **Un canal de distribution gratuit vers l'audience QA exacte.** Le site accepte les
   soumissions (« Publish a Skill », CLI + dashboard) et il est adossé à The Testing Academy —
   **189 000+ abonnés YouTube**, c'est-à-dire la communauté QA que D12 visait depuis M0 et qui
   n'a jamais été approchée. C'est le geste au meilleur rapport effort/effet du projet.
2. **La carte des annuaires où QAIA est absente**, que leur propre analyse fournit : SkillsMP
   (66 000+ skills), ClawHub (3 000+, ~15 000 installs/jour), skills.sh de Vercel (49 000+),
   Smithery.ai, plus `claudemarketplaces.com`, `claudepluginhub.com`, `aitmpl.com`. Aucun ne
   connaît QAIA.
3. **La méthode, pas le contenu.** Leur stratégie SEO est un document réutilisable comme
   *gabarit* : clusters de mots-clés, pages de comparaison (qu'ils désignent comme le type de
   contenu le plus convertissant), `llms.txt` et lisibilité par les crawlers d'IA — qu'ils
   listent comme un **manque chez eux**, donc une place encore libre. Copier leurs textes serait
   à la fois inutile et contraire à ce que QAIA revendique ; copier la méthode ne l'est pas.
4. **L'ergonomie d'installation.** `npx @qaskills/cli add <skill>` avec auto-détection de
   l'agent, plus un serveur MCP au registre officiel qui permet de chercher et installer
   *depuis* l'agent. QAIA demande cinq gestes. L'écart d'adoption commence là.

À ne pas récupérer : leurs skills. Le recouvrement de noms est réel, la valeur de QAIA est dans
la chaîne et les contrôles, pas dans la quantité de fiches.

### QA Orchestra, contrat contre contrat (lecture du dépôt, 2026-08-08)

Ce que #70 demandait était de faire tourner QA Orchestra pour de vrai sur `examples/expense-demo`
et de comparer les sorties. **Ce n'est pas ce qui a été fait ici** : le dépôt a été cloné
(`5df9ad4`, 2026-04-20) et ses dix agents lus. Une lecture établit ce que le contrat *promet*,
jamais ce que l'exécution *rend* — la case de #70 reste donc ouverte. Ce qui suit est ce qu'une
lecture peut établir, et rien de plus.

`test-scenario-designer` est le recouvrement frontal avec `istqb-design`. Son contrat, en clair :
il impose happy path, négatifs, valeurs limites (« texte : vide, 1 car., max, max+1 » ; « nombres :
0, négatif, décimal, très grand »), cas limites (concurrence, double-soumission, retour arrière,
Unicode, injection HTML), intégration et non-fonctionnel. Il exige **au moins un happy path et un
négatif par CA**, des étapes littérales (« saisir `john@example.com` », pas « saisir des
données »), des résultats observables, et il marque `[ASSUMPTION]` quand un CA est ambigu — le
même geste que notre `# open: Qn`. Sa sortie est un tableau Markdown `TS-001…` plus une matrice de
couverture CA × catégorie.

Trois écarts qui tiennent, tous vérifiables dans leur propre texte :

1. **La cible est un nombre, pas une couverture.** « Target 10-20 scenarios per ticket » est une
   consigne de volume. Chez nous, ADR 0001 remplace le quota par une **porte** : chaque chemin de
   refus décrit par le CA doit avoir un scénario, et le ratio n'est qu'un signal rapporté. Un
   quota se satisfait en remplissant ; une porte se satisfait en couvrant.
2. **Pas d'identité stable.** `TS-001` est numéroté par le run. Nos `@QAIA-xxx` survivent à la
   régénération, et c'est ce qui rend la matrice de traçabilité et le lien scénario ↔ test
   opposables d'une exécution à l'autre.
3. **Producteur et évaluateur ne sont pas séparés.** `automation-writer` écrit les tests,
   `functional-reviewer` juge la couverture, `manual-validator` valide — tous du même essaim, sans
   outil déterministe extérieur. C'est exactement la règle 3, et c'est le point où nos propres
   garde-fous nous ont attrapés six fois dans la seule journée du 2026-08-08.

Deux écarts **en leur faveur**, à ne pas taire :

- `automation-writer` sort en Playwright, Cypress, Selenium, pytest, JUnit et Gherkin, en TS par
  défaut. `qaia-playwright` ne sait faire que Playwright/JS.
- `smart-test-selector` (mapper un diff vers la suite existante : quoi rejouer, quoi va casser, où
  manque la couverture) et `release-analyzer` n'ont **aucun équivalent** chez nous. Un diff, c'est
  ce qu'un utilisateur a sous la main tous les jours ; un CA, c'est ce qu'il a au début d'un
  sprint. Leur porte d'entrée est plus fréquente que la nôtre.

Enfin, leur périmètre est déclaré et étroit — « not in scope : code quality, linting, security
scanning, performance profiling, unit tests », borné à la correction fonctionnelle vis-à-vis des
CA. Nos exemples portent des projets `security` et `perf`. Comparer les largeurs sans dire que la
leur est **volontairement** bornée serait malhonnête.

### La lecture a ensuite été mise à l'épreuve, et elle se trompait sur un point

Leur agent `test-scenario-designer` a été **exécuté** sur la même user story que QAIA, jugé en
aveugle par trois relecteurs à contexte vide : `eval/head-to-head-qa-orchestra-2026-08-08/`.
Verdict **2 contre 1 pour QAIA**, et trois corrections à apporter à ce qui précède.

**Ils ne devinent pas les bornes ambiguës.** Les trois juges sont unanimes : sur le « exactement
500,00 € » que le critère ne tranche pas, leur sortie crée le scénario **et** déclare l'hypothèse
dans une section « Risks and Gaps ». Notre avantage n'est pas de déclarer là où ils devineraient —
c'est que chez nous l'ambiguité **voyage avec le scénario** et se filtre par tag, quand chez eux
elle est à soixante lignes de là et illisible par une machine. Supériorité de structure, pas de
lucidité.

**Deux écarts de plus en leur faveur, sur notre propre terrain.** Leur sortie est
**immédiatement exécutable** — URL, comptes, données exactes, date de référence fixe résolvant
« 90 jours » ; la nôtre laisse cinq décisions à prendre. Et ils couvrent **huit classes de risque
que nous ne couvrons pas** : montants nuls et négatifs, double-clic, concurrence entre approbateurs,
retour arrière navigateur, justificatif supprimé en cours d'approbation, XSS/Unicode/RTL,
performance, accessibilité clavier.

**Ce qui tient, mesuré** : 17 chemins de refus exercés contre 10 à 12 — il leur manque toute
l'authentification et l'autorisation transverse — et neuf ambiguïtés contre six, **chacune testée**
là où deux des leurs sont signalées sans qu'aucun scénario ne les incarne.

**Et l'épreuve nous a trouvé un défaut** : notre cahier assère 17 codes HTTP que l'exigence ne
mentionne jamais ([#83](https://github.com/QAIA-Project/QAIA/issues/83)). Il passait inaperçu parce
que nous avons aussi écrit l'application — un oracle circulaire.
