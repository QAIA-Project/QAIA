# Plan de reprise — quatre épiques, trois sprints

**Écrit le 2026-08-09, après l'audit à froid.** Ce plan part du seul constat qui compte :

> **Les deux seules choses que ce projet ait jamais prouvées à l'extérieur viennent d'outils
> qui lisent le code ou la documentation des autres — pas de la chaîne « exigence → cahier de
> test ».** Un défaut corrigé chez `realworld-apps/realworld` (84k ★, trouvé par
> `automation_score`), et **deux défauts fusionnés en amont chez `typicode/json-server`**
> (75k ★, `eval/external-application-2026-08-08/`) — celui-ci part de la documentation de la
> cible, pas d'une exigence qu'un humain nous a confiée.
>
> *Correction du 2026-08-09 : ce paragraphe ne mentionnait que RealWorld et présentait donc
> comme unique une preuve qui est double. Relevé par la revue « chef de projet ».*
>
> Le cœur — *donner une exigence, recevoir un cahier de test* — n'a jamais été validé par
> quelqu'un d'extérieur. Pas une fois en quinze jours.

Tout ce qui suit en découle. Les épiques sont ordonnées : **E1 avant tout le reste**, parce que si
le cœur ne tient pas, le reste n'a pas à être rangé.

---

## E1 — Charger la poutre

**Prouver le parcours principal sur du réel, avec quelqu'un qui n'est pas nous.**

18 skills sur 37 n'ont aucune trace d'avoir servi, et ce sont celles du parcours central :
`us-ingest`, `us-review`, `istqb-design`, `prioritize`, `testbook-generate`, `testbook-validate`.
La périphérie est éprouvée ; le centre est déclaratif.

| # | Tâche | Terminée quand |
|---|---|---|
| E1.1 | Choisir **une** exigence réelle, écrite par quelqu'un d'autre, non liée au projet | La source est gelée dans `eval/` avec son sha256 et son origine |
| E1.2 | Exécuter le parcours entier, sans raccourci, en consignant chaque refus et chaque question ouverte | Les 6 artefacts existent, horodatés, dans l'ordre |
| E1.3 | Faire noter le cahier par **Camille**, contexte vierge, sans accès à la production | Un verdict PASS/CONCERNS/FAIL avec ses constats |
| E1.4 | Faire attaquer le résultat par **Elian** | Chaque constat est REFUTÉ / TIENT / NON TRANCHABLE |
| E1.5 | Publier le résultat **échecs d'abord** | Le rapport ouvre sur ce qui n'a pas marché |
| E1.6 | Faire relire par un testeur QA **qui n'a pas participé** | Son verdict est publié tel quel, y compris s'il est mauvais |

**Ce qui ferme l'épique :** un rapport public où un tiers dit si le cahier lui aurait servi.
**Ni un score, ni une démo. Un avis.**

**Ce qui ne la ferme pas :** nous, disant que ça marche. C'est déjà écrit 196 fois.

---

## E2 — Rendre le dépôt installable en cinq minutes

**6,8 fichiers d'évaluation par fichier livré. 12× le poids.** Le produit est bon et petit
(666 Ko) ; il est enseveli sous 8 Mo de comptes rendus que personne ne relira, nous compris.

| # | Tâche | Terminée quand |
|---|---|---|
| E2.1 | Ramener `eval/` de 1 002 fichiers à **~30** : garder les fixtures que la CI exécute et les campagnes externes, archiver le reste hors dépôt | `make check` passe toujours ; `eval/` tient dans un `ls` |
| E2.2 | Scinder `docs/DECISIONS.md` (308 Ko) : **30 lignes de synthèse** en tête, l'historique dans un fichier séparé | Un nouveau venu comprend les arbitrages sans lire un livre |
| E2.3 | Réécrire le `README` pour **ouvrir sur la preuve**, pas sur la liste des fonctionnalités | La première section montre un résultat, pas un inventaire |
| E2.4 | Vérifier l'installation sur une machine vierge, en suivant le README à la lettre | Quelqu'un qui n'a pas écrit le README y arrive |

**Ce qui ferme l'épique :** quelqu'un installe et lance une skill sans poser de question.

---

## E3 — Rendre le backlog directeur, ou l'assumer comme journal

**L'issue #30 décrivait l'agent de revue adversariale — périmètre, opt-in, garde-fous compris.
Elle était ouverte depuis quinze jours. Je l'ai implémentée aujourd'hui sans l'avoir lue.**

Ça a bien fini par hasard. Mais un backlog qui n'est pas lu avant de coder n'est pas un backlog,
c'est un journal.

| # | Tâche | Terminée quand |
|---|---|---|
| E3.1 | Fermer ce qui est livré, avec la preuve dans le commentaire de clôture | Chaque clôture cite un fichier ou un commit |
| E3.2 | Tuer ce qui ne se fera pas, en disant pourquoi plutôt qu'en laissant pourrir | Zéro issue de plus de 30 jours sans décision |
| E3.3 | **Lire le backlog avant d'ouvrir un éditeur** — règle, pas intention | Chaque commit substantiel cite une issue ou déclare n'en avoir aucune |
| E3.4 | Réduire à **≤ 6 issues ouvertes**, chacune avec un propriétaire nommé | Aucune issue sans propriétaire |

---

## E4 — Distribution *(propriétaire : le fondateur, pas moi)*

Quatre des neuf issues ouvertes sont bloquées ici, et **aucune ne demande une ligne de code**.

| # | Tâche | Terminée quand |
|---|---|---|
| E4.1 | Post LinkedIn — le texte est prêt depuis deux jours | Publié |
| E4.2 | Relancer les 4 PR de référencement à J+7, pas avant | Fusionnées ou closes |
| E4.3 | Un enregistrement montrant le produit sans l'installer | En ligne |

**Argument disponible depuis aujourd'hui et pas hier :** *un défaut trouvé et corrigé dans un
projet à 84 000 étoiles.* Il ne se périme pas vite, mais il ne grandit pas non plus.

---

## Les trois sprints

| Sprint | Contenu | Test de fin |
|---|---|---|
| **S32 — Charger** | E1 en entier | Un tiers a lu le cahier et dit s'il lui aurait servi |
| **S33 — Alléger** | E2 + E3 | Le dépôt s'installe en cinq minutes, ≤ 6 issues ouvertes |
| **S34 — Sortir** | E4 + ce que S32 a révélé | Le compteur de visiteurs uniques a bougé |

## La règle que je m'impose pour ces trois sprints

**Aucune 38ᵉ skill tant que E1 n'est pas fermée.**

Quinze jours ont produit 37 skills, 12 contrôles, 4 boucles, 8 agents — et zéro utilisateur. Le
problème n'a jamais été le manque de fonctionnalités. Ajouter la 38ᵉ serait la troisième fois que
je réponds à une question que personne n'a posée.

## Ce que cet audit n'a pas

Il a été écrit **par la même partie qui a produit le travail audité**, avec tout le contexte de la
journée en tête — l'exact contraire de la règle 3 que ce projet impose partout ailleurs. Un audit
indépendant a été lancé en parallèle ; **s'il contredit ce plan, c'est lui qui a raison**, et le
plan sera réécrit plutôt que défendu.
