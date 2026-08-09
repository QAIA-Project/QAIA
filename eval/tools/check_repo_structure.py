#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cinq controles de structure que la CI faisait et que `make check` ne faisait pas.

`make check` se decrivait comme « tous les controles que la CI lance » et en omettait sept.
Un nouveau venu le lancait, le voyait vert, poussait, et decouvrait la CI rouge -- une cible
qui ment sur sa couverture est pire qu'une cible absente. Releve par la revue « developpeur »
du 2026-08-09.

Les cinq portes ci-dessous etaient ecrites en shell dans `ci.yml`. Les recopier en shell dans
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


def main():
    print("check_repo_structure :")
    marketplace_sources_are_relative()
    every_plugin_is_complete()
    plugins_carry_no_executable_tier()
    no_manifest_declares_an_executable_tier()
    output_contract_is_identical_everywhere()
    if failures:
        print("::error::%d controle(s) de structure en echec." % len(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
