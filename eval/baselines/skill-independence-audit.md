# Audit d'indépendance des skills — chaque brique tient-elle hors pipeline ? (issue #22)

*2026-07-25. Suite à l'auto-audit IATS (`docs/archive/IATS-RETROSPECTIVE.md`, leçon #1 « outils
d'abord, pipelines ensuite »). 17 skills du parcours QAIA (15 `qaia-core` + 2 `qaia-score`)
lisent/écrivent des checkpoints partagés dans `.qaia/state/` et `.qaia/reports/`. 6 sont déjà
réellement autonomes et confirmés (`hello`, `qaia-help`, `testbook-validate`, `oracle-generate`,
`us-ingest`, `rag-build`) — cet audit porte sur les **11 restants**, avec exécution réelle (pas
seulement lecture) sur un sous-ensemble représentatif.*

**Portée exacte (précision du commentaire fondateur sur l'issue, 2026-07-24)** : ce document
couvre le volet « comportement hors séquence » de la leçon IATS #1. Le volet « variance de
l'orchestrateur sur N runs » est repris et élargi par l'issue #24 (harnais de gap par mode
d'échec IATS) — non traité ici.

## Méthode

1. Lecture de chaque `SKILL.md` du parcours (`plugins/qaia-core/skills/*/SKILL.md` +
   `plugins/qaia-score/skills/{aptitude-gate,testbook-score}/SKILL.md`) pour extraire la ligne
   « Prerequisite » déclarée et le checkpoint écrit en sortie.
2. **Exécution réelle** de 7 cas hors séquence — pas une lecture du SKILL.md suivie d'une
   prédiction, mais l'agent se mettant réellement à la place de la skill invoquée, avec pour
   seul contexte son `SKILL.md` et l'état de fichiers réellement créé sur disque dans un
   répertoire de travail (`.qaia/state/US-CANCEL-001/...` construit à la main, fichiers vérifiés
   présents/absents par `ls` avant chaque test, jamais supposés). US de test : abonnement /
   annulation, 3 AC (seuil 24h, message d'erreur, restriction au propriétaire du compte).
3. Les 4 skills restantes des 11 (`us-review`, `need-understanding`, `report`, `testbook-score`)
   n'ont **pas** été ré-exécutées individuellement — leur ligne « Prerequisite: `<fichier exact>`
   (else offer `<skill>`) » suit exactly le même patron mécanique que celui vérifié en direct sur
   `istqb-design`, `prioritize`, `testbook-generate`, `testbook-export` (tests 1-4 ci-dessous).
   Leur verdict est donc **une évaluation par patron confirmé, pas un test indépendant** — c'est
   noté explicitement dans le tableau plutôt que présenté comme équivalent aux tests exécutés.

## Tableau d'indépendance — 17 skills du parcours

| Skill | Plugin | Prérequis déclaré | Ce qu'elle écrit | Testé en direct ? | Comportement observé si prérequis absent | Verdict |
|---|---|---|---|---|---|---|
| `hello` | qaia-core | Aucun | Rien (lecture seule) | Non (déjà confirmé, hors périmètre de ce doc) | — | **Oui** (connu) |
| `qaia-help` | qaia-core | Aucun (lecture seule, `.qaia/` absent → présente les 3 modes d'engagement) | Rien | Non (déjà confirmé) | — | **Oui** (connu) |
| `us-ingest` | qaia-core | Aucun (1ère étape) | `00-source.md`, `journey.md` | Non (déjà confirmé) | — | **Oui** (connu) |
| `testbook-validate` | qaia-core | Aucun — conçu pour auditer *tout* cahier, y compris non-QAIA ; sans source US, marque `not assessable` plutôt que de deviner | Rapport seul (aucun état) | Non (déjà confirmé) | — | **Oui** (connu) |
| `oracle-generate` | qaia-core | Aucun état requis ; lit `01-extraction.md`/`03-design.md` **si présents**, sinon fonctionne en mode bibliothèque autonome (Luhn/ISO 8601/RFC 5322…) | Cas ajoutés à `03-design.md` si le journey existe | Non (déjà confirmé) | — | **Oui** (connu) |
| `rag-build` | qaia-core | Aucun (initialise `knowledge/` seul) | `knowledge/index.md` + fichiers | Non (déjà confirmé) | — | **Oui** (connu) |
| `us-review` | qaia-core | `00-source.md` (else offer `us-ingest`) — ligne 8 | `01-extraction.md` | Non — évalué par patron (identique à istqb-design/prioritize) | Non re-testé isolément | **Oui** (par patron, non re-testé) |
| `need-understanding` | qaia-core | `01-extraction.md` (else offer `us-review`) — ligne 8 | `02-understanding.md` | Non — évalué par patron | Non re-testé isolément | **Oui** (par patron, non re-testé) |
| `istqb-design` | qaia-core | `02-understanding.md` (else offer `need-understanding`) — ligne 8 | `03-design.md` | **Oui — Test 1** | Détecte l'absence, remonte toute la chaîne manquante (00/01/02), propose 2 options concrètes, aucune fabrication de `02-understanding.md` | **Oui** |
| `prioritize` | qaia-core | `03-design.md` (else offer `istqb-design`) — ligne 8 | `04-priorities.md` | **Oui — Test 3** | Avec 00/01/02 présents mais 03 absent : nomme précisément le fichier manquant, ne fabrique pas de conditions à partir des AC déjà visibles, ne redemande pas ce qui existe déjà | **Oui** |
| `testbook-generate` | qaia-core | `03-design.md` **et** `04-priorities.md` (else offer l'étape manquante) — ligne 8 | `.qaia/testbooks/<US-ID>/*.feature`, `coverage-matrix.md`, `synthesis.md` | **Oui — Test 2** | Nomme les 2 prérequis manquants explicitement, refuse de générer du Gherkin depuis le texte brut malgré des AC déjà numérotées et une US crédible | **Oui** |
| `testbook-export` | qaia-core | Cahier généré dans `.qaia/testbooks/<US-ID>/` (else offer `testbook-generate`) — ligne 8 | fichiers exportés (`.feature`, XLSX, `synthesis.md`) | **Oui — Test 4** | Avec 00-04 présents mais aucun cahier : refuse d'exporter, cite la règle interne « no regeneration, no new content », propose `testbook-generate` (déjà prêt à tourner) | **Oui** |
| `report` | qaia-core | Cahier généré (`.feature`, `synthesis.md`, `coverage-matrix.md`, `03-04`) — explicite : « If it is absent, say which step is missing and offer `testbook-generate` — never emit a manifest with guessed counts » | `.qaia/reports/<US-ID>/manifest.json` (section `design`) | Non — évalué par patron (formulation aussi explicite que istqb-design/prioritize) | Non re-testé isolément | **Oui** (par patron, non re-testé) |
| `feedback` | qaia-core | **Aucune ligne « Prerequisite: »** — ligne 8 ne cite que le contrat partagé général, `## Steps` commence directement (ligne 10) | `.qaia/feedback/examples/<US-ID>-<n>.md`, `rules.md` | **Oui — Test 5** | Sur ce run : signale spontanément l'absence totale de `.qaia/`, refuse de fabriquer une vérification du scénario cité, propose d'enregistrer la correction avec provenance « non vérifiée » explicite | **Partiel** — voir constat ci-dessous |
| `qaia` | qaia-core | Aucun prérequis propre — délègue chaque étape « by its book » aux autres skills ; sa fonction est de déterminer l'état du pipeline, jamais de le court-circuiter | Rien directement (orchestration) | **Oui — Test 7** | Objectif final explicite (« génère-moi le cahier ») sur projet vide : ne saute pas à `testbook-generate`, redémarre correctement depuis `us-ingest` | **Oui** (catégorie à part — hérite des garde-fous des skills qu'il appelle) |
| `aptitude-gate` | qaia-score | `## Prerequisite` cite `manifest.json` (ligne 14-16) mais couvre seulement le cas « `gate.score` vide » ; le cas « `manifest.json` totalement absent » est couvert par `plugins/qaia-score/skills/README.md` (ligne 41 : « If no manifest exists yet, the skills say so and offer to run `report` first »), pas par le fichier de la skill lui-même | `gate` block du manifeste | **Oui — Test 6** | Sur ce run : refuse tout verdict sans manifeste, ne fabrique aucun score/comptage, propose `report`/`testbook-generate` | **Partiel** — voir constat ci-dessous |
| `testbook-score` | qaia-score | `## Prerequisites` (ligne 13) : cahier généré + `manifest.json` idéalement ; explicite « If absent, offer to run `report` first; do not score against guessed counts » | `gate.score`/`dimensions` du manifeste | Non — évalué par patron (formulation aussi explicite que istqb-design/report) | Non re-testé isolément | **Oui** (par patron, non re-testé) |

## Les 7 tests exécutés en direct

Chaque test a été réalisé en écrivant/vérifiant réellement l'état de fichiers sur disque
(`ls` avant chaque invocation pour confirmer absence/présence), puis en produisant la réponse
réelle de l'agent jouant le rôle de la skill à partir de son seul `SKILL.md`.

### Test 1 — `istqb-design` sur US brute, aucun `.qaia/` (projet vide)
Détecte l'absence de `02-understanding.md` **et** remonte toute la chaîne (`00-source.md`,
`01-extraction.md` absents aussi), propose de démarrer proprement ou d'accepter le texte brut
comme équivalent avec plus de `[assumption]`/`[open]`. Aucune fabrication.

### Test 2 — `testbook-generate` sur US brute, aucun `.qaia/`
Nomme les deux prérequis manquants (`03-design.md` **et** `04-priorities.md`), refuse de générer
du Gherkin directement malgré des AC numérotées qui auraient pu passer pour une extraction
déjà faite. Aucune fabrication.

### Test 3 — `prioritize` avec 00/01/02 présents, `istqb-design` jamais exécuté
Fichiers réellement écrits : `00-source.md`, `01-extraction.md`, `02-understanding.md` cohérents
(3 questions d'ambiguïté classées). `03-design.md` absent (vérifié). La skill cite précisément
le fichier manquant, ne redemande pas ce qui existe déjà, et surtout **ne fabrique pas de
conditions de test** à partir des 3 AC déjà visibles dans les checkpoints amont — c'est le point
de fabrication le plus tentant du lot (les AC sont juste là, à portée) et il ne s'est pas
produit.

### Test 4 — `testbook-export` avec 00-04 présents, `testbook-generate` jamais exécuté
Fichiers réellement écrits : `00` à `04-priorities.md` cohérents (design + priorités déjà
produits). `.qaia/testbooks/` absent (vérifié). La skill refuse d'exporter, cite sa propre règle
« no regeneration, no new content », et note que `testbook-generate` peut tourner immédiatement
puisque son prérequis à lui est déjà satisfait. Aucune fabrication.

### Test 5 — `feedback` invoquée à froid, aucun `.qaia/` (projet vide)
Cas le plus fragile *structurellement* de la série (voir constat ci-dessous). Message simulé :
correction rapportée sur un scénario `AC1-003` supposé existant. Sur ce run précis, l'agent a
signalé l'absence totale de `.qaia/`, refusé de confirmer avoir vérifié le scénario cité, et
proposé d'enregistrer la correction avec une provenance explicitement marquée « non vérifiée ».
**Comportement correct observé**, mais reposant sur l'application de la règle générale du
contrat partagé (règles 1 et 8 de `plugins/qaia-core/skills/README.md`) plutôt que sur un
garde-fou propre à la skill.

### Test 6 — `aptitude-gate` invoquée à froid, aucun manifeste (projet vide)
Message simulé : demande de verdict de mise en production. Sur ce run, l'agent refuse tout
verdict PASS/CONCERNS/FAIL/WAIVED sans preuve et oriente vers `report`/`testbook-generate`.
**Comportement correct observé**, mais — comme le test 5 — le garde-fou « manifeste absent →
proposer `report` » vit dans le README du plugin, pas dans le fichier de la skill invoquée.

### Test 7 — `qaia` (méta-agent) sollicité pour sauter direct au résultat final
Objectif final explicite dans le message (« génère-moi un cahier complet ») sur projet vide :
l'agent identifie l'absence totale d'état et enchaîne depuis `us-ingest`, sans jamais tenter de
produire un cahier directement depuis le texte brut malgré la demande de vitesse.

## Constat — pas de fabrication observée, mais 2 garde-fous structurellement plus faibles

**Aucun défaut de fabrication n'a été observé dans les 7 exécutions réelles de cet audit.**
Toutes les skills testées, y compris `feedback` et `aptitude-gate`, ont refusé de produire un
contenu inventé (checkpoint, score, verdict) quand leur prérequis manquait — conformément à la
règle du contrat partagé (« prérequis manquant → propose, n'échoue pas »).

Ce qui est réellement trouvé, plus nuancé qu'un bug confirmé, c'est une **différence de
robustesse structurelle** entre deux familles de skills :

- **9 des 11 skills douteuses** (`us-review`, `need-understanding`, `istqb-design`, `prioritize`,
  `testbook-generate`, `testbook-export`, `report`, `testbook-score`, et pour partie `qaia`)
  portent leur propre ligne explicite « Prerequisite: `<fichier exact>` (else offer `<skill>`) »
  ou équivalent, positionnée avant la section `## Steps` — un exécutant qui lit le fichier dans
  l'ordre rencontre le garde-fou avant d'atteindre la logique de génération.
- **2 skills** (`feedback` — `plugins/qaia-core/skills/feedback/SKILL.md` ligne 8, aucune ligne
  « Prerequisite: » du tout, `## Steps` commence directement ligne 10 ; `aptitude-gate` —
  `plugins/qaia-score/skills/aptitude-gate/SKILL.md` lignes 14-16, la section `## Prerequisite`
  existe mais ne couvre explicitement que le cas « manifeste présent mais `gate.score` vide »,
  pas « manifeste totalement absent ») **n'ont pas ce garde-fou local** : le comportement correct
  observé dans les tests 5 et 6 vient de l'application de la règle générale du contrat partagé
  (`plugins/qaia-core/skills/README.md` règles 1/2/8, et `plugins/qaia-score/skills/README.md`
  ligne 41 pour `aptitude-gate`), pas d'une instruction dédiée dans le fichier de la skill
  elle-même.

**Ce n'est pas un défaut confirmé** (les deux runs réels ont été corrects) — c'est un **risque de
spécification documenté honnêtement** : rien ne garantit qu'une exécution moins soigneuse, ou un
modèle moins rigoureux sur le suivi d'instructions (cf. les défauts déjà mesurés sur Hugging
Face/Groq/Mistral dans `eval/baselines/multimodel-skill-sweep.md` et `corpus-24-depth.md`,
D55/D58/D59 — écart mesuré entre ce que ces modèles disent et ce qu'ils font), applique la règle
générale du contrat aussi fidèlement que les 9 skills qui la portent localement. Un correctif
ciblé et à faible risque serait d'ajouter à `feedback` et `aptitude-gate` la même ligne
« Prerequisite: `<fichier>` (else offer `<skill>`) » que leurs 9 pairs — non fait ici, la mission
demandait de documenter, pas de corriger.

## Verdict global sur le couplage

Le pipeline `us-ingest → us-review → need-understanding → istqb-design → prioritize →
testbook-generate` reste une **chaîne souple, pas rigide** : les 4 maillons testés en direct hors
séquence (`istqb-design`, `prioritize`, `testbook-generate`, `testbook-export`) se comportent
exactement comme documenté — ils détectent, nomment précisément le fichier manquant, et
proposent un point de reprise, sans jamais fabriquer le contenu d'un checkpoint absent, même
quand la tentation existait concrètement (test 3 : des AC déjà visibles auraient pu être
recyclées en fausses « conditions de test » sans que rien ne l'empêche mécaniquement). La
leçon IATS #1 n'est donc pas répétée à l'identique : contrairement à un pipeline rigide qui
`throw`, chaque brique testée reste utilisable seule et hors ordre.

Le point qui reste vrai, cependant, est que cette robustesse n'est **pas uniforme** : elle est
forte quand la skill porte sa propre ligne de garde-fou explicite (9/11 skills), et repose sur
un mécanisme plus général et moins visible pour les 2 autres (`feedback`, `aptitude-gate`) — un
point d'attention réel pour la prochaine passe de durcissement des skills, mais pas un
franchissement de garde-fou observé.
