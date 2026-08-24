# Performance du noyau déterministe — mesurée, et ce n'est pas là que le coût est

**Date** 2026-08-24 · Machine : Windows 11, Python 3.12, mono-thread

La refonte fait du noyau Python **le produit**. Un produit qu'on demande à quelqu'un de lancer
sur son dépôt doit savoir ce qu'il coûte. Personne ne l'avait jamais mesuré.

## Débit sur le corpus réel

`structural_score.py` sur les 257 cahiers Gherkin étrangers (924,6 Ko) :

| | |
|---|---:|
| total | **0,17 s** |
| débit | **1 545 fichiers/s** — 5,4 Mo/s |
| par fichier | médiane **0,36 ms**, p95 1,97 ms, max 8,28 ms |

## Montée en charge — la question qui comptait

Le détecteur de redondance (« paradoxe du pesticide ») compare des scénarios entre eux. Écrit
naïvement, il serait en O(n²) et exploserait sur un gros cahier — le cas exact où un utilisateur
lancerait l'outil sur toute sa suite d'un coup.

Fichiers synthétiques, de 50 à 3 200 scénarios, dans les deux régimes (tous distincts / tous
identiques, ce dernier étant le pire cas pour le détecteur) :

| scénarios | distincts | identiques |
|---:|---:|---:|
| 50 | 7 ms | 7 ms |
| 200 | 13 ms | 12 ms |
| 800 | 32 ms | 33 ms |
| 1 600 | 61 ms | 58 ms |
| 3 200 | **108 ms** | **106 ms** |

**Linéaire, et insensible au régime.** Le détecteur groupe par empreinte de forme dans un
dictionnaire au lieu de comparer les paires : le pire cas théorique n'existe pas.

`automation_score.py` (passe statique seule) sur des suites de 50 à 1 600 tests : **99 ms pour
1 600 tests**, également linéaire. Le score reste à 99,9 et trois dimensions restent applicables
à 1 600 tests comme à 50 — la traçabilité étrangère (`JIRA-####`) est créditée à toutes les
échelles, ce qui vérifie le correctif du jour hors de ses fixtures.

## Ce que cette mesure ne dit pas, et qui est le vrai sujet

**Le noyau ne coûte rien. Le coût du produit est ailleurs, et il n'a pas bougé.**

QAIA coûte **2,9× un bon prompt direct** en tokens (133 100 contre 46 548) pour un rappel
d'ambiguïtés inférieur — mesure du 2026-07-28, jamais rejouée depuis. Ce coût est entièrement
dans la couche LLM : les six étapes du parcours avec leurs points de validation.

La refonte a d'abord réparé la face *juger*, qui est **la seule qui ne passe pas par un LLM du
tout** — un utilisateur peut noter ses cahiers sans consommer un seul token de son quota. C'est
délibéré : c'est la seule face dont un inconnu peut se servir sans rien adopter, et la seule dont
le coût soit nul.

Réduire le 2,9× de la face *générer* reste à faire, et c'est la cible ≤ 1,5× du
[tableau de bord](../../docs/DASHBOARD.md).

## Reproduire

```bash
python eval/tools/bench_core.py --corpus /chemin/vers/corpus
python eval/tools/bench_core.py            # montée en charge seule, sans corpus
```

*Note de méthode.* Ce rapport a d'abord été écrit en expliquant que les deux bancs **n'avaient
pas été figés en script**, au motif qu'une conclusion rassurante ne demande pas de surveillance.
C'est faux, et c'est exactement le cas où l'on est le plus tenté de s'en dispenser : une mesure
qu'on ne peut pas rejouer n'est pas une preuve, que son résultat arrange ou non. Le banc est donc
`eval/tools/bench_core.py`, et il vérifie au passage quelque chose que le selfcheck ne voit pas —
que la traçabilité étrangère reste créditée **à toutes les échelles**, pas seulement sur une
fixture de deux tests.
