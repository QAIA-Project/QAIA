# ADR 0004 — QAIA ne descend pas sous le niveau système

- Statut : **Accepté**
- Date : 2026-08-08
- Clôt : #78

## Contexte

La cartographie du 2026-08-08 (`docs/archive/TEST-COVERAGE-MAP.md`) a croisé les skills du catalogue — 30 au moment où elle a été établie —
avec les niveaux de test ISTQB (CTFL ch. 2.2). Résultat mesuré, pas supposé :

| Niveau | Skills |
|---|---|
| Composant (unitaire) | **0** |
| Intégration | **0** en tant que telle |
| Système | l'essentiel du catalogue |
| Acceptation | partielle |

Ce trou n'avait jamais été décidé. Il existait parce que chaque sprint partait d'une user story et
descendait vers un test exécutable par un navigateur ou un client HTTP, sans que personne ne se
demande où la chaîne devait s'arrêter par le bas.

Un trou non décidé se lit comme un oubli. C'est un problème d'argumentaire autant que de produit :
un lecteur qui remarque l'absence conclut qu'on n'y a pas pensé.

## Décision

**QAIA ne descend pas sous le niveau système, et le déclare.**

L'unité de travail de QAIA est une **promesse observable de l'extérieur** — un critère
d'acceptation, une clause de contrat d'API, une exigence d'accessibilité. Tout ce qu'elle produit
s'exerce à travers une interface publique : navigateur, HTTP, ou le contrat déclaré d'un service.

Ce qui reste **hors périmètre**, explicitement :

- le test unitaire et la génération de cas depuis la signature d'une fonction
- le test d'intégration entre composants internes non exposés
- le test structurel piloté par la couverture de code (boîte blanche)

Ce périmètre est écrit dans le README et dans le catalogue, à côté de ce que le produit fait — pas
dans une note de bas de page.

## Justification

**1. La valeur de QAIA vient précisément de partir du contrat, et le contrat n'existe pas en
dessous.** La campagne externe du 2026-08-08 (`eval/external-application-2026-08-08/`) a trouvé
deux défauts réels dans un projet à 75 694 étoiles en générant depuis sa documentation et **jamais**
depuis son code. Le plus important était un écart d'un caractère entre ce que la documentation
promettait et ce que l'implémentation lisait. **Une suite écrite en regardant le code ne peut pas
trouver cette classe de défaut : elle recopie l'erreur.**

Un test unitaire est écrit contre une fonction, c'est-à-dire contre l'implémentation. Descendre à
ce niveau, c'est abandonner l'oracle qui fait la valeur du reste.

**2. Le terrain est occupé, et bien.** Chaque écosystème a ses générateurs de tests unitaires, la
plupart intégrés aux IDE et aux assistants de code. QAIA n'y apporterait rien qu'on ne trouve
ailleurs, gratuitement, mieux intégré.

**3. Un périmètre déclaré et étroit est un argument.** QA Orchestra écrit noir sur blanc ce qu'elle
ne fait pas — « not in scope : code quality, linting, security scanning, performance profiling,
unit tests » — et ça la sert : un lecteur sait en dix secondes si l'outil est pour lui.

**4. Doubler la surface avant d'avoir prouvé la première moitié serait le mauvais ordre.** À la
date de cette décision, QAIA a **0 étoile, 0 pilote humain**, et une seule application à un
logiciel tiers. Le problème n'est pas qu'elle couvre trop peu de niveaux.

## Conséquences

- Le README et `CATALOGUE.md` portent une ligne « hors périmètre », visible, pas enfouie.
- `docs/archive/TEST-COVERAGE-MAP.md` requalifie la ligne « Composant » : **choix**, plus **trou**.
- Une demande de test unitaire est un refus explicite avec son motif, pas un silence.
- **Ce que la décision n'interdit pas** : un test système *derivé* d'une règle métier calculable
  reste dans le périmètre — ce qui compte est l'interface par laquelle il s'exerce, pas la
  granularité de la règle qu'il vérifie.

## Ce qui ferait rouvrir cette décision

Écrit maintenant, pendant qu'aucun enjeu ne pèse dessus :

- Des utilisateurs réels demandent le niveau unitaire **après** avoir adopté le reste — la demande
  compte quand elle vient de quelqu'un qui utilise déjà, pas d'un lecteur de README.
- Un oracle non-implémentation devient disponible au niveau unitaire, par exemple une
  spécification formelle par fonction. L'argument 1 tomberait, et il porte les autres.

## Alternatives considérées

**Couvrir le niveau composant.** Une skill dérivant des cas unitaires depuis les règles métier
d'une user story. Écartée sur l'argument 1 : ces cas devraient être écrits contre des fonctions,
donc contre l'implémentation, donc en abandonnant l'oracle qui fait la valeur du reste. L'argument
2 s'y ajoute.

**Ne rien décider et laisser le trou.** Écartée : c'était l'état de fait, et il se lit comme un
oubli. Une absence non décidée est indéfendable en revue ; une absence décidée est un
positionnement.
