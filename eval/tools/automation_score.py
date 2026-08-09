#!/usr/bin/env python3
"""Deterministic quality score for QAIA-generated Playwright test code.

Companion to `structural_score.py`, which does the same job for the Gherkin test book.
This tool judges the *generated automation* — the layer that, until now, was only ever
reviewed by its own producer (`automate` SKILL.md step 4), in violation of the project's
own rule 3 ("a producer plugin never grades its own output",
`plugins/qaia-score/README.md:26`).

It carries the two tracks that can be made mechanical and reproducible:

  STATIC    — reads the test files without running them: hollow assertions, fragile
              selectors, POM-as-fixtures compliance, forbidden waits, tag traceability
              back to the test book.

  MUTATION  — inverts the expectation of each assertion, re-runs the owning test, and
              requires it to go RED. An assertion that survives its own inversion is
              decorative: it cannot fail, so it tests nothing. Survivors are BLOCKING,
              in the same spirit as `structural_score.py`'s C1/C2 detectors.

              The mutation is applied to the TEST, never to the system under test — so the
              track works against any target, including public sites we do not own, and the
              score stays comparable from run to run. Honest limit, stated here rather than
              buried: this proves an assertion is sensitive to its own expected value; it
              does NOT prove it asserts the *right* thing. That second question is the LLM
              judge's job (`eval/AUTOMATION-RUBRIC.md`), and the two are never merged.

What this tool deliberately does NOT do: judge intent, business fidelity, or whether the
test matches the scenario's `Then`. Those are not mechanical. The LLM rubric owns them, and
its number is reported separately — never summed with this one. That separation is the
lesson of case US 676266 (100/100 machine vs 58/100 human), see `eval/RUBRIC.md`.

Parsing is regex-based, not a real JS parser. This is a deliberate trade-off (no Node
dependency for the static track) and it means unusual formatting can be missed. Every
finding therefore carries its file and line so a human can check it; a MISSED defect is
possible, a FABRICATED one is not.

Usage:
  python eval/tools/automation_score.py --tests-dir <dir> [--testbook <dir-or-file>]
      [--run-cwd <dir>] [--run-cmd "npx playwright test"] [--max-mutations N]
      [--skip-mutation] [--out result.json]
"""

import argparse
import json
import os
import re
import shutil
import atexit
import shlex
import signal
import subprocess
import sys
import tempfile

SPEC_GLOB = re.compile(r"\.spec\.(js|ts|mjs|cjs)$")

# --------------------------------------------------------------------------- static track

FORBIDDEN_WAITS = [
    (re.compile(r"waitForTimeout\s*\("), "waitForTimeout"),
    (re.compile(r"networkidle"), "networkidle"),
    (re.compile(r"waitForLoadState\s*\(\s*['\"]networkidle"), "waitForLoadState(networkidle)"),
]

# Assertions that can never fail, whatever the app does. Blocking.
# Une assertion dont le SUJET est un litteral -- `expect(true)`, `expect(3)`, `expect('abc')`,
# ou une propriete d'un litteral comme `expect('1234567890'.length)` -- ne peut pas echouer :
# sa valeur est connue a l'ecriture et le SUT n'y participe pas. Trouve le 2026-08-09 en
# prouvant une autre correction : la revue « developpeur » avait releve une telle assertion a
# la main dans la suite vitrine (`expect(comment.length).toBe(10)` sur le litteral defini deux
# lignes plus haut), et cet outil, qui existe pour les attraper, la classait « faible ».
TAUTOLOGICAL = re.compile(
    r"\bexpect\s*\(\s*(?:true|false|null|undefined|-?\d+(?:\.\d+)?|"
    r"(['\"`])(?:\\.|(?!\1).)*\1)\s*(?:\.\s*\w+\s*)?\)")

HOLLOW_ASSERTIONS = [
    (re.compile(r"expect\s*\(\s*true\s*\)\s*\.\s*toBe\s*\(\s*true\s*\)"), "expect(true).toBe(true)"),
    (re.compile(r"expect\s*\(\s*1\s*\)\s*\.\s*toBe\s*\(\s*1\s*\)"), "expect(1).toBe(1)"),
    (re.compile(r"expect\s*\(\s*\)\s*\."), "expect() with no subject"),
    # `toBeDefined()` is hollow ONLY on a locator: `page.locator('x')` returns a handle whether or
    # not the element exists, so the assertion cannot fail. On any other value it is a real check
    # — `expect(await getNodeRef(...)).toBeDefined()` fails when the lookup returns undefined, and
    # the code right after it uses `node?.`, which is the author saying so.
    # The unqualified rule fired on `valhalla/web-app` (7 times, all wrong) and on
    # `Jokimbe/ComfyUI-DrawThings-gRPC` (17 times, all wrong) before this was narrowed on
    # 2026-08-09. A hollow-assertion finding is BLOCKING, so a false one is expensive.
    (re.compile(r"(?:page\s*\.\s*locator|\.\s*locator\s*\(|getBy(?:Role|TestId|Label|Text|"
                r"Placeholder|Title|AltText))[^;]*\.\s*toBeDefined\s*\(\s*\)"),
     "toBeDefined() on a locator (the handle always exists, so this cannot fail)"),
]

# Assertions that CAN fail but carry little information. Reported, never blocking — the
# distinction matters: `expect(cart.items.some(i => i.id === x)).toBeTruthy()` is a real
# check on real data, and blocking on it wrongly failed US-EVAL-002 in this tool's own
# first run. Weak is not hollow.
WEAK_ASSERTIONS = [
    (re.compile(r"\.\s*toBeTruthy\s*\(\s*\)"), "toBeTruthy() — asserts existence, not a value"),
    (re.compile(r"\.\s*toBeFalsy\s*\(\s*\)"), "toBeFalsy() — asserts absence, not a value"),
    (re.compile(r"\.\s*not\s*\.\s*toBeNull\s*\(\s*\)"), "not.toBeNull() — asserts existence, not a value"),
]

# Single-sided refusal evidence. Added 2026-08-08 after four blank-context judge runs, three of
# which found the same shape: a negative test whose ONLY assertion is "not the success value".
# `expect(alertText.length).toBeGreaterThan(0)` for a scenario whose Then demands a specific alert
# AND the absence of "Product added." passes when the app shows "Product added" -- that string is
# 13 characters long. `not.toBe(200)` passes against an app that refused for an unrelated reason,
# and against one that did the forbidden thing and answered 201.
#
# Reported, never blocking, and the boundary is deliberate: the rubric states that the tool judges
# assertion *shape* while the judge judges *vacuity against the specification*. Whether a
# single-sided assertion is vacuous depends on what its scenario claimed, which this tool cannot
# read. What it can say is "this test's whole evidence is one-sided" -- a fact, handed to the judge.
SINGLE_SIDED = [
    (re.compile(r"\.\s*length\s*\)\s*\.\s*toBeGreaterThan\s*\(\s*0\s*\)"),
     "length > 0 -- satisfied by the forbidden value as readily as the expected one"),
    (re.compile(r"\.\s*not\s*\.\s*toBe\s*\("), "not.toBe(...) -- asserts what it is not, not what it is"),
    (re.compile(r"\.\s*not\s*\.\s*toContain\s*\("), "not.toContain(...) -- one-sided"),
    (re.compile(r"\.\s*not\s*\.\s*toEqual\s*\("), "not.toEqual(...) -- one-sided"),
]

# A scenario the test book flagged as resting on an open question, whose generated test carries no
# trace of the flag. Blocking, and the severity comes from the failure mode rather than the code:
# when such a test goes red, the reader cannot tell "the open question just got answered" from
# "the product regressed", and the cheapest resolution is to edit the expected value to match the
# app -- silently converting a finding into a specification. Found on two of the four suites judged.
FLAG_IN_CODE = re.compile(r"low[-_]confidence|open:\s*Q\d|unconfirmed|human arbitration|test\.(fixme|fail)", re.I)
FEATURE_FLAGGED_SCENARIO = re.compile(r"@low-confidence|#\s*open:\s*Q\d", re.I)

# A comment or report citing a file that does not exist. Added 2026-08-08 from the fifth judge
# run: `pages/api-helpers.js` carried "a real finding, see automation/NOTES.md" and no NOTES.md
# was ever written. The rubric already makes a false claim in the *run report* chargeable; this is
# the same failure mode -- evidence offered that cannot be inspected -- one file over. Cheap to
# check, impossible to argue with, and it decays silently: the citation looks authoritative
# precisely because nobody follows it.
# The path must contain a separator. `see app.js` in prose refers to a file the reader is
# expected to know, not to a location this tool can resolve -- flagging it was a false positive
# on this project's own showcase suite, found by running the check against it rather than
# trusting it. `see automation/NOTES.md` is a location, and still fires.
CITATION = re.compile(r"see\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]*\.(?:md|json|txt|ya?ml|js|ts))\b", re.I)

# Raw CSS/XPath selectors: the automate skill mandates getByRole/getByTestId/getByLabel.
RAW_SELECTOR = re.compile(r"\.\s*(locator|\$\$?|querySelector)\s*\(\s*['\"`]")
XPATH_SELECTOR = re.compile(r"['\"`]\s*(//|xpath=)")
ROLE_SELECTOR = re.compile(r"\.\s*(getByRole|getByTestId|getByLabel|getByPlaceholder|getByText|getByTitle|getByAltText)\s*\(")

NL = chr(10)
EXPECT_CALL = re.compile(r"\bexpect\s*[(.]")

# `expect.poll()` and `expect.soft()` are mainstream Playwright, and both are habitually written
# as a chain broken over several lines:
#
#     await expect
#       .poll(() => page.evaluate(...), { timeout: 15_000 })
#       .toMatch(/^blob:/);
#
# The detector reads one line at a time, so `expect` sat alone on its line and matched nothing:
# the test was reported as having NO assertion at all. Found on 2026-08-09 across
# `openplayerjs/openplayerjs` and `mxfng/drumhaus` — 12 tests declared assertion-less while every
# one of them asserted. `test-without-assertion` is BLOCKING in default mode, so this would have
# failed a QAIA-generated suite for using a documented Playwright idiom.
#
# Rejoining the chain before analysis fixes the count *and* keeps the one-sided check honest,
# which reading the pieces separately could not.
CHAIN_HEAD = re.compile(r"\bexpect\s*$")
CHAIN_TAIL = re.compile(r"^\s*\.")

# Closing punctuation and nothing else: the tail of the test declaration, not a statement.
EMPTY_BODY_NOISE = re.compile(r"^\s*[})\];,]*\s*$")

# Verification that is real but carries no literal `expect`. Both forms FAIL the test when the
# condition does not hold, which is the only thing `test-without-assertion` is entitled to claim.
#
#   - `page.waitForURL(/login/)`, `waitForSelector`, `waitForResponse` — throw on timeout.
#   - `await loginPage.expectVisible()` — a page object holding the assertion.
#
# The second one matters most: POM-as-fixtures is what `automate` SKILL.md MANDATES, so the
# unqualified rule penalised the exact pattern this project requires. Found 2026-08-09 on
# `antdigital-ai/agentic-ui` (8 tests, all delegating to a page object) and
# `th3cyb3rhub/TheCyberHub` (11, mostly `waitForURL`). `test-without-assertion` is blocking.
# The helper is as often a free function as a method — `expectHeading(page, /audit/i)` and
# `openAndAssertHeading(page, ...)`, both found on 2026-08-09 in `labsai/EDDI-Manager` (17 tests)
# and `chicio/chicio-blog` (5). Requiring a dot in front missed every one of them, which is the
# same defect as the page-object case one shape over.
#
# Two forms are accepted, and both demand a capital so that `checkbox(` and `should(` do not
# qualify: a name that STARTS with the intent (`expectHeading`), and one that CONTAINS it in
# camelCase (`openAndAssertHeading`).
INDIRECT_ASSERTION = re.compile(
    r"\.\s*waitFor(?:URL|Selector|Response|Request|Event|Function|LoadState)\s*\(|"
    r"\b(?:expect|assert|verify|should|check)[A-Z_]\w*\s*\(|"
    r"\b\w+(?:Assert|Expect|Verify)[A-Z_]?\w*\s*\(")


def join_chains(body):
    """Merge `expect` chains split across lines, keeping one entry per original line.

    The merged text lands on the line where the chain STARTS, and each continuation line is
    replaced by an empty placeholder so that reported line numbers stay true. The anchor is
    tracked by index rather than by `out[-1]`: a first version appended the placeholder and then
    tried to extend it, so a three-line chain kept only its first two parts and the selfcheck
    caught it.
    """
    out = []
    anchor = None
    for raw in body.split(NL):
        # `code_of` sur les DEUX bouts : une chaine coupee en fin de ligne est du code, et
        # un commentaire qui finit par le mot « expect » n'en est pas (B11).
        cont = anchor is not None and (CHAIN_TAIL.match(code_of(raw))
                                       or CHAIN_HEAD.search(code_of(out[anchor])))
        if cont:
            out[anchor] = out[anchor].rstrip() + " " + raw.strip()
            out.append("")
            continue
        out.append(raw)
        # A chain may start either as `await expect` (head) or `expect(x)` continued by `.not`.
        anchor = len(out) - 1 if EXPECT_CALL.search(raw) or CHAIN_HEAD.search(raw) else None
    return out
# `test(...)`, `test.only(...)`, `test.fixme(...)` — but never `test.describe(...)`, which is a
# grouping block, not a test. Counting describe blocks as tests reported every suite as having a
# "test without assertion" (found by running the tool on US-EVAL-001, not by reading it).
TEST_DECL = re.compile(
    r"^\s*test\s*(?:\.\s*(?P<modifier>only|skip|fixme|fail|slow)\s*)?\(\s*(['\"`])(?P<title>(?:\\.|(?!\2).)*)\2")

# `test.fixme('x', () => {})` and `test.skip(...)` are DECLARED placeholders: Playwright reports
# them as skipped, not passed, which is exactly the remedy `empty-test-body` recommends. Firing on
# them would have had this project file an issue against `solidcouch/solidcouch` for doing the
# right thing — 10 of its 16 flagged bodies were `test.fixme`, found 2026-08-09 by reading the
# source before filing rather than after.
DECLARED_PLACEHOLDER = ("skip", "fixme", "fail")
QAIA_TAG = re.compile(r"@?\bQAIA[-A-Za-z0-9_]*-\d+\b")
FEATURE_TAG = re.compile(r"@(QAIA[-A-Za-z0-9_]*-\d+)\b")


# A `//` line comment is prose, not code. Stripping it before pattern matching was added
# 2026-08-08 after the assertion rules fired on `// Was: expect(true).toBe(true)` in a fixture
# whose whole purpose is to document the defect it fixed. Any suite that explains its own
# corrections was being penalised for the explanation. Block comments and `//` inside a string
# literal are deliberately not handled: the cheap version is right far more often than not, and a
# clever one that mis-parses a URL would be worse than none.
COMMENT_TAIL = re.compile(r"(?<!:)//.*$")


def code_of(line):
    return COMMENT_TAIL.sub("", line)


def first_match(rules, line):
    """Only the first matching rule fires. `waitForLoadState('networkidle')` matches two
    patterns and was reported twice before this (found by running the tool, not reading it)."""
    for rx, label in rules:
        if rx.search(line):
            return label
    return None


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


SOURCE_GLOB = re.compile(r"\.(js|ts|mjs|cjs)$")


def _walk(tests_dir):
    for root, dirs, files in os.walk(tests_dir):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "test-results", "playwright-report", ".git")]
        for f in sorted(files):
            yield os.path.join(root, f)


# `.spec.ts` is not a Playwright marker: Vitest and Jest claim the same suffix. Every rule in this
# tool is Playwright-specific — "toBeDefined() (a locator handle always exists)" is sound about a
# locator and plain wrong about an object, where `toBeDefined()` genuinely checks a key exists.
# Found on 2026-08-09: `valhalla/web-app` was scored with 13 of its 15 `.spec.ts` files being
# Vitest unit tests, producing 7 hollow-assertion findings that were all false.
FOREIGN_RUNNER = re.compile(r"""from\s+['"](vitest|@jest/globals|jest|mocha|node:test)['"]|"""
                            r"""require\(\s*['"](vitest|jest|mocha|node:test)['"]""")
PLAYWRIGHT_IMPORT = re.compile(r"""['"]@playwright/test['"]""")

# Angular and Karma specs declare nothing: `describe`/`it` are globals injected by Jasmine, so
# there is no import to recognise and the "no runner found, judge it anyway" branch let them in.
# `scaljeri/oh-my-mock` was scored on `src/app/app.component.spec.ts` this way (2026-08-09).
# Playwright's block is `test(`, never `it(` — a file built from `it(` with no Playwright import
# is somebody else's runner. Files that import a local fixtures module keep passing: they use
# `test(`, which this does not match.
JASMINE_STYLE = re.compile(r"^\s*(?:it|fit|xit)\s*\(", re.M)


def find_spec_files(tests_dir):
    """Playwright specs only. A file that imports another runner is skipped, never scored."""
    out, skipped = [], []
    for p in _walk(tests_dir):
        if not SPEC_GLOB.search(os.path.basename(p)):
            continue
        head = read(p)[:4000]
        if PLAYWRIGHT_IMPORT.search(head):
            out.append(p)
        elif FOREIGN_RUNNER.search(head) or JASMINE_STYLE.search(read(p)):
            skipped.append(p)
        else:
            out.append(p)     # no runner signal either way: judged, as before
    return out, skipped


def find_support_files(tests_dir, spec_files):
    """Page objects and fixtures. Under POM-as-fixtures — which `automate` mandates — the
    selectors live here, not in the specs. Scoring selector quality on the specs alone
    reported 0 role selectors and 0 raw selectors for a suite that is entirely POM-based
    (found by running the tool on US-EVAL-001)."""
    specs = set(spec_files)
    return [p for p in _walk(tests_dir)
            if p not in specs
            and SOURCE_GLOB.search(os.path.basename(p))
            and not os.path.basename(p).startswith("playwright.config")]


def unescape_js(title):
    """`test('a manager\\'s report', ...)` carries the source escape into the captured title. The
    runner sees `a manager's report`, so grepping the escaped form matches nothing -- and Playwright
    exits 1 on "No tests found", which the mutation track used to score as a kill. Eight assertions
    across the two showcase suites were silently never run this way (2026-08-08)."""
    return title.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def split_tests(text):
    """Return [(title, start_line, end_line)] — 1-indexed, end exclusive.

    A test block ends where the next test declaration begins (or at EOF). Coarse but
    sufficient: we only need to attribute a line to its owning test.
    """
    lines = text.split("\n")
    starts = []
    for i, line in enumerate(lines):
        m = TEST_DECL.match(line)
        if m:
            starts.append((i + 1, unescape_js(m.group("title"))))
    blocks = []
    for idx, (ln, title) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines) + 1
        blocks.append((title, ln, end))
    return blocks


def static_track(spec_files, support_files, tests_dir, feature_ids, flagged_ids=frozenset(),
                 third_party=False):
    """`third_party=True` scores a suite QAIA did not generate.

    Three of the four budget lines encode QAIA's own conventions: POM-as-fixtures and tag
    traceability are mandated by `automate` SKILL.md, and the selector rule assumes CSS
    locators are incidental. A mature third-party suite fails all three for reasons that are
    not defects. Measured on `realworld-apps/realworld` (2026-08-09): 428 findings, of which 279
    flagged selectors that the project *publishes as a contract* every implementation must
    provide (`specs/e2e/SELECTORS.md`), 128 flagged tests as untraceable to a test book that
    does not exist, and 1 demanded a `pages/` directory. One finding out of 428 was real.

    So the score was 30.0/100 for a suite that had earned 30.0 out of the 30 points it could
    possibly earn. A number that low says "this is not QAIA-shaped", not "this is bad", and
    reporting it as a quality score would be a straightforward lie about someone else's work.

    This mode rescales the budget onto the dimensions that transfer, and demotes the three
    convention rules to advisory — same idiom already used below when no selector is found:
    not applicable, not penalised, and *said out loud* rather than silently dropped.
    """
    findings = []
    tests_total = 0
    tests_with_real_assertion = 0
    selector_role = 0
    selector_raw = 0
    tagged_tests = 0
    seen_ids = set()

    # A suite is laid out either as `tests/{pages,fixtures.js,*.spec.js}` or as
    # `automation/{tests/*.spec.js, pages/, fixtures.js}`. Looking only under tests_dir reported
    # `pom-missing` on suites whose pages/ sat one level up -- a false finding that appeared in
    # several campaign JSONs and that two independent judges flagged as a probable tool bug before
    # anyone checked. Look in both places, and remember which one won so support files and
    # citations resolve there too.
    pom_roots = [tests_dir, os.path.dirname(tests_dir.rstrip(os.sep))]
    pom_root = next((r for r in pom_roots if os.path.isdir(os.path.join(r, "pages"))), None)
    has_pages_dir = pom_root is not None
    fixtures_path = None
    for root in pom_roots:
        for cand in ("fixtures.js", "fixtures.ts", "fixtures.mjs"):
            p = os.path.join(root, cand)
            if os.path.isfile(p):
                fixtures_path = p
                break
        if fixtures_path:
            break

    # Un `pages/` peut exister et ne rien contenir : la dimension `pom_as_fixtures` creditait
    # l'existence de deux chemins, donc 20 points qu'aucune suite ne pouvait perdre. On regarde
    # ce qu'il y a dedans -- au moins un localisateur dans au moins un objet de page (B12).
    pom_has_locators = False
    if pom_root:
        pages_dir = os.path.join(pom_root, "pages")
        for dirpath, _dirs, files in os.walk(pages_dir):
            for name in files:
                if not name.endswith((".js", ".ts", ".mjs", ".cjs")):
                    continue
                body = read(os.path.join(dirpath, name))
                if ROLE_SELECTOR.search(body) or RAW_SELECTOR.search(body):
                    pom_has_locators = True
                    break
            if pom_has_locators:
                break

    for path in spec_files:
        text = read(path)
        lines = text.split("\n")
        rel = os.path.relpath(path, tests_dir)
        blocks = split_tests(text)

        for i, line in enumerate(lines, start=1):
            for cm in CITATION.finditer(line):
                target = cm.group(1)
                # resolved against the tests dir and against its parent (a suite root), the two
                # places a relative citation in a spec can plausibly mean
                if not any(os.path.exists(os.path.join(base, target))
                           for base in (tests_dir, os.path.dirname(tests_dir.rstrip(os.sep)))):
                    findings.append({"kind": "dead-citation", "file": rel, "line": i,
                                     "detail": "cites " + target + ", which does not exist: "
                                               "evidence offered that cannot be inspected",
                                     "blocking": False})

            # `code_of` comme les detecteurs d'assertions dix lignes plus bas : la meme
            # boucle lisait la ligne brute ici et le code seul la-bas, si bien que du code mis
            # en commentaire etait signale comme attente interdite (B16).
            wait = first_match(FORBIDDEN_WAITS, code_of(line))
            if wait:
                findings.append({"kind": "forbidden-wait", "file": rel, "line": i,
                                 "detail": wait, "blocking": False})
            if TAUTOLOGICAL.search(code_of(line)):
                findings.append({"kind": "tautological-assertion", "file": rel, "line": i,
                                 "detail": "le sujet de cette assertion est un litteral : sa "
                                           "valeur est connue a l'ecriture et le SUT n'y "
                                           "participe pas -- elle ne peut pas echouer",
                                 "blocking": True})
            hollow = first_match(HOLLOW_ASSERTIONS, code_of(line))
            if hollow:
                findings.append({"kind": "hollow-assertion", "file": rel, "line": i,
                                 "detail": hollow, "blocking": True})
            weak = first_match(WEAK_ASSERTIONS, code_of(line))
            if weak:
                findings.append({"kind": "weak-assertion", "file": rel, "line": i,
                                 "detail": weak, "blocking": False})
            if RAW_SELECTOR.search(line) or XPATH_SELECTOR.search(line):
                selector_raw += 1
                if not third_party:
                    findings.append({"kind": "fragile-selector", "file": rel, "line": i,
                                     "detail": line.strip()[:160], "blocking": False})
            if ROLE_SELECTOR.search(line):
                selector_role += 1

        for title, start, end in blocks:
            tests_total += 1
            body = "\n".join(lines[start - 1:end - 1])
            body_lines = join_chains(body)

            # A test whose body holds no executable statement at all — empty braces, or nothing
            # but comments describing what someone meant to write. It runs, does nothing, and
            # reports PASS, so a dashboard shows green for a feature with no coverage. Playwright
            # has `test.fixme()` for exactly this, and it reports as skipped instead.
            # Found 2026-08-09 on `Jokimbe/ComfyUI-DrawThings-gRPC`: nine such tests, no
            # `test.fixme`/`test.skip` anywhere in the repository. Blocking — a green that means
            # nothing is worse than a red.
            decl = TEST_DECL.match(lines[start - 1])
            declared_placeholder = bool(decl) and decl.group("modifier") in DECLARED_PLACEHOLDER
            if not declared_placeholder and not [
                    ln for ln in body_lines[1:]
                    if code_of(ln).strip() and not EMPTY_BODY_NOISE.match(code_of(ln))]:
                findings.append({"kind": "empty-test-body", "file": rel, "line": start,
                                 "detail": "no executable statement: " + title[:120],
                                 "blocking": True})
            real_assertions = len([
                1 for ln in body_lines
                # Les tautologiques sortent du compte au meme titre que les creuses : elles
                # etaient signalees comme bloquantes ET creditees au budget, ce qui revenait a
                # payer pour une assertion qu'on venait de declarer sans valeur.
                if EXPECT_CALL.search(code_of(ln))
                and not any(rx.search(code_of(ln)) for rx, _ in HOLLOW_ASSERTIONS)
                and not TAUTOLOGICAL.search(code_of(ln))
            ])
            # Verification held by a throwing wait or by a page object counts: it fails the test.
            real_assertions += len([1 for ln in body_lines if INDIRECT_ASSERTION.search(code_of(ln))])
            if real_assertions:
                tests_with_real_assertion += 1
            elif declared_placeholder:
                # `test.fixme(...)` reports as SKIPPED, not passed. It has no assertion by
                # design and reproaching it is reproaching the remedy.
                #
                # This exemption was added to `empty-test-body` and NOT to its twin, which kept
                # firing on the same repositories, the same lines, for the same reason — 24
                # findings across `solidcouch/solidcouch` and `Studio-Saelix/sencho`, still live
                # a batch after the campaign reported the defect as fixed.
                #
                # "Fixed for the case in front of me rather than for the class": batch 3 named
                # the pattern, batch 4 committed it again, and nobody re-ran the earlier batches
                # to notice. Found by an adversarial triage pass that did re-run them.
                pass
            else:
                findings.append({"kind": "test-without-assertion", "file": rel, "line": start,
                                 "detail": title[:160], "blocking": True})
            # Whole-evidence check: fires only when EVERY assertion in the test is one-sided.
            # A test that asserts `not.toBe(200)` and then reads the error body is fine.
            assertion_lines = [ln for ln in body_lines if EXPECT_CALL.search(code_of(ln))]
            if assertion_lines and all(first_match(SINGLE_SIDED, ln) for ln in assertion_lines):
                findings.append({"kind": "single-sided-evidence", "file": rel, "line": start,
                                 "detail": "every assertion in this test is one-sided ("
                                           + first_match(SINGLE_SIDED, assertion_lines[0])
                                           + "): it cannot distinguish the refusal under test from "
                                             "any other refusal, nor from the forbidden behaviour "
                                             "returning a different value",
                                 "blocking": False})

            tag = QAIA_TAG.search(title)
            if tag:
                tagged_tests += 1
                sid = tag.group(0).lstrip("@")
                seen_ids.add(sid)
                if sid in flagged_ids and not FLAG_IN_CODE.search(body):
                    findings.append({"kind": "flag-dropped", "file": rel, "line": start,
                                     "detail": sid + " rests on an open question in the test book "
                                               "(@low-confidence / # open: Q) and the generated test "
                                               "carries no trace of it: a red here is "
                                               "indistinguishable from a regression",
                                     "blocking": True})
            elif not third_party:
                findings.append({"kind": "untraceable-test", "file": rel, "line": start,
                                 "detail": "no @QAIA-<ID> in the test title: " + title[:120],
                                 "blocking": False})

        if has_pages_dir and fixtures_path:
            uses_fixtures = re.search(r"require\s*\(\s*['\"].*fixtures|from\s+['\"].*fixtures", text)
            if not uses_fixtures:
                findings.append({"kind": "pom-bypassed", "file": rel, "line": 1,
                                 "detail": "pages/ and fixtures exist but this spec does not import the fixtures",
                                 "blocking": False})

    # Page objects / fixtures: selectors and waits count here too.
    for path in support_files:
        rel = os.path.relpath(path, tests_dir)
        for i, line in enumerate(read(path).split("\n"), start=1):
            # Support files carry citations too, and the fifth judge found the dead one in a
            # page object rather than in a spec.
            for cm in CITATION.finditer(line):
                target = cm.group(1)
                if not any(os.path.exists(os.path.join(base, target))
                           for base in (tests_dir, os.path.dirname(tests_dir.rstrip(os.sep)))):
                    findings.append({"kind": "dead-citation", "file": rel, "line": i,
                                     "detail": "cites " + target + ", which does not exist: "
                                               "evidence offered that cannot be inspected",
                                     "blocking": False})
            wait = first_match(FORBIDDEN_WAITS, line)
            if wait:
                findings.append({"kind": "forbidden-wait", "file": rel, "line": i,
                                 "detail": wait, "blocking": False})
            if RAW_SELECTOR.search(line) or XPATH_SELECTOR.search(line):
                selector_raw += 1
                if not third_party:
                    findings.append({"kind": "fragile-selector", "file": rel, "line": i,
                                     "detail": line.strip()[:160], "blocking": False})
            if ROLE_SELECTOR.search(line):
                selector_role += 1

    if (not has_pages_dir or not fixtures_path) and not third_party:
        findings.append({"kind": "pom-missing", "file": ".", "line": 0,
                         "detail": "automate SKILL.md mandates POM-as-fixtures (pages/ + fixtures.js); "
                                   + ("pages/ missing" if not has_pages_dir else "fixtures file missing"),
                         "blocking": False})

    # Scenarios present in the test book but with no test carrying their ID.
    # L'autre sens, et c'est celui qui manquait. La tracabilite ne verifiait que
    # cahier -> test : « le titre porte-t-il un tag ? ». Un test etiquete
    # `@QAIA-US-004-043` alors qu'aucun scenario 043 n'existe marquait donc 25/25 -- alors que
    # les deux ensembles etaient deja en main. **Un tag qui ne resout rien est pire que pas de
    # tag : il ressemble a de la tracabilite.** Sept cas dans la vitrine du projet
    # (`US-004-039` a `-045`), trouves en la relisant, jamais par l'outil.
    # Bloquant : un lecteur ne peut pas distinguer un scenario supprime d'un identifiant invente.
    # ... mais UNIQUEMENT dans l'espace de noms du cahier. Une suite porte legitimement des
    # tags d'autres familles -- `@QAIA-VIS-001`, `@QAIA-A11Y-...`, `@QAIA-CP-...` -- pour des
    # tests visuels, d'accessibilite ou de contrat qui n'ont aucun scenario Gherkin et n'en
    # attendent pas. La premiere version signalait 18 cas la ou 7 sont reels : elle reprochait
    # a la suite d'avoir des espaces de noms separes, ce qui est le bon choix.
    # Encore « la regle est-elle applicable ? » -- la meme faute que les 279 selecteurs.
    def namespace(sid):
        parts = sid.rsplit("-", 1)
        return parts[0] if len(parts) == 2 and parts[1].isdigit() else sid

    book_namespaces = {namespace(s) for s in feature_ids}
    dangling = sorted(s for s in (seen_ids - feature_ids)
                      if namespace(s) in book_namespaces) if feature_ids else []
    for sid in dangling:
        findings.append({"kind": "test-without-scenario", "file": "<suite>", "line": 0,
                         "detail": sid + " — aucun scenario de ce nom dans le cahier de test",
                         "blocking": True})

    orphan_scenarios = sorted(feature_ids - seen_ids) if feature_ids else []
    for sid in orphan_scenarios:
        findings.append({"kind": "scenario-without-test", "file": "<testbook>", "line": 0,
                         "detail": sid, "blocking": False})

    def pct(num, den):
        return 0.0 if den == 0 else num / den

    selectors_total = selector_role + selector_raw
    selectors_applicable = selectors_total > 0
    if selectors_total == 0:
        # Ni punir ni recompenser : la dimension sort du budget et le reste est renormalise
        # (meme traitement que le mode tiers, cinquante lignes plus bas). Elle valait 25 points
        # pleins, si bien qu'une suite sans aucun localisateur encaissait la note maximale sur
        # une dimension qu'elle n'exerce pas -- « non applicable » note comme « parfait » (B13).
        robust_selectors = 0.0
        findings.append({"kind": "no-selector-detected", "file": ".", "line": 0,
                         "detail": "no locator call found in specs or page objects; the selector "
                                   "dimension is not applicable and was not penalised",
                         "blocking": False})
    else:
        robust_selectors = round(25 * pct(selector_role, selectors_total), 1)

    if third_party:
        # Only the dimensions that transfer. Assertion substance is 30 of the 100-point budget;
        # rescaling it to 100 keeps the number comparable ACROSS third-party suites while making
        # it plainly incomparable with a QAIA score — which it must be, since it answers a
        # narrower question. The three dropped lines are reported as excluded, never as zeros:
        # a zero would read as a failing grade for declining to adopt our conventions.
        budget = {"substantive_assertions": round(100 * pct(tests_with_real_assertion, tests_total), 1)}
        findings.append({"kind": "third-party-mode", "file": ".", "line": 0,
                         "detail": "third-party suite: pom_as_fixtures, traceability and "
                                   "robust_selectors are QAIA conventions and were EXCLUDED from "
                                   "the budget, not scored zero. This score judges assertion "
                                   "substance only and is not comparable with a QAIA score.",
                         "blocking": False})
    else:
        budget = {
            "substantive_assertions": round(30 * pct(tests_with_real_assertion, tests_total), 1),
            "robust_selectors": robust_selectors,
            # Credite sur le CONTENU, pas sur l'existence de deux chemins : un `pages/`
            # vide et un `fixtures.js` vide encaissaient les 20 points pleins. Moitie pour la
            # structure presente, moitie pour des objets de page qui portent effectivement des
            # localisateurs -- c'est ce que la dimension pretend mesurer (B12).
            "pom_as_fixtures": (10.0 if (has_pages_dir and fixtures_path) else 0.0)
                               + (10.0 if pom_has_locators else 0.0),
            # Un test dont le tag ne resout aucun scenario ne compte plus comme trace.
            "traceability": round(25 * pct(max(0, tagged_tests - len(dangling)), tests_total), 1),
        }
    if not third_party and not selectors_applicable:
        # `robust_selectors` pesait 25 des 100 points. On renormalise les trois dimensions
        # restantes sur 100 pour que la note reste comparable, et on le DIT -- une note
        # renormalisee en silence serait exactement le genre de chiffre que ce projet refuse.
        del budget["robust_selectors"]
        remaining = 75.0
        budget = dict((k, round(v * 100.0 / remaining, 1)) for k, v in budget.items())

    score = round(sum(budget.values()), 1)

    return {
        "score": score,
        "budget": budget,
        "counts": {
            "spec_files": len(spec_files),
            "tests": tests_total,
            "tests_with_real_assertion": tests_with_real_assertion,
            "role_selectors": selector_role,
            "raw_selectors": selector_raw,
            "tagged_tests": tagged_tests,
            "testbook_scenarios": len(feature_ids),
            "scenarios_without_test": len(orphan_scenarios),
        },
        "findings": findings,
    }


# ------------------------------------------------------------------------- mutation track

def _bump_number(txt):
    try:
        if "." in txt:
            return str(float(txt) + 1)
        return str(int(txt) + 1)
    except ValueError:
        return None


MUTANT_MARK = "__QAIA_MUT__"

# Playwright prints this and exits 1 when the filters select zero tests. Exit 1 also means "a test
# failed", so the two must be told apart by the output or every unselected mutation reads as killed.
NO_TESTS_FOUND = re.compile(r"No tests found", re.I)


def mutate_line(line):
    """Return (mutated_line, description) or (None, None) if nothing mutable here.

    Every mutation makes the expectation FALSE for an app that behaves as the original
    asserted. A correct, load-bearing assertion must therefore turn red.
    """
    # `.not.X(...)` -> `X(...)`: dropping the negation flips the expectation.
    m = re.search(r"\.\s*not\s*\.", line)
    if m:
        return line[:m.start()] + "." + line[m.end():], "drop .not."

    pairs = [("toBeVisible", "toBeHidden"), ("toBeHidden", "toBeVisible"),
             ("toBeEnabled", "toBeDisabled"), ("toBeDisabled", "toBeEnabled"),
             ("toBeChecked", "toBeHidden")]
    for src, dst in pairs:
        m = re.search(r"\.\s*" + src + r"\s*\(", line)
        if m:
            return line[:m.start()] + "." + dst + "(" + line[m.end():], "%s -> %s" % (src, dst)

    # Numeric matchers: shift the expected value so the real one no longer satisfies it.
    for name in ("toHaveCount", "toHaveLength", "toBeLessThan", "toBeLessThanOrEqual"):
        m = re.search(r"\.\s*" + name + r"\s*\(\s*(-?\d+(?:\.\d+)?)\s*\)", line)
        if m:
            if name.startswith("toBeLess"):
                new = "-1"
            else:
                new = _bump_number(m.group(1))
            if new is not None:
                return line[:m.start(1)] + new + line[m.end(1):], "%s(%s) -> %s(%s)" % (name, m.group(1), name, new)
    for name in ("toBeGreaterThan", "toBeGreaterThanOrEqual"):
        m = re.search(r"\.\s*" + name + r"\s*\(\s*(-?\d+(?:\.\d+)?)\s*\)", line)
        if m:
            return line[:m.start(1)] + "999999999" + line[m.end(1):], "%s(%s) -> %s(999999999)" % (name, m.group(1), name)

    # String matchers: append a marker no real UI text can contain.
    for name in ("toHaveText", "toContainText", "toHaveValue", "toHaveAttribute", "toContain", "toHaveTitle"):
        m = re.search(r"\.\s*" + name + r"\s*\(\s*(['\"])((?:\\.|(?!\1).)*)\1", line)
        if m:
            return (line[:m.end(2)] + MUTANT_MARK + line[m.end(2):],
                    "%s('%s') -> '...%s'" % (name, m.group(2)[:40], MUTANT_MARK))

    # Regex matchers (toHaveURL(/x/)): replace with a pattern that cannot match.
    m = re.search(r"\.\s*(toHaveURL|toHaveText|toContainText)\s*\(\s*/((?:\\.|[^/])*)/", line)
    if m:
        return (line[:m.start(2)] + "qaia_mut_never_matches" + line[m.end(2):],
                "%s(/%s/) -> /qaia_mut_never_matches/" % (m.group(1), m.group(2)[:40]))

    # `toEqual([])` / `toEqual({})` -- "nothing was found". The whole a11y idiom is
    # `expect(violations).toEqual([])`, and no operator above touches it: the two a11y assertions of
    # the showcase suite were simply absent from the mutation corpus, silently, which is the same
    # class of gap as counting an unrun mutation as a kill. Requiring a non-empty collection makes
    # the expectation false for an application that really has no violations.
    m = re.search(r"\.\s*(toEqual|toStrictEqual)\s*\(\s*\[\s*\]\s*\)", line)
    if m:
        return (line[:m.start()] + "." + m.group(1) + "(['" + MUTANT_MARK + "'])" + line[m.end():],
                "%s([]) -> %s(['%s'])" % (m.group(1), m.group(1), MUTANT_MARK))
    m = re.search(r"\.\s*(toEqual|toStrictEqual)\s*\(\s*\{\s*\}\s*\)", line)
    if m:
        return (line[:m.start()] + "." + m.group(1) + "({ " + MUTANT_MARK + ": true })" + line[m.end():],
                "%s({}) -> %s({%s: true})" % (m.group(1), m.group(1), MUTANT_MARK))

    # Generic equality on a literal.
    m = re.search(r"\.\s*(toBe|toEqual|toStrictEqual)\s*\(\s*(-?\d+(?:\.\d+)?)\s*\)", line)
    if m:
        new = _bump_number(m.group(2))
        if new is not None:
            return line[:m.start(2)] + new + line[m.end(2):], "%s(%s) -> %s(%s)" % (m.group(1), m.group(2), m.group(1), new)
    m = re.search(r"\.\s*(toBe|toEqual)\s*\(\s*(true|false)\s*\)", line)
    if m:
        flip = "false" if m.group(2) == "true" else "true"
        return line[:m.start(2)] + flip + line[m.end(2):], "%s(%s) -> %s(%s)" % (m.group(1), m.group(2), m.group(1), flip)
    m = re.search(r"\.\s*(toBe|toEqual)\s*\(\s*(['\"])((?:\\.|(?!\2).)*)\2", line)
    if m:
        return (line[:m.end(3)] + MUTANT_MARK + line[m.end(3):],
                "%s('%s') -> '...%s'" % (m.group(1), m.group(3)[:40], MUTANT_MARK))

    return None, None


def run_cmd(cmd, cwd, timeout):
    """`cmd` est une LISTE argv, jamais une chaine, et jamais interpretee par un shell.

    Voir la faille B8 : un titre de test lu dans le depot scanne s'executait. Le selfcheck
    verifie cette propriete en relisant le source de cette fonction -- il cherche donc
    litteralement le mot-cle interdit, raison pour laquelle il ne peut pas etre ecrit ici.
    """
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=False, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.returncode, p.stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT after %ss" % timeout
    except OSError as exc:
        return None, "OSError: %s" % exc


def baseline(run_cwd, base_cmd, timeout):
    """Which tests pass before any mutation? Only those are meaningful mutation targets."""
    code, out = run_cmd(base_cmd, run_cwd, timeout)
    if code is None:
        return None, out
    return code, out


def grep_pattern(title):
    """Le titre devient un motif litteral. Il est passe en ARGUMENT (argv), pas dans une chaine
    de shell : les metacaracteres de regex sont donc les seuls a neutraliser ici. Cette fonction
    s'appelait `escape_grep` et etait utilisee comme un echappement de shell alors qu'elle n'en
    est pas un -- c'etait la faille B8."""
    return re.sub(r"([.^$*+?()\[\]{}|\\/])", r"\\\1", title)


# Fichiers actuellement mutes, avec leur texte d'origine. Le mutant est construit pour que
# les assertions PASSENT : le laisser sur disque est pire que de ne rien faire. Un `finally`
# ne couvre ni Ctrl-C ni SIGTERM -- d'ou le filet ci-dessous. Seul SIGKILL reste hors de
# portee, et c'est dit dans le README de l'outil plutot que tu.
_PENDING = {}


def _restore_one(path):
    text = _PENDING.pop(path, None)
    if text is None:
        return
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    except Exception as exc:
        sys.stderr.write("ATTENTION : %s est reste MUTE (restauration impossible : %s)\n"
                         % (path, exc))


def _restore_all(*_a):
    for path in list(_PENDING):
        _restore_one(path)


atexit.register(_restore_all)
for _sig in ("SIGINT", "SIGTERM", "SIGBREAK"):
    if hasattr(signal, _sig):
        try:
            signal.signal(getattr(signal, _sig),
                          lambda *_a: (_restore_all(), sys.exit(130)))
        except (ValueError, OSError):
            pass  # pas le thread principal : le atexit suffit


def mutation_track(spec_files, tests_dir, run_cwd, base_cmd, max_mutations, timeout):
    code, out = baseline(run_cwd, base_cmd, timeout)
    if code is None:
        return {"status": "blocked", "blocker": "baseline run could not execute: " + out[-800:],
                "total": 0, "killed": 0, "survived": []}
    if code != 0:
        return {"status": "blocked",
                "blocker": ("baseline suite is not green (exit %s) — mutation results would be "
                            "meaningless because a test that was already red cannot prove anything. "
                            "Fix the suite first. Tail of output:\n%s" % (code, out[-800:])),
                "total": 0, "killed": 0, "survived": []}

    candidates = []
    for path in spec_files:
        text = read(path)
        lines = text.split("\n")
        blocks = split_tests(text)
        for i, line in enumerate(lines, start=1):
            if not EXPECT_CALL.search(line):
                continue
            if any(rx.search(line) for rx, _ in HOLLOW_ASSERTIONS):
                continue  # already reported as blocking by the static track
            mutated, desc = mutate_line(line)
            if mutated is None or mutated == line:
                continue
            owner = None
            for title, start, end in blocks:
                if start <= i < end:
                    owner = title
                    break
            candidates.append({"file": path, "line": i, "test": owner,
                               "original": line.strip()[:200], "mutation": desc,
                               "mutated_line": mutated})

    skipped = 0
    if max_mutations and len(candidates) > max_mutations:
        skipped = len(candidates) - max_mutations
        candidates = candidates[:max_mutations]

    survived, killed, errored, not_run = [], 0, [], []
    for cand in candidates:
        path = cand["file"]
        original_text = read(path)
        lines = original_text.split("\n")
        lines[cand["line"] - 1] = cand["mutated_line"]
        _PENDING[path] = original_text
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
            cmd = list(base_cmd)
            if cand["test"]:
                cmd = list(base_cmd) + ["--grep", grep_pattern(cand["test"])]
            rc, rout = run_cmd(cmd, run_cwd, timeout)
        finally:
            _restore_one(path)

        rel = os.path.relpath(path, tests_dir)
        if rc is not None and NO_TESTS_FOUND.search(rout or ""):
            # The runner selected nothing -- typically because --run-cmd filters to one Playwright
            # project while the candidate list is built from every spec under --tests-dir. Playwright
            # exits 1 on "No tests found", which is indistinguishable from a red test at the exit-code
            # level: this branch used to be counted as a KILL. It proved nothing. Found 2026-08-08 by
            # re-running the same suite under a different --project and getting the identical total.
            not_run.append({"file": rel, "line": cand["line"], "test": cand["test"],
                            "assertion": cand["original"], "mutation": cand["mutation"]})
        elif rc is None:
            errored.append({"file": rel, "line": cand["line"], "reason": rout[-300:]})
        elif rc == 0:
            survived.append({"file": rel, "line": cand["line"], "test": cand["test"],
                             "assertion": cand["original"], "mutation": cand["mutation"]})
        else:
            killed += 1

    return {
        "status": "ok",
        "blocker": "",
        "total": len(candidates),
        "killed": killed,
        "survived": survived,
        "errored": errored,
        "not_run": not_run,
        "skipped_over_cap": skipped,
        # `killed` is now over `total - len(not_run)`. A report that divides by `total` while
        # not_run is non-empty overstates the coverage, which is exactly the bug this field exists
        # to make visible.
        "exercised": len(candidates) - len(not_run),
    }


# ------------------------------------------------------------------------------- assembly

def collect_feature_ids(testbook):
    ids = set()
    if not testbook:
        # Two values, like every other exit: `--testbook` is optional, and this early return
        # once yielded a bare `ids`, so the caller's two-way unpack crashed on any run without
        # a test book. Never caught because the tool had only ever scored QAIA-generated
        # suites, which always carry one — the first third-party suite hit it immediately.
        return ids, set()
    paths = []
    if os.path.isfile(testbook):
        paths = [testbook]
    else:
        for root, dirs, files in os.walk(testbook):
            dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
            paths += [os.path.join(root, f) for f in files if f.endswith(".feature")]
    flagged = set()
    for p in paths:
        text = read(p)
        for m in FEATURE_TAG.finditer(text):
            ids.add(m.group(1))
        # A scenario is flagged when the marker sits on its tag line or in the comment block just
        # above it. Walk the file and attribute a pending flag to the next scenario ID seen.
        pending_flag = False
        for line in text.split(NL):
            if FEATURE_FLAGGED_SCENARIO.search(line):
                pending_flag = True
            m = FEATURE_TAG.search(line)
            if m and pending_flag:
                flagged.add(m.group(1))
            if line.strip().startswith("Scenario"):
                pending_flag = False
    return ids, flagged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tests-dir", required=True, help="directory holding the generated .spec files")
    ap.add_argument("--testbook", help="test book dir or .feature file, for traceability cross-check")
    ap.add_argument("--run-cwd", help="cwd for the Playwright run (defaults to --tests-dir)")
    ap.add_argument("--run-cmd", default="npx playwright test",
                    help="commande qui lance la suite (decoupee par shlex, jamais passee a un shell)")
    ap.add_argument("--max-mutations", type=int, default=25, help="cap on mutations (0 = no cap)")
    ap.add_argument("--timeout", type=int, default=300, help="per-run timeout in seconds")
    ap.add_argument("--skip-mutation", action="store_true", help="static track only")
    ap.add_argument("--third-party", action="store_true",
                    help="score a suite QAIA did not generate: QAIA-convention rules are excluded "
                         "from the budget rather than scored zero (see static_track docstring)")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    tests_dir = os.path.abspath(args.tests_dir)
    if not os.path.isdir(tests_dir):
        print("error: --tests-dir does not exist: %s" % tests_dir, file=sys.stderr)
        return 2
    spec_files, foreign_runner_files = find_spec_files(tests_dir)
    if foreign_runner_files:
        print("note: %d .spec file(s) skipped — they import Vitest/Jest/Mocha, and every rule here "
              "is Playwright-specific:" % len(foreign_runner_files), file=sys.stderr)
        for p in foreign_runner_files[:10]:
            print("        " + os.path.relpath(p, tests_dir), file=sys.stderr)
    if not spec_files:
        print("error: no Playwright .spec.* files under %s" % tests_dir, file=sys.stderr)
        return 2

    support_files = find_support_files(tests_dir, spec_files)
    # If pages/ lives one level up (the automation/{tests,pages} layout), its files are
    # support files too -- otherwise selectors and citations there are invisible.
    parent = os.path.dirname(tests_dir.rstrip(os.sep))
    if os.path.isdir(os.path.join(parent, 'pages')):
        support_files += [p for p in find_support_files(os.path.join(parent, 'pages'), spec_files)
                          if p not in support_files]

    feature_ids, flagged_ids = collect_feature_ids(args.testbook)
    static = static_track(spec_files, support_files, tests_dir, feature_ids, flagged_ids,
                          third_party=args.third_party)

    if args.skip_mutation:
        mutation = {"status": "skipped", "blocker": "--skip-mutation requested",
                    "total": 0, "killed": 0, "survived": []}
    else:
        # shlex des l'entree : `run_cmd` n'accepte plus qu'une liste argv (B8).
        mutation = mutation_track(spec_files, tests_dir, os.path.abspath(args.run_cwd or tests_dir),
                                  shlex.split(args.run_cmd, posix=(os.name != "nt")),
                                  args.max_mutations, args.timeout)

    blocking = []
    for f in static["findings"]:
        if f.get("blocking"):
            blocking.append("%s: %s (%s:%s)" % (f["kind"], f["detail"][:90], f["file"], f["line"]))
    for s in mutation.get("survived", []):
        blocking.append("mutation-survivor: %s (%s:%s) — %s" % (s["assertion"][:90], s["file"], s["line"], s["mutation"]))
    er = mutation.get("errored") or []
    if er:
        # Bloquant pour la meme raison que `not_run` : une mutation qui n'a pas pu s'executer
        # n'a rien prouve, et la compter pour rien fait lire « aucun survivant » a une campagne
        # qui n'a rien mesure du tout.
        files = sorted(set(x["file"] for x in er))
        blocking.append("mutation-errored: %d mutation(s) n'ont pas pu s'executer (%s) — elles ne "
                        "comptent ni comme tuees ni comme survivantes, et le taux les exclut"
                        % (len(er), ", ".join(files)))

    nr = mutation.get("not_run") or []
    if nr:
        # Blocking, not informational: a run that reports "n/n killed" while n assertions were never
        # executed is the silent truncation this project refuses to publish. Widen --run-cmd (drop
        # the --project filter, or run one project per invocation) until this list is empty.
        files = sorted(set(x["file"] for x in nr))
        blocking.append("mutation-not-run: %d assertion(s) were never executed by --run-cmd "
                        "(the runner selected no test) in %s — the kill count excludes them"
                        % (len(nr), ", ".join(files)))

    result = {
        "tool": "automation_score.py",
        "version": 1,
        "inputs": {"tests_dir": tests_dir, "testbook": args.testbook, "run_cmd": args.run_cmd},
        "static": static,
        "mutation": mutation,
        "blocking": {"failed": bool(blocking), "reasons": blocking},
        "llm_rubric": None,
        "note": ("static score and the LLM rubric score are never summed — see eval/RUBRIC.md, "
                 "case US 676266. A blocking failure stands regardless of either score."),
    }

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("written: %s" % args.out)
    else:
        print(text)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
