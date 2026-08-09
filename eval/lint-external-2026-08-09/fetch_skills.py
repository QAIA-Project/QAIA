# -*- coding: utf-8 -*-
"""Recupere des SKILL.md ecrites par d'autres, pour eprouver lint_skills.py sur du materiau etranger.

Deux outils sur deux, pointes ailleurs que sur leur propre production, portaient le meme defaut :
des regles de convention maison appliquees a du materiau qui ne les a jamais adoptees.
`lint_skills.py` est le seul des controles restants dont l'entree soit parametrable -- les autres
gardent ce depot par construction et ne peuvent pas prendre d'entree etrangere.
"""
import json, os, sys, time, urllib.request, urllib.parse

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


cand = {}
for q in ['filename:SKILL.md "description:"', '"name:" "description:" path:skills filename:SKILL.md']:
    d = api("https://api.github.com/search/code?q=" + urllib.parse.quote(q) + "&per_page=60")
    for it in d.get("items", []):
        cand.setdefault(it["repository"]["full_name"], set()).add(it["path"])
    time.sleep(2.5)

print("depots candidats : %d" % len(cand))
kept = []
for repo in sorted(cand):
    info = api("https://api.github.com/repos/" + repo)
    if "_err" in info or info.get("fork") or info.get("archived"):
        continue
    tree = api("https://api.github.com/repos/%s/git/trees/%s?recursive=1"
               % (repo, info["default_branch"]))
    if "_err" in tree or tree.get("truncated"):
        continue
    sk = [t["path"] for t in tree.get("tree", [])
          if t["type"] == "blob" and t["path"].endswith("SKILL.md")]
    if len(sk) < 3:
        continue
    got = 0
    for p in sk[:20]:
        t = raw(repo, info["default_branch"], p)
        if not t:
            continue
        # lint_skills attend une arborescence <name>/SKILL.md
        name = p.replace("/SKILL.md", "").split("/")[-1] or ("s%d" % got)
        d2 = os.path.join(DEST, repo.replace("/", "_"), name)
        os.makedirs(d2, exist_ok=True)
        with open(os.path.join(d2, "SKILL.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(t)
        got += 1
    if got:
        kept.append({"repo": repo, "stars": info["stargazers_count"], "skills": len(sk),
                     "fetched": got})
        print("  %-46s %5d * %3d SKILL.md" % (repo[:44], info["stargazers_count"], len(sk)))
    if len(kept) >= 12:
        break
    time.sleep(0.5)

json.dump(kept, open(os.path.join(DEST, "_batch.json"), "w"), indent=1)
print("\nretenus : %d depots, %d SKILL.md" % (len(kept), sum(k["fetched"] for k in kept)))
