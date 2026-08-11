#!/usr/bin/env python3
"""Exerce `check_open_work_issue.py` sur des messages construits pour le faire rougir.

Un controle qu'on n'a jamais vu rouge ne prouve rien. Les cas ci-dessous incluent les DEUX
sens : ce qui doit echouer, et ce qui doit rester silencieux. Le second groupe est le plus
important -- c'est lui qui garantit que le controle ne devient pas un bruit de fond qu'on
apprend a ignorer.

Trois des cas rouges sont des corps de commit REELS de ce depot (`7053a21d`, `56973c5a`,
`6c86d4c3`), abreges : le controle est mesure sur ce qui s'est vraiment produit, pas seulement
sur ce qu'on imagine.

Run: python eval/tools/selfcheck_open_work_issue.py
Exit 0 tous les cas se comportent comme attendu, 1 sinon.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_open_work_issue import verdict

# (nom, message, code attendu)
CASES = [
    # --- doivent ROUGIR ---------------------------------------------------------------------
    ("reel-7053a21d",
     "Sept relecteurs retournent la journee\n\nRESTE OUVERT : la lecture par quelqu'un qui\n"
     "n'ecrit pas de Gherkin.\n", 1),
    ("reel-56973c5a",
     "D187 : le \"non teste\" mesure\n\nCe qui reste ouvert : signal-ingest n'a pas de fixture.\n",
     1),
    ("reel-6c86d4c3",
     "Relecture a froid par 4 personas\n\nLe cinquieme point n'est pas fait.\n", 1),
    ("anglais",
     "Ship the exporter\n\nThe CI wiring remains open.\n", 1),
    ("todo-nu",
     "Refonte du validateur\n\nTODO: brancher la porte par niveau.\n", 1),
    ("non-livre-accentue",
     "Sprint 40 partiel\n\nLa projection est non livrée pour le dialecte francais.\n", 1),
    ("jamais-instancie",
     "Modele GitHub Actions revu\n\nIl n'a jamais ete instancie sur la demo.\n", 1),

    # --- doivent rester SILENCIEUX ------------------------------------------------------------
    ("declare-avec-issue",
     "Sprint 40 partiel\n\nRESTE OUVERT : la lecture externe -- suivie dans #109.\n", 0),
    ("recit-ordinaire",
     "Deux etapes de CI pouvaient passer vertes sur un ensemble vide\n\n"
     "Je l'avais cru inoffensif parce que j'avais lu $? apres un pipe.\n", 0),
    ("pas-encore-narratif",
     "La passe mutation tourne enfin\n\nLe journal n'avait pas encore de forme stable ce\n"
     "matin-la ; il en a une maintenant.\n", 0),
    ("todo-dans-un-mot",
     "Ajout du module todolist et de ses fixtures\n", 0),
]


def main():
    bad = []
    for name, msg, expected in CASES:
        code, lines = verdict(msg)
        state = "OK " if code == expected else "RATE"
        if code != expected:
            bad.append((name, expected, code, lines[0]))
        print("%s %-22s attendu=%d obtenu=%d" % (state, name, expected, code))

    print("\n%d cas, %d ecart(s)." % (len(CASES), len(bad)))
    if bad:
        print("::error::le controle ne se comporte pas comme annonce.")
        for name, exp, got, first in bad:
            print("  %s : attendu %d, obtenu %d -- %s" % (name, exp, got, first))
        return 1
    print("OK: les sept cas rouges rougissent, les quatre cas neutres restent silencieux.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
