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

**13 conditions `[req-neg]`** — toutes de niveau `api`, donc toutes à couvrir par un scénario
`@api` (ADR 0001 × ADR 0008). Un scénario d'interface montrant un message d'erreur ne les
acquitterait pas.

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
- **Q3 — `security` déclarée, `403` jamais déclaré.** Le jeton insuffisant en portée n'a pas de
  code de réponse. **Contradiction classe 3.** Aucune condition n'est dérivée : inventer un `403`
  que le contrat ne promet pas serait précisément ce que `references/api-steps.md` interdit.

## Ce que cette conception ne couvre pas

Les treize autres chemins du document Petstore-like d'origine n'existent pas ici : la
spécification est un **extrait** d'une seule opération, et elle le dit. La couverture est complète
**pour la clause ingérée**, pas pour une API de réservation en général.
