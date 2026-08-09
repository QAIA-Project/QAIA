#!/usr/bin/env python3
"""Lint every SKILL.md against the skill-authoring norm and this project's own rules.

Why this exists. The 2026-07-31 cold-read review by four business personas (Directeur QA,
Automaticien expert, Lead QA, PM/PO) scored the 29 skills on sense, clarity, size and format.
Sense came out at 2.87/3 — nobody struggles to understand *what* a skill does. Clarity came out
at 2.09 with ten skills at or below 1.75: the catalogue explains itself well and executes badly.
Several of the defects behind that gap are mechanical, and a mechanical defect that is only ever
caught by a human review comes back the next time nobody reviews.

So: the checks below are the ones a machine can decide. Everything requiring judgement — is this
instruction actually followable, is this the right technique — stays with human and LLM review,
and this tool deliberately says nothing about it.

FAIL (exit 1) — objectively wrong, blocks CI:
  - frontmatter missing, unterminated, or `name` not matching the directory
  - description missing, or with no trigger clause: the description is the whole triggering
    mechanism, and one that only says what the skill *does* leaves the model no reason to invoke
    it. Under-triggering is the dominant failure mode, so a skill with no "use when…" is
    effectively unreachable outside a scripted journey.
  - body over 500 lines (the authoring norm's ceiling — past it, split into references/ with a
    pointer rather than trimming content)
  - an unconditional `= done` on a journey step: a validation gate that writes itself done is
    the exact bypass the shared contract's rule 3 exists to prevent.

WARN (exit 0, printed) — worth knowing, not worth blocking:
  - density over 150 characters per line. The review's sharpest finding: size scores correlate
    with density, not length. The best-rated skills sit between 66 and 100 c/line; the worst
    between 150 and 245. `us-ingest` is 31 lines long and still unreadable — it is compacted,
    not long. Density is a smell, not a defect, so it warns.
  - description outside 120-600 characters (thin ones under-trigger, long ones dilute)
  - internal codes (D125, Q35, #41) and campaign dates in the body. All four personas asked for
    this, unanimously — but it is a readability debt, not a correctness one.

Usage:
  python eval/tools/lint_skills.py [--strict] [path ...]
    --strict  promote warnings to failures
    path      specific SKILL.md files (default: every SKILL.md under plugins/)
"""

import os
import re
import sys

NORM_MAX_LINES = 500
DENSITY_WARN = 150
DESC_MIN, DESC_MAX = 120, 600

# A description triggers when it says *when* to reach for the skill, not only what it does.
# "Use whenever…" and "Use right after…" are as valid as "Use when…", so match the verb plus any
# ordinary continuation rather than a closed list of next words — the first draft of this regex
# rejected a description it had itself just been written to accept.
# Un declencheur peut s'ecrire de plusieurs facons, et la regle en testait UNE : la notre.
# Mesure du 2026-08-09 sur 159 SKILL.md ecrites par d'autres -- 75 refus pour « ne dit jamais
# QUAND l'utiliser », dont **13 en ecriture non latine** que le motif ne peut physiquement pas
# voir, et **62 qui declarent leur declencheur autrement** (`Trigger: replace locator, ...`).
# Toutes disaient quand les utiliser. La regle mesurait la formulation, pas la propriete --
# troisieme fois dans la meme journee qu'une regle lexicale penalise une langue ou une
# convention plutot qu'une lacune.
TRIGGER = re.compile(
    r"\bUse\s+(when|whenever|for|to|it|this|after|before|right|on|during|in)\b"
    r"|\bTrigger(s|ed)?\s*[:\-]"
    r"|\b(Invoke|Call|Run|Apply)\s+(this|it|when|for|after|before)\b"
    r"|\bwhen\s+(the\s+)?(user|you|a|an|someone|asked|working|debugging|writing)\b"
    r"|\bfor\s+(when|any|every|tasks?|cases?)\b", re.I)

# Une description presque sans caracteres latins ne peut pas etre jugee par un motif latin.
# On le DIT au lieu de la refuser : un controle qui ne sait pas doit se taire.
NON_LATIN = re.compile(r"[\u2E80-\u9FFF\uAC00-\uD7AF\u0400-\u04FF\u0590-\u08FF]")
# `step X = done` with nothing making it conditional on the validation having happened.
UNCONDITIONAL_DONE = re.compile(r"step\s+`?[\w-]+`?\s*=\s*done(?!\s*\*{0,2}only)", re.I)
# `Qn` is deliberately absent from this pattern. In this catalogue it never means a project
# decision: it is the nth open question **of the run the skill is currently performing**, a
# numbering the skills define themselves (`Q1, Q2…`, `# open: Q5`). Flagging it told authors to
# gloss a scheme their own text had just introduced. Found by reading the nine warnings
# outstanding for three sprints rather than by acting on them: all nine were false positives.
INTERNAL_CODE = re.compile(r"(?<![A-Za-z0-9])(?:D\d{1,3}|T\d{1,2}|ADR\s*\d{4}|#\d{1,3})(?![A-Za-z0-9])")
# A code is acceptable when the sentence explains it on the spot: `ADR 0001, the negative-path
# coverage gate` or `ADR 0001 (the …)`, or when it is a markdown link. The warning's own remedy
# is "gloss on first use" — counting an already-glossed occurrence contradicts the remedy.
GLOSSED = re.compile(r"(?:D\d{1,3}|T\d{1,2}|ADR\s*\d{4}|#\d{1,3})\s*[(,]\s*(?:the|le|la|les|its|which)\b", re.I)
LINKED_CODE = re.compile(r"\[[^\]]*(?:D\d{1,3}|T\d{1,2}|ADR\s*\d{4}|#\d{1,3})[^\]]*\]\([^)]+\)")
# A date inside a path is a directory name, not a changelog entry: `eval/ci-proof-2026-08-01/`
# names an artifact folder and is the opposite of stale prose — it is how a claim stays
# checkable. Only a bare date in the text is a changelog smell.
CAMPAIGN_DATE = re.compile(r"(?<![\w/-])20\d{2}-\d{2}-\d{2}(?![\w/-])")


def find_skills(paths):
    """Fichiers ou repertoires. Sans argument : `plugins/`.

    L'argument n'acceptait qu'un CHEMIN DE FICHIER : passer un repertoire le renvoyait tel quel,
    et le linter tentait d'ouvrir un dossier comme un fichier -- zero skill lintee, sans message.
    Trouve le 2026-08-09 en pointant l'outil sur 161 SKILL.md ecrites par d'autres, ce qu'aucune
    execution n'avait jamais fait : il n'avait tourne que sur `plugins/`, ou le cas ne se pose pas.
    """
    if paths:
        out = []
        for p in paths:
            if os.path.isdir(p):
                for root, dirs, files in os.walk(p):
                    dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
                    if "SKILL.md" in files:
                        out.append(os.path.join(root, "SKILL.md"))
            else:
                out.append(p)
        return sorted(out)
    out = []
    for root, dirs, files in os.walk("plugins"):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
        if "SKILL.md" in files and os.path.basename(root) != "skills":
            out.append(os.path.join(root, "SKILL.md"))
    return sorted(out)


def parse_frontmatter(lines):
    """Return (fields, body_start_index, error)."""
    if not lines or lines[0].strip() != "---":
        return {}, 0, "no YAML frontmatter (a skill must open with ---)"
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, 0, "frontmatter opened with --- but never closed"
    fields, key = {}, None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        if re.match(r"^\s", raw) and key:          # continuation of a folded value
            fields[key] += " " + raw.strip()
            continue
        if ":" not in raw:
            return fields, end + 1, "frontmatter line is not a key: value pair -> %r" % raw[:60]
        key, val = raw.split(":", 1)
        key = key.strip()
        fields[key] = val.strip()
    return fields, end + 1, None


def lint_one(path):
    fails, warns = [], []
    text = open(path, encoding="utf-8", errors="replace").read()
    lines = text.split("\n")
    skill_dir = os.path.basename(os.path.dirname(path))

    fields, body_start, fm_err = parse_frontmatter(lines)
    if fm_err:
        fails.append(fm_err)
        return fails, warns

    name = fields.get("name")
    if not name:
        fails.append("frontmatter has no `name`")
    elif name != skill_dir:
        fails.append("`name: %s` does not match its directory %r — the two must agree or the "
                     "skill cannot be addressed reliably" % (name, skill_dir))

    desc = fields.get("description", "")
    if not desc:
        fails.append("frontmatter has no `description` — nothing would ever trigger this skill")
    else:
        if not TRIGGER.search(desc) and len(NON_LATIN.findall(desc)) > len(desc) * 0.2:
            warns.append("description is mostly non-Latin script — this linter's "
                         "trigger patterns are Latin-only and cannot judge it. "
                         "Not counted as a defect.")
        elif not TRIGGER.search(desc):
            fails.append("description never says WHEN to use the skill (no \"Use when/for/to …\"). "
                         "It is the only triggering signal the model gets; without it the skill is "
                         "reachable only by someone already following a scripted journey.")
        if len(desc) < DESC_MIN:
            warns.append("description is thin (%d chars, under %d) — likely to under-trigger"
                         % (len(desc), DESC_MIN))
        elif len(desc) > DESC_MAX:
            warns.append("description is long (%d chars, over %d) — the trigger dilutes"
                         % (len(desc), DESC_MAX))

    body = lines[body_start:]
    if len(lines) > NORM_MAX_LINES:
        fails.append("%d lines, over the %d-line authoring ceiling — move material into "
                     "references/ with a pointer rather than cutting it" % (len(lines), NORM_MAX_LINES))

    non_empty = [l for l in body if l.strip()]
    if non_empty:
        density = sum(len(l) for l in non_empty) / len(non_empty)
        if density > DENSITY_WARN:
            warns.append("%.0f characters per line — dense enough to read as a wall. The "
                         "best-rated skills sit between 66 and 100; length is not the problem, "
                         "compaction is." % density)

    for i, line in enumerate(body, start=body_start + 1):
        if UNCONDITIONAL_DONE.search(line):
            fails.append("line %d marks a journey step `= done` unconditionally. A validation gate "
                         "that writes itself done is the bypass rule 3 exists to prevent — make it "
                         "conditional on the validation actually happening." % i)

    body_text = "\n".join(body)
    # Drop the occurrences the sentence already explains, and those inside a markdown link.
    scrubbed = LINKED_CODE.sub("", body_text)
    scrubbed = GLOSSED.sub("", scrubbed)
    codes = INTERNAL_CODE.findall(scrubbed)
    dates = CAMPAIGN_DATE.findall(body_text)
    if codes:
        warns.append("%d internal code reference(s) (%s…) — unreadable to anyone without the "
                     "project's history; gloss on first use or move to references/"
                     % (len(codes), ", ".join(sorted(set(codes))[:4])))
    if dates:
        warns.append("%d campaign date(s) in the body — a skill is a specification, not a changelog"
                     % len(dates))

    return fails, warns


# A repo-relative path written inside a plugin. Absolute URLs are excluded by the leading
# negative lookbehind on "/" — `https://…/docs/x.md` must not match as `docs/x.md`.
REPO_PATH = re.compile(r"(?<![\w/.-])((?:docs|plugins|eval|examples|prompts)/[\w./-]+\.(?:md|json|yml|yaml|py|js))")
# `[`docs/x.md`](https://github.com/…)` — the label looks like a bare repo path but the link works.
LINKED_LABEL = re.compile(r"\[[^\]]*\]\(https?://[^)]+\)")


def lint_plugin_links(plugin_dir):
    """Every repo path referenced from inside a plugin must resolve *inside that plugin*.

    A user who runs `/plugin install qaia-playwright@qaia` receives the plugin directory, not the
    repository. A pointer to `docs/OUTPUT-CONTRACT.md` or to a sibling plugin therefore resolves
    to nothing on their machine — and the rules behind those pointers are guardrails, so what
    silently disappears is the justification for a constraint. The model then reconstructs it
    from memory, which is the failure this check exists to prevent (issue #66).

    Two escapes are legitimate and pass: an absolute URL to the versioned file, and a path that
    resolves within the plugin. Nothing else does.
    """
    fails = []
    for root, _dirs, files in os.walk(plugin_dir):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            text = open(path, encoding="utf-8", errors="replace").read()
            # A path used as the *label* of a link whose target is an absolute URL is already
            # reachable — drop those constructs before scanning, or the check punishes the very
            # fix it asks for.
            text = LINKED_LABEL.sub("", text)
            own_prefix = "plugins/" + os.path.basename(plugin_dir) + "/"
            for ref in set(REPO_PATH.findall(text)):
                # The only repo-style path that survives installation is one pointing inside
                # this very plugin. Testing existence in the *repository* is the trap: every
                # broken reference exists here, which is exactly why nobody noticed.
                if ref.startswith(own_prefix) and os.path.exists(ref):
                    continue
                fails.append("%s references %r, which is not in this plugin. An installed user "
                             "receives the plugin directory, not the repo — use a relative path "
                             "inside the plugin, or an absolute github.com URL."
                             % (os.path.relpath(path, plugin_dir), ref))
    return fails


def main(argv):
    strict = "--strict" in argv
    paths = [a for a in argv if not a.startswith("--")]
    targets = find_skills(paths)
    if not targets:
        print("no SKILL.md found")
        return 2

    n_fail = n_warn = 0
    for path in targets:
        fails, warns = lint_one(path)
        n_fail += len(fails)
        n_warn += len(warns)
        if fails or warns:
            print("%s" % path)
            for f in fails:
                print("  FAIL  %s" % f)
            for w in warns:
                print("  warn  %s" % w)

    # Cross-boundary link check, once per plugin rather than once per skill: the offending
    # pointers live in references/ and connectors/ as often as in SKILL.md itself.
    if not paths and os.path.isdir("plugins"):
        for plugin in sorted(os.listdir("plugins")):
            pdir = os.path.join("plugins", plugin)
            if not os.path.isdir(pdir):
                continue
            link_fails = lint_plugin_links(pdir)
            if link_fails:
                print("%s" % pdir)
                for f in link_fails:
                    print("  FAIL  %s" % f)
                n_fail += len(link_fails)

    print("\n%d skill(s) linted — %d failure(s), %d warning(s)" % (len(targets), n_fail, n_warn))
    if n_fail:
        return 1
    if strict and n_warn:
        print("--strict: warnings promoted to failures")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
