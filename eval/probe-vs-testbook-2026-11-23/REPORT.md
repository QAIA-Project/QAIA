# `probe` seul contre le cahier de tests, sur la même cible — la mesure que demandait #111

**Date** 2026-11-23 · Point B2 de la [feuille de route](../../docs/ROADMAP.md) ·
[#111](https://github.com/QAIA-Project/QAIA/issues/111)

## La question

#111 demande de trancher le sort d'`automate` (Gherkin → Playwright exécutable), et pose un
préalable : *combien des constats `json-server` la face `sonder` aurait-elle atteints seule, en
interrogeant l'application réelle sans passer par une suite Playwright générée ?*

La campagne du 2026-08-08 ([rapport](../external-application-2026-08-08/report.md)) avait trouvé
deux défauts réels dans `typicode/json-server` 1.0.0-alpha.23 (`8fb0f72`), par un cahier de 32
scénarios écrit depuis le README puis automatisé en Playwright : **EXT-019** (deux conditions sur
le même champ ne se combinent pas) et **EXT-030** (`_dependent` ne supprime pas les dépendances).

## Le protocole

| | |
|---|---|
| Cible | la même version, `8fb0f72`, lancée en local (auto-hébergée) |
| Données | la base d'exemple **du README**, et non `db.used.json` de la campagne, qui dérivait du cahier |
| Méthode | la page `probe/references/01-probing-a-live-app.md`, telle quelle |
| Exécutant | **un agent à contexte vierge**, à qui il était interdit de lire le code, les tests, l'historique git de la cible, le dossier `eval/` de QAIA, et de chercher sur le web. Boîte noire : README + HTTP |
| Ce qu'il ne savait pas | qu'une campagne avait déjà eu lieu, ni quels défauts elle avait trouvés |
| Contrôle | chaque constat rejoué à la main sur `8fb0f72`, puis sur `89a34a4` (beta.15, mars 2026) |

Le cahier ne pouvait pas être rejoué à l'aveugle par celui qui écrit ces lignes : les deux défauts
étaient connus. D'où l'agent à contexte vierge, seul usage d'un sous-agent de la journée.

## Le résultat

31 promesses extraites du README, 31 sondées, **3 rompues** — chacune reproduite deux fois.

| Constat | Trouvé par le cahier (2026-08-08) | Trouvé par `probe` seul | Sur beta.15 |
|---|:-:|:-:|---|
| **EXT-019** — `views_gt=150&views_lt=300` rend les deux posts | **oui** | **non** | corrigé (rend `['2']`) |
| **EXT-030** / CP-003 — `DELETE /posts/1?_dependent=comments` laisse les commentaires | **oui** | **oui** | corrigé (commentaires supprimés) |
| **CP-001** — `PATCH /profile {"age":3}` imbrique l'ancien contenu sous `item` | non | **oui** | corrigé (fusion) |
| **CP-002** — `POST /posts {"id":3}` stocke un id numérique, inatteignable par `GET /posts/3` | non | **oui** | corrigé (id forcé en chaîne) |

**Les quatre sont des défauts réels** : tous présents en alpha.23, tous corrigés par le
mainteneur en beta.15. Aucun faux positif dans les trois constats de `probe`. L'agent a en outre
classé trois comportements comme **extrapolations non comptées** (`_start` seul, `views_lt=1e3`,
id dupliqué accepté) — dont `_start` seul, que la campagne d'origine avait elle aussi fini par
retirer de son décompte pour la même raison.

## Pourquoi chacun a manqué ce qu'il a manqué

**`probe` a manqué EXT-019** parce qu'il a sondé chaque opérateur **isolément** (`_lt`, `_gt`…,
P13-P16 de son extraction). Le README liste les opérateurs sans jamais montrer leur combinaison
sur un même champ. Le cahier l'a trouvé parce qu'une technique de conception (partitions et
bornes sur un domaine `100 < views < 300`) **construit** la combinaison que la doc ne montre pas.

**Le cahier a manqué CP-001 et CP-002 alors qu'il couvrait les deux zones** :

- `@QAIA-EXT-011` patche le profil avec `name: "changed"` — un champ **déjà présent** — puis
  vérifie que `name` vaut `changed`. Sur alpha.23 la réponse est
  `{"item":{"name":"typicode"},"name":"changed"}` : l'assertion passe, le défaut aussi. **Vert à
  tort.**
- Le cahier vérifie qu'un id **généré** est une chaîne ; il n'envoie jamais un id **fourni** d'un
  autre type. Le sondage, si : c'est exactement l'entrée adverse de l'étape 2 de la page.

## Ce que ça dit pour #111 — des éléments, pas une décision

1. **`probe` seul atteint 1 des 2 constats d'origine**, et 2 de plus que le cahier n'a pas vus :
   **3 défauts réels contre 2**, sans cahier, sans suite générée, sans Playwright.
2. **Les deux approches ne se recouvrent qu'à moitié.** La conception (cahier) construit des
   combinaisons que la doc ne montre pas ; le sondage essaie des entrées hostiles que la conception
   juge hors chemin. Union : **4 défauts**, intersection : **1**.
3. **Ce qu'`automate` apportait en propre est ici nul** : EXT-019 et EXT-030 ont été trouvés par le
   *cahier*, que Playwright n'a fait qu'exécuter. Un `curl` par scénario aurait rendu les mêmes
   verdicts. La preuve externe que #111 attribuait à `automate` appartient au cahier
   (`generate`), pas au code exécutable.
4. **Limite** : une cible, une API REST sans interface, N = 1 exécution de chaque côté. Rien ici
   ne dit ce que vaut `automate` sur une application à navigateur, où l'exécution ne se réduit
   pas à un `curl`.

Le choix entre « le produit s'arrête au cahier » et « il va jusqu'au code » reste au fondateur.

## Fichiers

- `contract-source.md` — les 31 promesses extraites par l'agent, citées avec leur ligne.
  `README.target.md` y désigne le README de `8fb0f72`, identique octet pour octet à
  `../external-application-2026-08-08/sources/README.8fb0f72.md` (vérifié par `cmp`).
- `regressions.feature` — CP-001 à CP-003, produits par l'agent selon l'étape 5 de la page.
- `db.initial.json` — la base d'exemple du README, celle de ce sondage.
- Le rapport tabulaire de l'étape 6 n'a pas été écrit en fichier (le harnais refuse qu'un
  sous-agent écrive un rapport) ; son contenu est résumé dans le tableau ci-dessus.

Rejouer : `git -C json-server worktree add ../sut --detach 8fb0f72`, `npm install`,
`npx tsx src/bin.ts db.initial.json --port 3010`, puis les requêtes du tableau ; même chose avec
`89a34a4` pour la version corrigée.
