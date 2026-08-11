# PocketBase — campagne de recherche de défauts (2026-08-11)

## Cible

| | |
|---|---|
| Produit | PocketBase (github.com/pocketbase/pocketbase, ~60k étoiles) |
| Version testée | **`pocketbase.exe version 0.39.10`** — `pocketbase_0.39.10_windows_amd64.zip`, release du 2026-07-30 |
| Instance | **`http://127.0.0.1:8090`, auto-hébergée, mono-processus, données locales** |
| Date | 2026-08-11 |
| Oracle | `https://pocketbase.io/docs/api-rules-and-filters/` et `https://pocketbase.io/docs/api-records/` — **la prose uniquement** |

**Le code source de PocketBase n'a été lu à aucun moment pour dériver une condition de test.** Le
`CHANGELOG.md` livré dans l'archive n'a pas été consulté non plus. Toutes les attentes de ce rapport
sont dérivées de phrases de la documentation publique, citées dans la sonde à côté de chaque
vérification (champ `promise`).

Aucune instance publique, aucun service tiers n'a été sollicité. Les seuls appels réseau sortants
ont servi à (a) télécharger la release depuis GitHub, (b) lire la documentation, (c) chercher
l'antériorité dans le tracker amont.

**Stabilité de l'instance** : mono-processus, aucun écrivain concurrent, aucune mutation de données
après le `setup.js`. Chaque requête de la sonde est exécutée **deux fois** et son résultat n'est
retenu que si les deux exécutions sont identiques octet pour octet (colonne `2 identical runs`).
Le seul cas instable observé est `sort=@random`, ce qui est le comportement documenté et n'est donc
pas un constat.

## Fichiers

| Fichier | Rôle |
|---|---|
| `setup.js` | construit le schéma et les 7 enregistrements de fixture |
| `probe.js` → `evidence.txt` | passe 1 — 64 vérifications, filtres / pagination / tri / expand / fields / codes d'erreur |
| `probe2.js` → `evidence2.txt` | passe 2 — casse, modificateurs, profondeur d'`expand`, règles d'API, codes de statut |
| `probe3.js` → `evidence3.txt` | passe 3 — matrice des 8 opérateurs « any/at-least-one-of » sur tableau vide |
| `probe4.js` → `evidence4.txt` | passe 4 — opérateurs d'ordre sur multi-select |
| `probe5.js` → `evidence5.txt` | passe 5 — contrôle : la fixture est-elle réellement multi-valuée |
| `repro.js` → `repro-output.txt` | **reproduction minimale autonome** du seul constat retenu |

Rejouer : `./pocketbase.exe serve --http=127.0.0.1:8090` puis `node setup.js && node probe.js`.

---

## Ce qui a été éprouvé

Environ **60 affirmations distinctes de la documentation** — dénombrement qui m'est propre, chaque
vérification portant sa citation dans le champ `promise` de la sonde — ont été converties en
conditions et exécutées : les 16 opérateurs de filtre, la règle d'auto-encadrement par `%` de `~`,
la contrainte match-all par défaut et le préfixe `?`, les 5 modificateurs (`:isset`, `:changed`,
`:length`, `:each`, `:lower`), `geoDistance`, `strftime`, 6 macros datetime, le groupement et les
commentaires, les 4 combinaisons de codes de statut de règles d'API, la normalisation des en-têtes,
`@request.query.*`, `@collection.*` réservé aux superusers, les défauts `page`/`perPage`, `sort`
(`-`/`+`/`@rowid`/`@random`), `expand` et sa profondeur annoncée, `fields` avec `*` et `:excerpt`,
et `skipTotal`.

**Résultat brut de la passe 1, ligne SUMMARY de `evidence.txt` (rejeu depuis une base vierge) :
`{"MATCH":42,"DEVIATION":1,"OBSERVED-ONLY":20,"UNSTABLE":1}`** — soit 64 vérifications, une seule
DEVIATION (`F11`, voir U-01) et un seul cas instable (`sort=@random`, instabilité documentée).

L'ensemble de la chaîne (`setup.js` → 5 sondes → `repro.js`) a été **rejoué depuis un `pb_data`
supprimé**, avec de nouveaux identifiants d'enregistrements : résultats identiques.

Après instruction des candidats, **un seul constat est retenu comme confirmé et reproductible.**

---

## 1. CONFIRMÉ ET REPRODUCTIBLE

### D-01 — `!=` / `?!=` est le seul opérateur qui fait correspondre un enregistrement dont la relation multiple est vide

**Ce qui est promis.** La documentation donne aux huit opérateurs préfixés `?` une glose unique et
uniforme :

> `?=` Any/At least one of Equal — `?!=` Any/At least one of NOT equal — `?>` … `?~` Any/At least one
> of Like/Contains — `?!~` Any/At least one of NOT Like/Contains

et pour leurs contreparties non préfixées :

> Field expressions with array-like value or nested fields that originate from a source with multiple
> records will apply a **match-all** constraint by default.

Un quantificateur uniforme doit se comporter uniformément sur un ensemble vide : que la convention
retenue soit « vide ⇒ faux » (lecture stricte de *at least one of*) ou « vide ⇒ vrai » (vérité
vacuelle du *match-all*), elle doit être la même pour les douze opérateurs.

**Ce qui est observé.** Elle ne l'est pas. Sur douze opérateurs testés contre le même champ, un seul
retourne l'enregistrement à relation vide — et c'est celui dont l'analogue direct (`!~` / `?!~`) ne
le retourne pas.

`node repro.js` (fixture autonome : 3 enregistrements, `A→[news]`, `B→[tech]`, `C→[]`) :

```
filter                | matched                         | C (relation vide) ?
----------------------|---------------------------------|--------------------
cats.name ?=  "news"  | ["A_has_news"]                  | non
cats.name ?!= "news"  | ["B_has_tech","C_has_NOTHING"]  | OUI   <---
cats.name ?~  "news"  | ["A_has_news"]                  | non
cats.name ?!~ "news"  | ["B_has_tech"]                  | non
cats.name ?>  "news"  | ["B_has_tech"]                  | non
cats.name ?>= "news"  | ["A_has_news","B_has_tech"]     | non
cats.name ?<  "news"  | []                              | non
cats.name ?<= "news"  | ["A_has_news"]                  | non
cats.name =   "news"  | ["A_has_news"]                  | non
cats.name !=  "news"  | ["B_has_tech","C_has_NOTHING"]  | OUI   <---
cats.name ~   "news"  | ["A_has_news"]                  | non
cats.name !~  "news"  | ["B_has_tech"]                  | non
```

**L'incohérence est interne, pas seulement documentaire.** `?=` et `?!=` sont tous deux faux pour un
enregistrement sans élément lié — ce serait cohérent. `?=` faux et `?!=` vrai ne l'est pas. Et la
paire `!~` / `?!~`, décrite par la documentation avec exactement les mêmes règles, tranche dans
l'autre sens.

Le modèle que le mainteneur énonce lui-même ailleurs ne prédit pas non plus l'écart : il explique
en [#7193](https://github.com/pocketbase/pocketbase/issues/7193) qu'une relation vide prend « the
zero-default value of the field type ». Si la valeur jointe était `''`, alors `'' != 'news'` **et**
`'' NOT LIKE '%news%'` seraient tous deux vrais en SQL — les deux opérateurs devraient donc inclure
`C`. Un seul le fait. Les deux familles ne passent visiblement pas par le même chemin.

**Reproduction.**

```bash
# instance locale, PocketBase 0.39.10
./pocketbase.exe superuser upsert probe@example.com Probe12345678
./pocketbase.exe serve --http=127.0.0.1:8090
node repro.js
```

Une ligne suffit une fois la fixture en place :

```bash
curl -s '127.0.0.1:8090/api/collections/repro_posts/records?filter=cats.name%20%3F!%3D%20%22news%22'
curl -s '127.0.0.1:8090/api/collections/repro_posts/records?filter=cats.name%20%3F!~%20%22news%22'
```

**Reproductions** : 2 exécutions identiques dans `probe.js` (M03), 2 dans `probe2.js` (C2/C4),
5 consécutives dans `probe3.js` section E, plus la fixture indépendante de `repro.js` — soit
4 fixtures distinctes, résultat identique à chaque fois.

**Conséquence pratique.** Une règle d'API de la forme `cats.name != "secret"` — écrite pour exclure
une catégorie — laisse passer tous les enregistrements sans aucune catégorie. La même règle écrite
`cats.name !~ "secret"` les exclut. Deux formulations que la documentation présente comme
analogues n'ont pas le même périmètre d'exposition. Je décris la conséquence, je ne revendique
pas une sévérité : personne n'a démontré ici qu'une application réelle en dépend.

**Antériorité cherchée, non trouvée** : recherche `search/issues` sur `repo:pocketbase/pocketbase`
pour `"?!="`, *filter negation multi relation*, *not equal filter empty relation matches*, et
recherche GraphQL sur les Discussions pour *filter not equal relation empty*, *'?!=' operator*,
*filter excludes records empty relation*. Les plus proches — issue
[#7193](https://github.com/pocketbase/pocketbase/issues/7193), discussions
[#2444](https://github.com/pocketbase/pocketbase/discussions/2444) et
[#7474](https://github.com/pocketbase/pocketbase/discussions/7474) — traitent de la valeur zéro
d'une relation vide et de la sémantique match-all, mais aucune ne relève l'asymétrie entre `!=` et
`!~`. **Cette recherche n'est pas exhaustive** : la recherche GitHub est plein-texte et j'ai pu
manquer une formulation différente.

---

## 2. COMPORTEMENT DOCUMENTÉ AILLEURS — écarté

### N-01 — `?=` sur un champ multi-valué désigné sans sous-chemin ne renvoie rien

`opts ?= "a"` renvoie 0 enregistrement alors que trois enregistrements ont `"a"` dans `opts`
(`select`, `maxSelect=5`). Idem `tags ?= "<id>"` sur une relation multiple. Seuls `opts:each = "a"`,
`opts ~ "a"` et `tags.id ?= "<id>"` fonctionnent (`evidence5.txt`).

**Écarté** : répondu en amont dans [#6647](https://github.com/pocketbase/pocketbase/issues/6647)
(fermé le 2025-03-27, *not how it is supposed to work*) — « when you are applying a condition against
the plain field (aka. no modifier) you are applying a constraint against the db stored value, aka.
the serialized json array », et il faut `:each` pour viser les éléments. La documentation ne dit
pas cela — tous ses exemples `?` passent par un sous-chemin (`multiRelation.title ?= "test"`) — donc
il s'agit d'un manque de la documentation, pas d'un défaut du produit, et il est connu depuis
16 mois. Non retenu.

### N-02 — codes de statut des règles d'API : conformes

`probe2.js` section G. Règle non satisfaite → `list=200` avec 0 élément, `create=400`,
`view=404`, `update=404`, `delete=404`. Règle « verrouillée » (`null`) → `403` sur les cinq actions.
**Exactement ce que la documentation annonce.** Aucun écart.

### N-03 — profondeur d'`expand` : conforme

> Supports up to 6-levels depth nested relations expansion.

Chaîne de 8 collections construite pour l'occasion : 6 niveaux demandés → 6 niveaux rendus ;
7 niveaux demandés → 6 rendus, statut 200, l'excédent est silencieusement tronqué (`probe2.js`,
D1/D5/D6/D7/D8). « Up to 6 » est tenu au sens strict, sans erreur d'arrondi. Le silence sur le
traitement de l'excédent est un manque de documentation, pas un écart.

### N-04 — normalisation des en-têtes et `@request.query.*` : conformes

`X-Token`, `x-token`, `X-TOKEN` traités identiquement ; valeur incorrecte → 200 avec 0 élément,
comme promis pour une `listRule` non satisfaite. `@request.query.mytoken` fonctionne, et son absence
donne 0 élément (`probe2.js` section F).

---

## 3. NON ÉTABLI — écarts observés, insuffisants pour un signalement

### U-01 — `~` est insensible à la casse, alors que l'exemple de la doc promet un préfixe littéral

La documentation donne comme exemple :

> Allow access by anyone and return only the records where the title field value **starts with
> "Lorem"** (ex. "Lorem ipsum") : `title ~ "Lorem%"`

Observé (`probe2.js` A1) : `title ~ "Lorem%"` renvoie **`["Lorem ipsum", "lorem lower"]`**. `=` est
lui sensible à la casse (A2 : `title = "lorem ipsum"` → 0). Corollaire : l'exemple documenté du
modificateur `:lower`, `title:lower ~ "test"`, est un no-op — `~` fait déjà la comparaison
insensible à la casse (A4/A5).

**Non retenu** : c'est le comportement natif de `LIKE` en SQLite pour l'ASCII, la documentation ne
qualifie jamais la casse pour `~`, et l'exemple de la doc reste vrai pour l'enregistrement qu'il
cite. C'est une imprécision de documentation de faible portée, pas un défaut de comportement.
Signalable au mieux comme suggestion documentaire.

### U-02 — `:isset` et `:changed` sur un champ de schéma : acceptés silencieusement, résultat vide

La doc dit `:isset` « available only for the `@request.*` fields » et `:changed` « available only for
the `@request.body.*` fields ». Appliqués à un champ de schéma dans un filtre de liste, les deux
renvoient **200 avec 0 élément**, dans les deux sens (`title:isset = true` → 0, `title:isset = false`
→ 0) — `probe2.js` B1/B2/B4. Or un champ inconnu (`nosuchfield = "x"`) et un modificateur inventé
(`title:nosuchmodifier`) donnent bien 400 (B3/B5).

**Non retenu** : la documentation dit que le modificateur n'est pas disponible, elle ne promet pas
d'erreur. Le résultat est fail-closed. Constat réel mais sans promesse violée.

### U-03 — `expand` d'une relation inexistante ou d'un champ non-relation : ignoré silencieusement

`expand=nosuchrel` et `expand=title` → 200, clé `expand` absente (`probe2.js` E1/E3), alors qu'un
`sort` inconnu donne 400 (E2). Asymétrie réelle, mais la documentation ne promet rien sur
l'`expand` invalide. **Non retenu.**

### U-04 — `perPage=0`, `perPage=-1`, `page=0` : repli silencieux sur la valeur par défaut

`perPage=0` et `perPage=-1` → `perPage: 30`, 7 éléments ; `page=0` → `page: 1` (`evidence.txt`
P09/P10/P11). Documentation muette sur les valeurs hors domaine. **Non retenu.**

### U-05 — `:excerpt(4,true)` renvoie `"Lore..."` (4 caractères **plus** l'ellipse)

`:excerpt(4)` → `"Lore"`, `:excerpt(4,true)` → `"Lore..."` (`evidence.txt` C02/C03). La doc dit
seulement `:excerpt(maxLength, withEllipsis?)` sans préciser si l'ellipse est comptée dans
`maxLength`. Comportement cohérent entre les deux formes. **Non retenu**, documentation muette.

---

## 4. NON TESTÉ — l'absence de constat ici est une absence de test

Le silence de ce rapport sur ces catégories ne vaut pas absence de défaut :

- **API Files** — upload, `thumb`, tokens de fichier protégé, `@request.context = "protectedFile"`.
- **Authentification** — OAuth2, OTP, MFA, vérification d'e-mail, `manageRule`, impersonation,
  `@request.auth.*`, `@request.context` (aucune des 6 valeurs de contexte n'a été éprouvée).
- **Réaltime** (SSE), **API batch**, **backups**, **cron**, **logs**.
- **Back-relations** (`collection_via_field`) — le point le plus regrettable de cette liste : c'est
  le voisin syntaxique direct du constat D-01 et il n'a pas été sondé.
- **Collections `view`**, champs `geoPoint` réels (`geoDistance` n'a été testé qu'avec des nombres
  et des identifiants numériques), champs `file` multiples avec `:each` / `:length`.
- **Concurrence** — aucun test d'écriture concurrente ; l'instance est restée mono-client.
- **Admin UI**, SDK JS/Dart, extensions Go/JS.
- **`strftime`** n'a été testé qu'avec 1 et 2 arguments ; les modificateurs (3e argument et au-delà,
  « up to 8 max ») n'ont pas été éprouvés.
- **Injection / échappement** — un `%` et un `_` littéraux et un antislash ont été passés dans des
  opérandes, sans écart (F13/F14/F15) ; aucune campagne d'échappement systématique n'a été menée.

---

## 5. Estimation honnête

**Un seul constat mérite d'être remonté : D-01.** Il est reproductible sur quatre fixtures, minimal
(3 enregistrements, 2 requêtes), dérivé d'une phrase de la documentation et non du code, sans
antériorité trouvée, et il tient debout même sous le modèle sémantique que le mainteneur défend
lui-même dans le tracker. Il a la forme d'un signalement amont recevable — probablement comme
*bug report* sur l'asymétrie, avec la question ouverte : quelle convention est voulue pour
l'ensemble vide ?

Je tempère : le mainteneur de PocketBase répond vite et ferme, et il peut parfaitement répondre que
`!=` est intentionnellement le complément booléen de `=` sur la valeur jointe et que `!~` est
l'anomalie inverse. Dans ce cas le constat se transforme en demande de clarification documentaire.
C'est un risque assumé, pas une raison de ne pas remonter : la question « laquelle des deux est la
bonne ? » n'a de réponse que chez lui.

**Les onze autres écarts sont du bruit** et je ne les remonterais pas : cinq sont des silences de la
documentation sur des cas hors domaine, un est explicitement répondu en amont depuis 16 mois, et les
autres sont des imprécisions de rédaction sans conséquence sur le comportement.

Sur ce qui a le mieux tenu : **PocketBase 0.39.10 est remarquablement conforme à sa propre
documentation sur les points chiffrés et testables** — les cinq codes de statut de règles d'API sont
exacts, la profondeur d'`expand` annoncée est exactement 6, `skipTotal` renvoie bien `-1`/`-1` et
respecte `false`/`0`, les défauts de pagination sont ceux annoncés, la normalisation des en-têtes
est exacte, `strftime` et les macros datetime se comportent comme décrit, et la contrainte match-all
par défaut sur les relations multiples est correcte. C'est le contexte dans lequel il faut lire
D-01 : un angle mort dans un ensemble par ailleurs solide.
