# Tracabilite — campagne reverse-engineering 2026-08-11

Genere **depuis `junit.xml`**, jamais a la main : chaque ligne de resultat vient du run
reel (self-review D9 — un rapport ne doit rien affirmer que le code ne porte pas).

| Scenario | AC | Projet | Test | Resultat |
|---|---|---|---|---|
| `@QAIA-SD-001` | @AC1 | e2e.saucedemo.spec.js | Un couple valide ouvre la page catalogue | **PASS** |
| `@QAIA-SD-002` | @AC2 | e2e.saucedemo.spec.js | Un identifiant absent est refuse par un message qui nomme le champ | **PASS** |
| `@QAIA-SD-003` | @AC3 | e2e.saucedemo.spec.js | Un mot de passe absent est refuse par un message qui nomme le champ | **PASS** |
| `@QAIA-SD-004` | @AC4 | e2e.saucedemo.spec.js | Un couple inconnu est refuse sans reveler lequel des deux est faux | **PASS** |
| `@QAIA-SD-005` | @AC5 | e2e.saucedemo.spec.js | Un compte verrouille est refuse par un message de verrouillage, pas de mauvais identifiants | **PASS** |
| `@QAIA-SD-006` | @AC6 | e2e.saucedemo.spec.js | Apres un refus, l identifiant reste affiche et le mot de passe est vide | **FAIL** |
| `@QAIA-SD-007` | @AC7 | e2e.saucedemo.spec.js | La page catalogue n est pas accessible sans etre connecte | **PASS** |
| `@QAIA-SD-008` | @AC1 | e2e.saucedemo.spec.js | Ajouter un article incremente la pastille du panier de 1 | **PASS** |
| `@QAIA-SD-009` | @AC2 | e2e.saucedemo.spec.js | Le bouton d un article ajoute devient Remove | **PASS** |
| `@QAIA-SD-010` | @AC3 | e2e.saucedemo.spec.js | Retirer un article decremente la pastille et a zero elle disparait | **PASS** |
| `@QAIA-SD-011` | @AC4 | e2e.saucedemo.spec.js | Le panier contient exactement les articles ajoutes, libelle et prix identiques au catalogue | **PASS** |
| `@QAIA-SD-012` | @AC5 | e2e.saucedemo.spec.js | Le contenu du panier survit a un aller-retour vers une fiche article | **PASS** |
| `@QAIA-SD-013` | @AC6 | e2e.saucedemo.spec.js | Le tri du catalogue ne modifie pas le contenu du panier | **PASS** |
| `@QAIA-SD-014` | @AC1,@AC2 | e2e.saucedemo.spec.js | Le champ firstName est obligatoire et son absence est nommee | **PASS** |
| `@QAIA-SD-015` | @AC1,@AC2 | e2e.saucedemo.spec.js | Le champ lastName est obligatoire et son absence est nommee | **PASS** |
| `@QAIA-SD-016` | @AC1,@AC2 | e2e.saucedemo.spec.js | Le champ postalCode est obligatoire et son absence est nommee | **PASS** |
| `@QAIA-SD-017` | @AC3 | e2e.saucedemo.spec.js | Le recapitulatif affiche sous-total, taxe et total | **PASS** |
| `@QAIA-SD-018` | @AC4 | e2e.saucedemo.spec.js | Le total est la somme du sous-total et de la taxe | **PASS** |
| `@QAIA-SD-019` | @AC5 | e2e.saucedemo.spec.js | La taxe vaut 8 % du sous-total arrondi au centime | **PASS** |
| `@QAIA-SD-020` | @AC6 | e2e.saucedemo.spec.js | Confirmer la commande affiche une confirmation et vide le panier | **PASS** |
| `@QAIA-SD-021` | @AC7 | e2e.saucedemo.spec.js | Un panier vide ne permet pas d atteindre la confirmation | **FAIL** |
| `@QAIA-RB-001` | @AC1 | api.restfulbooker.spec.js | Des justificatifs valides renvoient un jeton | **PASS** |
| `@QAIA-RB-002` | @AC2 | api.restfulbooker.spec.js | Des justificatifs dont "password" est errone ne renvoient aucun jeton | **PASS** |
| `@QAIA-RB-002` | @AC2 | api.restfulbooker.spec.js | Des justificatifs dont "username" est errone ne renvoient aucun jeton | **PASS** |
| `@QAIA-RB-003` | @AC2 | api.restfulbooker.spec.js | Le champ "username" omis du corps d authentification est refuse | **FAIL** |
| `@QAIA-RB-003` | @AC2 | api.restfulbooker.spec.js | Le champ "password" omis du corps d authentification est refuse | **FAIL** |
| `@QAIA-RB-004` | @AC3 | api.restfulbooker.spec.js | Le statut d une authentification refusee differe de celui d un succes | **FAIL** |
| `@QAIA-RB-005` | @AC1 | api.restfulbooker.spec.js | Un corps complet cree la reservation et renvoie son identifiant | **PASS** |
| `@QAIA-RB-006` | @AC1 | api.restfulbooker.spec.js | Une reservation se cree sans aucun justificatif | **PASS** |
| `@QAIA-RB-007` | @AC2 | api.restfulbooker.spec.js | Une reservation creee est relisible avec les memes valeurs metier | **PASS** |
| `@QAIA-RB-008` | @AC3 | api.restfulbooker.spec.js | Omettre le champ obligatoire "firstname" a la creation est refuse | **FAIL** |
| `@QAIA-RB-008` | @AC3 | api.restfulbooker.spec.js | Omettre le champ obligatoire "lastname" a la creation est refuse | **FAIL** |
| `@QAIA-RB-008` | @AC3 | api.restfulbooker.spec.js | Omettre le champ obligatoire "totalprice" a la creation est refuse | **FAIL** |
| `@QAIA-RB-008` | @AC3 | api.restfulbooker.spec.js | Omettre le champ obligatoire "depositpaid" a la creation est refuse | **FAIL** |
| `@QAIA-RB-008` | @AC3 | api.restfulbooker.spec.js | Omettre le champ obligatoire "bookingdates.checkin" a la creation est refuse | **FAIL** |
| `@QAIA-RB-008` | @AC3 | api.restfulbooker.spec.js | Omettre le champ obligatoire "bookingdates.checkout" a la creation est refuse | **FAIL** |
| `@QAIA-RB-008` | @AC3 | api.restfulbooker.spec.js | Omettre le champ obligatoire "additionalneeds" a la creation est refuse | **FAIL** |
| `@QAIA-RB-009` | @AC3 | api.restfulbooker.spec.js | Un corps de creation vide est refuse | **FAIL** |
| `@QAIA-RB-010` | @AC3 | api.restfulbooker.spec.js | Le champ "totalprice" envoye dans un type non declare est refuse | **FAIL** |
| `@QAIA-RB-010` | @AC3 | api.restfulbooker.spec.js | Le champ "depositpaid" envoye dans un type non declare est refuse | **FAIL** |
| `@QAIA-RB-011` | @AC3 | api.restfulbooker.spec.js | Une date de check-in hors du format CCYY-MM-DD est refusee | **FAIL** |
| `@QAIA-RB-012` | @AC5 | api.restfulbooker.spec.js | Le statut declare d une creation est 200 | **PASS** |
| `@QAIA-RB-013` | @AC6 | api.restfulbooker.spec.js | Une creation en XML renvoie une reponse XML | **FAIL** |
| `@QAIA-RB-014` | @AC6 | api.restfulbooker.spec.js | Un type de contenu non supporte est refuse sans erreur serveur | **FAIL** |
| `@QAIA-RB-015` | @AC7 | api.restfulbooker.spec.js | Un totalprice de 0, hors du domaine metier, est refuse | **FAIL** |
| `@QAIA-RB-015` | @AC7 | api.restfulbooker.spec.js | Un totalprice de -1, hors du domaine metier, est refuse | **FAIL** |
| `@QAIA-RB-016` | @AC1,@AC2,@AC3 | api.restfulbooker.spec.js | Un PUT sans justificatif est refuse | **PASS** |
| `@QAIA-RB-016` | @AC1,@AC2,@AC3 | api.restfulbooker.spec.js | Un PATCH sans justificatif est refuse | **PASS** |
| `@QAIA-RB-016` | @AC1,@AC2,@AC3 | api.restfulbooker.spec.js | Un DELETE sans justificatif est refuse | **PASS** |
| `@QAIA-RB-017` | @AC3 | api.restfulbooker.spec.js | Un PUT avec un jeton inconnu est refuse comme sans justificatif | **PASS** |
| `@QAIA-RB-017` | @AC3 | api.restfulbooker.spec.js | Un PATCH avec un jeton inconnu est refuse comme sans justificatif | **PASS** |
| `@QAIA-RB-017` | @AC3 | api.restfulbooker.spec.js | Un DELETE avec un jeton inconnu est refuse comme sans justificatif | **PASS** |
| `@QAIA-RB-018` | @AC4 | api.restfulbooker.spec.js | Une modification refusee laisse la reservation inchangee | **PASS** |
| `@QAIA-RB-019` | @AC5 | api.restfulbooker.spec.js | Une modification totale portant le jeton en cookie est acceptee | **PASS** |
| `@QAIA-RB-020` | @AC5 | api.restfulbooker.spec.js | Une modification totale portant une authentification Basic est acceptee | **PASS** |
| `@QAIA-RB-021` | @AC6 | api.restfulbooker.spec.js | Une modification totale amputee d un champ obligatoire est refusee | **PASS** |
| `@QAIA-RB-022` | @AC7 | api.restfulbooker.spec.js | Une modification partielle ne touche que le champ envoye | **PASS** |
| `@QAIA-RB-023` | @AC7 | api.restfulbooker.spec.js | Une modification partielle a corps vide laisse la reservation inchangee | **PASS** |
| `@QAIA-RB-024` | @AC8 | api.restfulbooker.spec.js | La suppression authentifiee d une reservation creee par le test renvoie 201 | **PASS** |
| `@QAIA-RB-025` | @AC8 | api.restfulbooker.spec.js | Une reservation supprimee n est plus lisible | **PASS** |
| `@QAIA-RB-026` | @AC1 | api.restfulbooker.spec.js | La liste sans filtre renvoie des identifiants de reservation | **PASS** |
| `@QAIA-RB-027` | @AC2 | api.restfulbooker.spec.js | Le filtre declare "firstname" restreint la liste | **PASS** |
| `@QAIA-RB-027` | @AC2 | api.restfulbooker.spec.js | Le filtre declare "lastname" restreint la liste | **PASS** |
| `@QAIA-RB-027` | @AC2 | api.restfulbooker.spec.js | Le filtre declare "checkin" restreint la liste | **FAIL** |
| `@QAIA-RB-027` | @AC2 | api.restfulbooker.spec.js | Le filtre declare "checkout" restreint la liste | **PASS** |
| `@QAIA-RB-028` | @AC2 | api.restfulbooker.spec.js | Les quatre filtres combines restreignent la liste conjointement | **FAIL** |
| `@QAIA-RB-029` | @AC3 | api.restfulbooker.spec.js | Un filtre de check-in egal a la date de la reservation l inclut | **FAIL** |
| `@QAIA-RB-030` | @AC3 | api.restfulbooker.spec.js | Un filtre de date hors du format CCYY-MM-DD est refuse | **FAIL** |
| `@QAIA-RB-031` | @AC4 | api.restfulbooker.spec.js | Un filtre sans correspondance renvoie un tableau vide | **PASS** |
| `@QAIA-RB-032` | @AC5 | api.restfulbooker.spec.js | Un parametre de requete inconnu est ignore | **PASS** |
| `@QAIA-RB-033` | @AC1 | api.restfulbooker.spec.js | Une lecture par identifiant renvoie les champs declares | **PASS** |
| `@QAIA-RB-034` | @AC2 | api.restfulbooker.spec.js | Une lecture sur un identifiant inexistant est refusee | **PASS** |
| `@QAIA-RB-035` | @AC3 | api.restfulbooker.spec.js | Une lecture sur un identifiant non numerique est refusee | **PASS** |
| `@QAIA-RB-036` | @AC4 | api.restfulbooker.spec.js | Une lecture demandant du XML renvoie un document XML | **PASS** |
| `@QAIA-RB-037` | @AC1 | api.restfulbooker.spec.js | Le controle de sante renvoie le statut promis par son exemple | **PASS** |
| `@QAIA-RB-038` | @AC2 | api.restfulbooker.spec.js | Une methode non declaree sur un chemin valide est refusee comme telle | **FAIL** |

**Total : 76 tests — 51 passes, 25 echoues, 0 bloque, 0 ignore.**
