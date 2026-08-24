#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Banc du noyau deterministe : debit reel et montee en charge.

La refonte du 2026-08-24 fait de ce noyau LE produit. Un produit qu'on demande a quelqu'un de
lancer sur son depot doit savoir ce qu'il coute, et personne ne l'avait jamais mesure.

La question qui compte n'est pas le debit -- c'est la MONTEE EN CHARGE. Le detecteur de
redondance (« paradoxe du pesticide ») compare des scenarios entre eux ; ecrit naivement il
serait en O(n2) et exploserait sur un gros cahier, c'est-a-dire dans le cas exact ou un
utilisateur lancerait l'outil sur toute sa suite d'un coup. Le banc l'eprouve dans les deux
regimes, dont le pire cas du detecteur (tous les scenarios identiques).

Il est fige en script parce qu'une mesure qu'on ne peut pas rejouer n'est pas une preuve --
y compris quand sa conclusion est rassurante. C'est le cas ou l'on est le plus tente de s'en
dispenser.

Usage: python3 bench_core.py [--corpus <dir>]   (le corpus est optionnel : sans lui, seule la
                                                 montee en charge synthetique est mesuree)
"""
import os
import shutil
import statistics
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import automation_score as A  # noqa: E402
import structural_score as S  # noqa: E402

SIZES = (50, 100, 200, 400, 800, 1600, 3200)
# Au-dela, le banc dirait surtout combien de temps met Python a ecrire un fichier de 3 Mo.


def gherkin(n, distinct=True):
    out = ["Feature: charge", ""]
    for i in range(n):
        out += ["  @QAIA-PERF-%04d @AC1 @P1 @ep" % i,
                "  Scenario: le montant %d est accepte" % i,
                "    Given un panier de %d EUR" % (i if distinct else 1),
                "    When l'utilisateur valide",
                '    Then le total affiche est "%d,00 EUR"' % i, ""]
    return "\n".join(out)


def playwright(n):
    out = ["import { test, expect } from '@playwright/test';", ""]
    for i in range(n):
        out += ["test('JIRA-%04d le total est correct', async ({ page }) => {" % i,
                "  await page.getByRole('button', { name: 'valider' }).click();",
                "  await expect(page.getByRole('status')).toHaveText('%d,00');" % i,
                "});", ""]
    return "\n".join(out)


def time_gherkin(n, distinct):
    fd, path = tempfile.mkstemp(suffix=".feature")
    os.close(fd)
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(gherkin(n, distinct))
        t = time.perf_counter()
        result = S.score_feature(path)
        return (time.perf_counter() - t) * 1000, result
    finally:
        os.unlink(path)


def time_playwright(n):
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, "a.spec.ts"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(playwright(n))
        specs, _ = A.find_spec_files(d)
        t = time.perf_counter()
        result = A.static_track(specs, [], d, set())
        return (time.perf_counter() - t) * 1000, result
    finally:
        shutil.rmtree(d, ignore_errors=True)


def bench_corpus(root):
    files = [os.path.join(dp, f) for dp, _dn, fs in os.walk(root)
             for f in fs if f.endswith(".feature")]
    if not files:
        print("  aucun .feature sous %s -- debit non mesure" % root)
        return
    for f in files[:20]:            # chauffe : sinon on mesure l'import des expressions
        S.score_feature(f)
    per, t0 = [], time.perf_counter()
    for f in files:
        a = time.perf_counter()
        S.score_feature(f)
        per.append((time.perf_counter() - a) * 1000)
    total = time.perf_counter() - t0
    per.sort()
    sizes = [os.path.getsize(f) for f in files]
    print("  %d fichiers, %.1f Ko" % (len(files), sum(sizes) / 1024.0))
    print("  total %.2f s -- %.0f fichiers/s -- %.1f Ko/s"
          % (total, len(files) / total, (sum(sizes) / 1024.0) / total))
    print("  par fichier : mediane %.2f ms | p95 %.2f ms | max %.2f ms"
          % (per[len(per) // 2], per[int(len(per) * 0.95)], per[-1]))
    print("  taille moyenne %.0f octets" % statistics.mean(sizes))


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    corpus = None
    if "--corpus" in sys.argv:
        corpus = sys.argv[sys.argv.index("--corpus") + 1]

    if corpus:
        print("Debit sur corpus reel")
        bench_corpus(corpus)
        print("")

    print("Montee en charge -- structural_score (ms)")
    print("  %10s %12s %12s" % ("scenarios", "distincts", "identiques"))
    for n in SIZES:
        a, _ = time_gherkin(n, True)
        b, _ = time_gherkin(n, False)
        print("  %10d %9.0f ms %9.0f ms" % (n, a, b))

    print("")
    print("Montee en charge -- automation_score, passe statique (ms)")
    print("  %10s %12s %8s %6s" % ("tests", "duree", "score", "dims"))
    for n in SIZES[:-1]:
        d, r = time_playwright(n)
        # `dims` est verifie ICI et pas seulement dans le selfcheck : si la tracabilite
        # etrangere (JIRA-####) cessait d'etre creditee, le nombre de dimensions notees
        # tomberait, et le banc le verrait a TOUTES les echelles -- pas seulement sur la
        # fixture de deux tests du selfcheck.
        print("  %10d %9.0f ms %8.1f %6d" % (n, d, r["score"], len(r["budget"])))


if __name__ == "__main__":
    main()
