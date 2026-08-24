#!/usr/bin/env python3
"""Self-check for spec_suite_drift.py, on fixtures built in a temporary directory.

Two directions, because a detector that fires on everything discriminates nothing:

  DRIFTING  -- a specification and a suite that disagree in the three ways the tool names.
               Each rule must fire, exactly once, on the planted line.
  CLEAN     -- a specification and a suite that agree. Nothing may fire.

The founding case is `realworld-apps/realworld` (2026-08-09): the spec promises 409 on
`POST /users`, the suite mocks that exact case as 400, and no test exercises 409. Both halves
look self-consistent from inside, which is why only a cross-comparison finds it.

Run: python eval/tools/selfcheck_spec_suite_drift.py
Exits non-zero on the first failure.
"""
import io
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_suite_drift as D  # noqa: E402

failures = []


def check(label, got, want):
    if got != want:
        failures.append("%s\n    got:  %r\n    want: %r" % (label, got, want))


SPEC = """
openapi: 3.0.0
info: {title: fixture, version: '1'}
paths:
  /users:
    post:
      responses:
        '201': {description: created}
        '409': {description: conflict}
  /articles/{slug}:
    get:
      responses:
        '200': {description: ok}
        '404': {description: missing}
"""

DRIFTING = """
import { test, expect } from '@playwright/test';

test('registration rejects a duplicate email', async ({ page }) => {
  await page.goto('/register');
  await mockApiError(page, '/users', 400, { errors: { email: ['is already taken'] } });
  await page.click('button[type="submit"]');
});

test('an unknown article shows a message', async ({ page }) => {
  await page.route('/api/articles/some-slug', r => r.fulfill({ status: 404 }));
  await expect(page.locator('.msg')).toBeVisible();
});

test('the newsletter endpoint is reachable', async ({ page }) => {
  await page.route('/api/newsletter', r => r.fulfill({ status: 200 }));
});
"""

CLEAN = """
import { test, expect } from '@playwright/test';

test('registration rejects a duplicate email', async ({ page }) => {
  await mockApiError(page, '/users', 409, { errors: { email: ['is already taken'] } });
  await expect(page.locator('.msg')).toBeVisible();
});

test('an unknown article shows a message', async ({ page }) => {
  await page.route('/api/articles/some-slug', r => r.fulfill({ status: 404 }));
  await expect(page.locator('.msg')).toBeVisible();
});
"""


def run(suite_src):
    tmp = tempfile.mkdtemp(prefix="qaia-drift-")
    try:
        spec = os.path.join(tmp, "openapi.yml")
        io.open(spec, "w", encoding="utf-8", newline="\n").write(SPEC)
        tests = os.path.join(tmp, "tests")
        os.makedirs(tests)
        io.open(os.path.join(tests, "a.spec.ts"), "w", encoding="utf-8", newline="\n").write(suite_src)
        declared = D.load_spec(spec)
        if declared is None:
            # Sans PyYAML, `load_spec` rend None et le documente par un BROKEN sur stderr.
            # `compare(None, ...)` faisait alors `path in None` -> TypeError : le selfcheck
            # mourait sur une trace au lieu du code 2 qu'il est cense rapporter.
            print("BROKEN: PyYAML absent -- selfcheck non concluant (pip install pyyaml)",
                  file=sys.stderr)
            sys.exit(2)
        pairs, seen, all_status, files_read, files_skipped = D.scan_suite(tests)
        run.last_counts = (files_read, files_skipped, len(all_status))
        return D.compare(declared, pairs, seen, all_status)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- 1. path normalisation ------------------------------------------------------------------
check("an /api prefix is stripped", D.norm("/api/users"), "/users")
check("a template parameter collapses", D.norm("/api/articles/{slug}"), "/articles/{}")
check("a JS interpolation collapses", D.norm("/articles/${slug}"), "/articles/{}")
# A wildcard is a SEGMENT, not its absence: shaving `/profiles/*` to `/profiles` matched no
# template and produced a false `path-not-in-spec` on the founding target.
check("a wildcard segment becomes a parameter", D.norm("/api/profiles/*"), "/profiles/{}")
check("a query string is dropped", D.norm("/articles?limit=5"), "/articles")

# --- 2. concrete paths resolve to their template --------------------------------------------
declared = {"/articles/{}": {"200"}, "/users": {"201"}}
check("a concrete segment resolves", D.resolve("/articles/some-slug", declared), "/articles/{}")
check("an exact path resolves to itself", D.resolve("/users", declared), "/users")
check("a different arity does not resolve", D.resolve("/articles/a/b", declared), None)
check("an unknown path resolves to nothing", D.resolve("/newsletter", declared), None)

# --- 3. the drifting pair: each rule fires, exactly once -------------------------------------
found = run(DRIFTING)
by_rule = {}
for f in found:
    by_rule.setdefault(f["rule"], []).append(f)

check("the undeclared status is reported once", len(by_rule.get("undeclared-status", [])), 1)
if by_rule.get("undeclared-status"):
    f = by_rule["undeclared-status"][0]
    check("...on /users", f["path"], "/users")
    check("...for the 400 the suite mocks", f["status"], "400")

check("the unexercised status is reported once", len(by_rule.get("unexercised-status", [])), 1)
if by_rule.get("unexercised-status"):
    check("...and it is the 409 the spec promises", by_rule["unexercised-status"][0]["status"], "409")

check("the path absent from the spec is reported once", len(by_rule.get("path-not-in-spec", [])), 1)
if by_rule.get("path-not-in-spec"):
    check("...and it is /newsletter", by_rule["path-not-in-spec"][0]["path"], "/newsletter")

# `page.goto('/register')` is a page route, not an endpoint. Counting it made the block cite two
# paths, which the conservative pairing then skipped -- silencing the very finding above.
check("a navigation route is never reported as an endpoint",
      [f for f in found if f["path"] == "/register"], [])

# --- 4. the clean pair: nothing fires ---------------------------------------------------------
check("an agreeing spec and suite produce no finding", run(CLEAN), [])

# --- 5. un parse vide ne produit JAMAIS de verdict --------------------------------------------
#
# Trouve le 2026-08-24 en pointant cet outil sur du logiciel tiers. Un repertoire ne contenant
# AUCUN fichier de test lisible rendait trois `unexercised-status` affirmatifs : la regle est
# vraie et vide, l'outil ne mesure plus la suite mais sa propre cecite. Sur quatre projets
# etrangers, 11 constats sur 11 etaient de cette espece.
#
# Le refus vit dans `main()`, donc il se teste par la ligne de commande : le tester au niveau
# des fonctions aurait valide la logique de comparaison sans jamais toucher la garde.
import json as _json          # noqa: E402
import subprocess as _sp      # noqa: E402

_tmp5 = tempfile.mkdtemp()
try:
    _spec = os.path.join(_tmp5, "openapi.yml")
    io.open(_spec, "w", encoding="utf-8", newline="\n").write(SPEC)

    def _run_cli(tests_dir):
        out = os.path.join(_tmp5, "out.json")
        p = _sp.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "spec_suite_drift.py"),
                     "--spec", _spec, "--tests-dir", tests_dir, "--json", out],
                    capture_output=True, text=True)
        data = _json.load(io.open(out, encoding="utf-8")) if os.path.isfile(out) else None
        return p.returncode, data

    # (a) repertoire sans le moindre fichier de test
    _empty = os.path.join(_tmp5, "empty")
    os.makedirs(_empty)
    io.open(os.path.join(_empty, "README.md"), "w", encoding="utf-8").write("rien")
    code, data = _run_cli(_empty)
    check("un repertoire sans test rend UNCOMPARABLE", data and data["verdict"], "UNCOMPARABLE")
    check("...et AUCUN constat", data and data["findings"], [])
    check("...et un code de sortie distinct du vert comme du rouge", code, 3)
    # Le MOTIF, pas seulement le verdict. Les deux conditions du refus se recouvrent -- zero
    # fichier lu implique zero code reconnu -- si bien qu'une mutation neutralisant la premiere
    # survivait : la seconde rattrapait le cas et rendait le meme verdict sous un motif faux.
    # « Il n'y a pas de suite » et « la suite parle une langue que je ne lis pas » appellent deux
    # actions differentes chez le lecteur ; les confondre vide le refus de son utilite.
    check("...et le motif dit qu'il n'y avait AUCUN fichier lisible",
          bool(data and "aucun fichier de test lisible" in (data["uncomparableReason"] or "")),
          True)

    # (b) des fichiers de test que ce lecteur ne sait pas lire (Go, Python)
    _foreign = os.path.join(_tmp5, "foreign")
    os.makedirs(_foreign)
    io.open(os.path.join(_foreign, "api_test.go"), "w", encoding="utf-8").write(
        "package main\nfunc TestBan(t *testing.T) { assertStatus(t, resp, 400) }\n")
    code, data = _run_cli(_foreign)
    check("des tests dans un langage non lu rendent UNCOMPARABLE",
          data and data["verdict"], "UNCOMPARABLE")
    check("...et ils sont COMPTES comme ignores, pas passes sous silence",
          bool(data and data["counts"]["suite_files_skipped_unreadable"]), True)

    # (c) des fichiers lus mais dont aucune facon d'affirmer un statut n'est reconnue
    _idiom = os.path.join(_tmp5, "idiom")
    os.makedirs(_idiom)
    io.open(os.path.join(_idiom, "a.spec.ts"), "w", encoding="utf-8").write(
        "test('ban a user', async () => {\n"
        "  const res = await api.post('/v1/ban');\n"
        "  assertOk(res);\n"
        "});\n")
    code, data = _run_cli(_idiom)
    check("un fichier lu sans aucun code HTTP reconnu rend UNCOMPARABLE",
          data and data["verdict"], "UNCOMPARABLE")
    check("...et le compte de fichiers LUS le prouve",
          bool(data and data["counts"]["suite_files_read"]), True)
    check("...et le motif dit que c'est la FACON D'AFFIRMER qui n'est pas reconnue",
          bool(data and "AUCUN code HTTP reconnu" in (data["uncomparableReason"] or "")), True)

    # (d) contre-epreuve : une suite lisible doit toujours etre comparee, sinon la garde a
    # simplement eteint l'outil au lieu de le rendre honnete.
    _ok = os.path.join(_tmp5, "ok")
    os.makedirs(_ok)
    io.open(os.path.join(_ok, "a.spec.ts"), "w", encoding="utf-8", newline="\n").write(DRIFTING)
    code, data = _run_cli(_ok)
    check("une suite lisible est bel et bien comparee", data and data["verdict"], "compared")
    check("...et rend ses ecarts", bool(data and data["findings"]), True)
finally:
    shutil.rmtree(_tmp5, ignore_errors=True)

if failures:
    print("selfcheck_spec_suite_drift: %d FAILURE(S)\n" % len(failures))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("selfcheck_spec_suite_drift: ok")
