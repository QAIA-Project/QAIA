# Le barème universel devient le défaut — mesuré sur 257 cahiers écrits ailleurs

**Date** 2026-08-24 · Phase 1 de la refonte
([spec](../../docs/superpowers/specs/2026-08-24-qaia-refonte-design.md)) · corpus reconstitué
par `eval/tools/fetch_corpus.py` depuis le manifeste gelé du 2026-08-09

## Ce qui a changé

`structural_score.py` appliquait par défaut les conventions de ce projet à tout cahier, et
demandait un drapeau `--third-party` pour ne pas le faire. **L'exception était à demander.** Un
outil dont le métier est de juger ne peut pas avoir « ce test n'est pas de moi » câblé dans son
chemin par défaut : c'est ce qui rendait **0 PASS sur 244 fichiers étrangers** le 2026-08-09.

Le rapport est inversé. Le barème universel est le défaut ; `--profile qaia` ajoute les
conventions maison par-dessus, sur demande.

## Le remède évident a été essayé sur le corpus, et il ne marche pas

L'idée première était : *« la traçabilité reste notée, mais on accepte toute référence
d'exigence, pas seulement `@QAIA-` »*. Mesuré avant d'être écrit — la porte d'entrée que la spec
impose :

| | |
|---|---:|
| fichiers `.feature` étrangers | 257 |
| occurrences de tags | 410 |
| tags distincts | 126 |
| **tags portant une référence d'exigence** | **0** |

Les tags du monde réel sont des directives de lanceur : `@javascript` (47), `@wip`, `@fixture`,
`@setup`, `@seed_users`. **La traçabilité par tag n'est pas une propriété universelle du
Gherkin, c'est une convention de projet** — et la règle « généreuse » aurait rendu zéro elle
aussi, avec une meilleure justification et le même résultat.

**La bonne règle n'est donc pas un profil à choisir, c'est une détection.** La traçabilité est
notée quand le cahier montre une convention de référence, et **déclarée non évaluée** sinon —
retirée du dénominateur, jamais notée zéro, le barème se remettant à l'échelle sur les trois
dimensions qui transfèrent. Aucun drapeau à passer : l'outil s'adapte au matériau.

Le motif (`REQ_REF_RE`) exige au moins deux majuscules puis un chiffre. Calibré contre les 126
tags distincts du corpus pour ne déclencher sur aucun — `@tag1`, `@beforetag1`, `@scenarioTag1`,
`@gpl3` sont en minuscules ou à casse mixte — tout en reconnaissant `@QAIA-US-004-009`, `@AC1`,
`@REQ-5`, `@JIRA-1234`, `@US-4`.

## Le résultat

| | avant (défaut) | avant (`--third-party`) | **après (défaut)** |
|---|---:|---:|---:|
| PASS | **0** | 101 | **101** |
| CONCERNS | 100 | 56 | 56 |
| FAIL | 147 | 90 | 90 |
| non notables | 10 | 10 | 10 |
| score médian | 55 | 74 | **74** |
| constats | 666 | 420 | **173** |

**Ce qui compte n'est pas que 101 égale 101.** C'est que le chiffre s'obtienne désormais sans
qu'un utilisateur ait à découvrir un drapeau, et que les constats tombent de 666 à **173** :
493 d'entre eux ne nommaient aucun défaut, ils constataient l'absence de conventions QAIA. Le
signal réel — 90 paradoxes du pesticide, 50 scénarios sans résultat attendu, 19 `Then` non
vérifiables — était noyé sous un bruit produit par l'outil lui-même.

## Un défaut introduit par la correction, et attrapé

La première version faisait remonter « traceability NOT ASSESSED » dans `findings`, sur 247 des
257 fichiers. **Le même bruit, réintroduit par le correctif** : le compte de constats passait à
420 sans qu'aucun défaut de plus ait été trouvé. Un constat nomme un défaut ; un état se dit
ailleurs. Le champ `notes` a été séparé de `findings` — sans quoi « nombre de constats » ne veut
plus rien dire, et la mesure censée juger la refonte devient inutilisable.

## Non-régression sur nos propres cahiers

`examples/expense-demo/` : **76 / 77 / 90 / 74**, identiques au point près à la version d'avant
inversion (vérifié en rejouant l'ancien fichier depuis git, pas en le supposant). Nos cahiers
portent `@QAIA-<ID>`, la détection les reconnaît, la traçabilité y reste notée sur 25.

*En passant* : le rapport du 2026-08-09 annonçait « 76 / 80 / 90 / 77 ». Le 80 n'existe plus et
n'a pas disparu aujourd'hui — la version d'avant ma modification rend déjà 74. **Un chiffre
publié comme non-régression avait dérivé sans que rien ne s'en aperçoive**, ce qui est le
même mécanisme, un étage plus haut : une valeur de référence qu'aucun contrôle ne rejoue.

## La garde, et les deux trous que la mutation y a trouvés

`check_universal_default.py` remplace les portes de sortie par une porte d'entrée : il ne relit
pas une règle, il **mesure** la propriété sur des cahiers réels du dépôt en leur retirant les
conventions maison. Quatre invariants, quatre défauts déjà survenus.

Passée à la campagne de mutation (`mutate_guards.py`), la première version a laissé **deux
survivantes** — deux régressions que la garde aurait laissées passer :

| Mutation | Pourquoi elle survivait |
|---|---|
| la détection revient à n'accepter que `@QAIA-` | **la garde tirait son motif de l'outil qu'elle teste.** Le commentaire disait « pour que les deux ne puissent plus diverger » ; le résultat est qu'elles devenaient aveugles *ensemble*. Un contrôle qui importe la logique qu'il vérifie ne vérifie rien. |
| le profil par défaut bascule sur `qaia` | **la garde passait `profile="universal"` explicitement.** Elle vérifiait donc que ce profil se comporte bien, jamais que c'est *lui* le défaut — c'est-à-dire jamais ce que l'appelant obtient. |

Les deux corrigées : le motif est réécrit en toutes lettres dans la garde, l'appel se fait sans
argument de profil, et un quatrième invariant a été ajouté — **un cahier tracé par une convention
étrangère (`@JIRA-1234`, `@REQ-77`) doit être reconnu et noté**. Sans lui, I1–I3 se mesuraient
tous sur des cahiers de ce dépôt : ils prouvaient que l'outil ne nous pénalise pas, jamais qu'il
créditerait quelqu'un d'autre.

**Campagne finale : 21 mutations, 21 tuées, 0 survivante.**

*Un défaut trouvé en passant* : le journal de mutation datait chaque passe du **2026-08-11 en
dur**. Toute campagne postérieure s'archivait sous une date à laquelle elle n'avait pas eu lieu —
dans un fichier dont le rôle est précisément de prouver dans quel ordre les choses se sont
passées. Corrigé.

## Reproduire

```bash
python eval/tools/fetch_corpus.py eval/gherkin-external-2026-08-09/corpus.json /tmp/corpus
python eval/tools/score_corpus.py /tmp/corpus --profile universal
python eval/tools/score_corpus.py /tmp/corpus --profile qaia
```

`fetch_corpus.py` reconstitue le corpus depuis les **dépôts nommés** du manifeste, pas depuis une
recherche GitHub — le fetcher d'origine partait de requêtes de recherche et ne pouvait donc pas
reconstruire deux fois le même corpus. **12 empreintes sur 15 coïncident avec celles du gel du
2026-08-09** ; trois dépôts ont bougé depuis (`IfcOpenShell`, `alphagov/whitehall`,
`brighton36/CoinPost`, ce dernier passant de 12 à 25 fichiers, d'où 257 au lieu de 244).

## Limite honnête

**Le corpus n'est pas un échantillon représentatif du Gherkin mondial.** 15 dépôts issus d'une
recherche par mots-clés, dominés par l'outillage `behave`. 39,3 % de PASS y est une mesure de ce
barème sur ce corpus, pas une mesure de la qualité du Gherkin en général. Ce que le chiffre
établit, c'est que **le barème discrimine désormais sur des propriétés que le matériau étranger
peut satisfaire** — ce qu'il ne faisait pas.
