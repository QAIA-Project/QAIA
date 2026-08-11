#!/usr/bin/env python3
"""Campagne mutation sur les GARDE-FOUS construits en S38-S40.

Run: python eval/tools/mutate_guards.py   (ecrit eval/mutation-guards-<date>.txt)

Elle N'est PAS dans `make check` : elle modifie des fichiers du depot le temps de chaque
mutation, ce qu'une cible lancee en boucle par un nouveau venu ne doit pas faire. Elle se
relance a la main quand un garde-fou change.

Un controle protege une regle. Qui protege le controle ? Son auto-verification -- si elle est
reelle. Cette campagne mute la LOGIQUE DE DETECTION de chaque controle et exige que son selfcheck
passe au rouge. Une mutation qui survit designe une regle que le controle croit appliquer et
n'applique pas.
"""
import io, os, subprocess, sys, json

ROOT = os.getcwd()

MUTATIONS = [
    # (cible, selfcheck attendu rouge, libelle, avant, apres)
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "niveau absent : la detection de l'absence est neutralisee",
     "if len(found) == 0:", "if False:"),
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "niveau en double : la detection du doublon est neutralisee",
     "elif len(found) > 1:", "elif False:"),
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "etiquette retiree : la table des retirees est videe",
     'RETIRED_TAGS = {\n    "@use-case"', 'RETIRED_TAGS = {} or {\n    "@NEVER-EMITTED"'),
    ("eval/tools/check_test_levels.py", "eval/tools/selfcheck_test_levels.py",
     "la pile de tags ne remonte plus au-dessus d'un commentaire",
     'elif above.strip() == "" or above.lstrip().startswith("#"):', "elif False:"),

    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "etapes : la comparaison verbatim est neutralisee",
     "if block[2] != steps:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "titre : la comparaison de titre est neutralisee",
     "if block[1] != title:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "scenario omis : la boucle des identifiants attendus est neutralisee",
     "if seen_ids.count(scenario_id) == 0:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "bloc en trop : la detection d'un identifiant inconnu est neutralisee",
     "if scenario_id not in expected_ids:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "langue : l'en-tete `language:` n'est plus exige",
     "if language not in LABELS:", "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "Outline : les `Examples` ne sont plus eclates",
     'if current["outline"] and current["rows"]:', "if False:"),
    ("eval/tools/check_nl_projection.py", "eval/tools/selfcheck_nl_projection.py",
     "substitution : les parametres <x> ne sont plus remplaces",
     'text = text.replace("<%s>" % key, value)', "pass"),

    ("eval/tools/validate_manifest.py", "eval/tools/selfcheck_manifest_bylevel.py",
     "byLevel : la verification de la somme est neutralisee",
     "and summed != total:", "and False:"),
    ("eval/tools/validate_manifest.py", "eval/tools/selfcheck_manifest_bylevel.py",
     "byLevel : la liste fermee de cles n'est plus imposee",
     'unknown = sorted(set(by_lvl) - {"e2e", "api"})', "unknown = []"),
    ("eval/tools/validate_manifest.py", "eval/tools/selfcheck_manifest_bylevel.py",
     "byLevel : le bloc partiel n'est plus refuse",
     'for lvl in ("e2e", "api"):', "for lvl in ():"),
]


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=False)
    return p.returncode, (p.stdout + p.stderr)


def main():
    log = ["Campagne mutation sur les garde-foux S38-S40 -- %s" % "2026-08-11", ""]
    log.append("Chaque mutation neutralise UNE regle de detection dans un controle.")
    log.append("TUEE = l'auto-verification du controle passe au rouge. SURVIT = personne ne l'aurait vu.")
    log.append("")
    killed = survived = 0
    for target, selfcheck, label, before, after in MUTATIONS:
        original = io.open(target, encoding="utf-8", newline="").read()
        if before not in original:
            print("!! motif introuvable :", label)
            log.append("[ERREUR] motif introuvable : %s" % label)
            continue
        io.open(target, "w", encoding="utf-8", newline="").write(original.replace(before, after, 1))
        try:
            code, out = run([sys.executable, selfcheck])
            ok = code != 0
        finally:
            io.open(target, "w", encoding="utf-8", newline="").write(original)
        killed += ok
        survived += (not ok)
        first = next((l for l in out.splitlines() if l.strip()), "")
        log.append("[%s] %s\n    %s -> exit=%d  %s"
                   % ("TUEE  " if ok else "SURVIT", label,
                      os.path.basename(selfcheck),
                      code, first[:150]))
        print(("TUEE   " if ok else "SURVIT "), label)
    log.append("")
    log.append("TOTAL : %d candidates, %d executees, %d tuees, %d survivantes"
               % (len(MUTATIONS), len(MUTATIONS), killed, survived))
    io.open("eval/mutation-guards-2026-08-11.txt", "w", encoding="utf-8", newline="\n").write(
        "\n".join(log) + "\n")
    print("killed", killed, "survived", survived)


if __name__ == "__main__":
    main()
