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
    check("grep_pattern leaves the apostrophe alone",
          "\\'" in A.grep_pattern(titles[0]), False)

# Le titre d'un test vient du depot SCANNE -- en mode --third-party, de celui d'un inconnu. Il
# doit atteindre le lanceur comme un element d'argv, jamais comme un morceau de chaine de shell.
# Garde-fou de la faille trouvee par la revue « developpeur » le 2026-08-09 : `escape_grep`
# echappait les metacaracteres d'expression reguliere et etait utilise comme s'il echappait le
# shell, si bien qu'un backtick ou un guillemet dans un nom de test s'executait.
import inspect
_src = inspect.getsource(A.run_cmd)
check("run_cmd ne passe par aucun shell",
      ("shell=False" in _src) and ("shell=True" not in _src), True)

_HOSTILE = 'a manager`id`s "report" $(id)'
_pat = A.grep_pattern(_HOSTILE)
check("un titre hostile reste une donnee : rien n'est ajoute pour le refermer",
      ('"' in _pat) and ("`" in _pat) and ("\\\"" not in _pat), True)

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
# (`realworld-apps/realworld`, 128 tests). It had only ever scored its own output, so neither
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

# --- 5. multi-line expect chains, and suites that are not Playwright at all ------------------
# Found 2026-08-09 by scanning nine third-party Playwright suites (271 tests). Twenty
# high-precision findings came back; every single one was false, and two were the tool's fault.

# `expect.poll()` written as a chain over several lines left `expect` alone on its line, so the
# line-by-line detector saw no assertion and declared the test assertion-less -- BLOCKING in
# default mode. 12 tests across openplayerjs and drumhaus were wrongly reported this way.
POLL = "\n".join([
    "test('polls until the src becomes a blob', async ({ page }) => {",
    "  await expect",
    "    .poll(() => page.evaluate(() => document.querySelector('#p').src), { timeout: 15000 })",
    "    .toMatch(/^blob:/);",
    "});",
])
joined = A.join_chains(POLL)
check("a split expect.poll chain is seen as one assertion",
      any(A.EXPECT_CALL.search(ln) and ".toMatch" in ln for ln in joined), True)
check("join_chains preserves the line count, so reported line numbers stay true",
      len(joined), len(POLL.split("\n")))
check("expect.poll on a single line is still matched",
      bool(A.EXPECT_CALL.search("await expect.poll(() => x()).toBe(1);")), True)
check("an import line is not mistaken for an assertion",
      bool(A.EXPECT_CALL.search("import { expect, test } from '@playwright/test';")), False)

# `.spec.ts` is not a Playwright marker -- Vitest and Jest use it too, and every rule here is
# Playwright-specific. Scoring `valhalla/web-app` produced 7 hollow-assertion findings against
# Vitest unit tests, where `toBeDefined()` on a plain object is a real check, not a hollow one.
check("a Vitest import is recognised as a foreign runner",
      bool(A.FOREIGN_RUNNER.search("import { describe, it, expect } from 'vitest';")), True)
check("a Playwright import is not treated as foreign",
      bool(A.FOREIGN_RUNNER.search("import { expect, test } from '@playwright/test';")), False)
# Asserting the return SHAPE is not enough: the first version of this check passed while the
# skip branch was disabled outright. It has to exercise the behaviour on real files.
import shutil
import tempfile
_tmp = tempfile.mkdtemp(prefix="qaia-selfcheck-")
try:
    io_pairs = [
        ("pw.spec.ts", "import { expect, test } from '@playwright/test';\ntest('a', async () => {});\n"),
        ("unit.spec.ts", "import { describe, it, expect } from 'vitest';\nit('b', () => {});\n"),
        ("jest.spec.js", "const { expect } = require('jest');\ntest('c', () => {});\n"),
        # Angular/Karma: Jasmine injects describe/it as globals, so there is no import at all.
        ("ng.component.spec.ts", "describe('', () => {\n  it('', () => {\n"
                                 "    expect(true).toBe(true);\n  })\n})\n"),
    ]
    for fname, src in io_pairs:
        with open(os.path.join(_tmp, fname), "w", encoding="utf-8") as fh:
            fh.write(src)
    kept, skipped = A.find_spec_files(_tmp)
    check("the Playwright spec is kept", [os.path.basename(p) for p in kept], ["pw.spec.ts"])
    check("every foreign-runner spec is skipped, including the import-less Jasmine one",
          sorted(os.path.basename(p) for p in skipped),
          ["jest.spec.js", "ng.component.spec.ts", "unit.spec.ts"])
finally:
    shutil.rmtree(_tmp, ignore_errors=True)

# --- 6. three rules narrowed or added by the second third-party batch (863 more tests) --------

# `toBeDefined()` is hollow on a LOCATOR (the handle always exists) and a real check on anything
# else. Unqualified, it fired 7 times on valhalla/web-app and 17 on Jokimbe/ComfyUI-DrawThings —
# all wrong, all blocking.
def _hollow(line):
    return any(rx.search(line) for rx, _ in A.HOLLOW_ASSERTIONS)


check("toBeDefined on a locator is still hollow",
      _hollow("await expect(page.locator('#x')).toBeDefined();"), True)
check("toBeDefined on a getBy* locator is still hollow",
      _hollow("expect(page.getByRole('button')).toBeDefined();"), True)
check("toBeDefined on a plain value is NOT hollow",
      _hollow("expect(await comfy.getNodeRef('Sampler')).toBeDefined();"), False)

# Verification held by a throwing wait or by a page object still fails the test, which is all
# `test-without-assertion` is entitled to claim. POM-as-fixtures is what `automate` MANDATES, so
# the unqualified rule penalised the exact pattern this project requires.
check("a page-object assertion counts",
      bool(A.INDIRECT_ASSERTION.search("await markdownEditorPage.expectVisible();")), True)
check("waitForURL counts", bool(A.INDIRECT_ASSERTION.search("await page.waitForURL(/login/);")), True)
check("waitForSelector counts",
      bool(A.INDIRECT_ASSERTION.search("await page.waitForSelector('span:has-text(\"done\")');")), True)
check("an ordinary action does not count",
      bool(A.INDIRECT_ASSERTION.search("await page.click('#submit');")), False)
check("waitForTimeout is NOT a verification — it asserts nothing",
      bool(A.INDIRECT_ASSERTION.search("await page.waitForTimeout(1000);")), False)
# The helper is as often a free function as a method (batch 3: EDDI-Manager 17, chicio-blog 5).
check("a free helper starting with the intent counts",
      bool(A.INDIRECT_ASSERTION.search("await expectHeading(page, /audit/i);")), True)
check("a free helper carrying the intent in camelCase counts",
      bool(A.INDIRECT_ASSERTION.search('await openAndAssertHeading(page, "open art", /art/, "Art");')), True)
check("a lowercase lookalike does not count",
      bool(A.INDIRECT_ASSERTION.search("await checkbox(page);")), False)
check("navigation is still not a verification",
      bool(A.INDIRECT_ASSERTION.search("await gotoApp(page);")), False)

# A body with no executable statement runs, does nothing, and reports PASS.
check("closing punctuation is not a statement", bool(A.EMPTY_BODY_NOISE.match("  });")), True)
check("a real statement is not noise", bool(A.EMPTY_BODY_NOISE.match("  await page.goto('/');")), False)

# Matching the patterns is not the same as acting on them: the first version of the two checks
# above passed with `real_assertions += 0` and with the empty-body finding renamed away. Both
# have to be exercised through static_track on real files.
_tmp2 = tempfile.mkdtemp(prefix="qaia-selfcheck-behaviour-")
try:
    # Kept in two files so each assertion answers one question: the empty test SHOULD also raise
    # test-without-assertion, and mixing them made the first version of this check fail for the
    # right reason at the wrong place.
    with open(os.path.join(_tmp2, "pom.spec.ts"), "w", encoding="utf-8") as fh:
        fh.write("\n".join([
            "import { test, expect } from '@playwright/test';",
            "test('verification lives in the page object', async ({ loginPage }) => {",
            "  await loginPage.signIn('a', 'b');",
            "  await loginPage.expectDashboardVisible();",
            "});",
        ]))
    specs, _ = A.find_spec_files(_tmp2)
    kinds = [f["kind"] for f in A.static_track(specs, [], _tmp2, set(), third_party=True)["findings"]]
    check("a page-object assertion prevents test-without-assertion",
          kinds.count("test-without-assertion"), 0)
    check("a page-object assertion is not mistaken for an empty body",
          kinds.count("empty-test-body"), 0)

    os.remove(os.path.join(_tmp2, "pom.spec.ts"))
    with open(os.path.join(_tmp2, "empty.spec.ts"), "w", encoding="utf-8") as fh:
        fh.write("\n".join([
            "import { test, expect } from '@playwright/test';",
            "test('this one is empty', async ({ page }) => { });",
            "test('this one is only comments', async ({ page }) => {",
            "  // load the workflow",
            "  // assert the node is green",
            "});",
            # DECLARED placeholders: Playwright reports these as skipped, which is the very fix
            # the rule recommends. Flagging them would have had this project file an issue
            # against solidcouch/solidcouch for doing the right thing.
            "test.fixme('declared as unfinished', async ({ page }) => {});",
            "test.skip('declared as skipped', async ({ page }) => {});",
        ]))
    specs, _ = A.find_spec_files(_tmp2)
    kinds = [f["kind"] for f in A.static_track(specs, [], _tmp2, set(), third_party=True)["findings"]]
    check("both undeclared empty bodies are reported", kinds.count("empty-test-body"), 2)
finally:
    shutil.rmtree(_tmp2, ignore_errors=True)

# --- 7. traceability must be checked in BOTH directions ---------------------------------------
# It only ever asked "does the title carry a tag?". A test tagged `@QAIA-US-004-043` where no
# scenario 043 exists scored 25/25 — with both sets already in hand. A tag that resolves to
# nothing is worse than no tag: it looks like traceability. Seven such tags sat in this project's
# own showcase, found by reading it, never by the tool.
#
# And the first version of the fix flagged 18 instead of 7: it reproached the suite for carrying
# `@QAIA-VIS-*` and `@QAIA-A11Y-*` tags, which are deliberately separate namespaces with no
# Gherkin scenario and no need for one. "Is the rule applicable at all?" — the same failure as
# the 279 selectors, one file over.
_tmp3 = tempfile.mkdtemp(prefix="qaia-selfcheck-trace-")
try:
    with open(os.path.join(_tmp3, "a.spec.ts"), "w", encoding="utf-8") as fh:
        fh.write("\n".join([
            "import { test, expect } from '@playwright/test';",
            "test('@QAIA-US-001-001 covered by the book', async ({ page }) => {",
            "  await expect(page.locator('#a')).toHaveText('x');",
            "});",
            "test('@QAIA-US-001-099 no such scenario', async ({ page }) => {",
            "  await expect(page.locator('#b')).toHaveText('y');",
            "});",
            "test('@QAIA-VIS-001 a separate namespace, legitimately', async ({ page }) => {",
            "  await expect(page.locator('#c')).toHaveText('z');",
            "});",
        ]))
    specs, _ = A.find_spec_files(_tmp3)
    book = {"QAIA-US-001-001"}
    kinds = [f for f in A.static_track(specs, [], _tmp3, book)["findings"]
             if f["kind"] == "test-without-scenario"]
    check("a tag resolving to no scenario is reported", len(kinds), 1)
    if kinds:
        check("...and it is the dangling one, not the separate namespace",
              kinds[0]["detail"].split(" ")[0], "QAIA-US-001-099")
    # No test book supplied: the rule has nothing to resolve against and must stay silent.
    silent = [f for f in A.static_track(specs, [], _tmp3, set())["findings"]
              if f["kind"] == "test-without-scenario"]
    check("with no test book, the rule does not fire", len(silent), 0)
finally:
    shutil.rmtree(_tmp3, ignore_errors=True)

if failures:
    print("selfcheck_automation_score: %d FAILURE(S)\n" % len(failures))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("selfcheck_automation_score: ok")
