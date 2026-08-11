#!/usr/bin/env python3
"""Fail when a living test book carries a scenario without exactly one test-level tag.

## Pourquoi ce fichier existe

[ADR 0008](docs/adr/0008-test-level-is-a-design-property.md) decide que le niveau de test est une
propriete de la condition, decidee par `istqb-design`, portee par le scenario, et **lue** par
`automate` au lieu d'etre devinee. Une decision qu'aucun controle n'applique est une intention :
ce depot a deja eu deux portes de CI vertes a vide, les 2026-07-30 et 2026-08-10, et les deux fois
la panne tenait a ce que rien ne verifiait ce que la cible pretendait verifier.

`gherkin-lint` ne sait pas exiger une etiquette : ses regles de tags sont `allowed-tags` et
`no-restricted-tags` -- des listes de ce qui est **permis**, jamais de ce qui est **obligatoire**.
D'ou ce controle, dans la meme famille que `check_skill_counts.py` et `check_decision_register.py`.

## Ce qui est verifie

Pour chaque `Scenario:` / `Scenario Outline:` d'un cahier **vivant** : exactement une etiquette
parmi `@e2e` et `@api`, sur la ligne de tags qui precede le scenario. Ni zero, ni deux -- un
scenario qui reclamerait les deux verifie deux promesses par deux interfaces, ce qui est un defaut
d'atomicite a scinder (ADR 0008), pas une etiquette a ajouter.

## Ce qui n'est PAS verifie, et pourquoi c'est ecrit ici

Les **artefacts de campagne** -- `eval/baselines/`, `eval/gold-set/`, `eval/goldset-hardened/`,
les sorties de campagnes horodatees. Ce sont des preuves de ce qui a ete produit a une date. Les
reecrire pour satisfaire une regle posterieure falsifierait la preuve, et un depot qui retouche ses
mesures pour faire passer ses portes n'a plus de mesures. L'exclusion est **decidee** (ADR 0008,
section Consequences), pas subie.

Le perimetre exclut aussi ce que `make lint` exclut deja (node_modules, exports) : deux perimetres
qui divergent, c'est la panne du 2026-08-10 -- alors celui-ci est plus **strict** que celui du lint
et ne peut pas se retrouver a couvrir des fichiers que le lint ignore.

Run: python eval/tools/check_test_levels.py
Exit 0 conforme, 1 non conforme, 2 perimetre casse.
"""
import io
import os
import re
import sys

LEVEL_TAGS = ("@e2e", "@api")

SCENARIO_RE = re.compile(r"^\s*(Scenario|Scenario Outline)\s*:", re.IGNORECASE)
TAG_LINE_RE = re.compile(r"^\s*@")

# Les racines des cahiers VIVANTS -- ceux qu'une regle posterieure a le droit de faire evoluer.
LIVING_ROOTS = (
    os.path.join(".qaia", "testbooks"),
    "examples",
    os.path.join("plugins", "qaia-playwright", "skills"),
    os.path.join("eval", "tools", "fixtures"),
)

# Preuves gelees : jamais reecrites (ADR 0008). Liste explicite plutot que negative, pour qu'un
# nouveau repertoire de campagne soit hors perimetre par defaut et non dedans par accident.
EXCLUDED_MARKERS = (
    os.sep + "node_modules" + os.sep,
    os.sep + "export" + os.sep,
    os.path.join("eval", "tools", "fixtures", "test-levels-red"),  # la fixture rouge, voir selfcheck
)


def iter_feature_files(root="."):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "node_modules"]
        for name in filenames:
            if not name.endswith(".feature"):
                continue
            path = os.path.relpath(os.path.join(dirpath, name), root)
            normalized = os.sep + path + os.sep
            if any(marker in normalized for marker in EXCLUDED_MARKERS):
                continue
            if not any(path.startswith(living + os.sep) for living in LIVING_ROOTS):
                continue
            yield path


def check_file(path):
    """Return the list of offending (line_no, scenario_name, reason) for one file."""
    with io.open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    offenders = []
    for index, line in enumerate(lines):
        if not SCENARIO_RE.match(line):
            continue
        # Remonter la pile de tags contigus au-dessus du scenario : les commentaires et les
        # lignes vides ne cassent pas la pile cote Gherkin, mais un autre mot-cle si.
        tags = []
        cursor = index - 1
        while cursor >= 0:
            above = lines[cursor]
            if TAG_LINE_RE.match(above):
                tags = above.split() + tags
                cursor -= 1
            elif above.strip() == "" or above.lstrip().startswith("#"):
                cursor -= 1
            else:
                break
        found = [t for t in tags if t in LEVEL_TAGS]
        name = line.strip()
        if len(found) == 0:
            offenders.append((index + 1, name, "aucune etiquette de niveau (@e2e ou @api)"))
        elif len(found) > 1:
            offenders.append((index + 1, name,
                              "%d etiquettes de niveau (%s) -- un scenario en porte exactement une"
                              % (len(found), " ".join(found))))
    return offenders


def main(argv):
    root = argv[1] if len(argv) > 1 else "."
    files = sorted(iter_feature_files(root))
    if not files:
        print("ERREUR : perimetre casse -- aucun cahier vivant trouve, alors que ce depot en "
              "contient. Verifier LIVING_ROOTS.", file=sys.stderr)
        return 2

    total_scenarios = 0
    failures = []
    for rel in files:
        full = os.path.join(root, rel)
        with io.open(full, encoding="utf-8") as handle:
            total_scenarios += sum(1 for line in handle if SCENARIO_RE.match(line))
        for line_no, name, reason in check_file(full):
            failures.append((rel, line_no, name, reason))

    print("Perimetre niveaux : %d cahier(s) vivant(s), %d scenario(s) verifie(s)."
          % (len(files), total_scenarios))

    if failures:
        print("::error::%d scenario(s) sans etiquette de niveau conforme (ADR 0008)."
              % len(failures))
        for rel, line_no, name, reason in failures:
            print("  %s:%d  %s" % (rel, line_no, name))
            print("      %s" % reason)
        print("\nAjouter @e2e ou @api sur la ligne de tags du scenario. Le niveau se lit dans "
              "`03-design.md` (istqb-design l'y a assigne et justifie), il ne se rededuit pas "
              "du texte des pas.")
        return 1

    print("OK: chaque scenario porte exactement une etiquette de niveau (@e2e | @api).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
