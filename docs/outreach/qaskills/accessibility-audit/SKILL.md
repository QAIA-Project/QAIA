---
name: Accessibility Audit - axe-core plus the pass axe cannot do
description: Run axe-core through Playwright on every key screen, fail on critical and serious only, then run the seven manual checks a DOM scanner structurally cannot perform - because automated tooling detects roughly a third of WCAG success criteria and the other two thirds are what actually stops a disabled user.
version: 1.0.0
author: opaland
license: MIT
tags: [accessibility, a11y, wcag, axe-core, playwright, keyboard]
testingTypes: [accessibility, e2e]
frameworks: [playwright]
languages: [typescript, javascript]
domains: [web]
agents: [claude-code, cursor, github-copilot, codex]
---

# Accessibility Audit — axe-core, plus the pass axe cannot do

> **Standalone adaptation.** Self-contained version of the `a11y-audit` skill from
> [QAIA](https://github.com/QAIA-Project/QAIA) (MIT). The canonical version and its `references/`
> live in that repository. QAIA is pre-alpha and says so.

## Naming a regulation is an implicit promise

This skill's oracle is **WCAG 2.1 A/AA, and nothing else** — axe-core plus the manual pass.

EN 301 549, the European Accessibility Act, France's RGAA 4.1 and Section 508 are all *built on*
WCAG, which is why this run helps with every one of them. Each also adds obligations WCAG does not
contain, which is why a green run is **never** a compliance verdict for any of them.

**RGAA 4.1 in particular is a test *method*, not a synonym for WCAG:** 106 numbered criteria over
13 themes, a mandatory sample of pages, and a compliance rate computed as
`criteria compliant / criteria applicable` over that sample. This skill reports violations by
severity over the screens you point it at — **different numerator, different denominator, different
sample.** No axe-core rule maps one-to-one onto an RGAA criterion, and the *déclaration
d'accessibilité* is a legal artefact with a mandatory template that nothing here produces.

Say this:

> ✅ *"axe-core and the manual pass found no WCAG 2.1 AA violation on these screens. That covers
> roughly a third of the success criteria automatically; the rest, and the RGAA method itself,
> require a human audit."*

Refuse this:

> ❌ *"The application is RGAA compliant."*

What this skill legitimately gives a regulated audit is a fast, reproducible pass over the
automatable share, plus the keyboard, focus and contrast checks no scanner performs. It **narrows**
the manual audit. It does not replace it.

## The number that governs this skill

**Automated tooling detects roughly a third of WCAG success criteria.**

The other two thirds are not exotic. They are keyboard access, focus visibility, and whether
alt text says anything — the failures that actually stop a disabled user. A skill that ships only
the axe pass and calls the result "accessible" is wrong about the majority of the standard.

That is why the manual pass here is **a required step, not an appendix**.

## Install

```bash
npm i -D @axe-core/playwright axe-core
```

Pin both. `axe-core` is a peer of the Playwright wrapper; let them drift and rule ids move between
versions, which silently changes what "0 violations" means. **Record the resolved `axe-core`
version in the report** — a violation count is not comparable across versions.

## Steps

### 1. List the screens

Every key screen, plus any the user names. **A screen behind a form submission or a modal counts
as its own screen** — auditing the page that precedes it audits nothing.

### 2. Automated pass

For each screen: navigate, **assert a real element of that screen is visible**, then analyse.

That assertion is not ceremony. Client-rendered apps serve an empty shell (`<div id="app"></div>`),
and auditing before paint returns **0 violations** — a green run that examined nothing.

```js
await expect(page.getByRole('heading', { name: 'Book an appointment' })).toBeVisible();
const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
```

### 3. Fail on `critical` + `serious`, report the rest

```js
const blocking   = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
const reportable = results.violations.filter(v => v.impact === 'moderate' || v.impact === 'minor');
```

| `impact` | In practice | Decision |
|---|---|---|
| `critical` | blocks the user outright — no alt on a functional image, no label on a required field | **FAIL** |
| `serious` | severe barrier with a difficult workaround — contrast failure, missing form label | **FAIL** |
| `moderate` | real degradation, workaround exists — heading order skips a level | report, do not fail |
| `minor` | annoyance or best-practice drift | report, do not fail |

**Why the line sits there and not elsewhere.** Below it, findings are frequent and often
stylistic, and they produce the failure mode that kills accessibility work: a build red for a
skipped heading level, which teaches the team to disable the check. Above it, findings correspond
to a user who cannot complete the task at all. It is a deliberate trade of completeness for the
check staying switched on — and everything below is still *reported*, so nothing is hidden, only
un-gated.

**Do not move this line to make a suite green.** Downgrading a `serious` finding is the
accessibility equivalent of raising a visual-diff tolerance until the test passes. If a `serious`
violation is accepted, it is accepted **by a named human, with a reason and a date, in the
report** — not by editing a filter.

### 4. The manual pass — mandatory

Seven checks, each with its protocol, its expected result, and the way it is usually got wrong.
Run every one on every screen and **record a result for each, including "not applicable" with the
reason**.

**M1 — Keyboard reachability** (WCAG 2.1.1). From a fresh load, `Tab` to the end without touching
the mouse. Every interactive element must be reachable and operable.
*The failure axe misses:* `<div onclick=...>` with no `tabindex` and no `role` — visible,
clickable, entirely absent from the tab sequence. The DOM is not malformed, it is simply not
focusable.

```js
const order = [];
for (let i = 0; i < 40; i++) {
  await page.keyboard.press('Tab');
  order.push(await page.evaluate(() => {
    const el = document.activeElement;
    return el ? `${el.tagName}${el.id ? '#' + el.id : ''}` : 'NONE';
  }));
}
```

**M2 — Keyboard trap** (2.1.2). `Tab` *into* every modal, date picker, embedded player and custom
dropdown, then try to leave with `Tab` / `Shift+Tab` / `Escape` alone.

**M3 — Focus order** (2.4.3). The tab sequence must follow the visual and logical order. CSS
reordering (`order`, `grid-area`, absolute positioning) breaks this while the DOM stays valid.

**M4 — Focus visibility** (2.4.7). Every focused element shows a visible indicator. The classic
failure is a global `outline: none` in a reset, never restored.

**M5 — Contrast in non-default states** (1.4.3 / 1.4.11). axe measures the default state. Check
hover, focus, disabled, error, and placeholder text — where contrast is most often lost.

**M6 — Text alternatives that mean something** (1.1.1). axe checks an `alt` attribute *exists*.
Only a human can tell that `alt="image"` says nothing.

**M7 — Dynamic changes are announced** (4.1.3). Errors, confirmations and loading states must
reach an `aria-live` region **that is actually rendered** — a live region inside a `hidden`
subtree is announced to nobody, and no scanner flags it.

**If the manual pass was not run, the report says so in place of its results.** A missing pass and
a passed pass must never look alike.

### 5. Tag and report

Tag each automated test `@A11Y-<NNN>`. The report carries the full violation list, the manual-pass
results, and the axe-core version. Attach the raw axe JSON next to it.

## Guardrails

- **Never write "accessible" or "screen X is covered".** The only claim a green automated run
  supports is: *no axe-detectable serious or critical issue on that screen, with axe-core
  `<version>`*. The manual pass widens that claim; it still does not make it "conformant", which
  is an audit verdict a human specialist issues, not this skill.
- **Never suppress a rule to make a suite green.** Disabling a rule is a decision with a name
  attached, recorded with its reason — not a config edit.
- **Watch `results.incomplete`.** axe returns findings it could not decide. They are not passes.
- Accessibility is additive: it does not replace functional testing, it runs alongside it.
