# Correspondance QAIA ↔ ISTQB CT-GenAI (2026-07-25)

Issue GitHub #38 (P2), née de la veille concurrentielle (`docs/COMPETITIVE-ANALYSIS.md`, point 8) :
ISTQB a publié une certification spécialiste "Testing with Generative AI" (CT-GenAI) qui légitime
les techniques de conception assistées par IA et la gestion des risques associés (hallucination,
biais, non-déterminisme). QAIA cite déjà ISTQB pour ses techniques de conception
(`plugins/qaia-core/skills/generate/references/04-choosing-techniques.md`, Foundation + Test Analyst) mais ne cite jamais
ce référentiel spécifique. Ce document construit une correspondance vérifiée entre les skills QAIA
et le contenu réel du syllabus CT-GenAI.

**Ce document ne prétend à aucune conformité, accréditation ou certification officielle.** QAIA
n'est pas un organisme de formation accrédité ISTQB et ce mapping n'a pas été revu par l'ISTQB.
C'est une lecture de correspondance thématique, à usage interne et éditorial (documentation,
positionnement), pas une revendication marketing.

## Méthode de vérification

Recherche web réelle (WebSearch + WebFetch), pas de mémoire. Le syllabus officiel étant distribué
en PDF (compression FlateDecode), WebFetch ne pouvait pas en extraire le texte directement ; le
PDF a été téléchargé puis converti en texte avec `pdftotext -layout` (poppler-utils, disponible
dans l'environnement) pour une lecture ligne à ligne du document source primaire. Le texte extrait
complet (71 pages) a été conservé dans le scratchpad de session, pas dans le repo.

**Source primaire lue intégralement** : *Certified Tester Specialist Level Syllabus — Testing with
Generative AI (CT-GenAI), v1.1*, ISTQB, révision du 27/04/2026 (approuvé par l'Assemblée Générale
ISTQB le 25/07/2025, v1.0 ; mise à jour mineure v1.1 le 27/04/2026) —
[PDF officiel via ISQI](https://isqi.org/media/b9/8c/34/1777291646/ISTQB-CT-GenAI%20-%20Syllabus%20v1.1.pdf).
Auteurs : Abbas Ahmad (product owner), Gualtiero Bazzana, Alessandro Collino, Olivier Denoo, Bruno
Legeard (technical manager). Toutes les citations de sections, objectifs d'apprentissage (LO,
codes `GenAI-x.y.z`) et objectifs pratiques (HO) ci-dessous proviennent de cette lecture directe,
avec numéro de page.

### Une correction faite en cours de recherche — vigilance sur les sources secondaires

Une première recherche (WebFetch sur `istqb.guru`) a renvoyé une structure de syllabus en **7
chapitres** ("GenAI Foundations", "Quality Attributes for GenAI", "Test Design for
Non-Determinism", "Evaluation Methods and Metrics", "Data and Environment Management",
"Automation & CI/CD", "Risk, Ethics, and Governance") avec un format d'examen "40 questions,
60 minutes, ~65 % pour réussir". **Cette structure ne correspond pas au syllabus officiel** lu en
source primaire, qui contient **5 chapitres** avec des intitulés différents (voir ci-dessous) — et
elle ressemble davantage à un contenu générique "testing LLM applications" qu'au syllabus ISTQB
réel. Ce point n'a pas pu être confirmé indépendamment ; par prudence, **le contenu d'istqb.guru
est écarté de ce document** et aucune information qui n'en provient exclusivement n'est citée
ci-dessous. Cet épisode illustre pourquoi la consigne "vérifier, ne pas se fier à un résumé" était
nécessaire ici — un résumé de mémoire (la mienne comme celle d'un tiers non vérifié) aurait
produit un mapping bâti sur une structure fictive.

### Ce qui reste non vérifié / hors de portée de cette recherche

- Le document séparé *"Exam Structures and Rules V1.0"* (référencé section 0.6 du syllabus pour
  le format d'examen exact — nombre de questions, durée, seuil de réussite) n'a pas été récupéré ;
  aucune affirmation sur le format d'examen n'est faite dans ce document.
- Le contenu détaillé de l'Appendice B (matrice de traçabilité Business Outcomes ↔ Learning
  Objectives) et de l'Appendice D (glossaire complet des termes GenAI) n'a été parcouru que
  partiellement (structure confirmée, contenu exhaustif non retranscrit ici).
- Les changements précis introduits par la révision v1.1 vs v1.0 : l'annonce ISTQB
  ([istqb.org](https://istqb.org/istqb-announces-minor-update-to-certified-tester-testing-with-generative-ai-ct-genai/))
  indique des "corrections ciblées, mises à jour terminologiques et clarifications mineures" sans
  changement de structure, d'objectifs d'apprentissage ni de portée — mais l'Appendice C du PDF
  ("Release Notes") renvoie vers un document séparé téléchargeable non récupéré ; le détail exact
  des diffs n'est donc pas vérifié plus finement que ce résumé.
- Une source secondaire (cstb.ca) date la sortie v1.1 du "8 mai 2026" alors que le PDF officiel
  indique "27/04/2026" dans sa page de garde et sa révision — divergence non résolue, la date du
  PDF source primaire (27/04/2026) est retenue ici comme référence.

## Aperçu vérifié du syllabus officiel (v1.1)

Cible : testeurs, test analysts, test automation engineers, test managers, UAT testers,
développeurs ; prérequis ISTQB Foundation Level. 5 business outcomes déclarés (`GenAI-BO1` à
`GenAI-BO5`, section 0.4) : comprendre les concepts/limites du GenAI, développer des compétences
de prompting pour le test, identifier/mitiger les risques, connaître les applications du GenAI
pour le test, contribuer à une stratégie GenAI d'organisation. 5 chapitres examinables (durée
totale 13,6h) :

| # | Chapitre (titre exact) | Durée | Contenu (sections) |
|---|---|---|---|
| 1 | Introduction to Generative AI for Software Testing | 100 min | 1.1 Fondations GenAI/LLM (tokenisation, foundation/instruction-tuned/reasoning LLMs, multimodal) · 1.2 Principes clés d'usage du GenAI en test |
| 2 | Prompt Engineering for Effective Software Testing | 365 min | 2.1 Structure de prompt (rôle, contexte, instruction, données, contraintes, format) + techniques (prompt chaining, few-shot, meta-prompting) · 2.2 Application aux tâches de test (analyse, conception/implémentation, régression automatisée, monitoring/contrôle) · 2.3 Métriques d'évaluation et raffinement itératif |
| 3 | Managing Risks of Generative AI in Software Testing | 160 min | 3.1 Hallucinations, erreurs de raisonnement, biais (détection + mitigation) · 3.2 Confidentialité des données et sécurité · 3.3 Consommation énergétique/impact environnemental · 3.4 Réglementations et référentiels IA |
| 4 | LLM-Powered Test Infrastructure for Software Testing | 110 min | 4.1 Architecture (RAG, agents LLM) · 4.2 Fine-tuning et LLMOps |
| 5 | Deploying and Integrating Generative AI in Test Organizations | 80 min | 5.1 Feuille de route d'adoption (risques du "shadow AI", stratégie, sélection LLM/SLM, phases) · 5.2 Conduite du changement (compétences, montée en compétence des équipes, évolution des rôles) |

(Sections 6-12 : références, Appendice A niveaux cognitifs K1/K2/K3, Appendice B matrice de
traçabilité, Appendice C notes de version, Appendice D glossaire, Appendice E marques, Index.)

## Tableau de correspondance — skills QAIA ↔ sections CT-GenAI vérifiées

Légende : **Fort** = le skill implémente concrètement le mécanisme décrit dans la section citée ·
**Partiel** = recoupement thématique réel mais mécanisme différent ou plus étroit · **Absent
(écart assumé)** = la section existe dans le syllabus et QAIA ne la couvre pas, par conception ou
par manque — noté honnêtement plutôt que de gonfler la correspondance.

| Section CT-GenAI (code, page) | Thème | Skill(s) QAIA | Lien | Notes |
|---|---|---|---|---|
| 2.2.1 *Test Analysis with GenAI* (GenAI-2.2.1, p.24) | Générer/prioriser des conditions de test, détecter des défauts dans le référentiel de test, analyse de couverture, suggestion de techniques | `us-review`, `need-understanding`, `istqb-design`, `oracle-generate` | Fort | Le syllabus liste explicitement "suggest test techniques (e.g. boundary value analysis, equivalence partitioning)" comme tâche GenAI de test analysis — c'est exactement le rôle de `istqb-design` (palette de techniques ISTQB Foundation + Test Analyst justifiée par AC). |
| 2.2.2 *Test Design and Test Implementation* (GenAI-2.2.2/2.2.3, p.25-27), notamment HO-2.2.2b "few-shot prompting to generate Gherkin style test conditions and test cases" | Génération de cas de test, données de test, scripts automatisés, priorisation d'exécution | `istqb-design`, `testbook-generate`, `oracle-generate`, `prioritize` | Fort | HO-2.2.2b décrit *littéralement* la génération de scénarios Gherkin Given-When-Then depuis des user stories via few-shot — c'est la fonction centrale de `testbook-generate` (IDs stables, matrice de couverture, marquage de confiance). |
| 2.2.2 — génération de données de test synthétiques préservant la confidentialité | Test data synthesis | `oracle-generate` (partiellement), aucun générateur de données de production | Partiel | `oracle-generate` produit des cas limites *grounded* sur des standards (Luhn, ISO 8601, IBAN…), pas une synthèse de données de production anonymisées à grande échelle. |
| 2.2.3 *Automated Regression Testing* (GenAI-2.2.3, p.27-28) — scripts keyword-driven, self-healing, rapports automatisés | Automatisation de régression | `automate` (Playwright POM + CI), `run-report`, `flaky-detect` | Partiel | `automate` couvre la génération de scripts et le pipeline CI ; `run-report` couvre le reporting automatisé. **Écart assumé** : le "self-healing and adaptive tests" (réparation automatique de locators cassés) décrit p.27 n'existe pas dans QAIA — déjà identifié comme angle mort dans `docs/COMPETITIVE-ANALYSIS.md`. L'"impact analysis" (cibler la régression sur le code modifié) n'existe pas non plus. |
| 2.2.4 *Test Monitoring and Test Control* (GenAI-2.2.5, p.28-29) | Tableaux de bord, métriques, replanification | `run-report`, `report` (manifest standardisé) | Partiel | Les deux produisent des métriques normalisées après-coup ; aucun monitoring continu/temps réel ni replanification automatique de l'effort de test. |
| 2.3 *Evaluate GenAI Results and Refine Prompts* (GenAI-2.3.1/2.3.2, p.31-33) — métriques (accuracy, precision, recall, execution success rate…), A/B testing de prompts, feedback utilisateur | Évaluation et raffinement itératif | `testbook-score` (rubrique 10 dimensions /20), `aptitude-gate` (PASS/CONCERNS/FAIL), `feedback` (capture de corrections, promotion en règles) | Fort | Le principe "no producer scores itself" de QAIA (score séparé du générateur) est une réponse structurelle à ce chapitre : le syllabus prescrit d'évaluer la sortie GenAI avec des métriques déclarées ; `testbook-score`/`aptitude-gate` sont exactement ce mécanisme, en composant séparé. `feedback` correspond à "integrate user feedback" et à la construction de bibliothèques de prompts/règles réutilisables (5.2.2). |
| 3.1.1-3.1.2 *Hallucinations, Reasoning Errors, Biases* (p.35-36) — détection par cross-verification, consultation d'expert, vérification de cohérence | Détection des défauts GenAI | Discipline `[assumption]` / `[open]` / `@low-confidence` (`istqb-design`, `need-understanding`, contrat partagé `README.md` règle 7) | Fort | Le syllabus prescrit la "cross-verification: compare AI-generated output with existing documentation, requirements" — c'est le rôle du protocole de citation `BR-KB-nnn` (README.md, "Knowledge retrieval & citation") : toute extrapolation au-delà de la source est marquée et vérifiable, jamais silencieusement résolue. |
| 3.1.3 *Mitigation techniques* (p.37) — "provide complete context", "divide prompts into manageable segments" (prompt chaining), "compare results across models" | Mitigation des hallucinations/erreurs de raisonnement | Étapes structurées en checkpoints (`00-source.md` → `04-priorities.md`), validation humaine à chaque étape (⚠ VALIDATION) | Partiel | Le découpage en étapes vérifiées séquentiellement (le "journey" QAIA) correspond conceptuellement au "prompt chaining with human verification at each step" (HO-2.2.1b). **Écart** : QAIA ne compare pas les résultats entre plusieurs modèles (mitigation citée p.37) — aucun mécanisme d'ensemble/comparaison inter-LLM. |
| 3.1.4 *Non-Deterministic Behavior* (p.37) — température, seeds | Reproductibilité | Absent | Absent (écart assumé) | QAIA ne pilote aucun paramètre d'inférence (température, seed) : c'est hors périmètre d'un ensemble de skills Markdown sans clé API ni appel LLM direct dans le produit livré. |
| 3.2 *Data Privacy and Security Risks* (GenAI-3.2.1-3.2.3, p.38-39) | Confidentialité des données, vecteurs d'attaque (context/request manipulation) | Règle 5 (masquage PII à la source, pas de journal de correspondance), règle 6 (aucun effet de bord hors `.qaia/`, pas de réseau hors source désignée), règle 7 (refus des sources illicites/abusives) — `README.md` | Fort | Correspondance directe et précise : le syllabus liste "unintentional data exposure" et "lack of control over data usage" comme risques — la règle QAIA "PII redacted to typed placeholders before any file is written… no redaction ledger" est une mitigation concrète du premier risque cité. |
| 3.3 *Energy Consumption and Environmental Impact* (GenAI-3.3.1, p.40) | Empreinte énergétique du GenAI | Absent | Absent (écart assumé) | Aucun skill QAIA ne mesure ou ne discute la consommation énergétique/CO2 des appels LLM — cohérent avec le fait que QAIA ne fait pas d'appel LLM dans son propre code (skills Markdown exécutés par l'agent hôte), mais le sujet n'est traité nulle part dans la documentation produit. |
| 3.4 *AI Regulations, Standards and Best Practice Frameworks* (GenAI-3.4.1, p.41) | RGPD, cadres réglementaires IA | Absent (au-delà de la citation ISTQB elle-même) | Absent (écart assumé) | `istqb-design` cite déjà ISTQB comme référentiel de techniques ; aucun skill ne référence explicitement un cadre réglementaire (RGPD, AI Act…) au sens de cette section. |
| 4.1.2 *Retrieval-Augmented Generation* (GenAI-4.1.2, p.45) | RAG : chunking, embeddings, base vectorielle, récupération sémantique | `rag-build`, protocole "Knowledge retrieval & citation" du `README.md` | Partiel | `rag-build`/l'index `knowledge/index.md` implémentent le *principe* du RAG décrit (indexer une base de connaissance, ne charger que les fichiers pertinents, citer la source) mais **pas le mécanisme** : pas d'embeddings, pas de base vectorielle, pas de similarité sémantique — un routage par table d'index et tags textuels, volontairement plus simple et sans dépendance externe. Le mapping est thématique, pas technique. |
| 4.1.3 *LLM-Powered Agents* (GenAI-4.1.3, p.46) | Agents autonomes/semi-autonomes, orchestration multi-agents | Absent, par choix documenté | Absent (écart assumé) | `docs/COMPETITIVE-ANALYSIS.md` documente déjà ce choix (D33) : QAIA reste "un parcours de skills séquentiel invoqué par l'utilisateur/agent, pas un essaim autonome". Le syllabus décrit ce chapitre comme une évolution normale du domaine ("shifting test automation from script-based execution to goal-driven, agent-based test automation") — QAIA s'en écarte délibérément, ce n'est pas une lacune non discutée. |
| 4.2 *Fine-Tuning and LLMOps* (GenAI-4.2.1/4.2.2, p.47-48) | Fine-tuning de LLM/SLM, opérationnalisation | Absent, par choix structurel | Absent (écart assumé) | Cohérent avec la différenciation "zéro clé API dans le produit livré" documentée dans `docs/COMPETITIVE-ANALYSIS.md` — QAIA ne déploie ni n'opère de modèle. |
| 5.1.1 *Risks of Shadow AI* (GenAI-5.1.1, p.50) | IA non approuvée/non gouvernée : sécurité, conformité, PI | Posture "zéro clé API, zéro exécution automatique de hooks/agents/MCP" (`docs/COMPETITIVE-ANALYSIS.md`) | Partiel | Pas un mécanisme du produit à proprement parler, mais une réponse structurelle cohérente à ce risque nommé par le syllabus : un outil qui ne s'auto-enregistre pas et n'exige pas de clé API réduit la surface de "shadow AI" décrite (sécurité, conformité). Lien thématique, pas une fonctionnalité dédiée. |
| 5.1.2-5.1.4 Stratégie et feuille de route d'adoption GenAI | Sélection LLM/SLM, phases d'adoption | Absent | Absent (écart assumé) | Hors périmètre : QAIA est un outil de test, pas un accompagnement au changement organisationnel. |
| 5.2.1-5.2.3 Compétences et évolution des rôles | Montée en compétence des équipes, bibliothèques de prompts partagées | `feedback` (partiel), `qaia-help` (partiel) | Partiel | `feedback` capture et promeut des corrections en règles réutilisables (proche de "sharing prompt pattern libraries", 5.2.2) ; `qaia-help` oriente l'utilisateur dans le parcours mais ne constitue pas un programme de formation. |

## Ce que ce mapping ne dit pas

- Il ne dit pas que QAIA "prépare à la certification CT-GenAI" ni qu'il en couvre le programme —
  les chapitres 1 (fondations LLM), 3.3-3.4 (énergie, réglementation), 4.2 (fine-tuning/LLMOps) et
  5.1-5.2 (stratégie d'organisation) ne sont pas couverts ou ne le sont que marginalement.
- Il ne dit pas que le mécanisme technique de `rag-build` est un RAG au sens du syllabus (pas
  d'embeddings ni de base vectorielle) — seul le principe (index → récupération ciblée → citation)
  est comparable.
- Les correspondances "Fort" reflètent un recoupement de mécanisme (ce que le skill fait
  concrètement correspond à ce que la section prescrit), vérifié en relisant le texte source des
  deux côtés — pas une auto-évaluation de qualité.

## Sources

- [Syllabus CT-GenAI v1.1 (PDF officiel, ISQI)](https://isqi.org/media/b9/8c/34/1777291646/ISTQB-CT-GenAI%20-%20Syllabus%20v1.1.pdf) — source primaire, lue intégralement (71 pages) via extraction `pdftotext -layout`.
- [ISTQB — Certified Tester Testing with Generative AI, communiqué de presse (v1.0)](https://istqb.org/istqb-certified-tester-specialist-level-testing-with-generative-ai-ct-genai-press-release/)
- [ISTQB — Annonce de la mise à jour mineure v1.1](https://istqb.org/istqb-announces-minor-update-to-certified-tester-testing-with-generative-ai-ct-genai/)
- [CSTB — ISTQB CT-GenAI v1.1 Released](https://cstb.ca/news/istqb-ct-genai-v1-1-released) (source secondaire, date de sortie divergente non résolue — voir "Ce qui reste non vérifié")
- `docs/COMPETITIVE-ANALYSIS.md` (ce dépôt) — pour les choix de conception QAIA cités (D33, zéro clé API, angles morts self-healing/impact analysis)
- `plugins/qaia-core/skills/README.md`, `plugins/qaia-core/skills/*/SKILL.md`, `plugins/qaia-playwright/skills/*/SKILL.md`, `plugins/qaia-score/skills/*/SKILL.md` (ce dépôt) — pour le comportement réel des skills QAIA cités dans le tableau

Note écartée volontairement : [istqb.guru](https://www.istqb.guru/certified-tester-generative-ai/) —
structure de syllabus incompatible avec la source primaire (voir "Une correction faite en cours de
recherche"), non citée dans ce document.
