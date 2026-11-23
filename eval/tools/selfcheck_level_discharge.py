#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck de check_level_discharge.py : chaque defaut injecte doit etre vu (#107).

Les cas sont ecrits a l'execution dans un dossier temporaire, a partir de la paire de
reference restful-booker (22 conditions `[req-neg]`, toutes `[level: api]`).
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_level_discharge as C  # noqa: E402

ROOT = C.ROOT
DESIGN = os.path.join(ROOT, "eval/reverse-engineering-2026-08-11/20-restfulbooker-03-design.md")
FEATURE = os.path.join(ROOT, "eval/reverse-engineering-2026-08-11/21-restfulbooker.feature")

failures = []


def expect(label, got, want):
    if got != want:
        failures.append("%s\n    got:  %r\n    want: %r" % (label, got, want))


design = open(DESIGN, encoding="utf-8").read()
feature = open(FEATURE, encoding="utf-8").read()
tmp = tempfile.mkdtemp()


def run(design_text, feature_text):
    d, f = os.path.join(tmp, "d.md"), os.path.join(tmp, "f.feature")
    open(d, "w", encoding="utf-8").write(design_text)
    open(f, "w", encoding="utf-8").write(feature_text)
    return C.check(d, [f])[1]


try:
    base = run(design, feature)
    expect("la paire de reference est entierement acquittee", (len(base["discharged"]),
           base["violation"], base["unlinked"]), (22, [], []))

    # 1. Le cas que la regle existe pour interdire : un refus de contrat (`[level: api]`) couvert
    #    par un scenario d'interface. Le premier scenario `@api @negative` devient `@e2e @negative`.
    i = feature.index("@api @negative") if "@api @negative" in feature else None
    if i is None:
        failures.append("la paire de reference n'a plus de scenario `@api @negative` a muter")
    else:
        mutated = feature[:i] + "@e2e @negative" + feature[i + len("@api @negative"):]
        r = run(design, mutated)
        expect("un refus api couvert par un scenario e2e est une VIOLATION",
               len(r["violation"]) > 0, True)

    # 2. Le tag `@negative` retire : le scenario lie existe, au bon niveau, mais n'exerce pas de refus.
    r = run(design, feature.replace("@negative", "@pending", 1))
    expect("un scenario lie sans @negative ne l'acquitte pas", len(r["violation"]) > 0, True)

    # 3. Le lien retire : aucun commentaire `# condition:` ne cite plus la condition.
    first = next(ln for ln in feature.splitlines() if C.COND_COMMENT.match(ln)
                 and "RB01-AC2-C1" in ln)
    r = run(design, feature.replace(first, "    # (lien retire)"))
    expect("une condition que plus rien ne cite est NON LIEE", "RB01-AC2-C1" in r["unlinked"], True)

    # 4. La negation : « Pas `[req-neg]` » ecarte le marqueur, ne le pose pas.
    conds = C.parse_design("| X-C1 | foo | ep | `[level: api]` | **Pas `[req-neg]`** : un etat, pas un refus |\n")
    expect("« Pas [req-neg] » n'est pas une marque", conds["X-C1"]["reqneg"], False)
    conds = C.parse_design("| X-C1 | foo | ep | `[level: api]` | **`[req-neg]`** |\n")
    expect("« [req-neg] » est une marque", conds["X-C1"]["reqneg"], True)

    # 5. Une colonne `[req-neg]` qui porte autre chose (`[open] Q9`) n'est pas une affirmation.
    table = ("| # | Condition | `[req-neg]` |\n|---|---|---|\n"
             "| X-C1 | a | `[open] Q9` |\n| X-C2 | b | **oui** |\n")
    conds = C.parse_design(table)
    expect("une cellule non vide de la colonne n'est pas une marque",
           (conds["X-C1"]["reqneg"], conds["X-C2"]["reqneg"]), (False, True))

    # 6. Le niveau global : « Toutes les conditions sont `[level: api]` ».
    conds = C.parse_design("Toutes les conditions sont `[level: api]`.\n\n| X-C1 | a | `[req-neg]` |\n")
    expect("un niveau declare globalement s'applique", conds["X-C1"]["level"], "api")

    # 7. Un commentaire de condition APRES la ligne Scenario et avant les etapes appartient a ce
    #    scenario ; place apres des etapes, il appartient au suivant.
    sc = C.parse_feature("  @a\n  Scenario: un\n    # condition: X-C1\n    Given x\n"
                         "  # condition: X-C2\n  @b\n  Scenario: deux\n    Given y\n")
    expect("le rattachement des commentaires de condition", [sorted(s[2]) for s in sc],
           [["X-C1"], ["X-C2"]])

    # 8. Rien lu ne rend pas vert.
    d0 = os.path.join(tmp, "vide.md")
    open(d0, "w", encoding="utf-8").write("# rien\n")
    expect("une conception sans [req-neg] fait echouer le controle",
           C.main([d0, os.path.join(tmp, "f.feature")]), 1)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

if failures:
    print("selfcheck_level_discharge: %d FAILURE(S)\n" % len(failures))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("selfcheck_level_discharge: ok")
