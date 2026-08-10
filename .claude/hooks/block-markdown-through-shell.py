#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Refuse un appel Bash qui fait passer du Markdown par le shell.

## Pourquoi ce fichier existe

`CLAUDE.md` porte la regle depuis le 2026-08-08 : « tout corps de commentaire, d'issue ou de PR
s'ecrit dans un fichier, jamais dans une chaine passee a Bash ». Elle y est arrivee apres **six
recidives dans la meme session**, chacune suivie d'un rappel ecrit, chacune reproduite dans
l'heure.

Le 2026-08-10 la faute est revenue une septieme fois -- sur un `git commit -m` cette fois, pas
sur un commentaire GitHub. Le shell a execute les backticks du message : cinq identifiants
(`source:`, `skills:`, un nom de skill, `uv run`, un autre nom) ont ete remplaces par la sortie
vide de commandes introuvables. Le commit etait deja pousse sur `main` ; reecrire l'historique
pour un message aurait coute plus que la faute.

Le constat de `CLAUDE.md` vaut pour lui-meme : **une regle qui se repete malgre son rappel n'est
pas tenable par l'intention.** Le rappel avait tenu deux commits. L'outil, lui, supprime
l'occasion -- meme logique que `check_skill_counts.py`, `check_decision_register.py` et
`gh_comment.py`, tous nes du meme constat.

## Ce qui est refuse, et ce qui ne l'est pas

Refuse -- un corps de texte redige en ligne dans une commande, quand ce texte contient de quoi
etre mange par le shell :

  * `git commit -m "... `du code` ..."`  et `git tag -m`, `git notes ... -m`
  * `gh ... --body "... `du code` ..."` (issue/pr/comment)
  * un heredoc **non quote** (`<<EOF`) alimentant git ou gh : `$VAR`, `` ` `` et `\` y sont
    interpretes, ce qui est exactement le vecteur des six premieres recidives

Laisse passer, et c'est le point : la forme correcte doit rester sans friction.

  * `git commit -F fichier` / `--file`
  * `gh ... --body-file fichier`, `python eval/tools/gh_comment.py --file corps.md`
  * un heredoc **quote** (`<<'EOF'`), ou le shell n'interprete rien
  * `git commit -m "message simple sans backtick"` -- la majorite des cas, et ils vont bien

Le declencheur est la presence d'un backtick ou d'un `$(` dans le corps en ligne, pas la
longueur du message : un message d'une ligne sans backtick n'a jamais pose probleme, et refuser
tous les `-m` ferait de ce garde-fou un obstacle qu'on contournerait sous une semaine -- la
meme mort que les neuf avertissements de linter ignores trois sprints durant.

Protocole de hook : lit le JSON de l'appel sur stdin, sort 0 pour laisser passer, 2 avec le
motif sur stderr pour refuser (le motif est rendu a l'agent, pas a l'utilisateur).
"""
import json
import re
import sys

# Un corps redige en ligne : l'option, puis ce qui suit jusqu'a la fin de la commande. On ne
# cherche pas a delimiter la chaine (guillemets imbriques, echappements) -- inutile ici : il
# suffit de savoir qu'un backtick apparait APRES l'option de corps.
INLINE_BODY = [
    # Le `[^|;&]*?` doit pouvoir etre VIDE : `git commit -m` n'a qu'une espace entre le
    # sous-commande et l'option. La premiere version exigeait deux separateurs et laissait
    # donc passer la forme exacte qui a cause la panne -- attrapee par le cas 1 du test.
    (re.compile(r"\bgit\s+(?:-[^\s]+\s+)*(?:commit|tag|notes)\b[^|;&]*?\s(-m|--message)\b"),
     "git commit -F <fichier>"),
    (re.compile(r"\bgh\b[^|;&]*?\s(--body)\b(?!-file)"),
     "python eval/tools/gh_comment.py --file <fichier> (il relit depuis l'API et compare)"),
]

# `<<EOF` non quote vs `<<'EOF'` / `<<\"EOF\"` / `<<\\EOF` (quotes = pas d'interpretation).
UNQUOTED_HEREDOC = re.compile(r"<<-?\s*(?![\"'\\])([A-Za-z_][A-Za-z0-9_]*)")
DANGEROUS = re.compile(r"`|\$\(")


def verdict(cmd):
    """Rend (motif, remede) si la commande doit etre refusee, sinon None."""
    for rx, remede in INLINE_BODY:
        m = rx.search(cmd)
        if not m:
            continue
        corps = cmd[m.end():]
        if DANGEROUS.search(corps):
            quoi = "un backtick" if "`" in corps else "une substitution $(...)"
            return ("%s contient %s apres %s : le shell l'executera et le texte publie sera "
                    "ampute de ces references." % (m.group(0).strip(), quoi, m.group(1)), remede)

    if UNQUOTED_HEREDOC.search(cmd) and re.search(r"\b(git|gh)\b", cmd) and DANGEROUS.search(cmd):
        return ("heredoc non quote (`<<EOF`) alimentant git/gh, avec des backticks ou des "
                "substitutions dans le corps : le shell les interprete avant que git ne les voie.",
                "ecrire le corps dans un fichier, ou quoter le delimiteur : <<'EOF'")
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # Un hook qui plante ne doit jamais bloquer un depot.

    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return 0

    v = verdict(cmd)
    if not v:
        return 0
    motif, remede = v
    sys.stderr.write(
        "REFUSE -- du Markdown passe par le shell.\n\n"
        "  %s\n\n"
        "  Remede : %s\n\n"
        "Regle de CLAUDE.md, arrivee apres six recidives dans une meme session (2026-08-08) et "
        "une septieme sur un message de commit (2026-08-10) : un corps de texte s'ecrit dans un "
        "fichier, jamais dans une chaine passee a Bash. Ecris le corps avec l'outil Write, puis "
        "relance avec l'option fichier.\n" % (motif, remede))
    return 2


if __name__ == "__main__":
    sys.exit(main())
