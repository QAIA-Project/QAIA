# DEF-SITE-001 — la page qui montre le produit marcher est la seule à ne pas dire qu'il est pré-alpha

- **Trouvé le** 2026-08-11, par `QAIA-US-SITE-001-009` (AC2), premier passage du cahier US-SITE-001
- **Trace brute** : `evidence/junit-run-1-red.xml` — 26 tests, 1 échec
- **Sévérité** : majeure — voir plus bas *pourquoi ce n'est pas cosmétique*

## Reproduction minimale

```bash
cd site-qa/tests && npm install && npx playwright test --grep "SITE-001-009"
```

Deux des trois pages passent, la troisième échoue :

```
[e2e-desktop] › @QAIA-US-SITE-001-009 @AC2 "/walkthrough.html" discloses the pre-alpha status
  Expect: locator('body') toContainText(/pre-alpha/i)
```

Vérifiable sans lancer quoi que ce soit :

```bash
grep -ci "pre-alpha" site/index.html site/compare.html site/walkthrough.html
# site/index.html:2   site/compare.html:1   site/walkthrough.html:0
```

## Attendu contre obtenu, tracé jusqu'à l'exigence

| | |
|---|---|
| **Exigence** | AC2 de `US-SITE-001` — *le statut pré-alpha est annoncé sur **chaque** page publique, pas seulement sur l'accueil* |
| **Attendu** | Un visiteur arrivant directement sur `/walkthrough.html` apprend que le projet est pré-alpha |
| **Obtenu** | La page ne porte le mot nulle part. Elle divulgue les limites **de la démonstration** (« It is not evidence that it works on your ticket », le ticket à ambiguïtés plantées, l'exécution non interactive) — mais jamais le statut **du projet**. |

## Pourquoi la sévérité n'est pas « mineure »

1. **C'est la page la plus persuasive du site.** Elle montre six étapes d'une exécution réelle avec
   les fichiers produits. C'est exactement celle où un lecteur conclut « ça marche ».
2. **Elle est indexée séparément.** Le `sitemap.xml` lui donne une priorité de 0.9, supérieure à
   celle de la page de comparaison. Un visiteur venu d'un moteur de recherche ou d'un lien direct
   **n'aura jamais vu l'accueil**, donc jamais l'annonce.
3. **L'omission joue dans le sens qui avantage le projet.** Les deux pages qui portent la mention
   sont celles qui argumentent ; celle qui démontre ne la porte pas. Ce n'est pas ce que l'honnêteté
   du reste du dépôt annonce, et c'est le genre d'écart qu'un lecteur hostile relève en premier.

## Ce que ce défaut dit du dispositif, au-delà du défaut

Le site a été relu plusieurs fois, par plusieurs revues, et personne ne l'avait vu — **parce que
personne ne lit trois pages en se demandant ce qui est vrai sur les trois**. C'est précisément la
classe de condition que `03-design.md` isole (C4, C9, C14) : des promesses transversales que seule
une lecture croisée révèle.

Corollaire honnête : le cahier a trouvé ce défaut **parce qu'un critère d'acceptation disait
« chaque page »**. Sans AC2, aucun scénario n'aurait posé la question. Ce n'est pas l'outil qui a
été malin, c'est l'exigence qui a été écrite.

## Correction proposée

Porter sur `/walkthrough.html` la même mention que les deux autres pages — pas une variante, la
même phrase, pour qu'un lecteur ne puisse pas croire à trois statuts différents.

**Ce qui ne doit pas être fait** : retirer AC2 ou l'assouplir en « au moins une page ». Le test
serait vert et le visiteur toujours mal informé.
