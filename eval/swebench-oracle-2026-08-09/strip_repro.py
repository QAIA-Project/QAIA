#!/usr/bin/env python3
"""Retire les extraits de reproduction d'un enonce SWE-bench, et mesure ce qu'il en reste.

## Pourquoi cette etape existe avant toute mesure

`problem_statement` contient tres souvent le code qui reproduit le defaut. Le donner tel quel a
une chaine « exigence -> conditions de test », c'est lui faire lire un **quasi-test** et non une
exigence : le score obtenu serait vrai et sans valeur.

Otter (arXiv 2502.05368) fait la meme chose et le dit : il retire les extraits pour placer le
systeme dans le cas realiste ou le test doit naitre de la **description seule**. On adopte donc
un protocole publie plutot qu'une metrique maison -- une metrique inventee par l'auteur de
l'outil qu'elle note est le mode d'echec que ce depot combat.

## Ce que ce script mesure, et pourquoi c'est un resultat en soi

La part de code dans chaque enonce. Si, une fois le code retire, il ne reste qu'une phrase, alors
**ce corpus n'est pas un bon oracle pour un outil qui part de l'exigence** -- et le constater coute
une minute, alors que la campagne complete coute des jours. C'est la mesure qui decide s'il faut
lancer les autres.

Run: python eval/swebench-oracle-2026-08-09/strip_repro.py [--json out.json]
"""
import argparse
import io
import json
import os
import re
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACT = os.path.join(HERE, "swebench-lite-extract.json")

FENCE = re.compile(r"```.*?```", re.S)
INDENTED = re.compile(r"(?:^(?: {4}|\t).*(?:\n|$))+", re.M)
TRACEBACK = re.compile(r"^Traceback \(most recent call last\):.*?(?=^\S|\Z)", re.S | re.M)
# Une ligne qui EST du code sans etre indentee ni clôturee : appel, import, affectation.
BARE_CODE = re.compile(
    r"^\s*(?:from\s+\S+\s+import\s|import\s+\S|>>>|\$\s|\w+\s*=\s*\w+\(|\w+\.\w+\(.*\)\s*$)",
    re.M)


def strip(text):
    """Retourne (texte_sans_code, caracteres_retires)."""
    before = len(text)
    t = FENCE.sub(" ", text)
    t = TRACEBACK.sub(" ", t)
    t = INDENTED.sub(" ", t)
    t = NL.join("" if BARE_CODE.match(l) else l for l in t.split(NL))
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t).strip()
    return t, before - len(t)


def words(t):
    return len(re.findall(r"[A-Za-z][A-Za-z'-]+", t))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split(NL)[0])
    ap.add_argument("--json", help="ecrit le detail ici")
    args = ap.parse_args()

    if not os.path.isfile(EXTRACT):
        print("BROKEN: %s introuvable" % EXTRACT, file=sys.stderr)
        return 2
    data = json.load(io.open(EXTRACT, encoding="utf-8"))
    rows = []
    for inst in data["instances"]:
        raw = inst["problem_statement"]
        clean, removed = strip(raw)
        rows.append({
            "instance_id": inst["instance_id"],
            "repo": inst["repo"],
            "chars_raw": len(raw),
            "chars_clean": len(clean),
            "pct_code": round(100.0 * removed / max(1, len(raw)), 1),
            "words_clean": words(clean),
            "oracle_tests": len(inst["fail_to_pass"]),
            "clean": clean,
        })

    rows.sort(key=lambda r: -r["pct_code"])
    print("%-34s %6s %7s %7s %s" % ("instance", "%code", "mots", "oracles", "depot"))
    for r in rows:
        print("%-34s %5.1f%% %7d %7d %s"
              % (r["instance_id"][:32], r["pct_code"], r["words_clean"],
                 r["oracle_tests"], r["repo"]))

    n = len(rows)
    usable = [r for r in rows if r["words_clean"] >= 40]
    thin = [r for r in rows if r["words_clean"] < 40]
    med = sorted(r["pct_code"] for r in rows)[n // 2]
    print()
    print("  enonces                       : %d" % n)
    print("  part de code, mediane         : %.1f%%" % med)
    print("  exploitables (>= 40 mots)     : %d  (%.0f%%)" % (len(usable), 100.0 * len(usable) / n))
    print("  trop maigres apres nettoyage  : %d" % len(thin))
    for r in thin:
        print("      %-34s %d mots" % (r["instance_id"][:32], r["words_clean"]))

    if args.json:
        io.open(args.json, "w", encoding="utf-8", newline=NL).write(
            json.dumps({"_protocol": "extraits de reproduction retires, comme Otter "
                                     "(arXiv 2502.05368)",
                        "_source_extract_sha_prefix": data["_sha256_of_extract"][:24],
                        "rows": rows}, indent=1, ensure_ascii=False) + NL)
        print("\nwritten: %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
