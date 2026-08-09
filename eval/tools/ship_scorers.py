#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recopie les scoreurs de `eval/tools/` vers le plugin `qaia-score`.

A lancer apres tout changement volontaire d'un scoreur. `check_repo_structure.py` echoue tant
que ce n'est pas fait -- c'est le point de decision : lancer cette commande veut dire « j'ai
regarde ce qui change pour l'utilisateur du plugin, et je l'assume ».

Meme logique que `check_published_copies.py --update`, pour la meme raison : une copie sans
rien qui la surveille cesse silencieusement de correspondre a son original.
"""
from __future__ import print_function

import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCORERS = ("structural_score.py", "automation_score.py", "spec_suite_drift.py")


def main():
    src_dir = os.path.join(ROOT, "eval", "tools")
    dst_dir = os.path.join(ROOT, "plugins", "qaia-score", "scripts")
    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)
    for name in SCORERS:
        shutil.copyfile(os.path.join(src_dir, name), os.path.join(dst_dir, name))
        print("  recopie : plugins/qaia-score/scripts/%s" % name)
    print("Relancer `python eval/tools/check_repo_structure.py` pour confirmer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
