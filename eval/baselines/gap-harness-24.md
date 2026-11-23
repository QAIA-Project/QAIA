# Gap harness — 4 modes d'échec IATS sur cas durs réels (#24)

*2026-07-24. Mesure de gap par skill × mode d'échec, sur du matériel **réel** (pas des
fixtures fabriquées) — cf. la correction de `docs/archive/IATS-RETROSPECTIVE.md` : les cas de démo
ont des AC propres, ce qui masque l'écart d'extraction. Ce harnais utilise deux cas réels
sourcés sur le web (projets open source permissifs, catalogués comme dans
`eval/groundtruth-corpus.md`), délibérément présentés à QAIA sous une forme **dure** (ticket
terse, sans liste d'AC explicite) — c'est le ticket, pas la vérité-terrain, qui est dur.

## Méthode

Pour chaque cas : (1) rédiger un ticket volontairement pauvre en AC explicites (comme un vrai
PM pressé écrirait), grounded sur un vrai feature file mergé ; (2) faire tourner le pipeline
QAIA réel (règles condensées mais fidèles de `us-ingest`/`istqb-design`/`testbook-generate`)
dans une session **isolée, sans accès à la vérité-terrain ni à Internet** ; (3) comparer le
résultat à la vérité-terrain réelle (le vrai `.feature` mergé) pour mesurer le gap ; (4) pour
la variance (mode 4), 3 runs indépendants sur le même ticket.

## Cas A — extraction d'AC implicite + redondance + variance (modes 1, 3, 4)

**Source réelle** : feature "Groups" d'un projet DevOps open source mature (MIT-era, même
famille que `eval/groundtruth-corpus.md` G18), 11 scénarios mergés, **sans narratif US**
(titre + Background seulement) — cas réel de vérité-terrain à AC implicite.

**Ticket dur soumis** (aucune liste d'AC, notes en vrac) :
> Group pages — As a user I want a Group page where I can see my group's projects, its
> activity, and manage members/settings, similar to a Project page but for a collection of
> projects. Notes : groups have owners · non-existent groups should behave sensibly ·
> public groups visible to anyone incl. logged-out · settings page lets you manage the
> group's look (like changing its picture).

3 runs indépendants (aucun contexte partagé) ont produit le pipeline complet (extraction →
technique → conditions → `.feature`). *(analyse comparative détaillée après réception des 3
runs — cf. section Résultats)*

## Cas B — profondeur de contexte / config non décrite (mode 2)

**Source réelle** : feature "User creates a new listing" d'une marketplace open source
(même famille que G38), scénarios de champs personnalisés (dropdown/texte/numérique/
date/checkbox) définis par une configuration admin par catégorie — comportement
**config-driven** au sens exact de la règle-plafond `istqb-design` 3c.

**Ticket dur soumis** : "As a user creating a listing, I want to fill in the listing's
custom fields (dropdown/text/numeric/date/checkbox) so the listing captures the details
relevant to its category" + note que les types existent déjà, sans dire que la définition
par catégorie et les bornes de validation (aire max, format de date, options du dropdown)
sont pilotées par un admin — exactement l'information qu'un ticket réel omettrait.

### Résultat — 1 run

**Verdict : la règle-plafond tient sur un cas neuf.** L'agent a :
- correctement reconnu que le requis/optionnel par champ, les bornes numériques, le format
  de date, et la liste d'options du dropdown sont **pilotés par la configuration** (catégorie
  → admin), et les a **explicitement flaggés comme gap** (G1-G5) plutôt que de les inventer ;
- généré un `Scenario Outline` pour les 5 types de champ (une seule "shape", partitions de
  même comportement/priorité/confiance) — **pas** de duplication pesticide, contrairement à
  la vraie suite humaine qui écrit 5 scénarios atomiques séparés (choix humain légitime mais
  différent — QAIA a fait un choix plus économe, conforme à sa propre règle Outline) ;
  toujours testé les bornes de **format** génériques (numérique non-numérique, date
  malformée) sans inventer la borne métier réelle (aire max 150, observée dans le vrai
  fichier) ;
- reporté honnêtement un ratio négatif ~21-36 % (sous 40 %) plutôt que de le combler par des
  cas de config inventés — conforme à la règle "jamais de padding".

**Ce que ça prouve** : la règle-plafond (D38, ceiling clause 0.2.1) déjà mesurée sur 50 US
tient sur un **nouveau** cas réel non vu — pas une redécouverte, une confirmation de
généralisation. Aucun nouveau défaut de mode 2 trouvé sur ce cas ; à re-tester si un cas plus
retors (config **contradictoire** avec le ticket, pas seulement absente) est trouvé.

## Résultats — Cas A (3 runs isolés, même ticket, même règles)

| | run A1 | run A2 | run A3 | vérité-terrain réelle |
|---|---|---|---|---|
| AC extraites | 9 | 10 | 8 | — (pas d'AC dans le vrai fichier, narratif absent) |
| Scénarios/blocs émis | **29** | **39** | **42** | 11 |
| Ratio négatif reporté | 40.5 % | ~41 % | 42.9 % | non calculé côté humain |
| Outline utilisé pour éviter la duplication | oui (visibilité×rôle) | oui (fichier invalide) | non (3 scénarios `Anonymous ...` quasi-jumeaux) |

### Mode 4 — variance de l'orchestrateur : confirmée, significative

**29 à 42 scénarios (+45 %) sur un ticket strictement identique, mêmes règles condensées,
sessions isolées.** C'est une variance de volume bien plus large que celle déjà mesurée
(rappel pondéré train/held-out, tir unique par US). Le **cœur** de l'extraction est stable
(les 6-7 AC "porteuses" — projets, activité, membres, settings, ownership, groupe
inexistant, visibilité publique — sont retrouvées par les 3 runs) ; **la variance se
concentre dans la queue de l'expansion systématique** (combien de sous-conditions de liste,
d'échantillonnage pairwise, de scénarios de création/unicité sont ajoutés). → nouvelle
mesure, pas encore faite à cette granularité ; à surveiller si `testbook-generate` doit
borner l'expansion (ex. plafond explicite de conditions dérivées par AC) pour rendre le
volume plus prévisible, sans perdre le rappel.

### Mode 1 — extraction d'AC implicite : deux défauts concrets trouvés

Rappel contre les 11 scénarios réels (Groups, GitLab CE), **agrégé sur les 3 runs** :

| Scénario réel | Retrouvé ? |
|---|---|
| Groupe inexistant → réponse sensée | ✅ 3/3 (aucun n'invente le code HTTP 404, absent du ticket — correct) |
| Liste des projets du groupe | ✅ 3/3 |
| Flux d'activité | ✅ 3/3 |
| **Liste des issues assignées (rollup inter-projets)** | ❌ 0/3 |
| **Exclusion des projets archivés (issues)** | ❌ 0/3 |
| **Liste des merge requests (rollup inter-projets)** | ❌ 0/3 |
| **Exclusion des projets archivés (MR)** | ❌ 0/3 |
| Upload d'avatar | ✅ 3/3 |
| **Suppression d'avatar** (bouton "Remove" disparaît, pas d'image) | ⚠️ 3/3 divergent — voir défaut 2 |
| Liste des projets en settings + label "archived" | ❌ 0/3 |
| Visibilité publique pour visiteur déconnecté | ✅ 3/3 |

**Rappel réel : ~5/11 (45 %)** — cohérent avec le plancher structurel déjà documenté (D38),
mais deux défauts précis, jamais mesurés à ce niveau de détail, en ressortent :

**Défaut A — silence sur les entités-sœurs non nommées (extension à istqb-design 3c).**
Les 4 scénarios manqués (issues/MR/archived) ne sont pas un oubli de la règle "énumérer
CHAQUE liste/agrégation" (déjà dans 3c) — ils sont impossibles à dériver car le ticket ne
nomme **jamais** "issue", "merge request" ni l'attribut "archived". Le vrai défaut : **aucun
des 3 runs ne signale, même en gap explicite, que "une collection de projets" pourrait
exposer d'autres agrégations liées aux entités sous-jacentes** (contrairement au Cas B, où
le config-driven a été correctement flaggé). La règle 3c énumère ce qui est *nommé* mais ne
demande jamais "quelles autres collections l'entité mère peut-elle exposer que ce ticket ne
nomme pas ?" → **appliqué : istqb-design 3c amendée** (voir plus bas).

**Défaut B — invention convergente non flaggée d'une sémantique de suppression.** Les 3 runs,
indépendamment, ajoutent le même mécanisme inventé pour l'inverse CRUD de "changer l'image" :
un **reset vers une image par défaut** — alors que la vraie fonctionnalité est une
**suppression** (plus d'image du tout, un bouton "Remove" qui apparaît/disparaît). Aucun des
3 runs ne tague ce scénario `@low-confidence`/`[assumption]` alors que la sémantique exacte
de "supprimer" n'est dérivable d'aucune formulation du ticket. C'est une **fabrication
convergente et confiante** — plus dangereuse qu'une variance aléatoire, car elle se
reproduit de façon stable et pourrait passer une revue superficielle. → **appliqué :
istqb-design 3c amendée** (voir plus bas).

### Mode 3 — redondance : pas de vrai pesticide trouvé, mais le détecteur mérite d'être lu avec discernement

Aucun des 3 runs n'a produit de vraie duplication pesticide (chacun utilise un
`Scenario Outline` pour les cas à même forme). Passer `run-A3.feature` (42 scénarios réels,
pas une fixture) au détecteur déterministe (`structural_score.py`) donne un signal instructif :
3 groupes "redondants" détectés, mais dont 2 sont en réalité des **partitions légitimes**
(visibilité × rôle) écrites en scénarios atomiques séparés plutôt qu'en Outline — un faux
positif *attendu et documenté* (le détecteur compare la forme `Given`/`When`, pas le `Then` ;
voir `structural-score.md`). Confirme que la conception "signal, jamais STOP forcé" pour la
redondance était le bon choix.

**Bonus — un vrai défaut trouvé dans l'outil de mesure lui-même** : en scorant `run-A3.feature`
(contenu réel, pas fixture), le détecteur C1 (image creuse) faisait un **faux positif** sur
`Then the group picture should be the default image` (assertion vérifiable, pas une preuve
déléguée à une image). Corrigé dans `structural_score.py` (voir `structural-score.md`) — la
preuve que ce harnais trouve des défauts dans l'outillage mainteneur, pas seulement dans les
skills produit.

## Correctifs appliqués suite à ce harnais (istqb-design 0.2.7)

1. **Question sur les entités-sœurs non nommées** (défaut A) : quand une AC décrit une entité
   comme "collection de X", la règle 3c demande maintenant explicitement si l'entité X porte
   elle-même des sous-collections/attributs que le ticket ne nomme pas, et les flague en gap
   plutôt que de s'arrêter silencieusement à ce qui est nommé.
2. **Tag bas-confiance obligatoire sur toute sémantique de suppression/reset inventée**
   (défaut B) : quand le CRUD-complétude ajoute l'inverse d'une action de création/mise à jour
   et que le ticket ne précise pas le mécanisme exact, le scénario est tagué
   `@low-confidence`/`[assumption]` — jamais asserté avec confiance.

**Non refait dans cette session (à faire en suivi) : re-mesurer les 50 US de
`groundtruth-corpus.md` avec ces 2 amendements pour confirmer l'absence de régression** — le
changement est petit et ciblé (ajout de règle, pas de réécriture), mais seul le harnais
complet peut le confirmer avec certitude. Honnêteté : ce correctif est mesuré sur 2 cas durs
réels, pas encore re-validé à grande échelle.

## Cas B — pas de nouveau défaut, généralisation confirmée

Voir section dédiée plus haut : la règle-plafond (config-driven) tient sur un cas neuf. Aucun
changement de skill nécessaire pour le mode 2 sur ce cas.

## Bilan du sprint #24

| Mode | Statut | Résultat |
|---|---|---|
| 1 — extraction AC implicite | ✅ mesuré | 2 défauts trouvés et corrigés (entités-sœurs, suppression fabriquée) |
| 2 — profondeur de contexte/config | ✅ mesuré | règle-plafond confirmée, aucun défaut nouveau |
| 3 — données fantaisie/redondantes | ✅ mesuré | pas de vrai pesticide sur ce cas ; détecteur déterministe ajouté + validé (y compris un faux positif trouvé et corrigé dans l'outil) |
| 4 — variance orchestrateur | ✅ mesuré | variance de volume confirmée (29→42, +45 %), cœur d'extraction stable |

Le déterminisme (`testbook-validate` step 2) est maintenant branché sur ce même pass que
`testbook-score`, comme demandé.

