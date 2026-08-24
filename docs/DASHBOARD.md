# QAIA — tableau de bord

**Deux nombres. Tout le reste est du détail.**

Ce fichier remplace `docs/STATUS.md` (1 316 lignes) comme état de référence du projet. Le
raisonnement est dans [la spec de refonte](superpowers/specs/2026-08-24-qaia-refonte-design.md) :
un dépôt qui tient un journal de 1 316 lignes et 201 décisions pour un produit sans utilisateur
optimise le récit de son travail, pas son travail.

## Les deux nombres

| | Valeur | Mesuré le | Comment |
|---|---:|---|---|
| **Cahiers étrangers qui passent la porte** | **102 / 257** (39,7 %) | 2026-08-24 | `score_corpus.py` sur le corpus gelé |
| **Utilisateurs réels** | **0** | 2026-08-24 | 1 étoile, 0 fork, 0 watcher, 0 pilote |

Le premier est la première métrique de l'histoire du projet qui **ne dépende pas de sa propre
production**. Le second est la seule qui compte à la fin, et il n'a jamais bougé.

## Le détail qui a le droit d'exister

### Le noyau, mesuré hors de sa propre production

| Outil | Matériau étranger | Constats avant / après | Date |
|---|---|---:|---|
| `structural_score.py` | 257 cahiers Gherkin, 15 dépôts | 666 → **150** | 2026-08-24 |
| `automation_score.py` | 7 suites Playwright | 715 → **144** | 2026-08-24 |
| `spec_suite_drift.py` | 4 projets avec spec OpenAPI | 11 → **0** (4 × `UNCOMPARABLE`) | 2026-08-24 |
| `lint_skills.py` | 159 SKILL.md, 12 dépôts | 622 → 159 | 2026-08-09 |

Dans les quatre cas, la baisse n'est pas une perte de sensibilité : c'est du **bruit de
convention** retiré, ou des **verdicts rendus sur un parse vide** refusés. Chaque ligne renvoie à
un rapport qui donne la commande de reproduction.

### Les gardes

| | |
|---|---:|
| mutations sur les garde-fous | **40** |
| tuées | **40** |
| survivantes | **0** |
| invariants de la porte d'entrée | **10** |

**Et ce que la mutation ne remplace pas.** Le 2026-08-24, trente mutations tuées, cinq invariants
verts et une CI verte n'ont empêché **ni deux affirmations publiées d'être réfutées, ni six
régressions du jour de passer**. Trois relecteurs en contexte vierge — réfutation, persona de QA
lead, relecture développeur — les ont trouvées, et ils ont trouvé des choses **disjointes** : les
chiffres, l'arithmétique et les périmètres, la confiance.

La mutation vérifie que les gardes gardent ce qu'elles gardent. Elle ne dit rien de ce que
personne n'a pensé à garder. [Rapport complet →](../eval/refutation-2026-08-24/REPORT.md)

Registre complet : `eval/mutation-guards-2026-08-11.txt` (une entrée par passe, datée du jour où
elle a tourné). Une survivante ne se tolère pas par le code de sortie : elle s'annote et se
retire de la liste.

### La porte d'entrée

**Aucune capacité n'entre dans le produit avant d'avoir été mesurée sur du matériau étranger.**
C'est le seul contrôle de gouvernance que la refonte conserve, et il remplace les 25 contrôles de
sortie. Il est exécutable : `eval/tools/check_universal_default.py`, dans `make check` et dans la
CI.

Les trois défauts qui ont coûté le plus cher au projet — barème encodant des conventions maison
(deux fois, en deux outils, à un jour d'écart) et verdict rendu sur un parse vide — ont tous été
trouvés en pointant un outil ailleurs, et **aucun** des 25 contrôles de sortie ne pouvait les
voir : ils relisent tous le dépôt, jamais son comportement sur ce qu'il n'a pas écrit.

## Ce qui reste ouvert

| # | Sujet |
|---|---|
| [#111](https://github.com/QAIA-Project/QAIA/issues/111) | Trancher le sort d'`automate` : le produit s'arrête-t-il au cahier ou va-t-il jusqu'au code exécutable ? |
| [#112](https://github.com/QAIA-Project/QAIA/issues/112) | Le barème universel d'automatisation est trop pauvre : 100,0 avec 8 attentes interdites au compteur |
| [#113](https://github.com/QAIA-Project/QAIA/issues/113) | Doublons faux dans les deux sens, FAIL inexpliqué à 87/100, aucune sortie lisible pour 340 fichiers |
| #106 – #110 | Reste-à-faire ouvert le 2026-08-11 |

### La face « juger » est utilisable

Trois blocages nommés par une QA lead en contexte vierge, entre « je l'utiliserais une fois » et
« je le mettrais en CI » :

| | |
|---|---|
| `gateReason` | le JSON posait `score: 87` et `gate: FAIL` côte à côte sans un mot ; la raison est nommée, et pour un arrêt forcé elle nomme la **cause**, pas le seuil |
| `--format md` | rapport trié par gravité, 3,6 lignes par fichier. Sans lui, juger demandait à l'utilisateur d'écrire lui-même son rapport |
| doublons | un groupe n'est un doublon que si son résultat attendu l'est aussi. **36 % des constats** nommaient des paires de valeurs limites — facturées jusqu'à 15 points |

Reste un faux négatif entier : le détecteur ne trouve que les doublons qu'un humain ne produit
jamais. Mesuré, documenté, ouvert (#113).

## Ce qui n'a pas changé, et qu'il ne faut pas oublier

- **QAIA coûte 2,9× un bon prompt direct** pour un rappel d'ambiguïtés inférieur (3/4 contre 4/4).
  La refonte ne l'a pas encore corrigé : elle a d'abord réparé la face *juger*, qui est la seule
  dont un inconnu peut se servir sans rien adopter. Cible : ≤ 1,5×.
- **Personne n'a jamais utilisé QAIA dans son propre travail.** Les personas et les relectures en
  contexte vierge sont un substitut mesurable, pas un pilote.
- **Les corpus ne sont pas des échantillons représentatifs.** 15 dépôts Gherkin issus d'une
  recherche par mots-clés, 7 suites Playwright, 4 projets avec spécification. Ce qu'ils
  établissent, c'est que les outils discriminent sur des propriétés que du matériau étranger peut
  satisfaire — pas une note du logiciel mondial.

## Où est passé le reste

`docs/STATUS.md` et `docs/DECISIONS.md` sont conservés comme **archive historique**, gelés. Ils
racontent comment le projet en est arrivé là, ce qui a de la valeur ; ils ne décrivent plus son
état, ce qui en avait cessé.
