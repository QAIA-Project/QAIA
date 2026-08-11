---
stepsCompleted: [01-review, 02-understanding, 03-design, 04-priorities]
lastStep: 04-priorities
lastSaved: 2026-08-11
status: pending-validation
---

# Swag Labs — revue d'extraction, ambiguïtés, conception ISTQB et priorités

**Cible** : `https://www.saucedemo.com` — banc d'entraînement Sauce Labs.
**Source ingérée** : `00-BASELINE-sans-skills.md`, section « Cible 1 — Swag Labs » (US-SD-01/02/03,
20 critères d'acceptation).
**Sortie brute des observations** : [`10-saucedemo-02-observations.txt`](10-saucedemo-02-observations.txt)
— toute valeur chiffrée ci-dessous s'y relit (règle 4bis du contrat partagé).
**Base de connaissances** : `.qaia/knowledge/` **absente** pour cette cible → mode dégradé assumé
(règle 8). Aucune règle `BR-KB-nnn` appliquée, `design.knowledgeApplied` = vide. Sur un domaine
e-commerce réel ce vide serait un signal ; ici il dit simplement que rien n'a été capitalisé.

> ⚠ Aucune validation humaine n'est intervenue sur ce document. Les trois points ⚠ VALIDATION
> (`us-review` étape 3, `need-understanding` étape 6, `prioritize` étape 3) sont en
> `pending-validation` : les défauts appliqués sont **enregistrés, pas acceptés** (contrat
> partagé, règle 3). Trois entrées `simulated` dans `openArbitrations[]`.

---

# 1. `us-review` — contrôle d'extraction

L'extraction de la ligne de base est **fidèle en structure** : trois US bien formées, 20 AC
numérotés et stables, les règles métier hors liste AC signalées en prose. Rien n'a été perdu.
Trois écarts, tous produits par l'étape 2 (« montrer l'esprit de diff — dire ce qu'on n'a **pas**
trouvé ») :

| # | Écart | Étape qui le produit |
|---|---|---|
| E1 | Aucun marqueur `[assumption]` **sur l'artefact**. AC6 (US-SD-01), AC5 et AC7 (US-SD-03) sont signalés comme non vérifiés **en prose sous le tableau**, pas dans la ligne du critère. `us-review` étape 1 : « **Mentioning it in prose is not enough**: the marker sits on the artifact itself ». Un lecteur qui lit le tableau seul prend les 20 critères pour 20 constats. | `us-review` §1 |
| E2 | Le catalogue des **six profils utilisateur** est capturé dans « ce qui a été observé » mais n'entre dans **aucun** critère. C'est un élément « présent dans la source, non classable » que l'étape 1 oblige à garder **visible** ; la ligne de base l'a gardé visible et l'a laissé sans suite. | `us-review` §1 (dernier point) |
| E3 | Deux critères sont **intestables tels qu'écrits**. AC4 (US-SD-01) « sans révéler lequel des deux est faux » n'énonce pas l'oracle : révéler à qui, comparé à quoi ? AC1 (US-SD-03) « les trois champs sont obligatoires » n'énonce pas ce que *obligatoire* veut dire (vide ? blanc ? longueur ?). L'étape 2 demande de reproduire l'ambiguïté, pas de la lisser. | `us-review` §2 + guardrail « faithfulness over polish » |

Le compteur de traçabilité est repris tel quel : `AC1..AC7` par US, jamais renumérotés
(guardrail `us-review`). Comme les trois US cohabitent dans un seul fichier `.feature`, chaque
scénario porte en plus une étiquette `@US-SD-0n` — sans elle, `@AC1` désignerait trois critères
différents.

---

# 2. `need-understanding` — chasse aux ambiguïtés

## 2.1 Reformulation

Une boutique de démonstration doit laisser un client s'authentifier, composer un panier depuis un
catalogue de six articles, puis payer en saisissant une adresse de livraison, avec un
récapitulatif chiffré avant confirmation. Le risque principal n'est pas l'indisponibilité mais
**l'écart silencieux entre ce que le client voit et ce qu'il achète** : un prix affiché qui n'est
pas celui facturé, une commande enregistrée sans contenu, une commande enregistrée deux fois.
Second risque, propre à cette cible : l'application **publie six profils dont plusieurs sont
volontairement défectueux**, et rien dans la spécification ne dit lequel des comportements
observés est la règle et lequel est le défaut.

## 2.2 Balayage des catégories de l'étape 2 (aucune n'est laissée muette)

| Catégorie | Résultat |
|---|---|
| Termes et unités non définis | **Q7** — « obligatoire » : vide, ou blanc ? **Q4** — arrondi. |
| Toute durée ou échéance : quelle horloge ? | **Sans objet** : aucun AC ne comporte de durée, d'échéance ni de fraîcheur. La latence de `performance_glitch_user` n'est pas une échéance de la spécification, c'est une propriété d'un profil (voir Q1) — et un budget de latence relève de `qaia-playwright:perf-check`, pas d'ici. |
| Contradictions entre AC | **Q5** — AC4 × AC5 (US-SD-01). **Q3** — AC6 contredit par l'application. **Q2** — AC7 (US-SD-03) contredit par l'application. |
| Comportement manquant (erreurs, états vides, concurrence, permissions) | **Q2** (état vide du panier au paiement), **Q8** (double soumission), **Q9** (persistance de session), **Q10** (Reset App State), **Q11** (accès hors navigateur). |
| Règles de données non spécifiées (formats, arrondis, limites, unicité) | **Q4** (arrondi), **Q7** (format/longueur/jeu de caractères des trois champs), **Q6** (persistance du tri). Le format monétaire est signalé dans la passe différée (`$47.3`, `Item total: $0`). |

## 2.3 Passe adverse par type d'AC (obligatoire — étape 3)

- **Machine à états / cycle de vie** (connexion, panier, tunnel). Ré-entrance : peut-on
  re-confirmer une commande déjà confirmée ? → **oui**, observé (Q8). États terminaux : la page de
  confirmation n'est pas terminale, le retour arrière ramène sur un bouton `Finish` actif.
  Transitions interdites : aucune n'est déclarée par la source — c'est en soi le constat.
- **Auth / jetons / permissions.** Révocation vs expiration : la déconnexion invalide bien la
  session (observé). **Règle d'indiscernabilité sous *tous* les chemins de réponse** : c'est cette
  ligne de la checklist qui a produit Q5 — le message de verrouillage n'apparaît que pour qui
  détient déjà le bon mot de passe, donc l'AC5 ne divulgue rien à un attaquant qui ne sait pas déjà.
  Sans ce point de checklist, la tension AC4/AC5 restait un débat d'opinion ; elle est devenue une
  **table de décision à deux entrées** (identifiants valides ?) × (compte verrouillé ?).
- **Tri / pagination.** Départage à clés égales : deux articles à `$15.99` — quel ordre entre eux,
  et est-il stable d'un tri à l'autre ? Non spécifié → intégré à Q6. Pas de pagination (6 articles,
  une page). Cas dégénéré « le filtre retire 100 % des résultats » : sans objet, aucun filtre.
- **Seuils / quantités.** Inclusif/exclusif : sans objet, aucun seuil. **Arrondi** : Q4. **Unités** :
  devise USD, jamais énoncée par la source. **Horloge de référence** : sans objet.

**Règle dure appliquée** : aucun choix de donnée de test ne contourne un cas indéfini. Le départage
des deux articles à `$15.99` aurait pu être évité en ne prenant qu'un seul d'entre eux ; il est
posé en question (Q6) avant d'être contourné.

## 2.4 Passe d'interaction croisée entre AC (obligatoire — étape 4)

| Paire | Interaction à la borne | Statut |
|---|---|---|
| US-SD-02 AC1/AC3 × US-SD-03 AC7 | Le panier redescendu à zéro (borne basse de AC3) alimente AC7 « un panier vide ne permet pas d'atteindre la confirmation ». | **Q2** — l'observation dit le contraire. |
| US-SD-01 AC1 × US-SD-02 AC4 | Le profil retenu à la connexion change les prix affichés au catalogue (`visual_user`). | **Q1** |
| US-SD-02 AC6 × US-SD-02 AC5 | Le tri appliqué avant une navigation vers la fiche article : le panier survit (AC5), le tri non. | **Q6** |
| US-SD-03 AC6 × US-SD-02 AC1 | La confirmation vide le panier (AC6) ; le retour arrière ré-expose un `Finish` actif sur un panier déjà vidé — une seconde commande à $0. | **Q8** |
| US-SD-01 AC7 × US-SD-02 AC5 | La déconnexion invalide la session mais **conserve le panier** pour la reconnexion suivante. | **Q9** |

## 2.5 Passe de contradiction à trois AC (obligatoire — étape 4a)

Le triplet **règle d'état protégé × règle de portée × règle d'anti-divulgation** existe ici et
n'est pas décidé :

- **US-SD-01 AC5** — état protégé : un compte verrouillé est refusé avec un message qui *dit* qu'il
  est verrouillé ;
- **US-SD-01 AC1** — portée : un couple valide ouvre le catalogue ;
- **US-SD-01 AC4** — anti-divulgation : un couple inconnu est refusé sans révéler lequel des deux
  est faux.

Chacune est claire seule, les paires sont tenables, **seul le triple est indécidé** : que doit
répondre le service à `locked_out_user` + un **mauvais** mot de passe ? AC4 impose le message
générique, AC5 impose le message de verrouillage, et AC1 ne tranche pas puisque le couple n'est pas
valide. L'application répond « générique » — mais rien dans la source ne le dit, et le choix
inverse serait une divulgation d'existence de compte. → **Q5**, jamais un défaut silencieux.

## 2.6 Questions ouvertes

Onze questions. Le contrat borne à « ~10 par passe » ; j'en pose 11 et je le dis plutôt que
d'en couper une pour tenir un chiffre. Une seconde passe est proposée pour les points différés
listés en fin de section.

| ID | Question | Défaut proposé | Classement | Voie de l'arbre 5a |
|---|---|---|---|---|
| **Q1** | La page publie six profils. `problem_user`, `error_user`, `visual_user` sont-ils des **profils d'injection de défauts spécifiés** (fonction du banc d'essai) ou des **défauts** ? Toute anomalie observée sous ces profils n'est un constat que si la réponse est « défauts ». | aucun | **`[open]`** | §4 — décision produit, aucun défaut n'est neutre |
| **Q2** | Une commande à **zéro ligne** et **$0.00** est-elle une commande valide ? Observé : le tunnel aboutit à « Thank you for your order! » sur un panier vide. | aucun | **`[open]`** | §2 — argent/facturation |
| **Q3** | Après un refus, le mot de passe doit-il être vidé (AC6) ? Observé : il **reste saisi** après un refus « couple inconnu ». Qui gagne, le critère ou l'application ? | aucun | **`[open]`** | §4 — arbitrage produit, pas ambiguïté de rédaction |
| **Q4** | **Mode d'arrondi** de la taxe à la demi-unité près (arrondi au supérieur, au pair, troncature) ? | aucun | **`[open]`** | §2 — arrondi = politique monétaire, cité explicitement par l'arbre |
| **Q5** | Compte verrouillé **+ mauvais mot de passe** : message générique ou message de verrouillage ? (triplet AC1×AC4×AC5) | générique, conforme à l'observation | **`[open]`** | §4 — divulgation d'existence de compte, décision produit |
| **Q6** | Le **tri** doit-il survivre à une navigation aller-retour ? Et quel départage entre deux articles de même prix ? Observé : retour à `Name (A to Z)`, départage non spécifié. | non, réinitialisation acceptable | **`[assumption]`** | §3 — défaut sûr d'ergonomie |
| **Q7** | « Obligatoire » pour prénom / nom / code postal : non vide, ou **non blanc** ? Y a-t-il une longueur maximale, un jeu de caractères ? Observé : trois espaces passent, 300 caractères passent, `<script>` passe. | non blanc exigé, contenu restitué comme donnée jamais interprétée | **`[assumption]`** | §3 — défaut qu'un praticien accepte sans escalade |
| **Q8** | Une soumission = une commande ? Observé : retour arrière après confirmation → `Finish` de nouveau actif → seconde confirmation. | aucun | **`[open]`** | §2 — argent |
| **Q9** | Le panier doit-il **survivre à une déconnexion** et être restitué à la reconnexion ? Observé : oui. | oui, panier persistant | **`[assumption]`** | §3 |
| **Q10** | Que doit remettre à zéro « **Reset App State** », et fait-elle partie du contrat produit ou de l'outillage du banc ? Observé : panier et pastille vidés, **boutons `Remove` inchangés jusqu'au rechargement**. | remet à zéro l'état panier, et l'affichage suit immédiatement | **`[assumption]`** | mécanisme non spécifié → `[assumption]` (`coverage-expansion.md`, « mechanism unspecified ») |
| **Q11** | Que promet le service à une requête HTTP **hors navigateur** sur une route applicative ? Observé : `GET /inventory.html` → **404**, corps identique à celui d'une route inexistante, aucune donnée catalogue ; `POST` → **405**. | aucune donnée catalogue hors session navigateur ; le **code** n'est pas promis | **`[assumption]`** | §3 |

**Différé à une seconde passe** (nommé, pas posé — le budget de questions est borné) : format
monétaire (`$47.3` chez `visual_user`, `Item total: $0` sur panier vide, une décimale au lieu de
deux) · politique en cas d'image d'article indisponible · valeurs de points de rupture du rendu
responsive · contrat de statut HTTP par route.

**Ce que Q4 a de particulier, et pourquoi elle reste ouverte pour toujours.** Le taux 8 % est
**confirmé** sur quatre paniers ($7.99→$0.64, $49.99→$4.00, $55.97→$4.48, $129.94→$10.40), et
`Total = sous-total + taxe` sur les quatre. Mais le **mode** d'arrondi est indécidable *par cette
interface* : la taxe exacte vaut `0,08 × c` centimes pour un sous-total de `c` centimes, et une
égalité à la demi-unité exigerait `4c = 50k + 25`, dont le membre gauche est pair et le droit
impair. **Aucun panier possible ne produit d'égalité au demi-centime.** La question ne se
résoudra donc pas par un test supplémentaire ; c'est au produit de répondre, ou elle reste ouverte.
C'est le balayage « règles de données non spécifiées » qui l'a fait apparaître, et l'arithmétique
qui a montré qu'aucun test ne la fermerait.

---

# 3. `istqb-design` — techniques, niveaux, conditions

## 3.1 Carte AC → technique (étape 1)

| AC | Technique | Justification liée à la forme de l'AC |
|---|---|---|
| SD01-AC1 | Partition d'équivalence + table de décision | Une classe de couples valides ; et un **axe de profil** à six valeurs publiées qui change le comportement → table de décision (`coverage-expansion.md`, « conditional behavior — decision table over the variation axes »). |
| SD01-AC2/AC3 | Partition d'équivalence + table de décision | Classes « champ vide / champ rempli » ; la clause « **avant** toute autre vérification » est une **précédence**, qui ne se teste que par la cellule (vide, vide). |
| SD01-AC4 | Partition d'équivalence | Trois classes d'échec distinctes (identifiant inconnu, mot de passe faux, casse différente) dont l'AC exige la **même** sortie : l'oracle est l'indiscernabilité, pas le message. |
| SD01-AC5 | Transition d'état + table de décision | Le verrouillage est un état du compte ; croisé avec la validité du couple, c'est la table à deux entrées de la passe 4a. |
| SD01-AC6 | Estimation d'erreur | Comportement d'affichage résiduel après échec, hors règle métier — c'est exactement le domaine de l'estimation d'erreur ancrée sur le journal d'ambiguïtés (Q3). |
| SD01-AC7 | Partition d'équivalence + transition d'état | Classes « avec session / sans session » ; la déconnexion est une transition qui doit invalider. |
| SD02-AC1/AC3 | Analyse des valeurs limites | La pastille est un compteur : ses bornes sont 0 (elle disparaît) et 6 (le catalogue entier). |
| SD02-AC2 | Transition d'état | `Add to cart` ⇄ `Remove` est une transition et son inverse. |
| SD02-AC4 | **Test métamorphique** | On ne peut pas énoncer le prix « vrai » comme oracle — sous `visual_user` il change à chaque chargement. Mais la **relation** « vignette = fiche = ligne panier » est énonçable et vérifiable. C'est le cas d'emploi que la palette réserve au métamorphique : l'utiliser **au lieu** d'affirmer une valeur fabriquée. |
| SD02-AC5 | Transition d'état | Persistance d'un état à travers une navigation. |
| SD02-AC6 | Partition d'équivalence + transition d'état | Quatre options de tri = quatre classes ; « ne modifie pas le panier » est une invariance à travers une transition. |
| SD03-AC1/AC2 | Table de décision + valeurs limites | Les messages arrivent **un à un** : c'est une précédence à trois cellules, pas trois cas indépendants. La limite « vide vs blanc » est une borne du prédicat « rempli ». |
| SD03-AC3 | Partition d'équivalence | Présence des trois libellés, une seule classe. |
| SD03-AC4 | **Test métamorphique** | `Total = sous-total + taxe` est une relation entre sorties, vérifiable sur n'importe quel panier sans énoncer de valeur : c'est la définition du métamorphique, et elle vaut mieux que quatre littéraux figés. |
| SD03-AC5 | Analyse des valeurs limites | Un taux avec arrondi au centime : les cas intéressants sont les montants où l'arrondi mord. Valeurs **calculées puis observées**, jamais transcrites. |
| SD03-AC6 | Transition d'état | Confirmation = transition terminale supposée ; sa ré-entrance est le test. |
| SD03-AC7 | Partition d'équivalence | Classe « panier vide » du prédicat d'entrée au tunnel. |

**Hors palette, dit plutôt que sous-entendu** : aucune technique structurelle (l'implémentation
n'est pas lue) et aucun test exploratoire — exclusions délibérées d'`istqb-design`, pas des trous.

## 3.2 Étape 3c — expansion systématique de couverture

| Motif | Appliqué ? | Ce qu'il a produit |
|---|---|---|
| Vue liste / collection | **oui** | SD02-D3 (les 4 tris ont un oracle propre, absent de la ligne de base) et **SD02-D4 — la persistance du tri à travers une navigation**, que ce motif nomme mot pour mot et que rien d'autre n'aurait demandée. |
| Énumérer **toutes** les listes | **oui, sans effet** | Trois collections existent (catalogue, panier, récapitulatif) mais seul le catalogue porte un contrôle de tri/filtre. Enregistré comme balayé sans trouvaille. |
| Cycle CRUD complet + inverses + annulation | **oui** | SD02-C4 (Add⇄Remove), SD03-D2 (`Cancel` en cours de tunnel), **SD02-D6 (Reset App State et sa désynchronisation)**. |
| Collections sœurs d'une entité nommée | **sans objet** | Aucun AC ne décrit une entité comme « collection de X » ; l'article n'a pas de sous-collection. |
| Comportement conditionnel — table de décision sur les axes | **oui, et c'est le motif décisif** | L'axe de variation de cette application, **publié sur sa page d'accueil**, est le **type d'utilisateur**. Ce motif est le mécanisme qui fait apparaître `problem_user`, `error_user`, `visual_user` et `performance_glitch_user` : il demande de croiser « config / visibilité / rôle » avec chaque comportement, et le rôle est ici documenté à six valeurs. → SD01-C2, SD02-C7, SD02-C11, SD02-C12, SD03-C11, SD03-C12. |
| Autorisation et application côté serveur | **oui** | SD01-C13 (les **trois** pages protégées, pas seulement le catalogue), SD01-C15 (après déconnexion), **SD01-C14 — contournement de l'interface : la requête HTTP directe**. |
| Surface protocole | **partiellement** | Cible SPA sans contrat de service publié. Retenu : SD01-C14 (`GET` hors navigateur) et SD01-C16 (méthode non autorisée, **P3, dérogation de périmètre assumée**). Idempotence, négociation de contenu, pagination : **sans objet**, aucun endpoint documenté. |
| Surface de rendu | **non appliqué, et c'est déclaré** | Aucun point de rupture n'est nommé par la source ; le motif impose alors de dire quelle largeur on suppose. Je ne suppose rien : les conditions responsive sont **écartées de ce lot** et renvoyées à la seconde passe de questions. Les écarter en silence aurait été le défaut. |
| Récupération de compte | **sans objet** | Aucun « mot de passe oublié » n'existe sur la cible ; le motif est balayé sans trouvaille. |
| **Surface d'interaction** | **oui, et c'est le second motif décisif** | Double soumission → SD03-C10 (retour arrière après confirmation, `Finish` réactivé). Navigation en cours de parcours → SD02-D4, SD03-D2. Contenu textuel imprévu → SD03-D1. Dépendance retirée en cours de session → **sans objet** (aucune entité tierce). Deux acteurs sur un enregistrement → **sans objet** (mono-utilisateur). |

**Plafond respecté** : rien n'est inventé pour gonfler le rappel. Là où l'application fait quelque
chose que la source ne prévoit pas, la condition est **générée** et son résultat attendu reste une
**question ouverte** — jamais une certitude fabriquée.

## 3.3 Étapes 3b et 3d

- **3b — oracles de domaine standardisé** : **non invoqué**. Les seuls domaines normalisables ici
  seraient la devise (ISO 4217) et un éventuel format de code postal. Le code postal n'est
  contraint par aucune règle (Q7 : « x » passe), donc il n'y a pas de norme à opposer ; la devise
  n'est même pas énoncée par la source. Invoquer `oracle-generate` aurait produit des attentes que
  la source ne porte pas.
- **3d — conditions issues de la base de connaissances** : **sans objet**, `.qaia/knowledge/`
  n'existe pas pour cette cible (mode dégradé, règle 8). Aucune règle citée, `knowledgeApplied` vide.

## 3.4 Conditions de test dérivées

Notation : `[req-neg]` = chemin de refus au sens fermé (un refus, une erreur, un accès refusé).
`[level: …]` avec son motif (ADR 0008 : l'interface par laquelle la promesse est observable).

### US-SD-01 — Se connecter

| ID | Condition | Technique | Niveau + motif | Marques |
|---|---|---|---|---|
| SD01-C1 | Couple valide (`standard_user`) → page catalogue, 6 articles | partition d'équivalence | `[level: e2e]` — la promesse est un écran atteint | |
| SD01-C2 | Les **cinq** profils non verrouillés atteignent le catalogue (axe de profil) | table de décision | `[level: e2e]` — même promesse, même interface | `[assumption]` Q1 |
| SD01-C3 | `performance_glitch_user` atteint le catalogue malgré ~5,0 s contre ~0,05 s | estimation d'erreur | `[level: e2e]` — l'oracle retenu est **fonctionnel** (l'écran arrive), pas un budget de latence : le budget appartient à `qaia-playwright:perf-check` | `[assumption]` Q1 |
| SD01-C4 | Identifiant vide + mot de passe rempli → `Username is required` | partition d'équivalence | `[level: e2e]` | **`[req-neg]`** |
| SD01-C5 | Les deux champs vides → `Username is required` (**précédence** : le contrôle identifiant précède celui du mot de passe) | table de décision | `[level: e2e]` | **`[req-neg]`** |
| SD01-C6 | Identifiant rempli + mot de passe vide → `Password is required` | partition d'équivalence | `[level: e2e]` | **`[req-neg]`** |
| SD01-C7 | Identifiant inconnu → message générique | partition d'équivalence | `[level: e2e]` | **`[req-neg]`** |
| SD01-C8 | Identifiant connu + mot de passe faux → **le même** message générique (indiscernabilité) | partition d'équivalence | `[level: e2e]` | **`[req-neg]`** |
| SD01-C9 | `Standard_User` (casse modifiée) → message générique : l'identifiant est sensible à la casse | partition d'équivalence | `[level: e2e]` | **`[req-neg]`** |
| SD01-C10 | `locked_out_user` + mot de passe valide → message de verrouillage, reste sur la page de connexion | transition d'état | `[level: e2e]` | **`[req-neg]`** |
| SD01-C11 | `locked_out_user` + mot de passe **faux** → message générique, **pas** le message de verrouillage | table de décision | `[level: e2e]` | **`[req-neg]`**, `[open]` Q5 |
| SD01-C12 | Après un refus, l'identifiant saisi reste affiché | estimation d'erreur | `[level: e2e]` — état d'un champ à l'écran | |
| SD01-C13 | Après un refus « couple inconnu », le mot de passe **n'est pas vidé** — divergence avec AC6 | estimation d'erreur | `[level: e2e]` | `[open]` Q3. **Pas `[req-neg]`** : le refus lui-même est déjà couvert par SD01-C8 ; ce qui est asserté ici est l'état d'un champ, pas un refus. Le compter deux fois gonflerait le ratio sans rien couvrir de plus. |
| SD01-C14 | `/inventory.html`, `/cart.html`, `/checkout-step-two.html` atteintes sans session → message d'accès refusé, aucun contenu | partition d'équivalence | `[level: e2e]` — le refus est rendu par l'interface, pas par un statut HTTP | **`[req-neg]`** |
| SD01-C15 | Requête HTTP **hors navigateur** sur la route catalogue → aucune donnée de catalogue dans la réponse | partition d'équivalence | **`[level: api]`** — c'est le seul endroit du lot où la promesse s'observe **sans navigateur** : le contournement d'interface se vérifie là où il a lieu. Couvrir cela par un scénario d'écran laisserait la promesse invérifiée à l'interface où elle est faite (ADR 0008, §Contexte, point 3). | **`[req-neg]`**, `[assumption]` Q11 |
| SD01-C16 | Méthode HTTP non autorisée sur une route applicative → `405` | estimation d'erreur | `[level: api]` | **`[req-neg]`** — **P3, dérogation de périmètre assumée** (voir §4) |
| SD01-C17 | Après déconnexion, le retour au catalogue est refusé (la session est invalidée) | transition d'état | `[level: e2e]` | **`[req-neg]`** |

### US-SD-02 — Composer un panier

| ID | Condition | Technique | Niveau + motif | Marques |
|---|---|---|---|---|
| SD02-C1 | 1 article → pastille `1` ; les 6 articles → pastille `6` (bornes de la collection) | valeurs limites | `[level: e2e]` | |
| SD02-C2 | Le bouton d'un article ajouté devient `Remove` | transition d'état | `[level: e2e]` | |
| SD02-C3 | 2 articles, en retirer 1 → pastille `1` | valeurs limites | `[level: e2e]` | |
| SD02-C4 | 1 article, le retirer → **la pastille disparaît** (borne basse) | valeurs limites | `[level: e2e]` | |
| SD02-C5 | Sous `problem_user` et `error_user`, `Remove` ne décrémente pas la pastille | table de décision | `[level: e2e]` | `[open]` Q1. Pas `[req-neg]` : une fonction inopérante n'est pas un refus. |
| SD02-C6 | La ligne du panier reprend libellé et prix du catalogue (`standard_user`) | partition d'équivalence | `[level: e2e]` | |
| SD02-C7 | **Relation** : prix vignette = prix fiche = prix ligne panier. Rompue sous `visual_user` (vignette `$54.97`, fiche et panier `$29.99`) | métamorphique | `[level: e2e]` | `[open]` Q1 |
| SD02-C8 | **Relation** : le lien d'un article ouvre la fiche de l'article nommé. Rompue sous `problem_user` (« Sauce Labs Backpack » → fiche « Sauce Labs Fleece Jacket ») | métamorphique | `[level: e2e]` | `[open]` Q1 |
| SD02-C9 | Le panier survit à l'aller-retour vers une fiche article | transition d'état | `[level: e2e]` | |
| SD02-C10 | Chacune des 4 options de tri produit l'ordre annoncé | partition d'équivalence | `[level: e2e]` | |
| SD02-C11 | Le tri ne modifie pas le contenu du panier | transition d'état | `[level: e2e]` | |
| SD02-C12 | Le tri **ne survit pas** à une navigation aller-retour (retour à `Name (A to Z)`) | transition d'état | `[level: e2e]` | `[assumption]` Q6 |
| SD02-C13 | Sous `problem_user` et `error_user`, le sélecteur de tri est sans effet | table de décision | `[level: e2e]` | `[open]` Q1 |
| SD02-C14 | Le panier survit à une déconnexion puis reconnexion — **hors AC** | transition d'état | `[level: e2e]` | `[assumption]` Q9 |
| SD02-C15 | `Reset App State` vide panier et pastille mais **laisse les boutons sur `Remove`** jusqu'au rechargement — **hors AC** | CRUD | `[level: e2e]` | `[assumption]` Q10 |

### US-SD-03 — Passer commande

| ID | Condition | Technique | Niveau + motif | Marques |
|---|---|---|---|---|
| SD03-C1 | Précédence des trois refus : rien → `First Name`, prénom seul → `Last Name`, prénom+nom → `Postal Code` | table de décision | `[level: e2e]` | **`[req-neg]`** |
| SD03-C2 | Trois champs remplis d'espaces → **acceptés**, le tunnel continue | valeurs limites | `[level: e2e]` | `[assumption]` Q7. **Pas `[req-neg]` en l'état** : aucun refus ne se produit. Si Q7 est tranchée « non blanc exigé », cette condition **devient** `[req-neg]` et le scénario s'inverse. |
| SD03-C3 | Le récapitulatif affiche sous-total, taxe et total | partition d'équivalence | `[level: e2e]` | |
| SD03-C4 | **Relation** `Total = sous-total + taxe` sur 4 paniers (le moins cher, le plus cher, 3 articles, les 6) | métamorphique | `[level: e2e]` | |
| SD03-C5 | Taxe = 8 % arrondi au centime : `$7.99→$0.64`, `$49.99→$4.00`, `$55.97→$4.48`, `$129.94→$10.40` (calculées puis observées) | valeurs limites | `[level: e2e]` | |
| SD03-C6 | **Non dérivable** : égalité au demi-centime pour fixer le mode d'arrondi — aucun panier ne peut la produire (`4c = 50k + 25` est impossible) | valeurs limites | — | `[open]` Q4, **inatteignable par cette interface** : consigné comme non couvrable, jamais contourné par un choix de donnée |
| SD03-C7 | `Finish` → « Thank you for your order! » et panier vidé | transition d'état | `[level: e2e]` | |
| SD03-C8 | Retour arrière après confirmation → `Finish` de nouveau actif → seconde confirmation | transition d'état | `[level: e2e]` | `[open]` Q8. Pas `[req-neg]` : le défaut est précisément qu'**aucun** refus n'intervient. |
| SD03-C9 | Sous `error_user`, `Finish` reste sans effet (on reste sur le récapitulatif) | table de décision | `[level: e2e]` | `[open]` Q1 |
| SD03-C10 | Sous `problem_user`, le champ Nom rejette la saisie → la commande est **impossible** | estimation d'erreur | `[level: e2e]` | `[open]` Q1 |
| SD03-C11 | Panier vide → le tunnel **aboutit** à la confirmation, `Item total: $0`, `Total: $0.00` | partition d'équivalence | `[level: e2e]` | **`[req-neg]`** (AC7 déclare un refus), `[open]` Q2 — voir l'alerte ci-dessous |
| SD03-C12 | `Cancel` au premier écran du tunnel ramène au panier sans perte | transition d'état | `[level: e2e]` | P3 |
| SD03-C13 | Balisage, caractères non latins et 300 caractères dans les champs → restitués comme **donnée**, jamais interprétés — **hors AC** | estimation d'erreur | `[level: e2e]` | `[assumption]` Q7, **`[req-neg]`** selon `coverage-expansion.md` — voir la note de doctrine ci-dessous |

> **Alerte de porte — SD03-C11.** ADR 0001 exige que « tout chemin de refus, d'erreur ou de déni
> ait un scénario **exerçant** ce chemin ». Ici le chemin de refus est **déclaré par l'AC7 et
> absent de l'application** : le scénario qui couvre la condition documente la divergence, il
> n'exerce aucun refus, et il n'est donc **pas** compté `@negative` (définition fermée de
> `negative-ratio.md`). La porte est satisfaite **à la lettre et pas dans l'esprit**, et je le dis
> plutôt que de la laisser verte en silence. C'est le seul point où les deux textes ne se
> recouvrent pas : ADR 0001 n'a pas prévu le cas « le refus exigé n'existe pas », et rien dans les
> skills ne dit s'il faut alors bloquer ou documenter. **À arbitrer (Q2).**

> **Note de doctrine — SD03-C13.** `coverage-expansion.md` (motif « surface d'interaction »,
> puce « contenu textuel imprévu ») écrit que le résultat attendu — *« stored and rendered as
> data, never interpreted »* — est *« precisely what makes it a refusal-path condition »*. La
> définition fermée de `negative-ratio.md` dit l'inverse : `@negative` = « a scenario whose
> outcome is **a refusal, an error, or an explicitly denied access** ». Un scénario qui affirme
> « la chaîne est affichée telle quelle » n'a aucun refus pour sortie. **Les deux références se
> contredisent.** J'applique la définition fermée (c'est elle que l'outillage compte) : la
> condition est marquée `[req-neg]` comme la référence l'ordonne, le scénario n'est **pas** tagué
> `@negative`. Le désaccord est signalé, pas réconcilié à la main.

**Récapitulatif** : **45 conditions**, dont **1 non dérivable** (SD03-C6, démontrée inatteignable)
et **15 marquées `[req-neg]`** : SD01-C4, C5, C6, C7, C8, C9, C10, C11, C14, C15, C16, C17,
SD03-C1, SD03-C11, SD03-C13. Deux de ces quinze sont couvertes par un scénario **non compté
`@negative`** — SD03-C11 (le refus exigé n'existe pas) et SD03-C13 (les deux références se
contredisent) — pour les raisons dites juste au-dessus.

Répartition par niveau : **42 `e2e`, 2 `api`, 1 sans niveau** (SD03-C6, non dérivable, donc
aucune interface à désigner).

---

# 4. `prioritize` — risque proposé, **non arbitré**

> **Si vous êtes propriétaire du produit plutôt que des tests, lisez ceci. Vous n'avez pas besoin
> du reste de cette page.**
>
> - **Ce qu'on vous demande :** pour chaque comportement du tableau, nous avons deviné deux
>   choses — la gravité d'une panne en production, et sa probabilité. Corrigez la première. C'est
>   un jugement métier, et vous êtes le seul à le détenir.
> - **Pourquoi c'est important :** les deux nombres se multiplient en une priorité, et la priorité
>   décide de ce qui est écrit et joué. Sous-cotez et une chose ne sera jamais testée ; surcotez
>   tout et l'important perd sa place dans la file.
> - **Si vous ne répondez pas :** nous gardons notre proposition, marquée *proposée, non
>   arbitrée*. Rien ne s'arrête — mais l'effort de test est alors dirigé par notre supposition sur
>   votre risque métier, et l'histoire n'est pas apte à une décision de mise en production tant
>   que personne n'a regardé.
>
> Vous n'avez pas à relire chaque ligne. Celles qui valent vos minutes sont les **P1** — plus un
> survol des titres du reste : vous êtes la seule personne capable de repérer une ligne cotée
> basse que votre métier ne peut pas se permettre.

**Statut : proposé, non arbitré.** Aucune de ces cotations n'a été contredite par un humain ;
elles ne conviennent pas à une décision Go/No-Go.

| Condition(s) | Imp. | Prob. | Prio | Justification risque (une ligne, reportée dans le cahier) |
|---|---|---|---|---|
| SD03-C11 | 3 | 3 | **P1** | Une commande sans contenu est enregistrée : perte de données commerciales et écart de facturation, et le défaut est **constaté**, pas supposé. |
| SD03-C8 | 3 | 3 | **P1** | Double confirmation atteignable par le bouton retour : duplication de commande, domaine argent, constatée. |
| SD03-C4, SD03-C5 | 3 | 2 | **P1** | Le montant facturé est la promesse la plus coûteuse à trahir ; l'arithmétique est simple donc peu probablement fausse, mais Q4 laisse l'arrondi non tranché. |
| SD02-C7 | 3 | 2 | **P1** | Un prix affiché différent du prix facturé est une tromperie visible du client ; observé sous un profil publié. |
| SD01-C4→C11 (refus de connexion) | 3 | 2 | **P1** | La porte d'entrée : un refus mal rendu ouvre soit un accès indu, soit une énumération de comptes. |
| SD01-C14, SD01-C15, SD01-C17 | 3 | 2 | **P1** | Contrôle d'accès aux pages protégées, y compris hors navigateur : impact maximal, mécanique simple donc probabilité moyenne. |
| SD03-C1 | 2 | 3 | **P1** | Adresse de livraison incomplète = commande non livrable ; trois cellules de précédence, donc surface d'erreur réelle. |
| SD01-C1 | 3 | 1 | **P2** | Chemin nominal : impact maximal si rompu, mais c'est le trajet le plus exercé de l'application. |
| SD02-C8 | 2 | 2 | **P2** | Le lien mène à un autre article : le client peut acheter autre chose que ce qu'il croit, observé sous un profil publié. |
| SD02-C1, C2, C3, C4, C6, C9 | 2 | 2 | **P2** | Composition du panier : service dégradé si faux, logique de compteur simple mais très sollicitée. |
| SD02-C5, C13, SD03-C9, SD03-C10, SD01-C2, SD01-C3 | 2 | 3 | **P2** | Comportements des profils défectueux : chacun casse une fonction entière (tri, retrait, confirmation, saisie), mais leur statut de défaut dépend de Q1 — probabilité haute, impact conditionné à l'arbitrage. |
| SD02-C10, C11 | 2 | 2 | **P2** | Le tri est la seule fonction de recherche du catalogue ; son oracle manquait entièrement à la ligne de base. |
| SD02-C12, C14, C15, SD03-C2, SD03-C13 | 1 | 2 | **P2** | Ergonomie et robustesse d'entrée : cosmétique à dégradé, mais toutes reposent sur une hypothèse non confirmée, ce qui remonte la probabilité. |
| SD03-C3 | 1 | 1 | **P3** | Présence de trois libellés à l'écran ; couvert de fait par les conditions de calcul. |
| SD03-C12 | 1 | 2 | **P3** | `Cancel` ramène au panier : gêne, sans perte. |
| SD01-C16 | 1 | 1 | **P3** | Méthode HTTP non autorisée sur une SPA sans contrat publié : aucun client ne s'appuie dessus. |

**Périmètre de génération retenu : P1 + P2**, plus **une exception assumée**. Deux conditions P3
sont **différées par un choix de périmètre** — SD03-C12 (`Cancel`) et SD01-C16 (méthode HTTP non
autorisée) — ce qui n'est pas une violation de porte tant qu'elles restent visibles avec leur
motif (`negative-ratio.md`, §« Priority-scoped waivers »). SD01-C16 est `[req-neg]` et différée :
c'est la seule dérogation de la porte ADR 0001, nommée ici plutôt que disparue du compte.

La troisième condition P3, **SD03-C3, est générée malgré son rang** (scénario `@QAIA-SD-030`,
tagué `@P3`) : c'est la seule condition rattachée à l'AC3 de US-SD-03, et la différer laisserait
un critère d'acceptation **sans aucun scénario**. Un AC non couvert est un défaut plus lourd
qu'un léger dépassement de périmètre. L'écart est écrit ici parce que le rang et le contenu du
cahier doivent pouvoir se recouper ligne à ligne.

---

# 5. Ce que le cahier émet

**39 scénarios**, 62 cas exécutables (les `Scenario Outline` comptent pour leur nombre de lignes
d'exemple), scénario `@smoke` exclu du décompte. **16 cas `@negative`** → **ratio 25,8 %**.

**Explicateur de ratio (obligatoire quand le ratio est bas et la porte verte)** : les deux AC les
plus lourds de cette cible — le calcul de la taxe (SD03-AC4/AC5) et la composition du panier
(US-SD-02 en entier) — **ne portent aucun chemin de refus**. Les refus vivent presque tous dans
US-SD-01 (AC2 à AC5, AC7) et dans SD03-AC1. S'y ajoute une singularité : le défaut le plus grave
trouvé (SD03-C11) est précisément un refus **manquant**, donc son scénario ne peut pas compter au
numérateur. Un ratio bas sur un cahier complet est normal ici, ce n'est pas un défaut à corriger
en ajoutant des cas.

**Fichier émis** : [`11-saucedemo.feature`](11-saucedemo.feature).
