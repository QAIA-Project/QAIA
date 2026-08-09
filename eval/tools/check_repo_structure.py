#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Six controles de structure que la CI faisait et que `make check` ne faisait pas.

`make check` se decrivait comme « tous les controles que la CI lance » et en omettait sept.
Un nouveau venu le lancait, le voyait vert, poussait, et decouvrait la CI rouge -- une cible
qui ment sur sa couverture est pire qu'une cible absente. Releve par la revue « developpeur »
du 2026-08-09.

Les portes ci-dessous etaient ecrites en shell dans `ci.yml`. Les recopier en shell dans
une recette de Makefile aurait cree une deuxieme copie a maintenir -- exactement la faute qu'on
venait de corriger sur le perimetre Gherkin. Elles sont donc ici, en Python, appelees des deux
endroits, et eprouvables sur la machine ou elles sont ecrites (ce que `make` ne permet pas :
il n'existe pas dans l'environnement du fondateur, d'ou le controle par la CI).

Sortie : 0 si tout tient, 1 sinon, avec le detail sur stdout.
"""
from __future__ import print_function

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ce qui n'a pas le droit d'exister sous `plugins/` : un plugin du marketplace est du Markdown
# et rien d'autre. Un `hooks/`, un `agents/` ou un `.mcp.json` y ferait executer du code a
# l'installation, ce que le README promet noir sur blanc qu'il n'arrive pas (ADR 0002).
FORBIDDEN_DIRS = ("hooks", "agents")
FORBIDDEN_FILES = (".mcp.json",)

failures = []


def fail(msg):
    failures.append(msg)
    print("  ECHEC : %s" % msg)


def marketplace_sources_are_relative():
    """Une source absolue rendrait le marketplace ininstallable depuis un fork."""
    path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    if not os.path.isfile(path):
        return fail("`.claude-plugin/marketplace.json` est absent")
    data = json.loads(io.open(path, encoding="utf-8").read())
    for plugin in data.get("plugins", []):
        source = plugin.get("source", "")
        if not isinstance(source, str) or not source.startswith("./"):
            fail("source non relative pour %r : %r" % (plugin.get("name"), source))
    print("  ok : %d source(s) de plugin, toutes relatives" % len(data.get("plugins", [])))


def plugins_carry_no_executable_tier():
    """Le garde-fou d'approvisionnement : rien d'executable sous `plugins/`."""
    base = os.path.join(ROOT, "plugins")
    hits = []
    for dirpath, dirnames, filenames in os.walk(base):
        for d in list(dirnames):
            if d in FORBIDDEN_DIRS:
                hits.append(os.path.relpath(os.path.join(dirpath, d), ROOT))
        for f in filenames:
            if f in FORBIDDEN_FILES:
                hits.append(os.path.relpath(os.path.join(dirpath, f), ROOT))
    for h in sorted(hits):
        fail("%s est interdit sous plugins/ (palier opt-in, ADR 0002)" % h)
    if not hits:
        print("  ok : aucun hooks/, agents/ ou .mcp.json sous plugins/")


def output_contract_is_identical_everywhere():
    """Le contrat de sortie est copie dans chaque plugin ; les copies doivent etre au mot pres."""
    base = os.path.join(ROOT, "plugins")
    if not os.path.isdir(base):
        return fail("`plugins/` est absent")
    reference_path = os.path.join(base, "qaia-core", "OUTPUT-CONTRACT.md")
    if not os.path.isfile(reference_path):
        return fail("le contrat de reference `qaia-core/OUTPUT-CONTRACT.md` est absent")
    reference = io.open(reference_path, encoding="utf-8").read()
    n = 0
    for name in sorted(os.listdir(base)):
        candidate = os.path.join(base, name, "OUTPUT-CONTRACT.md")
        if not os.path.isfile(candidate):
            continue
        n += 1
        if io.open(candidate, encoding="utf-8").read() != reference:
            fail("plugins/%s/OUTPUT-CONTRACT.md diverge de celui de qaia-core" % name)
    print("  ok : %d copie(s) du contrat de sortie, identiques" % n)


# Champs qui feraient executer du code a l'installation s'ils apparaissaient dans un manifeste
# de plugin. Le garde-fou de dossier ne suffit pas : `plugin.json` peut les declarer en ligne.
FORBIDDEN_MANIFEST_KEYS = ("hooks", "mcpServers", "agents")


def every_plugin_is_complete():
    """Un plugin sans `plugin.json` ou sans `README.md` casse l'installation en silence."""
    base = os.path.join(ROOT, "plugins")
    n = 0
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        n += 1
        if not os.path.isfile(os.path.join(d, ".claude-plugin", "plugin.json")):
            fail("plugins/%s ne porte pas de .claude-plugin/plugin.json" % name)
        if not os.path.isfile(os.path.join(d, "README.md")):
            fail("plugins/%s ne porte pas de README.md" % name)
    print("  ok : %d plugin(s), manifeste et README presents" % n)


def no_manifest_declares_an_executable_tier():
    """`hooks`, `mcpServers` et `agents` sont interdits en champ, pas seulement en dossier."""
    base = os.path.join(ROOT, "plugins")
    n = 0
    for name in sorted(os.listdir(base)):
        path = os.path.join(base, name, ".claude-plugin", "plugin.json")
        if not os.path.isfile(path):
            continue
        n += 1
        data = json.loads(io.open(path, encoding="utf-8").read())
        for key in FORBIDDEN_MANIFEST_KEYS:
            if key in data:
                fail("plugins/%s/.claude-plugin/plugin.json declare %r (interdit)" % (name, key))
    print("  ok : %d manifeste(s) sans champ executable" % n)


# Scoreurs livres dans le plugin `qaia-score` (decision du 2026-08-09). Ce sont des COPIES des
# originaux de `eval/tools/`, ou une CI les eprouve par injection de faute a chaque commit.
SHIPPED_SCORERS = ("structural_score.py", "automation_score.py", "spec_suite_drift.py")


def shipped_scorers_match_their_source():
    """Une copie sans rien qui la surveille cesse silencieusement de correspondre.

    C'est la faute corrigee quatre fois le 2026-08-09 -- perimetre Gherkin en double, blocs de
    detection en double, expressions regulieres recopiees a la main, contrat de sortie copie dans
    chaque plugin. Livrer les scoreurs cree une cinquieme copie : elle part avec sa surveillance,
    sinon la decision de les livrer aurait reintroduit par la porte de service exactement ce que
    la journee a passe son temps a fermer.

    Refaire la copie apres un changement voulu :  python eval/tools/ship_scorers.py
    """
    src_dir = os.path.join(ROOT, "eval", "tools")
    dst_dir = os.path.join(ROOT, "plugins", "qaia-score", "scripts")
    if not os.path.isdir(dst_dir):
        return fail("plugins/qaia-score/scripts/ est absent -- les scoreurs livres ont disparu")
    n = 0
    for name in SHIPPED_SCORERS:
        src = os.path.join(src_dir, name)
        dst = os.path.join(dst_dir, name)
        if not os.path.isfile(dst):
            fail("le scoreur livre %s est absent de plugins/qaia-score/scripts/" % name)
            continue
        if not os.path.isfile(src):
            fail("l'original %s est absent de eval/tools/" % name)
            continue
        a = io.open(src, encoding="utf-8", newline="").read()
        b = io.open(dst, encoding="utf-8", newline="").read()
        # Comparaison sur le contenu, pas sur les fins de ligne : git les normalise sous Windows.
        if a.replace("\r\n", "\n") != b.replace("\r\n", "\n"):
            fail("plugins/qaia-score/scripts/%s a derive de eval/tools/%s "
                 "-- refaire la copie avec `python eval/tools/ship_scorers.py`" % (name, name))
            continue
        n += 1
    if n:
        print("  ok : %d scoreur(s) livre(s), identiques a leur original" % n)


def main():
    print("check_repo_structure :")
    marketplace_sources_are_relative()
    every_plugin_is_complete()
    plugins_carry_no_executable_tier()
    no_manifest_declares_an_executable_tier()
    output_contract_is_identical_everywhere()
    shipped_scorers_match_their_source()
    if failures:
        print("::error::%d controle(s) de structure en echec." % len(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
