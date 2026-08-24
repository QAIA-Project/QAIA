#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Echoue quand une skill documente une option que l'outil livre n'accepte pas (ou plus).

## Le trou que ce controle ferme

Le 2026-08-24, l'inversion du barème a rendu `--third-party` deprecie et sans effet. **Quatre
skills livrees ont continue d'ordonner de le passer**, dont une qui expliquait longuement
pourquoi il fallait « decider le mode avant de lancer ». Un mode qui n'existe plus.

Pire, `testbook-validate/references/structural-pass.md` disait encore « materialize a throwaway
script implementing the algorithm below » et « the script is never shipped » -- deux affirmations
devenues fausses le 2026-08-09 (ADR 0002). Un lecteur qui suivait cette page obtenait **un
scoreur reinvente par le modele a chaque execution**, c'est-a-dire exactement la
non-reproductibilite que la decision de livrer le code avait ete prise pour supprimer. Quinze
jours sans que rien ne le voie.

Le mecanisme est nommable : **le depot garde ses outils, garde ses copies, garde ses comptes --
et ne garde rien entre la couche prompt et le noyau qu'elle pilote.** Les skills sont du texte,
les outils du code, et personne ne relisait l'un en changeant l'autre.

## Ce qui est verifie

Pour chaque option longue (`--xxx`) citee dans une skill a cote de l'un des scoreurs livres :

  - l'outil l'accepte-t-il encore ?
  - et n'est-elle pas explicitement DEPRECIEE ? Une skill qui ordonne de passer un drapeau sans
    effet est aussi fausse qu'une skill qui en invente un -- elle promet un comportement que
    l'utilisateur n'obtiendra pas.

Une skill a le droit de MENTIONNER une option depreciee pour dire de ne pas s'en servir : le
controle ne se declenche que sur une citation qui la PRESCRIT (impératif, « add », « pass »,
« use », ou une ligne de commande contenant l'option).

## Ce qu'il NE voit PAS -- dit ici plutot que laisse deviner

Une option n'est rattachee a un outil que si la ligne le NOMME, ou si une seule fenetre de
quatre lignes au-dessus le nomme. **Une prescription eloignee du nom de l'outil echappe donc au
controle** -- verifie : `add \\`--third-party\\` avant de lancer`, seul dans un paragraphe, n'est
pas signale. C'est un choix : deviner de quel outil parle une phrase qui n'en nomme aucun
produirait des constats faux, et la premiere version de ce fichier en a produit six d'un coup en
attribuant les options de trois outils listes a la suite a chacun d'eux.

Ce controle attrape donc le cas courant -- une ligne de commande, ou une instruction citant
l'outil -- et pas le cas rare. Un controle qui couvre 80 % d'un trou en le disant vaut mieux
qu'un controle qui pretend le couvrir entierement.

Exit 0 si tout est coherent, 1 sinon.
"""
import argparse
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(ROOT, "eval", "tools")

# Les scoreurs livres, et le nom sous lequel une skill peut les citer.
SCORERS = ("structural_score.py", "automation_score.py", "spec_suite_drift.py")

OPTION_RE = re.compile(r"(--[a-z][a-z0-9-]{2,})")
# Une citation PRESCRIT l'option si elle apparait dans une ligne de commande, ou apres un verbe
# d'instruction. Sinon elle en parle -- ce qui est legitime, et meme souhaitable pour dire
# « ne l'utilisez plus ».
PRESCRIBES_RE = re.compile(r"(?:^\s*\$?\s*python\b|\badd\b|\bpass\b|\buse\b|\bajoute[rz]?\b|"
                           r"\bpasse[rz]?\b|\butilise[rz]?\b)", re.I)
DEPRECATION_RE = re.compile(r"deprecie|déprécié|deprecated|sans effet|no longer|does nothing|"
                            r"ne fait rien|until \d{4}-\d{2}-\d{2}", re.I)
# Une ligne qui INTERDIT l'option la mentionne sans la prescrire.
NEGATION_RE = re.compile(r"\bdo not\b|\bdon't\b|\bnever\b|\bne pas\b|\bne plus\b|\bjamais\b|"
                         r"\bau lieu de\b|\binstead of\b", re.I)


def tool_options(script):
    """Options que l'outil accepte reellement, et celles qu'il annonce depreciees.

    On lit le SOURCE plutot que `--help` : deux des trois scoreurs n'utilisent pas argparse, et
    lancer chaque outil avec un drapeau au hasard pour voir s'il proteste serait un test qui
    modifie ce qu'il mesure.
    """
    path = os.path.join(TOOLS, script)
    if not os.path.isfile(path):
        return None, None
    src = io.open(path, encoding="utf-8").read()
    accepted, deprecated = set(), set()
    for m in OPTION_RE.finditer(src):
        opt = m.group(1)
        line_start = src.rfind("\n", 0, m.start()) + 1
        line_end = src.find("\n", m.end())
        line = src[line_start:line_end if line_end > 0 else len(src)]
        # Une option n'est « acceptee » que si elle apparait dans du CODE : un `add_argument`,
        # une comparaison a `args`, ou un test d'appartenance. Sa seule presence dans la
        # docstring d'usage ne prouve rien -- c'est exactement le genre de promesse que ce
        # controle existe pour ne plus croire.
        if ("add_argument" in line or "in args" in line or "args.index" in line
                or "== " + repr(opt) in line or 'args[0] in (' in line):
            accepted.add(opt)
        if DEPRECATION_RE.search(line):
            deprecated.add(opt)
    # `argparse` en `dest` : `--profile` devient `args.profile`.
    for m in re.finditer(r'add_argument\(\s*"(--[a-z][a-z0-9-]+)"', src):
        accepted.add(m.group(1))
    return accepted, deprecated


def iter_skill_files():
    base = os.path.join(ROOT, "plugins")
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d != "node_modules"]
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    tools = {}
    for s in SCORERS:
        acc, dep = tool_options(s)
        if acc is None:
            print("::error::scoreur introuvable : %s" % s)
            return 2
        tools[s] = (acc, dep)

    failures, checked = [], 0
    for path in iter_skill_files():
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        text = io.open(path, encoding="utf-8", errors="replace").read()
        lines = text.split("\n")
        for i, line in enumerate(lines, start=1):
            # A QUEL outil cette ligne parle-t-elle ? Si elle en nomme un, c'est celui-la et
            # aucun autre. La premiere version prenait une fenetre de quatre lignes sans regarder
            # la ligne elle-meme : un README listant les trois outils a la suite faisait
            # attribuer les options de chacun a tous, et sortait six constats faux. Le meme
            # defaut de perimetre que ce depot repete -- dans le controle ecrit pour le chasser.
            named = [s for s in tools if s[:-3] in line or s in line]
            if named:
                candidates = named
            else:
                window = "\n".join(lines[max(0, i - 4):i])
                candidates = [s for s in tools if s[:-3] in window or s in window]
                if len(candidates) != 1:
                    # Zero outil nomme : rien a verifier. Plusieurs : on ne devine pas lequel.
                    continue
            for script in candidates:
                accepted, deprecated = tools[script]
                for opt in OPTION_RE.findall(line):
                    if opt in ("--batch",):     # options generiques, sans dest argparse
                        continue
                    checked += 1
                    if not PRESCRIBES_RE.search(line):
                        continue               # la skill en PARLE, elle ne la prescrit pas
                    # Le contexte, pas la ligne. En prose, la prescription et son dementi
                    # tombent presque toujours dans deux lignes differentes : « until
                    # 2026-08-24 this skill told you to add `--x` » se coupe entre les deux, et
                    # la garde signalait alors la phrase qui dit exactement ce qu'il faut dire.
                    context = " ".join(lines[max(0, i - 3):i + 2])
                    if DEPRECATION_RE.search(context) or NEGATION_RE.search(context):
                        # « ce drapeau est deprecie », « ne passez plus --x » : la skill dit
                        # exactement ce qu'il faut. La signaler apprendrait a l'auteur qu'il vaut
                        # mieux se taire sur une option morte que d'en avertir le lecteur.
                        continue
                    if opt in deprecated:
                        failures.append(
                            "%s:%d prescrit `%s`, que %s annonce DEPRECIE. Une skill qui ordonne "
                            "de passer un drapeau sans effet promet un comportement que "
                            "l'utilisateur n'obtiendra pas." % (rel, i, opt, script))
                    elif opt not in accepted:
                        failures.append(
                            "%s:%d prescrit `%s`, que %s n'accepte pas."
                            % (rel, i, opt, script))

    print("check_skill_cli_claims :")
    print("  %d citation(s) d'option examinee(s) dans les skills livrees" % checked)
    if failures:
        print("")
        for f in failures:
            print("::error::%s" % f)
        print("\n%d incoherence(s) entre la couche prompt et le noyau" % len(failures))
        return 1
    print("  -> aucune skill ne prescrit une option que l'outil refuse ou a depreciee")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
