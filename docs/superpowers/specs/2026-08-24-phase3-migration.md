# Phase 3 — fondre 37 skills en 3 lecteurs : le plan d'exécution

**Date** 2026-08-24 · Suite de [la spec de refonte](2026-08-24-qaia-refonte-design.md), section 4.

> **Ce document n'a pas été exécuté.** Il est le seul geste de la refonte qui soit **sortant et
> difficile à défaire** : supprimer 18 skills publiées d'un plugin que quelqu'un peut avoir
> installé. Tout le reste de la journée était réversible d'un `git revert` sans conséquence pour
> un tiers ; ceci ne l'est pas. Il attend un mot du fondateur.

## 1. Ce que la journée a appris et qui change ce plan

La spec de refonte, écrite ce matin, disait « 37 → 3 ». Trois enseignements de la journée la
corrigent avant qu'elle ne s'exécute.

**a) Restructurer, pas réécrire.** Les 37 SKILL.md pèsent 3 907 lignes et leurs `references/`
davantage. Réécrire ce volume en trois fichiers perdrait du contenu éprouvé pour un bénéfice qui
est de **surface**, pas de fond : ce qu'on veut réduire, c'est le nombre d'unités installables,
décrites et découvrables séparément — pas la connaissance. Le corps d'une skill absorbée devient
donc un fichier de `references/` du lecteur qui l'absorbe, **déplacé, pas récrit**.

**b) Un prompt n'a aucun test de non-régression.** C'est la conclusion la plus chère de la
journée : trente mutations, dix invariants et une CI verte n'ont empêché ni deux affirmations
d'être réfutées ni six régressions de passer, sur du **code**. Sur du prompt, il n'y a même pas
ça. Une fusion de 37 fichiers en une passe est donc, par construction, non vérifiable.

**c) La valeur mesurée du jour est venue du noyau, pas du parcours.** 0 → 102 PASS, 666 → 150
constats, 715 → 144 sur les suites. La fusion des skills n'apportera **aucun chiffre** ; elle
apportera de la clarté. C'est une raison suffisante de la faire, et une raison suffisante de ne
pas la faire à la sauvette.

## 2. La correspondance, fichier par fichier

### `judge` — la face prouvée, à faire en premier

| Absorbe | Devient |
|---|---|
| `qaia-core/skills/testbook-validate/SKILL.md` | le corps de `judge/SKILL.md` |
| `testbook-validate/references/*` (1 fichier) | `judge/references/` |
| `qaia-score/skills/testbook-score` | `judge/references/scoring-testbook.md` |
| `qaia-score/skills/aptitude-gate` | `judge/references/release-gate.md` |
| `qaia-score/skills/automation-score` | `judge/references/scoring-automation.md` |
| `qaia-score/skills/spec-suite-drift` | `judge/references/spec-vs-suite.md` |

**5 → 1.** C'est la face qui repose entièrement sur le noyau corrigé aujourd'hui, la seule qu'un
inconnu peut utiliser sans rien adopter, et la seule qui ne consomme aucun token de son quota.

### `generate`

| Absorbe | Fichiers |
|---|---:|
| `us-ingest`, `us-review`, `need-understanding`, `istqb-design`, `oracle-generate`, `prioritize`, `testbook-generate`, `report`, `testbook-export`, `openapi-ingest` | 10 SKILL.md + 25 fichiers de `references/` |

**10 → 1**, et les 25 références se rangent sous `generate/references/` en gardant leurs noms.
La palette de techniques ISTQB et la bibliothèque d'oracles deviennent des **données** —
`generate/references/techniques.md`, `generate/references/oracles.md` — et cessent d'être des
skills : personne n'invoque une table.

### `probe`

| Absorbe | |
|---|---|
| `qaia-playwright/skills/contract-probe`, `traffic-replay` | le corps |
| `qaia-core/skills/signal-ingest` | `probe/references/signals.md` |
| `qaia-playwright/skills/defect-report` | `probe/references/defect-report.md` — c'est un format de sortie, pas une compétence |

**4 → 1.**

### Supprimé — 18 skills, et le motif de chacune

| Skills | Motif |
|---|---|
| `a11y-audit` (346 l.), `security-surface` (299 l.), `usability-heuristic-review` (113 l.), `perf-check` (91 l.), `visual-check` (62 l.) | **911 lignes, cinq disciplines distinctes**, chacune exigeant une expertise réelle, **aucune validée par une preuve externe**. C'est de la surface « on pourrait aussi faire X ». |
| `locator-repair` (578 l.), `flaky-detect` (278 l.), `run-report` (255 l.), `confirm-fix` (110 l.), `impact-select` (100 l.) | **1 321 lignes** d'outillage de CI autour de Playwright. Besoins réels, mais ils appartiennent à qui possède le runner, pas à un moteur d'écart promesse↔tenue. |
| `rag-build`, `feedback` | L'« apprentissage ». Zéro utilisateur ⇒ zéro correction récurrente ⇒ zéro promotion en règle : jamais éprouvée une seule fois. |
| `test-plan-and-closure`, `dataset-generate` | Documents pour un destinataire qui n'existe pas encore. |
| `qaia`, `qaia-help`, `hello` | Le méta-agent routeur n'a plus rien à router avec trois portes d'entrée nommées. |

**2 232 lignes de prompt supprimées**, et c'est ce chiffre qui rend le geste sortant : il ne se
défait pas pour quelqu'un qui a déjà installé le plugin.

### En suspens

`automate` — [#111](https://github.com/QAIA-Project/QAIA/issues/111). Seule skill candidate à la
suppression qui porte une preuve externe réelle : les deux défauts confirmés de `json-server` ont
été trouvés par du Playwright généré, pas par le cahier. **Ne rien décider avant d'avoir mesuré**
combien de ces constats la face `probe` seule aurait atteints.

## 3. L'ordre, et pourquoi il n'est pas négociable

1. **`judge` d'abord, seul.** Elle repose sur un noyau mesuré aujourd'hui, ses quatre absorbées
   sont déjà minces, et le résultat est vérifiable : `check_skill_cli_claims.py` valide qu'elle
   ne prescrit rien que l'outil refuse, `lint_skills.py` valide sa forme, et le rapport `--format
   md` prouve qu'elle produit quelque chose d'utilisable.
2. **Les 18 suppressions ensuite, en un commit unique et isolé**, pour qu'un `git revert` les
   rende toutes d'un coup.
3. **`generate` en dernier**, parce que c'est la plus grosse (35 fichiers) et la moins vérifiable.

Faire (2) avant (1) laisserait le dépôt sans face de jugement pendant l'intervalle. Faire (3)
avant (1) commencerait par le morceau qu'on ne sait pas mesurer.

## 4. Ce qu'il faut changer autour, et que la spec du matin oubliait

Ces fichiers référencent le compte ou les noms des skills et casseront sinon :

- `.claude-plugin/marketplace.json` — la description de `qaia-playwright` cite nommément
  « accessibility, performance and security-surface checks » ;
- `plugins/qaia-core/CATALOGUE.md` — la table « je veux X → utilisez Y » couvre les 37 ;
- `eval/tools/check_skill_counts.py` — échouera au premier fichier supprimé, **et c'est son
  travail** ;
- `README.md` et `README.fr.md` — « 37 skills » y figure quatre fois ;
- `plugins/qaia-playwright/README.md`, `plugins/qaia-core/README.md` ;
- `docs/outreach/qaskills/SOURCES.json` — trois copies publiées dérivent de `need-understanding`,
  qui est absorbée et non supprimée : la provenance doit suivre le déplacement, sinon
  `check_published_copies.py` rougit à raison.

## 5. Ce que ce plan ne prétend pas

Il ne prétend **pas** que la fusion améliore quoi que ce soit de mesurable. Elle réduit une
surface : 37 unités installables deviennent 3 portes d'entrée nommées, et le mécanisme qui a
produit la prolifération — *tout ce que QAIA pouvait concevablement faire est devenu une skill,
parce qu'une skill est un fichier Markdown et ne coûte rien à ajouter* — se ferme avec la porte
d'entrée de la refonte : **aucune capacité n'entre sans avoir été mesurée sur du matériau
étranger.**

C'est une raison honnête. Ce n'en est pas une preuve, et le dépôt distingue les deux.
