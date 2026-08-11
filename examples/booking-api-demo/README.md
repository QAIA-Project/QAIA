# booking-api-demo — le niveau API, de la clause du contrat au résultat d'exécution

Cette démonstration existe pour une raison précise : jusqu'au 2026-08-11, QAIA produisait des tests
d'API **sans jamais avoir décidé** qu'elle en produisait. Le niveau était deviné par `automate` au
moment d'écrire le code ([ADR 0008](../../docs/adr/0008-test-level-is-a-design-property.md)). Ici, il
est décidé à la conception, porté par le scénario, lu par l'automatisation — et la chaîne entière
est exécutée.

## Ce qui est prouvé, et ce qui ne l'est pas

**Prouvé** : la chaîne *clause du contrat → condition → scénario → test → résultat* tient de bout en
bout, et les assertions ne sont pas décoratives (passe mutation ci-dessous).

**Non prouvé, et il faut le dire d'entrée** : que cette suite trouverait un défaut dans un logiciel
écrit par quelqu'un d'autre. **Le serveur et les tests ont été écrits par la même partie**, le même
jour. Une suite verte dans ces conditions mesure la cohérence interne, pas la capacité à détecter.
Ce que le dépôt possède sur ce terrain vient d'ailleurs — `eval/external-application-2026-08-08/`,
deux défauts réels corrigés en amont chez `typicode/json-server`.

**La seule indépendance réelle ici** : la spécification est **antérieure**. `booking-api.openapi.yaml`
a été écrite le **2026-07-25** (`ec0529e`) pour la démonstration d'`oracle-generate`, dix-sept jours
avant le serveur qui l'implémente. Le cahier a été dérivé de ce document et **jamais du code**.

## Ce qu'il y a dans le dossier

| Fichier | Rôle |
|---|---|
| `sources/booking-api.openapi.yaml` | La spécification, gelée, sha256 `009c4ecd…` |
| `qaia-journey/state/BOOK-API/03-design.md` | 16 conditions, **toutes `[level: api]`**, chacune citant sa clause · 13 `[req-neg]` · 3 questions ouvertes |
| `qaia-journey/testbooks/BOOK-API/appointments.feature` | 16 blocs / **23 cas exécutables**, tous `@api`, chacun avec son `# contract:` |
| `qaia-journey/testbooks/BOOK-API/testbook.en.md` | Le **même cahier en langage naturel**, lisible sans connaître Gherkin — vérifié étape par étape contre le `.feature` |
| `app/server.js` | Le serveur qui implémente la spécification. Aucune dépendance. `node app/server.js` |
| `tests/` | La suite Playwright : **un seul projet `api`, sans moteur de navigateur** |
| `qaia-journey/reports/BOOK-API/manifest.json` | Contrat 1.1 : `design.byLevel` = 0 e2e / 23 api, `execution.byType.api` = 23 |
| `evidence/mutation-run.txt` | La passe mutation, sortie brute conservée |

## Le résultat, mesuré

```
cd tests && npm install && npx playwright test
23 passed (707ms)
```

**Aucun navigateur n'est lancé ni installé.** Le projet `api` est déclaré sans `browserName` et sans
descripteur d'appareil, parce que le niveau du cahier l'impose : un moteur de rendu ne peut pas
changer le résultat d'une requête HTTP. C'est le découpage qu'ADR 0008 rend mécanique.

## La passe mutation — 8 candidates, 7 tuées, 1 survivante analysée

Chaque mutation neutralise **une** clause du contrat dans le serveur ; une suite dont les
assertions portent doit passer au rouge.

| Mutation | Verdict |
|---|---|
| Plafond des rendez-vous à venir : `>=` devient `>` | tuée |
| Borne `maxLength` de la note : 280 devient 281 | tuée |
| Délai minimal : strict devient large | tuée |
| Énumération `specialty` non vérifiée | tuée |
| Authentification désactivée | tuée |
| `additionalProperties: false` ignoré | tuée |
| Conflit de créneau ignoré | tuée |
| Champ requis non vérifié | **survivante — équivalente au contrat** |

La survivante n'est pas un trou. Sur la même requête, serveur muté et serveur intact renvoient le
même statut et nomment le même champ : deux clauses du schéma se recouvrent (un champ absent est
aussi un champ qui n'est pas une chaîne). La seule différence porte sur un champ que la
spécification ne déclare nulle part, et l'asserter serait précisément ce que
[`api-steps.md`](../../plugins/qaia-core/skills/testbook-generate/references/api-steps.md) interdit.
Détail et sorties brutes : `evidence/mutation-run.txt`.

**Compter 8/8 aurait été plus flatteur et faux. Compter 7/8 sans l'analyse aurait signalé un trou
qui n'existe pas.**

## Le rendu en langage naturel, et comment il a été produit

`testbook.en.md` porte les 23 cas — `Préconditions / Action / Résultat attendu`, les étiquettes
traduites en mots (niveau, priorité, technique, chemin de refus, question ouverte), les
`Scenario Outline` éclatés avec leurs valeurs substituées. **Aucun texte d'étape n'est réécrit** :
seul le mot-clé Gherkin est remplacé par un intitulé.

`python eval/tools/check_nl_projection.py` compare les deux fichiers étape par étape et échoue si
une seule diverge. La valeur du contrôle ne se démontre pas sur ce fichier-ci, qui est conforme :
elle se démontre sur `eval/tools/fixtures/nl-projection-red/`, **huit divergences injectées, huit
détectées** — dont une valeur d'`Examples` modifiée d'un caractère, la dérive qu'un relecteur
humain ne verra jamais dans un document de vingt pages.

**Dit franchement** : ce rendu-ci a été produit par un script de session, déterministe, et non par
un modèle suivant le format. En production c'est `testbook-export` qui l'écrit — et c'est
précisément la dérive d'un modèle que le contrôle existe pour attraper. Ce fichier montre le
format et le contrôle ; il ne mesure pas la fidélité d'une génération.

## Les trois questions que la spécification laisse ouvertes

Aucune n'est tranchée par le cahier ; chacune donne un scénario écrit sur un défaut sûr, marqué
`@low-confidence` avec son `# open: Qn`.

1. **La règle métier n'existe que dans une prose de description.** Le `422` dit « Business rule
   violated (e.g. > 3 upcoming, < 2h ahead) » ; le schéma ne porte ni compteur ni délai. Une machine
   ne lit que le schéma — donc rien n'impose ces règles. *(Contradiction classe 4 d'`openapi-ingest`.)*
2. **`startsAt` est optionnel alors que la règle des deux heures en dépend.** Le contrat ne dit pas
   ce qui se passe quand il est absent.
3. **`security` est déclarée, aucun `403` ne l'est.** La portée insuffisante n'a pas de code de
   réponse — **aucune condition n'en est dérivée** : inventer un statut que le contrat ne promet pas
   est interdit.

Le « e.g. » de la première dit par ailleurs que la liste n'est pas exhaustive : d'autres règles
métier peuvent exister, et rien dans ce document ne permet de les tester.
