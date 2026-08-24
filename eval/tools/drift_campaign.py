#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pointe `spec_suite_drift.py` sur des projets ECRITS PAR D'AUTRES et rend ce qu'il suppose.

## Pourquoi

`eval/lint-external-2026-08-09/REPORT.md` se termine par : *« aucun [des dix autres outils]
n'a ete essaye sur du materiau etranger »*. `spec_suite_drift.py` est le seul scoreur du noyau
qui reste dans ce cas -- il est ne d'un projet tiers (`realworld`), mais d'UN SEUL, celui qui a
servi a l'ecrire. Un outil valide sur l'exemple qui l'a fait naitre ne prouve rien.

Un outil qui n'a jamais lu que sa propre production ne sait pas ce qu'il suppose. Cette campagne
lui donne de quoi le decouvrir : des specifications OpenAPI reelles, avec les suites de tests
reelles qui pretendent les couvrir.

## Ce que la campagne compte comme un resultat

Deux choses, et elles sont d'egale valeur :

  - un **constat de derive** dans le projet cible (une promesse non eprouvee, un code attendu
    que la specification ne declare pas) ;
  - un **defaut de l'outil**, revele parce que le materiau ne ressemble pas au sien.

La campagne du 2026-08-09 a trouve trois defauts d'outil pour deux constats reels. C'est le
resultat attendu, pas un echec.

Usage: python3 drift_campaign.py <repos.txt|repo1,repo2,...> <work_dir>
"""
import json
import os
import posixpath
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TOK = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
SPEC_NAMES = ("openapi.yaml", "openapi.yml", "openapi.json", "swagger.yaml", "swagger.yml",
              "swagger.json", "api.yaml", "api.yml", "oas.yaml", "oas.yml", "spec.yaml")
TEST_SUFFIXES = (".spec.ts", ".spec.js", ".test.ts", ".test.js", ".test.py", "_test.py",
                 "_test.go", ".test.rb", ".spec.rb", ".e2e.ts", ".test.java")
MAX_TEST_FILES = 80


def _headers():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "qaia-drift-campaign"}
    if TOK:
        h["Authorization"] = "Bearer " + TOK
    return h


def api(url):
    try:
        return json.load(urllib.request.urlopen(
            urllib.request.Request(url, headers=_headers()), timeout=45))
    except urllib.error.HTTPError as exc:
        return {"_err": "HTTP %s" % exc.code}
    except Exception as exc:
        return {"_err": str(exc)}


def raw(repo, branch, path):
    url = "https://raw.githubusercontent.com/%s/%s/%s" % (repo, branch, urllib.parse.quote(path))
    try:
        return urllib.request.urlopen(
            urllib.request.Request(url, headers=_headers()), timeout=45
        ).read().decode("utf-8", "replace")
    except Exception:
        return None


def pick(repo):
    """Rend (branche, chemin_de_spec, [chemins_de_tests]) ou None si le couple n'existe pas.

    Un projet sans suite de tests n'est pas un echec de l'outil : il n'y a rien a comparer. On
    l'ecarte en le DISANT, plutot que de le faire disparaitre du compte -- un denominateur qui
    perd ses exclusions silencieusement transforme « 2 constats sur 3 projets » en « 2 sur 20 ».
    """
    info = api("https://api.github.com/repos/" + repo)
    if "_err" in info:
        return None, "depot indisponible (%s)" % info["_err"]
    branch = info["default_branch"]
    tree = api("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (repo, branch))
    if "_err" in tree:
        return None, "arbre indisponible"
    if tree.get("truncated"):
        return None, "arbre tronque par l'API -- perimetre incertain, ecarte"
    blobs = [t["path"] for t in tree.get("tree", [])
             if t.get("type") == "blob" and "node_modules" not in t["path"]]
    specs = [p for p in blobs if posixpath.basename(p).lower() in SPEC_NAMES]
    if not specs:
        return None, "aucune specification OpenAPI"
    tests = [p for p in blobs if p.endswith(TEST_SUFFIXES)]
    if not tests:
        return None, "aucun fichier de test"
    # La spec la moins profonde : c'est en general le contrat du projet, pas celui d'un exemple.
    spec = sorted(specs, key=lambda p: (p.count("/"), len(p)))[0]
    return (branch, spec, sorted(tests)[:MAX_TEST_FILES]), None


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    arg, work = sys.argv[1], sys.argv[2]
    repos = ([l.strip() for l in open(arg, encoding="utf-8")
              if l.strip() and not l.startswith("#")]
             if os.path.isfile(arg) else
             [r.strip() for r in arg.split(",") if r.strip()])
    os.makedirs(work, exist_ok=True)

    report = {"repos": [], "excluded": [], "tool_errors": []}
    for repo in repos:
        picked, why = pick(repo)
        if picked is None:
            print("  %-42s ecarte : %s" % (repo[:40], why))
            report["excluded"].append({"repo": repo, "why": why})
            continue
        branch, spec_path, test_paths = picked
        base = os.path.join(work, repo.replace("/", "_"))
        tdir = os.path.join(base, "tests")
        os.makedirs(tdir, exist_ok=True)
        spec_text = raw(repo, branch, spec_path)
        if spec_text is None:
            report["excluded"].append({"repo": repo, "why": "specification illisible"})
            continue
        spec_file = os.path.join(base, "spec" + os.path.splitext(spec_path)[1])
        with open(spec_file, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(spec_text)
        got = 0
        for p in test_paths:
            t = raw(repo, branch, p)
            if t is None:
                continue
            with open(os.path.join(tdir, p.replace("/", "__")), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(t)
            got += 1
        if not got:
            report["excluded"].append({"repo": repo, "why": "aucun test telechargeable"})
            continue

        out_json = os.path.join(base, "drift.json")
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "spec_suite_drift.py"),
             "--spec", spec_file, "--tests-dir", tdir, "--json", out_json],
            capture_output=True, text=True)
        entry = {"repo": repo, "branch": branch, "spec": spec_path, "tests_fetched": got,
                 "exit": proc.returncode}
        if os.path.isfile(out_json):
            try:
                data = json.load(open(out_json, encoding="utf-8"))
                fnd = data.get("findings", data.get("drift", []))
                entry["findings"] = len(fnd)
                kinds = {}
                for f in fnd:
                    k = f.get("kind", f.get("rule", "?"))
                    kinds[k] = kinds.get(k, 0) + 1
                entry["by_kind"] = kinds
            except Exception as exc:
                entry["parse_error"] = str(exc)
        else:
            # PAS de constats == 0 : l'outil n'a rien rendu du tout. Confondre les deux est la
            # faute que cette campagne existe pour trouver ailleurs ; elle ne va pas la commettre
            # sur elle-meme.
            entry["findings"] = None
            entry["stderr"] = (proc.stderr or "")[-400:]
            report["tool_errors"].append({"repo": repo, "exit": proc.returncode,
                                          "stderr": (proc.stderr or "")[-400:]})
        report["repos"].append(entry)
        print("  %-42s %3d tests, exit=%s, constats=%s %s"
              % (repo[:40], got, proc.returncode, entry.get("findings"),
                 entry.get("by_kind", "")))

    json.dump(report, open(os.path.join(work, "_campaign.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    ran = [r for r in report["repos"] if r.get("findings") is not None]
    print("\n%d depot(s) vises, %d ecarte(s), %d analyse(s), %d erreur(s) d'outil"
          % (len(repos), len(report["excluded"]), len(ran), len(report["tool_errors"])))
    if ran:
        print("constats totaux : %d" % sum(r["findings"] for r in ran))


if __name__ == "__main__":
    main()
