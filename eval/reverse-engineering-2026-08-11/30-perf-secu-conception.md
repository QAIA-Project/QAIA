---
stepsCompleted: [perf-check/design, security-surface/design]
lastStep: 30-conception
lastSaved: 2026-08-11
status: not-executed
---

# 30 — Perf & sécurité : ce qui **devrait** être testé, et qui ne l'a pas été

**Date : 2026-08-11.** Ce document est une **conception, pas un run.** Rien de ce qui est
décrit ici n'a été exécuté contre les trois cibles, et la raison est écrite avant la méthode
parce qu'elle prime sur elle.

---

## 0. La limite, avant la méthode

Les deux skills mobilisées portent une mention d'autorisation dans leur `description` même :

- `plugins/qaia-playwright/skills/security-surface/SKILL.md` — *« Authorized self-hosted
  targets only. »*
- `plugins/qaia-playwright/skills/perf-check/SKILL.md` — *« Self-hosted targets only. »*

Et le garde-fou bloquant de `security-surface` (l. 67-72) énumère les **trois seules** bases
d'autorisation admises :

> (a) an in-repo app under `examples/` […] ; (b) a target listed in […] `docs/DEMO-TARGETS.md`
> […] ; (c) a target explicitly authorized by the human founder this session […]. **If none of
> the three applies, do not scan.**

Aucune des trois cibles ne satisfait (a), (c). Reste (b) — et le catalogue du dépôt ne les
autorise pas : **il les interdit explicitement.**

`docs/DEMO-TARGETS.md`, règle d'or (l. 3) :

> *explore* on shared public demos; run *security scans and load tests only on self-hosted*
> instances (Docker/npm/VPS) — shared demos forbid them.

Matrice de couverture du même fichier, colonnes **Security** / **Perf** :

| Cible | Ligne du catalogue | Security | Perf | Verdict |
|---|---|---|---|---|
| `www.saucedemo.com` | « SauceDemo » (l. 18) | **❌** | **❌** | interdit par le catalogue, deux fois |
| `restful-booker.herokuapp.com` | voir note ci-dessous | *self-host* | *self-host* | l'instance visée **n'est pas** self-hosted |
| `www.alpes-envol.fr` | **absente du catalogue** | — | — | aucune base d'autorisation, et c'est une collectivité |

**Note sur restful-booker.** Le catalogue liste `Restful-Booker-Platform` avec « security:
self-host / perf: self-host ». C'est l'image Docker, **pas** l'instance partagée
`restful-booker.herokuapp.com`. La ligne du catalogue autorise ce qu'on héberge soi-même ; elle
n'autorise pas le bac à sable Heroku d'un tiers, qui est précisément la « shared public demo »
que la règle d'or vise. Lire cette ligne comme un feu vert pour l'URL Heroku serait un abus de
citation.

**Le cas `alpes-envol.fr` n'est pas du même ordre que les deux autres.** SauceDemo et
restful-booker sont des bancs d'entraînement dont la vocation est d'être testés — l'interdiction
y est contractuelle (leurs conditions d'usage) et technique (ressource partagée). Le site de
l'aérodrome de Gap-Tallard est le site en production d'une **collectivité territoriale
française**, avec un service utilisé par des administrés. Une montée en charge ou un scan y est
un incident d'exploitation potentiel, et suivant l'intention, l'**article 323-1 du code pénal**.
Il n'y a pas d'arbitrage à rendre sur celui-là.

### Ce qui a donc été refusé, nommément

| Action | Skill qui la prescrit | Cibles concernées | Motif |
|---|---|---|---|
| Exécuter `k6/load.js` (type `load`) | perf-check, étape 3 | les 3 | charge sur ressource tierce |
| Types `stress`, `spike`, `soak`, `scalability` | perf-check, étape 3, tableau des `stages` | les 3 | `stress` cherche **le point de rupture** d'un tiers ; `soak` tient 30 min de trafic soutenu |
| « fire N concurrent requests », p95 sur N=10 VU | perf-check, étape 1 | les 3 | boucle de requêtes |
| Intégrité sous concurrence (course de N clients) | perf-check, étape 2 | restful-booker | écritures concurrentes sur données d'autrui |
| S1 — 4 cas de jetons (absent/malformé/expiré/mal signé) | security-surface, `protocols.md#s1` | restful-booker | contournement d'authentification |
| S2 — IDOR, lecture + écriture + suppression croisées | security-surface, `#s2` | restful-booker | **destructif** (`DELETE` sur ressource d'autrui) |
| S3 — 6 charges malformées, dont 10 Mo et caractères de contrôle | security-surface, `#s3` | les 3 | fuzzing + charge |
| S4 — énumération d'utilisateurs, **~20 tentatives par cas** | security-surface, `#s4` | saucedemo, restful-booker | énumération + bourrage d'identifiants |
| S6 — OWASP ZAP baseline | security-surface, `#s6` | les 3 | scan, même « passif » : le spider parcourt tout le site |

Le refus **n'est pas un contournement de la mission** : c'est le premier livrable. Ce qui suit
décrit ce qu'on ferait *avec* mandat, et quel mandat il faudrait.

---

## 1. Sécurité (CT-SEC)

### 1.1 Étape 0 — actifs et menaces, avant la checklist

La skill impose l'ordre (l. 19-36) : nommer les actifs, classer les menaces, **puis** dérouler.
« A fixed checklist run uniformly treats every app the same regardless of what it actually
protects. » Les trois cibles le démontrent : ce sont trois profils d'actifs différents.

⚠ **VALIDATION** — la skill exige que le classement soit *proposé* par l'agent et *arbitré par
un humain* (l. 30-31). Personne ne l'a arbitré ici. Les trois tableaux ci-dessous sont donc des
**propositions non validées**, et le resteront tant que la ligne « arbitré par » est vide.

#### `saucedemo.com` — actifs

| Actif | Présent ? | Menace | Impact | Proba | Priorité |
|---|---|---|---|---|---|
| Identifiants | ✅ mais **publiés dans la page d'accueil** | vol | *nul* — ils sont publics | — | **hors sujet** |
| Données personnelles d'autres utilisateurs | ❌ pas de persistance serveur | — | — | — | — |
| Données de paiement | ❌ tunnel factice, aucun paiement | — | — | — | — |
| Fonctions d'administration | ❌ | — | — | — | — |

**Conclusion d'étape 0 : il n'y a pas d'actif à protéger.** SauceDemo est une application
statique dont les identifiants sont affichés à l'écran. Une campagne CT-SEC y est un exercice de
style : le classement par risque, appliqué honnêtement, dit que **la cible ne mérite pas la
checklist**, et c'est exactement ce que l'étape 0 est censée produire quand c'est le cas. La
skill prévoit ce cas (l. 27-29 : « An app with no sensitive asset […] still runs the full
checklist, simply without an elevated priority ») — mais elle ne prévoit pas le cas où l'app n'a
**aucun** back-end, où la moitié de la checklist est vide de sens faute de serveur à interroger.

À noter, et à ne pas signaler comme défaut : `protocols.md#s4` le dit déjà lui-même —
> SauceDemo returns a distinct locked-out message versus the generic one […]. That is
> enumeration by design in a teaching app — a useful reference for what the finding looks like,
> **not a target to file a report against.**

C'est la seule ligne des deux skills qui anticipe la question de la cible tierce, et elle est
enterrée dans un fichier de référence, au 4ᵉ protocole sur 6.

#### `restful-booker.herokuapp.com` — actifs

| Actif | Menace | Impact | Proba | Priorité proposée |
|---|---|---|---|---|
| Jeton d'authentification (`POST /auth`) | vol/forge → écriture sur toute réservation | Moyen | Élevée (pas d'HTTPS forcé, cf. doc 31) | **P1 → S1** |
| Réservations de tous les utilisateurs (`GET /booking` liste tout) | lecture/modification croisée | Moyen | Élevée — aucune notion de propriétaire | **P1 → S2** |
| Nom, prénom des réservants | divulgation | Faible (données de démo) | Élevée | P2 |
| Fonctions privilégiées | — | — | — | absentes |

**Réserve capitale sur l'impact** : ce sont des **données de démonstration factices** dans un bac
à sable réinitialisé périodiquement. Le même défaut sur une vraie application de réservation
serait Élevé ; ici il est plafonné à Moyen **par le contexte, pas par la preuve**. Un rapport qui
noterait ces lignes « Critique » serait techniquement défendable et professionnellement
malhonnête.

Point de méthode : `GET /booking` renvoie **la liste complète** des réservations sans
authentification. Ce n'est pas une IDOR — c'est le contrat documenté de l'API. Un test S2 qui
« découvre » cela signalerait comme faille une fonctionnalité annoncée. La skill ne demande nulle
part de confronter un constat au contrat de l'application avant de le qualifier de faille ;
c'est un manque, et `spec-suite-drift` existe dans le dépôt pour exactement ce rapprochement.

#### `alpes-envol.fr` — actifs

| Actif | Menace | Impact | Proba | Priorité proposée |
|---|---|---|---|---|
| **Panier / commande** (cookie `current_cart_id` observé, cf. doc 31) | vol de session, détournement de panier | **Élevé — usagers réels** | à établir | **P1 → S5 puis S1** |
| Données personnelles d'administrés | divulgation | **Élevé** | à établir | **P1** |
| Données de paiement | selon le prestataire, non déterminé | **Élevé** | à établir | **P1 si applicable** |
| Compte d'administration du CMS | prise de contrôle du site | **Élevé** | à établir | **P1** |

Trois « à établir » sur quatre lignes. C'est le résultat honnête : **l'étape 0 n'est pas
réalisable de l'extérieur.** La skill demande de nommer les actifs « from the US, test book or
knowledge base — never invented » (l. 21-22). Sur une cible tierce il n'existe ni US, ni test
book, ni base de connaissance. Ce que j'ai mis dans ce tableau vient d'un cookie et d'un
en-tête ; le reste serait inventé, et l'inventer serait violer la ligne 22.

**Conséquence méthodologique** : `security-surface` n'est pas seulement *interdite* sur une cible
tierce, elle est **inopérante** — son étape 0, qui commande tout le reste, exige des documents
que seul le propriétaire détient.

### 1.2 Les cinq protocoles, et le mandat qu'il faudrait

| ID | Ce qu'il faudrait faire | Fixtures exigées par la skill | Mandat nécessaire — **auprès de qui** |
|---|---|---|---|
| **S1** Frontières d'auth | 4 cas par endpoint protégé : jeton absent, malformé, expiré, signé avec la mauvaise clé → 401 aux quatre. Vérifier aussi que le corps du 401 ne dit pas *pourquoi* | 1 jeton valide + la **liste des endpoints censés être protégés**, « taken from the US, the API contract or the route table, **never guessed** » | **restful-booker** : Mark Winteringham (auteur/mainteneur) — ou, plus simplement, self-host de `Restful-Booker-Platform`, que le catalogue autorise déjà. **alpes-envol** : mandat écrit de la collectivité (aérodrome de Gap-Tallard / son délégataire) + de l'hébergeur/éditeur du CMS |
| **S2** IDOR | Avec le jeton **valide de B**, `GET`/`PUT`/`DELETE` sur la ressource de A → 404 ou 403, **et vérifier l'effet de bord**. Plus le contrôle : A sur sa propre ressource → 200 | **Deux comptes réels**, une ressource créée pendant le run, le jeton **valide** de B | Idem. Et sur restful-booker, **le modèle de données ne comporte pas de propriétaire** : il n'y a pas de « ressource de A ». Le test est donc **`blocked`, pas `pass`** — la skill impose ce mot (`#s2` : « If the test has no second account, it is not an IDOR test — report it as **blocked for want of a second account**, never as passed ») |
| **S3** Gestion d'erreur | 6 formes nommées : JSON tronqué, type inversé, champ requis manquant, charge ~10 Mo, unicode/caractères de contrôle, mauvais `Content-Type` → 4xx propre, jamais 5xx, jamais de trace | endpoint acceptant un corps | Mandat + **fenêtre de maintenance** : la charge de 10 Mo (S3-d) est une requête de charge, et sur un dyno Heroku gratuit elle peut suffire à faire tomber l'instance pour tout le monde |
| **S4** Énumération | 3 cas de connexion comparés sur **corps, statut et temps** ; **~20 répétitions par cas** pour comparer les médianes. Idem sur réinitialisation de mot de passe et inscription | 1 identifiant valide, 1 certain de ne pas exister | Mandat explicite : 60 tentatives de connexion, c'est ce qu'une défense anti-bourrage doit bloquer. Le faire sans mandat, c'est déclencher l'astreinte de quelqu'un |
| **S5** En-têtes/TLS | 1 `GET` sur le document, 1 sur un endpoint d'API. **Asserter la valeur, pas la clé** | aucune | **Aucun mandat requis** — c'est le seul protocole réalisable en visiteur ordinaire. Il est **exécuté**, résultats en doc 31 |

**Le seul protocole sur six exécutable sans mandat est S5.** C'est le fait le plus important de
cette section, et il devrait figurer dans la skill.

---

## 2. Performance (CT-PT)

### 2.1 Les deux nombres, et d'où ils viendraient

`perf-check` étape 1 impose de choisir **explicitement** N et le budget, et de dire d'où chacun
vient — « leaving them to the reader means two runs of the same skill disagree ». Défauts QAIA
en l'absence de SLO projet : **N = 10 VU, budget = 500 ms p95**, à annoncer comme défauts et non
comme engagement projet.

Aucune des trois cibles ne publie de SLO. Les trois budgets ci-dessous seraient donc des défauts
QAIA — sauf le premier, qui mérite un raisonnement propre.

| Cible | Endpoint clé (« the one the test book's P1 scenarios actually exercise most », pas la page d'accueil par réflexe) | N | Budget p95 | D'où vient le seuil |
|---|---|---|---|---|
| saucedemo | — | — | — | **Sans objet** : site statique servi par un CDN. Mesurer la p95, c'est mesurer Fastly, pas l'application. Il n'y a pas de traitement serveur à charger |
| restful-booker | `POST /booking` (création — le scénario P1 du test book `21-restfulbooker.feature`) | 10 | 500 ms — **défaut QAIA** | aucun SLO publié ; **et** un dyno Heroku gratuit s'endort : la première requête après inactivité paie un démarrage à froid de plusieurs secondes qui n'a rien à voir avec le code. Un run non averti mesurerait le réveil du dyno et le rapporterait comme latence applicative |
| alpes-envol | tunnel de commande / billetterie | 10 | 500 ms — **défaut QAIA** | aucun SLO publié. Ce seuil devrait venir de la collectivité, pas de QAIA |

La ligne saucedemo est un constat de méthode : **la skill n'a pas de critère d'applicabilité.**
Elle décrit comment mesurer, jamais quand mesurer n'a pas de sens.

### 2.2 Intégrité sous concurrence

Étape 2 : faire courir N clients sur une ressource limitée, exiger qu'**un seul** réussisse.

- **restful-booker** : la ressource limitée serait un créneau de réservation
  (`checkin`/`checkout` sur la même chambre). Il faudrait d'abord établir que l'API **prétend**
  refuser le double-booking. Rien dans la documentation apidoc ingérée (doc 20) ne l'affirme.
  **Sans règle métier revendiquée, il n'y a pas d'oracle** : deux réservations simultanées
  acceptées ne sont un défaut que si quelque chose a promis le contraire. La skill donne
  l'exemple « one bookable slot » sans jamais dire qu'il faut d'abord établir que la contrainte
  existe.
- **saucedemo** : aucun stock, aucune ressource limitée. Sans objet.
- **alpes-envol** : s'il y a une billetterie à places limitées, c'est **le** test qui compte
  (survente = préjudice réel pour des usagers réels). Et c'est exactement celui qu'on ne peut pas
  faire sans mandat, puisqu'il consiste à créer de vraies commandes concurrentes.

### 2.3 Les cinq types nommés — ce qu'on mesurerait, sur quel seuil, pourquoi

Cible de référence : une instance **self-hostée** de `Restful-Booker-Platform` (Docker), que le
catalogue autorise. C'est la manière correcte de faire ce travail : on ne demande pas
l'autorisation de charger un tiers, on héberge la même application.

| Type | `stages` (SKILL.md l. 58-62) | Ce qu'on mesure | Seuil / verdict | Pourquoi ce seuil |
|---|---|---|---|---|
| **load** | 30 s ↗ 10 VU, 2 min à 10, 30 s ↘ 0 | p50/p95/max sur le palier stable | p95 < 500 ms pendant le **palier**, pas sur le run entier | Vérifie que le budget tient au trafic **attendu**. Le mesurer sur tout le run mélange les rampes et flatte le résultat |
| **stress** | 10 → 20 → 40 VU, paliers d'1 min | **le niveau où le budget casse**, et *comment* ça casse : 5xx propre/backpressure vs. plantage ou blocage | **Pas de pass/fail** — un nombre : « le budget cède à N VU » | Le but est le point de rupture et le mode de défaillance. Un seuil binaire ne répond pas à la question posée |
| **spike** | 10 VU → 100 VU (10 s) → 10 VU → 10 VU (1 min) | taux d'erreur et p95 **pendant la traîne finale**, comparés à la ligne de base | Retour à la ligne de base pendant le dernier palier | « A system that survives the spike but never recovers has failed this test. » Le défaut visé (file d'attente saturée, pool de connexions jamais rendu) n'est visible **qu'après** la redescente |
| **soak** | 1 palier de 30 min à 10 VU | **dérive** : p95 du premier cinquième vs. p95 du dernier cinquième | Pas de dégradation significative entre les deux mesures | Cible les fuites mémoire et la croissance de tables/logs, invisibles en 2 min. **À déclarer comme approximation** si la session ne tient pas 30 min |
| **scalability** | forme `stress`, **mesurée par palier** | courbe capacité : concurrence → p95 | **Une courbe, pas un verdict** | Répond à « jusqu'où peut-on aller », qui est une question de dimensionnement, pas de conformité |

**Le piège que la skill nomme et qu'il faut redire** (l. 63-67) : `spike` et `soak` changent le
sens de « vert ». Une p95 agrégée sur tout le run masque précisément le défaut que chacun des
deux cherche — la non-récupération pour `spike`, la dérive pour `soak`. Ce sont deux mesures à
comparer, pas un nombre à seuiller.

Volume / configuration / baseline : nommés par CT-PT, non scriptés séparément ici (l. 44-47) —
volume se replie sur l'intégrité sous concurrence à grand N, configuration et baseline sont une
exigence de **documentation de l'environnement de mesure**. Cette dernière est loin d'être
cosmétique : sans elle les chiffres ne sont comparables à rien, et le dyno Heroku endormi de
§2.1 en est l'illustration.

---

## 3. Ce que les deux skills demandent et qui est inapplicable sur une cible tierce

Section demandée explicitement. Elle vaut comme **retour sur les skills**, pas sur les cibles.

| # | Ce qui est inapplicable | Ligne citée | Nature du problème |
|---|---|---|---|
| 1 | **Toute** `perf-check` | SKILL.md l. 74-75 : « Refuse a public shared target; require a self-hosted URL (Docker/VPS/local) » | Le garde-fou est **correct et net**. Mais il est en **bas** du fichier, après 70 lignes qui expliquent comment mesurer. Un agent qui lit en flux a déjà conçu le run quand il rencontre l'interdit |
| 2 | `security-surface` étape 0 | l. 21-22 : actifs « from the US, test book or knowledge base — **never invented** » | **Inopérant, pas seulement interdit** : ces documents n'existent que côté propriétaire. L'étape qui commande la priorisation ne peut pas être franchie de l'extérieur |
| 3 | S1 | `#s1` : liste des endpoints protégés « taken from the US, the API contract or the route table, **never guessed** » | Même dépendance documentaire |
| 4 | S2 | `#s2` : « **Two real accounts** […] the check is void without them » | Deux comptes ne s'obtiennent pas sans relation avec l'exploitant. Sur restful-booker le modèle n'a même pas de propriétaire |
| 5 | S4 | `#s4` : « Send each case **~20 times** and compare medians » | 20 × 3 tentatives d'authentification est indissociable d'un bourrage d'identifiants vu du côté de la victime |
| 6 | S3-d | `#s3` : « a ~10 MB string in a text field » | Requête de charge déguisée en test fonctionnel. Sur hébergement partagé, dommage collatéral pour les autres usagers |
| 7 | S6 (ZAP) | `#s6` : « it stays passive: the baseline scan spiders and observes » | « Passif » est trompeur : un spider parcourt tout le site et génère un volume de requêtes qui n'a rien d'ordinaire. Passif vis-à-vis de l'*exploitation*, pas vis-à-vis de la *charge* |

### Le défaut de skill, énoncé

`security-surface` place son garde-fou d'autorisation en **section « Guardrails », l. 65-87** —
c'est-à-dire **après** l'étape 0 et après les six protocoles. `perf-check` place le sien
**l. 72-76, en dernier**. Dans les deux cas, tout ce qui précède est écrit à l'indicatif
opératoire (« fire N concurrent requests », « run for every target »), sans réserve.

Les deux skills sont **honnêtes** : `security-surface` va jusqu'à admettre que son garde-fou est
narratif et non appliqué (l. 73-76 : « This authorization check is narrative, not enforced. No
allow-list mechanism exists in the repo: nothing outside the agent's own reasoning will stop a
scan »), et ce choix est argumenté plutôt que subi. Ce n'est donc pas un problème de franchise ;
c'est un problème de **placement**.

**Correctif proposé** (non appliqué — hors mandat de cette session) : une porte en tête de
fichier, avant toute méthode, dans les deux skills.

> **Avant toute chose : ai-je le droit ?** Nommer la cible et la base d'autorisation ((a)
> `examples/`, (b) `docs/DEMO-TARGETS.md` avec sa colonne Security/Perf citée, (c) autorisation
> nominative du fondateur **de cette session**). Si aucune ne s'applique : **s'arrêter ici et le
> dire**. Sur une cible non autorisée, seul **S5 (en-têtes/TLS)** reste praticable — c'est ce que
> voit un visiteur ordinaire. Tout le reste de ce fichier suppose l'autorisation acquise.

Deux ajouts distincts, qui ne se recouvrent pas :

1. **`perf-check` n'a pas d'étape 0.** `security-surface` a une identification actifs/menaces qui
   sert de sas de réflexion ; `perf-check` entre directement dans « fire N concurrent requests ».
   Il lui manque un critère d'**applicabilité** — la ligne saucedemo de §2.1 (charger un CDN
   statique ne mesure rien) n'est écartée par aucune ligne de la skill.
2. **Aucune des deux ne distingue « interdit » de « inopérant ».** C'est la distinction la plus
   utile de tout ce document : S2 sur restful-booker n'est pas seulement défendu, il est **vide
   de sens** (pas de propriétaire dans le modèle) ; l'étape 0 sur une cible tierce n'est pas
   seulement défendue, elle est **infaisable** (pas de documents). Un agent qui obtiendrait le
   mandat demain découvrirait que la moitié de la checklist reste bloquée pour des raisons qui
   n'ont rien à voir avec l'autorisation.

---

## 4. Statut

**Aucun test de ce document n'a été exécuté.** Aucun tag `@QAIA-PERF-<NNN>` ni
`@QAIA-SEC-<NNN>` n'est émis : les deux skills exigent que le rapport ne porte que des nombres
réellement mesurés (`perf-check` l. 76 : « never assert a budget you did not actually
measure »), et un tag sur un run inexistant serait la première ligne fausse du dossier.

Ce qui **a** été observé — dans les limites du visiteur ordinaire, S5 seulement — est en
`31-perf-secu-observations.md`.
