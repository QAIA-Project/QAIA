# Campagne de recherche de défauts — Uptime Kuma 2.5.0

**Date** : 2026-08-11
**Cible** : `louislam/uptime-kuma`, tag `2.5.0`, commit `d9a60dfc73140d15111752e4e8910ed4b54bd9a3`
(publié le 2026-08-01, dernière release au jour de la campagne)
**Environnement** : Windows 11 (10.0.26200.8973), Node v24.13.0, npm 11.6.2, pas de Docker.
**Instance** : auto-hébergée, `http://127.0.0.1:3001`, SQLite, `DATA_DIR=C:/uk-eval/data`.
**Cible surveillée** : un serveur HTTP local écrit pour la campagne (`probe/target.js`,
`http://127.0.0.1:3999`), pilotable à la demande (200 / 500 / lenteur / silence / chaîne de
redirections / corps de taille arbitraire). **Aucun moniteur n'a jamais pointé vers un service
que nous ne possédons pas.**

## 1. Installation — passée

```
git clone --depth 1 --branch 2.5.0 https://github.com/louislam/uptime-kuma.git
npm ci            # 1257 paquets, 30 s, aucune erreur
npm run build     # vite, dist/ produit
HOST=127.0.0.1 PORT=3001 DATA_DIR=... UPTIME_KUMA_DB_TYPE=sqlite node server/server.js
```

`package.json` exige `node >= 20.4.0` ; Node 24.13 passe sans avertissement.
Un seul point de friction, non bloquant : au premier démarrage le serveur s'arrête sur l'écran
« Setup Database » qui attend une action dans le navigateur. `UPTIME_KUMA_DB_TYPE=sqlite` permet de
le franchir sans interface graphique. Le compte administrateur est ensuite créé par l'événement
socket.io `setup` (voir `probe/kuma.js`).

## 2. L'oracle

La documentation, jamais le code : le wiki du projet
(`Maintenance`, `Internal API`, `Badge`, `Status Page`) et les libellés du formulaire de moniteur,
qui sont la documentation que l'utilisateur a réellement sous les yeux
(`src/lang/en.json` — `retriesDescription`, `timeoutAfter`, `resendEveryXTimes`,
`maxRedirectDescription`, `responseMaxLengthDescription`, `upsideDownModeDescription`,
`keywordDescription`, `retryOnlyOnStatusCodeFailureDescription`, `needPushEvery`).
Le code n'a servi qu'à savoir **où observer** (quel événement socket porte quelle valeur), jamais à
décider ce qui était correct.

## 3. Promesses éprouvées

| # | Promesse (source) | Sondes | Verdict |
|---|---|---|---|
| 1 | `retriesDescription` : « Maximum retries before the service is marked as down » | `p1` (N=0, N=2) | conforme |
| 2 | `retryCheckEverySecond` : « Retry every {0} seconds » | `p1` (interval 60 / retry 20) | conforme |
| 3 | `timeoutAfter` : « Timeout after {0} seconds » | `p2` (5 s, 12 s) | conforme (écart 0,02 s) |
| 4 | `acceptedStatusCodesDescription` | `p3` (4 cas) | conforme |
| 5 | `upsideDownModeDescription` | `p3` (2 cas) | conforme |
| 6 | `keywordDescription` (« The search is case-sensitive ») + `invertKeywordDescription` | `p3` (4 cas) | conforme |
| 7 | `resendEveryXTimes` : « Resend every {0} times » | `p4` (N=2, 7 battements) | conforme |
| 8 | wiki *Maintenance* : stratégies manual / single, effet sur les moniteurs, fuseau | `p5` (6 cas) | conforme |
| 9 | `maxRedirectDescription` : « Set to 0 to disable redirects » | `p6A` (5 cas) | conforme |
| 10 | `responseMaxLengthDescription` : « Set to 0 for unlimited » | `p6B`, `p7` (×2) | **écart confirmé (D-1)** |
| 11 | `retryOnlyOnStatusCodeFailureDescription` | `p8` (4 cas) | conforme |
| 12 | statut page — « Alphanumerical string and hyphens only » | `p9` (11 slugs) | conforme |
| 13 | wiki *Internal API* — `/api/push` : défauts, erreurs, `ping` en float | `p10` | conforme |
| 14 | `needPushEvery` : « call this URL every {0} seconds » | `p10` | conforme (DOWN à +21 s pour 20 s) |
| 15 | wiki *Maintenance* — « Recurring - Interval » : la fenêtre s'ouvre à l'heure dite | `p12`, `p13`, `p14`, `p15` | **écart confirmé (D-2)** |

Soit **15 promesses éprouvées**, 13 conformes, 2 écarts confirmés et reproduits.

### Promesses NON éprouvées, et pourquoi

- **Calcul de disponibilité (24 h / 30 j / 1 an)** : aucune définition écrite (pondération par la
  durée des battements ? traitement de PENDING et de MAINTENANCE ?). Sans définition publiée, tout
  écart mesuré aurait été une opinion, pas un défaut. Écarté délibérément.
- **Badges `/api/badge/...`** : nécessitent qu'un moniteur soit rendu public par une page de statut
  publiée ; monté mais non mené jusqu'aux valeurs numériques, faute de temps.
- **Cache des pages de statut (« cache results for 5 minutes »)** : vérifié seulement au niveau du
  routage (`cache("5 minutes")` sur `/status/:slug`, `cache("1 minutes")` sur
  `/api/status-page/heartbeat/:slug`) — non éprouvé en exécution.
- **Stratégies `cron`, `recurring-weekday`, `recurring-day-of-month`** : non éprouvées.
- **Types de moniteur non-HTTP** (TCP, ping, DNS, Steam, Docker, MQTT, SNMP) : hors périmètre d'un
  montage entièrement local sans Docker.
- **Notifications** : seul le transport `webhook` a servi, comme instrument de mesure.

## 4. Écarts

### D-1 — `responseMaxLength = 0` : « unlimited » stocke zéro caractère — CONFIRMÉ, REPRODUIT 3×

**Promesse.** Le formulaire de moniteur, sous le champ *Response Max Length*, affiche :
« Maximum size of response data to store. **Set to 0 for unlimited.** Larger responses will be
truncated. Default: 1024 (1KB) ». Le champ est un `<input type="number" min="0">` : 0 est une
valeur que le formulaire invite explicitement à saisir.

**Observé.** Avec `responseMaxLength = 0`, la réponse stockée n'est pas illimitée : elle est vide.
Le corps est remplacé par la seule marque de troncature.

```
DIFF responseMaxLength=0, body 10 chars     attendu 10 caractères, obtenu 0   raw="... (truncated)"
DIFF responseMaxLength=0, body 5000 chars   attendu 5000 caractères, obtenu 0 raw="... (truncated)"
OK   responseMaxLength=1024, body 10 chars  attendu 10, obtenu 10             raw="xxxxxxxxxx"
```

Reproduit à l'identique en 3 exécutions (`p6-run1`, `p7-run1`, `p7-run2`). Le contrôle à 1024 et à
100 tronque correctement — seule la valeur documentée comme « illimitée » détruit la donnée.

**Portée.** La réponse stockée ressort par les gabarits personnalisés de notification
(c'est le seul chemin de sortie : `monitor.js` la décode uniquement pour `sendNotification`). Un
utilisateur qui suit le libellé pour « ne rien tronquer » obtient l'inverse exact de ce qu'il
demande, silencieusement, et sur **toutes** les tailles de réponse, pas seulement les grandes.

**Antériorité cherchée, non trouvée** : `responseMaxLength+unlimited`, `response_max_length+0`,
`Maximum+size+of+response+data+truncated`, `responseMaxLength` — 4 requêtes sur l'API de recherche
GitHub du dépôt. Les seuls résultats sont les PR qui ont introduit la fonctionnalité (#6192, #6684,
#6691) et une demande d'évolution (#6852). Aucun signalement de cette valeur limite.

**Rejeu** : `node probe/p7-responsezero.js`

### D-2 — Maintenance récurrente : la première occurrence est sautée quand la plage de validité commence le jour même — CONFIRMÉ, REPRODUIT 2× + contrôle positif

**Promesse.** Wiki *Maintenance* : la stratégie « Recurring - Interval » planifie une fenêtre
quotidienne ; pendant la fenêtre, « affected monitors display in blue on the Dashboard and status
pages ». Le formulaire demande deux choses distinctes : une **plage de validité** (*Effective Date
Range*, `dateRange`) et une **plage horaire quotidienne** (`timeRange`).

**Observé.** Une maintenance récurrente dont la plage de validité commence **aujourd'hui** ne
s'ouvre pas à sa première occurrence du jour. Elle reste `scheduled`, les moniteurs restent UP,
et la fenêtre ne s'ouvrira que le lendemain.

A/B côte à côte, même plage horaire quotidienne (14:55), créés à 14:52 (`p14`) :

```
                                       A: validité depuis aujourd'hui 14:22
                                       B: validité depuis hier       14:22
  +2.7min 14:54:46  A: scheduled/UP           B: scheduled/UP
  +3.0min 14:55:06  A: scheduled/UP           B: under-maintenance/MAINTENANCE
  +3.7min 14:55:47  A: scheduled/UP           B: under-maintenance/MAINTENANCE
```

Le journal serveur ne montre qu'un seul démarrage à l'instant exact :
`14:55:00 [MAINTENANCE] INFO: Maintenance id: 19 is under maintenance now` — celui de B.
La configuration A avait déjà échoué à l'identique dans `p13` (fenêtre 14:50, observée jusqu'à
14:53:46, jamais ouverte).

**Mécanisme, isolé du produit** (`p15`). `server/model/maintenance.js` construit le job ainsi :

```js
const startDate = dayjs(this.startDate);              // début de la plage de validité
const startDateTime = startDate.hour(hour).minute(minute);   // + heure de la fenêtre
this.beanMeta.job = new Cron(this.cron, { timezone, startAt: startDateTime.toISOString() }, ...)
```

Quand la plage de validité commence le jour même, `startAt` tombe **exactement** sur la première
occurrence, et croner 8.1.2 (la version embarquée) traite la borne comme stricte :

```
plage de validité commençant AUJOURD'HUI  startAt=2026-08-11T14:55:00  nextRun=Wed Aug 12 2026 14:55:00
plage de validité commençant HIER          startAt=2026-08-10T14:55:00  nextRun=Tue Aug 11 2026 14:55:00
```

**Portée.** C'est le chemin par défaut du formulaire : à la création, `EditMaintenance.vue`
initialise `dateRange` à `[maintenant, maintenant + 1 h]`. Un utilisateur qui programme ce matin une
fenêtre pour ce soir obtient une maintenance qui ne s'ouvrira pas ce soir — sans message d'erreur,
avec un statut affiché « Scheduled » qui laisse croire que tout est en place. Les notifications ne
sont donc pas suspendues pendant l'intervention.

**Antériorité cherchée, non trouvée.** 8 requêtes sur l'API de recherche GitHub du dépôt
(`recurring+interval+maintenance+first+occurrence`, `maintenance+startAt`,
`maintenance+recurring+skips+first`, `maintenance+only+starts+next+day`,
`recurring-interval+maintenance`, `maintenance+effective+date+range`, `maintenance+does+not+start`,
`maintenance+window+today+not+active`). Le voisinage est fourni et déjà corrigé plusieurs fois —
#4738, #4939 (introduction de `startAt`), #5872/#5903/#5914 (décalage d'une minute par jour),
#6118 — mais aucun de ces tickets ne décrit la première occurrence sautée. Les correctifs successifs
sur ce même `startAt` renforcent l'intérêt du signalement plutôt qu'ils ne l'annulent.

**Rejeu** : `node probe/p14-recurring-startat.js` (≈ 9 min, A/B) et
`node probe/p15-croner-startat.js` (instantané, mécanisme isolé).

## 5. Non établi

- **Statut `unknown` renvoyé par l'événement socket `getMaintenance`.** Ce gestionnaire recharge la
  ligne depuis la base (`R.findOne`) au lieu d'utiliser le bean en mémoire ; le `beanMeta` du bean
  frais est vide, donc toute maintenance `cron`/`recurring-*` y est rapportée « unknown »
  (`p11`, `p12`). L'interface n'utilise cet événement que pour pré-remplir le formulaire d'édition
  et n'y lit pas le statut — la liste, elle, passe par `maintenanceList` et affiche le bon état
  (`p13`). Sans effet visible pour l'utilisateur : non retenu. **C'est aussi le piège qui a failli
  me faire signaler un faux défaut** : les deux premières sondes mesuraient le mauvais canal.
- **Slug de page de statut en majuscules.** `ProbeE` est accepté. C'est conforme à
  « Alphanumerical string and hyphens only » (les majuscules sont alphanumériques) ; l'attente
  inverse de la sonde était fausse. Reste ouverte, non éprouvée, la question de la collision entre
  deux slugs ne différant que par la casse.
- **`msg` de `/api/push` sans limite effective.** Le wiki annonce « Max length approx. 250 chars » ;
  10 000 caractères sont acceptés et stockés intégralement, sans erreur ni troncature. Le mot
  « approx. » rend la promesse indécidable : c'est une recommandation, pas une borne. Signalé ici
  comme ambiguïté de documentation, pas comme défaut.
- **Erreur SQL brute renvoyée au client.** Un `add` de moniteur sans champ `conditions` renvoie au
  client le texte complet de la requête `INSERT` et le message `SQLITE_CONSTRAINT`. L'API socket.io
  est interne et non documentée comme surface publique ; non retenu.

## 6. Comportement documenté (donc non-défaut) rencontré en chemin

- **`timeout = 0` produit un délai d'expiration de ~13 h** (`this.timeout = this.interval * 1000 *
  0.8` mélange secondes et millisecondes). Trouvé en lisant le code, **déjà signalé** : issue
  #7656, ouverte le 2026-08-01, toujours ouverte, toujours présente en 2.5.0. Non re-signalé.
  L'antériorité a été vérifiée avant toute exécution de sonde sur ce point.
- Fuseau horaire des fenêtres de maintenance : une plage exprimée en UTC alors que le serveur est
  en UTC+2 est correctement classée « scheduled » et non « under-maintenance » (`p5`).

## 7. Rejouer la campagne

```bash
# 1. instance Uptime Kuma locale (voir §1)
# 2. cible contrôlée
node probe/target.js                 # 127.0.0.1:3999

# 3. sondes (chacune crée puis supprime ses moniteurs)
node probe/p1-retries.js 2 60 20     # retries + retryInterval
node probe/p2-timeout.js 5           # timeout
node probe/p3-semantics.js           # codes acceptés, upside down, keyword
node probe/p4-resend.js 2 7          # resendInterval, via webhook local
node probe/p5-maintenance.js         # maintenance manual / single / fuseau
node probe/p6-boundaries.js          # maxredirects + responseMaxLength
node probe/p7-responsezero.js        # D-1, reproduction ciblée
node probe/p8-retryonly.js           # retryOnlyOnStatusCodeFailure
node probe/p9-slug.js                # validation des slugs
node probe/p10-push.js               # moniteur push
node probe/p11-recurring.js          # maintenance récurrente (canal getMaintenance — voir §5)
node probe/p12-recurring-fires.js    # ouverture effective d'une fenêtre récurrente
node probe/p13-recurring-instrumented.js  # idem, canal maintenanceList (le bon)
node probe/p14-recurring-startat.js  # D-2, A/B décisif
node probe/p15-croner-startat.js     # D-2, mécanisme isolé du produit
```

Variables : `UK_DIR` (dépôt cloné, pour `socket.io-client`), `KUMA_URL`, `KUMA_USER`, `KUMA_PASS`,
`TARGET_URL`. Transcriptions brutes dans `evidence.txt`.
