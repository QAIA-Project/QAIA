# Phase de Delivery — QAIA

> **Révision v2 (revue multi-personas) — points depuis tranchés en discovery** :
> 1. CI = forme uniquement ; le comportement des skills est validé par le harnais d'éval en session mainteneur, vert avant merge (D6, Q65).
> 2. Le harnais d'évaluation existe **avant** la première skill (T10) — livré en M0.
> 3. Parallélisation par sous-agents conservée avec passe de consolidation obligatoire (D30).
> 4. Couche Cucumber abandonnée : Gherkin comme cahier, tests Playwright natifs (D5).
> 5. Critère de sortie M3 mesuré sur une app pilote réelle (T17) ; la démo publique n'est qu'un objectif intermédiaire.
> 6. Roadmap recalibrée à 4-6 mois grâce au temps plein (D15). M2+ ne démarre que si M1 trouve des utilisateurs réels.
> 7. Gate juridique G1 traitée (purge D1) ; merge squash fait, branche source supprimée (D66).
> 8. **Gate G2 (5 pilotes) levée par le fondateur** (D67, 2026-07-25) : les critères de sortie M1/M3 ci-dessous qui citent des pilotes réels comme condition bloquante ne le sont plus — voir `docs/DECISIONS.md` D67 pour la portée exacte de la levée.

Roadmap par incréments. Chaque jalon livre quelque chose d'**utilisable seul** (leçon fondatrice : des outils, pas un pipeline). Aucun jalon ne démarre sans le critère de sortie du précédent. Les décisions actées (`docs/DECISIONS.md`, y compris au-delà de D32/T17) priment **toujours** sur le texte ci-dessous en cas de divergence — ce document est un plan initial, pas la source de vérité de l'état actuel (voir `docs/STATUS.md`).

---

## Architecture cible (résumé)

```
qaia/  (monorepo GitHub, marketplace de plugins Claude Code)
├── .claude-plugin/
│   └── marketplace.json            # index des plugins
├── plugins/
│   ├── qaia-core/                  # M1 — ingestion, compréhension, RAG, génération Gherkin
│   │   └── skills/                 #   hello, us-ingest, us-review, need-understanding, rag-build,
│   │       ...                     #   istqb-design, prioritize, testbook-generate, testbook-export, feedback
│   │                               #   (invocation : /qaia-core:<skill>)
│   ├── qaia-connectors-jira/       # M2 — 1er connecteur standard (puis ADO, GitLab…)
│   ├── qaia-playwright/            # M3 — Gherkin → tests Playwright (E2E, API, mobile-web)
│   ├── qaia-perf/                  # M4 — performance (k6, décision T6)
│   ├── qaia-security/              # M4 — surface OWASP baseline
│   └── qaia-a11y/                  # M4 — accessibilité (axe-core via Playwright)
├── docs/                           # discovery, delivery, kanban, ADR
└── .github/                        # CI, templates issues/PR, Projects
```

Principes d'implémentation :

- **Pas de clé API** : tout est skill/commande exécuté dans la session Claude de l'utilisateur.
- **RAG = fichiers versionnés** dans le projet de l'utilisateur (`.qaia/knowledge/`), pas d'infra.
- **Agents ReAct** : chaque skill décrit un cycle raisonner → agir (outil) → observer → valider avec l'utilisateur. Les sous-agents sont utilisés pour paralléliser (ex. 1 agent par critère d'acceptation lors de la génération).
- **Sobriété token** : chaque commande documente son budget token indicatif ; le RAG est découpé pour éviter les re-lectures complètes.

---

## Jalons

### M0 — Fondations du dépôt (1 semaine)

| Tâches | Critère de sortie |
|---|---|
| Licence, README (FR/EN), CONTRIBUTING, code de conduite, templates issues/PR | Un contributeur externe peut comprendre le projet et proposer une issue |
| GitHub Projects configuré (Kanban de `KANBAN.md`), labels de priorisation | Le backlog vit dans GitHub |
| Squelette `marketplace.json` + un plugin « hello » installable | `claude plugin install` fonctionne de bout en bout |
| CI GitHub Actions : lint des plugins, validation des `.feature` générés en exemple | CI verte obligatoire pour merger |

### M1 — `qaia-core` : de l'US au cahier de test (4-6 semaines) ← **le cœur de la valeur**

Skills livrés, dans l'ordre du parcours conversationnel :

1. `us-ingest` — récupération d'une US depuis fichier/URL/collage, **validation utilisateur** de la source
2. `us-review` — contrôle du scraping : restitution structurée, l'utilisateur confirme ou corrige
3. `need-understanding` — reformulation, détection d'ambiguïtés, questions à l'utilisateur
4. `rag-build` — création/enrichissement de `.qaia/knowledge/` (glossaire, règles, historique)
5. `istqb-design` — choix justifié des techniques ISTQB applicables
6. `prioritize` — priorisation par risque impact × probabilité, proposée par la skill, arbitrée par l'humain (T16)
7. `testbook-generate` — génération du cahier en **Gherkin atomique**, tests cibles en Playwright natif (D5), parallélisation par sous-agents avec passe de consolidation (D30)
8. `testbook-export` — export `.feature` + synthèses XLSX/Markdown (D25)
9. `feedback` — capture des corrections utilisateur → enrichissement du RAG et des exemples des skills

**Critère de sortie M1** : 5 pilotes recrutés (D12), dont au moins 3 génèrent chacun un cahier de test réel de bout en bout, l'exportent, le retravaillent ; le taux de scénarios conservés sans réécriture majeure est mesuré (baseline du gold set).

### M2 — Connecteurs standards (3-4 semaines, en partie parallélisable avec M3)

- `qaia-connectors-jira` : lecture d'US Jira (et Xray si prioritaire) via le MCP Atlassian existant — on **réutilise les MCP du marché**, on n'écrit pas de client API
- Reporting retour : publication du cahier / des résultats vers l'outil source
- Puis, selon la demande communautaire : Azure DevOps, GitLab, Notion, Confluence

**Critère de sortie** : un pilote fait le cycle complet depuis une US Jira réelle sans copier-coller.

### M3 — `qaia-playwright` : automatisation (4-6 semaines)

- Gherkin → tests **Playwright natifs** référençant l'ID stable de chaque scénario (D5)
- Exploration assistée par **Playwright MCP** (l'agent navigue l'application pour construire des sélecteurs fiables)
- API testing via le request context Playwright
- Mobile = émulation navigateur/responsive (décision discovery Q50 assumée dans le README)
- Rapport d'exécution (skill `run-report`)

**Critère de sortie** (T17) : sur une **application pilote réelle** (fournie par un pilote — SSO, données à provisionner, environnements réels), ≥ 80 % des scénarios P1 s'exécutent sans retouche manuelle. L'app de démo publique sert d'objectif intermédiaire de développement, pas de critère de sortie.

### M4 — Plugins étendus (itératif, tiré par la communauté)

- `qaia-perf` (outil décidé en Q27), `qaia-security` (baseline OWASP), `qaia-a11y` (axe-core)
- Chacun est un plugin **indépendant et optionnel** — jamais de dépendance du core vers eux

### M5 — Boucle d'apprentissage & communauté (continu)

- Gold set communautaire : corpus d'US originales synthétiques (clean-room, MIT) + cahiers de référence pour mesurer les régressions des skills
- Dette de test suivie via labels GitHub
- Rituel de release mensuel, changelog, appel à contributions

---

## Skills & plugins à installer pour *développer* QAIA (réponse à votre question)

Dans votre session Claude Code, sur ce dépôt :

| Outil | Usage | Priorité |
|---|---|---|
| **Playwright MCP** (`@playwright/mcp`, Microsoft) | Exploration d'apps, génération et debug des tests M3 | Dès M1 (POC), indispensable M3 |
| **Serveur MCP GitHub** (officiel — il existe déjà, c'est le « petit serveur » que vous évoquiez) | Issues, Projects, PR, CI depuis la conversation | M0 |
| **skill-creator** (skill Anthropic, déjà disponible dans Claude Code) | Créer/évaluer/optimiser les skills QAIA — c'est votre outil de production principal | M0 |
| **MCP Atlassian/Jira** (officiel Atlassian) | Connecteur M2 sans écrire de client API | M2 |
| Skills bureautiques intégrées (`docx`, `xlsx`, `pdf`) | Exports du cahier de test et lecture de spécs | M1 |

À **ne pas** installer : tout ce qui exigerait une clé API Anthropic côté projet (contrainte n°1).

---

## Façon de travailler (vibe-coding, mainteneur non-codeur)

1. **Une session agentique = une tâche du Kanban.** Jamais deux chantiers dans la même session.
2. Chaque PR est **petite** et validée par vous en *utilisant* le résultat (installer le plugin, dérouler le parcours), pas en lisant le code.
3. La **CI valide la forme, pas le comportement** : lint des plugins, validation Gherkin, structure, gardes supply-chain, DCO — rien ne merge en rouge. La validation du *comportement* des skills passe par le harnais d'éval exécuté dans la session du mainteneur (D6), **vert avant merge** de toute skill de génération, et par les pilotes ; la CI seule ne remplace jamais cette revue (leçon de la revue v2).
4. Chaque décision structurante = un **ADR** (`docs/adr/`) écrit par l'agent, validé par vous.
5. Les agents peuvent être multipliés (revue croisée : un agent génère, un agent adversarial critique) — c'est la « puissance agentic » demandée, encadrée par le Kanban.
