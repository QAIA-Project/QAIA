# Domaine — validation de posologie

> Source : `state/US-002/01-extraction.md`. **Rien ici n'est extrapolé au-delà de la source** ;
> ce qu'elle ne dit pas est en `questions-ouvertes.md`, pas ici.

## Vocabulaire

| Terme | Définition telle que la source la donne | Précision manquante |
|---|---|---|
| **Fiche de référence** | Porte quatre valeurs par médicament : dose minimale efficace, dose maximale sûre par prise, dose cumulée maximale sur 24 h, âge plancher | Qui l'écrit et la maintient n'est pas défini ici |
| **Dose minimale efficace** | Seuil bas ; en dessous **strictement**, avertissement surchargeable | — (l'inclusivité est énoncée) |
| **Dose maximale sûre par prise** | Seuil haut ; au-dessus, blocage | L'inclusivité **n'est pas** énoncée |
| **Dose cumulée sur 24 h** | Somme de toutes les prises du même médicament pour un patient | Fenêtre glissante ou calendaire, non dit |
| **Âge plancher** | Âge patient minimal en années | Calculé à quelle date, non dit |
| **Insuffisance rénale** | Drapeau patient réduisant **tous les seuils maximaux** de 50 % | Où le drapeau est enregistré, non dit |
| **Pediatric specialist** | Rôle prescripteur convertissant le blocage d'âge en avertissement surchargeable | Modèle de rôle non défini ici |
| **Surcharge** | Contournement d'un avertissement, tracé avec identité, horodatage et justification ≥ 20 caractères | — |

## Les trois verdicts

`pass` · `warning` (surchargeable avec motif) · `blocked` (signature impossible).

**Asymétrie qui commande la priorisation** : un faux *blocage* est visible et corrigeable par le
prescripteur ; un faux *laissez-passer* est invisible et sa conséquence est le patient. Toute
règle dont l'échec produit un faux laissez-passer est traitée en P1, quelle que soit sa
probabilité.

## Dépendances hors périmètre

Fiche médicament, modèle de rôle, enregistrement du drapeau rénal, stockage de la piste d'audit.
**Aucun identifiant de story sœur n'est nommé dans la source** — ces quatre dépendances n'ont pas
de propriétaire identifié.
