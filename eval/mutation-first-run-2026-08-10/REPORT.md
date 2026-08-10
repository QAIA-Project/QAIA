# Premiere execution de la passe mutation — 2026-08-10

**Cible** `examples/expense-demo/tests` (56 tests, suite verte verifiee avant : `56 passed`).
**Cahier** `examples/expense-demo/qaia-journey/testbooks/US-004`.
**Sortie brute conservee** : `automation-score.json` (regle 4bis du contrat partage).

| | |
|---|---|
| Mutations executees | **10** (plafond `--max-mutations 10`) |
| Tuees | **10** — l'assertion inversee a fait rougir son test |
| **Survivantes** | **0** |
| Score statique | 95.3 / 100 |

Une assertion qui survit a son inversion ne verifie rien. **Aucune n'a survecu.**

## Pourquoi c'est la premiere fois

La passe est la plus forte idee du catalogue et elle n'avait jamais tourne. La raison n'etait pas
la negligence : sur Windows, `npx` est `npx.CMD`, et `subprocess` avec `shell=False` -- voulu, la
faille B8 l'impose -- ne resout pas `PATHEXT`. Le lancement de reference echouait en
`OSError: [WinError 2]` **avant la moindre mutation**, et le champ `blocker` le disait dans un
JSON que personne ne lisait. Corrige en resolvant l'executable par `shutil.which`, sans
reintroduire de shell.

C'est la machine du fondateur qui est sous Windows : la seule preuve mecanique que les assertions
portent quelque chose etait donc inaccessible la ou le projet s'ecrit.

## Ce que cette mesure ne dit pas

- **10 mutations, pas 56.** Le plafond etait pose pour borner le temps ; 46 assertions n'ont pas
  ete inversees. « Aucune survivante » vaut pour l'echantillon, pas pour la suite.
- Elle porte sur **une suite generee par QAIA et notee par QAIA**, sur une application ecrite par
  ce projet. C'est la forme de preuve la plus faible, comme le README le dit deja pour le reste.
- Effet de bord constate : la passe restaure le contenu des fichiers mutes mais reecrit leurs
  fins de ligne, ce qui laisse l'arbre de travail sale sur Windows (contenu identique, 0 ligne
  changee).
