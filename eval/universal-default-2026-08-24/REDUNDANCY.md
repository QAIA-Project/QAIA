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

## Ce qui n'est pas corrigé

**Le faux négatif reste entier.** Deux scénarios manifestement copiés-collés ne sont pas vus dès
que leurs `When` diffèrent de deux mots :

```gherkin
When l'utilisateur ajoute "REF-100"
When l'utilisateur ajoute l'article "REF-100"
```

Formes différentes → pas de doublon. Or **un copier-coller humain dérive toujours d'un mot ou
deux** : *le détecteur ne trouve que les doublons qu'un humain ne produit jamais.*

Une forme approchée (similarité de jetons) le corrigerait, au risque de ramener des faux
positifs. La règle de la refonte s'applique : **elle sera mesurée sur le corpus avant d'être
écrite**, pas l'inverse. Reste ouvert dans #113.

## Garde

Invariant **I10** dans `check_universal_default.py`, dans les deux sens :

- une paire de valeurs limites (même forme, résultats attendus **différents**) doit être
  **signalée sans pénalité** — et signalée, sinon la correction aurait supprimé la détection au
  lieu de la requalifier ;
- un **vrai** doublon (même forme **et** même résultat) doit rester pénalisé — sans quoi le
  détecteur aurait été éteint, pas affiné.

Campagne de mutation : **40 mutations, 40 tuées.** Une survivante intermédiaire a révélé un défaut
de mon propre code : `redundant_groups = duplicate_groups` n'était qu'un alias, et il ne pilotait
que le **texte du constat** — la pénalité, elle, se calculait ailleurs. Une mutation vidant
l'alias changeait donc ce que le rapport *dit* sans changer ce que le score *fait*. **Deux noms
pour une chose sont déjà un endroit où les deux peuvent diverger.** Alias supprimé.
