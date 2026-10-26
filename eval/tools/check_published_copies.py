#!/usr/bin/env python3
"""Fail when a skill published to an external directory drifts from the skill it was derived from.

Why this exists. QASkills.sh and directories like it take a **single self-contained SKILL.md**.
QAIA's skills are deliberately not that: three sprints were spent moving long reasoning into
`references/` so the SKILL.md stays readable. Publishing therefore means shipping a *derived*
artifact, and a derived artifact with nothing watching it is a copy that silently stops matching
its original — the exact dette this project just closed for `OUTPUT-CONTRACT.md` by shipping it
into every plugin **with a CI job keeping the copies identical**.

The copies here cannot be byte-identical: they are adaptations, self-contained on purpose, with
different frontmatter and no `references/`. So identity is the wrong check. What is checkable is
**provenance**: each published copy records the sha256 of every source file it was derived from.
When a source changes, the recorded hash no longer matches and this fails — forcing whoever
changed the skill to look at the copy and decide, rather than letting the two drift apart
unnoticed for months.

Refreshing after a deliberate change is one command:

    python eval/tools/check_published_copies.py --update

which rewrites the recorded hashes. That command is the decision point: running it means "I have
looked at the published copy and it still says the truth", and the diff it produces is reviewable.

Exit codes: 0 all copies current, 1 at least one source changed since its copy was reviewed,
2 the manifest itself is missing or malformed.
"""

import hashlib
import io
import json
import os
import sys

CR, LF = chr(13), chr(10)
CRLF = CR + LF

MANIFEST = os.path.join("docs", "outreach", "qaskills", "SOURCES.json")


def sha256(path):
    """Hash the *normalised* text, not the bytes.

    A raw byte hash is not portable here: git rewrites line endings on checkout under Windows
    (`core.autocrlf`), so the same content hashes differently before and after a checkout and the
    check fires on a file nobody touched. Found by testing the check's own recovery path rather
    than only its failure path — it detected the drift correctly and then refused to clear.
    """
    text = io.open(path, encoding="utf-8", errors="replace").read()
    text = text.replace(CRLF, LF).replace(CR, LF)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load():
    if not os.path.isfile(MANIFEST):
        print("::error::%s is missing — published copies have no recorded provenance" % MANIFEST)
        sys.exit(2)
    try:
        return json.load(io.open(MANIFEST, encoding="utf-8"))
    except ValueError as exc:
        print("::error::%s is not valid JSON: %s" % (MANIFEST, exc))
        sys.exit(2)


def main(argv):
    update = "--update" in argv
    data = load()
    stale, missing = [], []

    retired = []
    for entry in data["published"]:
        copy = entry["copy"]
        # Une copie EN LIGNE dont la skill source a ete supprimee du depot (2026-10-26). Elle ne
        # peut plus deriver de rien, et la retirer de l'annuaire est un geste externe que ce
        # controle n'a pas a decider. Elle est donc ANNONCEE a chaque passage, jamais tue :
        # « non maintenue » doit rester visible tant que la copie est servie.
        if entry.get("source_retired"):
            retired.append("%s -- source retiree le %s, copie non maintenue (%s)"
                           % (copy, entry["source_retired"], entry.get("state")))
            continue
        if not os.path.isfile(copy):
            missing.append("%s is declared in the manifest and does not exist" % copy)
            continue
        for src in entry["derived_from"]:
            path = src["path"]
            if not os.path.isfile(path):
                missing.append("%s (source of %s) does not exist" % (path, copy))
                continue
            actual = sha256(path)
            if actual != src["sha256"]:
                if update:
                    src["sha256"] = actual
                else:
                    stale.append((copy, path, src["sha256"], actual))

    for m in missing:
        print("::error::%s" % m)
    for r in retired:
        print("::warning::%s" % r)

    if update:
        io.open(MANIFEST, "w", encoding="utf-8", newline="\n").write(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print("Recorded hashes refreshed. Review the published copies before committing:")
        for entry in data["published"]:
            print("  %s" % entry["copy"])
        return 2 if missing else 0

    if stale:
        print("::error::%d published copy/copies may no longer match their source." % len(stale))
        for copy, path, was, now in stale:
            print("  %s" % copy)
            print("    derived from %s" % path)
            print("    recorded %s..., now %s..." % (was[:12], now[:12]))
        print("")
        print("The source skill changed after the published copy was last reviewed. Read the")
        print("change, decide whether the copy still says the truth, edit it if not, then run:")
        print("    python eval/tools/check_published_copies.py --update")
        return 1

    if missing:
        return 2

    print("OK: %d published copy/copies current with their sources, %d retired (unmaintained)"
          % (len(data["published"]) - len(retired), len(retired)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
