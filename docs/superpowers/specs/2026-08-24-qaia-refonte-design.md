# QAIA — refonte depuis zéro

**Date** 2026-08-24 · Décision du fondateur : garder trois faces (juger, générer, sonder),
abandonner l'arrêt. Ce document remplace l'architecture en 4 plugins / 37 skills.

## 1. Le constat qui déclenche la refonte

Six faits, tous tirés du dépôt lui-même, aucun d'une opinion extérieure.

| # | Fait | Source |
|---|---|---|
| F1 | QAIA coûte **2,9×** un bon prompt direct (133 100 vs 46 548 tokens) et rappelle **3/4** ambiguïtés plantées contre **4/4** au prompt direct | `eval/baselines/qaia-vs-direct-prompt-benchmark-2026-07-28.md` |
| F2 | **1 étoile, 0 fork, 0 watcher, 0 pilote humain** après 20 jours plein temps et 330 commits | API GitHub, 2026-08-24 |
| F3 | En conditions externes : **~30 constats bruts → 4 publiables → 1 accepté** (1 fermée par bot, 1 fermée sans reformatage, 1 supprimée par le mainteneur) | `docs/STATUS.md`, campagnes 2026-08-11 |
| F4 | Pointé sur 244 cahiers écrits ailleurs, le scoreur rendait **0 PASS** et **463 de ses 622 constats portaient sur des conventions QAIA** ; `traceability` valait 0 par construction | `eval/gherkin-external-2026-08-09/REPORT.md` |
| F5 | Le **même défaut** (barème encodant des conventions maison) commis deux fois en deux outils à un jour d'écart, la leçon ayant été écrite entre les deux | idem |
| F6 | **Aucun des dix autres outils** de `eval/tools/` n'a jamais été essayé sur du matériau étranger ; plusieurs ne le peuvent pas (chemins codés en dur) | `eval/lint-external-2026-08-09/REPORT.md` |

**La cause unique.** F1, F4, F5 et F6 sont le même mécanisme : *l'outil ne sait pas distinguer
« ce test est mauvais » de « ce test n'est pas de moi »*, parce qu'il n'a jamais rien lu d'autre
que sa propre production. F2 et F3 en sont la conséquence commerciale : un outil qui recale tout
ce qui n'est pas lui n'a pas d'utilisateur possible qui n'ait d'abord tout adopté.

**Ce que le correctif partiel prouve.** `--third-party` retire les deux règles de convention et
remet le barème à l'échelle : la médiane passe de 57 à **77**, les portes de 0 PASS à **107 PASS /
45 CONCERNS / 92 FAIL**, les constats de 622 à **159** — et les 92 échecs restants tiennent
(pas de `Then`, `Then` non vérifiable, doublons, étapes tronquées), dont un défaut réel confirmé
chez `alphagov/whitehall`. **Le signal universel existe. Il était enterré sous la convention.**

## 2. La thèse

**QAIA n'est pas un générateur de tests. C'est un moteur d'écart entre une promesse et ce qui
prétend la tenir.**

| Face | La promesse | Ce qui prétend la tenir | Sortie |
|---|---|---|---|
| **Générer** | une US, une spec OpenAPI | *rien encore* | le cahier |
| **Juger** | une US, une spec | un cahier déjà écrit, par qui que ce soit | l'écart |
| **Sonder** | la doc d'un logiciel | le logiciel qui tourne | l'écart |

Générer est le cas dégénéré où le second terme est vide. Les trois faces partagent le même noyau
et ne diffèrent que par la porte d'entrée — c'est ce qui permet de les garder toutes les trois
sans revenir à 37 skills.

## 3. L'architecture

```
        US / OpenAPI ──┐
    cahier existant ───┼──► [ 3 lecteurs minces (LLM, Markdown) ]
      app + sa doc ────┘              │
                                      ▼
                        ┌──────────────────────────────┐
                        │  NOYAU DÉTERMINISTE (Python) │
                        │  · le contrat d'affirmation  │
                        │  · les contrôles universels  │
                        │  · le score, reproductible   │
                        └──────────────────────────────┘
                                      │
                                      ▼
                     un manifeste + un rendu, identiques
                     quelle que soit la porte d'entrée
```

**Le noyau est le produit.** C'est la seule couche que F1 désigne comme portant la valeur (« la
forme et les contrôles, pas le parcours »), la seule testable, la seule qu'un test de
non-régression peut casser. Les trois lecteurs LLM sont minces et interchangeables : leur unique
travail est de remplir le contrat.

### 3.1 Le contrat d'affirmation

Une unité, partagée par les trois faces. Chaque affirmation porte :

| champ | sens | universel ? |
|---|---|---|
| `id` | identifiant stable, survit à la régénération | convention |
| `source` | l'endroit de la promesse dont elle découle | **oui** |
| `claim` | ce qui est affirmé, sous forme vérifiable | **oui** |
| `evidence` | l'assertion concrète qui le prouve | **oui** |
| `confidence` | `high` / `low` — et `low` **impose** une question ouverte liée | **oui** |
| `openQuestion` | l'ambiguïté déclarée plutôt que résolue en silence | **oui** |
| `technique` | la technique ISTQB qui l'a produite | convention |
| `priority` | P1/P2/P3 | convention |

### 3.2 La règle qui remplace `--third-party`

**Le barème universel est le défaut. Les conventions QAIA sont une surcouche opt-in.**

- Un contrôle universel juge une propriété vraie de tout test, quel que soit son auteur :
  l'assertion est-elle vérifiable ? le scénario est-il atomique ? existe-t-il un résultat
  attendu ? l'ambiguïté est-elle déclarée ? y a-t-il des chemins négatifs ?
- Un contrôle de convention (`@P1`, tag de technique, `@QAIA-<ID>`) est **signalé, jamais compté,
  jamais bloquant** — sauf si l'utilisateur demande explicitement le profil QAIA.
- **Aucun contrôle ne peut entrer dans le barème universel sans avoir tourné sur un corpus
  étranger.** C'est la porte d'entrée qui remplace les 25 portes de sortie actuelles.

### 3.3 Métrique n°1 du projet

**Le taux de PASS sur du matériau que QAIA n'a pas écrit**, mesuré sur le corpus gelé de 244
cahiers (`eval/gherkin-external-2026-08-09/corpus.json`, sha256 par dépôt).
Référence : **107/244 (44 %)**. C'est la première métrique de l'histoire du projet qui ne dépende
pas de sa propre production. Elle remplace `docs/STATUS.md` comme tableau de bord.

## 4. Ce qui survit des 37 skills

**37 → 3 lecteurs + 1 noyau + 2 bibliothèques de référence.**

Le mécanisme de la prolifération est nommable : *tout ce que QAIA pouvait concevablement faire est
devenu une skill, parce qu'une skill est un fichier Markdown et ne coûte rien à ajouter.* La
plupart des 37 ne sont pas des compétences mais **des étapes de pipeline ou des données de
référence** — et ni l'une ni l'autre n'a besoin d'être une unité installable, décrite et
découvrable séparément.

| Nouveau | Absorbe | Compte |
|---|---|---|
| **`juger`** | `testbook-validate`, `testbook-score`, `aptitude-gate`, `spec-suite-drift`, `automation-score` | 5 → 1 |
| **`générer`** | `us-ingest`, `us-review`, `need-understanding`, `istqb-design`, `oracle-generate`, `prioritize`, `testbook-generate`, `report`, `testbook-export`, `openapi-ingest` | 10 → 1 |
| **`sonder`** | `contract-probe`, `traffic-replay`, `signal-ingest`, `defect-report` | 4 → 1 |
| *bibliothèque* | la palette de techniques ISTQB, la bibliothèque d'oracles (Luhn, ISO 8601, RFC 5322…) — **données, pas skills** | 2 fichiers |

**Supprimé, sans domicile dans la thèse (18 skills) :**

- `a11y-audit`, `perf-check`, `security-surface`, `visual-check`, `usability-heuristic-review` —
  cinq disciplines distinctes, chacune exigeant une expertise réelle, **aucune validée par une
  preuve externe**. C'est de la surface « on pourrait aussi faire X ».
- `flaky-detect`, `locator-repair`, `impact-select`, `confirm-fix`, `run-report` — outillage de
  CI autour de Playwright. Besoins réels, mais ils appartiennent à qui possède le runner, pas à
  un moteur d'écart promesse↔tenue.
- `rag-build`, `feedback` — l'histoire de l'« apprentissage ». Zéro utilisateur, donc zéro
  correction récurrente, donc zéro promotion en règle : jamais éprouvée.
- `test-plan-and-closure`, `dataset-generate` — génération de documents pour un destinataire qui
  n'existe pas encore.
- `qaia`, `qaia-help`, `hello` — le méta-agent routeur n'a plus rien à router avec trois portes
  d'entrée nommées.

**En suspens, une seule vraie question ouverte** *(marquée telle plutôt que tranchée en silence)* :
`automate` (Gherkin → Playwright exécutable). Le produit s'arrête-t-il au cahier, ou va-t-il
jusqu'au code qui tourne ? C'est la seule skill supprimée qui porte une preuve externe réelle
(les deux défauts de `json-server` ont été trouvés par du Playwright généré, pas par le cahier).
**Traitée en phase 4, pas maintenant** — [#111](https://github.com/QAIA-Project/QAIA/issues/111).

**`agents-tier/` (8 agents) : supprimé.** Son propre README concède que deux seulement méritent une
fenêtre de contexte et que `tools:` n'est pas une frontière de capacité. Avec un noyau et trois
lecteurs, il n'y a plus de phase à nommer.

## 5. Ce qui survit de `docs/` et de l'appareil de gouvernance

**24 fichiers `docs/` → 5.** Survivent : les 8 ADR (décisions de frontière, peu coûteuses — 0002,
0003, 0005 et 0007 à relire contre le nouveau périmètre), `DECISIONS.md` **gelé en archive
historique** (201 entrées, plus maintenu), `OUTPUT-CONTRACT.md` (devient le contrat d'affirmation),
`CONTRIBUTING.md`, `SECURITY.md`. Les 18 autres (ACTION-PLAN, KANBAN, PLAN-REPRISE, REVUE,
IATS-RETROSPECTIVE, M0-CHECKLIST, DELIVERY, DEMO-TARGETS, DISCOVERY, EPIC-…, OWNER-GUIDE,
PILOT-KIT, BMAD-ANALYSIS, USING-QAIA-WITH-BMAD, ISTQB-CTGENAI-MAPPING, TEST-COVERAGE-MAP, les
deux `*-REVIEW-PROMPT`) partent en `archive/`.

`docs/STATUS.md` (1 316 lignes) est remplacé par un tableau de bord de deux nombres : **le taux de
PASS sur corpus étranger**, et **le nombre d'utilisateurs réels**.

**Les 25 contrôles de `make check` → environ 8.** `check_skill_counts`, `check_loop_wiring`,
`check_agents_tier`, `check_published_copies`, `check_decision_register`, `check_open_work_issue`,
`check_retired_framing`, `check_oracle_library` gardent des objets qui disparaissent : ils partent
avec eux. Restent les contrôles qui testent **le noyau**, qui devient du vrai code avec de vrais
tests unitaires — plus un prompt qu'on garde par des greps.

**La porte d'entrée remplace les portes de sortie.** L'appareil actuel est fait de contrôles qui
vérifient *a posteriori* que le dépôt a bien écrit ce qu'il devait. Le nouveau n'en a qu'un :
*aucune capacité n'entre dans le produit avant d'avoir été notée sur du matériau étranger.* C'est
le seul contrôle qui aurait attrapé F4, F5 et F6 — et aucun des 25 ne les a attrapés.

## 6. Traitement des erreurs et des cas limites

- **Non notable ≠ zéro.** Un fichier dont aucun scénario n'est extractible rend `UNSCORED`, jamais
  un `20/100 FAIL` muet — règle déjà présente (#105), promue au rang d'invariant du noyau.
- **Dialecte inconnu.** Un mot-clé Gherkin non reconnu produit un constat nommé, pas une pénalité.
- **Convention absente.** Jamais une pénalité sur le chemin par défaut ; un constat de niveau
  information, explicitement étiqueté « convention QAIA, exclue du score ».
- **Langue et écriture.** Aucune règle lexicale ne peut pénaliser une formulation : le défaut
  `lint_skills` (13 refus pour écriture non latine, 62 pour une autre formulation du déclencheur)
  devient un cas de test du noyau.
- **Sonder** n'applique jamais de correctif et ne s'exécute que contre une cible auto-hébergée ou
  explicitement autorisée — invariant conservé tel quel de `contract-probe`.

## 7. Vérification

La refonte est réussie si, et seulement si, les trois nombres suivants bougent dans le bon sens :

| Métrique | Aujourd'hui | Cible |
|---|---|---|
| PASS sur les 244 cahiers étrangers, **sans drapeau** | 0 | **≥ 107** (le niveau que `--third-party` atteint déjà en opt-in) |
| Coût d'une génération vs prompt direct | 2,9× | **≤ 1,5×** |
| Outils de `eval/tools/` ayant tourné sur du matériau étranger | 2 sur 12 | **tous ceux du noyau** |

Aucune de ces trois métriques ne peut être satisfaite en écrivant un document.

## 8. Séquence

1. **Phase 1 — inverser le défaut.** Le barème universel devient le chemin par défaut ; la
   convention QAIA devient `--profile qaia`. Rejouer le corpus gelé de 244 et publier le nombre.
2. **Phase 2 — pointer les dix outils restants ailleurs.** F6 dit que personne ne l'a fait ;
   chaque défaut trouvé est une preuve non auto-référentielle, la denrée qui manque le plus.
3. **Phase 3 — fondre 37 en 3.** Après les phases 1 et 2, parce que fondre avant de savoir ce que
   les contrôles supposent reviendrait à figer les suppositions.
4. **Phase 4 — trancher `automate`.**
