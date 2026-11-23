#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrouve, pour chaque depot d'un manifeste de corpus, le commit qui porte son empreinte.

Le manifeste du 2026-08-09 gelait une empreinte par depot, pas un commit : des que l'amont
bouge, `fetch_corpus.py` reconstruit un autre corpus sous le meme nom (#119, 6 depots sur 15
le 2026-11-23). Ce script cherche, commit par commit sur la branche par defaut, celui dont
les N premiers `.feature` (N = `features` du manifeste, plafonne a 25) redonnent EXACTEMENT l'empreinte du gel, et l'ecrit dans le
manifeste (`commit`). `fetch_corpus.py` lit alors ce commit au lieu de la branche.

Il n'invente rien : un depot dont aucun commit candidat ne redonne l'empreinte reste sans
`commit`, et le script le dit. Il ne declare jamais « epingle » ce qu'il n'a pas verifie.

Recherche : les commits anterieurs a la date du gel (les plus recents d'abord), puis les
posterieurs (les plus anciens d'abord) -- un gel peut avoir lu une branche deja en avance
sur la date inscrite. Plafond de candidats par depot : --max (defaut 30).

Usage: python3 pin_corpus.py <manifest.json> [--freeze-date 2026-08-10] [--max 30] [--write]
Sans --write, le script rapporte et ne modifie rien.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_corpus import api, raw, repo_digest  # noqa: E402


def features_at(repo, ref):
    tree = api("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (repo, ref))
    if "_err" in tree:
        return None
    return [t["path"] for t in tree.get("tree", [])
            if t.get("type") == "blob" and t["path"].endswith(".feature")
            and "node_modules" not in t["path"]]


def digest_at(repo, ref, n, cache):
    """Empreinte des n premiers `.feature` au commit `ref` -- n vient du manifeste (#119)."""
    feats = features_at(repo, ref)
    if feats is None:
        return None
    texts = []
    for p in feats[:min(25, n)]:
        key = (ref, p)
        if key not in cache:
            cache[key] = raw(repo, ref, p)
        if cache[key] is not None:
            texts.append(cache[key])
    return repo_digest(texts)


def commits(repo, branch, **params):
    q = "&".join("%s=%s" % kv for kv in params.items())
    out = api("https://api.github.com/repos/%s/commits?sha=%s&per_page=100&%s" % (repo, branch, q))
    return [] if isinstance(out, dict) else [c["sha"] for c in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--freeze-date", default="2026-08-10T00:00:00Z")
    ap.add_argument("--max", type=int, default=30)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if "T" not in a.freeze_date:
        a.freeze_date += "T00:00:00Z"

    manifest = json.load(open(a.manifest, encoding="utf-8"))
    pinned, missing = 0, []
    for entry in manifest["repos"]:
        repo, want = entry["repo"], entry.get("sha256")
        if entry.get("commit"):
            print("  %-46s deja epingle  %s" % (repo[:44], entry["commit"][:12]))
            pinned += 1
            continue
        info = api("https://api.github.com/repos/" + repo)
        if "_err" in info:
            print("  %-46s INDISPONIBLE (%s)" % (repo[:44], info["_err"]))
            missing.append(repo)
            continue
        branch = info["default_branch"]
        before = commits(repo, branch, until=a.freeze_date)
        after = list(reversed(commits(repo, branch, since=a.freeze_date)))
        found, tried, cache = None, 0, {}
        for sha in before[: a.max] + after[: a.max]:
            tried += 1
            if digest_at(repo, sha, entry["features"], cache) == want:
                found = sha
                break
        if found:
            entry["commit"] = found
            pinned += 1
            print("  %-46s epingle       %s  (%d candidat(s))" % (repo[:44], found[:12], tried))
        else:
            missing.append(repo)
            print("  %-46s INTROUVABLE   aucun des %d commits ne redonne %s"
                  % (repo[:44], tried, want))

    print("\n%d depot(s) sur %d epingle(s) a un commit verifie" % (pinned, len(manifest["repos"])))
    if missing:
        print("sans commit : " + ", ".join(missing))
    if a.write:
        with open(a.manifest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(manifest, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print("manifeste reecrit : " + a.manifest)
    raise SystemExit(0 if not missing else 1)


if __name__ == "__main__":
    main()
