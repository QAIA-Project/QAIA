#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstitue localement un corpus etranger gele, a partir de son manifeste.

Le corpus de 244 cahiers Gherkin de `eval/gherkin-external-2026-08-09/` n'a jamais ete
conserve : seul son manifeste l'a ete (15 depots, un compte et un sha256 par depot). Le
fetcher d'origine partait de requetes de recherche GitHub, dont le resultat change d'un jour
a l'autre -- il ne pouvait donc pas reconstruire deux fois le meme corpus.

Ce script part du manifeste, pas d'une recherche : pour chacun des depots NOMMES, il reprend
les N premiers `.feature` de la branche par defaut, dans l'ordre de l'arbre git. C'est
reproductible tant que l'amont ne bouge pas, et quand l'amont bouge le script le DIT au lieu
de rendre un corpus different sous le meme nom.

La metrique n1 du projet (taux de PASS sur du materiau que QAIA n'a pas ecrit) se mesure sur
ce corpus : sans reconstruction possible, elle n'etait pas verifiable par un tiers.

Usage: python3 fetch_corpus.py <manifest.json> <dest_dir>
Env:   GITHUB_PERSONAL_ACCESS_TOKEN (optionnel -- sans lui, quota anonyme 60 req/h)
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

TOK = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()


def _headers():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "qaia-fetch-corpus"}
    if TOK:
        h["Authorization"] = "Bearer " + TOK
    return h


def api(url):
    try:
        req = urllib.request.Request(url, headers=_headers())
        return json.load(urllib.request.urlopen(req, timeout=45))
    except urllib.error.HTTPError as exc:
        return {"_err": "HTTP %s" % exc.code}
    except Exception as exc:  # reseau, DNS, timeout
        return {"_err": str(exc)}


def raw(repo, branch, path):
    url = "https://raw.githubusercontent.com/%s/%s/%s" % (repo, branch, urllib.parse.quote(path))
    try:
        req = urllib.request.Request(url, headers=_headers())
        return urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
    except Exception:
        return None


def repo_digest(texts):
    """Empreinte d'un depot : sha256 de ses fichiers concatenes, tronque a 16 hex.

    La methode d'origine n'etait pas documentee ; celle-ci l'est. Une empreinte qui ne
    correspond pas au manifeste n'est donc PAS la preuve que l'amont a bouge -- elle peut
    aussi signifier que les deux methodes different. Le script rapporte les deux et ne
    conclut pas a la place du lecteur.
    """
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
    return h.hexdigest()[:16]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    manifest_path, dest = sys.argv[1], sys.argv[2]
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    repos = manifest["repos"]
    os.makedirs(dest, exist_ok=True)

    report = {"manifest": os.path.basename(manifest_path), "repos": [],
              "files_expected": manifest.get("_files"), "files_fetched": 0}
    for entry in repos:
        repo, expected = entry["repo"], entry["features"]
        info = api("https://api.github.com/repos/" + repo)
        if "_err" in info:
            print("  %-46s INDISPONIBLE (%s)" % (repo[:44], info["_err"]))
            report["repos"].append({"repo": repo, "status": "unavailable",
                                    "detail": info["_err"]})
            continue
        branch = info["default_branch"]
        tree = api("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (repo, branch))
        if "_err" in tree:
            print("  %-46s ARBRE INDISPONIBLE (%s)" % (repo[:44], tree["_err"]))
            report["repos"].append({"repo": repo, "status": "unavailable",
                                    "detail": tree["_err"]})
            continue
        feats = [t["path"] for t in tree.get("tree", [])
                 if t.get("type") == "blob" and t["path"].endswith(".feature")
                 and "node_modules" not in t["path"]]
        # Le fetcher d'origine plafonnait a 25 fichiers par depot. Le manifeste enregistre le
        # nombre TOTAL vu a l'epoque, pas le nombre recupere -- pour les depots au-dela de 25,
        # `expected` et le nombre de fichiers du corpus ne coincident donc pas. On reprend le
        # meme plafond pour reconstituer le meme corpus, et on nomme l'ecart.
        take = feats[:25]
        outdir = os.path.join(dest, repo.replace("/", "_"))
        os.makedirs(outdir, exist_ok=True)
        texts, got = [], 0
        for p in take:
            t = raw(repo, branch, p)
            if t is None:
                continue
            with open(os.path.join(outdir, p.replace("/", "__")), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(t)
            texts.append(t)
            got += 1
        digest = repo_digest(texts)
        # La derive se lit sur l'EMPREINTE, pas sur un compte. Le champ `features` du manifeste
        # enregistre le nombre RECUPERE (plafonne a 25), pas le nombre total vu a l'epoque : le
        # comparer au total d'aujourd'hui faisait annoncer « +205 » sur un depot dont les 25
        # fichiers sont rigoureusement identiques. Comparer deux grandeurs de definitions
        # differentes est la faute que ce depot repete ; ici elle est attrapee par le fait que
        # 12 empreintes sur 15 coincidaient malgre une derive annoncee sur 7.
        drift = "identique" if digest == entry.get("sha256") else "A BOUGE"
        print("  %-46s %3d fichiers  %-9s  sha %s" % (repo[:44], got, drift, digest))
        report["repos"].append({
            "repo": repo, "status": "ok", "branch": branch,
            "features_now": len(feats), "features_at_freeze": expected,
            "fetched": got, "digest_now": digest,
            "digest_at_freeze": entry.get("sha256"),
        })
        report["files_fetched"] += got

    json.dump(report, open(os.path.join(dest, "_fetch-report.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    ok = [r for r in report["repos"] if r["status"] == "ok"]
    moved = [r for r in ok if r["digest_now"] != r["digest_at_freeze"]]
    print("\n%d depots sur %d, %d fichiers recuperes (manifeste : %s)"
          % (len(ok), len(repos), report["files_fetched"], report["files_expected"]))
    print("%d empreinte(s) sur %d identiques au gel" % (len(ok) - len(moved), len(ok)))
    if moved:
        print("%d depot(s) ont bouge depuis le gel -- le corpus n'est PAS strictement celui "
              "de la mesure d'origine : %s" % (len(moved), ", ".join(r["repo"] for r in moved)))


if __name__ == "__main__":
    main()
