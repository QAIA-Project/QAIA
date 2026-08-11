---
stepsCompleted: [openapi-ingest, istqb-design]
lastStep: istqb-design
lastSaved: 2026-08-11
---

# 03-design — conditions derived from the booking API contract

**Source** : `sources/booking-api.openapi.yaml`, sha256
`009c4ecd20f7c5e2c632b4c34c8bd7bae8f0f45ad50dd2b06b8d5ce6f3795d27`, 1 421 octets, gelée le
2026-08-11. Le document lui-même date du **2026-07-25** (`ec0529e`) : il précède de dix-sept jours
le serveur qui l'implémente, et **aucune condition ci-dessous n'a été dérivée du code**.

Opération unique : `createAppointment` — `POST /api/appointments`.

## Niveau (ADR 0008)

**Toutes les conditions sont `[level: api]`.** Chacune repose sur une clause du contrat de
service, observable en HTTP sans navigateur : c'est le critère d'ADR 0004 rendu opérationnel par
ADR 0008. Aucune n'a été remontée en `e2e` — cette spécification ne décrit aucun écran, et en
inventer un aurait été inventer la promesse.

## Conditions

| # | Condition | Clause du contrat | Technique | `[req-neg]` |
|---|---|---|---|---|
| C1 | Une requête valide crée le rendez-vous | `createAppointment · responses.201` | ep | — |
| C2 | Requête sans jeton refusée | `createAppointment · security` → `responses.401` | ep | **oui** |
| C3 | Requête avec jeton invalide refusée | `createAppointment · security` → `responses.401` | ep | **oui** |
| C4 | Chaque champ requis, omis à son tour, est refusé | `AppointmentCreate.required` → `responses.400` | ep | **oui** |
| C5 | Chaque valeur de l'énumération est acceptée | `AppointmentCreate.specialty.enum` | ep | — |
| C6 | Une valeur hors énumération est refusée | `AppointmentCreate.specialty.enum` → `responses.400` | ep | **oui** |
| C7 | Une propriété non déclarée est refusée | `AppointmentCreate.additionalProperties: false` → `responses.400` | ep | **oui** |
| C8 | Une note de 280 caractères est acceptée | `AppointmentCreate.note.maxLength` | boundary | — |
| C9 | Une note de 281 caractères est refusée | `AppointmentCreate.note.maxLength` → `responses.400` | boundary | **oui** |
| C10 | Un `startsAt` non conforme au format est refusé | `AppointmentCreate.startsAt.format` → `responses.400` | ep | **oui** |
| C11 | Un champ du mauvais type est refusé | `AppointmentCreate.slotId.type` → `responses.400` | ep | **oui** |
| C12 | Un créneau déjà pris est refusé | `createAppointment · responses.409` | ep | **oui** |
| C13 | Un patient au plafond de rendez-vous à venir est refusé | `createAppointment · responses.422` | boundary | **oui** |
| C14 | Un patient sous le plafond est accepté | `createAppointment · responses.422` | boundary | — |
| C15 | Un créneau à moins de deux heures est refusé | `createAppointment · responses.422` | boundary | **oui** |
| C16 | Un créneau à exactement deux heures est accepté | `createAppointment · responses.422` | boundary | — |
| C17 | Un identifiant conforme au format UUID est accepté | `AppointmentCreate.slotId.format` | ep | — |
| C18 | Un identifiant non conforme au format UUID est refusé | `AppointmentCreate.slotId.format` → `responses.400` | ep | **oui** |
| C19 | Une requête sans corps est refusée | `createAppointment · requestBody.required: true` → `responses.400` | ep | **oui** |

**Le dénominateur de la porte ADR 0001, reconstitué explicitement.** La table ci-dessus porte
**13 lignes marquées `oui`** ; le compte du manifeste est **15**, et l'écart n'était écrit nulle
part — un dénominateur de porte qu'il faut deviner n'est pas un dénominateur *(relevé le
2026-08-11)*. La reconstitution :

> 13 lignes `[req-neg]`, moins C4 qui compte pour **3** (chaque champ requis omis à son tour est
> une condition de refus distincte, per la table de dérivation d'`openapi-ingest`), soit
> 13 − 1 + 3 = **15**.

Toutes de niveau `api`, donc toutes à couvrir par un scénario `@api` (ADR 0001 × ADR 0008). Un
scénario d'interface montrant un message d'erreur ne les acquitterait pas.

**C19 avait été oubliée.** `requestBody: required: true` est une règle qui refuse, déclarée au
niveau de l'opération, et elle n'avait jamais été énumérée — la porte lisait donc vert au-dessus
d'une règle de refus que personne n'avait comptée. C'est exactement le mécanisme qu'ADR 0008
décrit dans son contexte, et il s'est reproduit ici. **Une porte n'est jamais meilleure que son
énumération.**

## Questions ouvertes — les contradictions de la spécification

Aucune n'est tranchée ici. Chacune donne un scénario écrit sur le **défaut sûr proposé**, marqué
`@low-confidence` avec son `# open: Qn`, conformément à `testbook-generate`.

- **Q1 — la règle métier n'existe que dans une prose de description.** Le `422` est décrit
  « Business rule violated (e.g. > 3 upcoming, < 2h ahead) » ; le schéma ne porte ni compteur ni
  contrainte de délai. **Contradiction classe 4 d'`openapi-ingest`** : une machine ne lit que le
  schéma, donc rien n'impose ces règles. *Défaut sûr appliqué : « plus de 3 à venir » signifie
  qu'un patient en ayant déjà 3 voit le quatrième refusé.* Le « e.g. » dit par ailleurs que la
  liste n'est pas exhaustive — d'autres règles métier peuvent exister, non testables.
- **Q2 — `startsAt` est optionnel, la règle des deux heures en dépend.** Le schéma ne le rend pas
  requis. Que se passe-t-il quand il est absent ? *Défaut sûr appliqué : aucune règle de délai ne
  s'applique, la création réussit.*
- **Q4 — `format` est-il normatif ?** *(ajoutée le 2026-08-11, après relecture — son absence
  rendait le cahier contradictoire avec lui-même.)* Le schéma déclare `slotId` et `patientId` en
  `format: uuid`, et `startsAt` en `format: date-time`. Le cahier traitait `date-time` comme
  **contraignant** (C10 attend un 400) et `uuid` comme **décoratif** — les données du chemin
  nominal étaient `"S1"` et `"P1"`, qui ne sont pas des UUID, et six scénarios affirmaient **201**
  sur un corps que leur propre source déclare non conforme. Le même mot-clé, dans le même schéma,
  lu dans deux sens opposés sans une ligne pour le dire.
  *Défaut sûr appliqué, et il est imposé par la doctrine plutôt que choisi : la table de
  dérivation d'`openapi-ingest` dit `pattern`, `format` → « one conforming, one not ». `format`
  est donc tenu pour **normatif**, les deux conditions sont dérivées (C17, C18), et les données du
  chemin nominal deviennent de vrais UUID.*
- **Q3 — `security` déclarée, `403` jamais déclaré.** Le jeton insuffisant en portée n'a pas de
  code de réponse. **Contradiction classe 3.** Aucune condition n'est dérivée : inventer un `403`
  que le contrat ne promet pas serait précisément ce que `references/api-steps.md` interdit.

## Ce que cette conception ne couvre pas

Les treize autres chemins du document Petstore-like d'origine n'existent pas ici : la
spécification est un **extrait** d'une seule opération, et elle le dit. La couverture est complète
**pour la clause ingérée**, pas pour une API de réservation en général.
