# -*- coding: utf-8 -*-
"""Recupere des cahiers Gherkin ECRITS PAR D'AUTRES, tous runners confondus.

Le scan des jours precedents ne visait que Playwright -- une skill sur trente-sept.
`testbook-validate` affirme auditer « n'importe quel cahier Gherkin, genere par QAIA ou non »,
et `structural_score.py` le note. Cette affirmation n'a jamais ete eprouvee sur du Gherkin
etranger : la population est de **624 640 fichiers** sur GitHub, dans toutes les langues et
tous les runners (Cucumber, SpecFlow, Behave, pytest-bdd, godog, Behat).
"""
import json, os, re, sys, time, urllib.request, urllib.parse

TOK = os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]
DEST = sys.argv[1]
os.makedirs(DEST, exist_ok=True)


def api(u):
    try:
        r = urllib.request.Request(u, headers={"Authorization": "Bearer " + TOK,
                                               "Accept": "application/vnd.github+json"})
        return json.load(urllib.request.urlopen(r, timeout=45))
    except Exception as e:
        return {"_err": str(e)}


def raw(repo, br, p):
    try:
        u = "https://raw.githubusercontent.com/%s/%s/%s" % (repo, br, urllib.parse.quote(p))
        return urllib.request.urlopen(
            urllib.request.Request(u, headers={"Authorization": "Bearer " + TOK}),
            timeout=45).read().decode("utf-8", "replace")
    except Exception:
        return None


# On cherche des depots reels et varies plutot qu'une seule requete : le lot precedent
# venait d'UNE recherche, et ses 2 % de precision jugeaient autant l'echantillon que l'outil.
QUERIES = [
    '"Scenario Outline" "Examples" extension:feature',
    '"Background:" "Given" extension:feature',
    '"Esquema del escenario" extension:feature',
    '"Szenario" extension:feature',
]

candidates = {}
for q in QUERIES:
    d = api("https://api.github.com/search/code?q=" + urllib.parse.quote(q) + "&per_page=50")
    for it in d.get("items", []):
        repo = it["repository"]["full_name"]
        candidates.setdefault(repo, set()).add(it["path"])
    time.sleep(2.5)

print("depots candidats : %d" % len(candidates))

kept = []
for repo, paths in sorted(candidates.items()):
    info = api("https://api.github.com/repos/" + repo)
    if "_err" in info or info.get("archived") or info.get("fork"):
        continue
    tree = api("https://api.github.com/repos/%s/git/trees/%s?recursive=1"
               % (repo, info["default_branch"]))
    if "_err" in tree or tree.get("truncated"):
        continue
    feats = [t["path"] for t in tree.get("tree", [])
             if t["type"] == "blob" and t["path"].endswith(".feature")
             and "node_modules" not in t["path"]]
    if len(feats) < 4:            # un cahier d'un seul fichier n'enseigne rien
        continue
    d = os.path.join(DEST, repo.replace("/", "_"))
    os.makedirs(d, exist_ok=True)
    got = 0
    for p in feats[:25]:
        t = raw(repo, info["default_branch"], p)
        if t is None:
            continue
        with open(os.path.join(d, p.replace("/", "__")), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(t)
        got += 1
    if got:
        kept.append({"repo": repo, "stars": info["stargazers_count"],
                     "lang": info.get("language"), "features": len(feats), "fetched": got})
        print("  %-46s %5d * %-12s %3d .feature" % (repo[:44], info["stargazers_count"],
                                                    info.get("language") or "-", len(feats)))
    if len(kept) >= 18:
        break
    time.sleep(0.6)

json.dump(kept, open(os.path.join(DEST, "_batch.json"), "w"), indent=1)
print("\nretenus : %d depots, %d fichiers .feature" % (len(kept), sum(k["fetched"] for k in kept)))
