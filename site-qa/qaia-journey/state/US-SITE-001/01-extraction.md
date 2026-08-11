---
stepsCompleted: [us-ingest, us-review]
lastStep: us-review
lastSaved: 2026-08-11
---

# US-SITE-001 — la page qui décide si quelqu'un essaie QAIA

## D'où vient cette exigence, et ce que ça coûte à sa crédibilité

**Elle a été écrite le 2026-08-11, après le site.** Il n'existait aucune exigence écrite pour
`site/` : les trois pages ont été produites directement. Une exigence rédigée après coup risque
d'être une **transcription de l'implémentation** — auquel cas les tests qui en découlent ne
peuvent rien trouver, puisqu'ils décrivent ce qui est déjà là.

C'est dit ici plutôt que découvert plus tard, et deux choses en découlent :

1. Les critères ci-dessous énoncent des **promesses faites au visiteur**, pas des éléments du DOM.
   « Le statut pré-alpha est visible sur chaque page » est une promesse ; « la page contient un
   `<span class="badge">` » serait une description.
2. Le seul critère qui ne pouvait pas être copié de l'implémentation est **AC6** : il porte sur
   la cohérence entre trois fichiers que personne ne lit ensemble (`sitemap.xml`, `robots.txt`,
   et l'ensemble réellement publié). C'est là qu'un défaut avait une chance d'exister.

## La story

> **En tant qu'**ingénieur QA qui vient d'entendre parler de QAIA,
> **je veux** comprendre en moins d'une minute ce que l'outil fait, ce qu'il exige de moi et
> comment l'installer,
> **afin de** décider s'il vaut mon temps — sans avoir à cloner le dépôt.

## Critères d'acceptation

| # | Critère |
|---|---|
| **AC1** | Dès l'ouverture de la page d'accueil, sans faire défiler, le visiteur lit **ce qui entre et ce qui sort**. |
| **AC2** | Le statut **pré-alpha** est annoncé sur **chaque** page publique, pas seulement sur l'accueil. |
| **AC3** | L'installation est **copiable telle quelle** et nomme les deux plugins avec leur commande de marketplace. |
| **AC4** | Toute affirmation de preuve **pointe l'artefact** qui la soutient — pas une reformulation. |
| **AC5** | Chaque destination de navigation interne **répond**, `/demo/` compris. |
| **AC6** | Les lecteurs machine sont servis : `robots.txt` désigne un `sitemap.xml` qui existe, et **le sitemap liste exactement les points d'entrée publiés** — ni plus, ni moins. |
| **AC7** | Chaque page déclare sa langue et porte un titre qui lui est propre. |

## Ce que le site publie, et par quel chemin

Le site publié **n'est pas** le contenu de `site/`. Le workflow `.github/workflows/pages.yml`
assemble deux sources :

```
_site/       <- site/                                   (accueil, comparaison, walkthrough, llms.txt…)
_site/demo/  <- examples/expense-demo/static-demo/      (la démo cliquable)
```

Un test qui servirait seulement `site/` renverrait 404 sur `/demo/` alors que la production
répond 200. **Le harnais assemble donc `_site` de la même façon que le workflow** — et c'est une
duplication de règle assumée, signalée dans `site/tests/README.md` : c'est AC6 qui attrape la
divergence si les deux assemblages cessent de coïncider.

## Hors périmètre, décidé

- **Les liens externes** (GitHub, sites concurrents). Les vérifier ferait dépendre le vert de la
  suite de serveurs que nous ne possédons pas, et un test rouge parce que GitHub est lent n'est
  pas une information sur le site. Voir Q3.
- **Le contenu de `/demo/`**, qui a sa propre suite (`examples/expense-demo/tests/`). Ici on
  vérifie seulement qu'il est **servi**.
- **Le rendu visuel**, couvert par `visual-check` si quelqu'un décide de l'exercer ici.
