#!/usr/bin/env python3
"""Prove validate_manifest.py enforces the `design.byLevel` rules of contract 1.1.

## Pourquoi ce fichier existe

`design.byLevel` (contrat 1.1, [ADR 0008](docs/adr/0008-test-level-is-a-design-property.md)) est
optionnel mais tout-ou-rien : cles fermees `e2e` / `api`, somme egale a `design.scenarios.total`.
Un `byLevel` partiel ou incoherent enoncerait une couverture par niveau que personne n'a etablie,
ce qui est pire que son absence.

Ces regles ont ete verifiees le jour de leur ecriture -- **dans une sonde de session, jamais
retenue**. Une campagne mutation du 2026-08-11 a du fabriquer cette sonde a la volee pour pouvoir
muter le validateur, et c'est ce qui a rendu le trou visible : la regle etait appliquee par le
code et prouvee par rien de durable. La regle 4bis du contrat partage dit exactement cela --
*une mesure citee pointe une sortie brute conservee*. Une verification qui ne vit que dans une
transcription de session n'est pas une verification.

Quatre cas, dont deux qui doivent PASSER : un controle qui refuserait tout serait inutilisable.

Run: python eval/tools/selfcheck_manifest_bylevel.py
Exit 0 conforme, 1 le validateur n'applique pas ce que le contrat annonce.
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate_manifest as V

BASE = {
    "scenarios": {"total": 22, "byPriority": {"P1": 9, "P2": 8, "P3": 5},
                  "negative": 9, "smoke": 1, "outlines": 3},
    "coverage": {"acTotal": 6, "acCovered": 6, "reqNegTotal": 7, "reqNegCovered": 7,
                 "negativeRatio": 0.41},
    "confidence": {"lowConfidence": 3, "openQuestions": 2, "assumptions": 4, "simulated": 1},
    "techniques": [], "oracles": [], "knowledgeApplied": [],
}


def errors_for(by_level):
    design = copy.deepcopy(BASE)
    if by_level is not None:
        design["byLevel"] = by_level
    errors = []
    V.validate_design(design, errors)
    return errors


CASES = [
    # (libelle, byLevel, doit_etre_refuse, fragment attendu dans l'erreur)
    ("manifeste 1.0, sans byLevel", None, False, None),
    ("somme egale a scenarios.total", {"e2e": 14, "api": 8}, False, None),
    ("somme differente de scenarios.total", {"e2e": 14, "api": 7}, True, "sum is"),
    ("byLevel partiel (une seule cle)", {"e2e": 22}, True, "byLevel.api"),
    ("cle hors de la liste fermee", {"e2e": 14, "api": 8, "integration": 0}, True, "closed key set"),
    ("valeur non entiere", {"e2e": 14, "api": "8"}, True, "byLevel.api"),
    ("valeur negative", {"e2e": 24, "api": -2}, True, "byLevel.api"),
]


def main():
    failures = []
    for label, by_level, must_fail, fragment in CASES:
        errors = errors_for(by_level)
        if must_fail and not errors:
            failures.append("%s : accepte alors que le contrat l'interdit" % label)
        elif not must_fail and errors:
            failures.append("%s : refuse alors que le contrat l'autorise -- %r" % (label, errors))
        elif must_fail and fragment and not any(fragment in e for e in errors):
            failures.append("%s : refuse, mais aucun message ne porte %r ; obtenu %r"
                            % (label, fragment, errors))

    if failures:
        print("::error::le validateur n'applique pas les regles de `design.byLevel`.")
        for line in failures:
            print("  " + line)
        return 1

    print("OK: byLevel absent accepte (1.0 reste valide), somme juste acceptee, et somme fausse, "
          "cle inconnue, bloc partiel, type et signe tous refuses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
