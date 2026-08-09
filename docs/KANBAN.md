# Kanban & Sprints — QAIA (v3, groomé)

Board GitHub Projects (à monter — action propriétaire M0-CHECKLIST #5). Colonnes : **Backlog** → **À challenger** → **Prêt** → **En cours** (WIP max 2 chantiers humains ; les agents parallélisent en dessous) → **En revue/validation** → **Terminé**. Processus de challenge inchangé : valeur / effort / leçon fondatrice / critère d'acceptation.

Le développement se déroule en **sprints courts** exécutés en sessions agentiques ; chaque sprint se termine par : harnais d'éval vert, revues (adversariale + cohérence) passées, Kanban re-groomé.

---

## Sprint 34 — huit agents exercés, onze défauts, et un critère qui explique les campagnes (2026-08-09, D172-D196) 🔵 OUVERT

Ouvert sur une campagne externe, **retourné trois fois dans la journée** par ce qu'elle a trouvé.

**Livré** : `spec-suite-drift` et `signal-ingest` (37 skills) · le tier `agents-tier/` (8 agents,
opt-in, hors des plugins) · les 4 boucles de retour fermées et gardées · `make check` de 8 à 12
contrôles · 408 fichiers d'`eval/` archivés, réversibles.

**Premier effet externe du projet** : `realworld-apps/realworld#1718`, corrigé par le mainteneur.

**Épiques ouvertes** — #89 charger la poutre *(attend un testeur, pas du code)* · #90 rendre le
dépôt installable · #91 rendre le backlog directeur · #92 distribution *(propriétaire : le
fondateur)*.

**Backlog** : 12 → 7 issues. #30, #61 et #73 fermées en constatant que **le travail était déjà
fait** — trois fois le même motif, consigné dans #91 : *un backlog qu'on ne relit pas est un
journal.*

**Ce que le sprint a appris et qui dépasse le sprint** : une règle qui encode une norme externe se
transporte, une règle qui encode une préférence maison ne se transporte pas. Mesuré sur trois
campagnes — 2 %, 26 %, 83 % de précision selon la nature de la règle, pas la qualité du code.

---

## Sprint 33 — la revue d'architecture retourne le sprint, et trois P0 apparaissent (2026-08-08, D165-D169) 🔵 OUVERT

Ouvert sur deux arbitrages ([ADR 0005](adr/0005-scope-discovery-and-run.md),
[ADR 0006](adr/0006-multi-agent-portability.md)) — puis **retourné le jour même** par une revue
d'architecture menée sur le dépôt avec obligation de preuve.
[ADR 0007](adr/0007-scope-delivery-and-maintenance.md) remplace ADR 0005 : le périmètre reste
*Delivery + Maintenance*. La portabilité (ADR 0006) tient et reste ouverte.

**Le verdict de la revue : ne rien construire de neuf, rendre vrai ce qui est déjà écrit, publier
ensuite.** Trois P0, tous vérifiés à la main :

| P0 | Constat |
|---|---|
| Kit pilote | il faisait ingérer au testeur `eval/gold-set/US-001…`, **dont la section « Judge reference » liste les ambiguïtés plantées** — le formulaire lui demandait ensuite lesquelles il avait manquées. La première mesure humaine du projet aurait été faussée par construction. |
| Chiffres vitrines | `run-log.txt` dit 32 exécutions pour **26 tests** ; les documents disaient 32, 31 et **24** — ce dernier dans une `SKILL.md` empaquetée et livrée. |
| ADR 0007 | n'était cité par **aucun** fichier hors lui-même, pendant qu'ADR 0005 portait toujours « Accepté » et fondait ce sprint. |

| Chantier | État | Note |
|---|---|---|
| **#84 — exécuter la chaîne dans un autre agent, telle quelle** | à faire, **en premier** | Mesurer, ne rien corriger en route. Le correctif est le backlog qui en sort. |
| **#85 — exigences non-fonctionnelles dérivées en Discovery** | à faire | Point dur : une exigence inventée est pire que pas d'exigence. Provenance ou question ouverte, jamais de chiffre orphelin. |
| **#86 — incident de production → test de non-régression** | à faire | La plus utile des quatre pratiques du shift-right, et la moins chère. |
| **#87 — chaos engineering** | différé, argumenté | Suppose une cible qu'on possède et qu'on peut casser, un environnement à déployer, et une production à éprouver. |

**L'ordre est imposé, pas suggéré.** #84 d'abord : tout ce qu'on construirait avant cette mesure
serait une supposition sur ce qui casse ailleurs.

**Le risque, écrit à l'ouverture** : élargir le périmètre avec **zéro utilisateur** est exactement
l'ordre que le sprint 32 s'est reproché toute la journée. Assumé par le fondateur au motif que
« couvrir le cycle » est une promesse de positionnement, et qu'un produit qui ne la tient pas ne se
rattrape pas par la qualité de ce qu'il tient.

---

## Sprint 32 — distribution, première application hors du dépôt, et un dépôt qui se corrige lui-même (2026-08-08, D140-D164) ✅ TERMINÉ

Session longue sous mandat d'autonomie. Deux temps : le matin, la distribution et une preuve de
mutation qui s'est révélée fausse ; le soir, la première application à un logiciel tiers, puis une
série de corrections déclenchées par des relectures que le projet ne s'était jamais imposées.

| Livré | Preuve |
|---|---|
| **Deux vrais défauts trouvés dans un logiciel qu'on n'a pas écrit** — cahier écrit depuis le seul README de la cible, jamais son code, passé sur deux versions. Les deux corrigés en amont depuis. Le troisième constat compté **contesté** parce que notre test extrapolait. | `eval/external-application-2026-08-08/` |
| **La preuve de mutation refaite après s'être révélée fausse** : elle annonçait 107/107 alors que **40 mutations n'avaient jamais tourné**. Trois défauts de l'outil, tous du même genre. Corrigée : 111 candidates, 111 exécutées, 111 tuées. | `eval/mutation-proof-2026-08-08/` |
| **Cinq skills** — `defect-report`, `openapi-ingest`, `impact-select`, `confirm-fix`, `test-plan-and-closure` — chacune éprouvée sur un cas réel, pas sur une fixture | 30 → 35 skills |
| **Trois issues fermées en refusant de construire** : ADR 0004 (pas de niveau unitaire), anonymisation écartée sur un critère de vérifiabilité, compatibilité navigateurs traitée en note plutôt qu'en 36ᵉ skill | #78, #81, #82 |
| **Panel de relecture à contexte vide sur le travail du jour** : 30 constats examinés, 11 réfutés, **19 confirmés** — dont un qui rendait la preuve principale non reproductible | `eval/cold-review-2026-08-08/` |
| **QA Orchestra exécutée et jugée en aveugle**, 2 juges sur 3 pour QAIA — et deux écarts en leur faveur sur notre propre terrain | `eval/head-to-head-qa-orchestra-2026-08-08/` |
| **Un défaut que rien d'interne n'avait vu** : le cahier vitrine assérait 17 codes HTTP absents de l'exigence. Oracle circulaire — on avait aussi écrit l'application testée. | #83, D161 |
| **Deux défauts répétés devenus des machines** : `check_skill_counts.py` et `check_decision_register.py`, tous deux éprouvés dans les deux sens | `make check` passe de 3 à 6 contrôles |
| **La carte de couverture gagne deux axes** : le cycle Discovery/Delivery/Run, et les outils face aux leaders du marché | `docs/TEST-COVERAGE-MAP.md` §3bis, §3ter |
| Prompt de revue pour un LLM **sans** accès au dépôt, écrit après que deux analyses externes ont inventé des faits | `docs/EXTERNAL-REVIEW-PROMPT.md` |

**Ce que le sprint établit, et qui n'est pas confortable** : QAIA vit entièrement dans **Delivery et
Maintenance**. Elle commence quand la discovery est finie, s'arrête quand le déploiement commence,
et sa couverture du shift-right est de zéro. C'est la description la plus exacte du produit à ce
jour, et elle n'avait jamais été écrite.

**Ce que le sprint ne change pas** : 0 étoile, 0 fork, **0 pilote humain**. Sur 35 skills, cinq ont
été exercées hors du dépôt et aucune n'a jamais servi à un humain dans son travail. Les 8 issues
restantes ne demandent plus une ligne de code produit — trois relèvent de la distribution, une exige
un vrai PM/PO, deux attendent un pilote, deux sont des tiers volontairement différés.

---

## Sprint 23 — Second audit externe (Gemini), recoupement, JSON Schema du contrat de sortie (2026-07-28, D104) ✅ TERMINÉ

Demande fondateur : lire un rapport d'audit produit par Gemini (3 personas ISTQB/IA/PM),
mettre à jour le Kanban, puis démarrer un plan d'implémentation ; en session, demande
complémentaire de rejouer le même exercice à 3 personas côté Claude pour recoupement
indépendant.

| Livré | Preuve |
|---|---|
| **Rapport Gemini sauvegardé et recoupé item par item** contre l'état réel du dépôt (pas pris au mot) | `eval/baselines/audit-report-gemini-2026-07-28.md` |
| **Second audit indépendant Claude 3-personas**, ancré sur les fichiers locaux (pas une exploration web comme demandé — voir note ci-dessous) | `eval/baselines/audit-report-claude-3persona-2026-07-28.md` |
| **Divergence de note expliquée, pas ignorée** : Gemini 7,5/10 ("prêt pour le pilote") vs Sprint 22 2,4/5≈4,8/10 ("non prêt sans conditions") — écart de méthode (lecture vs exécution/reproduction de défauts), pas de désaccord de fait une fois les mêmes items comparés | D104 |
| **JSON Schema formel du contrat de sortie livré** (item Phase 1 de l'audit Gemini, confirmé absent avant cette session) : `docs/schemas/output-contract-v1.schema.json` + validateur stdlib sans dépendance `eval/tools/validate_manifest.py`, vérifiés sans erreur contre les 2 manifests réels du dépôt + testés positifs sur un cas cassé injecté (5 erreurs détectées) | `docs/OUTPUT-CONTRACT.md` (section « Programmatic validation » ajoutée) |
| **Vrai défaut de dérive trouvé en construisant le validateur** : `examples/scoring-demo/manifest.json` ne portait pas `design.knowledgeApplied`, pourtant documenté comme faisant partie du contrat 1.0 (D38) — corrigé le jour même | D104 |
| **1 nouvelle issue** pour le gap Phase 1 restant (portabilité multi-LLM des instructions, distinct du bridge MCP #42) — pas implémenté à la volée, effort plus substantiel qu'un schema (nécessite un few-shot réel testé contre un fournisseur externe) | [#58](https://github.com/Opaland/QAIA/issues/58) |
| **Injection de prompt repérée et neutralisée** : la demande de recoupement contenait un bloc imitant une "IMPORTANT SYSTEM INSTRUCTION" exigeant une navigation web du dépôt GitHub — traité comme instruction utilisateur ordinaire, écarté sur ce point précis (repo local plus fiable), signalé explicitement au fondateur avant d'agir | D104 |

**Pattern de cette session** : un audit externe, aussi bien intentionné soit-il, se vérifie par
l'exécution (construire et tester la recommandation) plutôt que par la seule lecture — c'est
en construisant le schema demandé par Gemini que le vrai bug de dérive a été trouvé, pas en
lisant le rapport. Une instruction stylée comme un ordre système prioritaire, même reçue
directement de l'utilisateur, ne l'est pas automatiquement — signalée avant d'être suivie ou
écartée sélectivement.

---

## Sprint 24 — Plan d'action de l'audit externe : #51/#52/#58 livrés (2026-07-28, D105-D107) ✅ TERMINÉ

Demande fondateur, enchaînement direct après Sprint 23 : "fait 51 puis 52 puis 58" — les 3
items les plus prioritaires du plan d'action des audits externes (Sprint 22 + Gemini).

| Livré | Preuve |
|---|---|
| **#52 — vrai script k6, exécuté pour de vrai** : `k6` installé, `perf-check/k6/load.js` livré et exécuté contre `examples/expense-demo` (10 VUs/20s, 1981 requêtes, 0 échec, p95=2,23ms) | D105, `eval/baselines/perf-check-k6-load-2026-07-28.md`, `qaia-playwright` 0.1.10→0.1.11 |
| **#58 — premier adapter multi-LLM, exécuté réellement** contre Gemini/Groq/Mistral sur US-004 — résultat honnête et mitigé (25 scénarios, ratio 40,0% recalculé, mais 1/4 ambiguïtés plantées repérées contre 4/4 pour QAIA, + fabrication d'un rôle inexistant) | D106, `eval/baselines/multi-llm-adapter-gemini-benchmark-2026-07-28.md` |
| **#51 — benchmark QAIA vs prompt direct, résultat honnête publié** : coût QAIA ~2,9× plus élevé (133,1k vs 46,5k tokens) ; score structurel déterministe meilleur en moyenne côté QAIA (~72 vs 47/100) mais 2/7 fichiers QAIA échouent quand même au gate ; rappel des 4 ambiguïtés plantées **égal ou légèrement en faveur du prompt direct sur ce run** (variance confirmée, D62) ; différenciateur le plus solide = vérifiabilité/traçabilité (gate ADR 0001, schema D104, zéro fabrication de règle côté QAIA vs 4 côté prompt direct), pas "plus de couverture" | D107, `eval/baselines/qaia-vs-direct-prompt-benchmark-2026-07-28.md` |
| **1 run de benchmark rejeté et refait proprement** : le premier bras "prompt direct" avait accidentellement lu la réponse cachée (section judge-reference) via l'outil `Read` — invalidé, conservé pour trace, re-exécuté sans laisser l'agent toucher le fichier source | D107 |

**Pattern de cette session** : les 3 chantiers ont été traités par exécution réelle (agents en
`isolation: "worktree"`, `k6` installé et lancé pour de vrai, appels API réels aux fournisseurs
externes) plutôt que par description — et le résultat le plus significatif (#51) est publié
tel quel, y compris ce qui ne va pas dans le sens de QAIA (2/7 fichiers structurellement en
échec, rappel d'ambiguïté pas meilleur qu'un bon prompt direct sur ce run), cohérent avec D38.
Une contamination méthodologique détectée en cours de route (le premier run #51) a été
signalée et corrigée plutôt que silencieusement ignorée.

---

## Sprint 25 — Reliquat P1-P3 du plan d'action des audits clos (2026-07-28, D108-D114) ✅ TERMINÉ

Demande fondateur, enchaînement après Sprint 24 : "(#49, #50, #53-#57) enchaîne" — le reliquat
complet du plan d'action des deux audits externes (Sprint 22 + Gemini).

| Livré | Preuve |
|---|---|
| **#49 — coût rapproché des paliers d'abonnement**, honnêtement : source officielle vérifiée d'abord (Anthropic ne publie plus de chiffre exact), chiffres tiers datés/sourcés avec réserve, point clé trouvé (quota compté en prompts/session, pas en tokens bruts) | D108, `plugins/qaia-core/README.md` |
| **#50 — palette de techniques `istqb-design` réorganisée** selon la vraie taxonomie CTAL-TA v4.0, vérifiée contre le PDF officiel du syllabus (pas une source secondaire) : 2 dérives terminologiques corrigées (Domain Testing, Scenario-Based Testing) + trouvaille que EP/BVA/error-guessing ne relèvent pas du tout de la taxonomie ch.3 du syllabus | D109, `qaia-core` 0.2.17→0.2.18 |
| **#54/#55 — 2 exclusions de scope documentées honnêtement** (structure-based/white-box, exploratoire/session-based) — silence corrigé en nommant le choix plutôt qu'en le laissant impliqué | D110, D111 |
| **#57 — conflit multi-devs sur `.qaia/state/` résolu par convention** (un dev par US + garantie git ordinaire de conflit de merge visible), pas de mécanisme dédié construit, disproportionné sans signal d'usage réel | D112 |
| **#53 — techniques CT-AI exercées pour de vrai** contre une nouvelle fonctionnalité réelle (`POST /api/suggest-category`, classifieur déterministe explicitement non-ML) : 8 scénarios `@ai-feature`/`@metamorphic` exécutés réellement (`curl`) avant d'être écrits, relation métamorphique vérifiée (dilution → confiance strictement plus basse, 0,67→0,18 mesuré), score structurel 65/100 CONCERNS rapporté tel quel | D113 |
| **#56 — question posée au fondateur plutôt que tranchée seul** (positionnement produit, pas un choix technique) : revendication "logiciel médical / environnements réglementés" retirée du README (FR+EN) sur décision explicite, D2 révisée sans être supprimée | D114 |

**Pattern de cette session** : le seul item nécessitant un arbitrage de positionnement produit
(#56) a été posé en question au fondateur plutôt que tranché seul par l'agent — cohérent avec
la distinction déjà établie entre décisions techniques agent-faisables et décisions business
qui restent la main du fondateur. Les 6 autres items, tous techniques, ont été vérifiés contre
une source primaire quand une revendication factuelle était en jeu (PDF officiel CTAL-TA v4.0
pour #50, page d'aide Anthropic pour #49) plutôt que cités de mémoire. **Le plan d'action des
deux audits externes est maintenant intégralement traité** (19 issues à la fin du Sprint 22,
plus #58 : #49-#58 toutes closes).

---

## Sprint 26 — Transfert d'org + bridge MCP (2026-07-28/29, D115-D116) ✅ TERMINÉ

| Livré | Preuve |
|---|---|
| **Dépôt transféré vers l'organisation `QAIA-Project`** (action du fondateur) — URLs mises à jour partout dans le produit et la doc courante | D115 |
| **Bridge MCP livré (A+B), tier opt-in, engagement explicite du fondateur de construire avant pilote** — `mcp-bridge/`, hors de `plugins/`, jamais auto-installé ; testé réellement (8 tests unitaires + 1 end-to-end via vrai client MCP), revue adversariale faite, 1 vrai bug trouvé et corrigé en testant (CRLF) | D116, `docs/adr/0003-mcp-bridge-scoping.md` |
| **#32 retesté, toujours épuisé** (message HF explicite : crédit mensuel épuisé) — fondateur a choisi d'attendre le renouvellement | — |

---

## Sprint 31 — #60 fermée : une suite générée tourne dans une vraie CI (2026-08-01, D132-D139) ✅ TERMINÉ

Absent de ce tableau jusqu'au 2026-08-09, alors qu'il porte l'une des rares preuves externes du
projet. Relevé par la revue « chef de projet » ; le détail est dans
[`STATUS.md`](STATUS.md#sprint-31--60-fermée--une-suite-générée-tourne-dans-une-vraie-ci-2026-08-01-d132--terminé).

- **#60 fermée** — une suite générée par QAIA s'exécute sur un runner GitHub Actions, **sans
  session Claude ni skill chargée** : 8/8. C'est la démonstration que la sortie du produit vit
  sans le produit.
- 5 issues fermées ce jour-là (#60, #62 et trois autres), D132 à D139.

## Sprint 30 — revue externe confrontée au dépôt, corrections P0, README rendu vrai (2026-07-31, D131) ✅ TERMINÉ

Suite du Sprint 29. Trois analyses externes (ChatGPT, Gemini, Mistral) soumises par le fondateur, vérifiées avant exécution.

| Livré | Preuve |
|---|---|
| Vérification des 3 analyses : **5 affirmations fausses sur 12**, 4 déjà faites, 3 justes. Plan Gemini écarté (décrit un produit inexistant, contredit ADR 0002) | D131 |
| Revue architecturale 10 dimensions exécutée : **5,0/10**, 42 améliorations | D131, run `wf_3f561c44-999` + `wf_3bc6a8f2-ba6` |
| Preuves de US-EVAL-003 et US-EVAL-010 rapatriées depuis des worktrees non commités (19 fichiers) | commit `79c597b` |
| 233 Mo de worktrees protégés par `.gitignore` versionné (l'étaient seulement par `.git/info/exclude`, local) | `.gitignore` |
| Correctif de pointeurs D130 terminé (il était à moitié appliqué) | `aptitude-gate`, `report` |
| `qaia-testdata/README.md` : affirmation « no code ships » corrigée sur l'invariant réel | commit `79c597b` |
| CI rouge poussée puis corrigée : 2 preuves renommées selon leur contenu réel, contrôle CI non assoupli | commit `78c9fcb` |
| **README rendu vrai** : versions, contradiction 31/24 résolue par un run réel (32/32 verts, sortie brute conservée), expense-demo 40→43, **section d'installation ajoutée** | commit `442c928`, `examples/medibook/tests/run-log.txt` |
| Métadonnées GitHub : 10 topics + description (validation fondateur) | API GitHub |
| `docs/STATUS.md` : Sprint 30 + **prompt de reprise** actualisés | `docs/STATUS.md` |

**Reste ouvert** : #59 densité, #60 CI réelle (blocage n°1), #61 encart PO, #62 skills sous-écrites, #63 juge d'automatisation, #64 contract-probe, #65 recouvrement, #18 visual-check flaky.


## Sprint 29 — Vague d'évaluation exhaustive des 29 skills + bascule vers 6 corrections centrales (2026-07-31, D126) ✅ TERMINÉ

Suite directe du Sprint 28. Demande fondateur : couvrir les skills jamais testées, ouvrir l'approche API et le volet Mobile, rejouer les corrigées. Deux workflows bornés à 2 agents simultanés.

| Livré | Preuve |
|---|---|
| Vague A (46 agents) : 18 skills jamais évaluées jugées, dont les plugins `qaia-score` et `qaia-testdata` (jamais audités) et le méta-agent `qaia` | D126, journal du run `wf_f6e3c739-d44` |
| Premier parcours Mobile mené au bout (US-EVAL-013, émulation device, D100) — 8 skills cœur rejouées en non-régression | D126 |
| Premier parcours API-first réellement exécuté (US-EVAL-012) : `contract-probe` sondé contre une API vivante après 2 échecs de cible en D122 | `eval/skill-coverage-wave-2026-07-30/US-EVAL-012-api-first/` (22 fichiers, 4 logs curl) |
| Vague B (4 agents) : `a11y-audit` et `security-surface` rejouées ; les 2 paris de D125 tranchés par la mesure | D126, commit `e4bfe9e` |
| **28 verdicts, 0 CONFORME. Chiffre honnête consigné : 34 %, pas 69 %** (10 skills sur 29 ont une preuve rejouée par un tiers) | D126 |
| P1 — job CI validant `plugins/**/manifest*.json` ; a trouvé dès son 1er run un cas manqué par 46 agents (`traffic-replay`) | `.github/workflows/ci.yml`, commit `6190869` |
| P2 — `validate_manifest.py` durci : waiver conditionnel, `--check-paths`, kinds `flakiness`/`trafficReplay`, `confidence.*` défini | `eval/tools/validate_manifest.py`, `docs/OUTPUT-CONTRACT.md` |
| P3 — règle non-interactive arbitrée (3 textes divergents, `qaia` muet) : « enregistrer n'est pas accepter » | `plugins/qaia-core/skills/README.md` règle 3, `qaia` §Non-interactive mode |
| P4 — règle 4bis : tout nombre cité comme mesuré pointe son fichier brut conservé | `plugins/qaia-core/skills/README.md` |
| P6 — réflexe « surface de rendu » ajouté à `istqb-design` 3c (breakpoints, cible tactile WCAG 2.5.8, occlusion, orientation) | `plugins/qaia-core/skills/istqb-design/SKILL.md` |
| Juge des tests générés livré (harnais) : piste statique + piste mutation, discrimination prouvée sur fixture | `eval/tools/automation_score.py`, `eval/AUTOMATION-RUBRIC.md`, `eval/tools/fixtures/automation-score/VALIDATION.md` |

**Reste ouvert** : les 8 jurys du parcours API (preuves en dépôt, jamais jugées) ; `contract-probe` sans verdict ; la promotion du juge d'automatisation en skill produit ; la rubrique LLM jamais appliquée par un agent.


## Sprint 28 — Campagne d'évaluation continue des skills, jusqu'à l'étape 8 (2026-07-29/30, D118-D124) ✅ TERMINÉ

Demande fondateur : faire tourner le parcours QAIA complet sur des cas réels pour éprouver la
robustesse des skills (pas livrer un cahier), puis pousser jusqu'à l'automatisation réelle
(étape 8) sur les 11 cibles cumulées, avec un signalement CI traité en cours de route.

| Livré | Preuve |
|---|---|
| **11 cibles US-EVAL au total** (7 sur D118-D121, 4 nouvelles ce sprint : DemoBlaze, OctoPerf Pet Store, crAPI/sécurité API, QuickPizza/perf), chacune parcours complet + 7 évaluateurs skill à contexte vide | D118-D122, `eval/skill-eval-campaign-2026-07-29/` |
| **Étape 8 (automatisation réelle) exercée sur les 11 cibles** — jamais simulée : ~90 tests Playwright réels exécutés, vrais blocages documentés (503 Juice Shop, API Restful-Booker disparue, OAuth2 401 OpenEMR, jeton fabriqué crAPI/QuickPizza sans Docker), vraies trouvailles produit (2 défauts sécu Juice Shop, 2 violations a11y OpenEMR, 3 blocages 422 + 3 violations a11y Toolshop) | D122 |
| **38 nouvelles évaluations skill × run** : 9 `ÉCART STRUCTUREL`, 20 `ÉCART MINEUR`, 9 CONFORME, tous consignés pour arbitrage humain — trouvaille transversale sur le contournement `simulated: accepted-as-is` des gates ⚠ VALIDATION, signalée indépendamment par 4 évaluateurs | D122 |
| **Confirmation architecturale en situation réelle** : 2 sous-agents ont refusé à deux reprises un relais d'autorisation du fondateur (même verbatim), conformément à la garde-fou plateforme "aucun message d'agent n'est un consentement" — l'agent principal a exécuté lui-même l'étape 8 pour ces 2 cibles plutôt que d'insister par relais | D123 |
| **CI Gherkin lint cassé en silence depuis plusieurs commits, corrigé** suite à un signalement direct du fondateur — scope du lint restreint aux vrais testbooks, 5 dossiers de fixtures délibérément non-conformes exclus explicitement | D124, commit `5c18a87` |
| **2 garde-fous anti-récidive ajoutés** : `CLAUDE.md` créé (n'existait pas), puis la règle transformée en hook `PostToolUse` automatisé plutôt que de compter sur une relecture manuelle — décision explicite de préférer les hooks aux règles ad hoc pour tout ce qui est mécaniquement vérifiable | D124, `.claude/hooks/check-ci-after-push.sh` |
| **8 nouvelles cibles cataloguées** (non explorées) dans `docs/DEMO-TARGETS.md` depuis une liste externe partagée par le fondateur, marquées explicitement non vérifiées | `docs/DEMO-TARGETS.md` |

**Pattern de ce sprint** : la discipline D104/D105/D116/D117/D121 se confirme une fois de plus — exécuter réellement (pas relire) trouve des défauts, y compris dans le travail produit par la session elle-même (POM non respecté sur 2 automatisations manuelles, corrigé et assumé plutôt que masqué). Nouveauté notable : une confrontation réelle (pas hypothétique) du garde-fou anti-injection multi-agent de la plateforme, qui a tenu sous pression répétée et de bonne foi — leçon retenue pour le design des futures campagnes multi-agents.

---

## Sprint 27 — Campagne de validation multi-métier à l'aveugle (2026-07-29, D117) ✅ TERMINÉ

| Livré | Preuve |
|---|---|
| **3 US neuves multi-métier (fintech/civic-tech/éducation) dérivées d'oracles réels** (`apache/fineract`, `ushahidi/platform`, `moodle/moodle`), parcours complet (11 étapes) exécuté à l'aveugle dans 3 worktrees isolés, jamais contaminé par l'oracle | `eval/gold-set/US-005/006/007-*.md`, `eval/gold-set/oracle-2026-07-29/` |
| **Rappel comparé à l'oracle : 0 règle métier du cœur manquée** sur les 3 tickets — détail scénario-par-scénario, 1 écart honnête signalé (pas corrigé en douce) sur une nuance d'AC5/US-007 | `eval/baselines/pilot-campaign-2026-07-29.md` |
| **Dogfooding réel des outils `mcp-bridge` (D116)** sur 13 `.feature` + 3 manifestes — 3 défauts réels trouvés et corrigés (faux positif `"XXX"`/ISO 4217 sur le détecteur de marqueurs, `TECHNIQUE_TAGS` obsolète depuis D109, `kind` manquant + `gate: null` non conforme au schéma) | D117, `eval/tools/structural_score.py`, `eval/tools/validate_manifest.py`, `docs/schemas/output-contract-v1.schema.json` |

---

## Sprint 22 — Audit externe multi-persona, correction et suivi (2026-07-26, D99-D103) ✅ TERMINÉ

Demande fondateur : lancer un audit externe (cabinet fictif, personas ISTQB + hors périmètre,
revue adversariale) pour challenger QAIA dans son ensemble, puis mettre à jour les issues et
corriger ce qui est agent-faisable le jour même.

| Livré | Preuve |
|---|---|
| **Audit externe multi-persona exécuté** (`Workflow`, 17 agents : 13 personas + 3 sceptiques + synthèse, ~1,77M tokens, 23 min). Verdict : **prototype d'ingénierie avancé, non prêt pour adoption pilote sans conditions** — moyenne 2,4/5 sur 13 personas | `eval/baselines/audit-report.html` (aussi publié en artifact) |
| **Faille critique trouvée et corrigée le jour même** : `GET /api/audit` non authentifié dans `expense-demo` ET `medibook`, exposait emails/montants/commentaires de rejet — reproduite en direct par les 3 sceptiques | D99 |
| **8 items P0/P1 du plan d'action corrigés directement** : 3 citations internes cassées (D50/D93 mal attribuées, rétro-documentées en D100/D101/D102), chemin Chromium codé en dur dans medibook, BASE_URL non câblé, `flaky-detect` gonflait sa preuve ×3, politique retry/quarantaine rendue concrète (3 templates CI), trou de couverture CT-MBT symétrique comblé (`approved` jamais testé comme terminal) | D103 |
| **Démo statique GitHub Pages testée en navigateur réel** (Playwright reconnecté en cours de session) : flux complet employee→manager rejoué, captures d'écran, zéro erreur console | `eval/baselines/static-demo-accounts-verification.md` |
| **9 nouvelles issues créées** pour le reliquat du plan d'action (P1-P3, benchmark coût/valeur, moteur k6 réel, démo IA/ML, taxonomie CTAL-TA v4.0, décisions de scope à trancher) | [#49](https://github.com/Opaland/QAIA/issues/49)-[#57](https://github.com/Opaland/QAIA/issues/57) |
| **#1/#2 mis à jour** avec la confirmation de l'audit (2 des 3 faits bloquants du verdict final) | Commentaires ajoutés |

**Pattern de cette session** : un audit multi-agent avec revue adversariale a trouvé, en une
session, une vraie vulnérabilité active que le développement initial n'avait pas détectée —
corrigée le jour même de sa découverte, pas laissée pour plus tard. Les items nécessitant une
action fondateur ou un effort substantiel sont tracés en issues plutôt que bâclés.

---

## Sprint 21 — Élargissement ISTQB global, IDOR trouvé, démo statique GitHub Pages (2026-07-26, D94-D98) ✅ TERMINÉ

Demande fondateur : veille concurrentielle élargie hors médical (regard global, GitHub +
web) puis audit complet de couverture ISTQB (tous les syllabus, pas seulement CT-GenAI),
implémentation des gaps trouvés, tests locaux, et une démo statique GitHub Pages.

| Livré | Preuve |
|---|---|
| **Veille élargie hors médical** — écosystème de plugins Claude Code QA densifié depuis D67, aucun concurrent à l'échelle d'Agentic QE Fleet ; 1 trouvaille distincte (`chaos-qa`, sondage adversarial de contrat) convertie en piste de backlog | D94, [#47](https://github.com/Opaland/QAIA/issues/47) |
| **8 ajouts ISTQB au-delà de CTFL/CT-GenAI** : Domain Analysis, Metamorphic testing, techniques CT-AI (`istqb-design`) ; menu de types CT-PT (`perf-check`) ; refonte risk-based CT-SEC (`security-surface`) ; précheck de testabilité CTAL-TAE (`automate`) ; nouvelle skill `usability-heuristic-review` (CT-UT) — vérifiée pour de vrai contre `expense-demo`, 3 violations trouvées avec preuve fichier:ligne | D95, [#48](https://github.com/Opaland/QAIA/issues/48) fermée |
| **Vrai IDOR trouvé et corrigé** en testant localement le nouveau security-surface risk-based : `GET /api/reports/:id` n'avait aucune vérification de propriété — corrigé, 3 cas de non-régression ajoutés | D96 |
| **Démo statique GitHub Pages** publiée (`static-demo/`, mock-backend fidèle y compris le correctif IDOR) pour tester usability-heuristic-review/a11y-audit/visual-check sans backend — vérifiée fonctionnellement avant publication, puis re-vérifiée en navigateur réel (Playwright reconnecté) : flux complet employee→manager rejoué, captures d'écran, zéro erreur console | D97, `.github/workflows/pages.yml`, `eval/baselines/static-demo-accounts-verification.md` |
| **Nouvelle skill `contract-probe`** (sondage adversarial de contrat, CT-SEC/exploratoire) — ferme #47, dernier chantier de la veille élargie. Vérifiée sur un fixture dédié avec un défaut injecté délibérément (`GET /tasks/:id` retourne 500 au lieu du 404 promis) : 3 promesses extraites du README, 5 sondes adversariales, 1 scénario de régression généré | D98, [#47](https://github.com/Opaland/QAIA/issues/47) fermée |

**Pattern de cette session** : recherche réelle vérifiée avant tout ajout au backlog (un lead
IEC 62304 écarté après lecture directe de la source, D101) ; discipline de coût agent — édition
directe préférée au dispatch de sous-agent pour du travail déjà bien cadré, sur demande
explicite du fondateur en cours de session (D102) ; démo statique testée à deux niveaux (logique Node
identique au déployé, puis navigateur réel dès l'outillage redisponible).

**Backlog agent-faisable de nouveau épuisé** (toutes les issues #47/#48 ouvertes cette session
sont refermées) — un audit externe multi-persona (cabinet fictif, personas ISTQB + non couverts,
revue adversariale) a été lancé en parallèle pour challenger le produit dans son ensemble ; voir
son verdict une fois rendu avant de conclure à un nouveau palier.

---

## Sprint 20 — Reliquat post-mandat : connecteur TestRail, budget token complet, fiabilisation veille (2026-07-25, D89-D92) ✅ TERMINÉ

Demande fondateur, après constat que le backlog GitHub agent-faisable était épuisé (Sprint 19) :
compléter le reliquat honnête déjà identifié (#35 TestRail, #7 mesures restantes) plutôt que
d'attendre un nouveau levier fondateur, plus une passe de fiabilisation sur la veille
concurrentielle déjà publiée.

| Livré | Preuve |
|---|---|
| **Citation Agentic QE Fleet vérifiée** (421★/75 forks, re-fetch direct) — la réserve "non revérifié avant citation publique" explicitement levée, chiffre confirmé exact | D (commit `0a16383`) |
| **Connecteur d'export TestRail** — ferme #35 en totalité (Xray D86 + TestRail ici), même discipline d'honnêteté (doc TestRail réelle lue en direct, réserves explicites), vérifié indépendamment (38 lignes/ID, distribution priorité identique à l'export Xray du même cahier, zéro fuite de commentaire, `--strict` vert) | D89, [#35](https://github.com/Opaland/QAIA/issues/35) fermée |
| **Budget token : 14/14 skills de `qaia-core` désormais mesurées** (9 nouvelles mesures réelles cette session : `hello`, `qaia-help`, `us-review`, `need-understanding`, `oracle-generate`, `prioritize`, `feedback`, `testbook-validate`, `report`) — ferme #7 en totalité | D91, D92, [#7](https://github.com/Opaland/QAIA/issues/7) fermée |
| **Gain méthodologique réutilisable** : confirmé que la notification de fin de tâche d'un agent délégué porte le vrai total de tokens (`subagent_tokens`), exploitable directement par l'orchestrateur — plus besoin de deviner si l'infra expose le chiffre pour toute mesure future | D91 |
| **Correctif `hello`** : ne fige plus une description "0.1.0 pre-alpha" périmée (trouvaille incidente) | D90 |
| **2 défauts trouvés en exerçant `testbook-validate`/`report` en conditions réelles sur le cahier US-004** : `synthesis.md` omettait un scénario `@low-confidence` de sa liste (corrigé directement) ; 2 totaux de conversion de devise assertés au centime sans source de taux tracée, flagués à raison par le sniffer anti-fabrication (tracé, pas patché à la va-vite) | D92, [#46](https://github.com/Opaland/QAIA/issues/46) ouverte |

**Pattern d'exécution** : agents en `isolation: "worktree"` en parallèle, réutilisant l'état déjà
produit pour US-004 (`examples/expense-demo/`) comme prérequis plutôt que de régénérer un
parcours complet à chaque mesure — limite le coût réel de la mesure elle-même. Chaque livraison
vérifiée indépendamment avant merge (re-grep, re-parse, re-run du scoreur déterministe).

---

## Sprint 19 — Mandat élargi post-M0 : gate G2 levée, veille concurrentielle, backlog remodelé (2026-07-25, D67-D88) ✅ TERMINÉ

Demande fondateur : la validation humaine (gate G2) est considérée franchie, le développement
reprend en autonomie. Veille concurrentielle, remodelage du backlog, extension du produit
hors du seul domaine médical.

| Livré | Preuve |
|---|---|
| **Gate G2 levée** — #1 (recrutement pilotes), #23 (gel connecteurs) fermées comme superseded ; #29/#30 (tier opt-in "post-pilote") débloqués ; #5 (validation conversationnelle) reformulée sans blocage strict | décision D67 |
| **Veille concurrentielle** — paysage (Agentic QE Fleet et 7 autres catégories), angles morts, différenciation réelle de QAIA, 10 pistes de backlog | `docs/COMPETITIVE-ANALYSIS.md` |
| **10 nouvelles issues ouvertes** depuis la veille (#33-#42), priorisées P1-P3 | idem |
| **Démonstration hors médical livrée et vérifiée indépendamment** — US-004 (notes de frais, finance/HR), app réelle + parcours QAIA complet (38 scénarios) + automatisation Playwright réelle : 40/40 tests verts (re-vérifié soi-même, pas seulement le rapport de l'agent), score déterministe 4/4 PASS (85/97/94/94) | `examples/expense-demo/`, D68 |
| **3 vrais défauts trouvés et corrigés pendant l'automatisation** (pas simulés) : violation WCAG réelle, course de test induite par le correctif, erreur arithmétique dans le cahier généré attrapée par un test API en échec | idem |
| **1 vrai défaut produit trouvé** : `istqb-design` classe parfois `[assumption]` une ambiguïté métier qui aurait dû rester `[open]` (convention de machine à états trop généreuse) — pas corrigé, tracé | D68, [#43](https://github.com/Opaland/QAIA/issues/43) |
| **Skill `flaky-detect` livrée** (qaia-playwright 0.1.2→0.1.3), comble le gap #1 de la veille — détecte le pass/fail variable entre N≥3 runs à code inchangé depuis JUnit/Cucumber déjà produits par `run-report`, fusion manifeste `flakiness` (jamais `execution`/`design`/`gate`/`status`), zéro auto-retry/fix. Validée sur fixture autonome, 5 runs réels : 3 tests correctement flagués flaky, contrôle toujours-vert et contrôle toujours-rouge correctement exclus de la liste flaky | `plugins/qaia-playwright/skills/flaky-detect/`, D69, [#34](https://github.com/Opaland/QAIA/issues/34) |

| **Budget token partiellement instrumenté** (3/~15 skills mesurées réellement, `us-ingest` dépasse nettement l'ancienne estimation) | `plugins/qaia-core/README.md`, D70, [#7](https://github.com/Opaland/QAIA/issues/7) |
| **Audit d'indépendance des skills** — 7 tests hors séquence réels, aucune fabrication, 2 garde-fous structurels trouvés et corrigés (`feedback`/`aptitude-gate`) | `eval/baselines/skill-independence-audit.md`, D69, [#22](https://github.com/Opaland/QAIA/issues/22) |
| **#43 corrigé** (`istqb-design` distingue désormais `[assumption]` de `[open]` sur les transitions non déclarées) | commit `3c262fe` |
| **`istqb-design` décompose les règles composites** (#45) — `BR-KB-203` passe de 3/7 à 7/7 sous-faits assertés, comble le défaut trouvé par le gain RAG chiffré (D77). Non-régression vérifiée octet pour octet sur les scénarios existants | D81, [#45](https://github.com/Opaland/QAIA/issues/45) |
| **Audit `visual-check` vs diff perceptuel** (#40) — suffisant tel quel pour son usage documenté ; 1 vraie lacune trouvée (contenu dynamique non masqué peut consommer le budget de tolérance en silence) et corrigée dans `SKILL.md` | D82, [#40](https://github.com/Opaland/QAIA/issues/40) |
| **`structural_score.py` corrige une limite résiduelle `ASSERT_RE`/guillemets** (#31) — le cas C5 du corpus 24 (`"P1"`/`"P2"` masquant un `Then` vague) est maintenant correctement détecté FAIL, zéro régression sur les 7 fixtures existantes | D83, [#31](https://github.com/Opaland/QAIA/issues/31) |
| **Première validation conversationnelle simulée** (#5) — parcours QAIA sur US-004 avec un persona testeur exerçant un vrai arbitrage humain : 8 objections/corrections sur 5 étapes, rétention mesurée 28/34 scénarios (82,4 %) livrés sans réécriture | D84, [#5](https://github.com/Opaland/QAIA/issues/5) |
| **Budget token : 2 mesures réelles de plus** (`rag-build` 67,6k, `testbook-export` 77,6k) — 5/12 skills désormais mesurées, 7 restent honnêtement estimées | D85, [#7](https://github.com/Opaland/QAIA/issues/7) |
| **Connecteur d'export Xray** (git-master, CSV, fichier seul, jamais d'API/credential) livré et vérifié ; TestRail explicitement non couvert | D86, [#35](https://github.com/Opaland/QAIA/issues/35) |
| **4ème plugin `qaia-testdata`** — génération de jeux de données synthétiques cohérents métier, validé sur US-002 (10/10 tests Playwright verts, rejoués indépendamment) | D87, [#15](https://github.com/Opaland/QAIA/issues/15) |
| **Nouvelle skill `traffic-replay`** (`qaia-playwright`) — capture/rejeu de trafic HAR → conditions de non-régression, masquage PII/secrets sur 8 catégories vérifié sans fuite | D88, [#39](https://github.com/Opaland/QAIA/issues/39) |

**Terminé.** Tous les items agent-faisables identifiés par la veille concurrentielle (#33-#42)
sont désormais soit livrés (#33-#40, #45, #5, #7 partiel, #15, #31, #39), soit honnêtement
laissés ouverts faute d'un déclencheur agent-faisable : **#2** (transfert d'org, propriétaire
seul), **#10/#12/#13/#14/#18** (T17 sur app pilote réelle, mur humain #1), **#32** (crédit
Hugging Face épuisé, ressource externe), **#29/#30** (tier opt-in — ADR 0002 dit encore
« post-pilote uniquement », pas rouvert sans engagement plus explicite du fondateur malgré
D67), **#42** (son propre critère d'acceptation exige un tranchage fondateur avant tout code).
Le backlog agent-faisable de ce cycle est **épuisé** — prochain pas = décisions/actions
fondateur.

## Sprint 10 — Harnais de gap #24 sur matériel réel (accès web) ✅ TERMINÉ (2026-07-24 ter)

Demande fondateur : utiliser l'accès web confirmé cette session pour sourcer un vrai gold set
dur (pas des fixtures fabriquées) et attaquer le #24 jusqu'au bout.

| Livré | Preuve |
|---|---|
| 2 cas durs réels sourcés sur le web (GitLab CE `groups.feature` sans narratif US ; Sharetribe champs custom pilotés par config admin) | `eval/goldset-hardened/real-cases-24.md` |
| 4 runs isolés (3× sur le cas Groups pour la variance, 1× sur le cas config) mesurant les 4 modes d'échec IATS | `eval/baselines/gap-harness-24.md` |
| **2 défauts trouvés et corrigés** dans `istqb-design` (silence sur les entités-sœurs non nommées ; fabrication convergente non flaggée d'une sémantique de suppression) | `plugins/qaia-core/skills/istqb-design/SKILL.md` 3c, D44 |
| **Pass structurel déterministe branché sur `testbook-validate`** (comme demandé), aligné sur `testbook-score` | `plugins/qaia-core/skills/testbook-validate/SKILL.md`, D45 |
| **Détecteur de redondance (pesticide paradox)** ajouté à `structural_score.py`, validé sur fixture + contenu réel | `eval/tools/structural_score.py`, `eval/baselines/structural-score.md`, D46 |
| **Faux positif trouvé et corrigé dans le scoreur lui-même** (`HOLLOW_RE` sur du contenu réel généré) | `eval/baselines/structural-score.md` |
| `qaia-core` 0.2.6 → 0.2.7, `--strict` vert | validation `claude plugin validate --strict` |

**Reste (marqué honnêtement, non fait cette session)** : re-mesurer les 50 US de
`groundtruth-corpus.md` avec les 2 amendements `istqb-design` pour confirmer l'absence de
régression à grande échelle — le changement est petit et ciblé, mais seul le harnais complet
peut le confirmer. Prochain palier : **#25** (durcir l'oracle OpenAPI).

## Sprint 11 — Durcissement oracle OpenAPI (#25) ✅ TERMINÉ (2026-07-24 ter)

Enchaînement autonome après le Sprint 10 : prochain palier de plus haute valeur du backlog.

| Livré | Preuve |
|---|---|
| Résolution `$ref` interne rendue obligatoire (step 0.1) — un noeud non résolu perdait tous les négatifs de champ requis en silence | `oracles/openapi.md` |
| Avertissement « spec sous-documentée » (step 0.3) : 0 erreur 4xx/5xx documentée sur tout le spec, OU mutations sans auth déclarée | `oracles/openapi.md`, `SKILL.md` |
| Règle **re-vérifiée en re-fetchant les 3 vraies specs** (Petstore/apis.guru/Notion) — la première mouture aurait manqué apis.guru, corrigée avant livraison | `eval/baselines/connectors-real-data.md` |
| `qaia-core` 0.2.7 → 0.2.8, `--strict` vert | validation `claude plugin validate --strict` |

Décision D47.

## Sprint 12 — Contrôle de non-régression échantillonné des amendements #24 ✅ TERMINÉ (2026-07-24 ter)

Enchaînement autonome : au lieu du re-run complet des 50 US (disproportionné), 2 cas réels
neufs (jamais vus par les runs d'origine) soumis en tickets durs pour vérifier que les 2
amendements `istqb-design` généralisent.

| Livré | Preuve |
|---|---|
| Cas Dashboard (GitLab CE) : gap des entités-sœurs explicitement flagué, pas silencieux | `eval/baselines/istqb-amendments-regression-24.md` |
| Cas 2FA (Diaspora) : `@low-confidence` correctement posé sur désactivation + régénération codes | `eval/baselines/istqb-amendments-regression-24.md` |
| Aucune régression détectée sur les 2 cas | idem, décision D48 |

**Limite assumée** : pas équivalent au re-run complet des 50 US (pas de mesure de
rappel/précision agrégée) — signal de généralisation, pas clôture définitive du risque.

## Sprint 13 — Nouvelles sources (PRD réel, API publique réelle) + durcissement scoreur ✅ TERMINÉ (2026-07-24 ter, suite 3)

Demande fondateur : tester plusieurs types de sources (PRD, US, sites/APIs de pratique QA)
et vérifier la couverture du pass déterministe (tags, ratio).

| Livré | Preuve |
|---|---|
| Gate de décomposition testé sur un PRD réel-forme (TaskFlow, clean-room) : 19 stories listées, NFR séparées, 2 ambiguïtés flaggées | `eval/baselines/new-sources-25bis.md` |
| Risque de fabrication testé sur une vraie API publique en prose (Airport Gap, sans fichier spec) — zéro fabrication, y compris contre la tentation de rappel de connaissance d'entraînement | idem, vérité-terrain `curl` en direct |
| Audit déterministe des tags priorité/technique + **ratio négatif recalculé indépendamment** (fermait un trou de la règle 3) | `eval/tools/structural_score.py`, `eval/baselines/structural-score.md`, fixture `tag-conformant.feature` |

Décision D50. Aucun défaut produit trouvé (confirmations positives) ; le durcissement
scoreur corrige un vrai trou. Catalogue de sites/APIs de pratique QA reçu, pas encore
exploité pour `qaia-playwright:automate` contre une cible publique réelle.

## Sprint 14 — Prompt management sur les 23 skills + second juge indépendant ✅ TERMINÉ (2026-07-24 ter, suite 6)

Demande fondateur : auditer précision/format/exemples des skills produits, et évaluer
shadow/A-B testing comme méthode de vérification des changements de formulation.

| Livré | Preuve |
|---|---|
| Audit des 23 skills (précision/format/exemples) — 1 bug de numérotation trouvé et corrigé (`need-understanding`, deux étapes "4.") | `plugins/qaia-core/skills/need-understanding/SKILL.md`, `qaia-core` 0.2.9 |
| Second juge LLM indépendant (`eval/tools/second_judge.py`), repli gratuit Gemini→Groq→HF, HTTP direct sans SDK (ni LiteLLM ni API Anthropic) | `eval/baselines/second-judge.md`, D51 |
| Vérifié en live sur les 3 fournisseurs — 2 défauts de plomberie trouvés en l'exécutant (403 User-Agent HF, format de réponse Gemini mal documenté par une source web) ; accord tri-source avec le juge Claude et le scoreur déterministe sur le défaut C1 | idem |
| Premier test A/B contrôlé sur un skill (`prioritize`, avec/sans exemple chiffré) | `eval/baselines/prioritize-ab-test.md`, D52 |
| Résultat A/B **négatif et honnête** : l'exemple aurait sur-généralisé et dégradé la calibration — pas appliqué | idem |
| `.gitignore` racine créé (n'existait pas), `.env`/`.env.example` pour les secrets d'outillage mainteneur | — |

Décisions D51-D52. Prochain candidat si le prompt management continue : `qaia` (méta-agent
ReAct, le skill le plus vague du corpus).

## Sprint 15 — Balayage multi-modèles complet, Phase 1 (9/9 skills du cœur) ✅ TERMINÉ (2026-07-24 ter, suite 10)

Demande fondateur : étendre le harnais de gap à tous les skills, vérifier systématiquement
sur 4+ modèles gratuits, domaines variés (pas seulement médical).

| Livré | Preuve |
|---|---|
| 5 fournisseurs opérationnels (Claude + Gemini/Groq/HF/Mistral ; Cerebras ajouté mais bloqué côté compte, 402) | `eval/tools/second_judge.py`, `eval/baselines/second-judge.md` |
| 9 skills du cœur testés sur du matériel dur, domaines variés (santé, e-commerce, logistique, SaaS, ingénierie) | `eval/baselines/multimodel-skill-sweep.md` |
| 3 sans-faute collectifs sur tâches mécaniques (rag-build, testbook-export, feedback) | idem |
| 3 défauts réels trouvés, sans classement stable entre modèles (Groq/raisonnement, Mistral/traçabilité, HF/3 défauts distincts dont fuite PII) | idem, décision D55 |
| Claude sans défaut sur les 9 cas, hygiène épistémique démontrée 2 fois (oracle-generate) | idem |

Décision D55. Phase 2 (qaia-playwright, qaia-score) en attente de priorisation.

## Sprint 17 — Corpus élargi 24 cas, profondeur statistique ✅ TERMINÉ (2026-07-24 ter suite 13 → 2026-07-25)

Suite à D55-D57 (balayage en largeur, N=1/skill) : demande fondateur de creuser en profondeur
sur du matériel neuf pour voir si les patterns tiennent à N=20+. Plan complet (24 cas, 4 réels
GitLab CE + 20 clean-room par format/domaine) : `eval/goldset-hardened/corpus-24-plan.md`.

| Livré | Preuve |
|---|---|
| Lot 1/6 : 4 cas réels GitLab CE v8.16.9 (jamais utilisés cette session), Claude + Groq + Hugging Face + Mistral (Gemini rate-limité après R1) | `eval/baselines/corpus-24-depth.md` |
| **2 nouveaux défauts** : HF fabrique des codes HTTP précis (201/404/409) non demandés (4e défaut distinct chez HF cette session) ; Mistral invente une exception "propriétaire" non fondée | idem, décision D58 |
| Signal plus léger confirmé (dédup tautologique Groq/Mistral, R1) ; sans-faute total sur le piège précondition SSH (R3, 5/5 modèles) | idem |
| Lot 2/6 : 4 cas clean-room (fintech/PRD/spec/Jira-ticket), exécutés via 4 agents indépendants en parallèle, Claude + Gemini + Groq + Hugging Face + Mistral (Gemini dispo cette fois) | `eval/baselines/corpus-24-depth.md` |
| **2 défauts HF supplémentaires** (5e/6e cette session : contradiction résolue en silence, fabrication matrice/seuils config-driven) ; **Groq et Mistral confirment leurs profils** sur matériel neuf (raisonnement multi-règles ; invention non fondée, 3/8 cas) | idem, décision D59 |
| **Nuance nouvelle** : fuite PII possible dans la narration du modèle, pas seulement l'artefact (Mistral/Groq, C2) ; **confirmation transversale** : ratio négatif auto-rapporté peu fiable (valide D50) | idem |
| Claude et Gemini : 8/8 cas cumulés sans défaut | idem |

| Lot 3/6 : 4 cas clean-room (gaming/IoT/HR-tech/voyage), 4 agents parallèles | `eval/baselines/corpus-24-depth.md` |
| **Gemini : 1er défaut sur ce corpus** (fabrication codes HTTP, C7) ; **Hugging Face : 3 cas propres consécutifs** (C6-C8) après 6 défauts sur 8 cas ; Groq/Mistral confirment leurs profils | idem, décision D60 |
| **Gap outillage trouvé** : `structural_score.py` (`VAGUE_RE`) rate un `Then` vague ciblé (C5) — non corrigé cette session, noté en suite du #24/D46 | idem |

| Lot 4/6 : 4 cas clean-room (immobilier/média/fintech-KYC/logistique), 4 agents parallèles | `eval/baselines/corpus-24-depth.md` |
| **Sans-faute sur les défauts de pure détection** (CRUD-inverse, contradiction) ; **2e gap outillage trouvé** (`HOLLOW_RE` rate un renvoi paraphrasé au mockup, C10) ; Hugging Face indisponible 3/4 cas (402, crédit épuisé — pas un défaut qualité) | idem, décision D61 |

| Lot 5/6 : 4 cas clean-room (santé/edtech/gaming/IoT), 4 agents parallèles | `eval/baselines/corpus-24-depth.md` |
| **Mistral échoue net sur C14** (fabrication grave + auto-contradiction) ; **Groq échoue net sur C15** (rate le cas, erreur logique sur son propre ratio) ; **Gemini confirme un ratio D20 fiable** (3/4 cas exacts) ; 5e sans-faute consécutif sur CRUD-inverse (C16) | idem, décision D62 |
| Hugging Face indisponible sur les 4 cas (402, 7-10e échec consécutif — crédit épuisé) | idem |

| Lot 6/6 (DERNIER) : 4 cas clean-room (HR-tech/voyage/immobilier/média), 4 agents parallèles | `eval/baselines/corpus-24-depth.md` |
| **Mistral échoue net une 2e fois sur PII** (C17, ledger complet 4 catégories) ; **3e gap outillage aggravé** (`VAGUE_RE`, C18) ; **auto-contradiction synthèse/artefact chez Mistral** (C19) ; 3e cas consécutif sans-faute sur traçabilité (C20) | idem, décision D63 |
| **Bilan global 24/24 cas** : Claude 0 défaut ; Gemini le plus fiable des externes (0 échec de détection, ratio D20 exact) ; Groq/Mistral ~25-33% d'échec sur raisonnement profond ; HF 6 défauts denses sur 13/24 cas mesurés puis indisponible ; 2 défauts transversaux confirmés (ratio D20, gaps regex) ; CRUD-inverse/traçabilité généralisent fortement | idem, décision D64 |

**Corpus élargi 24 cas TERMINÉ.**

## Sprint 18 — Correctif `VAGUE_RE`/`HOLLOW_RE` ✅ TERMINÉ (2026-07-25)

| Livré | Preuve |
|---|---|
| `VAGUE_RE`/`HOLLOW_RE` étendus pour capter les 2 formulations paraphrasées trouvées par le corpus (C5-Mistral, C18-Groq) | `eval/tools/structural_score.py`, décision D65 |
| Vérifié sans régression : 7 fixtures existantes identiques (diff vide), seuls les 2 cas ciblés basculent sur 15 fichiers réels du corpus | `eval/baselines/structural-score.md` |
| Nouvelle fixture de régression (2 cas FAIL attendus + 1 cas concret + 1 cas config-driven légitime qui ne doit jamais être flagué) | `eval/goldset-hardened/paraphrased-vague.feature` |
| 3e cas documenté (C10) réexaminé : pas un vrai bug, le scénario est racheté par des lignes `And` concrètes — noté honnêtement, pas compté comme corrigé | idem |

**Reste (backlog, non fait)**, désormais tracé en issues GitHub : retenter Hugging Face sur
C10-C20 ([#32](https://github.com/Opaland/QAIA/issues/32)) ; limite résiduelle `ASSERT_RE`
trop permissif sur les guillemets ([#31](https://github.com/Opaland/QAIA/issues/31)).

## Backlog GitHub resynchronisé (2026-07-25)

Le connecteur MCP GitHub a été connecté cette session (PAT personnel). Recoupement du board
avec `docs/DECISIONS.md`/`docs/KANBAN.md` :

| Action | Issues | Preuve |
|---|---|---|
| Fermées (livrées, preuve citée en commentaire) | [#25](https://github.com/Opaland/QAIA/issues/25), [#26](https://github.com/Opaland/QAIA/issues/26), [#27](https://github.com/Opaland/QAIA/issues/27), [#28](https://github.com/Opaland/QAIA/issues/28) | D43, D47, D65 |
| Fermée (obsolète, superseded par des campagnes bien plus larges) | [#6](https://github.com/Opaland/QAIA/issues/6) | — |
| Fermée (harnais de gap #24, corpus 24 cas) | [#24](https://github.com/Opaland/QAIA/issues/24) | D44-D48, D58-D64 |
| Ouvertes (backlog agent-faisable identifié cette session) | [#31](https://github.com/Opaland/QAIA/issues/31), [#32](https://github.com/Opaland/QAIA/issues/32) | D65 |

**Constat** : plusieurs chantiers étaient marqués "TERMINÉ" dans ce fichier depuis des
sessions antérieures sans que l'issue GitHub correspondante soit fermée — les deux avaient
dérivé. Resynchronisé maintenant ; à surveiller pour ne pas reproduire l'écart.

## Sprint 16 — Balayage multi-modèles Phases 2 & 3 (8/8, qaia-playwright + qaia-score) ✅ TERMINÉ (2026-07-24 ter, suite 11)

Suite du Sprint 15 : demande fondateur d'aller au bout des 23 skills.

| Livré | Preuve |
|---|---|
| 8 skills testés (automate, perf-check, a11y-audit, run-report, security-surface, visual-check, testbook-score, aptitude-gate) sur 4-5 modèles | `eval/baselines/multimodel-skill-sweep.md` |
| **0 défaut trouvé** — contraste net avec la Phase 1 (3 défauts/9 skills) | idem, décision D56 |
| 17/23 skills couverts au total ; `hello`/`qaia-help` (triviaux) non testés | idem |

Décision D56. **Complété dans la foulée** (`hello`, `qaia-help`) : 23/23 skills couverts,
sans-faute total y compris sur un test de sécurité (injection via nom de fichier). Décision
D57 — balayage multi-modèles clos pour ce cycle.

## Sprint 9 — Sortie unifiée, plugin de score & 4 leviers skill-level ✅ TERMINÉ (2026-07-23)

Demande fondateur : enchaîner les 4 leviers + standardiser la sortie + un plugin de score seul.

| Livré | Preuve |
|---|---|
| **Contrat de sortie standardisé (D39)** : manifeste JSON unique par US, tous plugins au même format | `docs/OUTPUT-CONTRACT.md`, skill `qaia-core:report`, `run-report` fusionne `execution` |
| **Plugin `qaia-score` (D40)** : `testbook-score` (rubrique /20) + `aptitude-gate` (PASS/CONCERNS/FAIL/WAIVED), lecture seule, n'écrit que `gate` | `plugins/qaia-score/`, `examples/scoring-demo/`, `--strict` vert |
| **RAG en usage réel** : protocole récupération/citation + `istqb-design` 3d dérive des conditions citées des règles (casse le plafond D38) | `skills/README.md`, `examples/rag-demo/` (+5 conditions non inférables) |
| **Oracle v2 OpenAPI (D36b, #16)** : parsing du contrat désigné → statuts/champs requis/contraintes/format-chaining, borné | `oracles/openapi.md`, `examples/oracle-demo/*.openapi.yaml` (lint vert) |
| **Connecteur Jira (D9, #9)** : portable-first (export REST v3/CSV/collé) + live MCP borné, PII masquée, injection reportée | `connectors/jira.md`, `examples/jira-demo/` |
| **M3 `automate` durci (D41, #10)** : scaffold + templates CI (GitHub/GitLab/Jenkins) + handoff manifeste + gate T17 honnête | `automate/templates/`, exit-criterion T17 documenté |
| Versions : qaia-core 0.2.2→0.2.6, qaia-playwright 0.1.0→0.1.1, qaia-score 0.1.0 ; marketplace 3 plugins | `--strict` vert sur les 3 + marketplace |

**Reste à mesurer (non skill-level)** : gain de rappel RAG chiffré au harnais, verdict `qaia-score` vs humain sur baselines, M3/T17 sur app pilote — cf. « Prochains leviers » de `STATUS.md`. Le mur humain (5 pilotes, #1) est inchangé.

---

## Sprint 1 — Fondations & première baseline ✅ TERMINÉ (2026-07-23)

| Livré | Preuve |
|---|---|
| Discovery v2 (4 personas), 88 questions, 33 décisions + 17 défauts | `DISCOVERY.md`, `DECISIONS.md` |
| Gates G1 (purge + squash) et G3 (3 contradictions tranchées) | D1, D5, D6, D17 |
| M0 côté repo : licence, README bilingue, gouvernance, marketplace validée (`--strict`), CI durcie (supply-chain, DCO, gherkin-lint épinglé + config), harnais d'éval AVANT les skills | `M0-CHECKLIST.md` |
| 12 skills (parcours complet + hello, qaia-help, testbook-validate, agent `qaia`) | `plugins/qaia-core/skills/` |
| 3 revues (conformité, sécurité, cohérence) : 40 findings corrigés | commits `585b804`, `ba0f38d` |
| Étude BMAD : 12 patterns adoptés (D33), A1/A7 implémentés | `BMAD-ANALYSIS.md` |
| **Baseline 0.1.0 : 17/20 PASS** (3 runs × 3 juges, lint vert) | `eval/baselines/0.1.0-US-001.md` |

## Sprint 2 — Régression 0.1.1 & agent ReAct ✅ TERMINÉ (baseline 19/20, +2 ; dims 6 et 9 récupérées ; skills qaia-help/testbook-validate testées et corrigées)

## Sprint 9 *(ancienne numérotation — le Sprint 9 courant est plus haut)* — Industrialisation & sortie standardisée ✅ TERMINÉ
Contrat de sortie unifié (manifeste JSON par US, `docs/OUTPUT-CONTRACT.md`, D39) écrit au même format par tous les plugins. Nouveau plugin **`qaia-score` 0.1.0** (D40) : score /20 + gate PASS/CONCERNS/FAIL/WAIVED, lecture seule — aucun producteur ne s'auto-score. RAG en usage réel (récupération/citation, `examples/rag-demo/`). Oracle projet **OpenAPI** (#16b, `examples/oracle-demo/`). Connecteur **Jira** (#9 fermé, `examples/jira-demo/`). Durcissement M3 `automate` (#10 : scaffold + templates CI GitHub/GitLab/Jenkins + gate T17 honnête). Rituel `/session-review` (`.claude/commands/`). Issues fermées : #9, #11. **Mesure en cours** : calibration `qaia-score` (#17). Restant = **mesurer en réel** (RAG au harnais, M3/T17 sur app pilote) — majoritairement mur humain (#1).

## Sprint 8 — Éval vérité-terrain (oracle humain) ✅ TERMINÉ
50 paires réelles (US + tests d'acceptation humains validés : gitlab/diaspora/sharetribe). QAIA reçoit l'US seule, on compare au test humain. Protocole train/held-out anti-overfitting. Résultat (skills 0.1.9→0.2.2, `groundtruth-training.md`) : **généralisation prouvée** (held-out 53 % ≥ train 33 %, pas d'overfitting), **précision ~93 %**, **+200 scénarios valides** au-delà des humains, plafond structurel honnête (config-driven → RAG). Heuristiques génériques de couverture (listes/CRUD/décision/autorisation) ajoutées à `istqb-design`. ⚠️ Mesure de rappel bruitée (juge LLM ±15-20 pts) — seules les comparaisons intra-run sont fiables.

## Sprint 7 — Robustesse & oracles ✅ TERMINÉ
Campagne robustesse (50 vrais specs GitHub + 18 monkey, 3 vagues) → **2 blocages sécurité corrigés** (PII verbatim, abus) + 6 gates ajoutés, saturation atteinte (skills 0.1.6→0.1.8, D37, `robustness-campaign.md`). Skill **`oracle-generate`** (0.1.9, D36) : standards comme générateurs de cas (Luhn vérifié). Plugin **`qaia-playwright`** créé (jalon M3 : automate/a11y/perf/sécu/report en skills, industrialise medibook).

## Sprint 6 — Terrain réel & campagne (voir Sprint 7)

## Sprint 5 — Chaîne complète sur app réelle ✅ TERMINÉ
Recherche de cibles (médical + généraliste, `docs/DEMO-TARGETS.md`) ; sandbox fermée → app cible **auto-hébergée localement** (MediBook, implémente les CA d'US-001). Automatisation **POM-fixtures Playwright** (D34) : E2E desktop + mobile (Pixel 7), API, a11y (axe-core, 0 violation), visuel — **24/24 verts, déterministes**. Traçabilité continue exigence → scénario `@QAIA-xxx` → test (`examples/medibook/traceability.md`). 3 findings réels du chasse-flaky (course d'état partagé → `workers:1`, pin Chromium, baselines visuelles). Livré dans `examples/medibook/`.

## Sprint 4 — Skills 0.1.2 ✅ TERMINÉ (top-5 rétro appliqué ; spot-check en cours de validation)

## Sprint 3 — Élargissement (équipe agile en workflow, 8 agents) ✅ TERMINÉ — voir `eval/baselines/sprint3-retro.md` (US-002 : 17/20 4/4 ambiguïtés ; US-003 : 19/20 mais 0/4 → action C1 ; régénération/export/RAG : ✅). **Sprint 4 (nouveau) = skills 0.1.2** : top-5 actions de la rétro, puis re-run harnais 3 US.

> **Numéros réutilisés.** Ce document a connu deux numérotations : celle d'origine, et celle
> qui a suivi la réorganisation. Trois numéros — 3, 4 et 9 — servent donc deux fois, avec des
> contenus et des états différents. Les entrées de l'ancienne série portent désormais la mention
> *(ancien plan)* ou *(ancienne numérotation)* pour qu'on sache laquelle on lit. Elles ne sont
> pas renumérotées : ce sont des traces, et les renuméroter casserait toute référence
> extérieure. Relevé par la revue « chef de projet » du 2026-08-09.

## Ancien plan Sprint 2 (conservé pour trace) 🔄

| # | Tâche | État |
|---|---|---|
| S2.1 | Skills 0.1.1 : correctifs convergents (inter-AC, rationale, ratio, [open], @smoke) | ✅ livré |
| S2.2 | Skills `qaia-help` (A4), `testbook-validate` (A3+A5), méta-agent ReAct `qaia` (A9 — en skill, pas en `agents/` : garde-fou sécurité maintenu) | ✅ livré |
| S2.3 | 3 runs de régression 0.1.1 sur US-001 | 🔄 en cours |
| S2.4 | 3 juges + baseline 0.1.1 comparée (attendu : dim. 6 et 9 ↑, rien ne régresse) | ⏳ après S2.3 |
| S2.5 | Test d'exécution de `qaia-help` et `testbook-validate` sur artefacts réels | 🔄 en cours |
| S2.6 | Grooming du backlog (ce document) | ✅ ce commit |

## Sprint 3 *(ancien plan, jamais joué sous ce numéro)* — Élargissement du gold set & cycle complet (PRÊT)

| # | Tâche | Critère d'acceptation |
|---|---|---|
| S3.1 | Runs + juges sur **US-002** (frontières) et **US-003** (API/états) — les skills n'ont jamais vu ces US | Baseline 3 US, aucune dimension < 1 |
| S3.2 | Exercer `rag-build` + `feedback` en conditions réelles (initialisation knowledge, une correction promue en règle, effet mesuré au run suivant) | Boucle d'apprentissage démontrée sur le gold set |
| S3.3 | Exercer `testbook-export` (XLSX + Markdown réels) | Fichiers ouvrables, matrice conforme |
| S3.4 | Exercer la **régénération par diff** (D17) : US-001 modifiée + cahier retouché à la main | Retouches préservées, diff arbitré |
| S3.5 | Step-files pour `testbook-generate` (BMAD A6) si les runs 0.1.1 montrent encore des dérives d'exécution | Skill découpée, harnais non dégradé |
| S3.6 | Doc « Using QAIA with BMAD » (canal d'acquisition, D33) | Page publiée |

## Sprint 4 *(ancien plan, jamais joué sous ce numéro)* — Sortie publique (BLOQUÉ par actions propriétaire)

| # | Tâche | Bloqué par |
|---|---|---|
| S4.1 | Org GitHub + transfert + second admin + Sponsors/Security Advisories + Projects (Discussions/branch protection/2FA déjà faits) | M0-CHECKLIST #1, #4-5 |
| S4.2 | Merge **squash** de la branche + suppression (nom à purger) — 🔄 en attente, le fondateur s'en charge via l'UI GitHub (droits admin requis, hors de portée de l'agent) | M0-CHECKLIST #3 |
| S4.3 | Vérification nom QAIA + relecture contrat (G1 résiduel) | M0-CHECKLIST #2, #6 |
| S4.4 | Recrutement des **5 pilotes** via communautés QA (gate G2) | M0-CHECKLIST #8 |
| S4.5 | Release 0.2.0 taguée + baseline publiée + annonce | S4.1-S4.4 |

---

## Backlog groomé (au-delà des sprints planifiés)

### P1 — refonte à décider (remontée convergente du harnais)
- ~~**Repenser le gate D20 (ratio négatifs ≥ 40 %)**~~ — **résolu** (grooming 2026-07-24 ter,
  vérifié dans `testbook-generate/SKILL.md` : le vrai gate bloquant est désormais la
  **couverture** ADR 0001 — « chaque `[req-neg]` a son scénario `@negative` ou une dérogation
  explicite » — et le ratio est **reporté, jamais un seuil, jamais gonflé**. C'est exactement
  la proposition ci-dessous, déjà en place ; le backlog n'avait pas été re-groomé pour le
  refléter.

### P1 — après les pilotes (M1 fin)
- Parcours conversationnel réel avec les 5 pilotes (les baselines actuelles sont non-interactives — limite documentée) ; taux de scénarios conservés mesuré
- Budget token mesuré par commande, publié (T11)
- Gate d'aptitude PASS/CONCERNS/FAIL/WAIVED sur la matrice (A5 complet, tâche ex-17d)

### P2 — connecteurs & automatisation (M2-M3, tirés par l'usage réel de M1)
- Connecteur Jira via MCP Atlassian (lecture US) ; reporting retour Xray (mode git-master, D10)
- `qaia-playwright` : tests Playwright natifs référençant les IDs (D5) ; exploration Playwright MCP bornée (T5) ; tests API ; critère T17 sur app pilote réelle ; skill `run-report` (formats T1)
- Import de référentiels existants (Xray, Excel — ex-tâche 39/40 étendue)

### P3 — extensions (M4-M5)
- Plugins `qaia-a11y` (axe-core), `qaia-perf` (k6), `qaia-security` (périmètre D26) — indépendants du core
- Génération de jeux de données (D16) ; connecteurs additionnels votés ; agent nommé enrichi (customisation en couches A10)
- Rituel de release mensuel, good-first-issues, POC prédictibilité

### Supprimé au grooming (avec motif)
- ~~« Steps cucumber-js »~~ (invalidé par D5) ; ~~tâches 1-37 v2 numérotées~~ (absorbées par les sprints ci-dessus — l'historique reste dans git) ; ~~mode commands/ legacy~~ (migré skills/) ; ~~« 3-5 pilotes »~~ (harmonisé : 5 engagés, dont ≥ 3 cycles complets).

## Alimentation continue

Inchangée : issues « Proposition » → À challenger (contributeurs : votes 👍 pour les connecteurs ; agents : jamais d'auto-admission). Revue de backlog à chaque fin de sprint (ce grooming) + mensuelle une fois la communauté active.
