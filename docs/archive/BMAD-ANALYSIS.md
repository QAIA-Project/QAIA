# Analyse BMAD → décisions d'adoption pour QAIA

> Étude réalisée sur les sources (clone de `bmad-code-org/BMAD-METHOD` v6 — docs incluses — et `bmad-method-test-architecture-enterprise`), 2026-07-23. Synthèse opérationnelle ; la décision d'ensemble est actée en D33 (`DECISIONS.md`).
>
> **Mise à jour 2026-07-29** : recoupée contre la doc publique live (`bmad-code-org.github.io/bmad-method-test-architecture-enterprise`) — 1 écart trouvé et corrigé ci-dessous (workflow *Teach Me Testing* + *TEA Academy*, absents de la version 2026-07-23). Pas de révision de fond : le reste (modèle de risque, gates, écart de nature avec QAIA) tient toujours.
>
> **Ce document analyse TEA, pas la méthode de construction de QAIA elle-même.** QAIA (le produit) n'a pas été bâti en suivant le pipeline BMAD 4 phases (Analysis → Planning → Solutioning → Implementation) : sa propre discovery (`docs/DISCOVERY.md`, gates G1-G3, questions Q1-Qn, ADRs, Kanban) a précédé cette étude BMAD de plusieurs semaines et suit un format distinct, propre à QAIA. Cette étude est arrivée **après** le début de la construction, comme une veille ponctuelle débouchant sur une adoption sélective de patterns (D33) — pas comme la méthode fondatrice du projet.

> **Relecture à six personas, 2026-08-10, contre BMAD v6.10.0 (51 711 ⭐, poussé le jour même).**
> Trois faits nouveaux que les relevés du 07-23 et du 08-09 ne pouvaient pas contenir, et un
> constat qui porte sur nous : **sur les 12 patterns « adoptés » ci-dessous, 5 n'ont jamais été
> implémentés** (A2, A6, A8, A10, A11) — vérifié fichier par fichier, pas de mémoire. Un tableau
> « Adopté » qui liste des intentions non tenues est la même faute que les comptes de skills
> périmés : il porte une garantie qu'il n'honore pas. Le statut réel est désormais en colonne.
>
> 1. **BMAD est devenu un marketplace de plugins Claude Code** (`.claude-plugin/marketplace.json`,
>    6 plugins). Le pattern à reprendre n'est pas une idée, c'est un champ : ses plugins déclarent
>    `"source": "./"` **plus un tableau `skills: [...]` explicite**, donc une même skill est servie
>    par plusieurs plugins sans duplication de dossier. BMAD en tire un étagement d'entrée que
>    QAIA n'a pas : **quatre plugins à UNE skill** (`bmad-brainstorming`, `bmad-party-mode`,
>    `bmad-forge-idea`, `bmad-deep-recon`), un paquet à 3, et le complet à 30. QAIA impose
>    `qaia-core` = 18 skills comme seule porte d'entrée. C'est A11 (« modèles gradués »), jamais
>    fait, et le mécanisme pour le faire sans rien restructurer existe désormais, démontré chez
>    le voisin.
> 2. **`bmad-qa-generate-e2e-tests` est entré dans `bmm-skills/ship/`** — le cœur de BMAD, plus
>    seulement TEA. Le relevé du 07-23 concluait « aucun recouvrement réel sur le cœur M1 » ;
>    ce n'est plus vrai sur le mot *recouvrement*. Mais la frontière d'ADR 0004 en sort **plus
>    nette, pas moins** : la skill dit d'elle-même « Generate automated API and E2E tests for
>    **implemented code** », donc elle prend le code pour oracle. C'est exactement la suite qui,
>    sur `json-server`, ne pouvait pas trouver `_dependent` — elle aurait recopié la faute.
>    À dire ainsi, avec la mesure derrière, plutôt qu'en affirmant qu'il n'y a pas de voisin.
> 3. **BMAD exécute du code depuis ses skills : 31 fichiers `.py` sous `src/`**, dont
>    `resolve_customization.py` et `pick_methods.py` appelés en `uv run` à l'activation. Prérequis
>    annoncés : Node 20.12+, Python 3.10+, **uv**. La promesse « rien ne s'auto-exécute » de QAIA
>    cesse d'être une prudence abstraite : elle se mesure contre un voisin de 51k ⭐ qui a tranché
>    l'inverse. **Et leur solution de repli mérite d'être copiée** : chaque appel de script est
>    suivi de « If the script fails, resolve it yourself by reading these three files… » — la
>    skill dégrade en prose au lieu de casser. QAIA a remplacé la prose par du code le 08-09 ;
>    BMAD garde les deux. Le chemin du milieu existe et on ne l'a pas envisagé.
>
> **Ce que la relecture a trouvé de réutilisable et qui n'était pas dans la liste A1-A12 :**
>
> - **`bmad-advanced-elicitation` — un point de contrôle partagé que les AUTRES skills appellent**
>   à leurs pauses naturelles pour pressurer ce qu'elles viennent de produire, avec un menu au
>   contrat stable (1-5 / r / a / x) et la règle « ne jamais modifier le travail sans un oui ».
>   QAIA a `elian-refuter`, mais c'est un **agent du tier opt-in, non installé par défaut** : nos
>   skills n'ont aucun mécanisme partagé d'auto-contestation. C'est le pattern le plus directement
>   transposable de toute l'étude, et il sert la règle 3 (nul ne note sa propre sortie) au niveau
>   où elle manque le plus — pendant la production, pas après.
> - **Le catalogue servi par script pour qu'il n'entre jamais entier en contexte**
>   (`pick_methods.py --category …`). QAIA le fait à moitié : `istqb-design` a bien un
>   `references/`, mais les cinq plus grosses skills pèsent 1 500 à 2 100 mots de prompt chargés
>   d'un bloc. Sur un produit dont **13 des 14 commandes mesurées coûtent plus cher que son propre
>   devis**, l'économie de contexte n'est pas un raffinement.
> - **`communication_language` en configuration.** BMAD parle la langue du config. Les skills QAIA
>   produisent en anglais sans réglage — pour un projet dont le fondateur vise d'abord des
>   communautés QA francophones, c'est un frein d'adoption gratuit à lever.
>
> **Écarté à la relecture** : le `customize.toml` à trois couches (base → équipe → perso) reste
> le bon dessin (c'est A10), mais sa résolution BMAD passe par `uv run` — à reprendre en Markdown
> lu par la skill, pas en script, sous peine de casser ADR 0002.

## Ce qu'est BMAD en une page

**BMAD** (Build More Architect Dreams, ~51k ⭐, MIT) est un framework de développement piloté par IA : *agentic planning* (les agents facilitent la réflexion via des workflows structurés, phase par phase) + *context-engineered development* (chaque phase produit les documents qui deviennent le contexte de la suivante ; « le LLM est le moteur », tout est markdown). Cycle v6 en 4 phases (Analysis → Planning → Solutioning → Implementation), 6 agents nommés à persona (Mary, John, Winston, Amelia…), story files auto-contenus, tracks adaptatifs à l'échelle, installeur multi-outils (40+ plateformes, Claude Code « preferred »), releases mensuelles.

**Le module TEA (Test Architect, agent « Murat »)** est le voisin direct de QAIA : **9 workflows** (Teach Me Testing/TMT, Test Design/TD, Framework Setup/TF, CI/CD Integration/CI, ATDD/AT, Test Automation/TA, Test Review/RV, NFR Evidence Audit/NR, Requirements Tracing/TR — TMT ajouté le 2026-07-29, absent du relevé initial du 2026-07-23), modèle de risque probabilité×impact (priorisation **P0-P3**) avec gates **PASS/CONCERNS/FAIL/WAIVED** et waivers datés/approuvés, base de connaissance à chargement sélectif par tiers (« 40-50 % de contexte économisé »), step-files chargés un à un avec reprise sur frontmatter YAML. Deux points d'entrée pédagogiques notés le 2026-07-29 : **TEA Academy** (7 sessions d'onboarding) et **TEA Lite** (automatisation rapide sans le parcours complet) — non repris dans QAIA (pas de volet formation en v1). **Différence de nature** : TEA part du code et de l'architecture d'un projet BMAD pour outiller des développeurs ; il ne produit pas de cahier Gherkin depuis des US, n'applique pas de techniques ISTQB nommées, n'a ni référentiel de test ni régénération par diff. Aucun recouvrement réel sur le cœur M1 de QAIA.

## Adopté (patterns retenus, par ordre valeur/effort)

> **Colonne « Réel » ajoutée le 2026-08-10, après vérification fichier par fichier.** « Adopté »
> ne voulait dire que « décidé ». Cinq lignes sur douze n'ont jamais été construites et la table
> ne le disait pas — ✅ implémenté, ◐ partiel, ❌ jamais fait.

| # | Pattern BMAD/TEA | Application QAIA | Quand | Réel |
|---|---|---|---|---|
| A1 | **Frontmatter YAML de progression + Resume** dans les artefacts (`stepsCompleted`, `lastStep`, `lastSaved`) | Complète `.qaia/state/` (T8) : l'état intra-document vit dans l'artefact lui-même — portable (D29), partageable git, lisible humain | M1 | ✅ `.qaia/state/*/journey.md` |
| A2 | **Index de connaissance à tiers** (core/extended/specialized) + flags de config | Colonne `tier` dans `knowledge/index.md` (D21) + chargement conditionnel (ex. fragments médical si `regulated: true`) | M1 | ❌ aucun `tier` dans l'index |
| A3 | **Trois intents par skill : Create / Update / Validate** | QAIA a Create et Update (diff D17) ; ajouter un mode **Validate** (audit d'un cahier existant contre la checklist qualité — y compris un cahier non produit par QAIA : produit d'appel) | M1 | ✅ `testbook-validate` |
| A4 | **Skill d'orientation `bmad-help`** | Skill `qaia-help` : inspecte `.qaia/`, dit la prochaine étape, invoquée en fin de chaque skill — résout le « et maintenant ? » | M1 | ✅ `qaia-help` |
| A5 | **Gate formalisée PASS/CONCERNS/FAIL/WAIVED** avec waivers (raison + approbateur + expiration) | La matrice de couverture (D18) débouche sur une **décision d'aptitude auditable** — différenciateur niche réglementée (D2), traçabilité depuis l'exigence (pas depuis le code comme TEA) | M1-M2 | ✅ WAIVED, contrat de sortie |
| A6 | **Step-file architecture** pour les skills longues | Découper `testbook-generate` en step-files chargés un à un + `checklist.md` de validation séparée | M1 (refactor) | ❌ aucun step-file |
| A7 | **Sous-agents → JSON temporaire → agrégation** | Protocole de la parallélisation D30 : seuls les résultats agrégés remontent au contexte principal | M1 | ◐ 3 skills le mentionnent |
| A8 | **Checklists par artefact + revue adversariale à filtrage humain** (« zéro finding = re-analyse ; l'IA trouve des faux positifs, l'humain filtre ») | Outillage de D28 (revue des PR de skills) et D31 (aide à la revue du cahier) | M1 | ❌ aucun `checklist.md` |
| A9 | **Un agent nommé à persona** (un seul — pas six) | Un « Test Architect » conversationnel qui porte le parcours et dispatche sur intention ; persona = continuité + découvrabilité | M2 | ✅ skill `qaia` |
| A10 | **Customisation en couches** (défauts → équipe committée → perso gitignorée) | Couche préférences personnelles non versionnées au-dessus du RAG d'équipe (D23) | M2 | ❌ aucune couche perso |
| A11 | **Modèles d'engagement gradués** (à la « TEA Lite ») | Documenter : QAIA Lite (`testbook-generate` seul sur une US collée) / Solo (sans RAG) / Full (parcours complet) | M1 (doc) | ❌ Lite/Solo/Full jamais écrits |
| A12 | **README-architecture transparent** (quel fichier se charge quand) | Standard de doc des skills QAIA — aide aussi la revue adversariale des contributions | M1 (doc) | ◐ README par plugin, pas de standard |
## Écarté (et pourquoi)

1. **Constellation d'agents + party mode** — QAIA couvre un métier : un agent, des skills.
2. **Pipeline 4 phases complet** — QAIA consomme des US, il ne cadre pas le produit ; la leçon fondatrice (« des outils, pas un pipeline ») est l'inverse de cette tentation, que BMAD lui-même contourne (Quick Flow, TEA Solo).
3. **Installeur Node/Python 40-plateformes** — ingénierie inmaintenable en solo ; le canal QAIA reste marketplace + copie markdown (T12). Pas de scripts résolveurs non plus (casserait D29) — BMAD paie déjà cette dette.
4. **Sharding de documents** — mécanisme v4 abandonné par BMAD v6 lui-même ; QAIA part directement sur index + fragments ≤ 2k tokens (D21).
5. **Duplication des fragments de connaissance par workflow** — cauchemar de synchronisation en solo ; une seule source `.qaia/knowledge/`.
6. **Web bundles Gemini/ChatGPT** — hors positionnement session Claude, matrice de test triplée.
7. **Boucle non supervisée (bmad-loop)** — l'anti-thèse du contrat QAIA « le testeur valide chaque étape », qui est l'argument réglementaire.
8. **Taxonomie de risque TEA telle quelle** — pensée dev/produit ; QAIA garde les référentiels du métier test (ISTQB, compatible ISO 14971) et mappe vers un score simple (T16).

## Positionnement

**Inspiration d'abord, complément ensuite, concurrent en apparence seulement.** Pas de distribution comme module BMAD en v1 (dépendance à un écosystème mouvant, perte du positionnement skills portables) — mais l'option reste quasi gratuite plus tard : l'architecture skills v6 de BMAD converge vers les plugins Claude Code. Un doc « Using QAIA with BMAD » (QAIA en phase 4, en pair de TEA) est un canal d'acquisition vers une communauté de 51k ⭐ déjà sensibilisée. **Veille active sur TEA à chaque release** : son `risk_threshold` annoncé pointe vers le territoire de QAIA.
