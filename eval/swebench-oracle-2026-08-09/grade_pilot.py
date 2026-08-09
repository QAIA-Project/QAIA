#!/usr/bin/env python3
"""Confronte des conditions derivees a ce que le test-oracle assure REELLEMENT.

La notation est mecanique : on extrait de `test_patch` les identifiants et les valeurs sur
lesquels le test ajoute assure, puis on cherche ces jetons dans les conditions. Aucun humain
n'arbitre -- ce qui est le seul moyen d'obtenir un chiffre quand le producteur des conditions
est aussi celui qui les confronte.

Ce que cette mesure PEUT dire : « la condition derivee nomme-t-elle la chose que le test-oracle
verifie ? » Ce qu'elle NE PEUT PAS dire : si un test genere echouerait avant le correctif et
passerait apres (la metrique fail-to-pass d'Otter), qui demande d'executer deux versions du
depot -- Docker, images par instance, environnements. Hors de portee ici, et dit plutot que
contourne par un chiffre approchant.

Run: python eval/swebench-oracle-2026-08-09/grade_pilot.py
"""
import io
import json
import os
import re
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))

# Jetons trop generiques pour signifier quoi que ce soit s'ils correspondent.
STOP = set("""self test tests def assert assertEqual assertTrue assertIn true false none null
import from return with for the and not that this value values result results object data
get set add new old str int bool list dict none type name class case check call""".split())


def tokens(text):
    """Identifiants, valeurs entre guillemets et nombres cites par le test ajoute."""
    added = NL.join(l[1:] for l in text.split(NL) if l.startswith("+") and not l.startswith("+++"))
    out = set()
    for m in re.finditer(r"[A-Za-z_][A-Za-z_0-9]{2,}", added):
        t = m.group(0)
        if t.lower() not in STOP:
            out.add(t)
    for m in re.finditer(r"""['"]([^'"]{2,40})['"]""", added):
        out.add(m.group(1))
    return out


def normalise(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower())


def main():
    corpus = {i["instance_id"]: i for i in
              json.load(io.open(os.path.join(HERE, "swebench-lite-extract.json"),
                                encoding="utf-8"))["instances"]}
    pilot = json.load(io.open(os.path.join(HERE, "pilot-conditions.json"), encoding="utf-8"))

    total_hit = total_key = 0
    report = []
    for entry in pilot["instances"]:
        iid = entry["instance_id"]
        inst = corpus[iid]
        toks = tokens(inst["test_patch"])
        blob = normalise(" ".join(entry["conditions"] + [entry["reformulated_need"]]
                                  + entry.get("open_questions", [])))

        # Jetons DISCRIMINANTS. Premiere version : tout identifiant un peu long du test ajoute.
        # Elle donnait 5/65 en reprochant a QAIA de ne pas avoir devine `setattr`,
        # `call_command`, `getvalue`, `fnmatch_lines`, `tmpdir_factory` -- c'est-a-dire **comment
        # le test est plombe**, ce que la chaine refuse de deriver par construction puisqu'elle
        # ne lit jamais le code. Le denominateur mesurait la mauvaise chose, et un chiffre faux
        # est pire qu'aucun chiffre.
        #
        # Un jeton ne compte donc que s'il appartient au vocabulaire du DOMAINE : present dans
        # l'enonce nettoye, ou dans le NOM du test-oracle. Les deux sont accessibles a quelqu'un
        # qui n'a pas lu le code source, ce qui est exactement la position de la chaine.
        vocab = normalise(inst["problem_statement"] + " " + " ".join(inst["fail_to_pass"]))
        key = sorted(t for t in toks
                     if len(t) > 4 and not t.startswith("test_")
                     and normalise(t).strip() in vocab)
        hit = [t for t in key if normalise(t).strip() and
               all(w in blob for w in normalise(t).split())]

        total_hit += len(hit)
        total_key += len(key)
        report.append({
            "instance_id": iid,
            "oracle_tests": inst["fail_to_pass"],
            "conditions_derived": len(entry["conditions"]),
            "key_tokens": len(key),
            "matched": sorted(hit),
            "missed_sample": [t for t in key if t not in hit][:12],
        })

    print("%-32s %6s %8s %8s" % ("instance", "cond.", "jetons", "couverts"))
    for r in report:
        print("%-32s %6d %8d %8d" % (r["instance_id"][:30], r["conditions_derived"],
                                     r["key_tokens"], len(r["matched"])))
        if r["matched"]:
            print("     couverts : %s" % ", ".join(r["matched"][:8]))
        print("     manques  : %s" % ", ".join(r["missed_sample"][:8]))
    print()
    print("  jetons discriminants couverts : %d / %d" % (total_hit, total_key))
    print()
    print("  VERDICT DU PILOTE : un correspondance LEXICALE ne peut pas faire ce travail.")
    print("  Trois denominateurs essayes, trois fois autre chose de mesure :")
    print("    - tous les identifiants du test  -> 5/65, en reprochant la plomberie du test")
    print("    - vocabulaire du domaine         -> 5/23, deja plus juste")
    print("    - et il reste `scope` compte manquant alors que la condition dit « portee » :")
    print("      la mesure penalise une TRADUCTION, pas une lacune.")
    print()
    print("  Ce que la campagne demande donc, et que ce pilote a servi a etablir :")
    print("    1. produire les conditions dans la LANGUE de l'exigence, sinon tout")
    print("       correlateur lexical est fausse d'avance ;")
    print("    2. faire noter par un juge AVEUGLE et distinct du producteur (regle 3),")
    print("       ou executer fail-to-pass a la maniere d'Otter -- deux versions du depot.")
    print()
    print("  Aucun chiffre de cette sortie n'est un score de QAIA. Le pilote a mesure")
    print("  l'instrument, pas l'outil -- et l'instrument ne convient pas.")

    io.open(os.path.join(HERE, "pilot-grades.json"), "w", encoding="utf-8", newline=NL).write(
        json.dumps({"_limitation": pilot["_limitation_the_reader_must_weigh"],
                    "results": report}, indent=1, ensure_ascii=False) + NL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
