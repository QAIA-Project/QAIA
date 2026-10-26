# Step 3c — systematic coverage expansion (recall)

Beyond the ACs literally written, derive the conditions a mature tester adds by reflex. Apply
each pattern whose trigger the feature matches. Every derived condition still cites its technique
and, if it goes beyond the source, carries `[assumption]` / `@low-confidence`.

**This step exists because real human test suites cover these by reflex and
generation-from-AC-alone systematically misses them** — a measured recall gap, not a hypothesis.

Conditions here are `[req-neg]` wherever they refuse or deny.

---

## List / collection view

*Trigger: any screen showing a set of items.*

Sort by each column or criterion · filter by each displayed attribute · empty-list state ·
pagination bounds · **persistence of sort and filter across navigating away and back**.

## Enumerate EVERY list or aggregation view, not just the primary one

A screen often exposes several distinct collections — a dashboard with separate issues,
merge-requests and groups lists; a profile with several tabs. **Each distinct list gets the
sort/filter/persistence treatment above.** Do not stop at the first or most obvious one.

## Full CRUD lifecycle, not just create

*Trigger: any entity.*

Read, **update, delete** · lifecycle transitions **and their inverses** (open→close→reopen,
submit→accept/reject, enable→disable) · **cancel mid-operation** (abandon an edit) · the
forbidden transitions.

**When the source does not specify the exact delete or inverse mechanism, tag the derived
scenario `[assumption]` / `@low-confidence` — never assert one specific mechanism with full
confidence.** Measured on a real hard case: three independent runs each *confidently* invented
the same plausible-but-wrong mechanism ("reset to a default value") for an unspecified deletion,
none flagging it as an assumption. **A converged, confident fabrication is worse than random
variance**, because it reads as certain and can pass a shallow review.

### `[assumption]` versus `[open]` for an undeclared transition — do not conflate

- **Mechanism unspecified** → `[assumption]`. E.g. *how* a delete cascades.
- **Permissibility unspecified, with no safety-obvious default** → `[open]`.

A default-deny reflex is legitimate for **destructive or dangerous** actions — delete, payment
capture, permission escalation. Those get `[assumption]` / `@low-confidence` with "forbidden
unless stated" as the safe default.

But when the transition is not obviously dangerous either way — "can a record in status X be
rejected directly, or must it go through Y first?" — the reflex "undeclared = forbidden" is
itself an unstated **business-policy answer**, not a neutral placeholder. That case is `[open]`,
prompting human arbitration, and must not be silently resolved through the state machine's own
default-deny convention.

## Sibling collections of a named entity

*Trigger: an AC describing an entity as "a collection/group of X".*

Explicitly ask — and surface as a gap if the source is silent — whether **X itself carries
sub-collections or attributes that would naturally roll up here.** A group is a collection of
projects; a project has issues, merge requests, an archived flag; a group dashboard commonly
aggregates those.

Measured failure: three independent runs on a real hard case each recalled the entity's *own*
fields (name, activity) and silently missed every roll-up of the child entity's sub-collections,
without flagging that more might exist. Do not stop at what the source names for the primary
entity only.

## Conditional behavior — decision table over the variation axes

Cross the system's real axes: **config or feature flag** on/off · **visibility** private/public ·
**ownership and role** owner vs member vs admin vs anonymous. Generate the cell for each
combination that changes behavior.

## Authorization and server-side enforcement — the most common miss

For every action: **unauthenticated** access · **permission denied** (wrong role) ·
**cross-tenant** access to another user's resource (IDOR) · **uniqueness or constraint**
violation · **UI bypass** — the rule holds even when the request is sent directly rather than
through the UI.

## Protocol surface

*Trigger: any AC whose system under test is an API rather than a screen.*

Most patterns in this list assume a UI, so on an API target they fall silently for lack of a
medium — and the coverage looks complete while the protocol itself was never exercised. Derive:

- **wrong method on a valid path** — 405 versus 404 mean different things to a client;
- **idempotence** — replaying `PUT`/`DELETE` must converge; replaying `POST` normally must not;
- **content negotiation** — missing or wrong `Content-Type`, unparsable body: a 4xx, never a 5xx;
- **payload boundaries** — empty body, oversized body, unknown fields rejected *or* ignored (the
  source must say which);
- **collection-root operations** — a mutation aimed at `/things` instead of `/things/{id}`;
- **pagination and ordering contracts** — page beyond the last, page size 0 or negative, stable
  order across calls;
- **rate limiting** — documented quota reached returns the documented status, not a generic
  error.

Each is a promise a client will rely on. Where the source states one and the API can break it,
the condition is `[req-neg]`. **Where the source is silent, that silence is itself the finding** —
raise it for `need-understanding` rather than assuming a convention.

## Rendering surface

*Trigger: any AC with a visible UI.*

The same behavior on a narrow viewport is not the same test. Derive:

- **breakpoint boundaries** — the layout switches at a width; that is a boundary value like any
  other, so test width and width±1;
- **navigation collapsed into a menu** — an action reachable directly on desktop may need an
  extra step;
- **touch-target size** — WCAG 2.5.8, 24×24 CSS px minimum. A real refusal condition, so
  `[req-neg]`;
- **occlusion** — a sticky header/footer or on-screen keyboard hiding the element the AC acts on;
- **orientation**, where the content reflows.

Where the source names no breakpoint, tag the condition `[assumption]` / `@low-confidence` and
**say which width you assumed** — never assert a project's breakpoints.

**Scope, stated rather than implied**: QAIA is web-first and "mobile" means **browser device
emulation** (Playwright device descriptors). Native iOS/Android is explicitly out of scope for
v1. Derive the emulation conditions, and if the AC genuinely requires native behavior — push
notifications, biometrics, app lifecycle — surface it as out of scope rather than pretending an
emulated equivalent covers it.

## Account and auth features — include the recovery path

Beyond the authenticated happy path (change password while logged in), derive the **forgot /
reset / recovery** flow when the feature implies it: request reset, email token, invalid new
value, unknown account. **Recovery is a distinct flow, not a variant of the authenticated
change.**

---

## Why the protocol and rendering bullets exist at all

Both are stated explicitly because nothing else in the journey asks for their conditions.

On an API target, the UI-shaped patterns above have no medium to apply to, so they produce
nothing — **including the one this skill itself calls "the most common miss"**. Symmetrically, no
other step asks for viewport-dependent conditions.

Without these two bullets, those conditions get derived only when whoever runs the journey
happens to think of them. **Individual initiative is not a control, and a coverage claim that
depends on it is not reproducible.**

---

## The ceiling — do not hallucinate to chase recall

## Interaction surface — what a user does that the AC never describes

Found by measurement, not by review. On 2026-08-08 a competitor's design agent was run on the same
user story and judged blind against ours
([the head-to-head](https://github.com/QAIA-Project/QAIA/tree/main/eval/head-to-head-qa-orchestra-2026-08-08)).
It produced **eight risk classes this file did not name**, and three of them were genuinely absent
from every pattern above — verified by grep, not by impression.

They share one shape: **the AC describes a transaction, the user performs a session.** Between the
two sit actions no criterion mentions because no author thinks to write them down.

- **Rapid repeated action** — the same submit dispatched twice before the first answers. The
  protocol pattern above covers `POST` idempotence at the API; this is the interface event that
  produces it, and it needs its own scenario because the defence lives in the UI, not the endpoint.
- **Mid-flow navigation** — browser back after a state change, refresh mid-wizard, navigating away
  and returning. A workflow with states (`draft` → `submitted` → …) has one of these per
  transition, and back-after-transition is where stale state resurfaces.
- **Concurrent actors on one record** — two approvers deciding the same item, an editor and a
  deleter. This is *not* the same as protocol idempotence: the two calls are both valid, both
  authorised, and only their interleaving is the defect. Any AC naming **two roles acting on one
  entity** implies it.
- **Text-field content the author never pictured** — Unicode beyond Latin-1, right-to-left text,
  a string carrying markup or SQL-like syntax. The expected result is almost always *"stored and
  rendered as data, never interpreted"*, which is precisely what makes it a **refusal-path**
  condition rather than a decorative one.
- **A dependency removed mid-session** — the attachment deleted while the approval is pending, the
  referenced entity gone between reading and writing. The CRUD pattern above asks *how* a delete
  cascades; this asks what happens to whoever was already holding the thing.

### The ceiling still applies

None of these may be invented into an expected result. If the AC does not say what should happen
when a back button follows a state transition, the condition is generated **and its outcome is an
open question** — same discipline as everywhere else in this file. Generating the condition is
recall; asserting an outcome the source never states is fabrication.

### And two the competitor covered that belong elsewhere

Their output also carried performance-under-volume and keyboard/screen-reader accessibility.
Those are **not** gaps in this file: `qaia-playwright:perf-check` and
`qaia-playwright:a11y-audit` own them, with their own oracles. Listing them here would duplicate a
skill and dilute this one.

Two families are legitimately **not** inferable from a thin US and must not be invented:

1. **Config or feature-flag-driven behavior** — what a button does when payments are off, a
   community is private, a custom field is enabled. This depends on the project's configuration
   and belongs to the **knowledge base** (`rag-build`), not to guessing.
2. **Rich domain-specific interactions the US never mentions** — a merge request's inline diff
   comments, a Markdown preview. If the source does not imply them, generating them is
   fabrication, not coverage.

When you detect such a family, **surface it as a gap** — "this feature likely has config-driven
or detail-page behavior not described in the US; provide it, or the knowledge base" — rather than
inventing scenarios.

**Honest recall beats fabricated recall.**
