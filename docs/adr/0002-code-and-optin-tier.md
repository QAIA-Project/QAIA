# ADR 0002 — Un peu de code, et un tier opt-in pour hooks/MCP/agents

- **Statut :** accepté (demande du fondateur, 2026-07-24 : « prends le meilleur d'IATS » +
  « tu peux faire un peu de Python et mettre des MCP, des hooks, des commands, des agents »)
- **Révise :** D14 (qui interdisait hooks/MCP/agents dans les plugins)
- **Contexte :** la lecture de la doc IATS réelle montre que ses meilleures parties (score
  **déterministe**, sniffer anti-fabrication, observabilité + budget cappé, robustesse fail-closed,
  agents ReAct) reposent sur du **code**. QAIA, distribué en **skills Markdown à un public inconnu**,
  s'était interdit tout code auto-exécuté (leçon fondatrice #2 : le public inconnu exécute avec ses
  propres permissions).

## Décision

On **prend le meilleur d'IATS** sans trahir la leçon #2, en distinguant deux natures de code :

### 1. Python *en session*, généré par un skill — AUTORISÉ et encouragé
Un skill peut **matérialiser et exécuter un script jetable** dans la session de l'utilisateur
(avec ses permissions, sous ses yeux), puis le jeter. C'est ainsi qu'on obtient le **déterminisme
d'IATS** (score structurel reproductible, sniffer) **sans shipper de code** : le plugin reste
100% Markdown. Même modèle que la génération des tests Playwright. Rien n'auto-exécute à
l'installation ; le garde-fou supply-chain (pas de `hooks/`, `agents/`, `.mcp.json` **dans les
plugins**) reste **intact**.

### 2. Hooks / MCP / agents — TIER OPT-IN séparé, jamais dans le cœur
Ceux-là **auto-exécutent du code** dans l'environnement de l'installeur. Les distribuer à un
public inconnu par défaut = l'erreur exacte que D14 prévenait. Donc :

- ils vivent dans un **tier opt-in explicitement séparé** (paquet/marketplace distinct, jamais
  installé par `qaia-core`/`qaia-playwright`/`qaia-score`) ;
- chaque composant subit la **revue adversariale tracée** de `CONTRIBUTING.md` (diff traité comme
  données non fiables, sans réseau ni write), résumé posté avant merge ;
- il est **désactivé par défaut**, documenté « ce que ce code exécute chez toi », et **jamais un
  prérequis** du cœur ;
- il n'arrive **qu'après** que le cœur soit éprouvé sur pilote (leçon #2 + issue #23).

### 3. Commands (slash) — AUTORISÉES (déjà le cas)
Une command est un **prompt** (ex. `session-review.md`). Aucun code auto-exécuté → pas de risque
de distribution. On peut en ajouter librement.

## Conséquences

- Le déterministe (score, sniffer, détecteurs C1/C2) se livre **maintenant** en skill (Python en
  session). Cf. `eval/tools/structural_score.py` (preuve) et `testbook-score` step 0.
- Les « best of IATS » qui exigent de l'auto-exécution — **hook budget/observabilité** (issue #7,
  la régression FinOps), **MCP connecteur** (Tuleap/Jira temps réel), **agent revue ReAct** — sont
  tracés comme **tier opt-in**, post-pilote, revus en adversarial. Ils ne polluent pas le cœur.
- La matrice de portabilité (D29) tient : le cœur reste utilisable en skills seules ; le tier
  opt-in est un bonus Claude Code, jamais un prérequis.

## Ce qu'on NE fait pas

- On ne met **pas** de hook/MCP/agent dans `plugins/qaia-*` (CI continue de le bloquer).
- On ne rend **pas** le déterminisme dépendant d'un binaire installé — il est généré en session.
- On ne construit pas le tier opt-in **avant** le pilote du cœur (sinon on répète la leçon #2).

## Amendement du 2026-08-09 — les scoreurs sont livrés

**Ce qui change.** `plugins/qaia-score/scripts/` contient désormais `structural_score.py`,
`automation_score.py` et `spec_suite_drift.py`. La formule « 100 % Markdown » ne s'applique plus
à ce plugin, et a été retirée du README.

**Pourquoi.** Une revue « développeur » indépendante a établi le 2026-08-09 que les trois skills
de notation demandaient au modèle de **matérialiser l'algorithme en session** depuis leur propre
prose — environ 300 lignes d'expressions régulières re-dérivées à chaque invocation. La promesse
mise en avant partout par le projet, « une note déterministe, pas une auto-notation par un LLM »,
tenait donc à l'intérieur du dépôt, où `eval/tools/*.py` sont figés et exécutés par une CI, et
s'amollissait exactement à la frontière de livraison. Deux passages sur le même fichier pouvaient
légitimement diverger. **Une note qui n'est pas reproductible n'est pas une note.**

**Ce qui ne change pas — et c'est l'essentiel.** La décision d'origine visait le code
**auto-exécuté** : hooks, agents, serveurs MCP, scripts d'installation. Rien de tout cela
n'arrive ici. Ces fichiers sont lus et lancés par Claude quand l'utilisateur invoque la skill,
avec ses droits, dans sa session — exactement ce qui se passait avant. La seule différence est
que le code est figé et lisible au lieu d'être réécrit de mémoire. **Du point de vue de la chaîne
d'approvisionnement c'est une surface plus petite, pas plus grande** : un fichier qu'on peut
diffier et épingler vaut mieux qu'un programme qu'un modèle réécrit à chaque fois.

**Ce qui reste interdit sous `plugins/` :** `hooks/`, `agents/`, `.mcp.json`, et les champs
`hooks`/`mcpServers`/`agents` d'un `plugin.json`. `eval/tools/check_repo_structure.py` le vérifie
mécaniquement à chaque passage de la CI, et rien de cet amendement ne l'assouplit.

**Le risque assumé : la copie.** Les fichiers livrés sont des copies des originaux de
`eval/tools/`. Une copie sans surveillance cesse silencieusement de correspondre — c'est la faute
corrigée quatre fois dans la journée même de cette décision. Elle part donc avec son garde-fou :
`check_repo_structure.py` compare les octets et la CI échoue à la moindre divergence ;
`python eval/tools/ship_scorers.py` refait la copie et **constitue le point de décision** — la
lancer veut dire « j'ai regardé ce qui change pour l'utilisateur du plugin, et je l'assume ».
