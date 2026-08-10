#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Eprouve le hook `block-markdown-through-shell.py` dans les deux sens, a chaque commit.

## Pourquoi ce fichier existe

Le hook a ete ecrit le 2026-08-10 pour supprimer une faute que `CLAUDE.md` rappelait sans succes
depuis six recidives : du Markdown passe par le shell, les backticks executes, le texte publie
ampute. Il a ete eprouve a la main le jour meme -- 12 cas, 12 verts.

**Ce test-la vivait dans une transcription de session, pas dans le depot.** Et le premier jet du
hook **laissait passer la faute exacte qu'il devait attraper** : son motif exigeait deux
separateurs entre `commit` et `-m` alors que la forme reelle n'en a qu'un. C'est un cas de test
qui l'a montre, pas une relecture.

Un garde-fou dont la preuve n'est pas rejouable est un garde-fou qu'une retouche de motif casse en
silence. C'est exactement ce que le depot reproche a une liste dupliquee, et la meme reponse
s'applique : l'ecrire une fois, l'executer a chaque commit.

Trouve par `qaia-playwright:impact-select` applique au diff de la session du 2026-08-10, sur sa
seconde question -- « qu'est-ce que le changement laisse non couvert ? », celle dont la skill dit
qu'elle a le plus de valeur et que personne ne demande.

## Ce qui est verifie

Les deux sens, parce qu'un garde-fou qui ne refuse rien et un garde-fou qui refuse tout sont
egalement inutiles :

* **Doit refuser (exit 2)** -- un corps redige en ligne contenant de quoi etre mange par le shell.
* **Doit laisser passer (exit 0)** -- les formes correctes, et tout `-m` inoffensif, qui est la
  majorite des cas. Refuser trop ferait de ce hook un obstacle contourne sous une semaine.

Run: python eval/tools/selfcheck_markdown_shell_hook.py
Exit 0 tous les cas conformes, 1 au moins un cas diverge, 2 hook introuvable.
"""
import json
import os
import subprocess
import sys

HOOK = os.path.join(".claude", "hooks", "block-markdown-through-shell.py")

# (code attendu, intitule, commande soumise au hook)
CAS = [
    (2, "git commit -m avec backticks (la faute du 2026-08-10)",
     'git commit -m "corrige `source:` et `skills:`"'),
    (2, "git commit -a -m avec backticks (une option intercalee)",
     'git commit -a -m "voir `foo`"'),
    (2, "git tag -m avec backticks",
     'git tag -a v1 -m "voir `foo.py`"'),
    (2, "gh --body en ligne avec backticks",
     'gh issue comment 88 --body "voir `check_skill_counts.py`"'),
    (2, "heredoc non quote alimentant git",
     'git commit -F - <<EOF\nvoir `foo.py`\nEOF'),
    (2, "substitution $(...) dans un -m",
     'git commit -m "version $(cat v.txt)"'),

    (0, "git commit -F fichier (la forme correcte)",
     'git commit -F msg.txt'),
    (0, "gh_comment.py --file (l outil du depot)",
     'python eval/tools/gh_comment.py --file corps.md --issue 88'),
    (0, "gh --body-file",
     'gh issue create --body-file corps.md'),
    (0, "heredoc quote -- le shell n interprete rien",
     "git commit -F - <<'EOF'\nvoir `foo.py`\nEOF"),
    (0, "message simple sans backtick (le cas courant)",
     'git commit -m "corrige le compte de skills"'),
    (0, "commande sans rapport contenant un backtick",
     'echo "`date`"'),
    (0, "git log avec un backtick -- lecture, pas ecriture",
     'git log --grep="`"'),
]


def main():
    if not os.path.isfile(HOOK):
        print("BROKEN: %s introuvable -- lancer depuis la racine du depot." % HOOK)
        return 2

    divergences = []
    for attendu, nom, cmd in CAS:
        p = subprocess.run(
            [sys.executable, HOOK],
            input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
            capture_output=True, text=True)
        if p.returncode != attendu:
            divergences.append((nom, attendu, p.returncode, cmd))

    # Un refus doit expliquer pourquoi : un hook qui bloque sans motif se fait desactiver.
    p = subprocess.run(
        [sys.executable, HOOK],
        input=json.dumps({"tool_name": "Bash",
                          "tool_input": {"command": 'git commit -m "voir `foo.py`"'}}),
        capture_output=True, text=True)
    if "REFUSE" not in p.stderr or "-F" not in p.stderr:
        divergences.append(("le refus n'enonce pas son motif et son remede", "motif+remede",
                            p.stderr.strip()[:60] or "(stderr vide)", "-"))

    if divergences:
        print("HOOK NON CONFORME -- %d cas sur %d.\n" % (len(divergences), len(CAS) + 1))
        for nom, attendu, obtenu, cmd in divergences:
            print("  %s\n    attendu %s, obtenu %s\n    sur : %s\n" % (nom, attendu, obtenu, cmd))
        print("Le hook refuse ce qu'il devrait laisser passer, ou l'inverse. Les deux le rendent")
        print("inutile : le premier le fait contourner, le second le fait ignorer.")
        return 1

    refus = sum(1 for a, _, _ in CAS if a == 2)
    print("OK: %d cas -- %d refus attendus, %d passages attendus, plus le motif du refus."
          % (len(CAS), refus, len(CAS) - refus))
    return 0


if __name__ == "__main__":
    sys.exit(main())
