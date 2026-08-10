#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Echoue quand un cadrage explicitement RETIRE reapparait dans ce que l'utilisateur installe.

## Pourquoi ce fichier existe

Le 2026-08-10, une execution reelle de `/qaia-core:hello` -- le premier dogfood du produit
installe -- a affiche a l'utilisateur que QAIA etait prouve sur un domaine « **medical** ».

Ce cadrage avait ete retire par la decision **D114** apres une verification honnete : QAIA ne
cartographie aucun referentiel du secteur (IEC 62304, 21 CFR Part 11, ISO 13485) et n'a aucun
deploiement medtech. Le README racine dit depuis « healthcare-*shaped*, pas une revendication
reglementaire ». Le README **livre dans le plugin** portait encore l'ancien mot.

C'est la difference qui compte : **la retraction vivait dans les documents de gouvernance, pas
dans le fichier que lit un utilisateur installe.** Le depot avait deja des controles pour la
version (`check_skill_counts`), pour les copies du contrat (`check_published_copies`), pour le
schema (`check_schema_matches_validator`) -- aucun pour « cette phrase a ete retiree, elle ne doit
plus etre livree ». Une affirmation retiree qui survit dans le produit est pire qu'une
affirmation jamais corrigee : le depot peut prouver qu'il savait.

## Portee, deliberement etroite

Ne scanne que `plugins/` -- ce qu'un utilisateur recoit reellement. `docs/`, `eval/` et
`STATUS.md` sont des relevés dates : ils DOIVENT pouvoir citer le cadrage retire pour raconter
qu'il l'a ete, exactement comme `docs/STATUS.md` est hors du perimetre de `check_skill_counts`.

Une ligne n'est signalee que si elle emploie le terme retire **sans** l'un des marqueurs qui
montrent qu'elle en parle plutot qu'elle ne l'affirme (`retired`, `D114`, `no regulatory`,
`shaped`, ...). C'est ce qui separe l'affirmation de la mention -- et c'est la lecon du premier
jet de `check_skill_counts.py`, qui rendait 35 constats dont 33 faux : un controle qui crie au
loup est un controle que personne ne lance.

Run: python eval/tools/check_retired_framing.py
Exit 0 rien de retire n'est livre, 1 au moins une ligne l'affirme, 2 arborescence introuvable.
"""
import io
import os
import re
import sys

# (terme retire, decision, marqueurs qui rendent la ligne legitime, explication rendue au lecteur)
RETIRES = [
    (re.compile(r"\bm[eé]dical\b", re.I),
     "D114",
     # Deux familles d'exemption, et la seconde a ete apprise du premier lancement.
     #
     # 1. La MENTION de la retraction : la ligne parle du cadrage retire au lieu de l'affirmer.
     # 2. L'AVERTISSEMENT : « do not use these thresholds as medical advice » est l'acte de parole
     #    inverse d'une revendication de couverture -- c'est une mise en garde, et l'interdire
     #    pousserait a retirer un disclaimer de securite pour faire taire un linter. Trouve des le
     #    premier lancement sur `qaia-testdata/fixture/US-002-dosage-dataset.json`, un fichier que
     #    mon propre grep manuel avait manque parce qu'il ne cherchait que les .md.
     #
     # La regle est RESSERREE, pas filtree : un avertissement n'est pas une affirmation. Meme
     # discipline que D179, ou chaque reduction de faux positifs s'est faite en precisant la
     # regle et jamais en ecartant sa sortie.
     re.compile(r"retir|retract|no regulatory|not a regulatory|shaped|D114|jamais|"
                r"plus\s+revendiqu|"
                r"(?:medical|clinical)\s+(?:advice|guidance)|do not use|nothing here is real",
                re.I),
     "Le cadrage « medical / environnements reglementes » a ete retire par D114 : QAIA ne "
     "cartographie ni IEC 62304, ni 21 CFR Part 11, ni ISO 13485. Ecrire « healthcare-shaped », "
     "ou nommer explicitement la retraction sur la meme ligne."),
]

RACINE = "plugins"
LISIBLES = (".md", ".txt", ".json", ".yaml", ".yml")


def main():
    if not os.path.isdir(RACINE):
        print("BROKEN: %s/ introuvable -- lancer depuis la racine du depot." % RACINE)
        return 2

    constats, lus = [], 0
    for dossier, sousdossiers, fichiers in os.walk(RACINE):
        sousdossiers[:] = [d for d in sousdossiers if d != "node_modules"]
        for nom in fichiers:
            if not nom.endswith(LISIBLES):
                continue
            chemin = os.path.join(dossier, nom)
            lus += 1
            for i, ligne in enumerate(io.open(chemin, encoding="utf-8", errors="replace"), 1):
                for terme, decision, exemption, remede in RETIRES:
                    if terme.search(ligne) and not exemption.search(ligne):
                        constats.append((chemin, i, decision, ligne.strip()[:110], remede))

    if constats:
        print("CADRAGE RETIRE ENCORE LIVRE -- %d ligne(s).\n" % len(constats))
        for chemin, i, decision, extrait, remede in constats:
            print("  %s:%d  (%s)\n    %s\n    -> %s\n" % (chemin, i, decision, extrait, remede))
        print("Ces fichiers partent chez l'utilisateur a l'installation. Une affirmation retiree")
        print("qui survit dans le produit est pire qu'une affirmation jamais corrigee.")
        return 1

    print("OK: %d fichier(s) livrable(s) lus, aucun cadrage retire (%d terme(s) surveille(s))."
          % (lus, len(RETIRES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
