# QAIA — plateforme QA agentique, open source

[![CI](https://github.com/QAIA-Project/QAIA/actions/workflows/ci.yml/badge.svg)](https://github.com/QAIA-Project/QAIA/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Site](https://img.shields.io/badge/site-qaia--project.github.io-3b5bdb)](https://qaia-project.github.io/QAIA/)

> 🇬🇧 [Read this README in English](README.md)

**Une user story en entrée. Un cahier de test Gherkin traçable et des tests Playwright
exécutables en sortie** — sous forme de plugins Claude Code qui tournent dans *votre* session.
Pas de clé API, pas de backend, aucune donnée ne quitte votre session au-delà de ce que vous
envoyez déjà à Claude.

## Le produit entier en un écran

Un critère d'acceptation, tiré de [`eval/gold-set/US-004-expense-approval.md`](eval/gold-set/US-004-expense-approval.md)
(l'original est en anglais, ceci est une traduction) :

> Un rapport sous 500 € au total demande une approbation (le manager direct). 500–5000 € demande
> le manager **puis** la finance.

*Sous 500 €* et *500–5000 €* ne disent pas ce qui se passe à **exactement 500,00 €**. Voici ce qui
est sorti ([`approval-chain.feature`](examples/expense-demo/qaia-journey/testbooks/US-004/approval-chain.feature),
verbatim) :

```gherkin
  @QAIA-US-004-009 @AC2 @P1 @boundary @low-confidence
  # condition: AC2-C2 — priority P1 — open: Q1 (exact-€500 boundary — read as inclusive
  # in band B: manager then finance)
  Scenario: A report of exactly €500.00 needs manager then finance
    Given a submitted report "R" by "employee@demo" totalling exactly 500.00 EUR
    When "manager@demo" approves report "R"
    Then report "R" still awaits approval from "finance"
```

L'outil n'a pas choisi silencieusement une lecture de la borne. Il en a choisi une, a marqué le
scénario `@low-confidence`, numéroté la question ouverte, et **écrit son hypothèse dans le
fichier** — pour qu'un humain la renverse en une ligne au lieu de la découvrir en production. Un
identifiant stable qui survit à la régénération, le critère dont il vient, la technique qui l'a
produit, et l'ambiguïté déclarée plutôt que devinée.

38 scénarios sont sortis de cette seule histoire, 11 marqués « confiance basse ». **Divulgué,
parce qu'une démo doit l'être :** ce ticket est notre propre fixture de gold set avec des
ambiguïtés plantées exprès, le parcours a été exécuté en non-interactif (chaque décision humaine
consignée `simulated`), et le modèle avait lu la section juge séquestrée du fichier — les trois
sont écrits dans [le journal du parcours](examples/expense-demo/qaia-journey/state/US-004/journey.md).
Ça montre la *forme* de la sortie, pas que ça marche sur votre ticket.

## Deux vrais défauts, dans un logiciel que nous n'avons pas écrit

Tout ce qui précède est mesuré sur du code que ce projet a lui-même produit, la preuve la plus
faible qui soit. La chaîne a donc été pointée sur [`typicode/json-server`](https://github.com/typicode/json-server)
— 75 694 étoiles — avec le droit de lire **son seul README**. Jamais le code, jamais les tickets,
jamais les correctifs.

- **Une rupture de contrat d'un caractère.** La documentation promettait `_dependent` ; le code
  lisait `dependent`. L'endpoint répondait en succès, supprimait le post, et laissait toutes les
  ressources dépendantes en place. **Une suite écrite en regardant le code ne peut pas trouver
  ça** — elle recopie l'erreur. Signalé par un vrai utilisateur (issue #1551), corrigé en `1b7c0fb`.
- **Deux filtres qui s'écrasaient.** `views_gt=100&views_lt=300` renvoyait tout. Corrigé en `e6055e6`.
- **Un troisième constat, refusé.** `_start` seul renvoie une liste vide — c'est un fait — mais le
  README ne le montre qu'**en paire**. **Compté contesté. Deux, pas trois.**

**Et ce qui va contre nous.** Sur la version *actuelle*, quatre tests échouent et **trois sont de
notre faute** : ces fonctionnalités ont quitté la documentation et la suite continuait d'exiger des
promesses périmées. Désormais détecté par
[`check_requirement_drift.py`](eval/tools/check_requirement_drift.py) plutôt que refermé en silence.

**Ce n'est pas un pilote.** Aucun humain n'a utilisé QAIA dans son propre travail. Une cible, une
API, aucune interface, 32 scénarios. [La campagne entière, son protocole et ses limites →](eval/external-application-2026-08-08/report.md)

## Installer

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-core@qaia
```

`/qaia-core:hello` vérifie l'installation. Ensuite, décrire son besoin en langage naturel —
« travaille avec QAIA sur cette user story » — suffit : la méta-skill `qaia` appelle les bonnes
étapes et s'arrête à chaque décision humaine.

```
/plugin install qaia-playwright@qaia      # tests Playwright exécutables, a11y, perf, sécurité, visuel
/plugin install qaia-score@qaia           # score et gate de release
/plugin install qaia-testdata@qaia        # jeux de données synthétiques
```

[`plugins/qaia-core/CATALOGUE.md`](plugins/qaia-core/CATALOGUE.md) est la carte « je veux faire X →
utilise Y » des 37 skills. Des exemples complets avec leurs sorties réelles sont dans
[`examples/`](examples/).

## Ce qui distingue QAIA, et ce qui ne le distingue plus

**Appliquer les techniques ISTQB n'est plus un différenciateur** — [QASkills.sh](https://qaskills.sh/)
publie à lui seul ~380 skills MIT compétemment écrites, et des concurrents natifs Claude Code
([Agentic QE Fleet](https://github.com/proffesor-for-testing/agentic-qe),
[QA Orchestra](https://github.com/Anasss/qa-orchestra)) recouvrent QAIA directement. Trois choses
le distinguent réellement, toutes vérifiables par un inconnu en cinq minutes :

- **Aucun producteur ne s'auto-note.** Le score structurel vit dans un plugin séparé en lecture
  seule (`qaia-score`), distinct du juge LLM sémantique, et depuis le 2026-08-09 il est livré en
  **Python figé que vous pouvez lire, comparer ou refuser** — pas un algorithme rejoué de mémoire à
  chaque invocation. Une note non reproductible n'est pas une note
  ([ADR 0002](docs/adr/0002-code-and-optin-tier.md)).
- **Zéro clé API, rien qui s'auto-exécute.** Les skills sont du Markdown, invoqué à la demande.
  Installer QAIA n'enregistre ni hook, ni agent, ni serveur MCP. Les scoreurs ne tournent que
  lorsque vous invoquez la skill de score, sous vos droits.
- **Les échecs sont publiés aussi.** Une suite générée s'exécute sur un runner GitHub Actions
  **sans session Claude ni skill chargée**
  ([run 30702503888](https://github.com/QAIA-Project/QAIA/actions/runs/30702503888)) ; chaque
  chiffre annoncé comme mesuré pointe vers le fichier brut dont il vient — y compris un benchmark
  qui conclut que QAIA coûte ~2,9× un prompt direct et n'en trouve pas plus.

**Le contrepoids honnête :** QAIA est plus jeune et bien moins utilisée que chacun d'eux, **aucun
pilote humain ne l'a jamais menée de bout en bout**, et ce qu'elle produit pour un vrai
utilisateur reste non mesuré.
[Quel outil installer ? On en recommande d'autres dans 3 cas sur 4 →](https://qaia-project.github.io/QAIA/compare.html)

## État et limites

**Pré-alpha, en développement actif.** `qaia-core` 0.2.35 (18 skills), `qaia-playwright` 0.1.27
(14 skills), `qaia-score` 0.2.4 (4 skills), `qaia-testdata` 0.1.3 (1 skill) — **37 skills** —
validant tous `--strict`, prouvés bout-en-bout sur deux domaines indépendants : santé
([`examples/medibook/`](examples/medibook), 26 tests / 32 exécutions, tous verts) et finance/RH
([`examples/expense-demo/`](examples/expense-demo), 56 tests verts, vrais bugs trouvés pendant
l'automatisation), plus un corpus de robustesse multi-modèles à 24 cas.

- **L'outil consomme votre quota Claude.** Le coût par commande est publié, mesuré, et supérieur
  aux estimations du projet lui-même sur 13 des 14 commandes.
- **« L'apprentissage » = des fichiers locaux.** Le feedback enrichit une base de connaissance
  versionnée dans votre dépôt. Pas d'entraînement de modèle, pas de serveur central.
- **Web-first.** Le mobile signifie émulation navigateur, pas natif iOS/Android.
- **Pas une revendication réglementaire.** Le cadrage d'origine « logiciel médical / environnements
  réglementés » a été retiré (D114) : QAIA ne cartographie aucun référentiel réel — ni IEC 62304,
  ni 21 CFR Part 11, ni ISO 13485. `examples/medibook/` est une démo de *forme* santé, pas un
  artefact certifié.
- **Ce que QAIA ne fait délibérément pas** ([ADR 0004](docs/adr/0004-test-level-boundary.md)) : les
  tests unitaires et de composant, l'intégration interne, le test structurel piloté par la
  couverture. QAIA part d'une promesse observable de l'extérieur — un test écrit contre une
  fonction est écrit contre l'implémentation, c'est-à-dire contre l'oracle qu'il existe pour éviter.

**Envie d'être le premier pilote ?** [`docs/PILOT-KIT.md`](docs/PILOT-KIT.md) est un parcours guidé
de 15 minutes sur une histoire toute prête, et la seule chose demandée en retour, c'est de dire où
ça a raté. État honnête : [`docs/STATUS.md`](docs/STATUS.md) (le relevé complet) ·
[`docs/STATUS-en.md`](docs/STATUS-en.md) (résumé anglais).

## Les agents — un tier optionnel

[`agents-tier/`](agents-tier) livre huit agents nommés. Il n'est **installé par aucun plugin** et
n'est jamais un prérequis — les 37 skills fonctionnent sans lui. Seuls deux méritent leur propre
fenêtre de contexte (`camille-judge`, `elian-refuter`), parce qu'un producteur ne note jamais sa
propre sortie ; les six autres regroupent une phase derrière un nom — ergonomie réelle, aucune
capacité nouvelle. Deux réserves que le README du tier documente au lieu de les cacher : `tools:`
est une demande au harnais et non une frontière de capacité, et un agent délégué exécute les points
de validation sans personne dans la pièce.

## Carte du dépôt

| Chemin | Contenu |
|---|---|
| [`plugins/`](plugins/) | Les quatre plugins — core, playwright, score, testdata |
| [`examples/`](examples/) | Sept exemples complets avec leurs sorties réelles |
| [`eval/`](eval/) | Harnais d'évaluation : gold set, rubrique, baselines notées, campagnes |
| [`docs/STATUS.md`](docs/STATUS.md) | **État honnête du projet** (à lire pour reprendre le travail) |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Chaque décision d'architecture avec sa raison et ses réserves |
| [`docs/adr/`](docs/adr/) | Les sept ADR qui fixent les frontières de périmètre |
| [`docs/COMPETITIVE-ANALYSIS.md`](docs/COMPETITIVE-ANALYSIS.md) | Revue du paysage et angles morts de QAIA |
| [`docs/OUTPUT-CONTRACT.md`](docs/OUTPUT-CONTRACT.md) | Le manifeste de run partagé par tous les plugins |
| [`docs/PILOT-KIT.md`](docs/PILOT-KIT.md) | Parcours guidé de 15 minutes pour pilotes |
| [`PROMPT.md`](PROMPT.md) | Prompt fondateur : vision, contraintes, parcours utilisateur |

## Contribuer

Lire [`CONTRIBUTING.md`](CONTRIBUTING.md) d'abord. Toute PR exige un DCO ; celles qui touchent aux
skills exigent en plus une revue adversariale tracée par agent — une skill est un prompt, et une
instruction malveillante est invisible à un linter. Signalements de sécurité :
[`SECURITY.md`](SECURITY.md).

Licence : [MIT](LICENSE).
