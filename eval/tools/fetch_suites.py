#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recupere des suites Playwright ECRITES PAR D'AUTRES, depuis une liste de depots NOMMES.

Pendant du `fetch_corpus.py` du Gherkin, pour l'etage automatisation. Meme principe, meme
raison : la campagne du 2026-08-09 avait scanne 27 depots sans jamais conserver de quoi
rejouer la mesure, et son fetcher partait de requetes de recherche GitHub -- donc d'un
resultat qui change d'un jour a l'autre.

Une suite est prise ENTIERE (le repertoire qui contient les specs, pas seulement les
`*.spec.*`) : trois faux constats de la campagne d'origine venaient d'un fichier d'aide absent
du perimetre de scan, ce qui etait une faute de methode et non de l'outil.

Usage: python3 fetch_suites.py <repos.txt|repo1,repo2,...> <dest_dir>
Env:   GITHUB_PERSONAL_ACCESS_TOKEN (optionnel)
"""
import hashlib
import json
import os
import posixpath
import sys
import urllib.error
import urllib.parse
import urllib.request

TOK = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
SPEC_SUFFIXES = (".spec.ts", ".spec.js", ".spec.mjs", ".spec.tsx",
                 ".test.ts", ".test.js", ".e2e.ts")
SUPPORT_SUFFIXES = (".ts", ".js", ".mjs", ".cjs", ".tsx")
MAX_FILES = 60


def _headers():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "qaia-fetch-suites"}
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


def is_playwright_spec(path, text):
    """Une suite Playwright, pas n'importe quel fichier de test.

    Le filtre par extension seul ramene du Jest et du Vitest, que ce scoreur ne sait pas lire :
    il les aurait notes quand meme, et un score sur un materiau qu'on ne sait pas lire est
    fabrique. On exige un import Playwright dans le fichier.
    """
    return ("@playwright/test" in text or "playwright-core" in text
            or "from 'playwright'" in text or 'from "playwright"' in text)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    arg, dest = sys.argv[1], sys.argv[2]
    if os.path.isfile(arg):
        repos = [l.strip() for l in open(arg, encoding="utf-8")
                 if l.strip() and not l.startswith("#")]
    else:
        repos = [r.strip() for r in arg.split(",") if r.strip()]
    os.makedirs(dest, exist_ok=True)

    manifest = {"_retrieved": None, "_why": "suites Playwright ecrites par d'autres, pour "
                                            "mesurer le barème d'automatisation hors de sa "
                                            "propre production", "repos": []}
    for repo in repos:
        info = api("https://api.github.com/repos/" + repo)
        if "_err" in info:
            print("  %-40s INDISPONIBLE (%s)" % (repo[:38], info["_err"]))
            manifest["repos"].append({"repo": repo, "status": "unavailable"})
            continue
        branch = info["default_branch"]
        tree = api("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (repo, branch))
        if "_err" in tree:
            print("  %-40s ARBRE INDISPONIBLE" % repo[:38])
            manifest["repos"].append({"repo": repo, "status": "unavailable"})
            continue
        blobs = [t["path"] for t in tree.get("tree", [])
                 if t.get("type") == "blob" and "node_modules" not in t["path"]]
        specs = [p for p in blobs if p.endswith(SPEC_SUFFIXES)]
        if not specs:
            print("  %-40s aucune spec" % repo[:38])
            manifest["repos"].append({"repo": repo, "status": "no-specs"})
            continue
        # Le repertoire qui porte le plus de specs : c'est la suite. On prend tout ce qu'il
        # contient, fichiers d'aide compris.
        counts = {}
        for p in specs:
            counts[posixpath.dirname(p)] = counts.get(posixpath.dirname(p), 0) + 1
        suite_dir = max(counts, key=lambda d: counts[d])
        wanted = [p for p in blobs
                  if posixpath.dirname(p) == suite_dir and p.endswith(SUPPORT_SUFFIXES)]
        # Les objets de page vivent souvent un cran a cote (`pages/`, `fixtures/`).
        parent = posixpath.dirname(suite_dir)
        for sub in ("pages", "fixtures", "support", "helpers", "po"):
            wanted += [p for p in blobs
                       if p.startswith(posixpath.join(parent, sub) + "/")
                       and p.endswith(SUPPORT_SUFFIXES)]
        wanted = sorted(set(wanted))[:MAX_FILES]

        outdir = os.path.join(dest, repo.replace("/", "_"))
        got, texts, pw = 0, [], 0
        for p in wanted:
            t = raw(repo, branch, p)
            if t is None:
                continue
            os.makedirs(os.path.join(outdir, posixpath.dirname(
                posixpath.relpath(p, suite_dir)).replace("..", "_up")), exist_ok=True)
            flat = posixpath.relpath(p, suite_dir).replace("../", "_up_").replace("/", "__")
            with open(os.path.join(outdir, flat), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(t)
            texts.append(t)
            got += 1
            if p.endswith(SPEC_SUFFIXES) and is_playwright_spec(p, t):
                pw += 1
        digest = hashlib.sha256("".join(texts).encode("utf-8")).hexdigest()[:16]
        if pw == 0:
            print("  %-40s %3d fichiers, AUCUNE spec Playwright -- ecarte" % (repo[:38], got))
            manifest["repos"].append({"repo": repo, "status": "not-playwright",
                                      "files": got})
            continue
        print("  %-40s %3d fichiers, %2d spec(s) Playwright  sha %s"
              % (repo[:38], got, pw, digest))
        manifest["repos"].append({"repo": repo, "status": "ok", "branch": branch,
                                  "suite_dir": suite_dir, "files": got,
                                  "playwright_specs": pw, "sha256": digest,
                                  "stars": info.get("stargazers_count")})

    ok = [r for r in manifest["repos"] if r["status"] == "ok"]
    manifest["_files"] = sum(r["files"] for r in ok)
    json.dump(manifest, open(os.path.join(dest, "_manifest.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print("\n%d suite(s) Playwright retenue(s) sur %d depots, %d fichiers"
          % (len(ok), len(repos), manifest["_files"]))


if __name__ == "__main__":
    main()
