#!/usr/bin/env python3
"""Echoue quand un commit DECLARE du travail ouvert sans citer d'issue.

## Pourquoi ce fichier existe

Le 2026-08-11, le fondateur formule une impression : *« j'ai l'impression que depuis le debut du
projet on a loupe des issues »*. Mesuree plutot que crue :

- **82 affirmations de travail ouvert dans `docs/`, 33 seulement citent une issue** (40 %) ;
- sur les **300 derniers commits, 24 portent une declaration de travail ouvert dans leur corps --
  12 sans la moindre reference `#N`**, dont sept sections litteralement titrees « RESTE OUVERT ».

L'impression etait juste, et le mecanisme est identifiable : le corps de commit est l'endroit ou
ce depot ecrit ce qu'il n'a pas fait -- honnetement, longuement, et **sans destinataire**. Un
paragraphe « reste ouvert » dans un message de commit n'est lu par personne apres le jour ou il
est ecrit. Le registre d'issues, lui, est ce qui se relit.

C'est exactement la classe de `check_decision_register.py` : *« les messages de commit ne sont pas
la memoire du projet »*. Celui-la portait sur les decisions ; celui-ci porte sur les dettes.

## La regle

**Un commit qui declare du travail ouvert doit citer une issue dans le meme message.**

Une seule reference `#N` suffit, n'importe ou dans le message. Le controle ne verifie pas que
l'issue est la bonne -- il ne peut pas -- il verifie qu'il y en a une. La question qu'il pose au
redacteur est la bonne : *« ou est-ce que ce reste-a-faire sera relu ? »*

## Ce qui n'est PAS verifie, et pourquoi c'est dit

- **Que l'issue citee corresponde au travail decrit.** Un `#106` colle au hasard passe. Le
  controle supprime l'oubli, pas la mauvaise foi -- et il n'a jamais pretendu autre chose.
- **Le travail ouvert qui n'est pas ECRIT.** Ce qu'on ne dit pas reste invisible ; aucun controle
  automatique ne peut couvrir ce trou-la. C'est la limite reelle et elle est structurelle.

## Le taux de declenchement, mesure avant d'ecrire l'outil

Un controle qui crie trop apprend a tout le monde a l'ignorer -- le contraire du but. Le jeu de
marqueurs ci-dessous a ete confronte a l'historique AVANT d'etre retenu, puis re-mesure apres
elargissement : **24 commits sur 300 (8 %) le declenchent, 12 (4 %) auraient echoue**. Un commit
sur vingt-cinq, sur des cas qui sont tous de vrais restes-a-faire jamais suivis.

« pas encore » seul a ete essaye et ECARTE a cette etape : il apparait constamment dans la prose
narrative de ce depot et aurait double le taux sans ajouter un seul vrai cas. Si le taux monte,
c'est le jeu de marqueurs qu'il faut resserrer, pas le controle qu'il faut retirer.

Run: python eval/tools/check_open_work_issue.py [--message-file FICHIER]
Exit 0 rien a signaler, 1 travail ouvert declare sans issue, 2 aucun message lisible.
"""
import io
import os
import re
import subprocess
import sys

# Marqueurs retenus apres confrontation a 300 commits. Volontairement etroits : ce sont des
# formules d'ANNONCE (« reste ouvert », « non livre »), pas des tournures de recit. « pas encore »
# seul a ete ECARTE -- il apparait constamment dans la prose narrative des messages de ce depot
# et aurait fait du controle un bruit de fond.
MARKERS = re.compile(
    r"(reste[nt]?\s+(?:ouvert|a\s+faire|à\s+faire)"
    r"|non\s+livr(?:e|é)"
    r"|(?:non|(?:n'est|ne\s+sont)\s+pas)\s+(?:fait|livr(?:e|é)|couvert)"
    r"|jamais\s+(?:(?:ete|été)\s+)?(?:fait|lanc(?:e|é)|instanci(?:e|é)|couvert)"
    r"|remains?\s+open"
    r"|not\s+done"
    r"|\bTODO\b)",
    re.I)

ISSUE = re.compile(r"#\d+")


def messages():
    """HEAD, ou toute la branche face a sa base sur une PR -- meme logique que le registre.

    Ne lire que HEAD laisserait passer une PR de dix commits declarant son reste-a-faire au
    troisieme, et c'est la forme qu'ont les PR.
    """
    base = os.environ.get("GITHUB_BASE_REF")
    cmds = [["git", "log", "-1", "--format=%B"]]
    if base:
        cmds.insert(0, ["git", "log", "origin/%s..HEAD" % base, "--format=%B"])
    last_err = None
    for cmd in cmds:
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, OSError) as exc:
            last_err = str(exc)
            continue
        text = out.decode("utf-8", "replace")
        if text.strip():
            return text, None
    return None, last_err or "aucun message de commit lisible"


def verdict(msg):
    """Rend (code, lignes) -- separe de la lecture git pour que la selfcheck puisse l'exercer."""
    found = [m.group(0) for m in MARKERS.finditer(msg)]
    if not found:
        return 0, ["OK: aucune declaration de travail ouvert dans les commits controles."]
    if ISSUE.search(msg):
        return 0, ["OK: travail ouvert declare (%s) et une issue est citee (%s)."
                   % (", ".join(sorted(set(found))[:3]),
                      ", ".join(sorted(set(ISSUE.findall(msg)))[:3]))]
    return 1, [
        "TRAVAIL OUVERT SANS ISSUE : le message declare %s, et ne cite aucune issue."
        % ", ".join("%r" % f for f in sorted(set(found))),
        "",
        "  Un commit qui declare du travail ouvert doit citer une issue dans le meme message.",
        "  Un paragraphe « reste ouvert » dans un corps de commit n'est relu par personne apres",
        "  le jour ou il est ecrit. Le registre d'issues est ce qui se relit.",
        "",
        "  Ouvrir l'issue (gabarits dans .github/ISSUE_TEMPLATE/), puis citer son numero ici.",
        "  Si ce reste-a-faire ne merite pas une issue, il ne merite pas ce paragraphe non plus.",
    ]


def main(argv):
    if "--message-file" in argv:
        path = argv[argv.index("--message-file") + 1]
        msg = io.open(path, encoding="utf-8", errors="replace").read()
    else:
        msg, err = messages()
        if msg is None:
            print("BROKEN: aucun historique git lisible (%s)." % err)
            return 2
    code, lines = verdict(msg)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
