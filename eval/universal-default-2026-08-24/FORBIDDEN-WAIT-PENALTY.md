# Attentes interdites : mesure avant la règle (#112)

**Date : 2026-10-17. Outil mesuré : `eval/tools/automation_score.py`, piste statique, profil `universal`.**

## Le défaut

`#112` : *« Le barème universel d'automatisation est trop pauvre : `realworld` obtient 100,0
avec 8 attentes interdites au compteur. »*

Reproduit sur la mesure archivée de la campagne du 2026-08-09
([`eval/realworld-2026-08-09/static-score.json`](../realworld-2026-08-09/static-score.json)) :

| suite | profil | dimensions notées | `score` | `waitForTimeout` au compteur |
|---|---|---|---|---|
| `realworld-apps/realworld` (128 tests) | universal | `substantive_assertions` seule | **100,0** | **8** |

Le score n'était pas faux — la suite est parfaite sur la substance de ses assertions — il était
**étroit** : les huit attentes interdites étaient relevées comme constats `forbidden-wait` non
bloquants, puis **absentes du nombre**. Un « 100 sur 100 » qui ignore huit fragilités temporelles
ne dit pas la vérité, même en se déclarant étroit (`scoreScope.narrow = true`). C'est le reproche
de #112.

## Pourquoi une pénalité transfère hors de notre production

La porte d'entrée du barème universel (docstring de `static_track`) :

> Toute nouvelle ligne de budget doit passer la porte d'entrée de la refonte : être mesurée sur
> du matériau étranger avant d'entrer, et ne jamais pénaliser une suite pour n'avoir pas adopté
> une convention de ce projet.

Une attente interdite **n'est pas une convention de QAIA**. La documentation Playwright elle-même
la proscrit : `page.waitForTimeout()` est explicitement marquée *« never wait for a timeout in
production »*, et `waitForLoadState('networkidle')` est *« discouraged »*. C'est un anti-patron
reconnu de toute la communauté Playwright, pas une préférence maison. La pénaliser dans le profil
`universal` juge donc une fragilité réelle, pas l'allégeance à nos conventions — et pour cette
raison elle s'applique **aussi sous le profil `qaia`**, où `automate` l'interdit déjà.

## Mesure sur matériau étranger (prévalence)

Huit suites tierces, récupérées via jsDelivr (l'API GitHub est bloquée dans ce bac à sable ;
`raw.githubusercontent.com` et `cdn.jsdelivr.net` sont joignables). Détection par les propres
motifs `FORBIDDEN_WAITS` de l'outil, commentaires retirés (`code_of`) :

| suite (tierce) | specs | tests | attentes interdites |
|---|---:|---:|---:|
| `realworld-apps/realworld` (archive 2026-08-09) | 12 | 128 | **8** |
| `solidcouch/solidcouch` | 1 | 3 | **3** |
| `mxfng/drumhaus` | 17 | 29 | 0 |
| `dbcls/sparqlist` | 3 | 6 | 0 |
| `microsoft/playwright-mcp` | 3 | 6 | 0 |
| `US-EVAL-001` saucedemo (local) | 2 | 9 | 0 |
| `reverse-engineering` (local) | 2 | 57 | 0 |
| `external-application` (local) | 1 | 32 | 0 |

**Deux suites sur huit en portent, six n'en ont aucune.** Une attente interdite est donc *rare*
dans une suite tierce ordinaire : la pénalité ne frappe pas le cas commun. Quand elle frappe
(`realworld`, `solidcouch`), c'est sur une fragilité temporelle avérée — `waitForTimeout(5000)`,
`(1000)`, `(500)` dans `solidcouch/messages.spec.ts`, un délai fixe en dur qui rend le test lent
et instable.

## La règle choisie, et pourquoi pas une dimension de budget

**Déduction plafonnée, pas dimension de budget.** Une dimension-fraction (`tests sans attente /
tests`, poids ~25) rendrait la pénalité négligeable sur une grande suite : `realworld` à 8/128
coûterait ~0,2 point et resterait à ~98 — ce qui ne corrige rien. Une déduction **par
occurrence**, plafonnée, mord dès la première attente et sature :

```
penalite = min(WAIT_PENALTY_CAP, nombre_d_attentes * WAIT_PENALTY_PER)
score    = max(0, budget - penalite)
WAIT_PENALTY_PER = 2,0   WAIT_PENALTY_CAP = 20,0
```

Non bloquante : une attente est une *fragilité*, pas un *mensonge* ; les constats bloquants
(assertion creuse, tautologique, test sans assertion) s'occupent des mensonges. Une suite n'est
donc jamais ramenée à zéro pour cela seul — une suite par ailleurs parfaite plafonne à 80,0.

## Avant / après (vérifié)

| suite | budget | attentes | pénalité | score avant | **score après** |
|---|---:|---:|---:|---:|---:|
| `realworld` (#112) | 100,0 | 8 | 16,0 | 100,0 | **84,0** |
| `solidcouch/messages` | 100,0 | 3 | 6,0 | 100,0 | **94,0** |
| `mxfng/drumhaus` | 96,1 | 0 | 0,0 | 96,1 | **96,1** (inchangé) |
| `dbcls/sparqlist` | 89,0 | 0 | 0,0 | 89,0 | **89,0** (inchangé) |
| suite 40 attentes, sinon parfaite | 100,0 | 40 | 20,0 (plafond) | 100,0 | **80,0** (jamais 0) |

Le cas #112 ne marque plus 100,0. Les suites propres gardent leur note au point près. La
régression est discriminante : elle baisse exactement les suites qui portent la fragilité, et
seulement elles.

Garde-fou : `eval/tools/selfcheck_automation_score.py`, section 10 — budget plein + attentes ⇒
score < 100, −2/attente, plafond à 20, zéro attente ⇒ aucune pénalité, s'applique sous les deux
profils.
