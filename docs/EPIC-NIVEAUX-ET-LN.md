# EPIC E5 — Deux niveaux, deux langues, une campagne

**Écrit le 2026-08-11.** Demande du fondateur : *« terminer la partie E2E et API en Gherkin et en
langage naturel »*, plus *« un rapport de campagne en sortie, s'il n'existe pas dans l'outil »*.

Ce document est le plan d'exécution de cette demande. Il commence par ce qui a été **mesuré**, pas
par ce qui a été supposé — deux des quatre trous annoncés existent bel et bien, un troisième existe
mais pas là où on l'attendait, et le quatrième est **partiellement déjà couvert**, ce qui change ce
qu'il faut construire.

---

## Partie 1 — L'état mesuré, le 2026-08-11

Toutes les lignes ci-dessous sont vérifiables par la commande citée, depuis la racine du dépôt.

| Constat | Vérification | Verdict |
|---|---|---|
| **Aucun scénario ne déclare son niveau de test.** Les étiquettes `@e2e` / `@api` n'existent nulle part dans les quatre plugins. | `grep -rn "@e2e\|@api" plugins --include=*.md` → **0 résultat** | trou **confirmé** |
| **Le niveau est pourtant déjà attendu en aval.** Le contrat de sortie déclare `execution.byType` avec les clés `e2e-desktop`, `e2e-mobile`, `api`. | `docs/OUTPUT-CONTRACT.md:79` | **incohérence** : l'exécution sait un découpage que la conception n'a jamais produit |
| **C'est `automate` qui devine le niveau**, au moment d'écrire le code — *« API-only scenarios use Playwright's… »*, *« projects split by type (e2e-desktop / e2e-mobile / api) »*. | `plugins/qaia-playwright/skills/automate/SKILL.md:83,86` | la décision est prise **au mauvais bout de la chaîne** : par l'automaticien, pas par le concepteur |
| **Aucun rendu en langage naturel.** Ni dans une skill, ni dans un livrable. | `grep -rln "langage naturel\|natural language" plugins/` → **0 résultat** | trou **confirmé** |
| Le seul document en prose, `synthesis.md`, est une **aide à la revue** (compteurs, ordre de relecture, table par technique) — il ne restitue **aucun scénario**. | `plugins/qaia-core/skills/README.md`, § *Deliverable contract* | ne comble pas le trou |
| L'export XLSX porte une colonne « Gherkin text » et rien d'autre de lisible sans formation. | `plugins/qaia-core/skills/testbook-export/SKILL.md:26` | ne comble pas le trou |
| **Le rapport de campagne existe à moitié.** `test-plan-and-closure` produit un plan et un bilan ; mais *« seule la moitié bilan a été appliquée pour de vrai »*, et les deux portent sur **une** US. | `plugins/qaia-core/skills/test-plan-and-closure/SKILL.md:86,91` | trou **partiel** : le document existe, l'**agrégation multi-US n'existe pas** |
| `run-report` couvre **une** exécution d'**une** US. | `plugins/qaia-playwright/skills/run-report/SKILL.md:20` | rien n'agrège N exécutions |
| Catalogue actuel | `find plugins -name SKILL.md \| wc -l` → **37** | — |

### Ce que ces constats disent, en une phrase

> **La chaîne QAIA produit des tests de deux niveaux sans jamais l'avoir décidé, dans une seule
> langue qui n'est pas celle du lecteur qui signe, et ne sait rendre compte que d'une exigence à la
> fois.**

Le niveau de test n'est pas absent : il est **implicite, tardif et non tracé**. C'est pire qu'absent,
parce que `execution.byType` en donne un chiffre qui a l'air d'une mesure de couverture alors qu'il
est le sous-produit d'une heuristique appliquée par la skill qui écrit le code.

---

## Partie 2 — L'arbitrage préalable, et pourquoi il tient

`docs/PLAN-REPRISE.md` porte une règle explicite : **« Aucune 38ᵉ skill tant que E1 n'est pas
fermée »** (E1 = un testeur extérieur a lu un cahier et a dit s'il lui aurait servi).

**Décision du fondateur, 2026-08-11 : la règle est tenue à la lettre — cette EPIC ne crée aucune
skill.** Tout ce qui suit est une **extension de skills existantes** :

| Capacité | Où elle vit | Nouvelle skill ? |
|---|---|---|
| Niveau de test comme donnée | `istqb-design`, `testbook-generate`, `report`, `automate` | non |
| API de bout en bout | `openapi-ingest`, `istqb-design`, `testbook-generate`, `automate` | non |
| Rendu langage naturel | `testbook-export` | non |
| Rapport de campagne | `test-plan-and-closure`, `report` | non |

Le compteur reste à **37**. La règle survit ; la promesse produit avance. C'est le seul arrangement
des deux qui ne demande à personne de mentir.

---

## Partie 3 — L'EPIC, en quatre chantiers et une preuve

### Chantier A — Le niveau de test devient une donnée, décidée à la conception

**Le principe** : le niveau se déduit de **l'interface par laquelle la promesse est observable**, ce
qui est exactement le critère qu'[ADR 0004](adr/0004-test-level-boundary.md) a déjà posé pour
délimiter le périmètre (*« navigateur, HTTP, ou le contrat déclaré d'un service »*). On ne crée pas
un critère : on rend explicite celui qui gouverne déjà.

- `istqb-design` assigne à **chaque condition de test** son niveau — `e2e` (parcours traversant
  l'interface utilisateur) ou `api` (clause de contrat observable en HTTP) — et **justifie** ce choix
  comme il justifie déjà sa technique.
- `testbook-generate` émet **exactement une** étiquette de niveau par scénario, issue d'une liste
  fermée : `@e2e` `@api`. Même discipline que les étiquettes de technique, mêmes raisons.
- Le linter Gherkin **refuse** un scénario sans étiquette de niveau. *(Rappel de sprint 34 : une
  cible de lint qui ne dit pas ce qu'elle vérifie peut passer verte à vide — la règle nouvelle est
  accompagnée de sa fixture rouge, sinon elle ne prouve rien.)*
- `report` remplit un bloc **`design.byLevel`** — bump mineur du contrat (1.0 → 1.1, additif, comme
  la règle 3 du contrat l'autorise).
- `automate` **lit** l'étiquette au lieu de deviner, et route vers le projet Playwright correspondant.
  L'heuristique actuelle devient une **vérification** : si elle contredit l'étiquette, elle le
  signale au lieu de trancher seule.

**Ce que ça débloque, et qui est la vraie raison du chantier** : `execution.byType` cesse d'être un
sous-produit et devient comparable à `design.byLevel`. L'écart *conçu vs automatisé* devient lisible
**par niveau** — « 12 conditions API conçues, 4 automatisées » est une phrase qu'aucun artefact
QAIA ne peut produire aujourd'hui.

### Chantier B — Le niveau API va jusqu'au bout

`openapi-ingest` existe et alimente `istqb-design`. Ce qui manque est **entre la condition et le
scénario** : rien ne dit à quoi ressemble un Gherkin d'API, et le résultat prend la forme de prose
d'interface utilisateur parce que c'est la seule forme que la skill montre.

- Un fichier de référence `testbook-generate/references/api-steps.md` : la forme d'un scénario API
  — précondition déclarative sur l'état de la ressource, **un seul** `When` = une requête,
  `Then` sur le statut, puis sur le corps, puis sur les en-têtes significatifs. Une forme se copie ;
  une prose se réinterprète. *(C'est la leçon mesurée du contrat d'émission, `testbook-generate/SKILL.md:92` :
  deux modèles sur quatre ont échoué sur une règle donnée en prose et réussi sur une forme donnée à copier.)*
- Les techniques déjà dérivables d'une spécification — partitions sur les `enum`, bornes sur les
  contraintes de schéma, chemins de refus depuis les `required` et les codes d'erreur déclarés —
  produisent des scénarios **`@api`** tracés jusqu'à la clause du contrat, pas seulement jusqu'à l'AC.
- `automate` génère ces tests avec `APIRequestContext` (sans moteur de navigateur), et la CI générée
  déclare le projet `api` séparément.
- La porte de refus d'[ADR 0001](adr/0001-negative-coverage-gate.md) s'applique **par niveau** :
  un chemin de refus déclaré dans la spécification et couvert seulement par un scénario d'interface
  utilisateur n'est pas couvert au niveau API. Aujourd'hui, rien ne fait la différence.

### Chantier C — Le rendu en langage naturel

**Règle cardinale, et elle décide tout le reste : la version en langage naturel est une
_projection_, jamais une seconde source.** `testbook-export` porte déjà cette règle mot pour mot
(*« Export is a projection, never a second source »*) ; ce chantier l'étend sans l'affaiblir.

- Nouveau livrable de `testbook-export` : `testbook.<lang>.md` — un bloc par scénario, dans la langue
  du projet, structuré **Préconditions / Action / Résultat attendu**, portant le **même identifiant**
  `QAIA-<US>-<NNN>`, et les étiquettes rendues en mots (priorité, niveau, technique, confiance).
- Les `Scenario Outline` sont **éclatés** en un bloc par ligne d'`Examples`, suffixe `-eN` — même
  convention que l'XLSX, pour que les deux comptent pareil.
- L'XLSX gagne les trois colonnes correspondantes, à côté de la colonne Gherkin qu'il porte déjà.
- **Le garde-fou, qui est le cœur du chantier** : `eval/tools/check_nl_projection.py` vérifie que
  chaque scénario Gherkin a exactement un bloc en langage naturel, que le bloc n'introduit **aucune
  étape absente** du Gherkin, et qu'aucun scénario n'est omis. Éprouvé **dans les deux sens** : une
  divergence injectée doit être détectée, au caractère près.

  *C'est la même logique que `check_skill_counts.py`, `check_decision_register.py` et `gh_comment.py` :
  quand deux textes disent la même chose, ils divergent, et une règle qui se répète malgré son rappel
  n'est pas tenable par l'intention.* Sans ce contrôle, le rendu en langage naturel deviendrait le
  document que les gens lisent et que personne ne re-vérifie — c'est-à-dire un mensonge à retardement.

### Chantier D — Le rapport de campagne

Une **campagne** = N user stories × N exécutions. Aujourd'hui tout est per-US.

- `test-plan-and-closure` accepte un **ensemble** de `<US-ID>` et produit
  `.qaia/reports/campaign-<nom>/campaign-report.md`, plus `campaign.json` — l'agrégation des N
  `manifest.json`, sous le même contrat de sortie.
- Sections, chacune **dérivée d'un artefact nommé**, jamais rédigée : périmètre (les N sources) ·
  couverture par AC **et par niveau** · exécuté vs conçu, par niveau · défauts ouverts à la livraison
  · questions jamais tranchées (`# open: Qn`) · critères de sortie, cochés un à un avec le fichier qui
  le prouve · **ce que les chiffres ne disent pas**.
- **Trois refus, hérités de la skill et renforcés par l'agrégation** :
  1. **Jamais de moyenne qui efface un échec.** « 94 % de réussite » sur une campagne cache quelle US
     est rouge : le rapport nomme l'US, le scénario, et le niveau.
  2. **Aucun chiffre sans le manifeste dont il est lu** (règle 4bis du contrat partagé).
  3. **Aucune US sans manifeste n'est comptée** — elle est listée comme *non mesurée*, ce qui est une
     information, pas un blanc.

### Preuve E — L'exercice croisé, sans lequel les quatre chantiers ne sont que du code

Une cible réelle portant **les deux niveaux à la fois** : une interface utilisateur *et* une
spécification d'API publiée. La chaîne entière tourne dessus, une seule fois, sans raccourci, et **on
publie ce qui n'a pas marché en premier**.

**Ce qui ferme l'EPIC** : un rapport de campagne agrégeant ≥ 2 US et les 2 niveaux, contenant **au
moins un échec réel non lissé**, et un cahier en langage naturel qu'une personne qui n'a jamais vu de
Gherkin lit sans poser de question sur la forme.

**Ce qui ne la ferme pas** : nous, disant que ça marche. C'est déjà écrit ailleurs, souvent.

---

## Partie 4 — Les quatre sprints

> **Numérotation : S38 à S41.** S35, S36 et S37 sont **réservés** par `docs/PLAN-REPRISE.md`
> (épiques E1→E4) et non encore ouverts. Ce plan ne les réutilise pas : le dépôt s'est déjà fait
> prendre une fois par deux calendriers portant les mêmes numéros (correction du 2026-08-09), et
> refaire la même chose serait la deuxième.

| Sprint | Chantier | Test de fin — vérifiable, pas déclaratif |
|---|---|---|
| **S38 — Le niveau devient une donnée** | A | Chaque scénario du jeu de référence porte `@e2e` ou `@api` ; `design.byLevel` est rempli ; **le linter passe au rouge sur une fixture sans niveau** ; `automate` lit l'étiquette au lieu de deviner. |
| **S39 — L'API va jusqu'au bout** | B | Une spécification OpenAPI réelle produit un cahier `@api` exécuté **vert**, tracé clause de contrat → condition → scénario → test → résultat ; la porte de refus d'ADR 0001 s'évalue par niveau. |
| **S40 — Le langage naturel** | C | `testbook.<lang>.md` livré ; `check_nl_projection.py` **prouvé dans les deux sens** (divergence injectée détectée) ; un contrôle de plus dans `make check`. |
| **S41 — La campagne, et la preuve** | D + E | Un `campaign-report.md` agrégeant ≥ 2 US et 2 niveaux, contenant un échec réel, chaque chiffre pointant son manifeste. |

### S38 — Le niveau devient une donnée

| # | Tâche | Terminée quand |
|---|---|---|
| S38.1 | **ADR 0008** — *le niveau de test est une propriété de la condition, pas du script* | Accepté, et **cité** par au moins un fichier hors lui-même *(le défaut exact relevé sur ADR 0007 en sprint 33)* |
| S38.2 | `istqb-design` : niveau assigné et justifié par condition | `03-design.md` porte le niveau sur chaque condition |
| S38.3 | `testbook-generate` : liste fermée `@e2e` / `@api`, exactement une par scénario, dans le contrat d'émission | La règle est dans la **section contrat d'émission**, avec la forme à copier |
| S38.4 | Linter Gherkin : niveau obligatoire + **fixture rouge** | La fixture sans niveau fait échouer `make lint` |
| S38.5 | Contrat de sortie 1.0 → **1.1** : `design.byLevel`, additif | `validate_manifest.py` accepte 1.1 et refuse un `byLevel` incohérent avec `scenarios.total` |
| S38.6 | `automate` : lire l'étiquette ; l'heuristique devient un contrôle de cohérence | Un désaccord étiquette/heuristique est **signalé**, jamais tranché en silence |

**Risque nommé à l'ouverture** : les cahiers déjà générés (`eval/`, `examples/`) n'ont pas
d'étiquette de niveau. Soit on les migre, soit le linter les casse. **Décision : on migre, dans ce
sprint, et la migration est un commit séparé** — un linter qu'on assouplit pour ne pas migrer est
un linter vert à vide, exactement la panne du 2026-08-10.

### S39 — L'API va jusqu'au bout

| # | Tâche | Terminée quand |
|---|---|---|
| S39.1 | `references/api-steps.md` — la **forme** d'un scénario API | La forme est copiable, pas décrite |
| S39.2 | `openapi-ingest` → conditions `@api` tracées jusqu'à la clause du contrat | La trace va plus loin que l'AC |
| S39.3 | ADR 0001 évaluée **par niveau** | Un refus couvert seulement en interface utilisateur n'est plus compté comme couvert au niveau API |
| S39.4 | `automate` : `APIRequestContext`, projet `api` séparé dans la CI générée | La CI générée exécute le projet `api` seul |
| S39.5 | Exercice sur une spécification réelle | Suite verte, `execution.byType.api > 0`, comparable à `design.byLevel.api` |

### S40 — Le langage naturel

| # | Tâche | Terminée quand |
|---|---|---|
| S40.1 | `testbook-export` : livrable `testbook.<lang>.md`, éclatement des `Outline` en `-eN` | Le fichier existe et compte comme l'XLSX |
| S40.2 | XLSX : trois colonnes Préconditions / Action / Résultat attendu | Présentes à côté de la colonne Gherkin |
| S40.3 | `check_nl_projection.py` + **auto-vérification** (`selfcheck_*`, comme les cinq existantes) | Une divergence injectée est détectée et localisée |
| S40.4 | Un contrôle de plus dans `make check`, la cible **annonce** ce qu'elle vérifie | Le contrôle ne peut pas passer vert sur un ensemble vide |
| S40.5 | Lecture par quelqu'un qui n'écrit pas de Gherkin | Son retour est publié **tel quel**, y compris s'il est mauvais |

### S41 — La campagne, et la preuve

| # | Tâche | Terminée quand |
|---|---|---|
| S41.1 | `test-plan-and-closure` accepte N US | Le plan et le bilan portent sur un ensemble |
| S41.2 | `campaign.json` + `campaign-report.md`, agrégation de N manifestes | Chaque chiffre pointe son manifeste (règle 4bis) |
| S41.3 | Les trois refus d'agrégation, avec leur fixture | Une campagne à une US rouge **ne peut pas** produire un rapport qui n'en parle pas |
| S41.4 | **La moitié « plan » enfin exercée** — écrite **avant** la campagne | Le bilan coche des critères de sortie qui existaient avant de connaître le résultat |
| S41.5 | Preuve E sur une cible à deux niveaux | Rapport publié, **échecs d'abord** |

---

## Partie 5 — Ce que ce plan ne résout pas

**Il ne produit toujours pas un utilisateur.** E1 de `docs/PLAN-REPRISE.md` — *quelqu'un d'extérieur
lit un cahier et dit s'il lui aurait servi* — reste ouverte, et aucune des quatre lignes ci-dessus ne
la ferme. Les deux pistes ont des propriétaires différents et n'attendent pas l'une sur l'autre.

**Ce qu'il change quand même pour E1** : le cahier qu'un testeur extérieur recevra sera lisible sans
formation Gherkin, et le rapport qu'un responsable recevra existera. C'est la seule raison
défendable de construire ceci avant d'avoir fermé E1 — et elle est écrite ici pour pouvoir être
reprochée plus tard si elle s'avère fausse.

**Ce que ce plan n'a pas** : il a été écrit par la partie qui exécutera le travail, à partir du seul
dépôt. Aucun testeur extérieur n'a dit que le langage naturel lui manquait — c'est le fondateur qui
l'a demandé, et cette demande est la meilleure donnée disponible, pas une mesure.

---

## Annexe — Décisions prises en autonomie, à contester si elles sont fausses

Le fondateur a tranché deux points (périmètre : niveaux **et** double format ; méthode : extension,
zéro nouvelle skill) puis a demandé de continuer sans interruption. Les six suivantes sont **les
miennes** et n'ont été validées par personne :

1. **Deux niveaux seulement, `@e2e` et `@api`** — pas de `@integration`, qu'[ADR 0004](adr/0004-test-level-boundary.md) place hors périmètre.
2. **Une seule étiquette de niveau par scénario.** Un scénario qui en réclamerait deux est un
   scénario non atomique : c'est un défaut à corriger, pas une étiquette à ajouter.
3. **Quatre sprints, numérotés S38-S41**, un chantier par sprint, la preuve fusionnée dans le dernier.
4. **Le langage naturel est une projection vérifiée par un outil**, jamais une génération. C'est ce
   qui coûte le plus cher dans le chantier C, et c'est ce qui l'empêche de devenir un passif.
5. **La migration des cahiers existants est dans S38**, pas différée.
6. **Le rapport de campagne étend `test-plan-and-closure`** plutôt que `report` : il s'adresse à un
   humain qui signe, comme le plan et le bilan ; `report` reste l'enveloppe machine.

> **Correction du 2026-08-11, relevée par une relecture « chef de projet ».** Ce plan annonçait
> « `make check` passe de 12 à 13 contrôles ». La cible en comptait **17** au moment où le plan a
> été écrit (`git show 4c85ef0:Makefile`), et 23 après la session. Le chiffre de départ était faux,
> donc le test de fin qu'il portait n'était pas vérifiable — dans un document dont la partie 1
> exige une commande derrière chaque chiffre. Corrigé en une formulation qui ne dépend pas d'un
> compte que personne n'avait vérifié.

*Les commandes de vérification de la partie 1 ont été exécutées le 2026-08-11, et chaque référence
à un fichier de skill pointe une ligne relue à cette date. Toute affirmation chiffrée qui n'est pas
accompagnée de sa commande ou de son chemin est à traiter comme non vérifiée.*
