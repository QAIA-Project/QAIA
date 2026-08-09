# Ce qui a été archivé, pourquoi, et comment le récupérer

**2026-08-09 — 408 fichiers, 3,5 Mo, sortis de l'arbre et rassemblés dans
`ARCHIVE-raw-captures-2026-07.zip` (1,1 Mo).**

## Pourquoi

Un audit indépendant du dépôt, mené sans accès à nos conclusions, a mesuré ceci :

> Le produit livré fait **138 fichiers / 682 Ko**. Les preuves *à propos* du produit font
> **983 fichiers / 8,2 Mo** — 12× plus lourd, 7× plus nombreux. Un inconnu qui clone ne peut pas
> deviner en cinq minutes que 90 % de ce qu'il regarde ne le concerne pas.

Deux répertoires de campagne pesaient à eux seuls 622 fichiers — **48 % du dépôt** — pour
l'essentiel des captures brutes de session (`A-artifacts/oracle-generate/02-structural-score-v1.txt`
et ses semblables), datant de campagnes menées contre des versions de plugins depuis longtemps
dépassées.

**La crédibilité vient des rapports, pas des 3,5 Mo de sortie terminal derrière eux.**

## Ce qui a été gardé, et pourquoi

| Gardé | Raison |
|---|---|
| Tous les `.md` — rapports, README, VALIDATION, synthèses | Ce sont eux qui portent le raisonnement et les constats |
| Tous les `manifest.json` | Le contrat de sortie, vérifié par `validate_manifest.py` à chaque CI |
| `US-EVAL-001-saucedemo-login/automation/**` **en entier** | **Exécuté par `.github/workflows/generated-suite.yml`** — vérifié ligne par ligne avant la coupe |

**214 fichiers gardés, 1,2 Mo.** Les onze contrôles de `make check` passent après la coupe, et la
suite que la CI joue est intacte.

## Comment récupérer

Trois voies, de la plus simple à la plus complète :

```bash
# 1. l'archive, dans le dépôt
unzip eval/ARCHIVE-raw-captures-2026-07.zip -d /tmp/qaia-raw

# 2. l'historique git — rien n'est perdu, la coupe est un commit comme un autre
git show <sha-avant-coupe>:eval/skill-coverage-wave-2026-07-30/A-artifacts/00-baseline-validate.txt

# 3. le répertoire entier, à la révision qui précède
git checkout <sha-avant-coupe> -- eval/skill-coverage-wave-2026-07-30
```

## Ce que cette coupe ne règle pas

`eval/` reste à **986 fichiers suivis**. L'objectif de l'épique #90 est ~30. Cette coupe traite le
cas le plus gros et le plus clairement mort ; elle ne traite pas les vingt-quatre autres
répertoires de campagne, dont plusieurs datent du même jour et racontent le même travail.

**Et une réserve, formulée par la relecture adversariale de la campagne et qu'il faut lire avant
d'archiver quoi que ce soit d'autre :** le lot 1 de la campagne du 2026-08-09 est déjà
*inauditable*, parce que ses sources récupérées vivaient dans un répertoire temporaire de session
et ont disparu. Le chiffre le plus cité de cette campagne — 428 constats — **n'a aucune preuve
stockée**. Archiver ce qui est reproductible est sain ; laisser expirer ce qui ne l'est pas ne
l'est pas. La règle qui en découle : **un constat dont la preuve ne survit pas à la session n'est
pas un constat.**
