# ADR 0008 — Le niveau de test est une propriété de la condition, pas du script

- Statut : **Accepté**
- Date : 2026-08-11
- Ouvre : sprint S38 de [`EPIC-NIVEAUX-ET-LN.md`](../EPIC-NIVEAUX-ET-LN.md)
- Prolonge : [ADR 0004](0004-test-level-boundary.md), qui fixe la borne basse du périmètre

## Contexte

[ADR 0004](0004-test-level-boundary.md) a décidé où la chaîne s'arrête **par le bas** : QAIA ne
descend pas sous le niveau système, et l'unité de travail est *« une promesse observable de
l'extérieur — un critère d'acceptation, une clause de contrat d'API, une exigence
d'accessibilité »*, exercée *« à travers une interface publique : navigateur, HTTP, ou le contrat
déclaré d'un service »*.

Cette phrase distingue déjà deux interfaces. **Elle n'a jamais été outillée.** Mesuré le
2026-08-11, sur le dépôt :

| Constat | Vérification |
|---|---|
| Aucune étiquette de niveau n'existe dans les quatre plugins | `grep -rn "@e2e\|@api" plugins --include=*.md` → **0** |
| Le contrat de sortie attend pourtant déjà un découpage par type à l'exécution | `docs/OUTPUT-CONTRACT.md` : `execution.byType` = `e2e-desktop`, `e2e-mobile`, `api` |
| C'est `automate` qui décide du niveau, en écrivant le code | `plugins/qaia-playwright/skills/automate/SKILL.md` — *« API-only scenarios use… »*, *« projects split by type (e2e-desktop / e2e-mobile / api) »* |

Autrement dit : **le niveau existe dans la sortie sans jamais avoir existé dans la conception.**
Il est produit par une heuristique appliquée par la dernière skill de la chaîne, à partir de la
forme du texte d'un scénario, sans trace et sans recours.

Trois conséquences, toutes vérifiables aujourd'hui :

1. **`execution.byType` ressemble à une couverture et n'en est pas une.** C'est le compte de ce
   que l'automaticien a rangé où. Rien ne le compare à une intention, parce qu'aucune intention
   n'a été écrite.
2. **L'écart *conçu vs automatisé* ne peut pas se dire par niveau.** « 12 conditions API conçues,
   4 automatisées » est une phrase qu'aucun artefact QAIA ne sait produire.
3. **La porte de couverture des refus ([ADR 0001](0001-negative-coverage-gate.md)) est aveugle au
   niveau.** Un chemin de refus déclaré dans une spécification OpenAPI et couvert seulement par un
   scénario d'interface utilisateur compte comme couvert. C'est faux : la promesse était une
   clause de contrat HTTP, et rien ne l'a vérifiée là où elle est faite.

Le troisième point est le plus grave, parce qu'il fait passer une porte pour verte alors qu'elle
n'a pas été franchie.

## Décision

**Le niveau de test est décidé à la conception, porté par la condition, transporté par le
scénario, et lu — jamais deviné — par l'automatisation.**

1. **Liste fermée, deux valeurs : `@e2e` et `@api`.** Rien d'autre. `@integration` et le niveau
   composant restent hors périmètre par ADR 0004, et une liste ouverte redeviendrait une
   convention par projet, donc rien.
2. **Le critère est l'interface par laquelle la promesse est observable** — celui d'ADR 0004,
   rendu opérationnel :
   - `@e2e` — la promesse ne s'observe qu'à travers l'interface utilisateur (un parcours, un
     rendu, un état visible d'écran) ;
   - `@api` — la promesse est une clause du contrat de service, observable en HTTP sans
     navigateur (statut, corps, en-tête, effet sur une ressource).
3. **`istqb-design` assigne le niveau à chaque condition et le justifie**, comme il justifie déjà
   sa technique. Le niveau entre dans `03-design.md`.
4. **`testbook-generate` émet exactement une étiquette de niveau par scénario.** Ni zéro, ni deux.
5. **`automate` lit l'étiquette.** Son heuristique actuelle devient un **contrôle de cohérence** :
   quand elle contredit l'étiquette, elle le **signale** et ne tranche pas.
6. **`report` publie `design.byLevel`**, ce qui rend `execution.byType` comparable à une intention.

### Pourquoi exactement une étiquette, et pas plusieurs

Un scénario qui réclame `@e2e` **et** `@api` vérifie deux promesses observables par deux
interfaces : il n'est pas atomique, et l'atomicité est déjà une règle non négociable de
`testbook-generate`. **Le cas est un défaut à corriger par une scission, pas une étiquette à
ajouter.** Autoriser le doublon reviendrait à offrir une sortie de secours à la règle
d'atomicité, par le côté.

L'exception connue est le scénario de parcours `@smoke` (un par US, exclu du décompte
d'atomicité) : il traverse par définition l'interface utilisateur et porte donc `@e2e`.

## Conséquences

- Le linter refuse un scénario sans étiquette de niveau, **avec une fixture rouge** qui le prouve.
  *(Sans fixture, la règle serait une intention : ce dépôt a déjà eu deux fois une porte de CI
  verte à vide, les 2026-07-30 et 2026-08-10.)*
- Contrat de sortie **1.0 → 1.1**, additif : `design.byLevel`. Un consommateur 1.0 l'ignore.
- **Les cahiers vivants sont migrés** — `.qaia/testbooks/`, `examples/`, les fixtures des skills.
- **Les artefacts de campagne ne sont pas migrés.** `eval/baselines/`, `eval/gold-set/`, les
  sorties de campagnes horodatées : ce sont des **preuves de ce qui a été produit à une date**.
  Les réécrire pour satisfaire une règle postérieure falsifierait la preuve. Ils restent hors du
  périmètre du contrôle, et cette exclusion est écrite ici plutôt que subie.
- `test-plan-and-closure` peut désormais énoncer un périmètre **par niveau**, ce qui était
  jusqu'ici indérivable.

## Alternatives considérées

**Laisser `automate` décider, et documenter l'heuristique.** Écartée : elle décide au moment où
il est trop tard pour que la décision serve à quoi que ce soit. Un cahier de test doit pouvoir
dire ce qu'il couvre **avant** qu'une ligne de code de test existe — sinon `test-plan-and-closure`
n'a rien à écrire et la porte d'ADR 0001 reste aveugle.

**Déduire le niveau du texte des pas, à la volée, partout où on en a besoin.** Écartée : c'est la
même heuristique, recopiée à N endroits. Ce dépôt a passé le 2026-08-09 à corriger cinq cas de
règle dupliquée, et la panne du 2026-08-10 venait d'un périmètre écrit deux fois.

**Trois niveaux ou plus, en ouvrant la liste.** Écartée par ADR 0004 pour le composant et
l'intégration. Pour les autres types de vérification déjà couverts par des skills dédiées
(accessibilité, performance, sécurité, visuel), le type est porté par la skill qui les produit et
apparaît déjà dans `execution.byType` — ce sont des **types de test**, pas des niveaux, et les
confondre dans une seule liste rendrait les deux inutilisables.

## Ce qui ferait rouvrir cette décision

- Un niveau intermédiaire devient observable sans code source — par exemple un contrat de
  messagerie ou d'événement publié, vérifiable de l'extérieur comme une spécification HTTP. Le
  critère d'ADR 0004 l'admettrait ; la liste fermée à deux valeurs devrait s'ouvrir à trois.
- Des utilisateurs réels demandent un découpage plus fin **après** avoir utilisé celui-ci. La
  demande compte quand elle vient de quelqu'un qui s'en sert.
