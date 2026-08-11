# Trois campagnes sur du logiciel réel — quatre constats publiables, après seize qui ne l'étaient pas

**2026-08-11.** Après deux échecs de la journée sur des bibliothèques de fonctions pures (zéro
défaut, seize constats bruts effondrés à la vérification), changement de classe de cible :
**applications avec état, auto-hébergées, dont la documentation promet un comportement précis.**
C'est la forme exacte de la campagne json-server — la seule qui ait jamais produit un effet
externe dans ce projet.

**Ça a marché.** Quatre constats confirmés, reproduits indépendamment, sans antériorité — sur les
trois cibles.

## Publié en amont le 2026-08-11

| Constat | Signalement |
|---|---|
| Uptime Kuma — `responseMaxLength = 0` détruit la réponse | [louislam/uptime-kuma#7703](https://github.com/louislam/uptime-kuma/issues/7703) |
| Uptime Kuma — maintenance récurrente qui saute sa première occurrence | [louislam/uptime-kuma#7704](https://github.com/louislam/uptime-kuma/issues/7704) |
| PocketBase — `?!=` et `?!~` se contredisent sur une relation vide | [pocketbase/pocketbase#7801](https://github.com/pocketbase/pocketbase/issues/7801) |
| restful-booker — 500 sur corps malformé | [mwinteringham/restful-booker#58](https://github.com/mwinteringham/restful-booker/issues/58) |
| Meilisearch — `totalHits` ignore `maxTotalHits`, se reproduit en v1.53.0 | [commentaire sur #6482](https://github.com/meilisearch/meilisearch/issues/6482#issuecomment-5253843510) |

**Quatre issues et un commentaire**, publiés sous l'identité du fondateur, chacun avec sa
reproduction minimale et l'antériorité citée. Corps relus depuis l'API après publication.

**Non publié, et c'est délibéré** : l'incohérence Meilisearch `minimum: 0` documenté / `0` refusé.
Vérifiée et sans antériorité, mais elle relève du dépôt de documentation et son impact se limite
aux schémas générés. Le brouillon reste disponible ; ouvrir cinq issues le même jour depuis le
même compte est le meilleur moyen de n'être lu par personne.

---

## Ce qui est publiable

### PocketBase — `?!=` et `?!~` se contredisent sur une relation vide

**Version** : 0.39.10 (release du 2026-07-30), auto-hébergée, mono-processus.

La documentation donne aux huit opérateurs `?` **une glose uniforme** :

> `?!=` — *Any/At least one of NOT equal*
> `?!~` — *Any/At least one of NOT Like/Contains*

Sur trois enregistrements, dont un dont la relation multiple est **vide** :

```
cats.name ?=  "news"  ->  ['A_has_news']
cats.name ?!= "news"  ->  ['B_has_tech', 'C_has_NOTHING']   <- l'enregistrement VIDE sort
cats.name ?~  "news"  ->  ['A_has_news']
cats.name ?!~ "news"  ->  ['B_has_tech']                    <- l'enregistrement vide ne sort pas
```

**La force du constat n'est pas qu'un opérateur soit « faux » — c'est que les deux se
contredisent.** Sous la glose « au moins un », un enregistrement sans aucun élément ne peut
satisfaire aucun des deux. Sous la lecture inverse (`!=` complément booléen de `=`), les deux
devraient l'inclure. **Aucune lecture ne rend les deux réponses cohérentes**, donc l'une des deux
est non voulue — et seule l'équipe peut dire laquelle.

**Reproduit indépendamment** : instance relancée sur un autre port, mêmes quatre résultats.
**Antériorité** : cherchée dans les issues et les Discussions, non trouvée. #6647, #7193, #2444,
#7474 sont voisines et ne relèvent pas l'asymétrie.

**Risque assumé** : le mainteneur peut répondre que `!=` est intentionnellement le complément
booléen et que `!~` est l'anomalie inverse. Le constat devient alors une demande de clarification
documentaire — ce qui reste utile, puisque la doc ne permet pas aujourd'hui de le savoir.

### Meilisearch — `minimum: 0` documenté, `0` refusé

**Version** : v1.53.0 (release du 2026-08-10), auto-hébergée.

La référence d'API déclare `minimum: 0` pour **deux** réglages. Le serveur en accepte un et
refuse l'autre :

```
PATCH /indexes/v/settings/pagination  {"maxTotalHits": 0}
  -> HTTP 400  « a non-zero integer value ... was expected, but found a zero »

PATCH /indexes/v/settings/faceting    {"maxValuesPerFacet": 0}
  -> HTTP 202  accepté
```

Même contrat documenté, deux comportements, dans la même page de référence. Impact faible —
schémas et clients générés — mais le constat est net et **vérifié indépendamment**.
**Antériorité** : non trouvée.

### Uptime Kuma — deux constats, et c'est la campagne la plus productive

**Version** : 2.5.0, commit `d9a60df`, publiée le 2026-08-01. Installée, construite et exécutée
**deux fois indépendamment** — une fois par la campagne, une fois par moi sur un clone neuf.

**D-1 — `responseMaxLength = 0` détruit la réponse au lieu de ne pas la tronquer.**

Le produit affiche à l'utilisateur, dans sa propre chaîne de traduction :

> *« Maximum size of response data to store. **Set to 0 for unlimited.** Larger responses will
> be truncated. Default: 1024 (1KB) »*

Le champ du formulaire est un `type="number"` que rien n'empêche de mettre à 0. Résultat mesuré
sur mon clone, corps de 10 caractères **et** de 5 000 :

```
responseMaxLength=0,    corps 10 chars   -> stocké : "... (truncated)"   0 caractère conservé
responseMaxLength=0,    corps 5000 chars -> stocké : "... (truncated)"   0 caractère conservé
responseMaxLength=1024, corps 10 chars   -> stocké : "xxxxxxxxxx"        témoin correct
```

**« Illimité » signifie « rien ».** Antériorité : les seuls résultats sont les PR qui ont *ajouté*
la fonctionnalité (#6684, #6192, #6691) — aucun rapport de ce défaut.

**D-2 — une maintenance récurrente saute sa première occurrence si la plage de validité commence
le jour même.**

Mécanisme **isolé hors du produit**, en trois lignes, sur `croner` 8.1.2 tel que livré :

```js
new Cron('55 14 * * *', {startAt: 2026-08-11T14:55}).nextRun(depuis 14:54)  ->  2026-08-12
new Cron('55 14 * * *', {startAt: 2026-08-10T14:55}).nextRun(depuis 14:54)  ->  2026-08-11
```

`startAt` est une borne **stricte**. Or le produit construit `startAt` à la date de début de
validité + l'heure de la fenêtre : il tombe donc exactement sur la première occurrence, qui est
sautée. **Et le formulaire initialise la plage de validité à « maintenant »** — c'est le chemin
par défaut.

Aucune erreur n'est levée, le statut affiché reste « Scheduled » : l'utilisateur croit sa fenêtre
en place, et **les notifications ne sont pas suspendues pendant l'intervention**.

*Précision sur ce que j'ai vérifié moi-même* : le **mécanisme**, ci-dessus. Le comportement de
bout en bout vient de la campagne, qui l'a établi par un A/B côte à côte avec journal serveur
horodaté. Antériorité : zéro résultat sur le symptôme, chez elle comme chez moi.

---

## L'étape du protocole qui manquait, et que deux dépôts ont fait payer

**Avant de publier quoi que ce soit chez un tiers, lire sa politique de contribution et ses
gabarits d'issue.** Cette étape n'existait pas ; elle existe maintenant, parce que son absence a
coûté trois publications sur quatre.

| Ce qui a été vérifié six fois | Ce qui ne l'a jamais été |
|---|---|
| l'antériorité du constat dans le tracker | `CONTRIBUTING.md` de la cible |
| la reproductibilité, deux fois minimum | `.github/ISSUE_TEMPLATE/` et ses champs obligatoires |
| la sévérité bornée par la preuve | la politique du projet sur les contributions automatisées |

- **`louislam/uptime-kuma`** impose `bug_report.yml` — quatre champs obligatoires, une case de
  politique de sécurité — et un bot ferme toute issue qui ne passe pas par là. #7703 et #7704 ont
  été fermées, étiquetées `invalid-format`. Corps réécrits au format depuis ; **le dépôt ne laisse
  pas l'auteur rouvrir** ce que son bot a fermé.
- **`pocketbase/pocketbase`** n'a pas de gabarit, mais son `CONTRIBUTING.md` porte un encadré :
  *« Due to recent LLM spam… LLM contributions are not welcome »*. #7801 a été **supprimée**, et
  c'était leur droit. Le constat technique tient ; il n'a rien à faire chez eux sous cette forme.

**La divulgation n'était pas l'erreur.** Chaque corps publié se terminait par une note disant d'où
venait le constat — c'est ce qui a rendu la provenance visible, et c'est délibéré : la cacher aurait
été pire, et c'est exactement ce que ce mainteneur combat (*« if not obvious »*). L'erreur est
d'avoir publié sans lire ce que la cible demande.

**On vérifie ce qu'on sait devoir vérifier, pas ce que la cible impose.** C'est la même classe que
les trois périmètres faux du matin.

## Ce qui n'est pas publiable, et pourquoi c'est écrit ici

**Meilisearch — `totalHits`/`totalPages` ignorent `maxTotalHits`.** Réel, reproductible, et
**déjà rapporté** : issue #6482, ouverte le 2026-06-30, étiquetée `bug`, avec une reproduction
identique à la nôtre — et PR #6496 ouverte, non fusionnée, dernière activité le 2026-08-06. La
seule chose que nous ajoutons est *« se reproduit encore en v1.53.0 »*, ce qui vaut un
commentaire d'une ligne et pas une issue.

**PocketBase — onze autres écarts**, tous classés bruit par la campagne elle-même : `~`
insensible à la casse, `:isset` silencieux sur un champ de schéma, `expand` invalide ignoré,
`perPage=0` en repli silencieux, `:excerpt` qui compte l'ellipse en plus. Dans les cinq cas la
documentation est **muette** — ce sont des écarts par rapport à une attente, pas par rapport à une
promesse. Un douzième (`?=` sur un champ JSON sans modificateur) est **répondu en amont depuis
seize mois** (#6647, fermé : *« not how it is supposed to work »*).

---

## Le chiffre de la journée, et ce qu'il dit

| | |
|---|---|
| Constats bruts sur du logiciel tiers | **~30** |
| Publiables après vérification | **4** |
| Effondrés : notre propre corpus faux | 12 |
| Effondrés : comportement documenté | 8 |
| Effondrés : déjà rapportés en amont | 3 |
| Effondrés : erreur d'API de l'opérateur | 1 lot de 34 |
| Effondrés : instance instable, constat invalide par construction | 3 |

**Le rendement est de l'ordre de 1 sur 15.** Ce n'est pas une anomalie, c'est le régime — et
c'est exactement la proportion que la passe de réfutation de ce dépôt existe pour produire
(*91 constats faux contre 2 confirmés*, mesuré le 2026-08-09).

**Ce qui a changé entre les échecs et les réussites n'est pas la méthode, c'est la cible.**

| Terrain | Résultat |
|---|---|
| Fonction pure implémentant une norme publiée | **0 défaut**, deux campagnes |
| Application avec état, promesse en prose | **4 défauts**, sur les **trois** campagnes |

Une fonction pure dans une bibliothèque à 23 000 étoiles n'a ni état, ni concurrence, ni
intégration, ni configuration — et sa spécification est une norme ISO, donc il n'y a rien à
interpréter et rien qui dérive. **C'est le pire terrain possible, et je l'avais choisi parce
qu'il était facile à lancer.**

## Les fichiers

| | |
|---|---|
| [`pocketbase-2026-08-11/`](pocketbase-2026-08-11/) | ~60 affirmations éprouvées, 64 vérifications, `repro.js` autonome |
| [`meilisearch-2026-08-11/`](meilisearch-2026-08-11/) | 45 vérifications sur seuils chiffrés, filtres, pagination |
| [`uptime-kuma-2026-08-11/`](uptime-kuma-2026-08-11/) | 15 promesses éprouvées, 17 sondes rejouables, cible HTTP locale pilotable |
| [`oracle-vs-validatorjs-2026-08-11/`](oracle-vs-validatorjs-2026-08-11/) | Les deux campagnes à zéro défaut, et l'analyse de pourquoi |

**Publié le 2026-08-11** — voir le tableau en tête. Ce que ces cinq signalements deviennent
n'appartient plus au projet : un mainteneur peut fermer, requalifier, ou demander une
clarification. **Le résultat de cette campagne sera ce qu'ils en feront**, pas ce que nous en
avons écrit.
