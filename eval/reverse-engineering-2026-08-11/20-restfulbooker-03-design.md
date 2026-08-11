---
stepsCompleted: [00-source, 01-review, 02-understanding, 03-design]
lastStep: 03-design
lastSaved: 2026-08-11
status: unconfirmed
usId: RB
---

# US-RB — restful-booker · conception (openapi-ingest → us-review → need-understanding → istqb-design)

**Statut : `unconfirmed`.** Aucun humain n'a arbitré les points ⚠ VALIDATION de `us-review`
(étape 3), `need-understanding` (étape 6) et `istqb-design` (étape 4). Conformément à
`plugins/qaia-core/skills/README.md` règle 3, le défaut documenté est appliqué, la course
continue, et **aucune de ces trois étapes n'est marquée `done`** : elles restent
`pending-validation`, et les 16 questions ouvertes ci-dessous comptent comme `simulated` dans
`openArbitrations[]`.

---

## 0. Source figée (openapi-ingest, étape 1)

| | |
|---|---|
| Document | `https://restful-booker.herokuapp.com/apidoc/api_data.json` (+ `api_project.json`) |
| Générateur | apidoc 0.25.0, généré le **2025-06-11T20:24:26.733Z** |
| Version projet | `restful-booker` 1.0.0 |
| Source gelée | `sources/api_data.json` + `sources/api_project.json`, empreintes dans `sources/REQUIREMENT-SOURCE.json` (sha256 `1ae02a5f…` / `e061624f…`) |

**La documentation n'est pas de l'OpenAPI/Swagger** : c'est de l'apidoc. `openapi-ingest` ne le
prévoit pas, mais la structure est isomorphe (opération, `parameter`, `header`, `success`,
`error`) et la table de dérivation s'y applique terme à terme — sauf sur un point, dit ici
plutôt que passé sous silence : apidoc n'a **ni `enum`, ni `minimum`/`maximum`, ni `pattern`,
ni `required` explicite** (il a `optional: true|false`), et surtout **il n'a pas de bloc
`security`**. Trois des cinq lignes de la table de dérivation n'ont donc pas de source formelle
ici : ce qui en tiendrait lieu est écrit **en prose**, ce qui fait tomber ces clauses dans la
contradiction n° 4 par construction. C'est la conclusion principale de l'ingestion.

**Aucune requête n'a été émise pour produire ce document.** `openapi-ingest` l'interdit
explicitement (« Probing the live server. This skill reads a document. It never sends a
request »). Les comportements observés cités plus bas viennent de la ligne de base, et sont
étiquetés comme tels — jamais mélangés à ce que la documentation promet.

### Inventaire (étape 2)

| | |
|---|---|
| Chemins | 4 (`/auth`, `/booking`, `/booking/:id`, `/ping`) |
| Opérations | **8** — `CreateToken`, `GetBookings`, `GetBooking`, `CreateBooking`, `UpdateBooking`, `PartialUpdateBooking`, `DeleteBooking`, `Ping` |
| Schémas | 0 (apidoc n'a pas de composants ; les champs sont listés par opération) |
| Codes de réponse déclarés | **1 seul groupe : `Success 200`**, sur les 8 opérations |
| Codes d'erreur déclarés | **0 — aucune opération ne porte de bloc `error`** |
| `$ref` à résoudre | 0 (étape 3 sans objet) |

Ce tableau est déjà le résultat le plus lourd de l'ingestion : **une API dont trois opérations
exigent un justificatif d'authentification et dont zéro opération déclare un code d'échec.**

---

## 1. Ce que la ligne de base a écrit, revu (`us-review`)

`us-review` étape 1 restructure et étape 2 « montre la différence » — ce qui a été trouvé, et ce
qui **ne** l'a pas été. Les AC de la ligne de base sont conservés avec leur numéro (garde-fou :
« never renumber after validation ») ; les corrections sont marquées.

### US-RB-01 — Obtenir un jeton d'accès

| # | Critère (ligne de base) | Verdict après revue |
|---|---|---|
| AC1 | Identifiants valides → jeton exploitable | **Conservé.** Dérivable : `CreateToken · success.200.token`. « Exploitable » n'est pas dérivable (aucune clause ne dit où ni combien de temps le jeton vaut) → reformulé en « le corps porte un champ `token` ». |
| AC2 | Identifiants invalides → pas de jeton | **Conservé.** Dérivable par contraposée du `success`. |
| AC3 | Un échec est distinguable d'un succès **par le seul code de statut** | **Requalifié.** Ce n'est pas un critère dérivé du contrat : le contrat ne déclare **aucun** code d'échec. C'est la **contradiction n° 3** d'`openapi-ingest`. Devient **Q1**, et une condition `[open]`. La ligne de base a raison sur le fond et se trompe de statut d'énoncé : elle présente comme critère ce qui est une question ouverte. |

**Manquant dans la ligne de base, ajouté :** `username` et `password` sont déclarés
**obligatoires** (`optional: false`) — deux chemins de refus par omission que la ligne de base
n'a pas dérivés (ligne « `required` » de la table de dérivation).

### US-RB-02 — Créer une réservation

| # | Critère (ligne de base) | Verdict après revue |
|---|---|---|
| AC1 | Corps complet → identifiant | **Conservé.** `CreateBooking · success.200.bookingid`. |
| AC2 | Relisible à `GET /booking/{id}` avec les mêmes valeurs | **Conservé avec réserve.** Le schéma de réponse de `GetBooking` **ne contient pas `bookingid`** : « les mêmes valeurs » ne peut porter que sur les 7 champs métier. → **Q16**. |
| AC3 | Corps incomplet → **erreur client (4xx)** | **FAUX comme critère.** Le contrat ne déclare aucun 4xx. `api-steps.md` : *« Assert a status the specification never declares »* est interdit. La condition est conservée, l'assertion devient un **défaut proposé** (`400`) marqué `@low-confidence` + `# open: Q3`. |
| AC4 | Le refus nomme ce qui manque | **Supprimé.** Aucun bloc `error`, aucune forme de corps d'erreur n'est déclarée nulle part. C'est une invention pure : la documentation ne promet pas ça. |
| AC5 | Une création renvoie **201**, conformément à la sémantique HTTP | **Supprimé comme critère, inversé comme condition.** La documentation déclare `Success 200`. Le contrat étant explicite, il n'y a **aucune ambiguïté d'exigence** : `need-understanding` étape 5 interdit d'y consommer un slot de question (« Q-slots are for requirement ambiguity only »). Ce n'est ni un critère ni une question : c'est une **remarque de qualité du contrat**, consignée en §6. La condition testable est l'inverse : `RB02-AC5-C1` vérifie que le statut est **200**, tel que promis. |

**Manquant dans la ligne de base, ajouté :** `CreateBooking` **ne déclare aucun mécanisme
d'authentification** alors que `UpdateBooking`/`PartialUpdateBooking`/`DeleteBooking` en
déclarent un. La création anonyme est donc une promesse du contrat, jamais écrite par la ligne
de base ; elle alimente Q7.

### US-RB-03 — Protéger les opérations destructrices

| # | Critère (ligne de base) | Verdict après revue |
|---|---|---|
| AC1 | `PUT` sans jeton refusé | **Conservé**, mais le *code* du refus n'est pas dérivable → **Q2**. Le 403 de la ligne de base est un **fait observé**, pas une promesse. |
| AC2 | `DELETE` sans jeton refusé | Idem. |
| AC3 | Jeton invalide refusé comme aucun jeton | **Conservé** (non vérifié, et il n'a pas à l'être ici : c'est une condition de conception). |
| AC4 | Un refus d'autorisation ne modifie rien | **Conservé.** Bon critère, et le seul de la ligne de base qui touche l'effet de bord. |

**Manquant dans la ligne de base, ajouté — et c'est le trou le plus large :**

1. **`PATCH /booking/:id` (`PartialUpdateBooking`) n'existe pas dans la ligne de base.** Une
   opération mutante sur huit, protégée par les mêmes en-têtes, absente du périmètre.
2. **Le mécanisme `Authorization: Basic` n'existe pas dans la ligne de base.** La documentation
   déclare **deux** voies d'authentification (`Cookie: token=...` **ou** `Authorization: Basic`)
   et publie l'en-tête Basic encodé dans son propre exemple. La ligne de base ne parle que du
   jeton.
3. Les deux en-têtes d'authentification sont déclarés **`optional: true`** alors que la prose
   dit « Requires an authorization token » → **contradiction n° 1**, → **Q2**.

### Trois US absentes de la ligne de base

`us-review` étape 2 impose de dire ce qu'on **n'a pas** trouvé. Sur 8 opérations documentées, la
ligne de base en couvre 4 (`CreateToken`, `GetBookings` en passant, `CreateBooking`,
`GetBooking` en passant) et n'en formalise que 3. Sont ajoutées :

- **US-RB-04 — Lister et filtrer les réservations** (`GetBookings`, 4 paramètres de requête
  optionnels, dont deux dates avec un format et une sémantique `>=` énoncés **en prose**) ;
- **US-RB-05 — Lire une réservation** (`GetBooking`, 8 champs de réponse déclarés) ;
- **US-RB-06 — Contrôle de santé et surface protocolaire** (`Ping`).

---

## 2. Reformulation du besoin (`need-understanding`, étape 1)

`restful-booker` publie un contrat de réservation hôtelière à six opérations métier plus un
contrôle de santé. Un client anonyme peut **lire l'intégralité du jeu de données** (liste des
identifiants, puis chaque réservation avec le nom du client et le prix) et **créer** des
réservations ; seules la modification totale, la modification partielle et la suppression
exigent un justificatif, obtenu par `POST /auth` ou fourni en Basic. Le risque principal si le
service dévie : **le contrat ne décrit aucun chemin d'échec**, donc un client intégrateur n'a
aucune base documentaire pour distinguer un refus d'un succès — ni sur l'authentification, ni
sur la validation de charge utile, ni sur l'autorisation. Tout le comportement défensif de
l'API est, littéralement, hors contrat.

---

## 3. La passe des quatre contradictions (`openapi-ingest`, étape 5)

C'est le mécanisme qui a produit l'essentiel de ce que la ligne de base n'avait pas vu. Les
quatre classes sont **toutes présentes**.

### Contradiction 1 — un paramètre obligatoire qui porte un défaut

| Où | Constat |
|---|---|
| `CreateToken · parameter.username`, `parameter.password` | `optional: false` **et** `defaultValue` renseigné avec les identifiants d'administration publiés. Si le champ est requis, le défaut est inatteignable ; si le défaut s'applique, un `POST /auth` à corps vide s'authentifie. Le contrat ne tranche pas. → **Q6** |
| `CreateBooking · header.Content-Type`, `header.Accept` | Requis (`optional: false`) **et** porteurs d'un `defaultValue`. Même forme. Idem `UpdateBooking`, `PartialUpdateBooking`, `GetBooking`. |
| `DeleteBooking · header.Cookie`, `header.Authorization` | L'inverse et pire : déclarés **`optional: true`** avec un `defaultValue`, alors que la `description` de l'opération dit *« Requires an authorization token to be set in the header or a Basic auth header »*. → **Q2** |

La ligne de base n'a vu aucune des trois.

### Contradiction 2 — le même champ contraint ici et pas là

| Champ | Ici | Là |
|---|---|---|
| `id` (paramètre d'URL) | `GetBooking` le type **`String`** | `UpdateBooking`, `PartialUpdateBooking`, `DeleteBooking` le typent **`Number`** |
| `bookingdates.checkin` / `.checkout` | Corps de `CreateBooking`/`UpdateBooking` : type `Date`, **aucun format** | Requête de `GetBookings` : type `date` + *« Format must be CCYY-MM-DD »* en prose |
| `firstname` / `lastname` | Corps de `CreateBooking` : `String`, **obligatoire** | Requête de `GetBookings` : `String`, **optionnel**, sémantique de correspondance non déclarée |

→ **Q8** (type de `id`), **Q5** (format des dates), **Q12** (sémantique de filtrage).

### Contradiction 3 — de la sécurité déclarée, aucun code d'échec déclaré

**La forme la plus pure possible.** Trois opérations exigent un justificatif dans leur prose et
déclarent des en-têtes d'authentification. **Zéro opération, sur les huit, ne déclare le moindre
code d'erreur** : le champ `error` d'apidoc est absent des huit entrées. Il en découle trois
questions distinctes, une par famille de refus, parce qu'elles ne s'arbitrent pas ensemble :

- **Q1** — refus d'authentification (`POST /auth`) ;
- **Q2** — refus d'autorisation (`PUT`/`PATCH`/`DELETE`) ;
- **Q3** — refus de validation de charge utile (`POST`/`PUT /booking`) ;
- **Q10** — ressource inexistante (`GET /booking/:id`).

**Correction factuelle à la ligne de base.** Son tableau d'observation porte une colonne
« Documenté » qui est fausse dans trois cellules :

| Ligne de base | Réalité de la documentation |
|---|---|
| `GET /booking/999999` → 404, *« documenté »* | **Non.** Aucun 404 n'est déclaré nulle part. Le 404 est **observé**, jamais promis. |
| `PUT`/`DELETE` sans jeton → 403, *« jeton requis »* | La **exigence** est documentée ; le **403** ne l'est pas. Deux choses différentes rangées dans la même case. |
| `GET /ping` → 201, *« HealthCheck »* (présenté comme non documenté) | **Si, documenté** — voir contradiction n° 4. |

C'est exactement le piège que la skill nomme : *« une spécification est une promesse, pas un
fait »*. La ligne de base a mélangé les deux dans une seule colonne, dans les deux sens.

### Contradiction 4 — une contrainte en prose, absente du schéma

| Où | Prose | Schéma |
|---|---|---|
| `GetBookings · parameter.checkin/checkout` | *« Format must be CCYY-MM-DD »*, *« greater than or equal to »* | type `date`, rien d'autre |
| `CreateBooking · header.Content-Type` | *« Can be application/json or text/xml »* | type `string` |
| `CreateBooking · header.Accept` | *« Can be application/json or application/xml »* | type `string` |
| `DeleteBooking · description` | *« Requires an authorization token »* | en-têtes `optional: true` |
| `Ping · success` **et** `DeleteBooking · success` | groupe intitulé **`Success 200`**, description du champ : *« Default HTTP **201** response »*, exemple : *« HTTP/1.1 **201** Created »* | — |

Les deux dernières lignes méritent d'être lues deux fois.

- **Le bloc `Success 200` de `Ping` et de `DeleteBooking` se contredit lui-même**, à
  l'intérieur d'un seul bloc, sur trois lignes consécutives : l'intitulé dit 200, la description
  dit 201, l'exemple dit 201. → **Q4**. La ligne de base a traité le 201 de `/ping` comme une
  anomalie non documentée ; c'est en réalité une promesse documentée **et** auto-contradictoire.
  La différence compte : ce n'est pas un défaut du service, c'est un défaut du contrat.
- **L'énumération en prose des `Content-Type` est démentie par les exemples du document
  lui-même**, qui montrent un `curl` en `application/x-www-form-urlencoded` — valeur qui n'est
  dans aucune des deux énumérations. Et l'énumération d'entrée dit `text/xml` quand celle de
  sortie dit `application/xml`. → **Q11**.

---

## 4. Passes obligatoires de `need-understanding`

### Passe adversariale par type d'AC (étape 3)

| Type d'AC | Présent ? | Résultat |
|---|---|---|
| **Machine à états / cycle de vie** | Oui (réservation : créée → modifiée → supprimée) | Aucune transition interdite n'est déclarée. `PATCH` sur une réservation supprimée, `PUT` sur un id inexistant : non déclarés → **Q10** (même famille). Conditions dérivées `RB03-AC8-C2`, `RB05-AC2-C1`. |
| **Authentification / jetons / permissions** | Oui | Durée de vie du jeton : non déclarée. Révocation : non déclarée. Portée : non déclarée. Deux mécanismes concurrents (`Cookie`, `Basic`) sans règle de priorité si les deux sont envoyés. → **Q2**, et la règle dure de la skill (« an unstated access boundary is a question, never an assumption ») force **Q7**. |
| **Tri / pagination** | **Non applicable** : `GetBookings` ne déclare ni tri, ni pagination, ni ordre stable. Le silence est lui-même consigné (`coverage-expansion.md`, surface protocolaire : *« where the source is silent, that silence is itself the finding »*) → **Q14** pour les paramètres inconnus. |
| **Seuils / quantités** | Oui, en creux | `totalprice` est un `Number` **sans `minimum`** : 0 et les valeurs négatives sont dans le domaine déclaré. Aucune longueur maximale sur `firstname`/`lastname`/`additionalneeds`. → condition frontière `RB02-AC7-C1`, `[open] Q3`. |

### Passe d'interaction inter-AC (étape 4)

| Paire | Constat |
|---|---|
| US-RB-02·AC1 (créer, sans justificatif) × US-RB-03·AC1 (modifier, avec justificatif) | **Asymétrie non justifiée** : n'importe qui crée, seul un porteur de jeton modifie. Le contrat ne dit pas pourquoi. → **Q7** |
| US-RB-04·AC1 (lister tous les identifiants) × US-RB-05·AC1 (lire une réservation nominative) | Les deux sont anonymes. Enchaînées, elles exposent l'intégralité du jeu de données nominatif sans justificatif. → **Q7** |
| US-RB-02·AC2 (relecture) × US-RB-05·AC1 (schéma de lecture) | `POST` renvoie `{bookingid, booking:{…}}`, `GET` renvoie `{…}` **sans `bookingid`**. Un client ne peut pas corréler une lecture à son identifiant. → **Q16** |
| US-RB-03·AC7 (`PATCH` partiel) × US-RB-03·AC6 (`PUT` total) | `PUT` exige les 7 champs, `PATCH` n'en exige aucun. La frontière est nette et testable — c'est la seule paire du lot qui soit **cohérente**, et elle est consignée comme telle. |

### Passe de contradiction à trois AC (étape 4a)

**Elle produit quelque chose ici**, contrairement à ce qu'on pouvait craindre sur une API de
sept opérations. Les trois règles :

1. **règle d'état protégé** — `PUT`/`PATCH`/`DELETE` exigent un justificatif ;
2. **règle de portée** — le justificatif est obtenu avec un couple d'identifiants unique et
   publié dans la documentation, sans notion de propriétaire ;
3. **règle de non-divulgation** — inexistante : `GET /booking` et `GET /booking/:id` sont
   anonymes et exposent tout.

Prises deux à deux, elles sont consistantes. Prises à trois, elles disent que **le service n'a
aucune notion de propriété** : le « contrôle d'autorisation » de US-RB-03 est en fait un
contrôle d'**authentification**, et il protège l'écriture d'un jeu de données que n'importe qui
lit intégralement. Aucun AC ne peut donc être écrit sur l'isolement entre clients (IDOR) — non
parce qu'il est respecté, mais parce que le contrat ne le promet nulle part. C'est une
**limite de couverture déclarée**, pas un trou. → consigné en Q7.

### Questions ouvertes

`need-understanding` borne l'interrogation à **~10 questions par passe** (garde-fou : *« Bound
the interrogation: maximum ~10 questions per pass »*). Ce document en pose donc **10** et en
**offre 6 de plus en seconde passe** — la borne n'est pas gratuite : elle a repoussé six
questions réelles hors du premier tour.

| Q | Question | Origine | Défaut proposé | Statut |
|---|---|---|---|---|
| Q1 | `POST /auth` ne déclare aucun code d'échec. Que doit renvoyer une authentification refusée — statut et corps ? | contradiction 3 | `401` + corps d'erreur | `[open]` |
| Q2 | `PUT`/`PATCH`/`DELETE` : la prose exige un jeton, les en-têtes sont `optional: true`, et aucun code d'échec n'est déclaré. Quelle lecture fait foi, et quel statut pour un refus ? | contradictions 1 et 3 | en-tête obligatoire ; `403` | `[open]` |
| Q3 | `POST`/`PUT /booking` : 7 champs obligatoires, aucun code d'erreur déclaré. Quel statut pour un champ absent, mal typé ou hors format ? | contradiction 3 | `400` | `[open]` |
| Q4 | `Ping` et `DeleteBooking` : bloc intitulé `Success 200`, description et exemple disant `201 Created`. Laquelle des deux est la promesse ? | contradiction 4 | `201`, l'exemple étant le plus concret | `[open]` |
| Q5 | `bookingdates.*` est typé `Date` sans format dans le corps ; `CCYY-MM-DD` n'est écrit que dans la prose des paramètres de requête. Quel format le corps accepte-t-il ? | contradictions 2 et 4 | `CCYY-MM-DD` | `[open]` |
| Q6 | `username`/`password` sont obligatoires **et** portent en `defaultValue` les identifiants d'administration. Le défaut est-il atteignable ? | contradiction 1 | non : champ obligatoire, défaut décoratif | `[open]` |
| Q7 | Lecture intégrale anonyme (liste + fiches nominatives) et création anonyme, face à une écriture protégée par un unique justificatif partagé. Est-ce la frontière d'accès voulue ? | passes inter-AC et triple-AC | aucun — frontière d'accès non énoncée, jamais supposée | `[open]` |
| Q8 | `id` est typé `String` par `GetBooking` et `Number` par les trois autres opérations. Quel type fait foi, et que renvoie un id non numérique ? | contradiction 2 | `Number` ; `404` | `[open]` |
| Q9 | `PATCH` avec un corps `{}` est **valide au contrat** (tous les champs sont optionnels). La réservation reste-t-elle inchangée, ou des champs sont-ils réinitialisés ? | cycle de vie CRUD | inchangée | `[open]` |
| Q10 | `GET /booking/:id` ne déclare aucun 404. Que renvoie un identifiant inexistant ? | contradiction 3 | `404` | `[open]` |
| — | *seconde passe, offerte* | | | |
| Q11 | Ensemble réel des `Content-Type`/`Accept` acceptés : la prose dit deux valeurs, l'exemple du document en utilise une troisième, et l'entrée dit `text/xml` quand la sortie dit `application/xml`. | contradiction 4 | json, xml, urlencoded | `[open]` |
| Q12 | `GetBookings` : le filtrage par nom est-il sensible à la casse, exact ou partiel ? Le `>=` des dates est-il inclusif ? | contradiction 2 | insensible à la casse, exact, `>=` inclusif | `[open]` |
| Q13 | Une réservation dont le `checkout` précède le `checkin` est-elle valide ? Rien ne l'interdit. | seuils | acceptée, aucune validation n'étant déclarée | `[open]` |
| Q14 | Un paramètre de requête inconnu sur `GET /booking` est-il ignoré ou rejeté ? | surface protocolaire | ignoré | `[open]` |
| Q15 | Méthode invalide sur un chemin valide (`POST /ping`) : `404` ou `405` ? | surface protocolaire | `405` | `[open]` |
| Q16 | Le schéma de réponse de `GetBooking` ne contient pas `bookingid`. Est-ce voulu ? | interaction inter-AC | oui, l'id est dans l'URL | `[open]` |

**Aucune question de faisabilité n'occupe un slot.** `need-understanding` étape 5 l'interdit
(*« Q-slots are for requirement ambiguity only … never for test-feasibility or flakiness »*), et
il y en avait une évidente à écarter : *restful-booker* est un banc partagé et remis à zéro
périodiquement, donc la liste de `GET /booking` n'est pas stable et une réservation créée peut
disparaître entre deux pas. C'est un problème d'**automatisation** — chaque scénario doit créer
sa propre donnée — consigné ici et **pas** en question ouverte. La règle a bien mordu.

---

## 5. Conception ISTQB (`istqb-design`)

### 5.1 Niveau de test (étape 2b, ADR 0008)

**Les 42 conditions portent `[level: api]`.** Le motif est unique et vaut pour toutes : la cible
n'a aucune interface utilisateur, chaque promesse est une clause d'un contrat de service
observable en HTTP — statut, corps, en-tête, effet sur une ressource. `openapi-ingest` étape 6
le pose d'ailleurs comme inconditionnel (*« `[level: api]` on every derived condition »*), et
aucune condition ne remonte en `e2e` faute d'écran à observer.

Deux conséquences à dire franchement plutôt qu'à subir :

1. **`istqb-design` étape 2b demande une justification par condition d'une décision
   qu'`openapi-ingest` étape 6 a déjà prise pour toutes.** Écrire 42 fois la même phrase
   n'ajoute rien ; elle est écrite une fois, ici, et référencée. Voir §7.
2. **Aucun scénario `@smoke` n'est produit.** ADR 0008 (« Pourquoi exactement une étiquette »)
   dit que le scénario de parcours *« traverse par définition l'interface utilisateur et porte
   donc `@e2e` »*. Sur une cible sans interface, cette phrase **interdit tout scénario de
   parcours**, alors qu'un parcours CRUD multi-requêtes est un test scenario-based parfaitement
   légitime au niveau API. C'est une lacune de l'ADR, signalée en §7. La technique CRUD est donc
   portée par des scénarios atomiques (`@crud`), ce qui reste conforme à `api-steps.md`
   (interdiction d'enchaîner deux requêtes pour une assertion).

### 5.2 Table AC → technique

| AC | Technique(s) | Justification |
|---|---|---|
| RB01-AC1/AC2 | Partitionnement d'équivalence | Deux classes de justificatifs (valide / invalide) traitées identiquement, plus la classe « champ obligatoire absent » dérivée de `optional: false`. |
| RB01-AC3 | Partitionnement d'équivalence | Une seule condition, sur la classe « échec », dont la sortie attendue est ouverte (Q1). |
| RB02-AC1/AC2/AC5/AC6 | Partitionnement d'équivalence, CRUD | Classes valides de charge utile et de négociation de contenu ; la relecture après création est la paire *create/read* de CRUD (§3.2.1). |
| RB02-AC3 | Partitionnement d'équivalence (classes invalides) | Un chemin de refus par champ obligatoire omis, plus les classes de type et de format. Sept champs `optional: false` → sept partitions invalides, ligne « `required` » de la table de dérivation. |
| RB02-AC7 | Analyse des valeurs limites | `totalprice` est un `Number` sans borne déclarée : 0 et -1 encadrent la seule frontière naturelle d'un montant. |
| RB03-AC1/AC2/AC3 | **Table de décision** (§3.3.1) | Deux axes réels : mécanisme d'authentification (aucun / jeton invalide / Cookie / Basic) × opération mutante (`PUT`/`PATCH`/`DELETE`). C'est une combinaison conditions → actions, pas une suite de BVA. |
| RB03-AC4 | CRUD | L'assertion porte sur l'**absence** d'effet de bord, ce qui se vérifie par une lecture — inverse de l'écriture. |
| RB03-AC6/AC7/AC8 | CRUD | Update total, update partiel, delete, et l'inverse du delete (relecture). |
| RB04-AC1/AC2 | Partitionnement d'équivalence + **combinatoire** (§3.1.2) | Quatre paramètres de filtre indépendants et optionnels : un par classe, plus une combinaison. La combinaison complète explose (2⁴ hors valeurs), d'où le pairwise. |
| RB04-AC3 | Analyse des valeurs limites | La prose dit *« greater than or equal »* : la valeur exacte est la frontière, et son inclusivité est le seul point qui distingue les deux lectures. |
| RB04-AC4/AC5 | Partitionnement d'équivalence, supposition d'erreur | Résultat vide (classe valide, **pas** un refus) ; paramètre inconnu (silence de la source). |
| RB05-AC1/AC2/AC3/AC4 | Partitionnement d'équivalence | Id existant / inexistant / non conforme au type, et négociation de contenu. |
| RB06-AC1 | Partitionnement d'équivalence | Une seule classe, dont la sortie attendue est contradictoire dans la source (Q4). |
| RB06-AC2 | Supposition d'erreur | Surface protocolaire : méthode invalide sur un chemin valide. |

**Techniques écartées, et pourquoi** — l'omettre laisserait croire qu'on n'y a pas pensé :
*Domain Testing* (§3.1.1) suppose plusieurs variables **liées** portant chacune leur frontière ;
ici `checkin`/`checkout` seraient candidates, mais aucune règle ne les lie (Q13 est justement là
parce que la relation n'est pas déclarée) — l'appliquer reviendrait à inventer la contrainte.
*State Transition Testing* (§3.2.2) : aucune machine à états n'est déclarée, une réservation n'a
pas de statut. *Metamorphic* : les sorties attendues sont énonçables. *CT-AI* : sans objet.

### 5.3 Sous-étapes obligatoires

- **3b — oracles standardisés : appliqué.** Deux domaines normalisés sont touchés : **codes de
  statut HTTP** (l'oracle dit que 201 signifie « ressource créée », ce qui rend le `201` de
  `GET /ping` — un *health check* qui ne crée rien — anormal **au regard de la norme**, jamais
  au regard du contrat, lequel le promet) et **dates ISO 8601** (`CCYY-MM-DD` est la forme
  étendue d'ISO 8601 ; les valeurs hors format de `RB02-AC3-C4` et `RB04-AC3-C2` en sont
  dérivées). Aucun oracle Luhn / IBAN / ISO 4217 / RFC 5322 n'est pertinent : `totalprice` est
  un nombre nu, sans devise déclarée — ce qui est en soi consigné en §6.
- **3c — expansion systématique de couverture : appliquée, patron par patron.**

  | Patron | Résultat |
  |---|---|
  | Vue liste / collection | **Appliqué** : `GetBookings` sans filtre, par filtre, combiné, résultat vide. Tri, pagination, persistance : **non déclarés** — le silence est consigné (Q14) plutôt que supposé. |
  | Énumérer *chaque* liste | **Appliqué** : `GetBookings` est la seule collection du contrat. Vérifié sur les 8 opérations. |
  | Cycle CRUD complet | **Appliqué** : create, read, update total, update partiel, delete, relecture après delete. |
  | Collections sœurs | **Sans objet** : aucune entité du contrat ne porte de sous-collection. |
  | Comportement conditionnel | **Appliqué** : table de décision mécanisme d'auth × opération. Aucun drapeau de configuration n'est déclaré. |
  | Autorisation et contrôle côté serveur | **Appliqué** : non authentifié (×3 méthodes), justificatif invalide (×3). **IDOR non dérivable** : le contrat n'a pas de notion de propriétaire (passe triple-AC) — déclaré comme limite, pas couvert en silence. |
  | **Surface protocolaire** | **Appliqué** : méthode invalide sur chemin valide (`RB06-AC2-C1`) ; négociation de contenu (`RB02-AC6-C1/C2`, `RB05-AC4-C1`) ; corps vide (`RB02-AC3-C2`) ; champs inconnus et pagination : silence consigné (Q14). Idempotence de `PUT`/`DELETE` : **non dérivée**, faute de clause — voir §7, c'est un manque assumé. |
  | Surface de rendu | **Sans objet** : aucune interface utilisateur. Les cinq patrons à médium visuel tombent pour absence de médium, exactement comme `coverage-expansion.md` le prévoit. |
  | Récupération de compte | **Sans objet** : aucun flux de réinitialisation n'est déclaré. |
  | Surface d'interaction | **Partiellement sans objet** : double soumission, navigation en cours de flux, contenu textuel inattendu — les trois premiers supposent une interface. Reste **deux acteurs sur un enregistrement** : deux `PUT` concurrents sur la même réservation. Le contrat ne dit rien de l'ordre ni du gagnant → **non dérivé en condition**, consigné comme manque en §7 plutôt qu'inventé. |

- **3d — conditions issues de la base de connaissance : dégradé.** `.qaia/knowledge/` n'existe
  pas dans ce dépôt pour cette cible. **Base de connaissance absente** (règle 8 du contrat
  partagé) ; `knowledgeApplied` est vide, aucune règle `BR-KB-nnn` n'est citée. Sur une cible
  externe c'est attendu, et c'est aussi la raison pour laquelle rien ici ne dépasse ce que le
  document publie.

### 5.4 Conditions dérivées

Notation : `[req-neg]` = condition de refus/erreur/déni au sens d'ADR 0001 ; `[open] Qn` =
condition reposant sur une question non arbitrée ; **toutes** portent `[level: api]` (§5.1).

#### US-RB-01 — `CreateToken` · `POST /auth`

| # | Condition | Technique | Clause | `[req-neg]` | Prio | Motif de priorité |
|---|---|---|---|---|---|---|
| RB01-AC1-C1 | Justificatifs valides → 200, corps portant `token` | EP | `CreateToken · success.200.token` | — | P1 | Porte d'entrée de toutes les opérations mutantes : sa panne bloque trois opérations sur huit. |
| RB01-AC2-C1 | Mot de passe erroné → aucun `token` dans le corps | EP | `CreateToken · success.200.token` (contraposée) | `[req-neg]` `[open] Q1` | P1 | Un client qui obtiendrait un jeton sur un mauvais mot de passe est une faille d'accès, impact maximal. |
| RB01-AC2-C2 | Nom d'utilisateur inconnu → aucun `token` | EP | idem | `[req-neg]` `[open] Q1` | P2 | Même impact, probabilité moindre (même chemin de code présumé). |
| RB01-AC2-C3 | `username` omis → refus | EP (classe invalide) | `CreateToken · parameter.username` (`optional: false`) | `[req-neg]` `[open] Q6` | P1 | Si le `defaultValue` s'applique, un corps vide s'authentifie : impact maximal, probabilité réelle (la contradiction 1 est écrite dans le document). |
| RB01-AC2-C4 | `password` omis → refus | EP (classe invalide) | `CreateToken · parameter.password` | `[req-neg]` `[open] Q6` | P1 | Idem. |
| RB01-AC3-C1 | Le statut d'un échec diffère du statut d'un succès | EP | **aucune clause** — absence de bloc `error` | `[req-neg]` `[open] Q1` | P1 | C'est le défaut candidat n° 1 de la ligne de base ; un client testant `response.ok` traite un refus comme un succès. |

#### US-RB-02 — `CreateBooking` · `POST /booking`

| # | Condition | Technique | Clause | `[req-neg]` | Prio | Motif |
|---|---|---|---|---|---|---|
| RB02-AC1-C1 | Corps complet → 200, `bookingid` numérique et `booking` renvoyant les 7 champs envoyés | EP | `CreateBooking · success.200.bookingid`, `success.200.booking` | — | P1 | Fonction centrale du service. |
| RB02-AC1-C2 | Création **sans** justificatif → 200 | EP | `CreateBooking · (aucun en-tête d'authentification déclaré)` | — | P2 | La promesse d'anonymat de l'écriture ; sa violation casserait tous les intégrateurs. |
| RB02-AC2-C1 | Relecture `GET /booking/{id}` → les 7 champs métier identiques (`bookingid` **non** attendu) | CRUD | `GetBooking · success.200` | — | P1 | Une création non relisible rend le service inutile. |
| RB02-AC3-C1 | Chacun des 7 champs obligatoires omis à son tour → refus | EP (classes invalides) | `CreateBooking · parameter.*` (`optional: false`) → **aucun code déclaré** | `[req-neg]` `[open] Q3` | P1 | Sept partitions invalides déclarées ; c'est là que vit le 500 observé. |
| RB02-AC3-C2 | Corps `{}` → refus | EP | idem | `[req-neg]` `[open] Q3` | P1 | Cas observé en 500 par la ligne de base : une faute du client imputée au serveur, avec astreintes à la clé. |
| RB02-AC3-C3 | `totalprice` en chaîne, `depositpaid` en chaîne → refus | EP (type) | `CreateBooking · parameter.totalprice` (`Number`), `parameter.depositpaid` (`Boolean`) | `[req-neg]` `[open] Q3` | P2 | Un typage non contrôlé corrompt la donnée stockée. |
| RB02-AC3-C4 | `bookingdates.checkin` hors `CCYY-MM-DD` → refus | EP (format) | `CreateBooking · parameter.bookingdates.checkin` (`Date`, format en prose seulement) | `[req-neg]` `[open] Q5` | P2 | Le format n'étant contraint nulle part dans le corps, la probabilité d'acceptation silencieuse est forte. |
| RB02-AC5-C1 | Le statut d'une création est **200**, tel que déclaré | EP | `CreateBooking · success (Success 200)` | — | P1 | Remplace l'AC5 « 201 » de la ligne de base : on teste le contrat publié, pas la sémantique HTTP. |
| RB02-AC6-C1 | `Content-Type: text/xml` + corps XML → 200 + corps XML | EP | `CreateBooking · success.examples (XML Response)` | — | P2 | Chemin déclaré par un exemple de réponse, donc promis. |
| RB02-AC6-C2 | `Content-Type: text/plain` → refus | Supposition d'erreur | **aucune clause** | `[req-neg]` `[open] Q11` | P3 | Surface protocolaire ; impact limité, mais un 5xx ici serait le même défaut que `RB02-AC3-C2`. |
| RB02-AC7-C1 | `totalprice` à 0 puis à -1 | Valeurs limites | `CreateBooking · parameter.totalprice` (`Number`, **aucune borne**) | `[req-neg]` `[open] Q3` | P3 | Un prix négatif accepté est un défaut métier ; aucune borne n'étant déclarée, l'attente est ouverte. |

#### US-RB-03 — `UpdateBooking`, `PartialUpdateBooking`, `DeleteBooking`

| # | Condition | Technique | Clause | `[req-neg]` | Prio | Motif |
|---|---|---|---|---|---|---|
| RB03-AC1-C1 | `PUT` sans en-tête d'authentification → refus | Table de décision | `UpdateBooking · header.Cookie`, `header.Authorization` + `description` | `[req-neg]` `[open] Q2` | P1 | Écriture non protégée = altération de données par un anonyme. |
| RB03-AC2-C1 | `DELETE` sans en-tête d'authentification → refus | Table de décision | `DeleteBooking · description`, `header.*` | `[req-neg]` `[open] Q2` | P1 | Destruction par un anonyme : impact maximal. |
| RB03-AC3-C1 | `PATCH` sans en-tête d'authentification → refus | Table de décision | `PartialUpdateBooking · header.Cookie`, `header.Authorization` | `[req-neg]` `[open] Q2` | P1 | **Opération absente de la ligne de base** ; même surface d'écriture que `PUT`. |
| RB03-AC3-C2 | Justificatif invalide sur `PUT`/`PATCH`/`DELETE` → même refus que sans justificatif | Table de décision | idem | `[req-neg]` `[open] Q2` | P2 | Une différence de traitement entre « absent » et « invalide » est une fuite d'information exploitable. |
| RB03-AC4-C1 | Après un refus d'autorisation, la réservation est inchangée | CRUD | `GetBooking · success.200` | `[req-neg]` | P1 | Un refus qui écrit quand même est le pire des deux mondes. |
| RB03-AC5-C1 | `PUT` avec `Cookie: token=<jeton>` → 200 + corps mis à jour | EP | `UpdateBooking · header.Cookie`, `success.200` | — | P1 | Chemin nominal de la modification. |
| RB03-AC5-C2 | `PUT` avec `Authorization: Basic` → 200 | EP | `UpdateBooking · header.Authorization`, `examples (XML/URLencoded)` | — | P1 | **Second mécanisme, absent de la ligne de base** : promis par le contrat, donc dû. |
| RB03-AC6-C1 | `PUT` avec un champ obligatoire omis → refus | EP (classe invalide) | `UpdateBooking · parameter.*` (`optional: false`, les 7) | `[req-neg]` `[open] Q3` | P2 | `PUT` est le seul endroit où « total » est promis ; l'accepter partiel effacerait des champs. |
| RB03-AC7-C1 | `PATCH` d'un seul champ → 200, les autres champs conservés | CRUD | `PartialUpdateBooking · parameter.*` (`optional: true`), `success.200` | — | P1 | C'est la promesse qui distingue `PATCH` de `PUT`. |
| RB03-AC7-C2 | `PATCH` avec un corps `{}` (valide au contrat) | CRUD | `PartialUpdateBooking · parameter.*` (tous `optional: true`) | `[open] Q9` | P2 | `coverage-expansion.md` documente exactement ce piège : trois exécutions indépendantes avaient inventé « réinitialisation aux valeurs par défaut » avec assurance. Ici l'issue reste ouverte. |
| RB03-AC8-C1 | `DELETE` authentifié d'une réservation **créée par le test** → 201 | CRUD | `DeleteBooking · success` (intitulé 200, exemple `201 Created`) | — | P2 | Chemin nominal ; l'attente elle-même est contradictoire dans la source (Q4). |
| RB03-AC8-C2 | Une réservation supprimée n'est plus lisible | CRUD | **aucune clause** (aucun 404 déclaré) | `[req-neg]` `[open] Q10` | P2 | L'inverse du delete ; sans lui, « supprimé » n'est pas vérifié. |

#### US-RB-04 — `GetBookings` · `GET /booking`

| # | Condition | Technique | Clause | `[req-neg]` | Prio | Motif |
|---|---|---|---|---|---|---|
| RB04-AC1-C1 | Sans filtre → 200 + tableau d'objets portant chacun `bookingid` numérique | EP | `GetBookings · success.200.object`, `object.bookingid` | — | P1 | Point d'entrée de toute intégration. |
| RB04-AC2-C1 | Un filtre à la fois (`firstname`, `lastname`, `checkin`, `checkout`) → 200 + sous-ensemble | EP | `GetBookings · parameter.*` (`optional: true`) | — | P2 | Quatre partitions déclarées ; un filtre ignoré renvoie trop de données. |
| RB04-AC2-C2 | Les quatre filtres combinés | Combinatoire | idem | — | P2 | La combinaison est la seule qui teste l'ET logique entre critères. |
| RB04-AC3-C1 | `checkin` égal à la date de check-in d'une réservation → celle-ci est incluse | Valeurs limites | `GetBookings · parameter.checkin` (*« greater than or equal to »*, prose) | `[open] Q12` | P2 | L'inclusivité est la frontière ; elle n'existe que dans la prose. |
| RB04-AC3-C2 | `checkin` hors `CCYY-MM-DD` → refus | EP (format) | `GetBookings · parameter.checkin` (format en prose) | `[req-neg]` `[open] Q5` | P2 | Contrainte énoncée mais non outillée : classiquement non appliquée. |
| RB04-AC4-C1 | Filtre sans correspondance → 200 + tableau vide | EP | `GetBookings · success.200.object` | — | P2 | **Ce n'est pas un `@negative`** : `negative-ratio.md` range explicitement l'exclusion de liste hors des refus. |
| RB04-AC5-C1 | Paramètre de requête inconnu | Supposition d'erreur | **aucune clause** | `[open] Q14` | P3 | Silence de la source ; l'issue est ouverte, pas supposée. |

#### US-RB-05 — `GetBooking` · `GET /booking/:id`

| # | Condition | Technique | Clause | `[req-neg]` | Prio | Motif |
|---|---|---|---|---|---|---|
| RB05-AC1-C1 | Id existant → 200 + les 8 champs déclarés | EP | `GetBooking · success.200` | — | P1 | Lecture nominale. |
| RB05-AC2-C1 | Id inexistant → refus | EP (classe invalide) | **aucune clause** (aucun 404 déclaré) | `[req-neg]` `[open] Q10` | P1 | Corrige la ligne de base, qui présentait ce 404 comme documenté. |
| RB05-AC3-C1 | Id non numérique | EP (type) | `GetBooking · parameter.id` (`String`) **vs** `UpdateBooking · parameter.id` (`Number`) | `[req-neg]` `[open] Q8` | P2 | Contradiction 2 : deux typages du même paramètre selon l'opération. |
| RB05-AC4-C1 | `Accept: application/xml` → 200 + corps XML | EP | `GetBooking · success.examples (XML Response)` | — | P2 | Chemin déclaré par un exemple de réponse. |

#### US-RB-06 — `Ping` · `GET /ping`

| # | Condition | Technique | Clause | `[req-neg]` | Prio | Motif |
|---|---|---|---|---|---|---|
| RB06-AC1-C1 | `GET /ping` → 201, tel que l'exemple le promet | EP | `Ping · success` (intitulé `Success 200`, description et exemple `201`) | `[open] Q4` | P1 | Toute supervision branchée dessus dépend du code exact ; et l'attente est indécidable dans la source. |
| RB06-AC2-C1 | `POST /ping` → méthode invalide sur chemin valide | Supposition d'erreur | **aucune clause** | `[req-neg]` `[open] Q15` | P3 | 404 et 405 ne disent pas la même chose à un client ; la source ne tranche pas. |

### 5.5 Comptes

| | |
|---|---|
| Conditions | **42** |
| dont `[level: api]` | 42 (100 %) — aucune `[level: e2e]`, cible sans interface |
| dont `[req-neg]` (ADR 0001) | **22** |
| dont `[open] Qn` | 25 |
| Questions ouvertes | 16 (10 en première passe, 6 offertes en seconde) |
| Priorités (conditions) | P1 : 21 · P2 : 17 · P3 : 4 |

Périmètre de génération retenu : **P1 + P2 + P3** (le cahier est petit ; aucun renoncement de
périmètre à consigner, donc aucune dérogation de priorité au sens de `negative-ratio.md`).

### 5.6 Vérification du cahier émis (contrat partagé, règle 4bis)

Les nombres ci-dessous sont **lus dans le fichier émis**, pas récapitulés d'intention — c'est la
règle 2 de `negative-ratio.md` (« only reading the emitted file tells you what it *says* »).
Commande de relecture, rejouable :

```
python - <<'PY'   # comptage des scenarios, cas executables et etiquettes @negative
# voir 21-restfulbooker.feature ; Outline compte N cas pour N lignes d'Examples
PY
```

| Mesure | Valeur lue dans `21-restfulbooker.feature` |
|---|---|
| Scénarios (blocs) | **38** |
| Cas exécutables (Outline = N lignes) | **55** |
| Cas `@negative` | **32**, portés par **18** lignes de tags `@negative` |
| Ratio négatif (signal, jamais une porte) | **58,2 %** |
| Scénarios `@low-confidence` | **22** |
| Priorités (scénarios) | P1 : 18 · P2 : 16 · P3 : 4 |
| Identifiants | `@QAIA-RB-001` … `@QAIA-RB-038`, uniques, **sans trou** |
| Scénarios `@smoke` | **0** — voir §5.1, point 2 |

**Porte ADR 0001 : verte, 22 conditions `[req-neg]` sur 22 couvertes**, chacune par un scénario
portant le niveau de la condition (`@api`) — la précision qu'ADR 0008 ajoute à la porte est
satisfaite trivialement ici, puisqu'aucune condition n'est `e2e`.

**Explicatif du ratio** (exigé par le contrat partagé quand le ratio s'écarte de ~40 %) : 58 %
est **haut**, et ce n'est pas du remplissage. La cause est structurelle : la cible est une API
dont **aucune des huit opérations ne déclare de code d'erreur**, donc chaque champ obligatoire,
chaque en-tête d'authentification et chaque identifiant inexistant ouvre un chemin de refus non
spécifié. À l'inverse, `RB04-AC4-C1` (filtre sans correspondance) est délibérément **non**
compté comme `@negative` : `negative-ratio.md` range l'exclusion de liste hors des refus, et
c'est le moyen le plus courant de gonfler un ratio sans intention de tricher.

**Deux erreurs de comptage trouvées par cette vérification**, corrigées ci-dessus : la
répartition de priorité avait été écrite de mémoire (P1 17 / P2 18 / P3 7 au lieu de
21 / 17 / 4) et le nombre de conditions `[open]` était surévalué (30 au lieu de 25). Aucune des
deux n'était visible en relisant le texte — seul le recomptage les a montrées. C'est exactement
la panne que la règle 4bis décrit.

### 5.7 Portes du dépôt

| Contrôle | Résultat |
|---|---|
| `python eval/tools/check_test_levels.py` | **OK** — « 19 cahier(s) vivant(s), 176 scenario(s) verifie(s) », le nouveau cahier est bien dans le périmètre (vérifié via `iter_feature_files`) |
| `gherkin-lint -c .gherkin-lintrc` sur le périmètre de `make lint` | **exit 0** — 23 fichiers, dont celui-ci |

---

## 6. Défauts candidats du service — ce que le service **fait**, à distinguer de ce qu'on **promet**

Rien dans cette section n'est dérivé du contrat, et rien n'y est vérifié par ce document.
Ce sont des observations reprises de la ligne de base, plus des défauts **du contrat lui-même**
trouvés par l'ingestion. Confirmer ou infirmer les premiers relève de `contract-probe`.

**Défauts candidats du service** (observés par la ligne de base, non reproduits ici) :

1. `POST /auth` avec un mauvais mot de passe → **200**. Un client testant `response.ok` traite un
   refus comme un succès. Sévérité la plus haute des quatre.
2. `POST /booking` avec un corps `{}` → **500**. Faute du client imputée au serveur ; déclenche
   alertes, relances et astreintes injustifiées.
3. `GET /booking/999999` → **404** — conforme à l'attente d'un client, mais **hors contrat** :
   la documentation ne le promet pas. Défaut de **documentation**, pas de service.
4. `PUT`/`DELETE` sans jeton → **403** — même remarque : le comportement est bon, le contrat est
   muet.

**Défauts du contrat publié** (trouvés par la passe des quatre contradictions, pas par
l'observation) :

5. **Aucun code d'erreur n'est déclaré sur aucune des huit opérations**, alors que trois exigent
   un justificatif. Le comportement défensif entier de l'API est hors contrat.
6. Le bloc `Success 200` de `Ping` **et** de `DeleteBooking` annonce `201 Created` dans sa
   description et son exemple. Auto-contradiction en trois lignes.
7. `id` typé `String` par `GetBooking`, `Number` par les trois opérations mutantes.
8. Les en-têtes d'authentification sont `optional: true` alors que la prose les dit requis.
9. Les identifiants d'administration sont publiés comme `defaultValue` de deux champs déclarés
   obligatoires — contradiction 1 sur un champ de justificatif.
10. L'énumération en prose des `Content-Type` acceptés est démentie par un exemple du document
    lui-même (`application/x-www-form-urlencoded`), et l'entrée dit `text/xml` quand la sortie
    dit `application/xml`.
11. `totalprice` est un nombre sans devise déclarée et sans borne.

**Remarque de qualité, ni critère ni question** (`need-understanding` étape 5 interdit d'y
consommer un slot, le contrat étant sans ambiguïté) : `POST /booking` déclare `200` là où la
sémantique HTTP attendrait `201` + `Location`. Le service **tient sa promesse** ; c'est la
promesse qui est discutable. La ligne de base avait diagnostiqué cela correctement puis l'avait
tout de même écrit comme critère d'acceptation (AC5) — c'est le seul endroit où elle se
contredit elle-même.

---

## 7. Ce que la méthode a coûté pour rien — dit sans ménagement

1. **`istqb-design` étape 2b redemande ce qu'`openapi-ingest` étape 6 a déjà tranché.**
   `openapi-ingest/SKILL.md` l. 80-83 : *« `[level: api]` on every derived condition »* — sans
   condition ni exception, sauf remontée explicite en `e2e`. `istqb-design/SKILL.md` l. 80-92
   demande malgré tout *« la justification en une phrase »* **par condition**. Sur une cible sans
   interface, c'est 42 copies de la même phrase. La règle utile serait : justifier le niveau
   **par exception**, quand il diffère du niveau par défaut de la source.
2. **ADR 0008 interdit involontairement tout scénario de parcours sur une cible API.** Section
   « Pourquoi exactement une étiquette », l. 73-74 : *« il traverse par définition l'interface
   utilisateur et porte donc `@e2e` »*. Sur `restful-booker` il n'y a pas d'interface, donc pas
   de `@smoke` possible — alors qu'un parcours CRUD est un test scenario-based légitime au
   niveau API. L'ADR a été écrit en supposant qu'un parcours est forcément un parcours d'écran.
3. **`testbook-generate/SKILL.md` contient deux fois son contrat d'émission, et les deux copies
   divergent.** La section `## Emission contract` (l. 71-132) et la section
   `### The emission contract — what a .feature file must look like` (l. 168-190) disent la même
   chose deux fois. Pire, elles se contredisent sur un point précis : la première (l. 82-86)
   **décrit** la convention `# Feature: US-004` comme « une habitude QAIA » ; la seconde
   (l. 178-181) explique qu'elle a été **délibérément retirée** parce que la décrire faisait
   émettre le commentaire *à la place* de la déclaration. C'est exactement la panne « deux
   sources pour une règle » que ce dépôt documente à trois endroits — à l'intérieur d'un seul
   fichier. Accessoirement, la seconde section est insérée **entre l'étape 5 et l'étape 6** de la
   liste numérotée `## Steps — initial generation`, qu'elle coupe en deux.
4. **Cinq des dix patrons de `coverage-expansion.md` supposent une interface** et se soldent par
   cinq lignes « sans objet » qu'il faut écrire quand même (garde-fou : *« a sub-step of 3c with
   no mention at all … is a defect »*). C'est défendable — la trace vaut mieux que le silence —
   mais sur une cible API le patron « la plus courante des omissions » (autorisation) est le seul
   des cinq premiers à produire quelque chose. Un aiguillage explicite « cible API → appliquer
   ces N patrons » économiserait la moitié de l'étape.
5. **La cérémonie non-interactive** (`unconfirmed`, `pending-validation`, `openArbitrations`,
   `simulated`) est correcte et coûte trois paragraphes qui ne disent qu'une chose : personne
   n'a validé. Elle est justifiée par l'historique du dépôt (bypass D125), pas par ce document.
6. **Ce que la méthode m'a fait manquer, faute de clause** : idempotence de `PUT`/`DELETE`, et
   deux `PUT` concurrents sur la même réservation. Les deux sont des conditions qu'un testeur
   API dérive par réflexe ; `coverage-expansion.md` les nomme, et le plafond anti-fabrication
   les bloque parce que le contrat ne promet rien à leur sujet. Le plafond a raison sur le
   principe, mais il produit ici une **couverture protocolaire volontairement incomplète** — dite
   ici plutôt que masquée.

**Une remarque de forme** : `testbook-generate/references/negative-ratio.md` l. 11-17 insère un
paragraphe de correction en **français** au milieu d'un fichier entièrement en anglais. Le
contenu est bon ; la langue signale une correction faite dans l'urgence.
