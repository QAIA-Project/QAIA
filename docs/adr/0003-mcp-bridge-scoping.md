# ADR 0003 — Note de cadrage : bridge MCP optionnel pour Cursor/Copilot (#42)

- *État au 2026-11-23 : `mcp-bridge/` existe toujours, mais il ne sert que les `SKILL.md`, alors
  que les quatre skills fusionnées gardent leurs étapes dans `references/` : un client du pont
  reçoit le sommaire sans les pages (voir `mcp-bridge/README.md`, « Known gap », et #122).*
- **Statut : accepté (D116, 2026-07-28) — option "Go, Option A+B, construit maintenant".** Le
  fondateur a explicitement levé la réserve post-pilote pour ce chantier précis (contrairement
  à #29/#30). Livré : `mcp-bridge/`. Voir D116 pour le détail complet.
- ~~**Statut : proposé — en attente d'une décision du fondateur.**~~ Ce document ne tranche rien ;
  il pose la faisabilité et la compatibilité avec les garde-fous existants, comme demandé par
  #42 ("À faire (pas de développement avant tranchage) : note de cadrage... **à valider par le
  fondateur avant tout code**"). Aucune ligne de code n'a été écrite pour ce chantier.
- **Origine :** veille concurrentielle D67/D94 (`docs/COMPETITIVE-ANALYSIS.md`, point 10) —
  Agentic QE Fleet et d'autres concurrents couvrent Cursor/Copilot/Cline en plus de Claude Code ;
  QAIA est aujourd'hui Claude-Code-first par choix, rien n'est packagé pour les autres éditeurs.
- **Révise/complète :** ADR 0002 (tier opt-in pour hooks/MCP/agents), D29 (portabilité).

## Contexte technique : ce qu'un bridge MCP impliquerait réellement

Les skills QAIA sont des instructions Markdown lues et suivies par l'assistant qui les invoque
(Claude, dans Claude Code) — pas des fonctions/API. Pour rendre QAIA "utilisable" dans
Cursor/Copilot, il faut qu'un modèle **différent** (celui de Cursor/Copilot) puisse lire ces
mêmes instructions et les exécuter fidèlement. MCP (Model Context Protocol) est le mécanisme
standard pour ça : un **serveur** qui expose des *tools*/*resources* qu'un client MCP (Cursor,
Copilot, ou Claude Code lui-même) peut appeler.

Deux formes très différentes sont possibles sous ce même nom générique "bridge MCP" — la
distinction est le cœur de ce cadrage, l'issue originale ne les séparait pas :

### Option A — serveur MCP passif (resource-only)

Le serveur ne fait qu'une chose : **servir en lecture** le contenu déjà existant des skills
(`SKILL.md`, `docs/OUTPUT-CONTRACT.md`, `.qaia/knowledge/`) comme des *resources* MCP, que le
modèle de Cursor/Copilot lit et suit lui-même — exactement le rôle qu'un skill Markdown joue
déjà dans Claude Code, juste exposé par un protocole différent au lieu d'un chargement de
fichier local. **Aucune logique métier, aucun état, aucune exécution de code côté serveur** —
un simple serveur de fichiers typé MCP.

- **Faisabilité :** élevée. Une implémentation minimale (Node/Python, SDK MCP officiel) tient
  en quelques centaines de lignes ; pas de nouvelle surface de données sensibles (mêmes fichiers
  que ceux déjà lisibles localement).
- **Compatibilité avec ADR 0002 :** la lettre du garde-fou ("hooks/MCP/agents auto-exécutent du
  code dans l'environnement de l'installeur") s'applique quand même — un serveur MCP est par
  nature un **processus qui tourne**, même s'il n'exécute aucune logique métier. Reste donc
  strictement **tier opt-in** (paquet séparé, jamais installé par `qaia-core`), jamais dans le
  cœur, revue adversariale tracée comme tout composant de ce tier (même discipline que #29/#30).
- **Risque supply-chain :** faible-à-modéré — le serveur lui-même est une surface de code neuve
  à maintenir et auditer, même minimale.

### Option B — serveur MCP actif (tools/orchestration)

Le serveur exposerait des *tools* exécutant réellement une partie de la logique QAIA côté
serveur (ex. valider un manifeste, lancer `structural_score.py`, orchestrer plusieurs étapes
du parcours) plutôt que de laisser le modèle client tout interpréter lui-même depuis du texte.

- **Faisabilité :** modérée-à-élevée en effort, mais un changement d'architecture réel — ce
  n'est plus "des skills portées vers un protocole différent", c'est un **exécuteur de code
  côté serveur** au service d'un assistant tiers.
- **Compatibilité avec ADR 0002 :** tension directe avec la leçon fondatrice #2 et D33 ("pas de
  multi-agents/exécution autonome sans preuve de valeur") — cette option se rapproche
  nettement du territoire déjà explicitement écarté (agent ReAct de revue adversariale, #30,
  lui-même gelé "post-pilote" pour la même raison).
- **Risque supply-chain :** plus élevé — plus de code exécuté, plus de surface d'attaque, exige
  la même ceinture que #29/#30 (paquet séparé, doc de ce qu'il exécute, revue adversariale) mais
  avec un effort de revue proportionnellement plus lourd.

## Question de valeur, pas seulement de faisabilité

Les deux options sont techniquement faisables. La vraie question, que la seule faisabilité ne
tranche pas :

- **Aucun signal d'usage réel ne demande ça aujourd'hui.** Le mur humain reste entier (#1, 5
  pilotes jamais recrutés) — QAIA n'a pas encore de retour d'un seul utilisateur réel sur
  Claude Code, encore moins sur Cursor/Copilot. Construire un pont vers d'autres éditeurs avant
  que le cœur soit éprouvé sur son éditeur cible reprend exactement la tension déjà nommée pour
  #29/#30 (D42 : "construit seulement après pilote du cœur").
- **La différenciation actuelle de QAIA** ("zéro clé API, zéro exécution automatique", mise en
  avant dans le README et confirmée toujours valable par la veille D94) **s'applique moins
  nettement dès qu'un serveur MCP tourne en permanence** — même l'option A, la plus légère,
  nuance ce positionnement pour les utilisateurs de ce tier opt-in spécifiquement (le cœur reste
  intact pour tout le monde d'autre).

## Options pour le fondateur

1. **Ne pas construire (no-go).** QAIA reste Claude-Code-first ; la portabilité multi-LLM
   continue par la voie déjà ouverte (#58, `prompts/adapters/` — reformuler le contenu du
   prompt pour un autre modèle, sans protocole d'exécution partagé). Cohérent avec la
   discipline "pas de nouveau tier avant preuve de valeur du cœur".
2. **Go, mais Option A seulement (tier opt-in, post-pilote).** Le serveur MCP passif le plus
   proche de la philosophie existante (juste un vecteur de lecture différent) — tracé comme
   #29/#30, construit seulement après que le mur humain (#1) soit levé.
3. **Go, Option A+B (tier opt-in, post-pilote).** Investissement plus lourd, réel gain
   d'intégration (orchestration côté serveur, pas juste lecture), mais rouvre la tension
   multi-agents (D33) que le projet a choisi de ne pas rouvrir seul.
4. **Différer sans trancher maintenant.** Laisser #42 ouverte, revisiter une fois qu'un signal
   concret existe (un pilote demande explicitement Cursor/Copilot, ou un concurrent gagne du
   terrain grâce à cette couverture) — cohérent avec "ne pas inventer de travail marginal" déjà
   appliqué ailleurs dans le backlog.

## Décision

**Option "Go, A+B, construit maintenant"** (2026-07-28) — voir D116 dans `docs/DECISIONS.md`
pour le détail complet de ce qui a été livré, vérifié et revu. `mcp-bridge/README.md` documente
exactement ce que le composant exécute, conformément à la règle de transparence d'ADR 0002.
