# Ligne de base — US et critères d'acceptation écrits SANS les skills QAIA

**Date : 2026-08-11.** Ce document est la **moitié témoin** d'une expérience en deux temps :

1. *(ce fichier)* trois cibles réelles observées, et les user stories + critères d'acceptation
   qu'on en tire **sans ouvrir une seule skill du dépôt** — pas de parcours `.qaia/`, pas de
   technique ISTQB nommée, pas d'étiquette, pas de Gherkin. Juste ce qu'un professionnel écrit
   après avoir regardé le produit ;
2. *(fichier suivant)* un testeur qui **utilise les skills** sur les mêmes cibles et sur les
   critères ci-dessous.

**Ce que l'expérience peut prouver** : ce que les skills ajoutent, retirent ou contredisent par
rapport à une rédaction ordinaire. **Ce qu'elle ne peut pas prouver** : que le résultat serait le
même avec quelqu'un d'autre à la place. Les deux moitiés sortent de la même partie — c'est la
limite, elle est écrite ici et non en note de bas de page.

## Périmètre d'observation, et ce que je me suis interdit

| Cible | Nature | Ce qui a été fait | Ce qui a été refusé |
|---|---|---|---|
| `saucedemo.com` | banc d'entraînement fourni par Sauce Labs pour l'automatisation | navigation complète, connexion, panier, tunnel de commande | rien à refuser : c'est sa raison d'être |
| `restful-booker.herokuapp.com` | *« playground API »*, annoncée comme telle par sa propre documentation | lecture, authentification, une création | aucune suppression, aucune modification d'une réservation existante |
| `alpes-envol.fr` | **site réel d'une collectivité** (aérodrome de Gap-Tallard, Hautes-Alpes) | **lecture de pages publiques uniquement** | aucun formulaire soumis, aucune charge, aucun test de sécurité, aucun envoi |

La troisième ligne est la seule qui demandait un arbitrage. Un site public se lit comme un
visiteur le lit ; il ne se sonde pas. Les critères que j'en tire portent donc sur ce qu'un
visiteur constate, pas sur ce qu'un testeur mandaté vérifierait.

*Note : la demande disait « aeroportgap ». Aucun site de ce nom ne répond (`aeroport-gap.fr`,
`aeroportgap.fr` : injoignables). `alpes-envol.fr` est le site désigné comme officiel par l'Union
des Aéroports Français pour cet aérodrome. Hypothèse, pas certitude.*

---

# Cible 1 — Swag Labs (saucedemo.com)

## Ce qui a été observé, littéralement

La page de connexion **affiche elle-même** six noms d'utilisateur et le mot de passe commun :
`standard_user`, `locked_out_user`, `problem_user`, `performance_glitch_user`, `error_user`,
`visual_user`, mot de passe `secret_sauce`. Trois messages d'erreur relevés au caractère près :

- champs vides → `Epic sadface: Username is required`
- mauvais couple → `Epic sadface: Username and password do not match any user in this service`
- utilisateur verrouillé → `Epic sadface: Sorry, this user has been locked out.`

Catalogue : 6 articles, tri à 4 options (`Name (A to Z)`, `Name (Z to A)`, `Price (low to high)`,
`Price (high to low)`). Bouton **Add to cart** qui devient **Remove**, pastille de panier
incrémentée. Tunnel : trois champs obligatoires refusés **un à un** (`First Name is required`,
puis `Last Name is required`, puis `Postal Code is required`), récapitulatif
`Item total: $29.99 · Tax: $2.40 · Total: $32.39`, confirmation `Thank you for your order!`.

## US-SD-01 — Se connecter à la boutique

> **En tant que** client de Swag Labs, **je veux** me connecter avec mes identifiants,
> **afin de** voir le catalogue et passer commande.

| # | Critère d'acceptation |
|---|---|
| AC1 | Un couple identifiant/mot de passe valide ouvre la page catalogue. |
| AC2 | Un identifiant absent est refusé **avant** toute autre vérification, avec un message qui nomme le champ manquant. |
| AC3 | Un mot de passe absent est refusé avec un message qui nomme le champ manquant. |
| AC4 | Un couple inconnu est refusé **sans révéler lequel des deux est faux**. |
| AC5 | Un compte verrouillé est refusé avec un message qui dit que le compte est verrouillé, et non que les identifiants sont faux. |
| AC6 | Après un refus, l'identifiant saisi reste affiché et le mot de passe est vidé. |
| AC7 | La page catalogue n'est pas accessible sans être connecté. |

**Points que je note en écrivant, et que je ne tranche pas :**
- AC4 et AC5 sont **en tension**. AC4 demande de ne rien révéler ; AC5 révèle qu'un compte existe
  et qu'il est verrouillé. C'est un arbitrage sécurité contre ergonomie qui appartient au produit.
- AC6 est une **supposition de ma part** : je ne l'ai pas vérifiée.
- La page publie les identifiants valides. Sur un vrai produit ce serait un défaut majeur ; ici
  c'est la fonction du banc d'essai. **Un critère ne doit pas être écrit contre ça.**

## US-SD-02 — Composer un panier

> **En tant que** client connecté, **je veux** ajouter et retirer des articles,
> **afin de** ne commander que ce que j'ai choisi.

| # | Critère d'acceptation |
|---|---|
| AC1 | Ajouter un article incrémente la pastille du panier de 1. |
| AC2 | Le bouton d'un article ajouté devient **Remove**. |
| AC3 | Retirer un article décrémente la pastille ; à zéro, la pastille disparaît. |
| AC4 | Le panier contient exactement les articles ajoutés, avec leur libellé et leur prix identiques à ceux du catalogue. |
| AC5 | Le contenu du panier survit à une navigation vers une fiche article et retour. |
| AC6 | Le tri du catalogue ne modifie pas le contenu du panier. |

## US-SD-03 — Passer commande

> **En tant que** client avec un panier, **je veux** finaliser ma commande,
> **afin de** recevoir les articles.

| # | Critère d'acceptation |
|---|---|
| AC1 | Les trois champs prénom, nom et code postal sont obligatoires. |
| AC2 | Chaque champ manquant est signalé par un message qui le nomme. |
| AC3 | Le récapitulatif affiche le sous-total des articles, la taxe et le total. |
| AC4 | **Le total est la somme du sous-total et de la taxe.** |
| AC5 | **La taxe vaut 8 % du sous-total**, arrondie au centime. |
| AC6 | Confirmer la commande affiche un message de confirmation et vide le panier. |
| AC7 | Un panier vide ne permet pas d'atteindre la confirmation. |

**AC5 est la seule règle que j'ai eu à *déduire*, et c'est celle où je peux me tromper.** Observé :
`$29.99` → taxe `$2.40`. 2,40 / 29,99 = 8,003 %. J'écris donc « 8 % arrondi au centime ». Une
seule observation ne distingue pas 8 % d'un barème par tranche qui donnerait le même résultat sur
cette valeur. **C'est une hypothèse, pas un constat**, et il faudrait deux autres montants pour
la confirmer. Je l'écris comme critère parce qu'un critère faux et visible vaut mieux qu'une
absence de critère — mais il est signalé.

AC7 est également non vérifié : je n'ai pas essayé.

---

# Cible 2 — restful-booker (API)

## Ce qui a été observé, et ce que la documentation en dit

| Appel | Observé | Documenté |
|---|---|---|
| `POST /auth`, identifiants corrects | **200** + `{"token":"…"}` | 200 + token |
| `POST /auth`, mauvais mot de passe | **200** + `{"reason":"Bad credentials"}` | *aucun code d'échec documenté* |
| `GET /booking` | 200 + liste d'identifiants | documenté |
| `GET /booking/999999` | 404 | **rien** ⚠ |
| `POST /booking`, corps valide | **200** + l'objet créé | documenté « Success 200 » |
| `POST /booking`, corps `{}` | **500** | *rien* |
| `PUT /booking/2` sans jeton | 403 | jeton exigé, **code jamais documenté** ⚠ |
| `DELETE /booking/1` sans jeton | 403 | jeton exigé, **code jamais documenté** ⚠ |
| `GET /ping` | **201** | `Success 200` **dont l'exemple montre `201 Created`** ⚠ |

> **⚠ Trois cellules de ce tableau étaient fausses, et c'est la moitié « avec skills » qui l'a
> établi.** Corrigées le 2026-08-11 après vérification dans la source gelée
> (`sources/api_data.json`) : **les huit opérations documentées ne déclarent AUCUN code d'erreur**
> — que des blocs `Success 200`. Le 404 et le 403 ne sont donc documentés nulle part, alors que
> j'écrivais « documenté ». À l'inverse, le 201 de `/ping` que je donnais pour non documenté l'est
> — dans l'*exemple* du bloc, qui contredit son propre en-tête `Success 200`.
>
> **J'ai mélangé la promesse et le fait dans les deux sens.** C'est précisément la règle que
> `openapi-ingest` énonce en tête (*« une spécification est une promesse, pas un fait »*) et que
> je n'ai pas appliquée faute de l'avoir lue. C'est le résultat le plus net de l'expérience, et
> il est à la charge de cette moitié-ci.

## US-RB-01 — Obtenir un jeton d'accès

> **En tant que** client de l'API, **je veux** obtenir un jeton,
> **afin de** modifier ou supprimer une réservation.

| # | Critère d'acceptation |
|---|---|
| AC1 | Des identifiants valides renvoient un jeton exploitable. |
| AC2 | Des identifiants invalides **ne** renvoient **pas** de jeton. |
| AC3 | Un échec d'authentification est **distinguable d'un succès par le seul code de statut**. |

**AC3 est écrit en sachant qu'il échoue.** Le service renvoie **200** dans les deux cas ; seule la
forme du corps change. Un client qui teste `response.ok` traite une authentification refusée
comme réussie. Je l'écris comme critère parce que c'est ce qu'un client a le droit d'attendre, et
je note à côté que **le produit ne le respecte pas aujourd'hui** — c'est un défaut candidat, pas
une erreur de rédaction.

## US-RB-02 — Créer une réservation

> **En tant que** client de l'API, **je veux** créer une réservation,
> **afin qu'**elle soit enregistrée et relisible.

| # | Critère d'acceptation |
|---|---|
| AC1 | Un corps complet crée la réservation et renvoie son identifiant. |
| AC2 | La réservation créée est relisible à `GET /booking/{id}` avec les mêmes valeurs. |
| AC3 | Un corps incomplet est **refusé par une erreur client (4xx)**, jamais par une erreur serveur. |
| AC4 | Le refus nomme ce qui manque. |
| AC5 | Une création renvoie **201**, conformément à la sémantique HTTP. |

**AC3 et AC5 échouent l'un et l'autre aujourd'hui** : corps vide → **500**, création → **200**.
Le 500 est le plus grave des deux : *« le serveur ne peut pas traiter votre requête »* pour une
requête que le client a mal formée, c'est une faute reportée sur le mauvais acteur — et un 5xx
déclenche des alertes, des relances automatiques et des astreintes qui n'ont pas lieu d'être.

Le 200 au lieu du 201, en revanche, est **discutable** : la documentation écrit « Success 200 »,
donc le service **tient sa promesse**. Mon AC5 mesure la sémantique HTTP, pas le contrat publié.
Je le garde en le disant, parce que c'est exactement le genre de critère qu'un relecteur doit
pouvoir refuser.

## US-RB-03 — Protéger les opérations destructrices

> **En tant qu'**exploitant du service, **je veux** que modification et suppression exigent un
> jeton, **afin qu'**un client anonyme ne puisse pas altérer des réservations.

| # | Critère d'acceptation |
|---|---|
| AC1 | `PUT` sans jeton est refusé. |
| AC2 | `DELETE` sans jeton est refusé. |
| AC3 | `PUT`/`DELETE` avec un jeton invalide sont refusés de la même façon qu'avec aucun jeton. |
| AC4 | Un refus d'autorisation ne modifie rien. |

AC3 et AC4 ne sont **pas vérifiés** : le premier demanderait de forger un jeton, le second de
relire une ressource après une tentative — et j'ai décidé de ne rien modifier sur ce service.

---

# Cible 3 — alpes-envol.fr (site de l'aérodrome de Gap-Tallard)

## Ce qui a été observé

Navigation : `Webcam`, `Annuaire`, `Album`, `Cadre Institutionnel`. La page d'accueil oriente vers
quatre aérodromes (Gap-Tallard, St Crépin, Aspres sur Buëch, Serres-La Bâtie *privé*), un annuaire
d'entreprises par catégories avec des compteurs, une liste de prestataires de loisirs avec leurs
compteurs (parachutisme 9, parapente 11, ULM 9, planeur 7…), et deux offres du Département
(locations sur aérodromes, offres d'emploi). Aucun formulaire, aucun tarif, aucun horaire sur
l'accueil. Accroche : *« Venez exploiter le Ciel des Hautes-Alpes »*.

## US-AE-01 — Trouver un prestataire d'activité aérienne

> **En tant que** visiteur qui veut faire un baptême de l'air dans les Hautes-Alpes,
> **je veux** trouver qui le propose et où, **afin de** le contacter.

| # | Critère d'acceptation |
|---|---|
| AC1 | Depuis l'accueil, une activité mène en un clic à la liste de ses prestataires. |
| AC2 | Chaque prestataire affiche au minimum un nom et un moyen de contact. |
| AC3 | Le compteur annoncé à côté d'une activité **est le nombre d'entrées réellement listées**. |
| AC4 | Un prestataire rattaché à un aérodrome indique lequel. |
| AC5 | Aucun lien de la navigation principale ne mène à une page absente. |

**AC3 est le seul critère qui vaut vraiment le déplacement.** Un compteur affiché à côté d'une
liste est une promesse chiffrée, c'est le genre d'écart que personne ne remarque, et il se vérifie
sans rien envoyer au serveur. Les autres sont honnêtes mais banals.

## US-AE-02 — Consulter les conditions avant de venir

> **En tant que** pilote ou visiteur, **je veux** connaître l'état du terrain avant de me
> déplacer, **afin de** ne pas venir pour rien.

| # | Critère d'acceptation |
|---|---|
| AC1 | La webcam est atteignable depuis la navigation principale. |
| AC2 | L'image de la webcam est datée, ou son défaut de fraîcheur est annoncé. |
| AC3 | Le cadre institutionnel indique qui exploite le site et comment le contacter. |

**AC2 est le critère le plus utile des deux stories, et le plus fragile.** Une webcam qui affiche
une image d'hier sans le dire est pire qu'une webcam en panne. Je ne l'ai **pas vérifié** : je
n'ai pas ouvert la page.

---

# Ce que cette moitié témoin vaut, dit franchement

**Ce qu'elle a produit** : 8 user stories, **35 critères d'acceptation**, et **6 anomalies
candidates** trouvées en observant — dont quatre sur l'API (200 sur échec d'authentification,
500 sur corps invalide, 200 sur création, 201 sur un *health check*).

**Ses trois faiblesses, que je connais en l'écrivant :**

1. **Je n'ai vérifié qu'une partie de ce que j'affirme.** AC6 de US-SD-01, AC7 de US-SD-03, AC3 et
   AC4 de US-RB-03, tout US-AE-02 : écrits par raisonnement, pas par observation. Rien ne les
   distingue visuellement des critères observés — un lecteur les prendra tous pour des constats.
2. **Aucune couverture systématique.** J'ai écrit ce qui m'est venu en regardant. Personne ne peut
   dire ce qui manque, parce qu'il n'y a aucune méthode derrière à laquelle comparer le résultat.
   Les bornes, les combinaisons de règles, les états intermédiaires : rien ne garantit qu'ils sont
   là, et pour une raison simple — je ne les ai pas cherchés dans un ordre.
3. **Aucune trace.** Aucun critère ne dit d'où il vient ni ce qui le justifie. Dans trois mois,
   personne ne saura si AC5 de US-SD-03 vient d'une observation, d'un calcul ou d'une habitude.

**C'est exactement ce que la seconde moitié doit être capable de reprocher à celle-ci.** Si elle
ne le fait pas, c'est le dispositif qui est en cause, pas ce document.
