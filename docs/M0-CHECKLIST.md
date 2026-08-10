# Jalon M0 — Fondations : avancement

Critère de sortie global : un contributeur externe comprend le projet et peut proposer une issue ; `claude plugin install` fonctionne ; la CI protège `main` ; le harnais d'éval existe avant toute skill.

## ✅ Fait (dans ce dépôt)

| Élément | Détail |
|---|---|
| `LICENSE` | MIT (D3) |
| `README.md` | Bilingue EN/FR, positionnement honnête (quota, apprentissage local, web-first, Claude Code first) |
| `CONTRIBUTING.md` | DCO obligatoire, règles spéciales skills (revue adversariale tracée, démonstration par l'usage, gold set non dégradé) — D28, T14 |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1, limite mainteneur-unique documentée |
| `SECURITY.md` | Signalement privé via Security Advisories, périmètre injection/supply-chain/code généré |
| Templates | Issues (Proposition avec processus de challenge, Bug) + PR (checklist DCO/skills) |
| Marketplace | `.claude-plugin/marketplace.json` + **4 plugins validés `--strict`** : `qaia-core` 0.2.35 (18 skills, parcours complet US→cahier), `qaia-playwright` 0.1.27 (14 skills), `qaia-score` 0.2.4 (4 skills), `qaia-testdata` 0.1.3 (1 skill) — **37 skills**. Les quatre sources résolvent, aucun manifeste ne déclare `hooks`/`mcpServers`/`agents` (vérifié par `check_repo_structure.py` à chaque commit). *Chiffres du 2026-08-10 ; ce tableau n'est pas couvert par `check_skill_counts.py`, qui ne lit pas ce fichier.* |
| CI | Validation JSON, structure plugins, frontmatter des skills, lint Gherkin épinglé, **gardes supply-chain** (hooks/agents/MCP interdits, sources marketplace locales), job **DCO** ; Actions épinglées par SHA (T15) |
| Harnais d'éval | `eval/RUBRIC.md` (10 dimensions, gate ≥ 16/20) + gold set durci + corpus élargi 24 cas (`eval/goldset-hardened/`, `eval/baselines/`) ; score structurel déterministe (`eval/tools/structural_score.py`) |
| Discussions activées, branch protection sur `main` (CI requise, pas de push direct), 2FA exigée pour les admins | confirmé dans `docs/STATUS.md` |
| **Organisation GitHub `QAIA-Project` créée, dépôt transféré** (`Opaland/QAIA` → `QAIA-Project/QAIA`, redirection confirmée) — URLs mises à jour partout (marketplace.json, plugin.json ×4, README×4 (racine+plugins), skill `hello`, `git remote`) | fondateur, 2026-07-28 |

## ⏳ À faire par le propriétaire (droits que l'agent n'a pas)

| # | Action | Référence |
|---|---|---|
| 1 | Ajouter un **second admin** de confiance à l'organisation `QAIA-Project` (bus factor — le transfert lui-même est fait, il reste à ne pas rester seul admin) | D14, Q73 |
| 2 | Vérifier la **disponibilité du nom QAIA** (produits IA homonymes, npm, domaine) — décider du gel du nom | Q1, D32 |
| 3 | Merger cette branche dans `main` (**squash**) puis **supprimer la branche** (son nom contient l'ancien acronyme "iats") — nécessite des droits admin que l'agent n'a pas (branch protection active sur `main`, pas de `gh` CLI disponible en session) ; à faire via l'UI GitHub ou en levant temporairement la protection | D1 |
| 4 | Activer : **GitHub Sponsors**, **Security Advisories** (private vulnerability reporting) — Discussions déjà actif | D27, SECURITY.md |
| 5 | Configurer **GitHub Projects** (board de `KANBAN.md` : colonnes, labels, WIP max 2) et importer le backlog en issues | Kanban |
| 6 | Relire le **contrat de travail** (réserve D1) — recommandé avant toute communication publique sur le projet | G1 |
| 7 | Vérifier l'installation de bout en bout depuis un autre compte : `/plugin marketplace add <org>/QAIA` puis `/plugin install qaia-core@qaia`, lancer `/qaia-core:hello` | Critère M0 |
| 8 | Recrutement de pilotes réels dans les communautés QA — **souhaitable, plus une condition d'entrée en M1** (gate G2 levée par décision du fondateur, D67, 2026-07-25) | D12, D67 |

## Critère de passage en M1

Tous les points « À faire » cochés. Le recrutement de pilotes nommément engagés (gate G2) n'est
plus une condition bloquante depuis D67 — M1 peut démarrer sur les skills du parcours dans
l'ordre, chacune évaluée au harnais avant merge, sans attendre de pilotes réels.
