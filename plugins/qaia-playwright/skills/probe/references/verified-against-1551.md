# Éprouvé contre un ticket écrit par un humain

Une rubrique note un rapport contre des critères qu'on a soi-même choisis. Un **ticket humain
existant, sur le même défaut**, est un étalon qu'on n'a pas fabriqué. C'est plus rare et ça vaut
plus cher.

Le défaut : `_dependent` dans `typicode/json-server`. Trouvé par QAIA le 2026-08-08 en générant
depuis le seul README (`eval/external-application-2026-08-08/`), scénario `@QAIA-EXT-030`.
Trouvé par un humain le 2024-05-29, [issue #1551](https://github.com/typicode/json-server/issues/1551),
auteur `wll8`.

## Le ticket humain, en entier

> **`_dependent` value error**
>
> The parameter in the document is `_dependent`, but in the code it is `dependent`, so the data
> is not retrieved correctly.
>
> - version 1.0.0-beta.0
> - Document location *(lien vers la ligne 191 du README au commit 0f392e6)*
> - Code location *(lien vers la ligne 113 de `src/app.ts` au même commit)*
> - *(capture d'écran)*

Quatre lignes. Elles suffisent.

## Comparaison, poste par poste

| | Ticket humain (#1551) | Rapport QAIA |
|---|---|---|
| Cause | **nommée exactement** — `dependent` vs `_dependent`, avec le lien vers la ligne | `non établie` |
| Promesse | lien vers la ligne du README | citée **verbatim** avec sa position |
| Version du SUT | `1.0.0-beta.0` | commit exact `8fb0f72` |
| Reproduction | aucune — le lecteur doit la reconstruire | **test rejouable** `@QAIA-EXT-030` |
| Attendu / obtenu | dans une capture d'écran | en texte, cité de la trace |
| Sévérité | absente | Majeure, avec son argument |
| Traçabilité vers une exigence | implicite | `@QAIA-EXT-030` → `.feature` → README gelé |
| Longueur | 4 lignes | ~25 lignes |

## Ce que ça dit, et qui n'est pas flatteur

**Le ticket humain gagne sur le seul point qui fait gagner du temps au correcteur : la cause.**
`wll8` a ouvert `src/app.ts`, vu la ligne, et donné au mainteneur la correction en une phrase. Le
correctif `1b7c0fb` est arrivé cinq jours plus tard et c'est exactement ce que le ticket disait.

QAIA ne pouvait pas faire ça : le protocole de la campagne lui interdisait d'ouvrir le code. Elle
a donc écrit `Cause : non établie`, ce qui est honnête et **moins utile**.

**Ce n'est pas une limite de la skill, c'est une limite du protocole de cette campagne-là.** Lire
la source, c'est observer ; un rapport qui cite la ligne qu'il a lue respecte la règle « ne jamais
affirmer une cause non observée ». La règle interdit de *deviner*, pas de *regarder*.

## Ce que QAIA apporte que le ticket humain n'a pas

- **Un test qui échoue à la demande.** `#1551` demande au mainteneur de reconstruire le cas.
  `@QAIA-EXT-030` se rejoue en une commande et re-tombera au premier retour en arrière.
- **La promesse citée, pas liée.** Un lien vers une ligne de README pointe vers un fichier qui
  bouge — c'est précisément ce qui s'est passé ici : la section a changé depuis. Le README de
  mai 2024 est gelé dans `sources/`, donc la citation reste vérifiable
  (`check_requirement_drift.py`, D148).
- **Attendu et obtenu en texte.** Une capture d'écran ne se cherche pas, ne se diffe pas, et ne
  survit pas au lien qui l'héberge.

## La conclusion, telle qu'elle est

Ni l'un ni l'autre ne domine. L'humain est meilleur sur la cause parce qu'il a lu le code.
La machine est meilleure sur la reproduction, la traçabilité et la forme — la moitié la moins
intéressante et la plus fastidieuse, donc exactement celle qu'on veut automatiser.

Le meilleur rapport possible est celui qui fait les deux : **partir du contrat pour trouver**,
puis **ouvrir le code pour nommer**. C'est ce que la skill demande, et le protocole de la campagne
externe interdisait volontairement la seconde moitié.
