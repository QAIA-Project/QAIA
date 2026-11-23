# Plan d'action QAIA — établi le 2026-08-08

Ce plan a une origine précise : trois analyses externes du dépôt, commandées par le fondateur à
**Gemini, ChatGPT et Mistral**. Elles ne sont pas reprises telles quelles. Chaque affirmation
chiffrée a été vérifiée contre le dépôt avant d'entrer ici, et **la moitié ne survit pas à la
vérification**. C'est le premier résultat du travail, et il vaut d'être écrit avant le plan
lui-même.

---

## Partie 1 — Ce que les trois analyses ont dit, et ce qui est vrai

### Gemini a audité un produit qui n'existe pas

Son prompt décrit QAIA comme *« un framework d'Assurance Qualité et d'évaluation automatisée pour
systèmes IA, approche multi-juge (Gemini, Mistral, Groq) »*.

**C'est faux, et l'erreur est structurante.** Le multi-juge est de l'**outillage de mainteneur**
qui vit dans `eval/` : il sert à éprouver nos propres skills, jamais à servir un utilisateur.
`eval/tools/multi_model_generate.py` le dit dans sa première ligne : *« Maintainer eval tooling
only… Never shipped to installers »*. Le produit, ce sont quatre plugins Claude Code qui
transforment une user story en cahier Gherkin puis en tests Playwright.

Conséquence : **toute la feuille de route Gemini est celle d'un autre produit.** Abstraction
LiteLLM, cache KV pour les tokens, suivi du coût financier par exécution, leaderboard public de
modèles — cela décrit un banc d'essai de LLM. Rien de tout cela n'est retenu, et les retenir
aurait coûté des mois.

Ce qui est **récupérable** chez Gemini, en revanche : le manque de `Makefile`, l'absence de
`devcontainer`/Docker, et l'idée d'un schéma d'architecture visuel dans le README. Vérifié : ni
`Makefile`, ni `Dockerfile`, ni `docker-compose.yml`, ni `.devcontainer` dans le dépôt. C'est un
vrai trou de DevEx.

### Mistral : le plan est bon, les chiffres ne le sont pas

| Affirmation | Vérification | Verdict |
|---|---|---|
| « Skills : 23+ » | `find plugins -name SKILL.md` → **30** | faux, sous-estimé |
| « Issues ouvertes : 12 » | **9** au moment de l'analyse (17 après les 8 créées ce jour) | faux |
| « Contributeurs : 2 (Opaland + Claude) » | `git log` → deux **identités git du même humain** | faux : 1 humain |
| « Ajouter des badges au README » | 5 badges déjà présents | déjà fait |
| « Créer un template Good First Issue » | `.github/ISSUE_TEMPLATE/` contient déjà 2 gabarits | partiellement fait |
| « Issue #42, bridge MCP, priorité élevée » | #42 existe mais est **fermée**, et était classée **P3** | faux |
| « Note CTO 8.5/10 » | aucune source | non vérifiable |
| « 0 étoile, 0 fork » | confirmé par l'API | **vrai** |
| Licence MIT | confirmé | **vrai** |

Le **format** de Mistral est le meilleur des trois : propriétaire, échéance, métrique de succès,
blocage. Il est repris ci-dessous. Ses **engagements** ne le sont pas : Discord, hackathon à
1000 €, partenariat ISTQB, conférences — ce sont des décisions et des dépenses qui appartiennent
au fondateur, pas des tâches qu'un agent planifie à sa place.

### ChatGPT : la seule des trois qui tient entièrement

Aucune fausse prémisse. Pas de chiffre inventé, parce qu'elle n'en avance aucun : c'est une
**méthodologie de revue**, pas un diagnostic. Deux de ses règles méritent d'être adoptées telles
quelles, parce qu'elles sont exactement ce que les deux autres ont violé :

> *« Always prefer documented evidence over assumptions. Never invent project goals. »*

Sa règle d'exécution — expliquer le problème, la solution, pourquoi c'est la meilleure option,
les risques, **puis attendre validation** — est la discipline que ce dépôt applique déjà par ADR
et par revue. Son découpage Quick Wins / court / moyen / long terme structure la partie 3.

**Ce qui est fait de cette analyse** : son prompt de revue est conservé tel quel dans
`docs/ARCHITECTURE-REVIEW-PROMPT.md` pour que toute revue future, quel que soit l'agent, parte du
même cadre.

---

## Partie 2 — L'état réel, mesuré

| Métrique | Valeur vérifiée le 2026-08-08 | Source |
|---|---|---|
| Étoiles | **0** | API GitHub |
| Forks | **0** | API GitHub |
| Humains contributeurs | **1** | `git log` |
| Skills | **30** | `find plugins -name SKILL.md` |
| Plugins | **4** | `ls plugins` |
| Issues ouvertes | **17** | API GitHub |
| Assertions prouvées non décoratives | **111/111** | `eval/mutation-proof-2026-08-08/` |
| Défauts trouvés sur un logiciel tiers | **2** | `eval/external-application-2026-08-08/` |
| Pilotes humains | **0** | — |

**Le blocage n'a pas changé de nature.** Ce n'est ni l'architecture, ni la DevEx, ni le nombre de
skills. C'est que **personne n'a jamais utilisé QAIA**. Les trois analyses le disent chacune à sa
manière, et c'est le seul point sur lequel elles convergent avec la réalité.

---

## Partie 3 — Le plan

### Règle de tri

Une action entre dans ce plan si elle satisfait l'un des deux critères :
1. elle **réduit la distance à un premier utilisateur réel**, ou
2. elle **rend une affirmation du projet vérifiable par un tiers**.

Tout le reste attend. Le catalogue n'a pas besoin de grossir tant que personne ne l'utilise.

### Quick wins — moins d'une journée chacun

| Action | Pourquoi | Issue |
|---|---|---|
| `Makefile` : `make setup`, `make test`, `make demo` | Trou de DevEx confirmé, aucun coût, réduit le temps du premier essai | à créer |
| Schéma d'architecture Mermaid dans le README | On demande à un visiteur de lire 200 lignes pour comprendre une chaîne linéaire | à créer |
| `docs/ARCHITECTURE-REVIEW-PROMPT.md` | Toute revue future part du même cadre | **fait ce jour** |
| `docs/TEST-COVERAGE-MAP.md` | Ce que QAIA couvre du métier de test, et ce qu'elle ne couvre pas | **fait ce jour** |

### Court terme — la distance au premier utilisateur

| Action | Pourquoi | Issue |
|---|---|---|
| Rapport de défaut | Le livrable quotidien d'un testeur, absent du catalogue | **#75** |
| Sélection des tests depuis un diff | Un diff, on en a un par jour ; une user story, une par sprint | **#76** |
| OpenAPI comme source d'exigence | La campagne json-server vient de prouver que partir du contrat trouve les vrais défauts | **#77** |
| Post LinkedIn | Le seul canal où se trouvent des QA que le fondateur ne connaît pas | **fondateur** |

### Moyen terme

| Action | Pourquoi | Issue |
|---|---|---|
| Plan de test et bilan | Les deux artefacts qu'un responsable lit — on ne parle aujourd'hui qu'aux testeurs | **#79** |
| Test de confirmation | Ferme la boucle du défaut ; dépend de #75 | **#80** |
| Trancher le niveau composant | Assumer un périmètre étroit **ou** le couvrir — mais l'écrire | **#78** |
| Deuxième application externe | Une seule cible, une seule API : rien ne se transporte encore | à créer |

### Long terme, et sous condition

| Action | Condition |
|---|---|
| Compatibilité navigateurs et appareils (#82) | après les court terme |
| Anonymisation de données réelles (#81) | **seulement si** on sait la vérifier — sinon ne pas la faire |
| Discord, hackathon, partenariats, conférences | décisions du fondateur, hors périmètre d'un agent |

---

## Partie 4 — Ce que ce plan ne résout pas

**Aucune ligne de ce document ne produit un utilisateur.** Il rend le produit plus complet et
plus vérifiable ; il ne le fait pas adopter. Les trois analyses externes ont chacune proposé des
dizaines d'actions et **aucune ne franchit ce mur**, parce qu'il ne se franchit pas depuis un
dépôt.

Le seul geste qui compte reste hors du code : **qu'un humain essaie**, et dise ce qu'il en pense.

---

*Établi à partir de trois analyses externes (Gemini, ChatGPT, Mistral) commandées par le
fondateur, dont les affirmations chiffrées ont été vérifiées une à une contre le dépôt. Les
erreurs relevées sont documentées en partie 1 plutôt qu'écartées en silence : une analyse fausse
qu'on corrige en public vaut mieux qu'une analyse fausse qu'on ignore.*
