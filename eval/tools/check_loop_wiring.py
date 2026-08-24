#!/usr/bin/env python3
"""Fail when a declared feedback loop stops naming both of its ends.

## Pourquoi ce fichier existe

Une boucle de retour n'existe pas parce que ses deux moities existent. `feedback` et `rag-build`
etaient ecrits, complets et testes bien avant le 2026-08-09, et la boucle « defaut -> jeu de
donnees » ne tournait pas : **aucun des deux ne nommait l'autre**, donc rien ne la declenchait.
Le meme motif exact avait deja coute une decouverte -- `mcp-bridge/` existait, ses tests
passaient, et rien ne les executait ; trois relectures externes l'avaient manque.

Le cablage d'une boucle vit dans de la **prose**, dans deux fichiers que personne ne relit
ensemble. C'est precisement la forme de contrat que ce depot a appris a ne jamais laisser sans
garde : `check_published_copies` pour les copies du contrat, `check_schema_matches_validator`
pour le schema contre le validateur. Celui-ci fait pareil pour les boucles.

Il ne verifie pas que la boucle *fonctionne* -- aucun texte ne peut le prouver. Il verifie
qu'elle est encore **declaree aux deux bouts**, ce qui est la condition necessaire, mecanique, et
la seule qui se decale en silence lors d'une reecriture.

Run: python eval/tools/check_loop_wiring.py
Exit 0 cablage intact, 1 un bout ne nomme plus l'autre, 2 fichier introuvable.
"""
import io
import os
import sys

P = os.path.join

# (nom, source, cible, ce que la source doit nommer, ce que la cible doit nommer)
LOOPS = [
    # `spec-suite-drift` a ete absorbee par `judge` le 2026-08-24. La boucle reste la meme --
    # une suite renvoie a la specification, la specification renvoie a l'application -- mais son
    # extremite porte un autre nom de fichier. Un controle de cablage dont un bout pointe un
    # fichier disparu ne verifie plus la boucle : il annonce sa propre panne.
    ("B  suite -> specification",
     P("plugins", "qaia-score", "skills", "judge", "references", "spec-vs-suite.md"),
     P("plugins", "qaia-playwright", "skills", "contract-probe", "SKILL.md"),
     ["contract-probe"], ["judge"]),

    ("C  defaut -> connaissance",
     P("plugins", "qaia-playwright", "skills", "confirm-fix", "SKILL.md"),
     P("plugins", "qaia-core", "skills", "rag-build", "SKILL.md"),
     ["rag-build", "anomaly-history"], ["confirm-fix"]),

    ("A  signal de production -> question ouverte",
     P("plugins", "qaia-core", "skills", "signal-ingest", "SKILL.md"),
     P("plugins", "qaia-core", "skills", "need-understanding", "SKILL.md"),
     ["need-understanding"], ["signal-ingest"]),
]


def main():
    problems = []
    for name, src, dst, src_needs, dst_needs in LOOPS:
        for path, needles, role in ((src, src_needs, "source"), (dst, dst_needs, "cible")):
            if not os.path.isfile(path):
                problems.append((name, role, path, "FICHIER ABSENT", None))
                continue
            text = io.open(path, encoding="utf-8", errors="replace").read()
            for needle in needles:
                if needle not in text:
                    problems.append((name, role, path, "ne nomme plus", needle))

    if problems:
        print("BOUCLE DECABLEE -- un bout ne nomme plus l'autre.\n")
        for name, role, path, what, needle in problems:
            print("  boucle %s" % name)
            print("      %-7s %s" % (role, path))
            print("      %s%s" % (what, (" : %r" % needle) if needle else ""))
        print("\nUne boucle dont les deux moities existent sans se nommer ne tourne pas :")
        print("c'est exactement ce qui a laisse `feedback` + `rag-build` inertes, et")
        print("`mcp-bridge/` non execute pendant des semaines.")
        return 1

    print("OK: %d boucle(s) -- chaque bout nomme encore l'autre." % len(LOOPS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
