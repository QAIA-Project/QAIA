# Ce que la refonte a coûté quand trois relecteurs en contexte vierge l'ont attaquée

**Date** 2026-08-24 · Trois passes indépendantes sur les quatre commits du jour, aucune ne
partageant le contexte de l'autre ni celui de l'auteur.

| Passe | Consigne |
|---|---|
| **Réfutation** | attaquer sept affirmations chiffrées ; réfuter par défaut au moindre doute ; rejouer chaque commande |
| **Persona** | Salma, QA lead, huit ans de Cucumber, 30 minutes, aucune patience pour un outil qui exige ses conventions |
| **Développeur** | relecture hostile du diff des quatre commits ; prouver chaque défaut par une commande |

## Le résultat, avant le détail

**Sur sept affirmations publiées : deux réfutées, deux affaiblies, trois tiennent.** Onze défauts
distincts trouvés, dont **six régressions introduites le jour même par la refonte elle-même**.

Aucun n'a été trouvé par les 30 mutations, ni par les neuf invariants de la garde, ni par la CI.

## Les deux réfutations

### A7 — « la détection de traçabilité est désormais universelle » : **RÉFUTÉE**

Deux cahiers rigoureusement identiques, seule la convention de tag diffère :

| convention | score | porte | traceability |
|---|---:|---|---:|
| `@QAIA-US-004-009` | **88** | PASS | 25,0 / 25 |
| `@JIRA-1234` | **78** | CONCERNS | 15,0 / 25 |

`REQ_REF_RE` avait bien été élargi. **La seconde moitié de la formule ne l'avait pas été** :

```python
ac_linked = [s for s in scen if any(re.search(r"@AC[:_-]?\w+|@QAIA-\w+-\d+", t) for t in s["tags"])]
traceability = 25 * (len(traced) / n) * (0.6 + 0.4 * (len(ac_linked) / n))
```

Le facteur `0,4` restait réservé à nos identifiants. Un cahier étranger **parfaitement tracé**
plafonnait à 60 % de la dimension, perdait dix points et changeait de porte. **Le défaut que
toute la refonte prétend supprimer, conservé à l'échelle 0,4.**

*Et la garde ne pouvait pas le voir* : l'invariant I4 n'exigeait qu'un crédit **non nul**. Il
passait au vert à 15/25. Le rapport le présentait comme la preuve que l'outil « créditerait
quelqu'un d'autre » ; il prouvait un crédit non nul, jamais un crédit **égal**.

**Corrigé** : le raffinement `ac_linked` devient une convention du profil `qaia`. Nouvel
invariant **I6** — le même cahier doit rendre le même score sous quatre conventions différentes.

### A5 — « 11 constats vides ; après correctif, 3 réels » : **RÉFUTÉE sur la seconde moitié**

Les trois rescapés étaient de la même espèce que les onze. Le seul dépôt déclaré comparable
affichait `path_status_pairs_in_suite: 0` — le symptôme que le rapport lui-même désigne comme la
définition de la cécité. Ses « 2 codes HTTP reconnus » étaient un `418` et un `500` littéraux dans
un test unitaire d'un formateur de log, qui n'émet aucune requête vers aucun chemin de la
spécification.

**La garde avait été posée sur `all_status` alors que le diagnostic désignait `pairs`.** Verdict
honnête après correction : **quatre dépôts, quatre `UNCOMPARABLE`, zéro constat.**

## Les deux affaiblissements

**A4 — « 80 % de bruit retiré sur les suites Playwright ».** Vrai en agrégé, porté par une seule
suite : `realworld` fournit 401 des 571 constats retirés. Médiane par suite **62,5 %**, hors
`realworld` **57,6 %**. Le chiffre à retenir pour une suite quelconque est ~60 %, pas 80 %.

**A1 — « 0 PASS → 101 ».** Les trois colonnes se rejouent au chiffre près, le « avant » sur le
code réellement pré-commit. Mais **aucun des tags du corpus ne déclenche `REQ_REF_RE`** : sur ce
corpus, la « détection » se comporte en exclusion inconditionnelle, exactement comme l'ancien
`--third-party`. Le 101 démontre le rebasculage du défaut, **pas la détection**.

## Les six régressions introduites le jour même

| # | Défaut | Effet mesuré |
|---|---|---|
| 1 | **La falaise.** `traceability_assessed = bool(traced)` en tout-ou-rien | **21 points et une porte** perdus pour **un seul** `@HTML5` sur quatre scénarios — l'adoption partielle punie plus durement que l'absence totale |
| 2 | `REQ_REF_RE` sans séparateur obligatoire | `@HTML5`, `@CSS3`, `@IE11`, `@WCAG21`, `@OAuth2` comptés comme références d'exigence |
| 3 | Deux `REQ_REF` divergents dans deux outils du même noyau | `@AC1`, `@TC2` reconnus d'un côté, refusés de l'autre, pour la même notion |
| 4 | Sous `qaia`, `robust_selectors` applicable sans aucun localisateur | Une suite **purement API** — le cas normal d'une suite QAIA sur une US d'API — passait de **73,3 à 55,0** |
| 5 | Sous `qaia`, la traçabilité n'était plus exigée | Un cahier QAIA ayant perdu ses identifiants passait de **75/CONCERNS à 100/PASS** — la porte écrite pour l'attraper le **promouvait** |
| 6 | `automation_score` sur un répertoire vide | `score: 0.0` affirmatif, alors que le commit voisin corrigeait précisément cela dans l'outil frère |

Les six sont corrigés. Quatre nouveaux invariants (**I6** égalité des conventions, **I7** détecter
ne doit jamais punir, **I8** le profil `qaia` ajoute des exigences et n'en retire pas, **I9** les
deux outils s'accordent sur une table de 18 cas) les rendent désormais visibles.

## Ce que la persona a trouvé que personne d'autre n'a vu

Un **chiffre faux affiché comme mesuré** : `negative_ratio_recomputed_pct` annonçait « 0,0 % » sur
un cahier contenant des tests négatifs, parce qu'il compte les scénarios portant le tag
`@negative`. Mesuré : **zéro scénario sur 1 564** en porte dans le corpus étranger.

> « Le jour où je découvre qu'un des chiffres compte en réalité une convention de tags, je cesse
> de croire les autres. »

Ni la réfutation ni la relecture développeur ne l'ont vu : **il ne pèse sur aucun score**. Il pèse
sur la confiance, ce qu'aucun invariant numérique n'attrape. C'est le seul défaut de la journée
qu'aucune des deux autres passes ne pouvait produire.

## Trois défauts de méthode qui sont à moi

1. **J'ai lancé trois relecteurs pendant que j'éditais les fichiers qu'ils mesuraient.** La passe
   de réfutation a vu l'arbre de travail se salir sous elle et a dû le signaler pour que ses
   mesures restent interprétables. Une passe de mesure lancée pendant qu'une autre session édite
   les outils mesurés ne mesure pas un état stable.
2. **Un `\b` passé par le shell est devenu un caractère backspace `\x08`** dans une expression
   régulière — invisible dans `sed`, et le motif ne correspondait plus à rien. `CLAUDE.md`
   interdit de faire passer du Markdown par le shell ; la règle vaut pour tout texte contenant
   des échappements, et le hook ne couvre que les corps de commit.
3. **Deux campagnes du même jour ont nourri un outil d'un matériau qu'il ne sait pas lire** — du
   Go et du Python vers un lecteur JS/TS, du Jest vers un lecteur Playwright. Que l'outil le dise
   désormais est l'acquis ; que je continue à le faire est le coût.

## Ce que l'épisode établit

**La mutation ne remplace pas un lecteur.** Trente mutations tuées, neuf invariants verts, une CI
verte — et onze défauts dont six régressions du jour. Les mutations vérifient que les gardes
gardent ce qu'elles gardent ; elles ne peuvent rien dire de ce que personne n'a pensé à garder.

Les trois angles ont trouvé des choses **disjointes** : la réfutation a attaqué les chiffres, le
développeur a attaqué l'arithmétique et les périmètres, la persona a attaqué la confiance. Aucun
n'aurait suffi.
