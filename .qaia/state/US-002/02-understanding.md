---
stepsCompleted: [00-ingest, 01-review, 02-understanding]
lastStep: 02-understanding
lastSaved: 2026-08-10
status: waived
---

# 02-understanding — US-002

> **Mesure contaminée — à lire avant toute autre ligne.** Le fichier `00-source.md`, écrit le
> 2026-07-25, affirme ne pas recopier la section juge séquestrée du document source ; c'est vrai
> du bloc verbatim, **mais le paragraphe suivant en nomme la substance** : inclusivité des bornes,
> portée de la réduction de 50 % d'AC6, fenêtre 24 h glissante ou calendaire, absence de règle
> d'arrondi. Ce fichier est lu par la présente skill.
>
> **Conséquence, énoncée avant les résultats et non après :** les questions Q1, Q3, Q4 et Q6
> ci-dessous recoupent les ambiguïtés plantées. Elles sont marquées `[contaminé]`. **Elles ne
> prouvent rien sur la capacité de QAIA à trouver une ambiguïté** — les réponses étaient dans le
> point de reprise. Les questions non marquées ont été dérivées du texte des AC seul et sont, à
> ce titre, les seules dont la découverte soit défendable.
>
> Base de connaissance : **absente** (`.qaia/knowledge/` n'existe pas). Parcours en mode QAIA
> Solo — aucune règle projet n'a pu répondre par avance à une question ci-dessous.

## Reformulation

Un prescripteur saisit une posologie et la fait valider **avant signature** contre la fiche de
sécurité du médicament : seuils par prise, cumul sur 24 h, âge plancher, le tout modulé par
l'état rénal du patient. Le système classe le résultat en *pass*, *avertissement surchargeable*
ou *blocage dur*, rend ce verdict dans l'écran de signature sans rechargement, et trace toute
surcharge dans une piste d'audit.

**Risque principal si la validation se trompe** : un surdosage atteint la pharmacie puis le
patient. La classe de défaut la plus grave n'est pas le faux blocage (gênant, visible,
corrigeable) mais le **faux laissez-passer** — une dose dangereuse classée *pass*, ou un blocage
converti en avertissement par un chemin d'exception mal borné. Toute la priorisation en découle.

## Balayage des catégories de l'étape 2 — chacune tranchée, aucune tue

| Catégorie | Résultat |
|---|---|
| Termes et unités indéfinis | **Q1, Q2** — inclusivité des seuils, unité de dose jamais nommée |
| Durée / délai → quel référentiel d'horloge ? | **Q3** — la fenêtre 24 h d'AC4 |
| Contradictions entre AC | **Q4, Q5** — AC6 contre AC2 ; AC5 croisé AC6 |
| Comportement manquant (erreur, vide, concurrence, permissions) | **Q7, Q8, Q9** |
| Règles de données non spécifiées (format, arrondi, limites, unicité) | **Q6, Q10** |

## Questions — numérotation stable, citée par les scénarios

> **Si vous êtes propriétaire du produit et non des tests, lisez ceci. Le reste de la page ne
> vous concerne pas.**
>
> - **Ce qu'on vous demande :** la spécification ne dit pas ce qui doit se passer dans les cas
>   ci-dessous. On vous demande quel est le *comportement correct* — pas comment le tester.
> - **Pourquoi ça compte :** chaque réponse devient un test qui affirme ce comportement.
>   Répondez, et le test vérifie ce que vous avez décidé. Ne répondez pas, et nous écrivons un
>   test qui affirme notre meilleure supposition — il passera au vert et ne prouvera rien de
>   votre vraie règle.
> - **Si vous ne répondez pas :** sur les points peu risqués nous appliquons un défaut annoncé,
>   marqué comme hypothèse. Sur tout ce qui touche à l'argent, la sécurité, les données de santé,
>   les mineurs ou la preuve légale, nous n'appliquons **aucun** défaut : ces points restent
>   ouverts et chaque test qui en dépend est marqué comme reposant sur une supposition non
>   confirmée. Ce marquage suit la story jusqu'à la décision de livraison.
>
> « Je ne sais pas » est une réponse utile : sur un point peu risqué elle devient une hypothèse
> marquée ; sur la santé, l'argent, la sécurité, les mineurs ou la preuve légale elle laisse la
> question **ouverte** et le scénario marqué, parce qu'aucun défaut n'y est sûr. Dans les deux
> cas c'est mieux qu'une certitude inventée. La seule réponse inutilisable est le silence.

**Domaine protégé — cette US est intégralement dans le champ « santé / sécurité ».** Toute
question portant sur un seuil de dose est donc classée `[open]` et **jamais** `[assumption]`,
même quand un défaut paraît évident. La règle est appliquée sans exception ci-dessous, et c'est
elle qui explique pourquoi si peu de questions reçoivent un défaut.

| ID | Question | Classe | Défaut proposé |
|---|---|---|---|
| **Q1** `[contaminé]` | AC3 dit « **above** the maximum safe dose ». Une dose **exactement égale** au maximum est-elle autorisée (borne inclusive) ou bloquée ? AC2 dit « **strictly below** » pour le minimum, donc la source sait distinguer — le silence d'AC3 est-il délibéré ? | `[open]` — santé | **aucun**. Une lecture inverse déplace la frontière du blocage d'un pas exactement là où le patient est le plus exposé. |
| **Q2** | Aucune **unité de dose** n'est nommée nulle part (mg ? mg/kg ? UI ?). AC1 parle de « dose », AC6 la réduit de 50 %. La validation compare-t-elle des grandeurs de même unité, et qui garantit la conversion ? | `[open]` — santé | **aucun**. Une comparaison entre unités hétérogènes est un faux laissez-passer silencieux. |
| **Q3** `[contaminé]` | AC4 : « cumulative dose over 24 h ». Fenêtre **glissante** (24 h avant l'instant de prise) ou **jour calendaire** ? Et évaluée sur quelle horloge — fuseau du prescripteur, du patient, du serveur ? | `[open]` — santé | **aucun**. Les deux lectures donnent des verdicts opposés sur la même prescription à cheval sur minuit. |
| **Q4** `[contaminé]` | AC6 réduit « **tous les seuils maximaux** » de 50 %. La dose **minimale efficace** (AC2) est-elle réduite aussi ? Si non, un médicament dont le max réduit passe **sous** le min efficace rend toute dose simultanément « sous le minimum » (avertissement) et « au-dessus du maximum » (blocage). Quel verdict prime ? | `[open]` — santé | **aucun**. Le cas est atteignable dès que max < 2 × min, ce qui est courant. |
| **Q5** | AC5 (exception pédiatrique) et AC6 (réduction rénale) peuvent s'appliquer au **même patient**. L'exception de rôle d'AC5 convertit un blocage d'âge en avertissement — convertit-elle aussi un blocage de seuil issu d'AC6 ? Ou chaque règle garde-t-elle son propre verdict ? | `[open]` — santé | **aucun**. C'est le chemin par lequel un blocage devient surchargeable. |
| **Q6** `[contaminé]` | Aucune **règle d'arrondi** n'est donnée pour la réduction de 50 % d'AC6 sur une valeur impaire (7 mg → 3,5 ? 3 ? 4 ?). | `[open]` — santé | **aucun**. L'arrondi vers le haut autorise une dose que l'arrondi vers le bas bloque. |
| **Q7** | AC1 pose l'existence d'une fiche de référence. Que se passe-t-il quand un médicament prescrit **n'en a pas** — ou qu'elle est incomplète (âge plancher absent) ? Blocage, laissez-passer, ou avertissement ? | `[open]` — santé | **aucun**. Un défaut « laisser passer si inconnu » est le pire mode de défaillance possible ici. |
| **Q8** | AC4 additionne les prises **du même patient**. Deux prescriptions signées **simultanément** par deux prescripteurs peuvent chacune être conforme et leur somme dépasser le cumul. La validation est-elle transactionnelle ? | `[open]` — santé | **aucun**. Concurrence non spécifiée sur un contrôle de sécurité. |
| **Q9** | AC2 dit « the physician may override ». **Tout** prescripteur, ou seulement l'auteur de la prescription ? Une frontière d'accès non énoncée est une question, jamais une hypothèse. | `[open]` — preuve légale | **aucun**. AC7 fait de la surcharge un acte tracé nominativement. |
| **Q10** | AC7 exige « au moins 20 caractères » de justification. Comptés comment — 20 espaces suffisent-ils ? Caractères Unicode ou octets ? Le contrôle est-il un garde-fou de qualité ou un simple seuil de longueur ? | `[assumption]` | **Défaut appliqué** : longueur ≥ 20 après suppression des espaces de tête et de fin, comptée en points de code Unicode. Seul point non-santé de la liste : il porte sur la forme de la trace, pas sur une dose. |

## Passe croisée entre AC — paires partageant une ressource ou une fenêtre

| Paire | Interaction | Statut |
|---|---|---|
| AC2 × AC6 | Le seuil min est-il réduit ? Inversion possible min > max | `[open]` → Q4 |
| AC3 × AC6 | Réduction appliquée avant comparaison — ordre et arrondi | `[open]` → Q6 |
| AC4 × AC6 | Le cumul 24 h est un « seuil maximal » : réduit de 50 % lui aussi | **couvert** — AC6 dit « tous les seuils maximaux », le cumul en est un |
| AC5 × AC6 | Exception de rôle contre modificateur rénal | `[open]` → Q5 |
| AC3 × AC4 | Une prise conforme par prise mais dépassant le cumul → deux règles, deux identifiants ; AC8 dit « rule identifiers » au pluriel | **couvert** — les deux sont rendus |
| AC5 × AC7 | La surcharge pédiatrique d'AC5 est-elle soumise au minimum de 20 caractères d'AC7 ? | **couvert** — AC7 dit « every override », AC5 en produit un |
| AC2 × AC7 | Idem pour la surcharge d'avertissement de dose | **couvert** |

## Passe de contradiction à trois AC

**AC2 × AC6 × AC3** est la seule triade indécidable : une règle de seuil bas (AC2), un modificateur
transversal (AC6) et une règle de blocage haut (AC3). Prises deux à deux elles sont cohérentes ;
c'est seulement à trois, sur un médicament dont le maximum réduit tombe sous le minimum efficace,
qu'aucune ne dit quel verdict l'emporte. Consignée en **Q4**.

## Ce qui n'est pas une question de cette étape

Écarté des slots Q à dessein — ce sont des sujets d'automatisation, pas des lacunes de la
spécification : la re-vérifiabilité indépendante du cumul 24 h, la stabilité d'un test dépendant
de l'horloge, et la façon d'observer « sans rechargement » (AC8) depuis un test.

## Dépendances hors périmètre — signalées, non inventées

`[out-of-slice]` : fiche médicament (AC1), modèle de rôle « pediatric specialist » (AC5),
drapeau d'insuffisance rénale (AC6), stockage de la piste d'audit (AC7). Aucune story sœur
nommée dans la source.

## ⚠ VALIDATION — non satisfaite

Testeur joignable, arbitrage **délégué** (waiver du 2026-08-10). Les dix questions restent
`pending-validation` : **neuf sont `[open]` sans défaut** parce qu'elles touchent à la santé, une
seule porte une hypothèse appliquée (Q10). Aucun scénario dépendant de Q1-Q9 ne peut être présenté
comme vérifiant une règle confirmée.
