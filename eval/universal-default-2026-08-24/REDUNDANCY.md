# Le détecteur de doublons facturait ce que la profession enseigne d'écrire

**Date** 2026-08-24 · Dernier point de [#113](https://github.com/QAIA-Project/QAIA/issues/113),
seule raison invoquée par la relectrice « QA lead » pour ne pas mettre l'outil en CI.

## Le défaut

Le détecteur groupait les scénarios par forme `Given`/`When` (littéraux réduits) et **pénalisait
tout groupe**, jusqu'à −15 points. L'en-tête du fichier promettait pourtant l'inverse :

> *reported for human judgment, not auto-failed*

Il facturait donc les **paires de valeurs limites** et les **paires nominal/refus** — c'est-à-dire
la chose la plus élémentaire du métier.

> « Il groupe *Export CSV d'un rapport mensuel* (42 lignes) et *Export d'un rapport vide*
> (0 ligne). C'est une paire de valeurs limites, exactement ce qu'on m'a appris à écrire. Il me
> facture 6 points pour l'avoir fait. »

## La mesure, avant d'écrire la règle

Sur les 257 cahiers étrangers :

| | |
|---|---:|
| groupes de forme `Given`/`When` identique | **225** |
| dont le `Then` est identique aussi — *vrai doublon* | **143** |
| dont le `Then` **diffère** — *paire limite ou nominal/refus* | **82 (36 %)** |

Un tiers des constats de redondance nommait des comportements distincts. Exemples relevés :
« Creating a new draft consultation » groupé avec « … in another language » ;
« Going from: `format.html { render 'users/index' }` » avec « `render :new, formats: [:js]` ».

## La règle

**Un groupe de même forme n'est un doublon que si son résultat attendu l'est aussi.**

- `Then` équivalent → **doublon**, pénalisé comme avant.
- `Then` différent → **signalement en `notes`, aucune pénalité**. Ce que le détecteur disait déjà
  faire.

## L'effet, des deux côtés

| | avant | après |
|---|---:|---:|
| **Corpus étranger** — PASS | 101 | **102** |
| médiane | 74 | **77** |
| constats | 173 | **150** |
| dont paradoxe du pesticide | 90 | **67** |
| **Nos propres cahiers** | | |
| `approval-chain.feature` | 76 CONCERNS | **85 PASS** |
| `workflow-state-machine.feature` | 74 CONCERNS | **80 PASS** |
| `line-items.feature` | 90 PASS | **96 PASS** |
| `audit-and-auth.feature` | 77 CONCERNS | 77 CONCERNS |

**Ce n'est pas une non-régression, et il ne faut pas le présenter comme telle.** Trois de nos
quatre cahiers changent de score et deux changent de porte. C'est voulu : la pénalité était
fausse, et **elle nous frappait aussi** — le projet se facturait à lui-même les paires de valeurs
limites qu'il génère délibérément. Les valeurs 76/77/90/74 citées dans les rapports antérieurs
sont désormais périmées.

## Troisième affinage, le même jour — et celui-là va au bout

La règle ci-dessus (« même forme **et** même `Then` réduit ») a été mesurée à son tour, comme
#113 l'exigeait avant toute correction du faux négatif. **Elle ne tenait pas non plus.**

Sur les 852 paires qu'elle comptait comme doublons dans le corpus étranger :

| | |
|---|---:|
| textes **strictement identiques** — copier-coller sans appel | **159** |
| ne différant **que par des littéraux** | **693 (81 %)** |

Or **après réduction des littéraux, une paire de valeurs limites et un copier-coller sont le même
texte.** Le détecteur ne les distinguait donc pas — il en avait seulement l'air. Les exemples
réels tranchent : `Opening new model` / `Opening new controller` / `Opening a new job` dans
`expanding-snippets` est une **partition d'équivalence**, pas une répétition.

**Aucun outil de texte ne peut trancher** entre « même test, nouvelle valeur, aucun comportement
neuf » et « valeurs distinctes, couverture délibérée » : c'est un jugement sur le **domaine**.

Règle finale : **pénalité sur le texte strictement identique, signalement pour tout le reste.**
Un détecteur qui facture un jugement qu'il ne peut pas rendre est pire que muet — il a l'autorité
d'un chiffre.

| | départ | 2ᵉ règle | **règle finale** |
|---|---:|---:|---:|
| corpus — PASS | 101 | 102 | **103** |
| médiane | 74 | 77 | **78** |
| constats | 173 | 150 | **107** |
| dont paradoxe du pesticide | 90 | 67 | **24** |
| `approval-chain.feature` | 76 CONCERNS | 85 PASS | **91 PASS** |
| `workflow-state-machine.feature` | 74 CONCERNS | 80 PASS | **80 PASS** |
| `line-items.feature` | 90 PASS | 96 PASS | **96 PASS** |

### La calibration par similarité, essayée et écartée

#113 proposait une similarité de jetons à seuil. Mesurée sur 13 398 paires de scénarios :

| seuil | paires retenues | dont `Then` égal | dont `Then` différent |
|---:|---:|---:|---:|
| 0,80 | 4 925 | 2 338 | 2 587 |
| 0,90 | 3 483 | 1 773 | 1 710 |
| 1,00 | 2 801 | 1 581 | 1 220 |

Abaisser le seuil ramène surtout des paires à `Then` **différent** — des variantes, pas des
doublons. Et le gain apparent en doublons est illusoire, puisque la mesure ci-dessus montre que
81 % de ces « doublons » ne diffèrent que par des littéraux. **La piste est écartée, mesure à
l'appui**, plutôt que laissée ouverte comme une promesse.

## Ce qui n'est pas corrigé

**Le faux négatif reste entier.** Deux scénarios manifestement copiés-collés ne sont pas vus dès
que leurs `When` diffèrent de deux mots :

```gherkin
When l'utilisateur ajoute "REF-100"
When l'utilisateur ajoute l'article "REF-100"
```

Formes différentes → pas de doublon. Or **un copier-coller humain dérive toujours d'un mot ou
deux** : *le détecteur ne trouve que les doublons qu'un humain ne produit jamais.*

La piste évidente — une forme approchée — vient d'être **mesurée et écartée** (section
précédente) : elle ne ramène presque que des variantes, et le gain apparent en doublons est
illusoire puisque 81 % d'entre eux ne diffèrent que par des littéraux.

**Il n'y a donc pas de correctif textuel connu**, et c'est le résultat honnête de la journée sur
ce point. Ce qui reste possible est d'un autre ordre : demander au lecteur, sur les groupes
*signalés*, si la répétition gagne sa place. Le détecteur cesse d'être un juge et redevient ce
qu'il aurait toujours dû être — **une liste de questions**. Reste ouvert dans #113, avec la
mesure jointe plutôt qu'une promesse.

## Garde

Invariant **I10** dans `check_universal_default.py`, dans les trois sens — un affinage successif
finit par ne plus rien détecter du tout si rien ne l'en empêche, et il y en a eu trois le même
jour :

- une paire de valeurs limites (même forme, résultats attendus **différents**) est **signalée
  sans pénalité** — et signalée, sinon la correction aurait supprimé la détection au lieu de la
  requalifier ;
- une paire ne différant **que par ses littéraux** n'est pas pénalisée non plus — c'est le cas
  que la deuxième règle facturait encore, et le plus difficile à voir ;
- un doublon **strict** (étapes identiques octet pour octet) reste pénalisé — sans quoi le
  détecteur aurait été éteint, pas affiné.

*La contre-épreuve a d'abord échoué pour une raison qui est à moi* : ma fixture « vrai doublon »
faisait varier le `Given` (499/501) et se croyait stricte. Elle ne testait donc pas le cas
qu'elle nommait.

Campagne de mutation : **41 mutations, 41 tuées.** Une survivante intermédiaire a révélé un défaut
de mon propre code : `redundant_groups = duplicate_groups` n'était qu'un alias, et il ne pilotait
que le **texte du constat** — la pénalité, elle, se calculait ailleurs. Une mutation vidant
l'alias changeait donc ce que le rapport *dit* sans changer ce que le score *fait*. **Deux noms
pour une chose sont déjà un endroit où les deux peuvent diverger.** Alias supprimé.
