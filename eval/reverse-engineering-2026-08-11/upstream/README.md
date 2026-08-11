# Signalements amont — ce qui part, ce qui ne part pas, et pourquoi

**Écrit le 2026-08-11, après vérification.** Trois défauts candidats étaient sortis de la
campagne. **Un seul est publiable.** Ce fichier dit pourquoi, parce que le tri vaut plus que les
constats.

---

## RETIRÉ — le filtre `checkin` : ma reproduction ne tenait pas

**J'ai annoncé un défaut confirmé. Il ne l'était pas.** Correction consignée ici, à l'endroit où
elle se lit.

Ce qui a été observé au départ : une réservation créée avec `checkin: 2027-07-08`, retrouvée par
`?lastname=`, absente de `?checkin=2027-07-08`. Conclusion tirée : *un paramètre documenté qui ne
filtre pas.* J'ai relayé ça comme « vérifié par moi-même ».

**Ce que la vérification suivante a montré :**

| Sonde | Résultat |
|---|---|
| `GET /booking/7485` (la réservation que je venais de créer) | **404 — elle n'existe plus** |
| `?checkin=2027-07-08`, trois appels | `[{"bookingid":751}]` à chaque fois |
| `GET /booking/751` | checkin `2026-05-25` — **antérieur au filtre**, donc ne devrait pas sortir |
| `?checkin=2026-05-25` (date exacte de 751) | 1 résultat, **et ce n'est pas 751** |
| `?checkin=2020-01-01` | de nombreux résultats |
| `?checkin=2030-01-01` | `[]` |

Les deux dernières lignes règlent la question : **le filtre fonctionne directionnellement.** Les
observations à un seul résultat, et la disparition de la réservation créée, s'expliquent par
l'implémentation — `models/booking.js` utilise **lokijs en mémoire**, l'instance hébergée porte
~3 618 réservations et se réinitialise ; deux requêtes consécutives ne voient pas nécessairement
le même état.

**Conséquence méthodologique, et c'est elle qui compte :** sur cette instance, **tout constat qui
compare l'état entre deux requêtes est invalide par construction.** Créer puis relire n'est pas une
observation, c'est une supposition sur le routage. Ça vaut pour ma reproduction — et ça vaut aussi
pour l'issue #42, qui procède exactement de la même façon.

**Ce qui subsiste, et que je ne publie pas non plus** : le code source dit
`{$gt: new Date(req.query.checkin).toISOString()}` (`routes/index.js`) là où sa propre
documentation, deux lignes plus haut, annonce *« checkin date **greater than or equal to** the set
checkin date »*. Un écart doc/implémentation réel — mais **je ne peux pas le démontrer en boîte
noire sur cette instance**, et signaler une lecture de code sans démonstration sur un dépôt qui a
déjà fermé le sujet serait exactement le bruit qu'on cherche à éviter.

**Le commentaire préparé pour #42 est retiré. Il n'a jamais été publié.**

---

## PUBLIABLE — le 500 sur corps invalide

`500-issue.md`. Reproduit **quatre fois au cours de la session**, à des moments différents :

```
POST /booking  -d '{}'                 -> 500
POST /booking  -d '{"firstname":"X"}'  -> 500
```

**Pourquoi celui-ci tient là où l'autre tombe** : c'est un constat à **requête unique**. Il ne
compare aucun état entre deux appels, donc l'instabilité de la base en mémoire ne l'atteint pas.
La réponse ne divulgue rien — 21 octets de `text/plain`, aucune trace de pile — vérifié, ce qui
borne la sévérité.

Recherche d'antériorité : **aucun rapport existant** (`500`, `malformed`, `empty body` → 0 résultat
pertinent chez `mwinteringham/restful-booker`).

Le brouillon mentionne aussi, en secondaire et explicitement comme une supposition non établie,
que `POST /auth` renvoie **200** sur identifiants refusés — même famille de constat à requête
unique, reproduit lui aussi.

---

## La leçon, chiffrée

**Trois candidats, un publiable.** Le tri a coûté une dizaine de requêtes et a évité deux
signalements que le mainteneur aurait eu raison de fermer.

C'est exactement le dossier dont la passe de réfutation de ce dépôt est née : *91 constats faux
contre 2 confirmés*, publiés trois fois avec un mauvais dénominateur. La règle qui l'évite est
écrite dans `agents-tier/agents/elian-refuter.md` et elle a fonctionné ici :

> *« Une affirmation dont l'emplacement cité n'a jamais été ouvert est réfutée par défaut — pas
> "en attente", réfutée. »*

Ce qui l'a déclenchée n'est pas un contrôle du dépôt. C'est une question posée à voix haute :
**« tu es sûr de tes erreurs ? »**
