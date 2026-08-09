# QAIA — état du projet & prompt de reprise

## Revue à cinq personas — 2026-08-09 (fin de sprint 34)

Cinq relectures indépendantes du dépôt, chacune avec un contexte vierge et un seul rôle :
testeur en poste, directeur des tests, chef de projet, développeur destinataire, utilisateur
final. **56 défauts remontés, 55 corrigés, 1 réfuté après vérification.** Chaque correction est
mesurée avant/après ; aucune n'a été retenue sur la seule foi du rapport qui la signalait.

### Les cinq qui comptent

**Une faille, pas une fausseté.** `automation_score.py` exécutait ce qu'un dépôt scanné mettait
dans un **nom de test** : `escape_grep` échappait les métacaractères d'expression régulière et
était utilisé comme s'il échappait le shell — ni le backtick ni le guillemet ne passaient par
lui — et le résultat partait dans `--grep "%s"` sous `shell=True`. Le mode `--third-party` de
cet outil existe précisément pour lire les dépôts des autres. Corrigé à la racine (argv en
liste, `shell=False`), tiré à blanc avec un `touch` dans un titre : aucun fichier créé.

**Le chiffre en tête du produit était faux.** `structural_score.py` créditait « AC1 » avec le
tag `@AC10` — une sous-chaîne. Un cahier déclarant AC1..AC10 et n'en couvrant qu'un marquait
**100/100 PASS**. Corrigé en jeton entier : 15/30 sur le cas témoin.

**La promesse centrale, cassée dans la vitrine.** Sept tests portaient un identifiant qui ne
renvoyait à aucun scénario du cahier. Les sept scénarios manquants ont été écrits — pas les
étiquettes retirées. Ça avait pu vivre parce qu'**aucun workflow ne pointait les outils du
projet sur un artefact réel** : vingt étapes de CI, et seuls tournaient les selfchecks. Deux
étapes ajoutées.

**La règle 3 n'était appliquée nulle part.** « Aucun producteur ne note sa propre sortie » est
le premier argument que le README oppose à la concurrence, et `validate_manifest.py` vérifiait
seulement que `gate.scoredBy` est une *chaîne*. Contrôle mécanique ajouté, éprouvé dans les
deux sens, promu en `selfcheck_rule3.py`.

**Le scoreur déterministe n'est pas livré.** Les trois skills de notation n'embarquent aucun
code : elles demandent au modèle de re-dériver ~300 lignes de regex depuis de la prose, à
chaque invocation. La promesse « note déterministe, pas une auto-notation par un LLM » tient
dans ce dépôt et s'amollit à la frontière de livraison. C'est l'ADR 0002, assumé — **le défaut
n'est pas la décision, c'est que seul son avantage était écrit.** Le prix est désormais dit,
aux trois endroits où l'affirmation vit et dans chacune des trois skills.

### Ce que la journée dit du projet

Trois défauts ont été trouvés **en prouvant la correction d'un autre**, pas par une revue :
`.toBe(404)` — la forme la plus courante pour affirmer un code HTTP — n'était jamais lu par
`spec_suite_drift` ; `expect(true).toBeTruthy()` était classé « faible » par l'outil censé
attraper exactement ça ; et une de mes propres corrections a fait **diverger** deux copies d'un
même bloc, transformant un défaut de style en défaut de correction dans l'heure.

Et j'ai rendu la CI rouge une fois, avec une garde « de prudence » que j'avais validée
**derrière un pipe** — donc en lisant le code de `tail` et non celui de l'outil. Le jour même
où je corrigeais cette classe de faute chez les autres.

**Cinq cahiers de la vitrine restent en CONCERNS** (74 à 77). L'outil dit vrai : leur `Then`
est volontairement vague (« the attempt is refused ») au titre de Q10 — l'exigence énonce un
refus, pas un statut. C'est un arbitrage documenté, pas un défaut, et il reste visible.

**Un constat réfuté :** la revue reprochait des URL GitHub absolues dans une skill. C'est
l'inverse — 18 skills sur 37 le font, et c'est correct : une skill **installée** vit hors du
dépôt, où un lien relatif est mort.

## Sprint 32 — la distribution, la première application hors du dépôt, et un dépôt qui se corrige lui-même toute la journée (2026-08-08, D140-D164) — TERMINÉ

Session de nuit, mandat d'autonomie complète du fondateur, objectif qu'il a fixé : **1000 étoiles
fin d'année**. Point de départ mesuré, pas supposé : **0 étoile, 277 vues pour 9 visiteurs
uniques sur 14 jours, zéro referrer externe**. Les 673 clones sont de la CI et des worktrees
d'agents, pas des utilisateurs. Aucun sprint n'avait jamais travaillé la distribution — c'était
devenu le facteur limitant devant tout le reste, **#1 (5 pilotes) compris, mécaniquement
inatteignable avec neuf visiteurs**.

### Ce qui a été livré

**#64 fermée (D140)** — `contract-probe` exercée pour la première fois sur son cas nominal
(cible self-hostée). Le run 1 de la sonde **ne testait rien** : elle créait les brouillons par un
endpoint qui ignore `lines`, donc sept sondes ont soumis des rapports vides et récolté le même
422. Écrit tel quel, le rapport annonçait six promesses tenues sans qu'une seule soit exercée.
Run 2 : 1 finding haut (`CP-001`, `amount: 1e309` → rapport `submitted` avec `amount` et
`totalEur` à `null`, re-reproduit indépendamment), 10 promesses vérifiées, 4 observations
écartées faute de promesse documentée.

**Infrastructure de visibilité (D141)** — site vitrine à la racine des Pages (elle servait
jusque-là l'app de démo, déplacée en `/demo/`), page de comparaison qui **recommande un
concurrent dans 3 cas sur 4**, `llms.txt`, `robots.txt`, sitemap, **première release taguée**
(`v0.1.0-prealpha`), badges, topics GitHub complétés (`claude-skills`, `claude-plugin`,
`claude-code-plugin` manquaient — ce sont ceux par lesquels on cherche un plugin), installation
ramenée de cinq gestes affichés à deux.

**Veille refaite, et l'ancienne s'était trompée de méthode** — celle du 2026-07-26 cherchait des
concurrents par domaine métier et concluait « aucun nouveau concurrent sérieux ». Elle n'avait pas
cherché dans le **canal de distribution** de QAIA. Trouvés : QA Orchestra (10 agents, plugin
Claude Code MIT), QASkills.sh (**~380 skills MIT qui recouvrent notre catalogue nom par nom**, et
compétentes — leur skill ISTQB lue en entier), neonwatty/qa-skills, ClaudeCodeAgents (756 ★),
agentic-qe (435 ★), playwright-skill (2 994 ★). **L'ISTQB n'est plus un différenciateur.**

**Outreach préparé, pas publié** — LinkedIn (FR), Show HN avec le commentaire qui tuerait le fil
et sa réponse, Reddit, Ministry of Testing : `docs/outreach/`. **PR de référencement ouverte** sur
`jeremylongshore/claude-code-plugins-plus-skills` (2 608 ★) — [#1163](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1163).

### Le panel, et pourquoi il compte plus que le reste

Cinq lentilles indépendantes sur les pages fraîchement écrites (fact-checker, SDET hostile, QA
lead acheteur, lecteur HN, et un **dogfooding d'`a11y-audit`/`usability-heuristic-review` sur les
pages de QAIA elles-mêmes**), chaque constat passé à un agent chargé de le **réfuter** :
**30 constats, 0 réfuté.** Les quatre plus graves revérifiés à la main avant correction.

**Trois erreurs factuelles** : une porte de ratio négatifs/limites vantée alors qu'**ADR 0001 l'a
supprimée** le 2026-07-23 (dans 6 fichiers) ; le mot **« planted-ambiguity » supprimé** d'une
citation présentée comme verbatim ; une affirmation sur les concurrents (« le même essaim produit
et évalue ») qui était une **inférence déguisée en constat**.

**Deux omissions décisives** : le parcours vitrine était **contaminé et non-interactif** (chaque
arbitrage `simulated: <default applied>`, modèle ayant lu la section juge séquestrée) alors que
la page vantait l'arbitrage humain ; et le **benchmark contre le prompt direct**, qui existait
depuis le 28/07 et dit ~2,9× plus de tokens avec un prompt direct **égal ou meilleur sur le
rappel des ambiguïtés plantées**, était absent d'une page qui se vante de publier ses échecs.

**Un surclassement** : l'« audit externe 13 personas » à 2,4/5 est **auto-administré** —
`docs/KANBAN.md:165` dit « cabinet fictif », 17 agents, 23 minutes. Le présenter comme externe
transformait un exercice de lecture hostile en validation indépendante. **À ne plus jamais écrire
autrement, y compris dans ce fichier** : les notes 2,4/5 et 5,0/10 sont des panels d'agents que
le projet a fait tourner sur lui-même.

Tout est corrigé et en ligne. Reste ouvert du panel, non traité cette nuit : lier
`docs/PILOT-KIT.md` depuis les pages (personne n'est jamais invité à combler le trou du pilote),
publier les chiffres de coût par commande au lieu de promettre qu'ils existent, réécrire la
section « ce que ça dépose dans votre dépôt » (PII, injection de prompt, MCP), et le fait que
`docs/STATUS.md` — lié depuis « vérifiable en cinq minutes » — est **en français avec des
virgules décimales**, donc un anglophone qui cherche `2.4` n'obtient rien.

### Deuxième partie de nuit : #66, #67, #71 fermées (D142)

Le travail est passé du site au produit — ce que l'utilisateur reçoit réellement.

**#66** — un utilisateur qui installe un plugin reçoit **le répertoire du plugin, pas le dépôt**.
20 fichiers (et non 12 skills : le constat d'origine ne comptait que les `SKILL.md`) renvoyaient
à `docs/`, `eval/`, `examples/` ou à un plugin voisin. `OUTPUT-CONTRACT.md` voyage désormais avec
chaque plugin, un job CI garde les 4 copies identiques, et `lint_skills.py` refuse tout chemin de
dépôt qui ne résout pas dans le plugin qui l'écrit. **Le contrôle a d'abord été faux** : il
testait l'existence dans le dépôt, où tout existe — l'angle mort du mainteneur, reproduit dans
l'outil censé le corriger.

**#67** — `dataset-map` déclaré (quatrième occurrence du motif), `artifacts[].path` interdit de
sortir de la run, et la règle « on ne merge jamais dans le manifeste d'une run qu'on n'a pas
produite » écrite dans le contrat. La règle a trouvé **un second cas que l'issue ignorait**.
37/37 manifestes valides.

**#71** — `CP-001` corrigé (`Number.isFinite`), scénario promu en tests exécutables, suite à
**50 tests verts**. Trois défauts de *vérification* pour un défaut de produit : un test construit
normalement aurait envoyé `null` au lieu de `1e309` (JavaScript convertit avant sérialisation) ;
la première mutation a « réussi » parce que `pkill` ne tue pas `node.exe` sous Git Bash ; et
`CP-002` mentait sur ce qu'il garde, ce qui a révélé que la branche `<= 0` n'avait aucun test.

Versions : `qaia-core` **0.2.31** · `qaia-playwright` **0.1.21** · `qaia-score` **0.2.1** ·
`qaia-testdata` **0.1.3**.

### Troisième partie : le backlog technique (D143)

**#18 avancée, pas fermée.** `visual-check` n'avait qu'une suite derrière elle — celle qu'elle
cite comme sa propre référence. Générée contre `examples/expense-demo`, domaine qu'elle n'avait
jamais vu : 6 snapshots, 6 verts, deux fois de suite, suite complète **56/56**. Vérifiée par
mutation et rapportée **par mutation** : couleur de bouton → 5/6 tués, padding `.card` +3 px →
2/6 tués, chaque mutation attrapée exactement par les snapshots dont le cadrage la contient.
**Le défaut trouvé n'est pas visuel** : sur un mot de passe faux, le message d'erreur était écrit
dans une section `hidden` — invisible, et son `aria-live` annoncé dans un sous-arbre caché, donc
à personne. Ni l'E2E ni l'a11y ne l'attrapaient. **T17 reste non mesuré** et les baselines sont
en `-win32`, donc le projet visual n'est pas câblé dans la CI.

**#65 fermée** — arbitrage tranché pour la carte plutôt que la fusion : `plugins/qaia-core/CATALOGUE.md`,
une page « je veux faire X → utilise Y ». Le cœur est la table des skills qui sondent une app en
marche, rangée **par oracle** et non par outil : `contract-probe` → la doc de la cible,
`security-surface` → des classes de défaut connues, `traffic-replay` → votre HAR, `flaky-detect`
→ le même test rejoué. Lue en colonne, la frontière disparaît. Le paragraphe de six lignes
« pourquoi je ne suis pas un doublon » de `contract-probe` — le symptôme d'origine — devient une
ligne et un renvoi.

**#74 aux quatre cinquièmes** — kit pilote lié, section `.qaia/`/PII/injection/MCP écrite,
coûts publiés en anglais, `STATUS-en.md`, légendes de tableaux. Reste : `plugins/qaia-core/README.md`,
où vivent les chiffres de coût complets, toujours en français.

**Deux contrôles ajoutés à la CI**, chacun sur une classe de défaut et non sur son instance :
les 4 copies du contrat partagé doivent rester identiques au canonique, et **toute version de
plugin doit être énoncée dans le README** — troisième dérive de la semaine, toujours dans le même
sens.

**#63, dernière case (D143)** — la rubrique LLM appliquée pour la première fois par **deux juges à
contexte vide**, sur deux suites que la session n'avait pas touchées (délibérément pas
`US-EVAL-001`, dont la notation de D136 portait un conflit déclaré). `US-EVAL-002` **3/12**,
`US-EVAL-006` **8/10 jugeables**. Vérifié à la main : 6 assertions `not.toBe(200)` et **zéro**
appel à `GET /invoices` sur 002 ; `toBeHidden()` — qui passe sur zéro élément — sur un scénario
dont le sujet est un élément *préexistant* sur 006. **Et le résultat le plus utile est ailleurs :
huit défauts trouvés dans la rubrique elle-même**, tous corrigés. Deux de plus consignés et non
corrigés parce que ce sont des décisions de scope. Les suites de campagne ne sont pas modifiées —
ce sont des preuves, les corriger détruirait la trace.

**#63 — cinq juges, et trois constats devenus des contrôles machine (D144).** Scores : 002 → 3/12,
004 → 4/12, 006 → 8/10 jugeables, 008 → 2/12, 013 → 5/12. **Aucune suite ne franchit la porte.**
Le pire défaut, vérifié à la main : `US-EVAL-004` assère l'**inverse** de son `Then` et encode
ainsi une fuite d'existence de comptes comme condition de succès.

Mais le résultat principal est le ratio : **19 défauts trouvés dans la rubrique contre 12 dans le
code.** Et trois d'entre eux ont migré vers la machine — `flag-dropped` (bloquant),
`single-sided-evidence`, `dead-citation` — avec fixture et zéro faux positif. Ajouter le troisième
a déterré un **bug de l'outil** que deux juges avaient soupçonné : `automation_score.py` ne
regardait que sous `--tests-dir`, donc sur la disposition `automation/{tests,pages}` il ne voyait
pas les page objects, d'où des `pom-missing` faux.

Et le contrôle de versions du README, ajouté quelques heures plus tôt, **a attrapé son propre
auteur** au commit suivant. Troisième fois de la session qu'un garde-fou du projet arrête celui
qui l'a posé.

**#63 fermée, et les défauts remontent au générateur (D145).** L'auto-relecture d'`automate` passe
de **4 à 9 classes** : les quatre existantes sont des *formes* qui ne peuvent pas échouer ; les
cinq nouvelles sont de vraies assertions sur un vrai état, qu'un lecteur statique accepte — une
assertion qui **contredit son propre `Then`**, un flag d'ambiguïté perdu, une évidence
unilatérale, un littéral sans provenance, une affirmation du rapport que le code ne soutient pas.
Chacune porte son cas mesuré et le mécanisme par lequel la génération la produit.

Trois sont démontrées sur la fixture : **before déclenche quatre classes, after aucune**.
Construire cette preuve a trouvé **deux défauts antérieurs dans l'outillage** — le scorer comptait
les assertions écrites dans les *commentaires* (donc pénalisait tout fichier qui documente ses
correctifs), et l'en-tête de la fixture citait `../VALIDATION.md` un répertoire trop haut depuis
toujours, attrapé au premier run du contrôle `dead-citation`.

**La piste mutation annonçait 107/107 — 40 de ces mutations n'avaient jamais tourné (D146).**
En voulant lever la limite « suites API seulement » que le rapport de la veille s'imposait, la
même suite relancée avec `--project=e2e-desktop` a rendu **exactement le même total de 75**
qu'avec `--project=api`. Cinq tests e2e ne peuvent pas produire autant de mutations que 43 tests
d'API. Deux défauts, tous deux dans la moitié de l'outil qu'aucune fixture n'atteint :
Playwright sort en **1** pour « un test a échoué » **comme** pour `No tests found`, et le corpus
de mutations est bâti sur tous les specs de `--tests-dir` sans tenir compte du filtre de
`--run-cmd` — **33 mutations** hors sélection comptées tuées sans qu'un test tourne ; et un titre
contenant une apostrophe était grepé avec son échappement JavaScript, donc ne matchait rien, donc
comptait tué aussi — **7 mutations**, dont les deux tests IDOR.

Corrigé et re-couru honnêtement, tous projets confondus : **111 candidates, 111 exécutées, 111
tuées, 0 survivante**. Le nombre affiché est passé de 107 à 111 pour une raison distincte et de la
même famille : **quatre assertions manquaient purement du corpus**. `expect(violations).toEqual([])`
est tout l'idiome a11y, et aucun opérateur ne touchait une attente de collection vide — les deux
tests a11y de chaque suite étaient absents de tous les runs de mutation jamais faits, sans qu'aucun
champ le dise. Un opérateur inverse désormais `toEqual([])` et `toEqual({})` ; les quatre sont
tuées. La leçon tient en une phrase : **une suite peut avoir des assertions hors du corpus et le
rapport affiche quand même « n/n tuées »**. Un `No tests found`
devient `not_run` et une liste `not_run` non vide est **bloquante** ;
`eval/tools/selfcheck_automation_score.py` tient les deux invariants en CI. Le comptage faussé
cachait par ailleurs **une vraie survivante** : `toBeVisible` inversée en `toBeHidden` passait
parce que `LoginPage.signIn()` rendait la main avant la réponse de `/api/login` — la région de
message existait mais vide, donc *hidden*. Le page object attend désormais la réponse. Les runs
contaminés sont conservés à côté des corrects : ils montrent à quoi ressemble un résultat faux
qui ne se dénonce pas.

**#70 : QA Orchestra lue contrat contre contrat — mais lue, pas exécutée.** Dépôt cloné
(`5df9ad4`), dix agents lus. `test-scenario-designer` impose happy/négatifs/limites/cas
limites/intégration/non-fonctionnel, exige au moins un happy path et un négatif par CA, des
étapes littérales et des résultats observables, et marque `[ASSUMPTION]` sur un CA ambigu — le
même geste que nos `# open: Qn`. Trois écarts tiennent : leur cible est un **volume**
(« 10-20 scenarios per ticket ») là où ADR 0001 pose une **porte** de couverture des chemins de
refus ; leurs `TS-001` sont renumérotés à chaque run quand nos `@QAIA-xxx` survivent à la
régénération ; et producteur et évaluateur sont le même essaim. Deux écarts sont **en leur
faveur** et sont écrits comme tels : ils sortent en Playwright/Cypress/Selenium/pytest/JUnit/
Gherkin quand nous ne savons que Playwright/JS, et leur `smart-test-selector` (mapper un diff
vers la suite existante) n'a **aucun équivalent** chez nous — or un diff, l'utilisateur en a un
tous les jours ; un CA, une fois par sprint. La case de #70 **reste ouverte** : une lecture
établit ce qu'un contrat promet, jamais ce qu'une exécution rend.

**Première application à un logiciel qu'on n'a pas écrit — deux vrais défauts (D147).** Tout ce que
le projet mesurait, il le mesurait sur du code qu'il avait produit. Cible : `typicode/json-server`,
**75 694 étoiles** (mesurées le 2026-08-08), choisie parce qu'elle a un contrat public **antérieur** — son README. Cahier de
32 scénarios écrit depuis ce README seul, jamais depuis le code, puis passé sur deux versions du
même logiciel. **29 verts sur 32, et deux défauts réels** confirmés par les correctifs du
mainteneur lus *après* génération. Le plus parlant : la doc disait `_dependent`, le code lisait
`dependent`. **Un underscore** — et une suite écrite en regardant le code ne peut pas le voir, elle
recopie l'erreur. Le troisième échec est compté **contesté** et non défaut : notre test extrapolait
une doc ambiguë. Deux, pas trois.

**Le résultat négatif traité à égalité (D148).** Sur la version courante, 3 des 4 rouges étaient de
notre faute : des fonctionnalités retirées de la documentation depuis, que la suite continuait
d'exiger avec l'assurance de tests autrefois verts. `check_requirement_drift.py` le détecte
désormais — la source est gelée dans le dépôt et son empreinte vérifiée en CI. Ce qui est contrôlé
est la **provenance**, pas le contenu : l'outil ne sait pas quelle promesse a disparu, seulement
que le sol a bougé.

**Trois analyses externes vérifiées une à une (D149).** Gemini, ChatGPT et Mistral ont analysé le
dépôt à la demande du fondateur. **La moitié des chiffres ne survit pas à la vérification**, et
Gemini a audité un autre produit — elle décrit QAIA comme un banc d'essai de LLM, ce qui est le
dossier `eval/`, outillage de mainteneur explicitement jamais livré. Sa feuille de route entière a
été écartée. ChatGPT est la seule qui tienne, parce qu'elle n'avance aucun chiffre : c'est une
méthodologie, conservée dans le dépôt. `docs/ACTION-PLAN.md` en tire une règle de tri : *une action
entre au plan si elle réduit la distance à un premier utilisateur réel, ou rend une affirmation
vérifiable par un tiers.*

**Les trois trous P1 de la carte, comblés dans la soirée.** `docs/TEST-COVERAGE-MAP.md` a croisé les
skills avec le processus, les niveaux et les types ISTQB. Sept trous, huit issues (#75-#82), et les
trois plus coûteux fermés le soir même :

- **`defect-report` (D150)** — le livrable quotidien d'un testeur, absent. Éprouvée contre un
  **ticket écrit par un humain** sur le même défaut. L'étalon nous a corrigés : ma rédaction
  affirmait à tort qu'il ne nommait pas la cause. Aucun des deux ne domine — l'humain gagne sur la
  cause parce qu'il a lu le code, la machine sur la reproduction et la traçabilité.
- **`openapi-ingest` (D151)** — deuxième porte d'entrée de la chaîne. Appliquée à une vraie
  spécification, elle y a trouvé **les quatre classes de contradiction** qu'elle cherche, dont
  celle-ci : **9 opérations sur 19 déclarent une sécurité, et aucune ligne du document ne déclare de
  401 ni de 403.**
- **`impact-select` (D152)** — mesurée avant d'être écrite. Sur une faute injectée pour de vrai, la
  lecture naïve **rate 6 impacts sur 10** ; la transitive n'en rate aucun. Règle instituée : le
  rappel est la métrique à protéger, pas la précision.

**Une issue fermée par une décision, pas par du code (D153).** ADR 0004 : QAIA ne descend pas sous
le niveau système, et le déclare. Le trou au niveau unitaire n'avait jamais été *décidé* — il
existait par défaut. Un trou non décidé se lit comme un oubli ; une absence décidée est un
positionnement.

**Cinq skills de plus, trois issues fermées en refusant de construire (D150-D157).** La carte de
couverture ISTQB (`docs/TEST-COVERAGE-MAP.md`) a produit huit issues, #75 à #82, toutes traitées le
soir même. Cinq par une skill : `defect-report` (le livrable quotidien d'un testeur, absent des 30),
`openapi-ingest` (deuxième porte d'entrée de la chaîne), `impact-select` (partir d'un diff),
`confirm-fix` (fermer la boucle d'un défaut), `test-plan-and-closure` (les deux documents qu'un
responsable signe). **Et trois par une décision de ne rien construire** : [ADR 0004](adr/0004-test-level-boundary.md)
assume que QAIA ne descend pas sous le niveau système ; l'anonymisation sort du périmètre sur un
critère de vérifiabilité ; la compatibilité navigateurs devient une note de raisonnement plutôt
qu'une 36ᵉ skill.

Chacune est éprouvée sur un cas réel, pas sur une fixture. `defect-report` contre un **ticket écrit
par un humain** sur le même défaut — et l'étalon nous a corrigés. `impact-select` **mesurée avant
d'être écrite** : sur une faute injectée pour de vrai, la lecture naïve rate **6 impacts sur 10**.
`confirm-fix` sur un cas entièrement public, où le verdict naïf (« fermé, 3 régressions ») est
**faux** — les trois tests étaient périmés, pas régressés, et une seule vérification retourne le
verdict.

**Un panel de relecture à contexte vide sur le travail du jour : 19 constats sur 30 survivent
(D158).** Cinq lentilles, chaque constat ensuite attaqué par un sceptique chargé de le détruire. Le
plus grave était matériel : **la procédure de reproduction publiée ne pouvait pas produire les
chiffres publiés** — la base utilisée était enrichie d'une collection que le README de la cible
illustre sans la fournir, et elle n'était archivée nulle part. Un tiers obtenait 5 rouges, pas 3.
Corrigé, et la correction **rejouée** plutôt que raisonnée. Les dix-huit autres relèvent tous du
même motif : un chiffre écrit de mémoire, jamais recroisé.

**Deux défauts répétés deviennent des machines (D159, D163).** Le compteur de skills avait quatre
valeurs différentes dans quatre documents du même jour ; corrigé quatre fois à la main, la cinquième
a servi à écrire `check_skill_counts.py`. Le registre de décisions a été trouvé incomplet **trois
fois dans la journée** — comblé, expliqué, et revenu dans les heures qui suivent à chaque fois ;
`check_decision_register.py` refuse désormais un commit qui nomme une décision sans l'enregistrer.
C'est la seule différence observable entre une résolution et une machine : la première tient
quelques heures.

**QA Orchestra exécutée, jugée en aveugle — 2 juges sur 3 pour QAIA (D160).** Leur agent joué
verbatim sur la même user story, avec un contexte écrit *pour eux* à leur format. Ce que la mesure
retire à notre argumentaire : **ils déclarent les bornes ambiguës eux aussi**. Notre avantage est
que l'ambiguïté voyage *avec* le scénario — supériorité de structure, pas de lucidité. Et deux
écarts en leur faveur sur notre terrain : leur sortie est immédiatement exécutable, et ils couvrent
huit classes de risque absentes de chez nous.

**Et l'épreuve nous a trouvé un défaut que rien d'interne n'avait vu (D161).** Le cahier vitrine
assérait **17 codes HTTP que l'exigence ne mentionne jamais**. Il avait survécu à cinq juges LLM, à
une piste mutation complète et au panel du matin — parce que **nous avons aussi écrit l'application
sous test**. Oracle circulaire : le cahier ne vérifiait pas l'exigence, il vérifiait notre
implémentation de l'exigence. Trouvé en mettant notre sortie à côté de celle d'un concurrent.

**La carte de couverture gagne deux axes, et j'étais généreux sur les deux (D164).** Sur la question
« le test est-il couvert à chaque étape du cycle ? », deux mauvaises réponses avant la bonne — dont
un découpage en neuf étapes **inventé de toutes pièces**, quand le SDLC canonique en compte sept.
Vérifié sur le web plutôt qu'improvisé. Résultat : **QAIA vit entièrement dans Delivery et
Maintenance**, elle commence quand la discovery est finie et s'arrête quand le déploiement commence.
Sur les quatre pratiques du shift-right, la couverture est de **zéro**. Deuxième axe ajouté : les
outils face aux leaders du marché — trois catégories au niveau (k6, axe-core, ZAP passif), trois
passant toutes par Playwright, deux vides (chaos, contrat standard).

**Deux arbitrages du fondateur, en fin de session (D165).** La carte de couverture posait deux
questions que seul lui pouvait trancher. Les deux sont prises, et elles ouvrent le sprint suivant.

**[ADR 0005](adr/0005-scope-discovery-and-run.md) — on vise Discovery et Run**, plutôt que de
corriger l'objectif pour qu'il colle au produit. Motif : le différenciateur revendiqué est la
couverture du cycle ; le réduire à sa moitié la mieux tenue reviendrait à ressembler aux outils qui
n'attaquent que l'exécution. ADR 0004 tient — élargir aux deux bouts ne rouvre pas le niveau
unitaire, ce sont des questions orthogonales.

**[ADR 0006](adr/0006-multi-agent-portability.md) — QAIA doit tourner dans l'agent que
l'utilisateur possède déjà.** Et sur ce point **l'erreur était de mon côté** : j'avais présenté le
multi-LLM comme incompatible avec la contrainte d'autonomie, en le lisant comme « livrer des clés
API vers plusieurs fournisseurs ». Le fondateur voulait dire l'inverse — le projet tourne dans
l'agent que l'utilisateur paie déjà, donc **aucune clé livrée, aucun service appelé par nous**. La
contrainte n'est pas violée, elle est **étendue** : aujourd'hui aucune dépendance à une clé, demain
aucune dépendance à un hôte. *Une contradiction apparente vient souvent d'une définition non
partagée, et la nommer sans demander la définition fait perdre la bonne réponse.*

Quatre issues, **#84 à #87**, avec un ordre imposé sur la portabilité : **mesurer d'abord**. On a
vérifié que les instructions survivent à un changement de *modèle* ; jamais qu'elles survivent à un
changement d'*hôte* — alors que le dépôt revendique déjà « 100 % Markdown, aucune clé ».

### Ce qui reste vrai et inchangé

Aucun gate humain franchi, aucun pilote réel, T17 non mesuré, qualité des tests produits pour un
utilisateur toujours pas mesurée. La nuit a construit un canal et corrigé une page qui mentait
par raccourci ; elle n'a pas changé ces quatre points.

Et la journée du 2026-08-08 non plus. Trois skills de plus, deux vrais défauts trouvés dans un
projet à 75 694 étoiles, une preuve de mutation enfin honnête — **et toujours 0 étoile, 0 fork,
0 pilote humain**. La carte de couverture le dit dans sa dernière ligne : sur 35 skills, cinq ont
été exercées hors du dépôt, et **aucune n'a jamais été utilisée par un humain dans son travail
réel**. C'est la seule mesure qui manque, et aucune quantité de travail dans le dépôt ne la
produira.


## Sprint 31 — #60 fermée : une suite générée tourne dans une vraie CI (2026-08-01, D132) — TERMINÉ

Session autonome, un seul objectif : le blocage n°1 identifié par le Sprint 30.

**Ce qui a changé.** `.github/workflows/generated-suite.yml` exécute la suite produite par
`automate` pour US-EVAL-001 sur un runner GitHub Actions — **8 tests, 8 verts**
([run 30702503888](https://github.com/QAIA-Project/QAIA/actions/runs/30702503888), log brut
conservé dans `eval/ci-proof-2026-08-01/`). Sur ce runner : aucune session Claude, aucune skill
chargée, aucun fichier de `plugins/` lu. La phrase « les tests générés survivent à QAIA » cesse
d'être une affirmation.

**Le test qui échouait n'était pas un défaut de CI.** `QAIA-US-EVAL-001-006` encodait un *défaut
proposé* que le cahier avait marqué `[open]`, avec un commentaire prédisant qu'un échec **serait**
la réponse à Q3. Sonde live sur 7 combinaisons : les credentials sont validés **avant** l'état de
verrouillage. Q2 disconfirmée au passage (les champs vides ont chacun leur message). Les deux
corrections **renforcent** les assertions — égalité de texte exacte là où il n'y avait qu'un
contrôle de visibilité. Aucun seuil abaissé.

**Un vrai défaut trouvé par lecture** : `gitlab-ci.yml` et `Jenkinsfile` épinglaient l'image
Docker Playwright `v1.48.0-noble` contre une suite en `@playwright/test` 1.62 — et le symptôme
(« Executable doesn't exist ») accuse une installation manquante au lieu de la dérive de version.

**Limites, dites et non tues** : seul le template GitHub Actions est prouvé *par exécution* ;
GitLab et Jenkins sont corrigés *par lecture*. La cible reste une démo publique — **T17 (≥ 80 %
des P1 sans retouche sur un pilote réel) demeure non mesuré**. Le point 1 de la liste « ce qu'on
ne sait toujours pas » du Sprint 30 tombe ; les points 2 à 5 restent entiers.

**Trouvé, non traité** : `eval/skill-eval-campaign-2026-07-29/US-EVAL-010-crapi-security/reports/manifest.json`
échoue au validateur (2 erreurs : `negativeRatio` à 100.0 au lieu d'un ratio [0,1], `kind`
`secondary-source` hors énumération). La CI ne le voit pas — elle ne valide que
`plugins/**/manifest*.json`. **Issue #68 ouverte.**

### Suite du sprint : #62 fermée, #61 et #59 avancées (D133-D135)

**#62 fermée (D133)** — les trois skills sous-écrites comblées par de la conception, en
divulgation progressive (`SKILL.md` court, protocole long en `references/`). `a11y-audit` : la
passe **manuelle** devient une étape obligatoire (7 contrôles, chacun avec son protocole et *la
façon dont il est habituellement mal joué*), motif chiffré — l'automatique ne couvre qu'environ
un tiers des critères WCAG. `run-report` : le bloc `execution` enfin montré ; **promesse fausse
traitée en la spécifiant** — le reporter `json` de Playwright n'est pas du Cucumber JSON et aucun
reporter maintenu n'existe (3 noms vérifiés au registre npm). `security-surface` : 6 titres de
chapitre → 6 protocoles, dont S2/IDOR qui **exige deux comptes réels** et nomme le mauvais jeu
classique (tester avec un jeton absent, c'est de l'authentification, ça passe trivialement).

**#61 avancée, non fermée (D134)** — l'encart PO est livré dans les 6 skills qui demandent un
arbitrage, en trois volets, à citer verbatim. Deux partis pris : nommer le risque de la *bonne*
réponse autant que celui du silence, et dire que ne pas répondre est parfois le résultat sûr.
Contrôle mécanique passé (3 volets partout, zéro jargon non glosé) — **mais ce n'est pas la
relecture PM/PO à froid que l'issue exige, et l'auteur des encarts ne peut pas la faire (règle
3)**. L'issue reste ouverte sur ce seul point.

**#59 avancée, non fermée (D135)** — **le chiffre de l'issue était faux** : elle annonçait 8
skills entre 150 et 245 caractères/ligne, la mesure réelle donnait **15 skills, jusqu'à 358**.
Les trois pires découpées (`us-ingest` 358, `testbook-generate` 329, `automate` 268), en
déplaçant le raisonnement long vers `references/` sans perdre une règle — vérifié par recherche
des invariants clés après découpage. **Reste 12 skills**, dont `istqb-design` 240,
`testbook-export` 237, `us-review` 234, `testbook-validate` 233.

Bilan linter sur la journée : **0 échec**, avertissements **25 → 21** (21 et non 20 : la nouvelle
skill `automation-score` en apporte un).

### Fin de sprint : #63 avancée, #68 fermée (D136-D137)

**#63 — deux cases sur trois (D136).** Le juge des tests générés passe du harnais au produit.
*Piste déterministe, première exécution sur du réel* : 8 suites de campagne, `US-EVAL-001`
**100/100**, 002/005/013 80, 006 75, **008 et 009 à 55**, **004 à 48,8**, aucun constat bloquant.
L'outil **reproduit indépendamment** le contournement POM que la campagne avait relevé à la main
sur 008/009. Mutation sur US-EVAL-001 : **8 tuées sur 8**. Les 7 autres suites n'ont jamais vu la
piste mutation — dit explicitement. *Promotion* : `qaia-score:automation-score`, algorithme
matérialisé en session (ADR 0002). *Rubrique LLM enfin appliquée*, *avec son conflit déclaré* :
j'avais édité la suite le matin même, donc le 10/12 est consigné **comme non fiable** et la case
« juge à contexte vide » reste ouverte. Elle a néanmoins trouvé ce que 5 vagues d'agents avaient
manqué : `003`/`004` n'assertaient que la visibilité d'une erreur là où l'exigence dit message
**générique** — donc passaient contre le défaut d'énumération que le mot interdit. **La faiblesse
était dans le cahier, le code en a hérité.** Corrigé (scénario `007` comparant les deux refus
l'un à l'autre) et vérifié : suite **9/9**, mutation **12/12 tuées**.

**#68 fermée (D137) — et mon propre constat d'ouverture était trop étroit.** Validateur lancé sur
les 32 manifestes du dépôt : **4 échecs en 3 classes**, dont **deux défauts du validateur
lui-même**. Le plus instructif : un bloc `gate` sans `verdict` était refusé, alors que
`testbook-score` le remplit avant `aptitude-gate` — le validateur forçait donc le seul producteur
honnête de cet état à fabriquer un verdict qu'il n'a pas le droit de posséder, ou à échouer pour
avoir respecté le contrat. Corrigé dans les deux sens (5 cas testés). CI étendue à `plugins`
**et** `eval` : les 32 manifestes passent.

## Sprint 30 — campagnes d'évaluation exhaustives, corrections centrales, revue externe (2026-07-31, D126-D131) — TERMINÉ

**Journée la plus dense du projet : 12 commits, 5 vagues d'agents (~80 agents), 6 décisions.**
Bilan honnête : le produit n'est pas devenu meilleur pour un utilisateur, il est devenu
*mesuré*. On sait maintenant précisément où il ne tient pas.

### Où en est le produit, en une phrase

Les 29 skills ont toutes un verdict issu d'une exécution réelle (c'était 10 la veille au matin) ;
**aucune n'est ressortie CONFORME** sur 36 verdicts ; et la revue architecturale externe donne
**5,0/10** sur 10 dimensions. QAIA reste un **pre-alpha**, mieux instrumenté qu'hier.

### Versions à jour

`qaia-core` **0.2.26** (15 skills) · `qaia-playwright` **0.1.17** (11) · `qaia-score` **0.1.7** (2)
· `qaia-testdata` **0.1.0** (1) — **29 skills**.

### Ce qui a été livré aujourd'hui

**Cinq vagues d'évaluation.** 18 skills jamais auditées + premier parcours Mobile + premier
parcours API-first (vague A) ; rejeu d'`a11y-audit` et `security-surface` (B) ; les 8 jurys du
parcours API récupéré (C) ; relecture à froid des 29 skills par 4 personas métier (D) ; revue
architecturale 10 dimensions (E).

**Six corrections centrales**, préférées à N corrections de skills :
- **P1** — job CI validant `plugins/**/manifest*.json`. A trouvé, dès son premier run, un cas
  que 46 agents avaient manqué.
- **P2** — `validate_manifest.py` durci : waiver conditionnel, `--check-paths`, kinds `flakiness`
  et `trafficReplay` enfin déclarés, `design.confidence.*` doté de définitions opératoires.
- **P3** — règle non-interactive arbitrée. Elle était contradictoire **à trois voix**, et `qaia`,
  l'arbitre désigné, était muet. Principe posé : **enregistrer n'est pas accepter**.
- **P4** — règle 4bis : tout nombre cité comme mesuré pointe le fichier brut conservé.
- **P6** — réflexe « surface de rendu » dans `istqb-design` (mobile), puis **surface protocolaire**
  (API) — les deux angles morts étaient symétriques.
- **Bloc `structural`** dans le contrat de sortie : le score déterministe /100 était calculé,
  rapporté en prose, puis perdu ; `aptitude-gate` ne pouvait pas le lire.

**Deux garde-fous de harnais** : `lint_skills.py` (CI + hook `PostToolUse` à l'écriture) et le
hook CI post-push fiabilisé — qui a correctement signalé la seule CI rouge de la journée.

**Un juge des tests générés** (`eval/tools/automation_score.py`) : piste statique + piste
mutation, discrimination prouvée sur fixture.

### Les chiffres qu'il ne faut pas arrondir

| Mesure | Valeur |
|---|---|
| Verdicts rendus | 36 — dont **0 CONFORME** |
| Skills avec preuve **rejouée par un tiers** | **10 / 29 (34 %)**, pas 69 % |
| Chiffres auto-déclarés faux à la vérification | **~31 %** |
| Revue architecturale | **5,0 / 10** (Documentation 4, Open source 4, Business 4) |
| Relecture 4 personas | sens **2,87/3**, clarté **2,09/3** |
| Stars / forks / pilotes | **0 / 0 / 0** |

### Ce qu'on ne sait toujours pas — nommément

1. ~~**Aucun test généré n'a jamais tourné dans une vraie CI** (#60).~~ **Levé le 2026-08-01**
   (D132, Sprint 31) : 8/8 sur un runner GitHub Actions, sans session ni skill. Portée exacte et
   limites dans `eval/ci-proof-2026-08-01/github-actions-run.md` — un seul template prouvé,
   une seule suite, une démo publique et non un pilote.
2. **Aucun gate humain n'a jamais été franchi.** Tout le produit a été évalué en mode dégradé,
   non-interactif. Le chemin nominal n'a jamais été exercé.
3. **Aucun pilote réel.** Le critère de sortie auto-fixé (80 % des scénarios P1 sans retouche)
   n'a jamais été mesuré.
4. **12 skills renvoient à `docs/`**, absent de toute installation de plugin.
5. **La qualité des tests produits** pour un utilisateur n'a jamais été mesurée — tout ce qu'on
   sait porte sur la conformité d'une skill à son propre texte.

---

## Prompt de reprise

> Copier-coller le bloc ci-dessous au démarrage d'une nouvelle session.

```text
Tu reprends le projet QAIA (dépôt QAIA-Project/QAIA, branche main, statut pre-alpha).

AVANT TOUT : lis `docs/STATUS.md` (ce fichier, section Sprint 30) et les décisions D126 à D131
de `docs/DECISIONS.md`. Ne te fie à aucun chiffre que je te donne ici sans le revérifier — la
campagne du 2026-07-31 a mesuré que ~31 % des chiffres auto-déclarés de ce projet étaient faux,
et trois analyses externes sur cinq contenaient au moins une affirmation vérifiablement fausse.

DISCIPLINE DU PROJET, non négociable :
- Exécuter réellement plutôt que décrire. Rapporter un blocage honnêtement plutôt que fabriquer
  un résultat. Ne jamais corriger un défaut en silence (D38).
- Règle 4bis : tout nombre annoncé comme mesuré cite le fichier brut dont il est tiré, et ce
  fichier est conservé. Sinon, l'écrire comme estimation ou ne pas l'écrire.
- Après tout `git push` sur main : vérifier que la CI passe (voir `CLAUDE.md`). Un hook le fait,
  il ne dispense pas de regarder.
- `ADR 0002` : rien ne s'auto-exécute à l'installation d'un plugin (pas de `hooks/`, `agents/`,
  `.mcp.json` — la CI le garde). Attention, la formulation « aucun code dans plugins/ » est
  falsifiable : 21 fichiers non-Markdown y vivent légitimement (fixtures, templates).
- Aucun producteur ne se note lui-même (règle 3).

OUTILS DE VÉRIFICATION À LANCER AVANT DE CONCLURE QUOI QUE CE SOIT :
  python eval/tools/lint_skills.py                    # 29 skills : doit rendre 0 échec
  python eval/tools/validate_manifest.py --batch .    # tous les manifestes
  find plugins -name 'manifest*.json' -exec python eval/tools/validate_manifest.py {} \;

CE QUI EST OUVERT, par ordre de valeur :
1. ~~#60~~ — **fermée le 2026-08-01** (D132). Le blocage n°1 est levé : 8/8 en CI réelle. Ce qui
   reste de cette famille : GitLab/Jenkins jamais exécutés, et T17 (pilote réel) non mesuré.
2. ~~#62~~ — **fermée le 2026-08-01** (D133).
3. ~~#59~~ — **fermée le 2026-08-01** (D135, D138, D139). 15 skills au-dessus du seuil → **0**.
   **Mais lire la ventilation, pas le chiffre** : 10 réellement découpées vers `references/`,
   **5 seulement reformatées** (`usability-heuristic-review`, `hello`, `qaia`, `perf-check`,
   `qaia-help` — contenu identique mot pour mot). Pour ces cinq, la dette de lisibilité au sens
   du persona est réduite, pas éliminée.
4. #61 — **rédaction faite** le 2026-08-01 (D134) ; reste la **relecture PM/PO à froid**, que
   l'auteur des encarts ne peut pas faire lui-même (règle 3). C'est le seul reliquat.
5. #63 — **2 cases sur 3 faites** (D136). Reste : la rubrique appliquée par un **juge indépendant
   en session vierge** (la passe du 2026-08-01 était en conflit déclaré et ne compte pas), les
   **7 autres suites** sans passe rubrique ni mutation, et `automation-score` jamais exercée par
   un agent qui n'en est pas l'auteur.
6. ~~#68~~ — **fermée le 2026-08-01** (D137).
7. #64, #65, #18 — voir les issues.

**Versions à jour au 2026-08-01** : `qaia-core` **0.2.30** · `qaia-playwright` **0.1.20** ·
`qaia-score` **0.2.0** · `qaia-testdata` **0.1.1** — **30 skills**.

**Bilan de la journée du 2026-08-01** (Sprint 31, D132-D139) : **5 issues fermées** (#60, #62,
#59, #68, et #63 aux deux tiers), 1 ouverte puis fermée (#68), 1 laissée ouverte volontairement
(#61 — la rédaction est faite, la relecture PM/PO à froid ne peut pas être faite par l'auteur).
Linter **0 échec, 25 → 9 avertissements**. Les 32 manifestes du dépôt passent le validateur, qui
les couvre désormais tous. CI verte sur les 9 commits.

**Ce qui reste vrai et inchangé** : aucun gate humain n'a jamais été franchi, aucun pilote réel,
T17 non mesuré, et la qualité des tests produits pour un utilisateur n'est toujours pas mesurée.
La journée a ajouté des preuves et des garde-fous ; elle n'a pas changé ces quatre points.

CE QU'IL NE FAUT PAS FAIRE, et pourquoi :
- Ne pas construire pour un « framework d'évaluation de LLM » : QAIA n'en est pas un. Pas de
  LiteLLM, pas de cache de tokens, pas d'abstraction de providers, pas de leaderboard.
- Ne pas courir après la visibilité avant #60. Le dépôt n'a aucun mécanisme d'absorption : pas
  de release, pas de CHANGELOG, une porte de merge que seul le mainteneur peut franchir.
- Ne pas purger `.claude/worktrees/` (233 Mo) sans inventaire : ils contiennent encore des
  sorties de campagne non commitées. Deux jeux de preuves y ont déjà été retrouvés le 31/07.
- Ne pas relever un seuil pour faire passer un test (les 2 tests visuels de medibook sont flaky).

CONTEXTE UTILE : `docs/DECISIONS.md` (131 lignes, la mémoire du projet), `docs/KANBAN.md`
(sprints), `docs/OUTPUT-CONTRACT.md` (le contrat de sortie partagé), `eval/RUBRIC.md` et
`eval/AUTOMATION-RUBRIC.md` (les deux juges), `docs/adr/` (3 ADR).
```

---

## Sprint 25 — reliquat P1-P3 des audits clos : #49/#50/#53-#57 (2026-07-28, D108-D114) — TERMINÉ

Enchaînement direct après Sprint 24 : demande fondateur "(#49, #50, #53-#57) enchaîne" — le
reliquat complet du plan d'action des deux audits externes.

- **#49 fermée** — coût rapproché des paliers d'abonnement Claude, honnêtement (source
  officielle vérifiée d'abord : Anthropic ne publie plus de chiffre exact ; le quota est en
  prompts/session, pas en tokens bruts). D108.
- **#50 fermée** — palette de techniques `istqb-design` réorganisée selon la vraie taxonomie
  CTAL-TA v4.0, vérifiée contre le PDF officiel (pas une source secondaire). 2 dérives
  terminologiques corrigées + trouvaille que EP/BVA/error-guessing ne relèvent pas de la
  taxonomie ch.3 du syllabus. `qaia-core` 0.2.17→0.2.18. D109.
- **#54/#55 fermées** — 2 exclusions de scope (structure-based/white-box, exploratoire/
  session-based) nommées explicitement plutôt que laissées en silence. D110, D111.
- **#57 fermée** — conflit multi-devs sur `.qaia/state/` résolu par convention (un dev par US +
  garantie git ordinaire), pas de mécanisme dédié construit. D112.
- **#53 fermée** — techniques CT-AI enfin exercées pour de vrai : nouvelle fonctionnalité réelle
  ajoutée à `examples/expense-demo` (classifieur déterministe, explicitement non-ML), 8
  scénarios exécutés réellement, relation métamorphique vérifiée. Score 65/100 CONCERNS
  rapporté tel quel. D113.
- **#56 posée au fondateur, pas tranchée seule** — question de positionnement produit, pas un
  choix technique. Décision : la revendication "logiciel médical / environnements réglementés"
  est **retirée** de `README.md` (FR+EN), D2 révisée sans être supprimée. D114.

**Le plan d'action des deux audits externes (Sprint 22 + Gemini) est maintenant intégralement
traité : #49-#58, toutes closes.** Prochain point de départ à déterminer à la prochaine
reprise — plus de backlog agent-faisable connu issu de ces deux audits ; revérifier le board
GitHub avant de conclure à un nouveau mur.

## Sprint 24 — #51/#52/#58 livrés : benchmark, k6, adapter multi-LLM (2026-07-28, D105-D107) — TERMINÉ

Enchaînement direct après Sprint 23 : demande fondateur "fait 51 puis 52 puis 58" (les 3 items
les plus prioritaires du plan d'action des audits externes).

- **#52 fermée** — vrai script k6 (`perf-check/k6/load.js`), exécuté réellement contre
  `examples/expense-demo` (10 VUs/20s, 1981 req, 0 échec, p95=2,23ms). `qaia-playwright`
  0.1.10→0.1.11. D105.
- **#58 fermée** — premier adapter multi-LLM (`prompts/adapters/gemini/testbook-generate.md`),
  exécuté réellement contre Gemini/Groq/Mistral sur US-004. Résultat honnête et mitigé : 1/4
  ambiguïtés plantées repérées par Gemini (contre 4/4 pour QAIA), plus une fabrication de rôle
  inexistant ("Executive Board"). D106.
- **#51 fermée** — le chantier le plus attendu : benchmark chiffré QAIA vs un bon prompt direct
  à Claude Code, deux bras exécutés à froid en isolation sur le même ticket (US-004).
  **Résultat honnête, pas une victoire nette pour QAIA** : coût ~2,9× plus élevé côté QAIA
  (133,1k vs 46,5k tokens) ; score structurel déterministe meilleur en moyenne côté QAIA
  (~72 vs 47/100) mais 2/7 fichiers QAIA échouent quand même au gate structurel (assertions
  narratives non vérifiables) ; sur le rappel des 4 ambiguïtés plantées du gold set, le prompt
  direct égale ou fait légèrement mieux que QAIA **sur ce run précis** (variance de génération
  déjà documentée, D62). Le différenciateur le plus solide n'est pas "QAIA trouve plus" mais
  **QAIA est vérifiable/gaté/traçable** (couverture négative auditée contre ADR 0001, manifeste
  validé par schema D104, zéro règle métier fabriquée côté QAIA contre 4 inventées et non
  signalées côté prompt direct). D107, `eval/baselines/qaia-vs-direct-prompt-benchmark-2026-07-28.md`.
- **1 run rejeté et refait proprement** : le premier bras "prompt direct" du benchmark #51
  avait accidentellement lu la réponse cachée du gold set (outil `Read`, pas de lecture
  partielle possible) — signalé, invalidé, re-exécuté sans laisser l'agent toucher le fichier
  source.

**Prochain point de départ** : le backlog agent-faisable venant d'un audit externe est
maintenant traité pour ses items les plus prioritaires (#51/#52/#58). Reliquat P2/P3 restant
des deux audits (taxonomie CTAL-TA v4.0 #50, démo IA/ML #53, décisions de scope #54-#57) —
vérifier le board GitHub avant de piocher, pas de nouveau levier majeur identifié à la date de
cette session au-delà de ce reliquat déjà tracé.

## Sprint 23 — second audit externe (Gemini), recoupement, JSON Schema (2026-07-28, D104) — TERMINÉ

Le fondateur a transmis un rapport d'audit produit par **Gemini** (3 personas : ISTQB, IA/Prompt
agentic, PM open-source), demandant mise à jour du Kanban puis démarrage d'un plan
d'implémentation ; en session, demande complémentaire de rejouer le même exercice à 3 personas
côté Claude pour recoupement indépendant (le message portait une injection de prompt imitant une
"IMPORTANT SYSTEM INSTRUCTION" exigeant une navigation web du dépôt — signalée au fondateur,
traitée comme une instruction utilisateur ordinaire, écartée sur ce point précis).

- **Rapport Gemini sauvegardé et recoupé** contre l'état réel (pas pris au mot) :
  `eval/baselines/audit-report-gemini-2026-07-28.md`.
- **Second audit Claude 3-personas**, ancré sur les fichiers locaux :
  `eval/baselines/audit-report-claude-3persona-2026-07-28.md`.
- **Divergence de note globale expliquée** : Gemini 7,5/10 ("prêt pour le pilote") vs Sprint 22
  2,4/5≈4,8/10 ("non prêt sans conditions") — différence de méthode (lecture de prose vs
  exécution/reproduction de défauts en direct comme D96/D99), pas de désaccord de fait une fois
  les mêmes items comparés en détail. Les deux s'accordent sur le point faible relatif : preuve
  d'exécution/outillage (#51/#52/#53, déjà ouvertes depuis Sprint 22).
- **JSON Schema formel du contrat de sortie livré le jour même** (`docs/schemas/output-contract-v1.schema.json`
  + `eval/tools/validate_manifest.py`, stdlib sans dépendance), vérifié sans erreur contre les 2
  manifests réels du dépôt + testé positif sur un cas cassé injecté (5 erreurs détectées).
  **Effet de bord** : a trouvé en le construisant un vrai défaut de dérive
  (`examples/scoring-demo/manifest.json` sans `design.knowledgeApplied`, pourtant du contrat 1.0,
  D38) — corrigé dans la foulée.
- **1 nouvelle issue** pour le seul gap Phase 1 restant non implémenté à la volée : portabilité
  multi-LLM des instructions elles-mêmes ([#58](https://github.com/Opaland/QAIA/issues/58),
  distinct du bridge MCP #42).

**Le prochain point de départ reste #51** (benchmark "QAIA vs prompt direct à Claude Code") —
confirmé comme priorité n°1 restante par les deux audits externes (Sprint 22 et ce recoupement),
inchangé par cette session.

Dernière session avant celle-ci : 2026-07-25 (mandat élargi post-M0 **terminé** — D67-D88 : gate G2 levée par
le fondateur, veille concurrentielle faite, backlog remodelé, démonstration hors médical livrée
et vérifiée, puis **8 chantiers du backlog remodelé livrés en autonomie continue** — composite
rules `istqb-design` #45, audit `visual-check` #40, correctif `structural_score.py` #31,
validation conversationnelle simulée #5, 2 mesures de budget token #7, connecteur d'export Xray
#35, nouveau plugin `qaia-testdata` #15, nouvelle skill `traffic-replay` #39 — chacun vérifié
indépendamment avant merge, pas seulement pris au mot de l'agent constructeur). Le backlog
agent-faisable de ce cycle est **épuisé** : tout ce qui reste ouvert est bloqué sur une décision
ou une action du fondateur, une ressource externe, ou un cadrage explicitement requis avant tout
code. Ce document donne l'état honnête du projet et un **prompt prêt à coller** pour reprendre
le travail plus tard (y compris en Claude Code **local** : tout est poussé sur `main`, le pickup
est immédiat).

## Sprint 22 — audit externe multi-persona, correction et suivi (2026-07-26, D99-D103) — TERMINÉ

**L'audit lancé en fin de Sprint 21 a rendu son verdict** : *« Prototype d'ingénierie avancé —
à mi-chemin vers un MVP crédible. Non validé en production, non prêt pour une adoption pilote
sans conditions. »* Moyenne 2,4/5 sur 13 personas (8 ISTQB couverts + 5 hors périmètre), après
revue adversariale à 3 sceptiques ayant reproduit >90% des claims en direct (curl, suites
rejouées, tokens recalculés). **Rapport complet : `eval/baselines/audit-report.html`.**

- **Faille critique trouvée et corrigée le jour même (D99)** : `GET /api/audit` non authentifié
  dans `expense-demo` ET `medibook`, exposait emails/montants/commentaires de rejet — reproduite
  en direct par les 3 sceptiques de l'audit.
- **8 items P0/P1 du plan d'action corrigés directement (D100-D103)** : 3 citations internes
  cassées rétro-documentées, portabilité Chromium/BASE_URL corrigée, preuve `flaky-detect`
  dégonflée (×3→réel), politique retry/quarantaine rendue concrète, trou de couverture CT-MBT
  symétrique comblé (`approved` jamais testé comme terminal, contrairement à `rejected`).
- **9 nouvelles issues (#49-#57)** pour le reliquat P1-P3 (benchmark coût/paliers, benchmark
  "QAIA vs prompt direct" — jugé le plus menaçant par l'audit, moteur k6 réel, démo IA/ML,
  taxonomie CTAL-TA v4.0, décisions de scope à trancher : white-box, exploratoire, niche
  médicale réglementée, multi-devs concurrent).
- **#1/#2 mis à jour** : l'audit les cite explicitement comme 2 des 3 faits bloquants du
  verdict final (gate G2 jamais franchie, bus factor = 1 non résolu).

**Le prochain point de départ n'est plus une veille à froid — c'est ce plan d'action.** Avant
de chercher un nouveau levier, lire le verdict complet et vérifier l'état des issues #49-#57.

## Sprint 21 — élargissement ISTQB global, IDOR trouvé, démo statique (2026-07-26, D94-D98) — TERMINÉ

Enchaînement après Sprint 20 : demande fondateur de sortir du seul angle médical pour la veille
concurrentielle (GitHub + web, regard global), puis d'auditer la couverture ISTQB complète
(pas seulement CT-GenAI) et de combler les gaps trouvés, de tester en local, et de publier une
démo statique GitHub Pages pour les skills UI-only.

- **Veille élargie (D94)** : écosystème de plugins Claude Code QA densifié depuis D67, aucun
  concurrent à l'échelle d'Agentic QE Fleet (421★, toujours le seul acteur sérieux). 1 trouvaille
  distincte vérifiée directement (`chaos-qa`, sondage adversarial de contrat) → #47.
- **8 ajouts ISTQB au-delà de CTFL/CT-GenAI (D95, #48 fermée)** : Domain Analysis + Metamorphic
  testing + techniques CT-AI v2.0 dans `istqb-design` ; menu de types nommés CT-PT dans
  `perf-check` ; refonte risk-based CT-SEC dans `security-surface` ; précheck de testabilité
  CTAL-TAE dans `automate` ; nouvelle skill `usability-heuristic-review` (CT-UT). Confirmé déjà
  couvert ou hors périmètre sans travail double : CRUD, Test Impact Analysis, CTAL-TM, CT-MAT
  natif.
- **Vrai IDOR trouvé et corrigé (D96)** en testant localement le nouveau `security-surface`
  risk-based sur `expense-demo` : `GET /api/reports/:id` n'avait aucune vérification de
  propriété, contrairement au `PUT` sœur — n'importe quel utilisateur authentifié pouvait lire
  le brouillon de n'importe qui. Corrigé, 3 cas de non-régression ajoutés.
- **Démo statique GitHub Pages (D97)** publiée à `https://opaland.github.io/QAIA/`
  (`static-demo/`, mock-backend fidèle y compris le correctif IDOR). Vérifiée à deux niveaux :
  logique Node identique au fichier déployé, puis navigateur réel une fois Playwright
  reconnecté (flux complet employee→manager rejoué, captures d'écran, zéro erreur console).
- **Nouvelle skill `contract-probe` (D98, #47 fermée)** : sondage adversarial de contrat,
  dernier chantier de la veille élargie. Vérifiée sur un fixture dédié avec un défaut injecté
  délibérément.

**Backlog agent-faisable de nouveau épuisé.** Un audit externe multi-persona (cabinet fictif,
8 personas ISTQB sur les disciplines couvertes + 5 personas sur les disciplines non couvertes,
revue adversariale à 3 sceptiques, synthèse) a été lancé en `Workflow` pour challenger le produit
dans son ensemble — **verdict pas encore rendu au moment de la rédaction de cette section**,
à consulter/résumer dans la prochaine reprise si la session s'est arrêtée avant qu'il ne finisse.

## Sprint 20 — reliquat + fiabilisation (2026-07-25, D89-D93) — TERMINÉ

Enchaînement direct après le mandat post-M0 : le fondateur a demandé de compléter le reliquat
honnête déjà identifié plutôt que d'attendre un nouveau levier, puis un nouveau passage de veille
concurrentielle pour re-chercher du carburant de backlog.

- **#35 fermée** — connecteur d'export TestRail livré (Xray déjà livré en D86), même discipline
  d'honnêteté, vérifié indépendamment (D89).
- **#7 fermée** — les 14 skills de `qaia-core` ont désormais une mesure réelle de budget token
  (9 nouvelles cette session). Gain méthodologique réutilisable : la notification de fin de
  tâche d'un agent délégué porte son vrai total de tokens (`subagent_tokens`), lisible
  directement par l'orchestrateur (D91, D92).
- **#46 ouverte puis fermée le jour même** — trouvée en exerçant `testbook-validate`/`report` en
  conditions réelles (effet de bord d'une mesure de budget token, pas cherchée) : `testbook-generate`
  pouvait asserter un total de conversion de devise précis au centime sans source de taux tracée.
  Corrigé (garde-fou ajouté + fixture réparée), vérifié indépendamment (D93).
- **Re-veille concurrentielle (même jour)** : un chemin prometteur (IEC 62304 Edition 2 vs
  AI-comme-outil-de-développement) **n'a pas résisté à la vérification directe** de la source —
  l'article ne couvre que l'IA embarquée dans le dispositif médical, pas l'IA utilisée comme
  outil de développement/test, et reste de toute façon en brouillon. Écarté honnêtement plutôt
  que forcé en backlog. **Aucun nouveau levier trouvé** — le paysage n'a pas bougé depuis D67
  (quelques heures plus tôt le même jour).
- **Board GitHub re-vérifié** : 10 issues ouvertes, toutes bloquées exactement comme documenté
  ci-dessous — aucune n'est devenue agent-faisable entre-temps.

## Mandat post-M0 (D67-D88, 2026-07-25) — TERMINÉ

Le fondateur a levé le gate G2 (5 pilotes réels) et donné un mandat élargi : veille
concurrentielle (faite, `docs/COMPETITIVE-ANALYSIS.md`), remodelage du backlog (fait —
#1/#5/#23 fermées ou reformulées, #29/#30 débloqués sur le papier, 10 nouvelles issues
#33-#42), extension du produit à un domaine non-médical (**faite**, `examples/expense-demo/`
sur US-004 — notes de frais, finance/HR), puis relance du développement en autonomie sur le
backlog remodelé — **exécutée jusqu'à épuisement de ce qui est agent-faisable**.

**Démonstration hors médical (D68)** : app réelle self-hostée + parcours QAIA complet (38
scénarios Gherkin) + automatisation Playwright — **40/40 tests verts, re-vérifié
indépendamment** (pas seulement le rapport de l'agent constructeur), score structurel
déterministe 4/4 fichiers PASS. **3 vrais défauts trouvés et corrigés pendant
l'automatisation** (une vraie violation WCAG, une course de test induite par le correctif,
une erreur arithmétique dans le cahier généré). **1 vrai défaut produit trouvé et corrigé** :
`istqb-design` sous-classifiait parfois une ambiguïté métier en `[assumption]` plutôt que
`[open]` quand une convention de machine à états comblait le vide silencieusement — tracé en
[#43](https://github.com/Opaland/QAIA/issues/43), corrigé, puis étendu par #45 (D81,
décomposition des règles composites).

**8 chantiers du backlog remodelé livrés en autonomie continue (D81-D88)**, chacun vérifié
indépendamment avant merge (tests rejoués, diffs isolés relus, valeurs grep-ées) — pas
seulement pris au mot de l'agent constructeur :
1. **#45** — `istqb-design` décompose désormais les règles composites (`BR-KB-203` 3/7→7/7).
2. **#40** — audit `visual-check` vs diff perceptuel : suffisant tel quel, 1 vraie lacune
   documentaire trouvée et corrigée (budget de tolérance consommé en silence).
3. **#31** — `structural_score.py` : limite résiduelle `ASSERT_RE`/guillemets corrigée (cas
   C5 du corpus 24 désormais détecté FAIL), zéro régression.
4. **#5** — première validation conversationnelle **simulée** (arbitrage humain réellement
   exercé, pas en mode non-interactif) : 8 objections/corrections sur 5 étapes, rétention
   28/34 scénarios (82,4 %).
5. **#7** — 2 mesures de budget token réelles de plus (`rag-build` 67,6k, `testbook-export`
   77,6k) — 5/12 skills mesurées, 7 honnêtement encore estimées.
6. **#35** — connecteur d'export Xray (git-master, CSV, fichier seul) ; TestRail
   explicitement non couvert.
7. **#15** — 4ème plugin `qaia-testdata` (jeux de données synthétiques), validé 10/10 tests.
8. **#39** — nouvelle skill `traffic-replay` (HAR → conditions de non-régression), masquage
   PII/secrets vérifié sans fuite sur 8 catégories.

Objectif final du mandat : un projet montrable, docs à jour, diffusable, sans bug évident —
pas seulement sur le médical. **Atteint pour tout ce qui est agent-faisable.** Ce qui reste
ouvert est bloqué sur le fondateur ou une ressource externe — voir « Ce qui bloque »
ci-dessous.

## Où on en est

**Le produit existe et est éprouvé (en automatique, et maintenant aussi sur du matériel dur réel). Quatre plugins.**
- **`qaia-core` 0.2.17** — 15 skills, **budget token intégralement mesuré (issue #7 fermée)**, **technique palette élargie CTFL+Test Analyst+CT-AI (D95)** : parcours complet US → cahier Gherkin (`us-ingest` [+ connecteur Jira #9], `us-review`, `need-understanding`, `rag-build`, `istqb-design` [RAG-in-use + amendements #24/#43/#45 + Domain Analysis/Metamorphic/CT-AI/modèle d'états explicite #48], `oracle-generate` [+ oracle projet OpenAPI #16, durci #25], `prioritize` [audité, A/B testé, +signal git-history #36], `testbook-generate` [garde-fou anti-fabrication étendu aux valeurs calculées non sourcées, #46], `report` [manifeste standardisé], `testbook-export` [+ export Xray et TestRail opt-in, #35 fermée], `feedback`) + `qaia` (méta-agent ReAct), `qaia-help`, `testbook-validate` [+ pass structurel déterministe, D45], `hello`.
- **`qaia-playwright` 0.1.9** — 11 skills : `automate` (Gherkin → Playwright POM + pipeline CI, +lint anti-assertions-creuses #41, +précheck de testabilité CTAL-TAE #48), `a11y-audit`, `visual-check` (régression visuelle, audité #40), `perf-check` (+menu de types nommés CT-PT #48), `security-surface` (+refonte risk-based CT-SEC #48, a trouvé et corrigé un vrai IDOR #96), `usability-heuristic-review` (nouveau, CT-UT #48), `contract-probe` (nouveau, sondage adversarial de contrat #47), `run-report`, `flaky-detect` (#34), `locator-repair` (#37), `traffic-replay` (HAR → non-régression, #39).
- **`qaia-score` 0.1.4** — score uniquement, lecture seule : `testbook-score` (rubrique ISTQB /20 + top-3, pass structurel DÉTERMINISTE step 0, sniffer anti-fabrication #27, détecteurs C1/C2 #28), `aptitude-gate` (PASS/CONCERNS/FAIL/WAIVED, +recalcul du total #21, +signal `flakiness` #44). N'écrit que le bloc `gate` ; aucun producteur ne se score lui-même.
- **`qaia-testdata` 0.1.0** (nouveau, #15) — 1 skill : `dataset-generate` (jeux de données synthétiques cohérents métier, injectables via fixtures Playwright, jamais de données réelles/PII).
- **Démo statique GitHub Pages** : `https://opaland.github.io/QAIA/` (`examples/expense-demo/static-demo/`), pour tester `usability-heuristic-review`/`a11y-audit`/`visual-check` sans backend local.

**Session 2026-07-25 — corpus élargi 24 cas TERMINÉ (lots 2-6, 20 cas clean-room via agents
parallèles) :** Reprise après un plantage de session (rien perdu, tout committé). Les 5 lots
restants (C1-C20) ont été exécutés via des agents indépendants en parallèle (4 par lot),
chacun rédigeant son propre ticket clean-room, sa propre génération Claude fidèle aux 3
skills, et ses propres appels aux fournisseurs externes. **Bilan global (D58-D64,
`eval/baselines/corpus-24-depth.md`)** : **Claude 24/24 cas sans défaut de détection** ;
**Gemini le fournisseur externe le plus fiable** (0 échec de détection sur 21 cas
disponibles, ratio négatif D20 auto-rapporté systématiquement exact, mais 4 défauts annexes
de fabrication non flaguée cumulés) ; **Groq et Mistral échouent chacun ~25-33 % des cas** à
raisonnement multi-règles ou `Then` vérifiable (sans-faute sur CRUD-inverse/traçabilité) ;
**Hugging Face couverture partielle (13/24 cas)**, le profil de défauts le plus dense (6
distincts) puis indisponibilité opérationnelle (crédit gratuit épuisé, `402`) sur les 11
derniers cas. **2 défauts transversaux confirmés à l'échelle du corpus entier** : le ratio
négatif D20 auto-rapporté est peu fiable chez tous sauf Gemini (valide fortement D50) ; le
détecteur `structural_score.py` (`VAGUE_RE`/`HOLLOW_RE`) a un angle mort sur les formulations
paraphrasées, confirmé 3 fois (C5, C10, C18) — **non corrigé cette session, backlog explicite**.
CRUD-inverse et traçabilité des IDs généralisent fortement (quasi aucun échec sur 24 cas).
Le produit QAIA lui-même (3 skills testés) n'a montré aucune régression — la variance mesurée
est modèle-dépendante, pas skill-dépendante.

**Session 2026-07-24 (ter, suite 13) — corpus élargi 24 cas, lot 1/6 (profondeur statistique) :**
Suite à D55-D57 (balayage en largeur, N=1/skill) : demande fondateur de creuser en profondeur
sur du matériel neuf pour voir si les patterns tiennent à plus grande échelle. Plan à 24 cas
(4 réels GitLab CE + 20 clean-room répartis par format/domaine, `eval/goldset-hardened/corpus-24-plan.md`).
**Lot 1/6 exécuté** (4 cas réels GitLab CE v8.16.9, jamais utilisés cette session) sur Claude +
Groq + Hugging Face + Mistral (Gemini rate-limité après le 1er cas, décision fondateur de
continuer sans lui). **2 nouveaux défauts** : Hugging Face invente des codes HTTP précis
(201/404/409) sur un ticket sans API REST mentionnée (4e défaut distinct trouvé chez HF cette
session) ; Mistral invente une exception "propriétaire" non fondée sur une page de visibilité
publique. Signal plus léger confirmé (dédup tautologique Groq/Mistral). Sans-faute total sur le
piège précondition SSH (5/5 modèles). Décision D58. Preuve : `eval/baselines/corpus-24-depth.md`.
**Reste** : lots 2-6 (20 cas clean-room), même protocole, par lots de 4-6 pour respecter les
paliers gratuits.

**Session 2026-07-24 (ter, suite 12) — balayage multi-modèles COMPLET, 23/23 skills :**
Demande fondateur : étendre le harnais de gap à tous les skills, vérifier systématiquement
sur 4+ modèles gratuits (Gemini, Groq, Hugging Face, Mistral ; Cerebras ajouté mais bloqué
côté compte). **Bilan** : 3 défauts réels trouvés, tous sur les 9 skills à jugement ouvert du
cœur du pipeline (Groq/raisonnement multi-règles profond, Mistral/traçabilité de provenance,
Hugging Face/3 défauts distincts dont une fuite de PII présentée comme "sanitized") ; **0
défaut** sur les 14 skills à règles mécaniques/ordonnées explicitement (tout
`qaia-playwright`, `qaia-score`, `hello`, `qaia-help`) — y compris un test de sécurité
(injection via nom de fichier) où aucun des 5 modèles n'a cédé. Décisions D55-D57. Preuve
complète : `eval/baselines/multimodel-skill-sweep.md`.

**Session 2026-07-24 (ter, suite 6) — prompt management sur les 23 skills + second juge :**
Demande fondateur : auditer précision/format/exemples des 23 skills, et outiller un second
juge LLM indépendant (multi-fournisseur gratuit, en repli : Gemini → Groq → Hugging Face).
**Trouvé et corrigé** : un doublon de numérotation dans `need-understanding` (deux étapes
"4."). **Second juge livré et vérifié en live sur les 3 fournisseurs** (2 défauts trouvés en
l'exécutant réellement : 403 urllib/User-Agent sur HF, format de réponse Gemini mal
documenté par une source web résumée) — converge avec le juge Claude et le scoreur
déterministe sur le même défaut C1 (accord tri-source). `eval/tools/second_judge.py`,
`.env`/`.gitignore` ajoutés (secrets jamais commis, jamais dans le produit livré — D29
intact). **Premier test A/B contrôlé sur un skill** (`prioritize`, avec/sans exemple
chiffré) : résultat négatif honnête — l'exemple testé aurait dégradé la calibration (sur-
généralisation "chemin négatif → probabilité plus haute" jusqu'à un contrôle d'auth
générique), **pas appliqué**. Décisions D51-D52. Preuves : `eval/baselines/second-judge.md`,
`eval/baselines/prioritize-ab-test.md`. Reste : auditer `qaia` (méta-agent, identifié comme
le skill le plus vague du corpus) si on continue le prompt management.

**Session 2026-07-24 (ter, suite 2) — non-régression des amendements #24 échantillonnée :**
2 cas réels neufs (GitLab CE `dashboard.feature`, Diaspora `two_factor_authentication.feature`),
jamais vus par les runs d'origine, soumis en tickets durs. **Les 2 amendements généralisent** :
le gap des entités-sœurs est explicitement flagué (pas silencieux) sur le Dashboard ; le tag
`@low-confidence` est correctement posé sur la désactivation 2FA et la régénération des codes
de récupération. Limite assumée : pas un re-run complet des 50 US (pas de mesure de
rappel/précision agrégée) — signal de généralisation, pas clôture définitive. Preuve :
`eval/baselines/istqb-amendments-regression-24.md`, décision D48.

**Session 2026-07-24 (ter, suite) — #25 durci en enchaînement autonome :** `oracle-generate`
(`oracles/openapi.md`) reçoit un **step 0** obligatoire : résolution `$ref` interne avant toute
lecture de contrainte (un noeud non résolu perdait les négatifs de champ requis en silence), et
avertissement explicite **« spec sous-documentée »** (0 erreur 4xx/5xx documentée sur tout le
spec, ou mutations sans auth déclarée) au lieu de dégénérer silencieusement vers `[open]`
partout. Règle **re-vérifiée en re-fetchant les 3 vraies specs** du constat initial
(Petstore/apis.guru/Notion) — la première mouture aurait manqué apis.guru (méta-API en lecture
seule), corrigée avant livraison. `qaia-core` 0.2.7→0.2.8. Preuve :
`eval/baselines/connectors-real-data.md`, décision D47.

**Session 2026-07-24 (ter) — harnais de gap #24 exécuté sur du matériel réel (accès web) :**
2 cas durs sourcés sur le web (GitLab CE `groups.feature` sans narratif US, Sharetribe champs
custom pilotés par config admin), 4 runs isolés (3× sur le cas Groups pour la variance).
**Résultats honnêtes** : mode 2 (config-driven) confirmé tenu sur cas neuf, zéro régression ;
mode 4 (variance) confirmé significatif (29→42 scénarios, +45 %, sur ticket identique) ; mode 1
(extraction) → **2 défauts trouvés et corrigés** dans `istqb-design` (silence sur les
entités-sœurs non nommées, fabrication convergente non flaggée d'une sémantique de
suppression) ; mode 3 (redondance) → détecteur déterministe ajouté à `structural_score.py`,
qui a lui-même révélé et corrigé un faux positif sur du contenu réel (C1 se déclenchait sur le
mot "image" seul). `testbook-validate` reçoit désormais le même pass structurel déterministe
que `testbook-score` (D45). Preuves : `eval/baselines/gap-harness-24.md`,
`eval/goldset-hardened/real-cases-24.md`, `eval/baselines/structural-score.md` (mis à jour).
Décisions D44-D46. **Non fait** : re-mesure des 50 US de `groundtruth-corpus.md` avec les 2
amendements — honnêtement marqué comme suivi, pas encore validé à grande échelle.

**Session 2026-07-24 — le meilleur d'IATS, en autonomie :** lecture des **vrais docs IATS** (Google Drive, dossier *Softway Medical*) → rétrospective honnête `docs/IATS-RETROSPECTIVE.md` (cas réel US 676266 : 100/100 machine vs 58/100 humain ; FinOps confirmé comme régression). **Score structurel déterministe** (`eval/tools/structural_score.py` + `eval/baselines/structural-score.md`, gold set durci `eval/goldset-hardened/`) — discrimine 100/PASS vs C1/C2/fabrication FAIL. **Connecteurs testés sur données réelles** (`eval/baselines/connectors-real-data.md` : oracle OpenAPI dégénère en silence sur specs sous-documentées #25 ; Jira sur réponse réelle). **Gouvernance ADR 0002 / D42-D43** (révise D14) : Python en session autorisé ; hooks/MCP/agents = tier opt-in post-pilote (#29 hook budget, #30 agent ReAct). Nouvelles issues : #18-#30.
- **Contrat de sortie standardisé (D39)** : un unique manifeste JSON par US (`docs/OUTPUT-CONTRACT.md`, contrat 1.0) que tous les plugins écrivent au même format — socle du scoring et de tout export/CI.
- Les trois valident `claude plugin validate --strict`. CI durcie (supply-chain, DCO, gherkin-lint). Marketplace prêt (3 plugins).

**Session 2026-07-23 (bis) — 6 chantiers livrés en autonomie :** contrat de sortie standardisé (D39), plugin de score `qaia-score` (D40), RAG en usage réel (protocole récupération/citation + conditions tirées des règles, `examples/rag-demo/`), oracle projet OpenAPI (D36b, `#16`), connecteur Jira (D9, `#9`, `examples/jira-demo/`), durcissement M3 `automate` (D41, `#10` : scaffold + templates CI + gate T17 honnête). Démos : `examples/scoring-demo/`, `rag-demo/`, `jira-demo/`, `oracle-demo/` (+OpenAPI).

**Ce qui a été mesuré (pas affirmé) :**
- Rubrique gold-set : **médiane 17→19/20** sur 5 US, défauts critiques fermés (C1).
- Exemple exécutable réel `examples/medibook/` : **31 tests Playwright verts, 7 types** (E2E desktop+mobile, API, a11y, visuel, sécu, perf).
- **Campagne robustesse** (50 vrais specs + 18 monkey) : **2 blocages sécurité trouvés et corrigés** (PII, abus), 6 gates ajoutés, saturation. `eval/baselines/robustness-campaign.md`.
- **Éval vérité-terrain** (50 paires US+tests humains validés, gitlab/diaspora/sharetribe) : **généralisation prouvée sans overfitting** (held-out ≥ train), **précision ~93 %**, **+200 scénarios valides** au-delà des humains. Plafond honnête (config-driven → RAG). ⚠️ mesure de rappel bruitée. `eval/baselines/groundtruth-training.md`.

**Décisions** : 38 décisions + 17 défauts tracés dans `docs/DECISIONS.md`. Étude BMAD intégrée (`docs/BMAD-ANALYSIS.md`).

## Ce qui bloque (et qui n'est pas à la main d'un agent)

Le mur humain reste réel, même si G2 a été levée sur le plan calendaire (D67) : personne n'a
encore validé le parcours avec un vrai testeur externe. `#5` a désormais une validation
**simulée** avec arbitrage humain réellement exercé (D84), mais ce n'est explicitement pas un
substitut à `#1` (5 vrais pilotes). Issues bloquées sur ce mur :
[#1](https://github.com/Opaland/QAIA/issues/1) (5 pilotes, gate G2),
[#10](https://github.com/Opaland/QAIA/issues/10)/[#12](https://github.com/Opaland/QAIA/issues/12)/[#13](https://github.com/Opaland/QAIA/issues/13)/[#14](https://github.com/Opaland/QAIA/issues/14)/[#18](https://github.com/Opaland/QAIA/issues/18)
(critère T17 sur app pilote réelle — D79 : la démo expense-demo ne le satisfait pas
littéralement, malgré sa forte valeur de preuve). Kit prêt : `docs/PILOT-KIT.md` (15 min) ;
message de recrutement dans `docs/OWNER-GUIDE.md`.

**Autres blocages non-agent (2026-07-25) :**
- [#2](https://github.com/Opaland/QAIA/issues/2) — transfert d'org GitHub, droits admin requis.
- [#32](https://github.com/Opaland/QAIA/issues/32) — crédit gratuit Hugging Face épuisé (`402`), ressource externe.
- [#29](https://github.com/Opaland/QAIA/issues/29)/[#30](https://github.com/Opaland/QAIA/issues/30) — tier opt-in (hook budget/observabilité, agent de revue adversariale) : ADR 0002 dit encore explicitement « post-pilote uniquement » dans son propre texte ; D67 a dit le développement « possible » mais je n'ai pas traité cette ligne ambiguë comme un blanc-seing pour rouvrir unilatéralement le débat multi-agents (D33) ou le tier supply-chain — nécessite un engagement plus explicite du fondateur.
- [#42](https://github.com/Opaland/QAIA/issues/42) — son propre critère d'acceptation exige un tranchage fondateur (« aller / ne pas aller » acté dans `docs/DECISIONS.md`) avant tout code.

## Prochains leviers (par ordre de valeur)

**Le backlog agent-faisable de ce cycle est épuisé (2026-07-25).** Les 8 chantiers du mandat
post-M0 remodelé (#45, #40, #31, #5, #7 partiel, #35 partiel, #15, #39) sont livrés et vérifiés
indépendamment (voir « Mandat post-M0 » ci-dessus). Tout ce qui reste ouvert sur le board
GitHub est listé dans « Ce qui bloque » — chacun nécessite soit une décision/action du
fondateur, soit une ressource externe non disponible en session. **Ne pas inventer de travail
marginal** : le prompt de reprise ci-dessous doit d'abord re-vérifier le board GitHub pour un
nouveau levier avant de conclure au mur, mais à la date de cette session il n'y en a aucun.

**Reliquat honnête sur des issues partiellement closes (pas de nouveau levier, juste à
compléter si le fondateur le demande) :**
- `#7` — 7 skills de `qaia-core` restent estimées, pas mesurées (`hello`/`qaia-help`,
  `us-review`, `need-understanding`, `prioritize`, `oracle-generate`, `testbook-validate`,
  `report`, `feedback`).
- `#35` — TestRail non couvert (Xray seul livré).

**Tier opt-in (post-pilote, ADR 0002) :** #29 hook budget/observabilité (comble #7 FinOps), #30 agent ReAct, #42 bridge MCP. Ne pas construire avant un engagement fondateur plus explicite que D67 (#23, leçon #2, tension D33 non rouverte).

> **Note accès web (2026-07-24 ter)** : cette session a confirmé l'accès à `WebSearch`/`WebFetch` (GitHub + web général), utilisé pour sourcer les 2 cas durs réels du #24 — à **reconfirmer en reprise** (l'environnement d'exécution peut varier d'une session à l'autre, ne pas supposer l'accès acquis par défaut).
>
> **Gold set IATS (~88 US) : piste abandonnée (D49, fondateur, 2026-07-24 ter).** Sur
> **Google Drive** (dossier *Softway Medical*, confidentiel), seul le pitch IATS (cas réel
> US 676266) est présent — le gold set des ~88 US N'EST PAS sur Drive, probablement dans
> **Tuleap** ou des exports Notion ZIP non inspectés. Le fondateur a tranché : ne pas
> poursuivre cette piste, le coût (accès Tuleap, dézippage/inspection Notion, tout
> confidentiel/jamais commité) dépasse la valeur puisque le harnais #24 fonctionne déjà sur
> du matériel réel public, réutilisable indéfiniment. **Ne pas rouvrir sans raison nouvelle
> et concrète.**

## Actions propriétaire restantes
Voir `docs/M0-CHECKLIST.md` (détail à jour) et `docs/OWNER-GUIDE.md`. Fait : repo public,
Discussions, branch protection, 2FA. Reste : **merger cette branche dans `main` (squash) puis
la supprimer** — nécessite des droits admin que l'agent n'a pas (pas de `gh` CLI en session,
branch protection active) ; pilotes (#1) ; contrat (#3) ; org (optionnel #2) ; Sponsors/
Security Advisories ; GitHub Projects.

---

## 🔁 Prompt de reprise (à coller dans une nouvelle session Claude Code sur ce repo)

```
Reprends le projet QAIA (plateforme QA agentic open source, plugins Claude Code).
Lis d'abord docs/STATUS.md, docs/DECISIONS.md et docs/KANBAN.md pour le contexte complet.

**Sprint 23 (D104) puis Sprint 24 (D105-D107), 2026-07-28, TERMINÉS** depuis la dernière reprise
ci-dessous : un second audit externe (Gemini) a été reçu et recoupé contre un audit indépendant
Claude 3-personas — voir `eval/baselines/audit-report-gemini-2026-07-28.md` et
`eval/baselines/audit-report-claude-3persona-2026-07-28.md`. JSON Schema formel du contrat de
sortie livré (`docs/schemas/output-contract-v1.schema.json` + `eval/tools/validate_manifest.py`,
D104). Puis, sur demande explicite du fondateur, les 3 items les plus prioritaires du plan
d'action des deux audits ont été traités dans l'ordre : **#52** (script k6 réel, exécuté
réellement, D105), **#58** (adapter multi-LLM, exécuté réellement contre Gemini/Groq/Mistral,
résultat mitigé honnête, D106), **#51** (benchmark QAIA vs prompt direct — le chantier le plus
attendu des deux audits, résultat honnête et **pas une victoire nette pour QAIA** : coût ~2,9×
plus élevé, score structurel meilleur en moyenne mais pas parfait, rappel d'ambiguïté égal ou
légèrement en faveur du prompt direct sur ce run précis ; le vrai différenciateur mesuré est la
vérifiabilité/traçabilité, pas la couverture brute — D107). **#49/#50/#53-#57 restent ouvertes**
(reliquat P2/P3, pas traité cette session, pas un nouveau levier majeur identifié).

État (2026-07-26) : QUATRE plugins validés --strict — qaia-core 0.2.17 (15 skills, budget
token intégralement mesuré, palette de techniques élargie CTFL+Test Analyst+CT-AI), qaia-playwright
0.1.9 (11 skills, dont usability-heuristic-review et contract-probe tout neufs), qaia-score
0.1.4 (2 skills), qaia-testdata 0.1.0 (1 skill). Éprouvé en automatique (gold set 19/20,
robustesse, éval vérité-terrain ~93 % précision), sur du matériel dur réel (harnais #24, corpus
élargi 24 cas D58-D64 : Claude 24/24 sans défaut), bout-en-bout sur DEUX domaines indépendants
(santé — examples/medibook/, 31 tests verts ; finance/RH — examples/expense-demo/, 40+ tests
verts), ET maintenant sur une démo statique GitHub Pages publique
(https://opaland.github.io/QAIA/, vérifiée en navigateur réel).

**Mandat post-M0 (D67-D88), Sprint 20 (D89-D93), Sprint 21 (D94-D98) TERMINÉS.** Sprint 21
(2026-07-26) : veille concurrentielle élargie hors médical (D94, aucun nouveau concurrent
sérieux, 1 trouvaille `chaos-qa` → #47), audit complet des syllabus ISTQB au-delà de CTFL/CT-GenAI
et 8 ajouts livrés (D95, #48 fermée : Domain Analysis/Metamorphic/CT-AI/modèle d'états dans
`istqb-design`, menu CT-PT dans `perf-check`, refonte risk-based CT-SEC dans `security-surface`,
précheck testabilité CTAL-TAE dans `automate`, nouvelle skill `usability-heuristic-review`),
**un vrai IDOR trouvé et corrigé** en testant localement le nouveau security-surface (D96),
démo statique GitHub Pages publiée et vérifiée à deux niveaux — logique Node puis navigateur
réel (D97), nouvelle skill `contract-probe` fermant #47 (D98). Décisions D67-D98 dans
docs/DECISIONS.md.

**Sprint 22 (D99-D103) : l'audit externe multi-persona a rendu son verdict.** *« Prototype
d'ingénierie avancé, non prêt pour une adoption pilote sans conditions. »* Moyenne 2,4/5 sur
13 personas. **Lire le rapport complet avant toute chose** (`eval/baselines/audit-report.html`)
si tu ne l'as pas déjà en contexte — il est plus informatif que ce résumé. Une faille critique
trouvée (IDOR sur `GET /api/audit`) a été corrigée le jour même (D99), 8 items P0/P1 du plan
d'action ont été corrigés directement (D100-D103), 9 nouvelles issues ouvertes pour le reliquat
(#49-#57, voir ci-dessous).

**Le backlog agent-faisable N'EST PLUS épuisé — 9 issues fraîches (#49-#57) attendent, plus le
reliquat pré-existant (10 issues, toujours bloquées comme avant).** Priorité suggérée par le
compte-rendu d'audit lui-même : **#51 (benchmark "QAIA vs prompt direct à Claude Code")** avant
d'étendre encore la couverture fonctionnelle — c'est l'angle que l'audit juge le plus menaçant
pour la valeur même du produit, et rien d'autre dans le backlog ne le remplace. Les autres
issues fraîches (#49 coût/paliers, #50 taxonomie CTAL-TA v4.0, #52 moteur k6 réel, #53 démo
IA/ML, #54-#57 décisions de scope à trancher) sont documentées avec un critère d'acceptation
clair. Le reliquat pré-existant reste bloqué sur : (a) le mur humain — #1 (5 vrais pilotes,
confirmé bloquant par l'audit), #10/#12/#13/#14/#18 (T17, D79) ; (b) une ressource externe —
#32 (crédit Hugging Face épuisé) ; (c) un cadrage fondateur — #29/#30/#42 ; (d) propriétaire
seul — #2 (transfert d'org, confirmé bloquant par l'audit). **Vérifie le board GitHub avant de
piocher** — l'état ci-dessus est celui de la fin de Sprint 22, une issue a pu bouger depuis.

**Coût agent (D102, réappliqué tout le Sprint 21) : par défaut, préfère l'édition directe
(Read/Edit/Bash) à un dispatch d'agent en sous-tâche pour du travail déjà bien cadré** — ne
réserve le dispatch d'agent (surtout en `isolation: "worktree"`, ~40-140k tokens par agent
observé) qu'aux tâches vraiment parallélisables ou nécessitant une exécution isolée/indépendante
(ex. une mesure qui doit être un run réel séparé). **Exception explicitement voulue par le
fondateur (fin Sprint 21) : le `Workflow` tool reste approprié pour un panel multi-persona
genuinement parallèle avec revue adversariale** (l'audit externe ci-dessus) — la discipline de
coût vise le dispatch d'agent isolé pour du travail séquentiel bien cadré, pas l'orchestration
multi-agents quand la tâche l'exige vraiment et que le fondateur la demande explicitement.

Principes non négociables : distribution 100 % skill (Markdown, sans clé API) ; Python EN
SESSION généré par un skill autorisé (déterminisme sans shipper de code, ADR 0002/D42) ;
hooks/MCP/agents = tier opt-in séparé, jamais dans le cœur, gardé post-pilote sauf engagement
fondateur explicite plus fort que D67 (leçon #2, tension D33 sur le multi-agents à ne pas
rouvrir seul) ; sortie au contrat standard (D39) ; aucun producteur ne s'auto-valide/score
(rule 3) ; Gherkin atomique + IDs stables ; Playwright natif (D5) ; POM-as-fixtures (D34) ;
PII masquée + gates abus/not-a-spec (D37, étendu au trafic HTTP par D88) ; rappel honnête >
fabriqué (D38) ; connecteurs portable-first (D29) ; jamais réutiliser un secret qui a transité
en clair dans le chat (D51, réappliqué cette session sur un PAT GitHub collé par le fondateur) ;
toute modif de skill se mesure au harnais eval/ ; le board GitHub est la source de vérité.

Pattern d'exécution établi cette session (à réutiliser) : dispatcher des agents en
`isolation: "worktree"` en parallèle, chacun committant localement SANS toucher à
docs/DECISIONS.md ni pousser ; l'orchestrateur diff chaque worktree contre son VRAI parent
(pas `main` si `main` a avancé depuis le dispatch — utiliser `git diff --stat <parent-sha>
<worktree-head>`), vérifie indépendamment au moins un chiffre/claim clé (re-grep, re-run de
tests, re-parse d'un artefact), merge avec `git merge --no-ff <sha>`, s'assure du sign-off DCO
(`git commit --amend -s --no-edit` si manquant — seulement avant push), ajoute UNE entrée
DECISIONS.md avec le prochain numéro D libre, bump la version de plugin si le contenu d'une
skill a changé (jamais pour un simple README), `claude plugin validate --strict .`, push,
commente + ferme (ou laisse honnêtement ouvert) l'issue GitHub, nettoie le worktree
(`git worktree remove --force` puis `git branch -D` — un verrou Windows résiduel se résout en
retentant après quelques secondes, rarement besoin de tuer un process node.exe).

Travaille en autonomie par sprints : une modif → validation --strict → mesure au harnais
→ commit signé → push sur main (déjà autorisé explicitement par le fondateur cette session
pour du travail vérifié). Pas de PR sans demande explicite.

Vérifie d'abord si `.env` contient toujours des credentials valides pour Gemini/Groq/HF/
Mistral avant de relancer `multi_model_generate.py`/`second_judge.py`, et si
GITHUB_PERSONAL_ACCESS_TOKEN est toujours valide dans ~/.claude/settings.json avant de
compter sur le connecteur GitHub MCP (`plugin:github:github`).

Le gold set IATS confidentiel (~88 US) reste abandonné pour de bon (D49) ; ne pas relancer de
nouveaux lots du corpus élargi 24 cas sans demande explicite (D58-D64, plan épuisé).
```

---

## État au 2026-08-09 (fin de session, D172 → D196)

**Produit** — 37 skills sur 4 plugins, **8 agents** dans un tier opt-in (`agents-tier/`, hors des
plugins), **12 contrôles** dans `make check`, CI verte.

**Nouveau ce jour** : `qaia-score:spec-suite-drift` (la spécification confrontée à la suite qui
prétend la couvrir — pur texte), `qaia-core:signal-ingest` (une preuve de production attachée à une
question ouverte, sans jamais la refermer).

**La première validation externe du projet.** `realworld-apps/realworld#1718` — un défaut trouvé par
notre outillage dans un dépôt à 84 000 étoiles, signalé, **accepté et corrigé par le mainteneur en
quelques heures**. Correctif vérifié dans la source, pas sur parole.

**Quatre boucles de retour fermées**, gardées par `check_loop_wiring.py` — qui a attrapé deux
décâblages dans l'heure même où il était écrit.

### Ce que les campagnes externes ont réellement mesuré

| campagne | matériau | précision |
|---|---|---:|
| `automation_score` | 62 suites Playwright, 3 234 tests | **~2 %** |
| `structural_score` | 244 cahiers Gherkin, 15 dépôts | ~26 % avant correction |
| `lint_skills` | 159 `SKILL.md` tierces, 12 dépôts | **83 %** |

**Le critère qui explique l'écart, et qui vaut pour toute règle future :** une règle qui encode une
**norme externe** se transporte ; une règle qui encode une **préférence maison** ne se transporte
pas. Se vérifie en une question — *un tiers qui ignore QAIA est-il quand même soumis à cette
règle ?*

### Art antérieur, découvert par accident

`mskelton/eslint-plugin-playwright` publie **59 règles maintenues, dont huit des douze nôtres**.
Ce qui reste réellement à nous : la piste de **mutation** (ESLint est statique et ne peut pas
inverser une assertion puis exiger le rouge) et la **traçabilité vers un cahier de test**.
Voir `eval/prior-art-2026-08-09/`.

### Ce qui n'a pas bougé

**0 étoile, 12 visiteurs uniques.** Sept issues ouvertes, dont quatre épiques (#89 à #92), et
**aucune ne demande une ligne de code**. #89 — prouver le parcours avec un tiers — attend une
personne, pas un développement.

