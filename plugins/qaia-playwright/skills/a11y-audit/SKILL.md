---
name: a11y-audit
description: Generate and run accessibility tests (axe-core via Playwright, WCAG 2 A/AA) against a running app, plus the keyboard/focus/contrast checks no scanner can perform, reporting violations by severity. Use when a test book or an app needs accessibility coverage, when an accessibility regulation applies (EAA, EN 301 549, RGAA, Section 508) — the oracle is WCAG 2.1 A/AA in every case, and no run here is a compliance verdict; see references/regulations.md — or when a user asks whether a screen is accessible.
---

# a11y-audit — accessibility via axe-core, plus the pass axe cannot do

Reference: [`examples/medibook/tests/a11y.booking.spec.js`](https://github.com/QAIA-Project/QAIA/blob/main/examples/medibook/tests/a11y.booking.spec.js) (0 serious/critical violations).

Tooling is fixed: **axe-core driven through Playwright** — the de-facto standard for automated
WCAG checks, and it reuses the browser context the functional tests already run in rather than
introducing a second driver stack.

**Naming a regulation is an implicit promise about what the run means.** This skill's oracle is
**WCAG 2.1 A/AA and nothing else**. EN 301 549, the EAA, RGAA 4.1 and Section 508 are all built on
WCAG, which is why the run helps with all of them — and each adds obligations WCAG does not
contain, which is why a green run is **never** a compliance verdict for any of them.

RGAA in particular is a *test method*, not a synonym: **106 numbered criteria, a mandatory page
sample, and a compliance rate this skill's output cannot produce** — different numerator, different
denominator, different sample. Load `references/regulations.md` before answering any question that
contains the word "compliant", and use the wording it gives.

**The number that governs this skill: automated tooling detects roughly a third of WCAG success
criteria.** The rest are not "advanced" — they are keyboard access, focus visibility, and
alt-text relevance, i.e. the failures that actually stop a disabled user. A skill that ships
only the axe pass and calls the result "accessible" would be wrong about the majority of the
standard, which is why the manual pass below is a required step and not an appendix.

## Install

```bash
npm i -D @axe-core/playwright axe-core
```

Pin both in `package.json` (`@axe-core/playwright` ^4.12.1, `axe-core` ^4.12.1 at the time of
writing). `axe-core` is a peer of the Playwright wrapper: let them drift and rule ids move
between versions, which silently changes what a "0 violations" run means. Record the resolved
`axe-core` version in the report — a violation count is not comparable across versions.

## Steps

1. **List the screens under audit** — every key screen the test book covers, plus any the user
   names. A screen behind a form submission or a modal counts as its own screen; auditing the
   page that precedes it audits nothing.
2. **Automated pass** — for each screen: navigate, **assert a real element of that screen is
   visible** (client-rendered apps serve an empty shell such as `<div id="app"></div>`, and
   auditing before paint returns 0 violations), then run
   `AxeBuilder({page}).withTags(['wcag2a','wcag2aa']).analyze()`.
3. **Filter and fail by `impact`** — axe labels every violation `critical`, `serious`,
   `moderate` or `minor`. Fail the test on `critical` + `serious`; report `moderate` + `minor`
   without failing. See `references/impact-and-reporting.md` for why that line and not another,
   and for the `results.incomplete` trap.
4. **Manual pass** — run the checks axe cannot: keyboard reachability, focus order, focus
   visibility, contrast in non-default states, and alt-text relevance. Protocol, expected
   results and how to record them: `references/manual-pass.md`. This step is **not optional**;
   if it was not run, the report says so in place of its results.
5. **Tag and report** — tag each automated test `@QAIA-A11Y-<NNN>`; write the report to
   `.qaia/reports/<US-ID>/a11y/report.md` with the full violation list, the manual-pass results,
   and the axe-core version. Attach the raw axe JSON next to it.

## Guardrails

- Report violation ids honestly; never suppress a rule to make a suite green. Disabling a rule
  is a decision with a name attached, recorded in the report with its reason — not a config edit.
- **Never write "accessible" or "screen X is covered".** The only claim a green automated run
  supports is *no axe-detectable serious/critical issue on that screen, with axe-core <version>*.
  The manual pass widens that claim; it still does not make it "conformant", which is an audit
  verdict a human accessibility specialist issues, not this skill.
- A11y is additive — it does not replace functional E2E; run alongside `automate`.
- If an accessibility **regulation** was named as the reason for this audit, say explicitly in
  the report that this skill produces evidence toward conformance and is not itself a
  conformance statement. See `references/impact-and-reporting.md`.
