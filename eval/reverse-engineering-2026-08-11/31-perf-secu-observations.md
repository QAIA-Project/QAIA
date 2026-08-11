---
stepsCompleted: [security-surface/S5]
lastStep: 31-observations
lastSaved: 2026-08-11
scope: passive-visitor-only
---

# 31 — Ce qu'une requête ordinaire révèle déjà

**Date : 2026-08-11.** Ce document ne contient **que des faits observés**, chacun accompagné de
la requête qui le produit. Il ne contient aucune extrapolation. Là où une conclusion tentante
dépasse la preuve, la limite est écrite à l'endroit de la tentation, pas en note finale.

## Périmètre de ce qui a été émis

Un seul protocole des six de `security-surface` a été exécuté : **S5 — en-têtes et TLS**, le
seul réalisable sans mandat (voir `30-perf-secu-conception.md` §1.2). **Zéro test de
performance** : aucune boucle, aucun k6, aucune requête concurrente.

Comptage exact du trafic émis, sur ~2 minutes :

| Cible | Requêtes HTTP | Poignées de main TLS |
|---|---|---|
| `www.saucedemo.com` | 3 (`GET https://` ×2, `GET http://` ×1) | 2 |
| `restful-booker.herokuapp.com` | 4 (`GET https:// /` ×2, `GET /booking` ×1, `GET http://` ×1) | 2 |
| `www.alpes-envol.fr` | 4 (`GET https://` ×3, `GET http://` ×1) | 2 |
| **Total** | **11** | **6** |

Uniquement des `GET` sur des ressources publiques, aucune écriture, aucun formulaire soumis,
aucun identifiant envoyé, aucune requête sur un chemin inexistant. **Aucune réponse d'erreur
n'a été provoquée** : la consigne disait « gestion des erreurs observée sans la provoquer », et
même un `GET` sur une page absente aurait été un déclenchement délibéré. Les erreurs analysées
en §5 sont **réutilisées** de la ligne de base et n'ont pas été rejouées.

---

## 1. En-têtes de sécurité — présence et valeur

Requête type :

```bash
curl -sS -D - -o /dev/null "https://<cible>/"
```

Légende : **✅** présent avec valeur exploitable · **⚠** présent, valeur à discuter ·
**❌** absent de la réponse observée.

| En-tête | `saucedemo.com` | `restful-booker` (`/` et `/booking`) | `alpes-envol.fr` |
|---|---|---|---|
| `Content-Security-Policy` | ❌ | ❌ | ❌ |
| `Strict-Transport-Security` | ❌ | ❌ | ❌ |
| `X-Content-Type-Options` | ❌ | ❌ | ❌ |
| `X-Frame-Options` | ❌ | ❌ | ⚠ `sameorigin` |
| `Referrer-Policy` | ❌ | ❌ | ❌ |
| `Permissions-Policy` | ❌ | ❌ | ❌ |

**Un seul en-tête de sécurité sur dix-huit cases.** `protocols.md#s5` prévient : « The usual
mis-run. Asserting the header *exists*. » Le piège ne s'est pas présenté — il n'y a
essentiellement rien à évaluer.

Le seul présent, `X-Frame-Options: sameorigin` sur alpes-envol, est **valide** : la valeur est
insensible à la casse par la RFC 7034, `sameorigin` interdit bien le cadrage par un tiers. Le ⚠
porte sur autre chose : `X-Frame-Options` est obsolète au profit de `frame-ancestors` en CSP, et
aucune CSP n'est servie. La protection anti-clickjacking existe donc, dans sa forme héritée
seulement.

`restful-booker` a été vérifié sur **deux** points d'entrée conformément à `#s5` (« one `GET` on
the main document, one on an API endpoint […] the API one is usually the bare one »). Résultat :
les deux sont également nus. La mise en garde de la skill ne se vérifie pas ici, faute d'écart.

---

## 2. Cookies

```bash
curl -sS -D - -o /dev/null "https://www.alpes-envol.fr/"
```

**`saucedemo.com` et `restful-booker` : aucun `Set-Cookie`** dans les réponses observées. Rien à
évaluer — et rien à conclure sur les cookies posés *après* connexion, que je n'ai pas déclenchée.

**`alpes-envol.fr`** — un unique `Set-Cookie` observé :

```
Set-Cookie: current_cart_id=deleted; expires=Thu, 01 Jan 1970 00:00:01 GMT; Max-Age=0; path=/; domain=www.alpes-envol.fr
```

| Attribut | Présent ? |
|---|---|
| `Secure` | ❌ |
| `HttpOnly` | ❌ |
| `SameSite` | ❌ |

**La limite de ce constat, et elle est décisive.** Ce cookie est une **directive de
suppression** (`Max-Age=0`, `expires` en 1970), pas un cookie de session en cours d'attribution.
Ce que la preuve établit exactement :

- ✅ **Établi** : l'application émet des directives de cookie **sans** `Secure`, `HttpOnly` ni
  `SameSite`, et elle gère un identifiant de panier nommé `current_cart_id`.
- ❌ **Non établi** : que le cookie de panier *réel*, posé lors d'une session d'achat, manque de
  ces attributs. Je n'ai pas ouvert de session d'achat.

L'inférence est plausible — la suppression est en général émise par le même code que la pose —
mais **plausible n'est pas observé**. Écrire « le cookie de panier est vulnérable au vol par
XSS » serait inventer une vulnérabilité à partir d'un cookie vide. Le constat qui tient est :
**il faut vérifier**, et c'est un `GET` sur la boutique qui le dirait — hors périmètre ici faute
de mandat sur un site de collectivité.

---

## 3. TLS et certificats

```bash
echo | openssl s_client -connect <hôte>:443 -servername <hôte>
```

| Cible | Protocole négocié | Chiffrement | Émetteur | Validité | Verdict |
|---|---|---|---|---|---|
| `saucedemo.com` | **TLS 1.3** | `TLS_AES_128_GCM_SHA256` | Let's Encrypt (YR2) | 30 juin → 28 sept. 2026 | ✅ valide |
| `restful-booker` | **TLS 1.2** | `ECDHE-RSA-AES128-GCM-SHA256` | Amazon RSA 2048 M01 (`*.herokuapp.com`) | 1ᵉʳ janv. 2026 → 29 janv. 2027 | ✅ valide |
| `alpes-envol.fr` | **TLS 1.2** | `ECDHE-RSA-AES256-GCM-SHA384` | Let's Encrypt (YR1) | 3 juil. → 1ᵉʳ oct. 2026 | ✅ valide |

**Les trois certificats sont valides, non expirés, correctement émis pour leur nom, et les trois
suites négociées offrent la confidentialité persistante (ECDHE) et un chiffrement authentifié
(GCM). Aucun problème.** C'est un résultat, et il est bon.

**Ce qui n'a pas été testé, et ne doit donc pas être déduit** : je n'ai pas cherché à savoir si
TLS 1.0/1.1 ou des suites faibles restent *acceptés* — cela demande une série de poignées de main
délibérément dégradées, c'est-à-dire un sondage de configuration. « TLS 1.2 négocié par défaut »
ne dit **rien** sur ce que le serveur accepterait d'un client plus faible.

---

## 4. HTTP en clair, et l'absence d'HSTS

```bash
curl -sS -D - -o /dev/null "http://<cible>/"
```

| Cible | Réponse en clair | HSTS |
|---|---|---|
| `saucedemo.com` | `301` → `https://www.saucedemo.com/` | ❌ |
| `alpes-envol.fr` | `301` → `https://www.alpes-envol.fr/` | ❌ |
| **`restful-booker`** | **`200 OK` — le site est servi en clair, aucune redirection** | ❌ |

**C'est le constat le plus net de la campagne.** Sur les deux premières cibles, l'absence de HSTS
est partiellement compensée par une redirection permanente : reste la fenêtre de la toute
première visite (`SSL stripping`), que HSTS existe précisément pour fermer, et qu'un préchargement
fermerait complètement.

Sur `restful-booker`, il n'y a pas de compensation du tout : **l'API répond en HTTP non chiffré**.
Conséquence directe et vérifiable dans la documentation de l'API — `POST /auth` transporte
`username` et `password` dans le corps de la requête. Un client qui vise l'URL en `http://`
transmet donc **des identifiants en clair**, et rien côté serveur ne l'en empêche ni ne le
signale.

**Bornage.** Je n'ai **pas** envoyé d'identifiants en clair pour le prouver : ce serait exécuter
l'attaque. Ce qui est établi est la condition qui la rend possible — le serveur répond `200` en
clair au lieu de rediriger. Et le contexte plafonne la gravité : les identifiants de ce bac à
sable sont **publiés dans sa propre documentation** (`admin`/`password123`). Il n'y a pas de
secret à intercepter. Le défaut est réel et sa conséquence pratique est nulle **sur cette
instance** ; il serait Élevé sur la même application self-hostée avec de vrais comptes.

---

## 5. Divulgation de la pile technique

| Cible | En-têtes observés | Ce qui est divulgué |
|---|---|---|
| `saucedemo.com` | `Server: GitHub.com`, `Via: 1.1 varnish`, `X-Served-By: cache-mrs10583-MRS`, `X-Fastly-Request-ID`, `X-GitHub-Request-Id`, `x-github-edge-region: fra` | Hébergement GitHub Pages derrière Fastly. **Aucune version.** Identifiants de cache/région : exploitation offensive nulle |
| `restful-booker` | `Server: Heroku`, **`X-Powered-By: Express`**, `Via: 1.1 heroku-router` | Framework applicatif (Express/Node). **Pas de numéro de version** |
| `alpes-envol.fr` | `Server: Apache`, **`X-Powered-By: PHP/8.3.29`**, `X-EMS-Server: 162` | **Version mineure exacte de PHP.** `X-EMS-Server: 162` semble un identifiant d'instance interne dans une flotte |

Le `Link` de préchargement d'alpes-envol expose en outre des versions de bibliothèques front :

```
</medias/static/themes/bootstrap_v4/js/jquery-3.6.3.min.js?v=26012023>; rel="preload"; as="script"
```

→ **jQuery 3.6.3**, **Bootstrap 4**, et deux préconnexions vers `fonts.googleapis.com` /
`fonts.gstatic.com`.

**Bornage, à tenir fermement.** Divulguer une version **n'est pas** une vulnérabilité, et
`protocols.md#s5` le classe correctement : « Also report, **as an information leak rather than a
missing control**. » Ce que ces en-têtes changent réellement : ils dispensent un attaquant du
travail d'empreinte, et rendent la cible triable par requête automatisée le jour où une CVE
touche PHP 8.3.x. **Je n'ai vérifié aucune base de CVE et je n'affirme rien sur la vulnérabilité
de PHP 8.3.29, de jQuery 3.6.3 ni de Bootstrap 4.** Le constat est la divulgation, pas
l'exploitabilité.

Deux observations de moindre portée, notées pour complétude :

- `saucedemo.com` répond `Access-Control-Allow-Origin: *` sur le document racine. Sur une
  ressource statique publique sans cookie ni authentification, c'est **sans conséquence** — ce
  n'est un problème que si des données sensibles ou des identifiants transitent, ce qui n'est pas
  le cas ici.
- `restful-booker` émet `Nel` / `Report-To` / `Reporting-Endpoints` pointant vers
  `nel.heroku.com` : télémétrie réseau standard de la plateforme Heroku, pas une configuration
  applicative.

---

## 6. Analyse sécurité des comportements d'API déjà observés

Ces quatre faits proviennent de la ligne de base. **Ils n'ont pas été rejoués.** Ils sont ici
lus sous l'angle sécurité, ce qui n'avait pas été fait.

### 6.1 `POST /auth` avec un mauvais mot de passe → **200** + `{"reason":"Bad credentials"}`

Une authentification qui **échoue** avec un code de **succès**.

Ce que ça vaut, concrètement :

1. **Tout contrôle qui s'appuie sur le code de statut est aveugle.** Limiteur de débit,
   détection de bourrage d'identifiants, WAF, alerte sur taux de 4xx, tableau de bord
   d'exploitation : tous comptent des `401`. Ici il n'y en a aucun. **Mille échecs de connexion
   et mille succès sont indiscernables** pour toute la chaîne d'observabilité. Le défaut n'est
   pas le confort du client d'API, c'est que la détection d'attaque repose sur un signal que le
   serveur n'émet jamais.
2. **Le code client s'y trompe.** `if (response.ok)` en `fetch`, `raise_for_status()` en
   `requests`, `expect(res.status).toBe(200)` en test : trois façons courantes de conclure que la
   connexion a réussi. Il faut inspecter le corps pour connaître le verdict, ce que la seule
   lecture du statut ne suggère à personne.
3. Réponse correcte attendue : `401` avec un en-tête `WWW-Authenticate`.

**Ce que ce fait n'établit PAS.** Il ne prouve **aucune** énumération d'utilisateurs. Pour cela
il faudrait comparer *utilisateur inexistant* et *mot de passe erroné* sur corps, statut **et**
temps (`protocols.md#s4`) — trois cas, ~20 fois chacun. **Non fait, hors mandat.** Le message
`"Bad credentials"` est d'ailleurs générique, ce qui est le bon comportement sur le canal du
message ; les canaux statut et temporel restent non mesurés.

### 6.2 `POST /booking` avec un corps `{}` → **500**

C'est le cas **S3-c** (champ requis manquant) de `protocols.md#s3`, dont le résultat attendu est
« a clean 4xx (400 or 422) […] **Never 5xx** ». La skill qualifie elle-même ce résultat :

> A 5xx here is a genuine finding (unhandled exception, availability risk, and usually an
> information leak in the error body) — report it with its severity rather than as a flaky test.

Ce qu'un `500` sur entrée malformée dit du traitement des erreurs : **la validation d'entrée
n'existe pas en amont de la logique métier.** Le corps vide n'est pas rejeté par un contrôle de
schéma ; il progresse jusqu'à ce qu'un accès à une propriété absente lève une exception non
rattrapée. Autrement dit, l'API n'a pas de frontière de validation — elle a un
`try/catch` implicite au niveau du framework, ou rien.

**Ce qu'il pourrait divulguer — et le mot « pourrait » est la limite.** Express, sans
`NODE_ENV=production`, renvoie par défaut la **trace d'appel complète** dans le corps de l'erreur :
chemins de fichiers absolus sur le serveur, arborescence du projet, versions des modules de la
pile d'appel, et parfois des fragments de requête SQL. **Je n'ai pas observé le corps de ce 500.**
La ligne de base a enregistré le statut, pas la charge utile. Donc :

- ✅ **Établi** : `500` sur `{}`, absence de validation d'entrée, risque de disponibilité.
- ❓ **Hypothèse explicitement étiquetée** : divulgation d'une trace dans le corps. Un seul `GET`
  du corps de cette réponse trancherait — **non fait**, parce que cela suppose de reprovoquer
  l'erreur.

Le lien avec §5 est direct : `X-Powered-By: Express` confirme le framework qui a ce comportement
par défaut.

### 6.3 `PUT` / `DELETE` sans jeton → **403**

C'est le cas **S1-a** de `protocols.md#s1`, et il **passe sur le fond** : l'écriture non
authentifiée est refusée. C'est le résultat le plus rassurant du lot.

Deux réserves, dans l'ordre d'importance :

1. **S1-a est le cas qui ne prouve presque rien**, et la skill le dit explicitement :
   > The usual mis-run. Testing only S1-a. A missing token is rejected by any framework's default
   > middleware; S1-c and S1-d are what tell you the signature and expiry are actually verified
   > […]. An API that accepts any well-formed JWT passes S1-a perfectly.

   **S1-b (jeton malformé), S1-c (expiré), S1-d (signé avec la mauvaise clé) n'ont pas été
   testés.** Le résultat correct pour S1 est donc **`blocked`, pas `pass`** — un quart de la
   preuve n'est pas la preuve.
2. Le code attendu est **401**, pas 403 : 403 signifie « authentifié mais interdit », alors que
   l'appelant n'est pas authentifié du tout. Écart sémantique, **Informationnel**.

### 6.4 `GET /ping` → **201**

`201 Created` sur une sonde de vie qui ne crée rien. Aucune conséquence de sécurité en soi.

**L'intérêt est ailleurs, et c'est le constat de synthèse de cette section.** Rapprochés,
§6.1 (échec d'auth → 200), §6.3 (non-authentifié → 403) et §6.4 (sonde → 201) dessinent le
**même défaut de fond** : sur cette API, **les codes de statut HTTP sont décoratifs**. Ils ne
sont pas choisis selon leur sémantique.

La portée sécurité de cette généralisation est concrète : toute défense périmétrique — limiteur
de débit, WAF, règle de corrélation SIEM, alerte, sonde de disponibilité — raisonne sur des
classes de statut. Sur une API où `200` peut signifier un échec d'authentification et `201` un
simple *ping*, **ces défenses lisent un signal faux**, et elles le lisent silencieusement. C'est
plus lourd que chacun des trois écarts pris isolément, et c'est invisible tant qu'on les examine
un par un.

---

## 7. Classement par risque — sévérité **bornée par la preuve**

Règle appliquée : la sévérité reflète ce qui est **démontré**, pas ce qui est redouté. La
colonne « plafond » nomme ce qui empêche de monter d'un cran.

| # | Constat | Cible | Preuve | Sévérité | Ce qui plafonne la sévérité |
|---|---|---|---|---|---|
| 1 | API servie en **HTTP clair**, sans redirection ni HSTS, alors que `POST /auth` transporte des identifiants | restful-booker | `curl http://…` → `200 OK` (§4) | **Moyenne** | Identifiants **publics** par conception (bac à sable). Aucun secret réel exposé. Élevée si self-hostée avec de vrais comptes |
| 2 | `500` sur corps `{}` — aucune validation d'entrée | restful-booker | ligne de base, §6.2 | **Moyenne** | Le corps du `500` **n'a pas été observé** : la divulgation de trace reste une hypothèse. Sans elle, il reste un risque de disponibilité |
| 3 | Échec d'authentification renvoyé en `200` → détection d'attaque aveugle | restful-booker | ligne de base, §6.1 | **Moyenne** | Aucune énumération **démontrée**. L'impact est sur l'observabilité, pas sur une compromission établie |
| 4 | Cookie émis sans `Secure`/`HttpOnly`/`SameSite`, sur un site marchand de collectivité | alpes-envol | `Set-Cookie` observé (§2) | **Faible-à-Moyenne** | Le cookie observé est une **suppression**, pas une session. Passe à Élevée **si** le cookie de panier réel présente les mêmes attributs — **non vérifié** |
| 5 | Aucun en-tête de sécurité (CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`) | les 3 | §1 | **Faible** | Défense en profondeur absente. **Aucune faille d'injection n'a été établie** — sans XSS démontrée, l'absence de CSP est une protection manquante, pas une brèche ouverte |
| 6 | Divulgation de version : `PHP/8.3.29`, jQuery 3.6.3, Bootstrap 4, `X-EMS-Server: 162` | alpes-envol | §5 | **Faible** | Fuite d'information, pas vulnérabilité. **Aucune CVE consultée**, aucune exploitabilité vérifiée |
| 7 | `X-Powered-By: Express` sans version | restful-booker | §5 | **Informationnelle** | Framework seul, sans version : gain quasi nul pour un attaquant |
| 8 | `403` au lieu de `401` sur écriture non authentifiée | restful-booker | ligne de base, §6.3 | **Informationnelle** | Le contrôle **fonctionne** ; seul le code est sémantiquement inexact |
| 9 | `201` sur `GET /ping` | restful-booker | ligne de base, §6.4 | **Informationnelle** | Aucun impact isolé — compte comme symptôme du point 3 |
| 10 | `Access-Control-Allow-Origin: *` sur le document | saucedemo | §5 | **Aucune** | Ressource statique publique, sans cookie ni authentification. Rien à protéger |

### Ce qui n'a **rien** donné, et c'est un résultat

- **Les trois certificats TLS sont valides et correctement configurés** (§3). Aucun défaut.
- **`saucedemo.com` ne présente aucun constat de gravité non nulle.** C'était prévisible — c'est
  un site statique sur GitHub Pages dont les identifiants sont affichés à l'écran — mais la
  prévision n'est pas l'observation, et l'observation confirme : rien à signaler.
- **Aucune vulnérabilité n'a été établie sur aucune des trois cibles.** Rien dans ce document ne
  décrit une faille exploitée, ni même une faille démontrée : le plus haut classement atteint est
  Moyen, sur des défauts de configuration et de traitement d'erreur.

### Ce qui reste indéterminé — et le mandat qu'il faudrait

| Question ouverte | Ce qui la trancherait | Mandat, et auprès de qui |
|---|---|---|
| Le corps du `500` contient-il une trace d'appel ? | Lire le corps d'une réponse d'erreur | Autorisation de provoquer l'erreur — mainteneur de restful-booker, **ou** self-host Docker (déjà autorisé par le catalogue) |
| Y a-t-il une énumération d'utilisateurs ? | S4 : 3 cas × ~20 essais, comparaison corps/statut/temps | Autorisation explicite : 60 tentatives de connexion sont un bourrage d'identifiants vu de la victime |
| La signature et l'expiration des jetons sont-elles vérifiées ? | S1-b/c/d | Idem — ces cas fabriquent des jetons contrefaits |
| Y a-t-il de l'IDOR ? | S2 avec deux comptes réels | Deux comptes + autorisation d'écriture/suppression. **Et** sur restful-booker le modèle n'a pas de propriétaire : le test est *vide de sens*, pas seulement interdit |
| Le cookie de panier d'alpes-envol porte-t-il `HttpOnly`/`Secure`/`SameSite` ? | Un `GET` sur la boutique, en lecture | **Mandat écrit de la collectivité** (aérodrome de Gap-Tallard / son délégataire) et de l'éditeur du CMS |
| TLS 1.0/1.1 ou des suites faibles sont-ils acceptés ? | Poignées de main délibérément dégradées | Sondage de configuration → mandat sur les trois |
| Quelle est la latence réelle sous charge ? | `perf-check`, un des cinq types | **Interdit sur les trois** (`DEMO-TARGETS.md`). Se fait sur instance self-hostée, où il n'y a personne à qui demander |
