# Trois campagnes sur du logiciel réel — deux constats publiables, après seize qui ne l'étaient pas

**2026-08-11.** Après deux échecs de la journée sur des bibliothèques de fonctions pures (zéro
défaut, seize constats bruts effondrés à la vérification), changement de classe de cible :
**applications avec état, auto-hébergées, dont la documentation promet un comportement précis.**
C'est la forme exacte de la campagne json-server — la seule qui ait jamais produit un effet
externe dans ce projet.

**Ça a marché.** Deux constats confirmés, reproduits indépendamment, sans antériorité.

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

---

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
| Publiables après vérification | **2** |
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
| Application avec état, promesse en prose | **2 défauts**, deux campagnes sur trois |

Une fonction pure dans une bibliothèque à 23 000 étoiles n'a ni état, ni concurrence, ni
intégration, ni configuration — et sa spécification est une norme ISO, donc il n'y a rien à
interpréter et rien qui dérive. **C'est le pire terrain possible, et je l'avais choisi parce
qu'il était facile à lancer.**

## Les fichiers

| | |
|---|---|
| [`pocketbase-2026-08-11/`](pocketbase-2026-08-11/) | ~60 affirmations éprouvées, 64 vérifications, `repro.js` autonome |
| [`meilisearch-2026-08-11/`](meilisearch-2026-08-11/) | 45 vérifications sur seuils chiffrés, filtres, pagination |
| [`oracle-vs-validatorjs-2026-08-11/`](oracle-vs-validatorjs-2026-08-11/) | Les deux campagnes à zéro défaut, et l'analyse de pourquoi |

**Rien n'a été publié en amont.** Les deux constats attendent une décision explicite du fondateur,
sous son identité GitHub.
