#!/usr/bin/env python3
"""The qaia router must name every routable skill, and no skill that does not exist.

Why this exists. The router in `plugins/qaia-core/skills/qaia/SKILL.md` lists its targets in
prose. That list has diverged four times: Gherkin scope (2026-07-30), skill counts (2026-08-08
and 2026-08-10), and the router itself after the 2026-08-24 judge consolidation — when it still
pointed at `testbook-score`/`aptitude-gate`/`automation-score`/`spec-suite-drift`/`testbook-validate`
(all absorbed into `judge`, so absent) and never named `judge`. Routing a user to a skill that no
longer exists is the exact failure issues #94 and #100 name: the entry point sends them nowhere.

A prose list a human maintains re-diverges on the next rename. So it is checked, not remembered.
Two directions, both failing CI:

  - DEAD NAME: a backtick token that looks like a skill name but is neither an installed skill nor
    an allowed non-skill token (plugin names, journey-state words). This catches routing to an
    absent skill.
  - COVERAGE: a qaia-core skill that exists but the router never names, unless it is explicitly
    excluded with a reason here.

Cross-plugin skills (qaia-playwright/score/testdata) are named behind an installed-check in the
router ("never claim to route to a skill you have not found"), so they are not required here --
qaia-core installs alone and cannot assume them. But a dead name from ANY plugin is still caught,
because a name the router prints must resolve to something real wherever it lives.
"""
import re, glob, os, sys

ROUTER = "plugins/qaia-core/skills/qaia/SKILL.md"

# Backtick tokens the router legitimately uses that are not skills.
ALLOWED_NON_SKILL = {
    "qaia-core", "qaia-playwright", "qaia-score", "qaia-testdata",   # plugin names
    "done", "status", "pending-validation", "simulated", "validated",  # journey-state words
}
# Skills that exist but are deliberately not routing targets, each with its reason.
COVERAGE_EXCLUSIONS = {
    "qaia": "the router itself",
    "hello": "an installation smoke-check, not a 'describe your need' target",
}


def main():
    if not os.path.exists(ROUTER):
        print("router not found: %s" % ROUTER); return 2
    text = open(ROUTER, encoding="utf-8").read()
    tokens = set(re.findall(r"`([a-z][a-z0-9-]+)`", text))
    installed = {os.path.basename(os.path.dirname(p))
                 for p in glob.glob("plugins/*/skills/*/SKILL.md")}
    core = {os.path.basename(os.path.dirname(p))
            for p in glob.glob("plugins/qaia-core/skills/*/SKILL.md")}

    fails = []
    # DEAD NAME: a skill-shaped token that resolves to nothing.
    for t in sorted(tokens - installed - ALLOWED_NON_SKILL):
        # a skill name carries a hyphen or is a known single word; the heuristic errs toward
        # flagging. A legitimate new non-skill token is added to ALLOWED_NON_SKILL on purpose.
        fails.append("router names `%s`, which is not an installed skill and not an allowed "
                     "non-skill token -- a dead name routes users nowhere (add the skill, fix the "
                     "name, or allow-list the token with a reason)" % t)
    # COVERAGE: every qaia-core skill is named, unless excluded with a reason.
    for s in sorted(core - tokens - set(COVERAGE_EXCLUSIONS)):
        fails.append("qaia-core skill `%s` is installable but the router never names it -- route "
                     "to it, or add it to COVERAGE_EXCLUSIONS with a reason" % s)

    if fails:
        for f in fails:
            print("FAIL  " + f)
        return 1
    print("OK: the router names every routable qaia-core skill and no skill that does not exist "
          "(%d skills across all plugins, %d qaia-core)." % (len(installed), len(core)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
