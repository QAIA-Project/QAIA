# Phase de Discovery — QAIA (v2)

> **v2** — document entièrement révisé après une revue croisée par 4 personas indépendants : un testeur senior ISTQB (utilisateur final), un mainteneur open source expérimenté, un architecte agentic/Claude, et un product manager sceptique. Les questions de la v1 ont été reformulées quand elles étaient mal posées, ~50 questions manquantes ont été ajoutées, et la section « la bête » est passée de 5 à 12 objections.

Objectif : lever toutes les ambiguïtés **avant** d'écrire la première ligne de plugin. Vous répondez aux questions (dans ce fichier ou en issues), l'agent synthétise, challenge, et transforme chaque réponse en décision tracée (ADR).

---

## 0. Préalables bloquants — à traiter AVANT tout le reste

Trois portes (« gates ») identifiées par la revue. Tant qu'elles ne sont pas franchies, ni publication du dépôt en public, ni écriture de la première skill.

### G1 — Juridique ex-employeur (impact : fatal, une lettre recommandée suffit)

> ✅ **Purge effectuée (décision D1)** : toute référence nominative à l'ex-employeur et au projet interne précédent a été retirée du dépôt, et l'historique de la branche a été réécrit au moment de la purge. ⚠️ Le **nom de la branche** contient encore l'ancien acronyme : merger en squash puis supprimer la branche avant toute communication publique.

Actions restantes avant toute publication publique :
- Relire contrat de travail et solde de tout compte : cession de PI, non-concurrence (portée/durée/contrepartie), confidentialité, **non-sollicitation** (interdit peut-être de recruter les anciens collègues comme pilotes).
- En cas de clause restrictive : avis juridique écrit, ou accord écrit de l'ex-employeur.
- Engagement « clean-room » : aucun artefact du projet précédent n'est réutilisé, tout est réécrit de zéro.

### G2 — Preuve de marché (impact : mort par indifférence)

La cible réelle est une intersection : testeurs × utilisateurs de Claude Code × abonnés payants × autorisés à envoyer des US dans un LLM. Chaque filtre élimine 80-95 % du précédent. Avant d'écrire du code :
- Sonder cette intersection (post LinkedIn / Ministry of Testing / communautés QA FR, sondage).
- Obtenir **5 pilotes engagés nommément** (créneau réservé, US réelle apportée, hors ex-employeur). Zéro engagement = no-go delivery.

### G3 — Contradictions techniques à trancher (impact : promesses intenables dans les docs actuels)

Trois contradictions internes détectées, à résoudre explicitement (questions 64-68 et 33-34) :
1. « La CI teste les skills sur le gold set » **vs** « aucune clé API » : exécuter une skill = exécuter un LLM ; sans clé, la CI ne fait que du lint.
2. « Cahier maintenu dans le temps » **vs** aucun mécanisme de régénération/merge : en l'état l'outil est *write-once*.
3. « Cucumber au-dessus de Playwright » : choix fondateur jamais challengé, largement abandonné par la communauté Playwright (double maintenance, débogage pénible).

---

## Livrables de sortie de la discovery

| Livrable | Description |
|---|---|
| **Décisions G1-G2-G3** | Avis juridique, sondage marché + pilotes engagés, ADR sur les 3 contradictions |
| **Vision produit** (1 page) | Problème, cible, proposition de valeur, non-objectifs, kill criteria |
| **Personas** | 3-4 profils de testeurs utilisateurs types |
| **Carte des capacités** | Les skills/commandes découpés en briques, avec dépendances |
| **ADR initiaux** | Licence+DCO, architecture plugins, RAG/retrieval, Gherkin/runner, éval |
| **Backlog priorisé v2** | Mis à jour dans le Kanban (cf. `KANBAN.md`) |

---

## Les questions

> La numérotation v1 (1-37) a été remplacée : les questions ont été reformulées, fusionnées et complétées. Les références Qxx dans `DELIVERY.md` et `KANBAN.md` pointent vers cette numérotation v2.

### Bloc A — Vision & positionnement

1. **Nom** : recherche de disponibilité effectuée pour « QAIA » (marque INPI/EUIPO, npm, domaine, repos GitHub homonymes, produits IA existants du même nom) : résultats ? Deux noms de repli ? Critère de gel définitif du nom avant M0 ?
2. **Accès de la cible à l'outil** : le testeur type a-t-il aujourd'hui accès à Claude Code (licence payante, autorisation sécurité, aisance terminal) ? Si non, qui l'a — et est-ce encore un « testeur » ou un SDET/dev ? Ensuite seulement : cible v1 = individu ou équipe ?
3. **Juridique ex-employeur** (détail de G1) : (a) que disent précisément contrat et solde de tout compte ? (b) détenez-vous encore un artefact du projet précédent — si oui, engagement clean-room ? (c) avis juridique écrit ou accord écrit avant publication ?
4. **Problème n°1** : quel est le problème le plus douloureux, fréquent et mal résolu du testeur cible aujourd'hui (verbatims de 5 testeurs à l'appui), et lequel de nos chantiers y répond le mieux — génération du cahier, automatisation, ou **ni l'un ni l'autre** ?
5. **Niche différenciante** : le médical/réglementé (IEC 62304, traçabilité) est-il la *cible de niche v1* — là où votre avantage fondateur est réel et où les copilotes génériques sont faibles — plutôt qu'une simple option de traçabilité ?
6. **Langues** : bilingue FR/EN dès le départ ? (Open source = audience mondiale ; communauté de départ probablement francophone.)
7. **Licence — décision articulée (1 ADR)** : licence du code (MIT / Apache-2.0 / AGPL — recommandation : Apache-2.0 pour la clause brevets), articulée avec : intention commerciale future (support payant, dual licensing ?), mécanisme de provenance des contributions (DCO minimum, cf. Q77), et licences distinctes du gold set (sous quelle licence sont réellement les « US publiques » ?) et de la documentation.

### Bloc B — Marché & concurrence *(nouveau)*

8. **Cartographie concurrentielle** : quels outils font déjà « US → cas de test générés par IA » (Xray+Jira AI, Azure Test Plans+Copilot, TestRail, testRigor, mabl, Qodo, Keploy, et les agents Playwright de Microsoft) ? Pour chacun : que fait-il déjà de ce que QAIA promet, et que ferait QAIA qu'il ne fait pas ?
9. **Le test du prompt nu** : un testeur avec Claude Code + Playwright MCP + un bon prompt obtient déjà un cahier Gherkin et des tests. Quelle est la valeur *différentielle mesurable* de QAIA (temps, qualité, reproductibilité) et comment la démontre-t-on (comparatif publié) ?
10. **QAIA vs l'IA native de l'ALM** : pourquoi un testeur quitterait-il l'outil où vivent déjà ses US et son référentiel ? Quel coût de friction lui impose-t-on (installer Claude Code, payer un abonnement, terminal) et qu'est-ce qui le justifie ?
11. **Why now** : qu'est-ce qui rend le projet nécessaire *maintenant* — et qu'est-ce qui empêche Anthropic (skills QA natives) ou Microsoft (agents Playwright) de le rendre redondant dans 12 mois ?
12. **Taille du marché réel** : quelle preuve que l'intersection décrite en G2 dépasse quelques centaines de personnes ? Comment la sonder avant d'écrire du code ?
13. **Non-consommation** : quelle part de la cible n'utilise aujourd'hui *aucun* outil IA et pourquoi (interdiction sécurité, culture, coût) ? Ces freins s'appliquent-ils à QAIA ?

### Bloc C — Utilisateurs & adoption

14. **Pilotes** : citez 5 testeurs nommément qui se sont *engagés* (créneau réservé, US réelle apportée) à tester la v1 sous 30 jours. Contrainte : hors ex-employeur si clause de non-sollicitation (cf. G1). Où les trouver sinon : communautés ISTQB/CFTL, Ministry of Testing, meetups QA FR ?
15. **Maturité technique supposée** : l'utilisateur sait-il installer un plugin Claude Code ? Utiliser un terminal ? Configurer un MCP ?
16. **Critère de succès à 6 mois — avec seuils et kill criterion** : combien d'utilisateurs *récurrents* (≥ 2 cahiers générés à ≥ 2 semaines d'intervalle) ? Quel seuil déclenche pivot ou arrêt (ex. < 10 récurrents = pivot) ?
17. **Boucle d'activation** : entre « j'ai vu le repo » et « premier cahier généré », combien d'étapes et de prérequis ? Quel parcours « première valeur en < 15 min » ?
18. **Canaux de découverte** : les 3 canaux priorisés (marketplace Claude Code, contenu/SEO, communautés QA, LinkedIn, conférences) avec un objectif chiffré chacun sur 6 mois ?
19. **Preuve sociale initiale** : quel artefact de démonstration public (vidéo, cahier exemple sur une app connue, benchmark vs « prompt nu ») fait dire « je veux ça » avant toute installation ?

### Bloc D — Adoption entreprise & conformité *(nouveau)*

20. **Dossier RSSI** : quelle documentation fournit-on (flux de données, ce qui part chez Anthropic, rétention, options entreprise) pour qu'un testeur obtienne le feu vert de son RSSI ? Sans ça, pas d'adoption en entreprise (santé, banque).
21. **Données sensibles** : documente-t-on explicitement que tout contenu ingéré transite vers l'API Anthropic via la session utilisateur (implications RGPD/HDS) ? Les skills doivent-elles masquer par défaut les motifs de données personnelles détectés (opt-out explicite) ?
22. **Quotas & plan Claude** : quel plan est supposé (Pro/Max/Team) et combien de cycles complets US→cahier→tests tiennent dans une fenêtre de quota ? Le vrai coût utilisateur est en **quota d'abonnement**, pas en euros — faut-il un mode dégradé sobre, et ce chiffre doit-il figurer dans le README ?

### Bloc E — Ingestion & sources

23. **Sources d'exigences v1** (≠ référentiels de test) : top 3 parmi Jira, Azure DevOps, GitLab, Notion, Confluence, fichiers (Word/PDF/Markdown), URL web ?
24. **Référentiels de test cibles** pour la publication : Xray, Zephyr Scale, TestRail, aucun ? Pour Xray : quel mode de synchronisation assume-t-on (Xray master vs git master) ? Une publication naïve inonde Jira de doublons à chaque régénération.
25. **Périmètre du « scraping » à valider** : extraction depuis un outil connecté (API), une page web, un document déposé — les trois ?
26. **Pièces jointes & vision** : quelle proportion des US cibles n'est compréhensible qu'avec les maquettes/captures ? Si majoritaire, l'analyse vision est un prérequis v1, pas une option.

### Bloc F — RAG & connaissance

27. **Mécanisme de retrieval** : le RAG v1 = fichiers Markdown dans `.qaia/knowledge/` (versionnés git, zéro infra). Quel mécanisme garantit que le bon fichier est chargé au bon moment sans exploser le contexte : index maître obligatoire, conventions de nommage, taille max par fichier, chargement sélectif ?
28. **Contenu minimal & responsabilité** : glossaire métier, règles de gestion, historique d'anomalies, cartographie applicative ? Qui le maintient ?
29. **Fiabilité du retrieval** : comment mesure-t-on les « misses » (règle existante non retrouvée) et comment les corrige-t-on (renommage, index, promotion en règle) ?
30. **Croissance du feedback** : comment borne-t-on l'accumulation des corrections — compaction périodique, promotion des corrections récurrentes en règles, péremption des exemples ?
31. **Conflits & empoisonnement** : que se passe-t-il quand deux feedbacks se contredisent, ou qu'une « correction » apprise est fausse ? Qui arbitre, comment purge-t-on ? Le RAG est un artefact de test comme un autre : a-t-il une revue ?
32. **Portabilité multi-projets/équipe** : RAG par repo, par produit, partageable via git ? Gestion des conflits de merge sur `.qaia/knowledge/` ?

### Bloc G — Génération & cycle de vie du cahier

33. **Gherkin vs runner** : la contrainte est-elle la **syntaxe Gherkin** (agnostique — quelle version, quels mots-clés autorisés/interdits) ou une **version de runner** ? « Cucumber 7 » est une version dépassée de cucumber-js (v10+ aujourd'hui) : si runner, viser la dernière stable et définir la politique de suivi des majors.
34. **Faut-il vraiment Cucumber au-dessus de Playwright ?** La communauté Playwright l'a largement abandonné (double maintenance Gherkin + glue code, débogage pénible, pas de trace viewer sur les steps). Du BDD sans collaboration dev/PO = du « Gherkin zombie ». Alternative à trancher : Gherkin comme documentation vivante + tests Playwright natifs, ou couche Cucumber assumée avec ses coûts ?
35. **Atomicité & état** : validez la définition (1 scénario = 1 comportement, `Background`/`Scenario Outline` autorisés) **et** la gestion d'état : comment un scénario atomique obtient-il ses préconditions — seeding API/fixtures obligatoire, interdiction des enchaînements UI ? Taille max d'un cahier avant découpage en features ?
36. **Langue du Gherkin** : keywords français (`# language: fr`) ou anglais ? À trancher avant la première skill — mixer les deux est irrécupérable.
37. **Identifiants stables** : chaque scénario porte-t-il un ID stable et unique (tag `@QAIA-123`) qui survit aux régénérations ? Sans ID stable : pas de traçabilité, pas de diff, pas de suivi des résultats.
38. **Régénération & merge** *(le trou le plus grave de la v1)* : quand l'US évolue, que fait QAIA du cahier déjà retravaillé à la main ? Régénération complète (retouches perdues), diff scénario par scénario, génération incrémentale des seuls critères modifiés ? Quel mécanisme de merge ?
39. **Existant** : QAIA sait-il ingérer un référentiel existant (tests Xray, `.feature` legacy, cas Excel) pour ne pas générer de doublons de ce qui existe déjà ?
40. **Détection de doublons** : à la génération, comment vérifie-t-on qu'un scénario proposé ne recouvre pas un scénario existant du repo ?
41. **Déterminisme** : deux runs de `testbook-generate` sur la même US produiront deux cahiers différents. Variabilité acceptable ? Impose-t-on un format canonique (ordre des scénarios, nommage, IDs stables) pour que diffs git et gold set restent exploitables ? Les métriques sont-elles mesurées sur 1 run ou une moyenne de N runs, avec quelle tolérance de variance ?
42. **Biais happy path** : quel ratio cible cas passants / cas d'erreur / cas limites (ex. ≥ 40 % de scénarios négatifs), et comment est-il vérifié automatiquement ?
43. **Coût de revue humaine** : la génération prend 5 min, mais relire 40-60 scénarios atomiques ? Quel dispositif réduit ce coût : résumé par technique ISTQB, mise en évidence des scénarios à faible confiance, ordre de revue par risque ?
44. **ISTQB** : l'outil justifie-t-il la technique choisie dans le cahier (traçabilité pédagogique) ? Syllabus Foundation seul ou aussi Test Analyst ?
45. **Jeux de données** : génération de données de test (héritage Faker + NLP) dès la v1 ou plugin séparé ?
46. **Traçabilité exigence → test** : quel schéma d'ID et comment la traçabilité survit-elle à une régénération et à un aller-retour avec le référentiel (Xray) ? Simple lien US ↔ scénario en v1 ou matrice de couverture ?
47. **Formats d'export** : fichiers `.feature` + synthèse éditable (Markdown/DOCX/XLSX) — lequel prioritaire ? Et les formats machine attendus par la profession : Cucumber JSON (import Xray), JUnit XML ?

### Bloc H — Priorisation & reporting

48. **Priorisation** : le risk-based testing exige des entrées humaines (probabilité, impact). Qui fournit les données de risque — l'utilisateur en conversation, le RAG, des défauts ? L'outil propose, l'humain arbitre : comment matérialise-t-on cet arbitrage ?
49. **Reporting** : distinguer rapport de *génération* (couverture des CA), rapport d'*exécution* (résultats Playwright) et rapport de *couverture exigences*. Formats machine : Cucumber JSON (Xray), JUnit XML, HTML autonome — lesquels en v1 ?

### Bloc I — Automatisation Playwright

50. **Ordre E2E / API / mobile** — et quel pourcentage de la cible teste du mobile *natif* ? Si > 30 %, « 100 % Playwright » est un mauvais slogan : assume-t-on publiquement « web-first » dès le README ?
51. **Sélecteurs & anti-flakiness** : quelle convention imposée au code généré (getByRole/getByTestId d'abord, XPath positionnel interdit, Page Objects ou non, politique retry/quarantaine) ? C'est LE facteur n°1 d'abandon des tests générés.
52. **Secrets & environnements** : URL, comptes de test, credentials — jamais dans la session ni dans le RAG versionné. Quel pattern imposé dès la conception (`.env`, vault, fixtures Playwright) ?
53. **CI de l'utilisateur** : les tests générés doivent tourner dans SA CI (Jenkins, GitLab CI, Azure Pipelines) sans session Claude. Confirme-t-on un code 100 % autonome + templates de pipelines ?
54. **Critère M3 réaliste** : « 80 % sur une app de démo publique » ne prédit rien d'un ERP interne (SSO/MFA, CAPTCHA, iframes, shadow DOM, VPN). Quel critère de sortie sur une application *pilote réelle* ?
55. **Playwright MCP** : les snapshots sont volumineux (plusieurs k tokens/page). Quelles limites d'exploration (nb de pages, profondeur, filtrage) et quel environnement minimal requis (navigateur, app accessible) documente-t-on ?
56. **Perf** : k6, Artillery, ou Playwright + web vitals ?
57. **Sécurité** : périmètre v1 passif (headers, TLS) vs actif (ZAP baseline) ? Le plugin exige-t-il une confirmation que la cible est autorisée (liste d'hôtes en config, refus par défaut) ? Quel disclaimer et quelle politique d'usage acceptable ?
58. **Accessibilité** : axe-core via Playwright — validez.

### Bloc J — Faisabilité agentique & qualité des skills *(nouveau)*

59. **Taille d'entrée** : taille max d'US supportée par skill ? Comportement au dépassement (découpage validé, résumé, refus explicite) ? Chaque skill déclare-t-elle sa limite ?
60. **Parcours vs session** : le parcours en 9 étapes tient-il dans une conversation ? Que se passe-t-il quand la compaction se déclenche au milieu (perte des validations) ? Quel checkpoint fichier (`.qaia/state`) permet de reprendre à l'étape N dans une nouvelle session ?
61. **État entre sessions** : où sont persistées les décisions validées (source confirmée, ambiguïtés levées, techniques choisies) ? Format/contrat du fichier d'état ? Conflits si deux sessions concurrentes modifient `.qaia/` ?
62. **Versionnement des skills** : SemVer par plugin ? Définition d'un breaking change (format du cahier, structure `.qaia/`, contrat entre skills) ? Migration des `.qaia/` entre versions majeures ?
63. **Compatibilité modèles** : contre quels modèles Claude les skills sont-elles validées ? À la sortie d'un nouveau modèle : re-run du gold set, matrice skill × modèle, épinglage recommandé ?
64. **Surfaces supportées** : plugins, commandes, sous-agents et MCP locaux n'existent que dans **Claude Code**. Assume-t-on « Claude Code only » en v1, écrit dans le README dès M0 ? Si Desktop/claude.ai plus tard : quelles briques repackagées (skills seules) et lesquelles définitivement exclues (Playwright) ?
65. **Tester les skills en CI sans clé API** (cf. G3.1) : option (a) CI = lint statique + validation Gherkin, éval qualitative manuelle par les pilotes ; option (b) clé API financée par le mainteneur en secret GitHub Actions (compatible avec « aucune clé *embarquée* », coût récurrent). Laquelle, avec quel budget mensuel ?
66. **Jugement de qualité** : la validation syntaxique ne mesure pas la qualité. Définit-on une rubrique (atomicité, couverture des CA, technique justifiée, ratio négatifs) exécutable par un LLM-judge sur le gold set ? Qui la maintient ?
67. **Ordre de construction** : le harnais d'évaluation (gold set + rubrique) doit-il exister **avant** la première skill (la v1 du Kanban le plaçait après huit skills — ordre inversé) ?
68. **« 1 sous-agent par critère d'acceptation »** : les sous-agents ne partagent pas de contexte — coût token ×N (contradiction avec la sobriété), incohérence du cahier (vocabulaire, `Background`, doublons entre CA). Passe de consolidation, ou abandon du parallélisme systématique ?
69. **Budget token honnête** : une skill ne voit pas sa propre consommation ; le « budget par commande » sera une estimation qui dérive. Dégrader en « ordre de grandeur mesuré sur le gold set à chaque release » ? (Les coûts au cahier mesurés sur le projet interne précédent ne se transposent pas : l'utilisateur paie ici en quota d'abonnement, cf. Q22.)

### Bloc K — Distribution & dépendance plateforme *(nouveau)*

70. **Dépendance Anthropic** : produit 100 % couplé au format skills/plugins Claude Code (propriétaire, jeune, mouvant). Plan si le format casse, si la marketplace change de règles, si le pricing devient inabordable ? La portabilité (skills = markdown réutilisable ailleurs) est-elle un objectif de conception ?
71. **Packaging vs découvrabilité** : marketplace (repo + `marketplace.json`) + mode « copie manuelle des skills » pour environnements contraints — OK ? (La découvrabilité est traitée en Q18.)
72. **Signal d'usage minimal** : sans backend, quel mécanisme opt-in (rapport local JSON anonymisé que le pilote poste en Discussion, compteur exportable) donne un signal d'usage réel dès la v1 — et quelle décision chaque signal déclenche-t-il ?

### Bloc L — Gouvernance, pérennité & supply chain *(nouveau)*

73. **Propriété du dépôt** : organisation GitHub dédiée avec un second owner de confiance dès M0 (jamais de repo personnel pour un projet communautaire) — validez ?
74. **Modèle de décision** : BDFL assumé, jusqu'à quand ? Critères écrits pour devenir committer puis mainteneur ? Traitement d'une décision contestée ?
75. **Bus factor** : si vous êtes indisponible 3 mois, que devient le projet ? Qui a les droits admin, l'accès marketplace, le domaine ? Document de succession ?
76. **Marque** : politique vis-à-vis des forks (« QAIA-pro » ?) et de l'usage commercial du nom (« QAIA consulting » ?) ; dépôt INPI/EUIPO ou nom non défendu, assumé ?
77. **DCO ou CLA** : sans mécanisme de provenance, impossible de changer de licence ou de prouver l'origine du code — et avec un mainteneur qui ne lit pas le code, la provenance est votre seule protection contre du code copié sous licence incompatible. DCO (sign-off) minimum ?
78. **Financement** : GitHub Sponsors / OpenCollective dès M0 ? Qui paie les coûts récurrents : votre abonnement Claude (outil de production), les tokens d'éval du gold set, l'app de démo, le domaine ? Ambition commerciale future (conditionne licence et CLA *maintenant*) ?
79. **Soutenabilité** : combien de mois de travail non rémunéré ? Critère explicite de pause/arrêt (ex. « 0 pilote actif à M+6 = gel ») ? Un projet qui définit ses conditions d'arrêt meurt proprement ; les autres meurent en épuisant leur mainteneur.
80. **PR de skills = surface d'attaque** : une skill est un prompt qui pilote la session de l'utilisateur avec ses accès. Une PR communautaire peut y glisser une instruction malveillante (exfiltration du RAG, actions non sollicitées) **qu'aucun lint ne détecte et que vous ne saurez pas lire**. Processus de revue spécifique : contributions code fermées tant qu'il n'y a pas de co-mainteneur technique ? Revue adversariale par agent tracée dans chaque PR ?
81. **Durcissement du dépôt** (critère de sortie M0) : 2FA obligatoire, branch protection, releases/tags signés, Actions épinglées par SHA, permissions minimales des workflows — validez la checklist ?
82. **SECURITY.md** : canal privé de signalement de vulnérabilité, qui triage (vous seul ?), quel délai réaliste ?
83. **Compromission de compte** : le compte qui merge tout est compromis → version vérolée installée chez tous les utilisateurs. Plan : passkeys, second owner pour révoquer, procédure de release annulée ?
84. **Modération** : le code de conduite désigne qui pour instruire un signalement (mainteneur unique = juge et partie) ? Contact externe neutre ? Politique face aux PR spam générées par IA (critères de fermeture, preuve d'exécution exigée) ?
85. **Co-mainteneur technique** : promu d'option à **prérequis** — critère de sortie de M1 (ou au plus tard M3 : on distribue du code exécuté chez autrui) ? Où le chercher, que lui offrir (co-décision réelle), quels droits ?

### Bloc M — Vous, mainteneur non-codeur

86. **Temps & réalisme** : combien d'heures hebdo ? La revue estime la roadmap v1 sous-évaluée d'un facteur 2-3 en vibe-coding solo (M0→M3 réaliste : 6-9 mois, support et animation compris) — acceptez-vous ce recalibrage ?
87. **Garde-fous sans revue humaine du code** : scan sécurité automatisé (CodeQL, secret scanning), agent relecteur adversarial systématique sur chaque PR, validation par l'usage tracée — et à partir de quel seuil un co-mainteneur codeur devient-il *bloquant* plutôt qu'optionnel ?
88. **Périmètre contributif tant que vous êtes seul** : limiter les contributions externes aux docs, gold set et issues (pas de code/skills) jusqu'à l'arrivée du co-mainteneur — validez ?

---

## La bête — 12 objections dures (v2)

1. **Le marché adressable est une intersection quasi vide.** Testeurs × Claude Code × abonnement payant × droit d'envoyer des US dans un LLM : le persona visé n'existe presque pas ; celui qui manie Claude Code est un SDET qui n'a pas besoin de Gherkin guidé. À vérifier (G2) avant d'écrire du code.
2. **La valeur vs « Claude nu » n'est pas établie et s'érode par les deux bouts.** Un bon prompt + Playwright MCP fait déjà 70 % de la promesse ; Microsoft et Anthropic grossissent l'un vers l'autre. Sans « why us / why now » démontré (benchmark publié), QAIA est une couche fine en voie d'absorption.
3. **L'outil est write-once.** Aucun mécanisme de régénération/merge quand l'US évolue : sprint 1 magique, sprint 3 l'utilisateur choisit entre perdre ses retouches ou maintenir à la main — et abandonne. Mode d'échec n°1 des générateurs de tests (Q37-40).
4. **« La CI est votre revue technique » est une illusion.** Sans clé API, la CI ne fait que du lint : elle ne détecte ni régression de qualité de génération, ni instruction malveillante dans une skill. La contrainte « pas de clé » et la promesse « CI qui teste les skills » sont mutuellement exclusives (Q65).
5. **Mainteneur non-codeur + PR de skills = injection indétectable.** L'ambition « communauté qui contribue du code » est en contradiction frontale avec « mainteneur qui ne peut pas relire ce qu'il distribue ». À résoudre par un périmètre contributif restreint et/ou un co-mainteneur (Q80, 85, 88).
6. **Cucumber au-dessus de Playwright est un choix contesté jamais challengé.** Double maintenance, débogage pénible, communauté partie ailleurs ; du BDD sans collaboration dev/PO = Gherkin zombie. La contrainte fondatrice elle-même doit passer la discovery (Q34).
7. **La revue coûte plus cher que l'écriture.** 8 CA = 40-60 scénarios atomiques ; relire 60 scénarios plausibles pour débusquer 5 règles métier fausses est plus long — et plus dangereux — qu'en écrire 20 bons : un test plausible-mais-faux au vert fabrique de la fausse confiance (Q42-43).
8. **Le risque juridique ex-employeur était matérialisé dans le repo** (références nominatives et métriques internes dans `PROMPT.md` — purgées, cf. D1 ; une description *anonymisée* de l'expérience passée est conservée et assumée ; le nom de la branche reste à traiter). Préalable bloquant G1, pas une question parmi d'autres.
9. **« 1 sous-agent par critère d'acceptation » est fragile.** Contexte rechargé N fois (coût ×N) et cohérence du cahier non garantie ; nécessite une passe de consolidation ou l'abandon du pattern (Q68).
10. **Le parcours en 9 étapes suppose une session infinie.** Sans checkpoints fichier entre étapes, la compaction détruit les validations en plein milieu ; c'est un prérequis d'architecture absent de M1 (Q60-61).
11. **Le coût réel utilisateur est en quota d'abonnement, pas en euros.** Un cycle complet (ingestion + RAG + génération multi-agents + exploration MCP) peut consommer une fenêtre de quota entière ; sans mode sobre, l'outil reste un jouet de démo (Q22, 69).
12. **Roadmap calibrée pour une équipe, mortalité par épuisement.** M0→M3 réaliste : 6-9 mois solo, support compris ; pilotes non recrutés ; aucun kill criterion. Réduire la promesse v1 au seul `qaia-core`, conditionner M2+ à l'usage réel de M1, définir les conditions d'arrêt (Q16, 79, 86).

*(Conservé de la v1 : le mobile natif est intenable en « 100 % Playwright » — assumer « web-first » ou ouvrir une exception, Q50.)*

---

## Risques consolidés (top 3 par persona)

| Persona | Risque n°1 | Risque n°2 | Risque n°3 |
|---|---|---|---|
| **Testeur ISTQB** | Abandon à la 3e itération (write-once, pas d'IDs stables) | Fausse assurance de couverture (plausible-mais-faux) | Validation dépendante de pilotes inexistants |
| **Mainteneur OSS** | Juridique ex-employeur (fatal si clauses restrictives) | Bus factor 1 + skill vérolée = confiance détruite | Épuisement entre M1 et M3 |
| **Architecte** | Régressions silencieuses des skills (pas d'éval, dérive des modèles) | Explosion de contexte bout en bout | Dépendance plateforme plugin jeune |
| **PM** | Marché trop étroit, friction d'entrée forte | Commoditisation par Microsoft/Anthropic/ALM | Confiance tuée par une démo médiocre |

---

## Déroulé proposé de la discovery (v2)

| Semaine | Activité | Sortie |
|---|---|---|
| S0 | **Gates** : G1 juridique (avis + purge PROMPT.md), lancement sondage G2 | Feu vert publication ; sondage en cours |
| S1 | Blocs A-B-C-D (vision, marché, adoption, entreprise) | Vision 1 page avec kill criteria, ADR licence, résultats sondage |
| S1-S2 | Blocs E-F-G-H (ingestion, RAG, génération, priorisation) — dont **Q34 (Cucumber vs Playwright natif)** et **Q38 (régénération)** | ADR format de test, carte des capacités v1, cycle de vie du cahier défini |
| S2 | Blocs I-J-K (automatisation, faisabilité agentique, distribution) — dont **Q65 (éval/CI)** et **Q67 (harnais d'abord)** | ADR éval & CI, périmètre automatisation, « Claude Code only » tranché |
| S2-S3 | Blocs L-M (gouvernance, supply chain, mainteneur) + engagement des 5 pilotes (G2) | Org GitHub + second admin, périmètre contributif, pilotes signés |
| S3 | Synthèse, go/no-go delivery | `KANBAN.md` v2 mis à jour, jalon M0 lancé — ou pivot/gel documenté |
