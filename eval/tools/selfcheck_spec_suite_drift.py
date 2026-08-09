#!/usr/bin/env python3
"""Self-check for spec_suite_drift.py, on fixtures built in a temporary directory.

Two directions, because a detector that fires on everything discriminates nothing:

  DRIFTING  -- a specification and a suite that disagree in the three ways the tool names.
               Each rule must fire, exactly once, on the planted line.
  CLEAN     -- a specification and a suite that agree. Nothing may fire.

The founding case is `realworld-apps/realworld` (2026-08-09): the spec promises 409 on
`POST /users`, the suite mocks that exact case as 400, and no test exercises 409. Both halves
look self-consistent from inside, which is why only a cross-comparison finds it.

Run: python eval/tools/selfcheck_spec_suite_drift.py
Exits non-zero on the first failure.
"""
import io
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_suite_drift as D  # noqa: E402

failures = []


def check(label, got, want):
    if got != want:
        failures.append("%s\n    got:  %r\n    want: %r" % (label, got, want))


SPEC = """
openapi: 3.0.0
info: {title: fixture, version: '1'}
paths:
  /users:
    post:
      responses:
        '201': {description: created}
        '409': {description: conflict}
  /articles/{slug}:
    get:
      responses:
        '200': {description: ok}
        '404': {description: missing}
"""

DRIFTING = """
import { test, expect } from '@playwright/test';

test('registration rejects a duplicate email', async ({ page }) => {
  await page.goto('/register');
  await mockApiError(page, '/users', 400, { errors: { email: ['is already taken'] } });
  await page.click('button[type="submit"]');
});

test('an unknown article shows a message', async ({ page }) => {
  await page.route('/api/articles/some-slug', r => r.fulfill({ status: 404 }));
  await expect(page.locator('.msg')).toBeVisible();
});

test('the newsletter endpoint is reachable', async ({ page }) => {
  await page.route('/api/newsletter', r => r.fulfill({ status: 200 }));
});
"""

CLEAN = """
import { test, expect } from '@playwright/test';

test('registration rejects a duplicate email', async ({ page }) => {
  await mockApiError(page, '/users', 409, { errors: { email: ['is already taken'] } });
  await expect(page.locator('.msg')).toBeVisible();
});

test('an unknown article shows a message', async ({ page }) => {
  await page.route('/api/articles/some-slug', r => r.fulfill({ status: 404 }));
  await expect(page.locator('.msg')).toBeVisible();
});
"""


def run(suite_src):
    tmp = tempfile.mkdtemp(prefix="qaia-drift-")
    try:
        spec = os.path.join(tmp, "openapi.yml")
        io.open(spec, "w", encoding="utf-8", newline="\n").write(SPEC)
        tests = os.path.join(tmp, "tests")
        os.makedirs(tests)
        io.open(os.path.join(tests, "a.spec.ts"), "w", encoding="utf-8", newline="\n").write(suite_src)
        declared = D.load_spec(spec)
        pairs, seen, all_status = D.scan_suite(tests)
        return D.compare(declared, pairs, seen, all_status)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- 1. path normalisation ------------------------------------------------------------------
check("an /api prefix is stripped", D.norm("/api/users"), "/users")
check("a template parameter collapses", D.norm("/api/articles/{slug}"), "/articles/{}")
check("a JS interpolation collapses", D.norm("/articles/${slug}"), "/articles/{}")
# A wildcard is a SEGMENT, not its absence: shaving `/profiles/*` to `/profiles` matched no
# template and produced a false `path-not-in-spec` on the founding target.
check("a wildcard segment becomes a parameter", D.norm("/api/profiles/*"), "/profiles/{}")
check("a query string is dropped", D.norm("/articles?limit=5"), "/articles")

# --- 2. concrete paths resolve to their template --------------------------------------------
declared = {"/articles/{}": {"200"}, "/users": {"201"}}
check("a concrete segment resolves", D.resolve("/articles/some-slug", declared), "/articles/{}")
check("an exact path resolves to itself", D.resolve("/users", declared), "/users")
check("a different arity does not resolve", D.resolve("/articles/a/b", declared), None)
check("an unknown path resolves to nothing", D.resolve("/newsletter", declared), None)

# --- 3. the drifting pair: each rule fires, exactly once -------------------------------------
found = run(DRIFTING)
by_rule = {}
for f in found:
    by_rule.setdefault(f["rule"], []).append(f)

check("the undeclared status is reported once", len(by_rule.get("undeclared-status", [])), 1)
if by_rule.get("undeclared-status"):
    f = by_rule["undeclared-status"][0]
    check("...on /users", f["path"], "/users")
    check("...for the 400 the suite mocks", f["status"], "400")

check("the unexercised status is reported once", len(by_rule.get("unexercised-status", [])), 1)
if by_rule.get("unexercised-status"):
    check("...and it is the 409 the spec promises", by_rule["unexercised-status"][0]["status"], "409")

check("the path absent from the spec is reported once", len(by_rule.get("path-not-in-spec", [])), 1)
if by_rule.get("path-not-in-spec"):
    check("...and it is /newsletter", by_rule["path-not-in-spec"][0]["path"], "/newsletter")

# `page.goto('/register')` is a page route, not an endpoint. Counting it made the block cite two
# paths, which the conservative pairing then skipped -- silencing the very finding above.
check("a navigation route is never reported as an endpoint",
      [f for f in found if f["path"] == "/register"], [])

# --- 4. the clean pair: nothing fires ---------------------------------------------------------
check("an agreeing spec and suite produce no finding", run(CLEAN), [])

if failures:
    print("selfcheck_spec_suite_drift: %d FAILURE(S)\n" % len(failures))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("selfcheck_spec_suite_drift: ok")
