# -*- coding: utf-8 -*-
"""Self-check for the parts of automation_score.py that a fixture suite cannot reach.

The static track is validated by running the tool against
`eval/tools/fixtures/automation-score-static/` (see its VALIDATION.md). The mutation track is not:
validating it needs a live Playwright suite and a running system under test, which CI does not have.

The two defects found on 2026-08-08 both lived in that unreachable half, and both inflated the kill
count without ever failing:

  1. Playwright exits 1 both for "a test failed" and for "No tests found". Mutations the run command
     never selected were therefore scored as kills.
  2. A test title containing an apostrophe was captured with its JavaScript escape (`manager\\'s`),
     so `--grep` matched nothing -- which, via (1), also read as a kill.

Run: python eval/tools/selfcheck_automation_score.py
Exits non-zero on the first failure.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import automation_score as A  # noqa: E402

failures = []


def check(label, got, want):
    if got != want:
        failures.append("%s\n    got:  %r\n    want: %r" % (label, got, want))


# --- 1. "No tests found" must be distinguishable from a failing test -------------------------
check("NO_TESTS_FOUND matches Playwright's message",
      bool(A.NO_TESTS_FOUND.search("Error: No tests found\n")), True)
check("NO_TESTS_FOUND does not match an ordinary failure",
      bool(A.NO_TESTS_FOUND.search("1 failed\n  [api] > api.spec.js:12:3 > a test\n")), False)

# --- 2. A title's JavaScript escapes must not reach --grep -----------------------------------
check("apostrophe unescaped", A.unescape_js("a manager\\'s report"), "a manager's report")
check("double quote unescaped", A.unescape_js('he said \\"no\\"'), 'he said "no"')
check("backslash unescaped", A.unescape_js("a\\\\b"), "a\\b")
check("plain title untouched", A.unescape_js("@QAIA-US-004-001 a plain title"), "@QAIA-US-004-001 a plain title")

SRC = "\n".join([
    "const { test, expect } = require('./fixtures');",
    # JavaScript source: test('@QAIA-1 a manager\'s own report escalates', ...)
    "test('@QAIA-1 a manager\\'s own report escalates', async () => {",
    "  expect(x).toBe('approved');",
    "});",
])
titles = [t for t, _, _ in A.split_tests(SRC)]
check("split_tests returns the runner's title, not the source's",
      titles, ["@QAIA-1 a manager's own report escalates"])

# The grep pattern is built from that title: it must escape regex metacharacters but must not
# reintroduce the JS escape, or the mutation is silently never run.
if titles:
    check("escape_grep leaves the apostrophe alone",
          "\\'" in A.escape_grep(titles[0]), False)

# --- 3. "nothing was found" assertions must be mutable ---------------------------------------
# `expect(violations).toEqual([])` is the entire a11y idiom. No operator covered it, so those
# assertions were absent from the mutation corpus without any field saying so -- the same class of
# gap as scoring an unrun mutation as a kill, one level earlier.
mutated, desc = A.mutate_line("    expect(serious).toEqual([]);")
check("toEqual([]) is mutated", mutated is not None and A.MUTANT_MARK in (mutated or ""), True)
check("the mutant still parses as a non-empty array",
      "toEqual(['" + A.MUTANT_MARK + "'])" in (mutated or ""), True)
check("toEqual({}) is mutated",
      A.MUTANT_MARK in (A.mutate_line("    expect(o).toEqual({});")[0] or ""), True)
check("a non-empty literal array is left to the other operators",
      A.mutate_line("    expect(x).toEqual([1, 2]);")[0], None)

# --- 4. the tool must survive having no test book, and must not judge a foreign suite -------
# Both found on 2026-08-09 the first time the tool was pointed at a suite QAIA did not write
# (`gothinkster/realworld`, 128 tests). It had only ever scored its own output, so neither
# path had ever been taken.

# `--testbook` is documented as optional, but this early return yielded ONE value while the
# caller unpacked TWO: every run without a test book died on a ValueError before scoring a line.
check("collect_feature_ids returns a pair when there is no test book",
      len(A.collect_feature_ids(None)), 2)

# Three of the four budget lines encode QAIA conventions. Scored against a mature third-party
# suite they produced 408 findings that were not defects -- 279 of them flagging CSS selectors
# the project PUBLISHES as a contract (`specs/e2e/SELECTORS.md`) -- and a 30/100 that read as a
# quality verdict on someone else's work. In third-party mode those three are excluded from the
# budget, never scored zero, and the hollow/blocking rules must keep firing regardless.
import inspect
sig = inspect.signature(A.static_track).parameters
check("static_track accepts third_party", "third_party" in sig, True)
check("third_party defaults to off, so QAIA's own suites keep the full budget",
      sig["third_party"].default, False)

if failures:
    print("selfcheck_automation_score: %d FAILURE(S)\n" % len(failures))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("selfcheck_automation_score: ok")
