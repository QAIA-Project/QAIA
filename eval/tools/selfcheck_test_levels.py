#!/usr/bin/env python3
"""Prove check_test_levels.py detects both ADR 0008 violations -- and stays silent otherwise.

## Pourquoi ce fichier existe

Un controle qui n'a jamais ete vu rouge ne prouve rien. `make lint` etait vert a vide le
2026-07-30 puis de nouveau le 2026-08-10, les deux fois parce que rien n'avait exerce la panne
que la cible pretendait attraper. `check_test_levels.py` nait donc avec sa fixture rouge et cette
auto-verification, dans la meme famille que `selfcheck_gherkin_dialect.py` et
`selfcheck_markdown_shell_hook.py`.

Les trois cas sont exerces sur `fixtures/test-levels-red/violations.feature` :

| Scenario | Attendu |
|---|---|
| aucune etiquette | signale |
| deux etiquettes | signale |
| une etiquette | silence |

Le troisieme cas compte autant que les deux autres : un controle qui signalerait tout serait
inutilisable, et son rouge ne voudrait rien dire.

Run: python eval/tools/selfcheck_test_levels.py
Exit 0 conforme, 1 le controle ne detecte pas ce qu'il promet, 2 fixture introuvable.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_test_levels as C

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "fixtures", "test-levels-red", "violations.feature")

EXPECTED = [
    ("FIX-001", "aucune etiquette de niveau", "aucune"),
    ("FIX-002", "deux etiquettes de niveau", "2 etiquettes"),
]


def main():
    if not os.path.exists(FIXTURE):
        print("::error::fixture rouge introuvable : %s" % FIXTURE, file=sys.stderr)
        return 2

    offenders = C.check_file(FIXTURE)
    failures = []

    retired = [o for o in offenders if "retiree" in o[2]]
    offenders = [o for o in offenders if "retiree" not in o[2]]

    if len(retired) != 1:
        failures.append("l'etiquette retiree @use-case devrait etre signalee une fois, "
                        "signalee %d fois" % len(retired))
    elif "Une etiquette retiree" not in retired[0][1]:
        failures.append("signalement de l'etiquette retiree sur le mauvais scenario : %s"
                        % retired[0][1])

    if len(offenders) != 2:
        failures.append("le controle signale %d scenario(s) de niveau, 2 attendus : %s"
                        % (len(offenders), [o[1] for o in offenders]))
    else:
        (_, name_a, reason_a), (_, name_b, reason_b) = offenders
        if "Aucune etiquette" not in name_a:
            failures.append("premier signalement attendu sur le scenario sans etiquette, obtenu : %s"
                            % name_a)
        elif "aucune etiquette de niveau" not in reason_a:
            failures.append("motif inattendu pour l'absence d'etiquette : %s" % reason_a)
        if "Deux etiquettes" not in name_b:
            failures.append("second signalement attendu sur le scenario a deux etiquettes, obtenu : %s"
                            % name_b)
        elif "2 etiquettes" not in reason_b:
            failures.append("motif inattendu pour le doublon d'etiquettes : %s" % reason_b)

    signalled = " ".join(o[1] for o in offenders + retired)
    if "Une seule etiquette" in signalled:
        failures.append("le scenario conforme (@api seul) a ete signale -- faux positif")
    # Forme reelle du depot : tags, puis commentaire, puis Scenario. Une campagne mutation du
    # 2026-08-11 a montre que neutraliser la remontee au-dessus d'un commentaire ne faisait
    # rougir aucune auto-verification -- le controle serait devenu aveugle a la moitie des
    # cahiers sans que rien ne le signale. C'est la seule mutation survivante des treize.
    if "separee du scenario par un commentaire" in signalled:
        failures.append("le scenario dont les tags sont suivis d'un commentaire a ete signale -- "
                        "faux positif sur la forme la plus courante du depot")

    # La fixture rouge doit rester HORS du perimetre du controle lui-meme, sinon `make check`
    # serait rouge en permanence et la preuve deviendrait une panne.
    in_scope = [p for p in C.iter_feature_files(".")
                if "test-levels-red" in p.replace("/", os.sep)]
    if in_scope:
        failures.append("la fixture rouge est dans le perimetre du controle : %s" % in_scope)

    # LE PERIMETRE LUI-MEME. La panne du 2026-08-11 n'etait pas une regle de detection cassee :
    # c'etait un perimetre en dur qui ignorait un dossier cree le soir meme. Aucune des trois
    # verifications ci-dessus ne l'aurait vue, parce qu'elles portent toutes sur la fixture.
    # Ces deux assertions portent sur le DEPOT : un cahier vivant connu doit etre dedans, une
    # preuve gelee connue doit etre dehors.
    in_scope = [p for p in C.iter_feature_files(".")]
    living_witness = os.path.join("site-qa", "qaia-journey", "testbooks")
    frozen_witness = os.path.join("eval", "baselines")
    if not any(p.startswith(living_witness) for p in in_scope):
        failures.append("perimetre : aucun cahier sous %s n'est controle -- c'est exactement la "
                        "panne du 2026-08-11, ou deux cahiers livres le soir etaient hors du "
                        "garde-fou ecrit le matin" % living_witness)
    if any(p.startswith(frozen_witness) for p in in_scope):
        failures.append("perimetre : une preuve gelee (%s) est entree dans le controle -- la "
                        "reecrire pour satisfaire une regle posterieure la detruirait "
                        "(ADR 0008)" % frozen_witness)
    if len(in_scope) < 10:
        failures.append("perimetre : %d cahier(s) seulement -- ce depot en contient davantage, "
                        "un controle qui n'en voit presque aucun passe vert sans rien verifier"
                        % len(in_scope))

    if failures:
        print("::error::l'auto-verification des niveaux de test echoue.")
        for line in failures:
            print("  " + line)
        return 1

    print("OK: la fixture rouge est vue rouge (absence, doublon, etiquette retiree), le cas "
          "conforme reste silencieux, et la fixture est hors perimetre du controle.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
