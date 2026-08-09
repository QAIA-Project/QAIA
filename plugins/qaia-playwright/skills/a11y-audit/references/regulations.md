# Which regulation applies, and what this skill does *not* cover

Read this before telling anyone the run means the product complies with something.

## The one sentence that matters

**This skill's oracle is WCAG 2.1 A/AA, checked by axe-core plus a mandatory manual pass.**
Every regulation below is *built on* WCAG, which is why the run is useful for all of them — and
every one of them adds obligations WCAG does not contain, which is why **no run here is a
compliance verdict**.

## The map

| Regulation | Where it binds | Its technical base | What this skill covers | What it does NOT |
|---|---|---|---|---|
| **EN 301 549** | EU public procurement | WCAG 2.1 AA, clauses 9–11 | the WCAG core | non-web software, documents, hardware, **support services** (clause 12), and the conformance *statement* |
| **EAA** (directive 2019/882) | EU, private sector, since 2025-06 | EN 301 549 → WCAG 2.1 AA | the WCAG core | the accessibility statement, the disproportionate-burden file, market-surveillance evidence |
| **RGAA 4.1** (France) | French public sector | WCAG 2.1 AA **restated as 106 numbered criteria over 13 themes** | the subset axe-core can automate | **the RGAA's own test methodology**, its numbered criteria, its compliance-rate arithmetic, its mandatory sample of pages, and its published *déclaration d'accessibilité* |
| **Section 508** | US federal | WCAG 2.0 AA (revised 2017) | the WCAG core | the ICT baseline, procurement documentation |
| **WCAG contractual** | anything you signed | WCAG itself | the automatable third | the two remaining thirds |

## RGAA in particular — say this out loud to a French public-sector client

RGAA 4.1 is **not a synonym for WCAG**. It is a *test method*: 106 criteria, each with numbered
tests, each with a stated procedure, and a compliance rate computed over a **defined sample of
pages** rather than over whatever screens the suite happens to visit.

Three consequences for anyone reading a run from this skill:

1. **No axe-core rule maps one-to-one to an RGAA criterion.** A green run does not satisfy criterion
   1.1, 8.9 or 10.7 — it makes them *likelier* to be satisfied.
2. **The compliance rate cannot be derived from this output.** RGAA's rate is
   `criteria compliant / criteria applicable`, over the sampled pages. This skill reports
   violations by severity over the screens it was pointed at. **Different numerator, different
   denominator, different sample.**
3. **The `déclaration d'accessibilité` is a legal artefact** with a mandatory template. Nothing here
   produces it, and nothing here entitles anyone to sign it.

**What this skill legitimately gives an RGAA audit:** a fast, reproducible pass over the
automatable share, plus the keyboard, focus and contrast checks that RGAA also requires and that no
scanner performs. It **narrows** the manual audit. It does not replace it.

## The sentence to use, and the one to refuse

> ✅ *"axe-core and the manual pass found no WCAG 2.1 AA violation on these screens. This covers
> roughly a third of the success criteria automatically; the rest, and the RGAA method itself,
> require a human audit."*

> ❌ *"The application is RGAA compliant."* — this skill cannot establish that, and saying so on a
> public-sector delivery is the kind of imprecision that is discovered during an audit rather than
> before it.

## Why this file exists

The skill's own `description` listed **EAA, RGAA, Section 508** as reasons to run it, while its
oracle was WCAG alone and nothing said so. Naming a regulation is an implicit promise about what
the run means. Found on 2026-08-09 by reading the description against the implementation.
