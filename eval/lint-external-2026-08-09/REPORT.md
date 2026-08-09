# 159 SKILL.md écrites par d'autres — et le résultat inverse la conclusion de la journée

**Date** 2026-08-09 · 12 dépôts, 159 `SKILL.md`, dont `LeoYeAI/openclaw-master-skills` (2 110 ★,
2 625 skills) et `TerminalSkills/skills` (1 018 skills)

## Pourquoi cette campagne existe

Deux outils sur deux, pointés ailleurs que sur leur propre production, portaient le même défaut :
des règles de convention maison appliquées à du matériau qui ne les a jamais adoptées. J'ai écrit
que **dix autres outils n'avaient jamais été essayés sur du matériau étranger**.

En vérifiant, la phrase était trop large : **la plupart de ces outils gardent ce dépôt par
construction** — `check_loop_wiring`, `check_agents_tier`, `check_oracle_library`,
`check_published_copies` lisent des chemins codés en dur et ne peuvent pas prendre d'entrée
étrangère. Un seul restait : **`lint_skills.py`**.

## Deux défauts dans l'outil, trouvés en le pointant ailleurs

**1. L'argument n'acceptait qu'un fichier.** Passer un répertoire le renvoyait tel quel, et le
linter tentait d'ouvrir un dossier comme un fichier — **zéro skill lintée, sans message d'erreur**.
Le cas ne s'était jamais posé : l'outil n'avait tourné que sur `plugins/`, sans argument.

**2. La règle du déclencheur mesurait notre formulation, pas la propriété.** 75 refus pour
« la description ne dit jamais QUAND l'utiliser » :

| | |
|---:|---|
| **13** | en **écriture non latine** — le motif `Use when/for/to` ne peut physiquement pas voir 用于, qui signifie littéralement « utilisé pour » |
| **62** | déclaraient leur déclencheur **autrement** : `Trigger: replace locator, locator, selector` |

Toutes disaient quand les utiliser. **Troisième fois dans la même journée** qu'une règle lexicale
pénalise une langue ou une convention plutôt qu'une lacune — après la métrique SWE-bench qui
comptait `scope` manquant quand la condition disait « portée », et les 279 sélecteurs CSS d'un
contrat publié.

Le motif accepte désormais les autres formes, et une description en écriture non latine est
**dite non jugeable** au lieu d'être refusée : *un contrôle qui ne sait pas doit se taire.*

## Le résultat, après correction

**111 → 89 défauts.** Et le tri, fait à la main :

| catégorie | n | verdict |
|---|---:|---|
| la description ne dit pas quand utiliser la skill | **53** | **réel** — vérifié : *« This skill encodes Emil Kowalski's philosophy… »*, *« The single entry point to the Conductor system »*. Elles décrivent ce que la skill **est**, jamais quand l'invoquer |
| `name` ≠ répertoire | **12** | **réel** — `13-Day Sprint Method` contre `13-day-sprint-method`, `360Guard` contre `360guard-…` : majuscules et espaces dans un nom qui doit être adressable |
| ligne de frontmatter mal formée | **7** | **réel** |
| aucun frontmatter YAML | **2** | **réel et fatal** — la skill ne se charge pas |
| `name` ≠ répertoire, répertoire nommé `skills` | 4 | **artefact de mon moissonnage** — mon script a pris le dernier segment du chemin |
| plus de 500 lignes | 10 | **notre plafond**, pas une norme publiée |

**74 constats réels sur 89.**

## Ce que ce chiffre renverse

| campagne | précision |
|---|---:|
| `automation_score` sur 62 suites Playwright | **~2 %** |
| `structural_score` sur 244 cahiers Gherkin | ~26 % avant correction |
| **`lint_skills` sur 159 skills tierces** | **83 %** |

La différence n'est pas la qualité du code de l'outil. Elle est **la nature de la règle** :

> **`lint_skills` vérifie une norme d'écriture que les tiers subissent aussi** — un `SKILL.md` sans
> frontmatter ne se charge chez personne, un `name` avec des espaces n'est adressable nulle part,
> une description sans déclencheur ne se déclenche chez personne.
>
> **`automation_score` vérifiait nos conventions** — tag `@QAIA`, POM-as-fixtures, priorité
> `@P1/@P2/@P3` — auxquelles personne d'autre n'a souscrit.

**Une règle qui encode une norme externe se transporte. Une règle qui encode une préférence
maison ne se transporte pas.** Les 506 constats faux de la journée sont presque tous du second
type, et ce n'était pas visible tant qu'un seul outil avait été essayé dehors.

## Limites

- **Corpus de commodité** : 12 dépôts d'une recherche de code, pas un échantillon représentatif des
  milliers de skills publiées.
- **Rien n'a été signalé en amont.** Ces 74 constats concernent des dépôts tiers ; les déposer est
  l'arbitrage du fondateur, et le garde-fou de l'environnement refuse la création d'issue.
- **Le plafond de 500 lignes reste appliqué en dehors de son domaine.** Il n'a pas été retiré parce
  qu'il n'a pas été mesuré : je ne sais pas s'il correspond à une limite réelle de chargement.
