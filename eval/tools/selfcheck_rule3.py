# -*- coding: utf-8 -*-
"""Garde-fou de la regle 3 : « aucun producteur ne note sa propre sortie ».

C'est l'argument que le README met en tete pour se distinguer, et il n'avait AUCUNE application
mecanique : `validate_manifest.py` verifiait que `gate.scoredBy` est une chaine, sans jamais la
comparer a `producers[]`. Un manifeste declarant que `testbook-generate` a produit le cahier ET
qu'il l'a note passait sans un mot. Releve par la revue « chef de projet » du 2026-08-09.

Le controle doit tenir dans les DEUX sens : refuser le generateur qui se note, et laisser
passer le controleur qui note ce qu'il n'a pas ecrit -- un premier jet trop grossier signalait
`testbook-validate`, ce qui est exactement le comportement que la regle demande.

Meme lecon que `check_skill_counts.py` et `check_decision_register.py`, nes du meme constat :
une regle qui n'est portee que par l'intention finit par ceder.
"""
import sys
sys.path.insert(0, "eval/tools")
import validate_manifest as V

PRODUCERS = [
    {"plugin": "qaia-core", "skill": "testbook-generate", "version": "x", "at": "2026-01-01T00:00:00Z"},
    {"plugin": "qaia-core", "skill": "testbook-validate", "version": "x", "at": "2026-01-01T00:00:00Z"},
]

CASES = [
    ("qaia-core:testbook-generate", True,  "le generateur note son propre cahier"),
    ("qaia-core:testbook-validate", False, "le controleur note un cahier qu'il n'a pas ecrit"),
    ("qaia-score:testbook-score",   False, "un scoreur exterieur"),
    ("qaia-core:istqb-design",      False, "une skill absente de producers[]"),
]

bad = 0
for scored_by, must_fail, label in CASES:
    errors = []
    V.check_scorer_is_not_a_producer(scored_by, PRODUCERS, "gate", errors)
    failed = bool(errors)
    ok = failed == must_fail
    bad += not ok
    print("  %-46s %-9s %s" % (label, "REFUSE" if failed else "accepte",
                               "ok" if ok else "<<< FAUX"))

print()
print("selfcheck_rule3: %s" % ("ok" if not bad
                          else "%d FAILURE(S)" % bad))
sys.exit(1 if bad else 0)
