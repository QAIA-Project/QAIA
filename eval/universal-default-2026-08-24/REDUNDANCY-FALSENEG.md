# Le faux négatif du détecteur de doublons n'est pas fermable par le texte — mesuré

**Date** 2026-08-24 · Dernier point ouvert de [#113](https://github.com/QAIA-Project/QAIA/issues/113).
La moitié faux-positif a été corrigée le jour même (voir `REDUNDANCY.md`). Reste le faux négatif :
deux scénarios copiés-collés dont le `When` dérive d'un ou deux mots ne sont pas vus, parce que leur
`shape_key` (littéraux réduits) diffère et qu'ils ne sont donc jamais comparés.

```gherkin
When l'utilisateur ajoute "REF-100"
When l'utilisateur ajoute l'article "REF-100"
```

La piste de l'issue : une **similarité de jetons** (Jaccard sur étapes normalisées) au lieu de
l'égalité stricte. Garde-fou non négociable : **mesurer sur le corpus étranger avant d'écrire la
règle**.

## Corpus

224 cahiers Gherkin **réels** re-clonés (diaspora 71, cucumber-ruby 153) — 787 scénarios,
3 275 paires intra-fichier. Le détecteur actuel groupe déjà **276 paires** par `shape_key` exact.
Mesure sur les paires qu'il **rate** (forme différente).

## Balayage Jaccard sur Given/When normalisés (paires que le détecteur actuel ne voit pas)

| seuil *s* | NEW littéraux identiques (signature copie-collé) | NEW littéraux différents (métamorphique = **faux positif**) |
|---:|---:|---:|
| 0.60 | 36 | 346 |
| 0.70 | 28 | 188 |
| 0.80 | 19 | 63 |
| 0.90 | 8 | 26 |
| 0.95 | 1 | 17 |

**À tous les seuils, les faux positifs dépassent les vrais.** Jaccard seul est un mauvais
pénaliseur — pénaliser reproduirait exactement le faux positif corrigé le matin (valeurs limites /
nominal-refus facturées).

## On resserre : littéraux identiques **ET** `Then` identique

| seuil *s* | même `Then` (vrai copie-collé ?) | `Then` différent (comportement distinct) |
|---:|---:|---:|
| 0.70 | 16 | 12 |
| 0.80 | 9 | 10 |
| 0.90 | 4 | 4 |

Toujours ~50/50. Et le premier « même `Then` » à 0.88 est
`the reference screenshot directory is used` vs `the comparison screenshot directory is used` :
mêmes littéraux, même `Then`, **comportement distinct** (répertoire de référence vs de comparaison).
Aucun de ces trois filtres ne l'écarte.

## On resserre encore : inclusion de jetons (insertion pure) vs substitution

Hypothèse : le cas de #113 est une **insertion** (`{ajoute} ⊂ {ajoute, l'article}`) ; reference/
comparison est une **substitution** (chacun a un mot unique). Sur les paires à littéraux identiques,
J ≥ 0.6 :

- **inclusion** (un jeu ⊆ l'autre) : **15** — dont 6 à même `Then`, 9 à `Then` différent ;
- **substitution** : 21 — et reference/comparison y tombe, **correctement exclu**.

L'inclusion écarte reference/comparison, mais **fuit encore** :
`i run \`cucumber -q …\`` vs `i run \`cucumber -x -q …\`` est une inclusion à même `Then` — et c'est
un **test délibérément distinct** (l'option `-x` est précisément ce qu'on teste). Le mot inséré
change le comportement ici, et ne le change pas dans le cas de #113. Le texte ne peut pas les
distinguer.

## Conclusion

**Aucune signature textuelle testée — Jaccard, + littéraux identiques, + `Then` identique,
+ inclusion de jetons — n'isole proprement le copie-collé du test délibérément proche.** Chaque
filtre laisse passer des tests distincts légitimes (`-x`, reference/comparison…) à un taux
comparable à celui des vrais doublons. Le signal qui les sépare — *le mot inséré/substitué
change-t-il ce qui est testé ?* — est **sémantique**, pas textuel.

C'est exactement la thèse déjà inscrite dans `structural_score.py` :

> *A detector that charges points for a judgement it cannot make is worse than a silent one — it
> carries the authority of a number.*

Un signalement (sans pénalité) souffrirait du même défaut : à ~50 % de précision après trois
filtres, il porterait « l'autorité d'un chiffre » sur un jugement qu'il ne peut pas rendre.

**Décision recommandée :** ne pas ajouter de règle de similarité textuelle — ni pénalité, ni
signalement. Le faux négatif est une **limite mesurée** de tout outil de texte ; on le nomme dans
le docstring du détecteur plutôt que de le masquer par un signal bruité. La mesure a tué la règle,
et c'est le bon résultat.

*Rejouable : `eval/tools/measure_redundancy_falseneg.py <dir>` sur un corpus de cahiers `.feature` réels (re-cloné, non versionné).*
