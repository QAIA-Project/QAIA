# Cadre de revue d'architecture QAIA

> **Document consomme — entree de campagne, pas guide vivant (marque le 2026-08-10).**
> Ce fichier est le *prompt* qui a servi a lancer la revue d'architecture ; son resultat est la
> note 5,0/10 consignee dans `docs/STATUS.md`. Il est garde pour la provenance : on doit pouvoir
> relire ce qu'on a demande avant de juger ce qu'on a obtenu. **Il ne decrit pas l'etat actuel du
> projet** et ne doit pas etre lu comme tel. Non deplace : des campagnes gelees sous `eval/` le
> referencent par ce chemin.

Origine : proposé par ChatGPT le 2026-08-08, dans un lot de trois analyses externes du dépôt
commandées par le fondateur. Des trois, c'est la seule qui n'avance aucune affirmation fausse —
parce qu'elle n'avance aucun chiffre : c'est une **méthodologie**, pas un diagnostic. Les deux
autres ont produit des diagnostics chiffrés dont la moitié n'a pas survécu à la vérification
(voir `ACTION-PLAN.md`, partie 1).

Conservé ici pour que **toute revue future parte du même cadre**, quel que soit l'agent qui la
mène, et pour qu'on puisse comparer deux revues séparées de six mois.

## Les deux règles qui comptent

> *Always prefer documented evidence over assumptions.*
> *Never invent project goals.*

Ce sont exactement les deux règles que les deux autres analyses ont violées : l'une a décrit un
produit d'évaluation de LLM que QAIA n'est pas, l'autre a inventé un numéro d'issue et sa
priorité. À lire avant de commencer, pas après.

## Dimensions à couvrir

1. **Vision produit** — positionnement, proposition de valeur, utilisateurs cibles,
   différenciation, paysage concurrentiel, cas d'usage manquants
2. **Architecture** — frontières de modules, graphe de dépendances, couplage, extensibilité,
   dette technique, sur-ingénierie, abstractions manquantes
3. **Organisation du dépôt** — structure, conventions de nommage, séparation des responsabilités,
   découvrabilité
4. **Documentation** — pour chaque document : utile ? redondant ? périmé ? trop verbeux ?
   incomplet ?
5. **Expérience développeur** — installation, démarrage rapide, CI, première contribution.
   Estimer le temps qu'il faut à un nouveau contributeur pour être productif
6. **Qualité de code** — complexité, lisibilité, cohérence, gestion d'erreur, stratégie de test
7. **Architecture IA** — prompts, skills, agents, gestion du contexte, coût en tokens,
   atténuation des hallucinations. L'architecture reste-t-elle maintenable quand le nombre
   d'agents croît ?
8. **Stratégie QA** — validation, revue humaine, traçabilité, prévention des régressions, portes
   de qualité. Alignement avec la philosophie du projet
9. **Maturité open source** — README, releases, versionnage, issues, gabarits, licence,
   accueil des contributeurs. *Qu'est-ce qui empêche ce dépôt de devenir une référence ?*
10. **Potentiel** — différenciation, barrières à l'adoption, potentiel de communauté

## Notation

Noter chaque dimension de 0 à 10. **Justifier chaque note par une preuve du dépôt.** Une note
sans fichier cité est une opinion, et elle ne compte pas.

## Sortie attendue

Un backlog en quatre catégories — moins d'un jour, moins d'une semaine, moins d'un mois,
stratégique — avec pour chaque entrée : priorité, impact attendu, effort estimé, risques,
dépendances.

Puis une feuille de route par jalons, chacun produisant une valeur visible. **Pas de grande phase
de refactoring.**

## Règles d'exécution

Ne jamais tout implémenter d'un coup. Pour chaque itération : expliquer le problème, la solution
proposée, pourquoi c'est la meilleure option, les risques — **puis attendre validation**. Ensuite
implémenter, mettre à jour la documentation, `STATUS.md`, et `DECISIONS.md` si l'architecture a
changé.

## Ton

Rigoureux, sans mots à la mode. Adosser chaque conclusion à une preuve du dépôt. Quand il y a
doute, énoncer l'hypothèse. **Préférer la critique constructive à l'éloge.**

L'objectif n'est pas de maximiser la quantité de code produite, mais la qualité, la
maintenabilité et l'adoption de QAIA sur la durée.
