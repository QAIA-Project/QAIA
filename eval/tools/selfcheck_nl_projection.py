#!/usr/bin/env python3
"""Prove check_nl_projection.py catches every way a natural-language rendering can drift.

## Pourquoi ce fichier existe

Le rendu en langage naturel n'a de valeur que si l'on peut affirmer qu'il ne ment pas. Cette
affirmation vaut ce que vaut son controle -- et un controle qui n'a jamais ete vu rouge ne prouve
rien. Ce depot a eu deux portes de CI vertes a vide en douze jours (2026-07-30, 2026-08-10) : les
deux fois, rien n'exercait la panne que la cible pretendait attraper.

Huit divergences injectees, une par facon dont une projection peut trahir sa source, plus le cas
conforme qui doit rester silencieux. Le neuvieme cas compte autant que les huit autres : un
controle qui signalerait tout serait inutilisable, et son rouge ne voudrait rien dire.

| Fixture | Ce qu'elle injecte | Attendu |
|---|---|---|
| `conforme.md` | rien | silence |
| `divergence-etape-inventee.md` | une etape absente du Gherkin | INVENTEE |
| `divergence-etape-perdue.md` | une etape du Gherkin non rendue | PERDUE |
| `divergence-scenario-omis.md` | un exemple d'`Outline` saute | absent du rendu |
| `divergence-bloc-en-trop.md` | un identifiant que le Gherkin ne porte pas | inconnu |
| `divergence-ordre.md` | memes etapes, ordre change | ordre different |
| `divergence-valeur-example.md` | une valeur d'`Examples` modifiee d'un caractere | INVENTEE + PERDUE |
| `divergence-titre.md` | un titre reecrit | titre divergent |
| `divergence-langue.md` | en-tete `language:` absent | langue hors liste fermee |

`divergence-valeur-example.md` est la plus importante : c'est la derive qu'un relecteur humain ne
verra jamais -- « 998 » au lieu de « 999 » dans un document de vingt pages.

Run: python eval/tools/selfcheck_nl_projection.py
Exit 0 conforme, 1 le controle ne detecte pas ce qu'il promet, 2 fixtures introuvables.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_nl_projection as C

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "nl-projection-red")
FEATURE = os.path.join(FIXTURES, "base.feature")

# (fichier, fragment attendu dans AU MOINS un probleme signale)
CASES = [
    ("divergence-etape-inventee.md", "INVENTEE"),
    ("divergence-etape-perdue.md", "PERDUE"),
    ("divergence-scenario-omis.md", "absent du rendu"),
    ("divergence-bloc-en-trop.md", "que le Gherkin ne contient pas"),
    ("divergence-ordre.md", "ordre different"),
    ("divergence-valeur-example.md", "INVENTEE"),
    ("divergence-titre.md", "titre rendu"),
    ("divergence-langue.md", "language"),
]


def main():
    if not os.path.exists(FEATURE):
        print("::error::fixture introuvable : %s" % FEATURE, file=sys.stderr)
        return 2

    failures = []

    clean, count = C.check_pair(FEATURE, os.path.join(FIXTURES, "conforme.md"))
    if clean:
        failures.append("le rendu CONFORME est signale -- faux positif : %s" % clean)
    if count != 3:
        failures.append("la fixture devrait porter 3 scenarios (1 + un Outline a 2 exemples), "
                        "%d comptes" % count)

    for name, fragment in CASES:
        path = os.path.join(FIXTURES, name)
        if not os.path.exists(path):
            failures.append("fixture manquante : %s" % name)
            continue
        problems, _ = C.check_pair(FEATURE, path)
        if not problems:
            failures.append("%s : divergence NON detectee -- le controle est aveugle a ce cas"
                            % name)
        elif not any(fragment in p for p in problems):
            failures.append("%s : detectee, mais aucun message ne porte %r ; obtenu %r"
                            % (name, fragment, problems[:2]))

    # Les fixtures rouges doivent rester HORS du perimetre du controle lui-meme, sinon `make check`
    # serait rouge en permanence et la preuve deviendrait une panne.
    in_scope = [p for p in C.find_pairs(".")
                if "nl-projection-red" in str(p)]
    if in_scope:
        failures.append("les fixtures rouges sont dans le perimetre du controle : %s" % in_scope)

    if failures:
        print("::error::l'auto-verification du rendu en langage naturel echoue.")
        for line in failures:
            print("  " + line)
        return 1

    print("OK: les 8 divergences injectees sont detectees, le rendu conforme reste silencieux, "
          "et les fixtures sont hors perimetre du controle.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
