#!/usr/bin/env python3
"""Fail when the JSON Schema of the output contract diverges from the Python validator.

## Pourquoi ce fichier existe

Le contrat de sortie est specifie **deux fois** : en prose dans `docs/OUTPUT-CONTRACT.md`, en
JSON Schema dans `docs/schemas/output-contract-v1.schema.json`, et il est **applique** par
`eval/tools/validate_manifest.py` -- le seul des trois que la CI execute.

Une revue d'architecture du 2026-08-08 a trouve les trois divergences que cela avait produites :

- l'enum `artifacts[].kind` du schema listait **6 valeurs**, le validateur en imposait **10** ;
- le bloc `structural` -- la passe deterministe sur 100, decrite par la revue comme la porte la
  plus contraignante du produit -- **n'existait pas du tout** dans le schema ;
- le schema exigeait les 8 champs du bloc `gate`, alors que le validateur autorise explicitement
  un **gate partiel** (`score` sans `verdict`).

Aucun job ne comparait les deux. Et en les realignant, l'auteur a **casse un troisieme enum** :
un parcours qui remplacait toute cle nommee `kind` a ecrase `openArbitrations[].kind` avec les
valeurs de `artifacts[].kind`. Detecte parce que la sortie affichait « 3 -> 10 valeurs ».

C'est la demonstration exacte du probleme : **deux sources pour une meme regle divergent, y compris
pendant qu'on les recolle.**

## Ce qui est verifie

Les quatre enumerations, comparees aux constantes du validateur -- qui fait autorite, puisque c'est
lui que la CI execute. Le schema est une **copie formelle** destinee aux consommateurs externes,
jamais une seconde verite.

Ce qui n'est PAS verifie : la prose de `OUTPUT-CONTRACT.md`. Un job de CI garantit deja que ses
cinq copies sont identiques entre elles ; comparer de la prose a du code demanderait un jugement,
pas une egalite.

Run: python eval/tools/check_schema_matches_validator.py
Exit 0 concordance, 1 divergence, 2 fichier illisible.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCHEMA = os.path.join("docs", "schemas", "output-contract-v1.schema.json")


def main():
    try:
        import validate_manifest as V
    except ImportError as e:
        print("BROKEN: validate_manifest.py introuvable (%s)" % e)
        return 2
    if not os.path.isfile(SCHEMA):
        print("BROKEN: %s introuvable -- lancer depuis la racine du depot." % SCHEMA)
        return 2
    try:
        d = json.load(io.open(SCHEMA, encoding="utf-8"))
    except ValueError as e:
        print("BROKEN: %s n'est pas du JSON valide (%s)" % (SCHEMA, e))
        return 2

    p = d.get("properties", {})

    def dig(*path):
        node = p
        for k in path:
            if not isinstance(node, dict) or k not in node:
                return None
            node = node[k]
        return node.get("enum") if isinstance(node, dict) else None

    pairs = [
        ("artifacts[].kind", dig("artifacts", "items", "properties", "kind"), V.ARTIFACT_KIND_ENUM),
        ("openArbitrations[].kind", dig("openArbitrations", "items", "properties", "kind"), V.ARBITRATION_KIND_ENUM),
        ("gate.verdict", dig("gate", "properties", "verdict"), V.GATE_VERDICT_ENUM),
        ("structural.gate", dig("structural", "properties", "gate"), V.STRUCTURAL_GATE_ENUM),
    ]

    bad = []
    for name, in_schema, in_validator in pairs:
        if in_schema is None:
            bad.append((name, "ABSENT du schema", sorted(in_validator)))
        elif set(in_schema) != set(in_validator):
            bad.append((name, sorted(in_schema), sorted(in_validator)))

    # le bloc structural entier, pas seulement son enum
    st = p.get("structural")
    if not isinstance(st, dict):
        bad.append(("structural (bloc)", "ABSENT du schema", sorted(V.STRUCTURAL_REQUIRED)))
    elif sorted(st.get("required", [])) != sorted(V.STRUCTURAL_REQUIRED):
        bad.append(("structural.required", sorted(st.get("required", [])), sorted(V.STRUCTURAL_REQUIRED)))

    if bad:
        print("SCHEMA DIVERGENT du validateur -- validate_manifest.py fait autorite.\n")
        for name, a, b in bad:
            print("  %s" % name)
            print("      schema     : %s" % a)
            print("      validateur : %s" % b)
        print("\nAligner le schema sur le validateur, jamais l'inverse : c'est le validateur que la CI execute.")
        return 1

    print("OK: %d enumeration(s) et le bloc structural concordent avec validate_manifest.py." % len(pairs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
