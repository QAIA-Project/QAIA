# Fourth batch — 14 repositories, 1 011 tests, 0 filed, and the defect that would have made me file wrongly

**Cumulative: 62 repositories, 3 234 Playwright tests.**

This report exists because an adversarial review on 2026-08-09 pointed out that batch 4 was
recorded in the decision register (D178) and had **no report at all**, while the campaign's
headline figures — "490 false findings", "7 tool defects" — were being carried forward onto
"62 repositories and 8 defects". A three-batch number attached to a four-batch campaign.

| | batch 1 | batch 2 | batch 3 | **batch 4** |
|---|---:|---:|---:|---:|
| repositories | 9 | 18 | 21 | **14** |
| tests | 271 | 863 | 1 089 | **1 011** |
| confirmed defects | 0 | 2 findings / 19 tests | 0 | **0** |
| tool defects found | 2 | 3 | 2 | **1** |

## Defect 8 — `empty-test-body` fired on declared placeholders

Two repositories came back with empty test bodies: `solidcouch/solidcouch` (10) and
`Studio-Saelix/sencho` (6). The rule was written the day before and had just produced a real,
filed-worthy finding on a third repository, so the temptation to file was strong.

Reading the source first showed this:

```ts
test.fixme('give contacts access to my hospex', () => {})
test.fixme('allow removing other person from contacts', () => {})
```

**`test.fixme()` is exactly the mechanism the rule recommends.** Playwright reports those as
*skipped*, not passed — which is the entire remedy the finding proposes. `solidcouch/solidcouch`
was doing the right thing, and the rule was about to reproach it for that.

`TEST_DECL` captured the modifier but `empty-test-body` ignored it. Declared placeholders
(`fixme`, `skip`, `fail`) are now exempt; an *undeclared* empty body still blocks.

After the fix: `empty-test-body` drops to **0** on both repositories.

**Without the standing rule that every finding is read in the source before it leaves the machine,
a wrong issue would have been filed against a project for following the advice the finding gives.**

## The corrected campaign totals

| # | Defect | False findings |
|---|---|---:|
| 1 | `collect_feature_ids` returned one value where the caller unpacked two | crash |
| 2 | Three of four budget lines encode QAIA conventions | 408 |
| 3 | `.spec.ts` treated as a Playwright marker | 7 |
| 4 | `expect.poll()` chains split across lines | 12 |
| 5 | `toBeDefined()` flagged as hollow on any value | 24 |
| 6 | Verification delegated to a page object or helper not counted | 38 |
| 7 | Angular/Karma specs judged because they import no runner | 1 |
| **8** | **`empty-test-body` fired on `test.fixme()`** | **16** |

**91 constats faux imputables a la campagne, contre 2 constats confirmes** portant sur 19 tests, sur 62 depots et 3 234 tests.

Ce chiffre a ete faux **trois fois**, et le detail vaut plus que le total :

| Publie | Erreur |
|---|---|
| « 490 contre 19 » | **19 etait un compte de TESTS** mis pour un compte de constats, et le lot 4 manquait |
| « 506 contre 2 » | **melange deux populations** : les 408 de RealWorld sont au numerateur, mais RealWorld n'est pas l'un des 62 depots, ses 128 tests ne sont pas dans les 3 234, et son 1 constat confirme est exclu du denominateur |
| **91 contre 2** | 506 − 408 (RealWorld, autre population) − 7 (les 7 de `valhalla/web-app` comptes au defaut 3 **et** dans les 24 du defaut 5) |

**Un nombre qui s'est trompe trois fois ne doit pas servir d'exemple de rigueur.** Trouve en recomputant, jamais en relisant.

## Ce que ce lot dit et que les trois premiers ne disaient pas

Le lot 1 trouvait 20 candidats sur 271 tests. Le lot 4 en trouvait 40 sur 1 011, et les 40 etaient
faux — 16 d'une regle ecrite la veille.

**Mais « 40 » n'est pas reproductible, et c'est la trouvaille la plus severe de la relecture.** En
rejouant les tranches du lot 4 avec l'outil corrige : **~73 candidats en premiere passe**, pas 40.
Ce rapport ne discutait que les 16 `fixme`, puis affirmait que « les 40 etaient faux ». Les ~41
autres — `bmatge/dsfr-data` 19, `solidcouch` 13, `Studio-Saelix/sencho` 11 — **n'ont jamais ete lus
a l'oeil et n'apparaissent dans aucun rapport**.

**Et un neuvieme defaut etait vivant jusqu'a sa decouverte.** Le correctif du defaut 8 a ete
applique a `empty-test-body` et **pas a sa jumelle** `test-without-assertion`, egalement bloquante,
qui continuait de tirer sur les memes `test.fixme`, dans les memes depots, aux memes lignes :
**24 constats**, un lot entier apres que la campagne ait declare le defaut corrige.

« Corrige pour le cas devant moi plutot que pour la classe » : le lot 3 avait nomme le motif, le
lot 4 l'a commis de nouveau, **et personne n'a rejoue les lots precedents pour s'en apercevoir**.
Rejouer chaque lot apres chaque correctif coute trois minutes. Ce n'a jamais ete fait.

**A new rule is at its most dangerous on the day it is written**, when it has just been validated
on the one case it was built from and has not yet met a project that solves the problem differently.
Both batch-4 repositories were doing it right.

## Honest limits

- **0 issues filed.** The two written in batch 2 remain unfiled — the environment refused further
  third-party issue creation, and the block was not worked around.
- **Static track only**, as in every batch. No application was stood up.
- **Absence of findings is not proof of quality.** These suites were judged on assertion shape,
  not on whether they assert the right thing.
