# Soumissions aux annuaires — état et textes prêts

Suivi de #69 et #73. Mis à jour le 2026-08-08 ; **états revérifiés contre l'API GitHub le 2026-11-23**.

| Annuaire | ★ | État | Action |
|---|---|---|---|
| [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | 2 608 | **PR fermée sans fusion le 2026-09-01 — [#1163](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1163)** | voir [`../marketplace-resubmission.md`](../marketplace-resubmission.md) et #114 : re-soumettre une skill étroite, après un pilote |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 51 858 | **soumise le 2026-08-08 — [#2466](https://github.com/hesreallyhim/awesome-claude-code/issues/2466), validation automatique passée ; toujours ouverte au 2026-11-23** | attendre la revue humaine, ne pas relancer |
| QASkills.sh | — | compte à créer | voir #73 |
| claudemarketplaces.com | — | à explorer | |
| claudepluginhub.com | — | à explorer | |
| aitmpl.com | — | à explorer | |
| SkillsMP / ClawHub / skills.sh / Smithery | — | à explorer | |
| [mxschmitt/awesome-playwright](https://github.com/mxschmitt/awesome-playwright) | 1 547 | **PR fermée sans fusion le 2026-08-12 — [#177](https://github.com/mxschmitt/awesome-playwright/pull/177)** | geste du fondateur s'il veut retenter |
| [TheJambo/awesome-testing](https://github.com/TheJambo/awesome-testing) | 2 329 | **PR fermée sans fusion le 2026-08-22 — [#201](https://github.com/TheJambo/awesome-testing/pull/201)** | geste du fondateur s'il veut retenter |
| [naodeng/awesome-qa-skills](https://github.com/naodeng/awesome-qa-skills) | 151 | **écarté volontairement** | voir §4 |

---

## 4. Les listes de liens — et celle qu'on a écartée

**`mxschmitt/awesome-playwright` — PR [#177](https://github.com/mxschmitt/awesome-playwright/pull/177).**
Section `AI & Agents`, qui ne contenait que **deux** entrées (Playwright Agent CLI et Playwright
MCP, toutes deux officielles). Liste maintenue par un membre de l'équipe Playwright : public
exactement ciblé, et un emplacement non encombré. La PR argumente sur ce qui est
Playwright-pertinent — POM-as-fixtures, locators par rôle, et la suite générée qui tourne en CI
sans session Claude — plutôt que sur QAIA en général.

**`TheJambo/awesome-testing` — PR [#201](https://github.com/TheJambo/awesome-testing/pull/201).**
Section `AI & LLM Testing`, où **QASkills.sh figure déjà**. Liste QA généraliste de référence,
poussée en continu.

Les deux PR déclarent l'état pré-alpha et proposent explicitement au mainteneur de refuser sur
des critères de maturité.

### `naodeng/awesome-qa-skills` : écarté, et le motif compte

151 ★, poussé quotidiennement, et **exactement notre niche** — c'est le candidat qui avait le
meilleur rapport signal/bruit sur le papier.

Mais ce n'est **pas une liste de liens** : contribuer signifie verser une skill complète dans
*leur* structure — `SKILL.md`, `quick-start.md`, `output-formats.md`, `prompts/`, `agents/`,
`evals/`, `references/`. Sept fichiers, leur schéma de métadonnées, leur arborescence. Aucune
section ne permet de simplement lier un projet externe (vérifié : `resources/` ne contient que
`ci-cd`, `examples`, `templates`).

**Ce serait une troisième copie divergente**, après le dépôt QAIA et les copies QASkills. On
vient de passer deux fois par cette dette — `OUTPUT-CONTRACT.md` (#66) et les copies QASkills —
et de la solder à chaque fois en posant un contrôle automatique. Ajouter une troisième variante,
dans un schéma qui n'est pas le nôtre, pour 151 étoiles, c'est rouvrir la dette au pire endroit :
là où le contrôle serait le plus coûteux à écrire.

**À reconsidérer** si leur dépôt ouvre une section de liens externes, ou si QAIA a assez
d'utilisateurs pour que l'effort de synchronisation se justifie.

---

## 1. jeremylongshore/claude-code-plugins-plus-skills — FAIT

PR [#1163](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/1163), ouverte
le 2026-08-08 depuis le fork `Opaland/`.

Chemin « Path B » que leur `CONTRIBUTING.md` désigne explicitement comme **la voie recommandée
pour les plugins tiers** : une seule entrée ajoutée à `sources.yaml`, `README.md` non touché,
rien de vendorisé. Leur dépôt reste le miroir, le nôtre reste la source de vérité, et une synchro
hebdomadaire (lundis 06:00 UTC) reprend nos pushs.

Entrée soumise : `qaia-core`, `source_path: plugins/qaia-core`, `target_path:
plugins/testing/qaia-core`, MIT, `verified: false`.

La PR déclare l'état pré-alpha en tête, cite les 2,4/5 et 5,0/10, et **propose explicitement au
mainteneur de refuser sur des critères de maturité** — c'est un pari : sur ce genre de dépôt,
une soumission qui annonce ses faiblesses passe mieux qu'une qui les cache et se fait attraper.
Elle signale aussi que `qaia-core` n'a pas de `SKILL.md` racine (c'est un bundle de skills) et
propose deux alternatives si leur catalogue l'exige.

**Si la PR est refusée** : ne pas insister, ne pas rouvrir. Noter le motif dans #73.

---

## 2. hesreallyhim/awesome-claude-code — FAIT le 2026-08-08

**51 858 étoiles, poussé quotidiennement. C'est l'annuaire qui compte le plus.**

Soumise : **[issue #2466](https://github.com/hesreallyhim/awesome-claude-code/issues/2466)**,
catégorie `Skills` (leurs 16 catégories n'incluent ni testing ni QA — `Skills` est le seul choix
littéralement exact), **validation automatique passée** le jour même, label `validation-passed`.
En attente de revue humaine, qui est discrétionnaire et sans délai annoncé.

**Ne pas relancer.** Leur `CONTRIBUTING.md` est explicite sur le fait qu'une recommandation ne
crée aucun contrat, et un mainteneur relancé refuse.

⚠️ **Ne pas soumettre par l'API.** Leur `CONTRIBUTING.md` est explicite :

> ALL RECOMMENDATIONS MUST BE MADE USING THE WEB UI ISSUE FORM TEMPLATE, OR YOU RISK BEING
> RESTRICTED FROM INTERACTING WITH THIS REPOSITORY TEMPORARILY.

Le risque, c'est ton compte GitHub restreint sur le dépôt le plus visible de l'écosystème. Une
soumission automatisée qui contourne le formulaire ne vaut pas ça. **Cette étape est à cliquer,
pas à scripter.**

**Éligibilité — vérifiée :** leur règle est « ≥ 14 jours depuis le premier commit ET
développement actif » OU « ≥ 100 étoiles ». QAIA : premier commit le 2026-07-23, soit **16 jours**,
avec des commits quasi quotidiens. La première branche passe. ✅

**Une seule ressource à la fois** — ne pas soumettre les quatre plugins.

👉 **[Ouvrir le formulaire](https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml)**

À coller dans les champs :

- **Resource name** : `QAIA`
- **URL** : `https://github.com/QAIA-Project/QAIA`
- **Category** : celle qui correspond le mieux à *tooling / workflows* (le formulaire propose une
  liste ; ne pas forcer une catégorie qui ne colle pas)
- **License** : `MIT`
- **Description** :

```
Claude Code plugins that take a user story to a traceable Gherkin test book — stable
scenario IDs, an acceptance-criterion coverage matrix, and ambiguous criteria surfaced as
open questions rather than silently resolved — then to native Playwright tests. Markdown
skills only: no API key, no MCP server, no hooks, nothing that executes on its own.
Pre-alpha and says so: no human pilot yet, and its own external audit scores (2.4/5, 5.0/10)
are published in the repo.
```

Leur note à lire avant de cliquer, et qui est juste : *« si "être sur la liste" fait partie de ta
stratégie promotionnelle, prévois un plan B »*. La soumission coûte deux minutes et ne doit pas
être attendue comme un levier. Le plan B, ce sont les autres lignes du tableau.

---

## 3. QASkills.sh — 7 skills pretes, 5 categories couvertes

**Compte cree le 2026-08-08** (`opaland`). Voie de publication tranchee apres verification de
leur chaine : leur guide documente `@qaskills/skill-validator` (**404 sur npm**),
`npx @qaskills/cli login` (**commande inexistante** en 0.4.1) et `/dashboard/tokens` (**404**).
La seule voie qui fonctionne est l'assistant web du dashboard — et il accepte une URL de
**sous-dossier**, l'etape 2 etant un formulaire manuel et non un parseur. Donc aucun depot dedie
n'est necessaire.

| Copie | Categorie | Etat au 2026-08-08 | Score qualite |
|---|---|---|---|
| `ambiguity-hunt` | E2E | **publiee** | 85/100 |
| `accessibility-audit` | **Accessibility** | **publiee** | **100/100** |
| `security-surface-checks` | **Security** | **publiee** | **100/100** |
| `istqb-technique-selection` | E2E / regression | prete | — |
| `generated-test-self-review` | E2E / API | prete | — |
| `performance-check` | **Performance** | prete | — |
| `visual-regression` | **Visual** | prete | — |

**Moyenne du compte : 95/100** sur trois skills, zero installation — donc portee entierement par
la profondeur de contenu et la fraicheur, les deux seuls criteres de leur formule qui ne
dependent pas d'utilisateurs.

**Le signal a exploiter.** Les deux skills a 100 sont les concretes : outillage nomme, protocoles,
code, cas limites. Celle a 85 est la methodologique. Leur guide dit exactement ca (« sois
specifique et opinione », « inclus des exemples de code », « couvre les cas limites ») et le
bareme le confirme. Pour les quatre restantes, envoyer d'abord `visual-regression` et
`performance-check`, qui ressemblent aux deux gagnantes.

**Rythme volontaire : trois publications le meme jour depuis un compte cree le matin, c'est le
maximum qui ne ressemble pas a du remplissage.** Sur un annuaire cure, l'impression compte autant
que le contenu. Les quatre restantes partent dans quelques jours.

Les quatre dernieres existent parce que les trois premieres tombaient toutes dans la meme zone :
publier trois skills qui se rangent en E2E, c'est occuper une case sur huit de leur navigation
par categorie. Les quatre ajoutees correspondent **au mot pres** a une categorie de leur liste.

Toutes sont surveillees par `eval/tools/check_published_copies.py` : chaque copie enregistre le
sha256 de ses sources, et la CI echoue en nommant la copie a relire des qu'une source bouge.

### Ancien etat

Voir #73. Nécessite la création d'un compte, donc le fondateur. Le catalogue accepte les
soumissions tierces (« Publish a Skill », dashboard ou CLI) et il est adossé à The Testing
Academy — 189 000+ abonnés YouTube, c'est-à-dire l'audience QA exacte.

Décision à prendre avant de soumettre : **des skills individuelles** (leur unité, meilleure
découvrabilité, mais QAIA y perd sa cohérence de chaîne) ou **une entrée pointant vers le
marketplace QAIA** (notre unité, plus fidèle, moins bien référencée). Recommandation : commencer
par deux ou trois skills qui tiennent debout seules — `istqb-design`, `us-review`,
`security-surface` — et lier le marketplace depuis leur description.

---

## 5. Le marketplace communautaire officiel d'Anthropic — la plus grosse trouvaille

**C'est le référencement le plus élevé possible pour un plugin Claude Code, et il nous manquait.**

Anthropic maintient **deux** marketplaces publics :

- **`claude-plugins-official`** — curé par Anthropic, **aucun processus de candidature**, inclusion
  à leur seule discrétion. Rien à faire, rien à demander.
- **`claude-community`** — le marketplace communautaire public où atterrissent les soumissions
  tierces après revue. Les utilisateurs l'ajoutent avec
  `/plugin marketplace add anthropics/claude-plugins-community` et installent en `@claude-community`.
  **C'est un chemin de découverte de premier ordre à l'intérieur même de Claude Code**, pas un
  site tiers.

### Comment soumettre — et quel formulaire

Deux formulaires existent, et **un seul nous concerne** :

| Formulaire | Pour qui |
|---|---|
| [claude.ai/admin-settings/directory/submissions/plugins/new](https://claude.ai/admin-settings/directory/submissions/plugins/new) | **exige une organisation Team ou Enterprise** avec accès à la gestion d'annuaire — pas notre cas |
| **[platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)** | **auteurs individuels hors organisation Team/Enterprise — c'est nous** |

**Prérequis déjà satisfait.** La doc demande de lancer `claude plugin validate` avant de
soumettre, la revue rejouant le même contrôle. Vérifié sur les quatre plugins, en `--strict` :

```
plugins/qaia-core        ✔ Validation passed
plugins/qaia-playwright  ✔ Validation passed
plugins/qaia-score       ✔ Validation passed
plugins/qaia-testdata    ✔ Validation passed
```

**Ce qui se passe après approbation** : le plugin est épinglé à un SHA de commit dans
[`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community),
et leur CI avance l'épingle automatiquement à chaque push. Le catalogue public se synchronise la
nuit, donc il y a un délai entre l'approbation et l'apparition dans `marketplace.json`.

**SOUMIS le 2026-08-08** via [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit).

Ce qui a ete declare : depot `QAIA-Project/QAIA`, chemin `plugins/qaia-core`, page d'accueil le
site GitHub Pages, nom `qaia-core` (le slug est **immuable** apres publication, il doit
correspondre au `plugin.json`), licence MIT, contact l'e-mail du fondateur.

**Plateforme cochee : Claude Code uniquement, pas Claude Cowork.** Le formulaire demande de tester
le plugin sur les surfaces declarees avant de soumettre ; QAIA est eprouve sur Claude Code et n'a
jamais tourne sur Cowork. Cocher les deux aurait ete une affirmation non soutenable, exactement le
genre de chose qui se retourne en revue.

**URL de politique de confidentialite laissee vide** (facultative) : QAIA ne collecte rien, pas de
backend, pas de cle API, aucune donnee ne sort de la session de l'utilisateur. Inventer une URL
aurait ete pire que le champ vide.

Revue manuelle, delai non annonce, et leur propre encart precise que **la soumission ne garantit
pas l'inclusion**. Si accepte : epinglage a un SHA de commit dans le catalogue, leur CI suit les
push, synchro nocturne. Verifier l'apparition dans
[le catalogue communautaire](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json).

## 6. ClaudePluginHub

[claudepluginhub.com/tools/submit-plugin](https://www.claudepluginhub.com/tools/submit-plugin) —
le formulaire ne demande **qu'une URL de dépôt public**, pour mettre en file de validation et
d'indexation. Leur auto-découverte scanne GitHub Code Search régulièrement, mais un dépôt jeune ou
peu actif peut mettre des jours à être indexé : la soumission directe court-circuite ça.

**Bloqué sur une connexion**, également.

## 7. Recherche web fraîche du 2026-08-08 — ce qui reste, vérifié

Recherche menée sans partir de la liste existante, pour éviter de re-trouver ce qu'on connaissait.
Activité de chaque candidat GitHub vérifiée par API, pas supposée.

### Fait dans la foulée

**[Prat011/awesome-llm-skills](https://github.com/Prat011/awesome-llm-skills)** — 1 450 ★, PR
[#206](https://github.com/Prat011/awesome-llm-skills/pull/206). Section « Development & Code
Tools », qui contient déjà `pypict-claude-skill` (tests par paires) et `playwright-skill` : QAIA
les complète plutôt qu'il ne les double. La PR répond point par point à leurs étapes de
contribution, **y compris en refusant la case « testé sur plusieurs plateformes »** — QAIA est
éprouvée sur Claude Code, la portabilité vers Codex ou Gemini CLI est revendiquée et non
démontrée, donc ces plateformes ne sont pas listées.

### Non retenus, avec le motif

| Liste | ★ | Motif |
|---|---|---|
| `heilcheng/awesome-agent-skills` | 6 073 | la plus grosse, mais **poussée le 2026-04-05** — quatre mois d'inactivité, une PR y dort |
| `caramaschiHG/awesome-ai-agents-2026` | 1 548 | poussée le 10/06, et « 300+ ressources, 20+ catégories » sans curation visible : le volume dilue |
| `ARUNAGIRINATHAN-K/awesome-ai-agents-2026` | 288 | trois listes homonymes créées la même année, profil de dépôt SEO |
| `Zijian-Ni/awesome-ai-agents-2026` | 216 | idem |
| `aloth/awesome-ai-agents` | 20 | trop petite pour l'effort |

Un dépôt à 6 000 étoiles qui ne bouge plus vaut moins qu'un dépôt à 1 400 étoiles vivant : la
seule chose qui compte, c'est qu'un mainteneur lise la PR.

### Canaux hors GitHub, par valeur — non faits, ils demandent le fondateur

1. **[TestGuild](https://testguild.com/)** — **41 000 ingénieurs QA**, un podcast de 589 épisodes,
   et une invitation explicite à proposer un outil ou à demander à être invité. C'est la plus
   grosse audience QA ciblée trouvée, et elle est adressable par un formulaire.
2. **Slack Ministry of Testing** — ~25 000 membres, la communauté QA la plus active. D12 la
   désignait comme canal pilote dès M0 ; toujours pas approchée.
3. **r/softwaretesting** — distinct de r/QualityAssurance, et souvent plus technique.
4. **[DevHunt](https://devhunt.org/)** — plateforme de lancement hebdomadaire dédiée aux outils
   pour développeurs, fenêtre d'une semaine au lieu de 24 h.
5. **AlternativeTo** — pas un lancement, un actif SEO durable : les gens y cherchent « alternative
   à X » pendant des années.
6. **Indie Hackers** — pour du *build in public*, pas pour une annonce produit.

**Ce qu'il ne faut pas faire de cette liste** : la dérouler entièrement. Six canaux tièdes valent
moins qu'un seul où l'on répond aux commentaires. TestGuild et le Slack Ministry of Testing sont
les deux qui touchent exactement l'audience visée par #1 — les cinq pilotes.

## Règle générale pour les prochains

1. **Une soumission par annuaire, jamais de relance.** Un mainteneur relancé refuse.
2. **Lire le CONTRIBUTING avant, en entier.** Le premier annuaire de cette liste restreint les
   comptes qui contournent son formulaire ; ce n'est probablement pas le seul.
3. **Déclarer l'état pré-alpha dans chaque soumission.** C'est ce qui distingue QAIA du bruit, et
   ça évite le retrait humiliant six semaines plus tard.
4. **Consigner ici** : date, lien, résultat. Y compris les refus, avec leur motif.
