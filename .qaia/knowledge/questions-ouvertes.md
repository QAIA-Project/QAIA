# Questions ouvertes — ce que la spécification ne tranche pas

> Source : `state/US-002/02-understanding.md`. **Aucune n'est répondue ici.** Ce fichier existe
> pour qu'une génération ultérieure sur le même domaine les retrouve au lieu de les redécouvrir —
> ou pire, de les résoudre en silence.
>
> **Neuf des dix ne portent aucun défaut** : l'US est intégralement en domaine protégé (santé), où
> aucun défaut n'est sûr.

| ID | Question | Statut | Défaut |
|---|---|---|---|
| Q1 | Une dose **exactement égale** au maximum par prise est-elle autorisée ? AC2 dit « strictly below » pour le minimum, AC3 ne dit rien pour le maximum | `[open]` | aucun |
| Q2 | Aucune **unité de dose** n'est nommée nulle part | `[open]` | aucun |
| Q3 | La fenêtre 24 h est-elle **glissante** ou **calendaire**, et sur quelle horloge ? | `[open]` | aucun |
| Q4 | La réduction de 50 % d'AC6 s'applique-t-elle aussi au **minimum efficace** ? Si non, un médicament dont le max réduit passe sous le min rend toute dose simultanément sous-minimum et sur-maximum | `[open]` | aucun |
| Q5 | L'exception de rôle d'AC5 convertit-elle aussi un **blocage de seuil** issu d'AC6 ? | `[open]` | aucun |
| Q6 | Aucune **règle d'arrondi** pour la réduction de 50 % sur une valeur impaire | `[open]` | aucun |
| Q7 | Que se passe-t-il quand un médicament **n'a pas de fiche** ou qu'elle est incomplète ? | `[open]` | aucun |
| Q8 | Deux prescriptions **concurrentes** peuvent chacune être conformes et leur somme dépasser le cumul | `[open]` | aucun |
| Q9 | **Tout** prescripteur peut-il surcharger, ou seulement l'auteur ? | `[open]` | aucun |
| Q10 | Les « 20 caractères » se comptent comment ? 20 espaces suffisent-ils ? | `[assumption]` | ≥ 20 points de code Unicode après suppression des espaces de tête et de fin |

## La contradiction à trois règles

**AC2 × AC6 × AC3** est la seule triade indécidable : prises deux à deux les règles sont
cohérentes ; à trois, sur un médicament dont le maximum réduit tombe sous le minimum efficace,
aucune ne dit quel verdict l'emporte. Le cas est atteignable dès que **max < 2 × min**, ce qui est
courant. Consignée en Q4, et le jeu de données porte `DRUG-D` construit exprès pour l'exercer.

## Réserve sur la valeur de ces questions

Q1, Q3, Q4 et Q6 recoupent les ambiguïtés plantées dans la fixture du gold set — et leur substance
avait **déjà été recopiée** dans `state/US-002/00-source.md` avant que la chasse ne commence. Elles
ne démontrent rien sur la capacité à trouver une ambiguïté. **Q2, Q5, Q7, Q8, Q9 et Q10** ont été
dérivées du seul texte des critères : ce sont les seules dont la découverte soit défendable.
