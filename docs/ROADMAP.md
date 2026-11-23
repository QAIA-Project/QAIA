# QAIA — audit du 2026-11-23 et feuille de route

Écrit à la reprise, quatre semaines après le dernier commit (`737a2fb`, 2026-10-26). Ce fichier
remplace, pour l'ordre des travaux, `ACTION-PLAN.md`, `KANBAN.md` et `PLAN-REPRISE.md`, qui
décrivent l'architecture d'avant la refonte. La référence de fond reste
[la spec de refonte](superpowers/specs/2026-08-24-qaia-refonte-design.md).

## 1. Audit

### Santé technique — bonne

| | |
|---|---|
| CI sur `main` | verte (run de `737a2fb`) |
| Contrôles de `make check` | **26/26 passent** en local (rejoués un à un : `make` n'est pas installé sur la machine Windows du fondateur) |
| PR ouvertes | 0 |
| Branche | `main` = `origin/main`, arbre propre |

### Avancement de la refonte, mesuré contre sa propre spec (§7 et §8)

| Phase | Spec | Réalité | Écart |
|---|---|---|---|
| 1 — inverser le défaut | PASS par défaut sur corpus étranger **≥ 107** | **101** (0 avant) — `eval/universal-default-2026-08-24/REPORT.md` | **6 PASS manquants**, jamais réexaminés depuis |
| 2 — pointer les outils ailleurs | tous les outils du noyau éprouvés sur du matériau étranger | `drift-external`, `refutation`, suites Playwright étrangères ; aucun décompte tenu | métrique non suivie |
| 3 — 37 → 3 lecteurs | 3 lecteurs (+ `automate` en suspens) | `judge` et `generate` faits, 17 suppressions faites ; **7 skills** | `probe` à faire (#118) |
| 4 — trancher `automate` | mesure préalable, puis décision | rien | #111, bloqué sur la mesure |
| Coût d'une génération | **≤ 1,5×** un prompt direct | 2,9× au dernier relevé, **jamais remesuré** après la fusion | #96 |

### Dette que la spec avait décidée et qui n'a pas été faite (§4, §5)

- **`docs/` : 24 → 5 fichiers visés, 32 aujourd'hui.** Aucun `docs/archive/`.
- **`docs/STATUS.md` : 1 350 lignes**, censé devenir un tableau de bord de deux nombres.
- **`make check` : 26 contrôles, ~8 visés.** Plusieurs gardent des objets que la refonte supprime
  (`check_loop_wiring`, `check_agents_tier`, `check_skill_counts`…).
- **`agents-tier/` : 6 agents, suppression visée.**
- **`DECISIONS.md` toujours alimenté** (D202), censé être gelé en archive.

Ces cinq points ne sont pas des oublis de détail : la spec en fait une condition de la thèse
(« le noyau est le produit »), et ils sont réversibles d'un `git revert`.

### Outillage

- #106 — le parseur Gherkin maison de `check_nl_projection.py` lit de travers 7 formes valides,
  dont le dialecte français, où il sort **vert à vide**. Toujours ouvert.
- #108 — deux suites Playwright livrées ne tournent dans aucune CI.
- #115 — le linter Gherkin n'est pas épinglé.

### Adoption — le mur, inchangé

**0 étoile, 1 fork, 0 watcher, 0 pilote** (API GitHub, 2026-11-23). La spec fait du nombre
d'utilisateurs réels l'une de ses deux seules métriques. Aucun travail d'agent ne la fait bouger :
elle dépend de #89 (un tiers qui mène le parcours) et des gestes de distribution (#110, #114).

### Backlog

22 issues ouvertes. Plusieurs ont été écrites pour l'architecture d'avant : #93 parle de « 18
skills d'un bloc » (il y en a 7). Celles-là sont à requalifier, pas à laisser vieillir.

## 2. Feuille de route

Ordonnée par ce qui débloque le reste. **A** et **B** sont faisables par un agent sans geste
sortant ; **C** est le travail de décision du fondateur.

### A — Finir la refonte (en cours)

1. ~~**#118 — fusion `probe`** (4 → 1).~~ **Fait** (`f45c004`, D203) : **4 skills, 3 plugins.**
2. **Alléger l'appareil, comme décidé en §5.** *Fait le 2026-11-23* : 20 documents de pilotage
   sous `docs/archive/` (dont l'ancien `STATUS`), `STATUS.md` devenu un tableau de bord à deux
   nombres, `agents-tier/` supprimé, `DECISIONS.md` gelé à D203. **Écart assumé avec la spec** :
   elle retirait 8 contrôles, 2 seulement sont partis (`check_agents_tier`,
   `check_decision_register`) — les 6 autres gardent des objets qui existent toujours (copies
   publiées sur qaskills.sh, bibliothèque d'oracles, boucles A/B de `probe`, comptes affichés,
   commits déclarant du travail ouvert). Trois documents que la spec archivait restent en place
   parce qu'ils servent dehors : `PILOT-KIT` (le tunnel du site, #89), `DEMO-TARGETS` (cité par
   `probe` comme liste de cibles autorisées), `COMPETITIVE-ANALYSIS` (lié depuis le README).
3. ~~**#106**~~ **Fait** (`3dd1421`) : parseur à blocs en bibliothèque standard, les sept formes
   couvertes ou refusées explicitement, intitulés comparés.
4. **Triage du backlog** — requalifier les issues écrites pour 37 skills.

### B — Mesurer ce que la refonte promettait

1. **Les 6 PASS manquants** (101 → ≥ 107). *Fait en partie le 2026-11-23*
   ([rapport](../eval/corpus-remeasure-2026-11-23/REPORT.md)) : un faux positif du noyau trouvé et
   corrigé — le contenu des docstrings lu comme des scénarios — **PASS 109 → 115, FAIL 74 → 63**
   sur le corpus rejoué, invariant I11. **Mais** 6 des 15 dépôts gelés ont bougé : le 101 de
   référence n'est plus rejouable, et la cible ne peut pas être déclarée atteinte tant que le
   corpus n'est pas re-figé (#119).
2. **#111 — la mesure préalable.** *Faite le 2026-11-23*
   ([rapport](../eval/probe-vs-testbook-2026-11-23/REPORT.md)) : `probe` seul, mené à l'aveugle,
   trouve **1 des 2** défauts d'origine et **2 que le cahier avait manqués** — 3 défauts réels,
   tous corrigés depuis par le mainteneur. Les deux défauts d'origine venaient du cahier, pas de
   Playwright. La décision reste au fondateur (section C).
3. **#96 — le coût** de `generate` d'un seul tenant contre un prompt direct, même protocole que
   le benchmark du 2026-07-28.

### C — Gestes réservés au fondateur

| Geste | Issue | Pourquoi il ne peut pas être fait par un agent |
|---|---|---|
| Retirer les deux copies orphelines de qaskills.sh | #110 | publication externe |
| Re-soumettre une skill étroite à un marketplace | #114 | publication externe |
| Trouver un premier pilote humain | #89 | seul levier sur la métrique d'adoption |
| Trancher `automate` | #111 | décision de périmètre, après B2 |

## 3. Comment ce fichier reste vrai

Chaque point coché porte son commit. Un point qui glisse dit pourquoi, ici, pas dans un corps de
commit sans destinataire.
