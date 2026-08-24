#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Note un corpus entier de cahiers Gherkin et rend la distribution des portes.

Mesure la metrique n1 du projet : le taux de PASS sur du materiau que QAIA n'a pas ecrit.
Aucun LLM, aucun reseau -- rejouable par un tiers a partir du corpus reconstitue par
`fetch_corpus.py`.

Usage: python3 score_corpus.py <dir> [--profile universal|qaia]
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structural_score  # noqa: E402


def walk_features(root):
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            if fn.endswith(".feature"):
                yield os.path.join(dirpath, fn)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        raise SystemExit(1)
    root = args[0]
    profile = "universal"
    if "--profile" in args:
        profile = args[args.index("--profile") + 1]

    rows, gates, findings = [], collections.Counter(), collections.Counter()
    for path in walk_features(root):
        try:
            r = structural_score.score_feature(path, profile=profile)
        except TypeError:
            # barème d'avant l'inversion : l'ancien parametre est `third_party`
            r = structural_score.score_feature(path, third_party=(profile == "universal"))
        r["path"] = os.path.relpath(path, root)
        rows.append(r)
        gates[r["gate"]] += 1
        for f in r.get("findings", []):
            findings[f.split(":")[0].split("(")[0].strip()[:60]] += 1

    scored = [r["score"] for r in rows if r.get("score") is not None]
    scored.sort()
    median = scored[len(scored) // 2] if scored else None
    out = {
        "corpus": os.path.abspath(root), "profile": profile,
        "files": len(rows), "scored": len(scored), "median": median,
        "gates": dict(gates),
        "pass_rate_pct": round(100 * gates["PASS"] / len(rows), 1) if rows else None,
        "findings_total": sum(findings.values()),
        "findings_by_kind": dict(findings.most_common()),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    with open(os.path.join(root, "_score-%s.json" % profile), "w", encoding="utf-8") as fh:
        json.dump({"summary": out, "rows": rows}, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
