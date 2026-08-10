#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Eprouve deux comportements de `structural_score.py` que rien ne gardait, dans les deux sens.

## Pourquoi ce fichier existe

Le 2026-08-10, en exercant `testbook-validate` sur un corpus reellement etranger, deux defauts
de lecture du Gherkin sont apparus. Les deux ont ete corriges le jour meme ; aucun n'avait de
garde-fou, et une retouche du parseur les recasserait en silence.

**#103 -- le mot-cle `*`.** Cucumber le documente : « Gherkin also supports using an asterisk
(`*`) in place of any of the normal step keywords ». Il etait absent du motif des pas, donc les
suites Karate -- qui n'utilisent que `*` -- n'avaient aucun pas capture, `then` restait vide, et
le detecteur C2 prononcait « no expected result » puis un FAIL force. Sur des fichiers qui
assertent `status 200` et `match response == first`, et qui tournent en production.

Rendre 0 quand on ne sait pas lire est la faute meme que ce projet reproche aux modeles : une
reponse assuree a la place d'un « je ne sais pas ». Un scenario dont TOUS les pas sont `*` est
donc desormais **rapporte comme non mappe**, exclu des detecteurs de resultat attendu, et jamais
note zero pour cette raison.

**#104 -- le comptage des `Examples`.** Les lignes d'un bloc `Examples:` etaient absorbees dans
le texte du dernier pas, donc un `Scenario Outline` a 6 exemples comptait pour 1 -- quand
`testbook-export` en projette 6 lignes. Deux tailles pour le meme cahier, et des ratios calcules
sur le mauvais denominateur. `executableCases` compte desormais ce qu'un lanceur executera, sans
changer la semantique historique de `scenarios` (les baselines publiees restent comparables).

## Ce qui est verifie, et pourquoi dans les deux sens

Un garde-fou qui ne refuse rien et un garde-fou qui refuse tout sont egalement inutiles. Le
premier jet du hook `block-markdown-through-shell` laissait passer la faute exacte qu'il devait
attraper, et c'est un cas de test qui l'a montre -- pas une relecture.

Run: python eval/tools/selfcheck_gherkin_dialect.py
Exit 0 conforme, 1 un comportement a change, 2 outil introuvable.
"""
import io
import json
import os
import subprocess
import sys
import tempfile

OUTIL = os.path.join("eval", "tools", "structural_score.py")

KARATE = """Feature: dialecte Karate

  Background:
    * url 'https://example.invalid'

  Scenario: get all users and then get the first user by id
    * path 'users'
    * method get
    * status 200
    * match response[0] contains { id: 1 }
"""

OUTLINE = """Feature: Outline a six exemples

  @QAIA-O-001 @AC1 @P1 @boundary
  # condition: C01 — priority P1
  Scenario Outline: Amount <amount> is refused
    Given a report of <amount>
    Then the submission is refused with "<message>"

    Examples:
      | amount | message   |
      | -1     | negative  |
      | 0      | empty     |
      | 0.001  | too small |
      | -0.01  | negative  |
      | -999   | negative  |
      | -1e9   | overflow  |
"""

# Un vrai `Then` vide DOIT toujours declencher C2 : la tolerance au dialecte ne doit pas
# devenir une amnistie generale. C'est le sens « refuse » du test.
THEN_VIDE = """Feature: un Then reellement absent

  @QAIA-V-001 @AC1 @P1 @ep
  # condition: C01 — priority P1
  Scenario: rien n'est verifie
    Given a submitted report
    When the total is evaluated
"""

# Une DataTable sous un `Then` porte le resultat attendu : elle ne doit PAS etre comptee
# comme des cas d'Examples, et ne doit pas declencher C2.
DATATABLE = """Feature: resultat attendu porte par une table

  @QAIA-D-001 @AC1 @P1 @boundary
  # condition: C01 — priority P1
  Scenario: thresholds
    Given a submitted report
    When the total is evaluated
    Then the required approvers are:
      | amount | approvers        |
      | 499.99 | manager          |
      | 500.00 | manager, finance |
"""


def note(contenu, tiers=False):
    d = tempfile.mkdtemp()
    io.open(os.path.join(d, "a.feature"), "w", encoding="utf-8").write(contenu)
    cmd = [sys.executable, OUTIL, "--batch", d] + (["--third-party"] if tiers else [])
    p = subprocess.run(cmd, capture_output=True, text=True)
    for l in p.stdout.splitlines():
        if l.strip().startswith("{"):
            return json.loads(l)
    return None


def main():
    if not os.path.isfile(OUTIL):
        print("BROKEN: %s introuvable -- lancer depuis la racine du depot." % OUTIL)
        return 2

    ko = []

    k = note(KARATE, tiers=True)
    if not k or k.get("unmappableDialect", 0) < 1:
        ko.append(("#103 le dialecte `*` n'est plus reconnu", "unmappableDialect >= 1", k and k.get("unmappableDialect")))
    if k and k.get("gate") == "FAIL" and any("no expected result" in f for f in k.get("findings", [])):
        ko.append(("#103 C2 prononce de nouveau un FAIL sur un cahier en `*`", "pas de C2", "C2 present"))

    o = note(OUTLINE)
    if not o or o.get("executableCases") != 6:
        ko.append(("#104 un Outline a 6 exemples ne compte plus 6 cas", 6, o and o.get("executableCases")))
    if not o or o.get("scenarios") != 1:
        ko.append(("#104 la semantique historique de `scenarios` a change", 1, o and o.get("scenarios")))
    if not o or o.get("outlines") != 1:
        ko.append(("#104 l'Outline n'est plus compte comme tel", 1, o and o.get("outlines")))

    v = note(THEN_VIDE)
    if not v or not any("no expected result" in f for f in v.get("findings", [])):
        ko.append(("un `Then` reellement absent ne declenche plus C2 -- la tolerance au dialecte "
                   "est devenue une amnistie", "C2 present", v and v.get("findings")))

    t = note(DATATABLE)
    if not t or t.get("executableCases") != 1:
        ko.append(("une DataTable est comptee comme des cas d'Examples", 1, t and t.get("executableCases")))
    if not t or any("no expected result" in f for f in t.get("findings", [])):
        ko.append(("une DataTable sous un `Then` declenche C2", "pas de C2", "C2 present"))

    if ko:
        print("LECTURE DU GHERKIN NON CONFORME -- %d cas.\n" % len(ko))
        for nom, attendu, obtenu in ko:
            print("  %s\n    attendu %r, obtenu %r\n" % (nom, attendu, obtenu))
        return 1

    print("OK: dialecte `*` reconnu et rapporte, Examples comptes en cas executables, "
          "`Then` vide toujours refuse, DataTable toujours acceptee.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
