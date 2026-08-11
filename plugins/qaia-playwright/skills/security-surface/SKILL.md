---
name: security-surface
description: Generate and run risk-based passive security-surface checks (CT-SEC - assets and threats identified first, then auth boundaries, IDOR, error handling, user enumeration prioritized by risk) against an authorized self-hosted app, plus optional OWASP ZAP baseline. Use for security coverage. Authorized self-hosted targets only.
---

# security-surface — risk-based passive security checks (CT-SEC)

## PORTE — à franchir avant l'étape 0, avant les protocoles, avant tout

**Cibles autorisées et auto-hébergées uniquement.** Trois bases d'autorisation, et trois
seulement — détaillées dans « Guardrails (blocking) » plus bas : une application du dépôt sous
`examples/` · une cible listée dans [`DEMO-TARGETS.md`](https://github.com/QAIA-Project/QAIA/blob/main/docs/DEMO-TARGETS.md) **et dont la colonne
Security l'autorise** · une autorisation nominative de l'humain, citée mot pour mot.
**Si aucune ne s'applique, tu ne sondes pas.** Tu peux concevoir, et tu dis que tu n'as pas exécuté.

**Interdit ≠ inopérant, et les deux se rencontrent.** Même avec le mandat, une partie de la
méthode reste bloquée pour d'autres raisons : l'étape 0 exige des actifs tirés de la US, du cahier
ou de la base de connaissance — **documents que seul le propriétaire détient** — et le protocole
d'isolement (IDOR) est vide de sens sur un service dont le modèle de données n'a pas de notion de
propriétaire. **Un seul des six protocoles, S5, est exécutable sans mandat.** Dis lequel s'applique
avant de commencer, plutôt que de le découvrir au protocole 4.

*Cette porte vivait après l'étape 0 et les six protocoles jusqu'au 2026-08-11, relevée par un
testeur appliqué à trois cibles tierces. La règle n'a pas changé ; sa place, oui.*

Reference: [`examples/medibook/tests/security.booking.spec.js`](https://github.com/QAIA-Project/QAIA/blob/main/examples/medibook/tests/security.booking.spec.js)
(401/IDOR/malformed-input/user-enumeration).

Scope is deliberately **passive** in this version — observation only, with an OWASP ZAP baseline
scan available opt-in — because an unattended agent running active exploitation against someone's
app is a liability, not a test.

The checklist is front-ended with a CT-SEC risk assessment: a fixed checklist run uniformly
treats every app the same regardless of what it actually protects. Step 0 sets the order and
depth; it never sets the scope.

## Step 0 — Asset & threat identification (CT-SEC, run before the checklist)

1. **Name the sensitive assets** the app actually holds, from the US, test book or knowledge
   base — never invented. Authentication credentials, other users' personal data,
   payment/financial data, admin or privileged functions, and any data a breach would make
   notably worse than a generic CRUD record: health data, financial totals, access tokens.
2. **Rank threats per asset**, with the same impact × probability spirit as `prioritize`: which
   asset, if compromised via which check below, causes the most damage? A payment-data asset
   raises IDOR and enumeration to the top; an admin-function asset raises the auth-boundary
   checks. An app with no sensitive asset beyond its own records still runs the full checklist,
   simply without an elevated priority on any one category.
   The agent **proposes** the ranking with its reasoning and a human arbitrates it — never a
   silent auto-verdict.
3. **Record the ranking** in the report: asset → top-priority check → why. This is the whole
   difference between a flat checklist and a risk-based one.
4. **Never skip a check because an asset ranking looks low-risk.** Risk-based means
   *prioritized*, not *reduced coverage*. A quiet asset still gets the full passive pass, just
   not the first or deepest one.

## Scope (v1, passive — run for every target, ordered/weighted by step 0)

Each item below is a **protocol with a fixture requirement and an expected result**, not a topic.
The full procedures — request-by-request, with the failure modes that make a junior's version
pass while testing nothing — are in `references/protocols.md`. Read it before writing the checks:
five of the six have a well-known way of being run wrong.

- **Auth boundaries** (`S1`): protected endpoints reject missing, malformed, expired and
  foreign-signed tokens with 401. Four distinct cases, not one — see `references/protocols.md#s1`.
- **IDOR / cross-tenant** (`S2`): **needs two real accounts.** A resource created by user A must
  be unreachable by user B's *valid* token, across read **and** update **and** delete. Expect
  404 (or 403 where existence is not itself sensitive), consistently.
  `references/protocols.md#s2` — the most frequently mis-run check in the list.
- **Robust error handling** (`S3`): six named malformed shapes (truncated JSON, inverted type,
  missing required field, oversized payload, unicode/control characters, wrong content-type)
  return a clean 4xx, never 5xx and never a stack trace.
  `references/protocols.md#s3`.
- **User enumeration** (`S4`): unknown-user and wrong-password failures are indistinguishable in
  body, status **and** response time. `references/protocols.md#s4`.
- **Headers/TLS** (`S5`): named header set present with usable values; cookies
  `HttpOnly`/`Secure`/`SameSite`. `references/protocols.md#s5`.
- Optional: **OWASP ZAP baseline** scan (opt-in, `references/protocols.md#s6`).

Every check emits a finding with a severity, including when it passes — a check that ran and
found nothing is evidence; a check that is absent from the report is indistinguishable from one
that was never run.

## Guardrails (blocking)

- **Authorized, self-hosted targets only.** Before running anything, state in the report which
  authorization applies, in this order:
  (a) an in-repo app under `examples/` — self-hosted and owned by definition, no catalog row
  needed; (b) a target listed in `https://github.com/QAIA-Project/QAIA/blob/main/docs/DEMO-TARGETS.md` — cite its golden rule and its per-target
  security column; (c) a target explicitly authorized by the human founder this session — cite
  that authorization verbatim. **If none of the three applies, do not scan.**
- **This authorization check is narrative, not enforced.** No allow-list mechanism exists in the
  repo: nothing outside the agent's own reasoning will stop a scan. The guardrail is written this
  way on purpose — one that implied an automated gate it does not have would be worse than none,
  because the agent would then rely on a check that never fires.
- **Never scan a third party** you do not own or are not explicitly authorized to test. Where the
  founder has named an exception this session (e.g. a target's own docs authorize public
  small-scale testing), cite it explicitly in the report rather than treating it as standing.
- No active exploitation beyond the passive surface above, without explicit user authorization
  and a named scope.
- Publish and honor an acceptable-use note; refuse any framing that targets a competitor or a
  production system without authorization (mirrors the ingestion abuse gate).
- **Produce a report file** next to the evidence — `report.md` in the run's output dir, not only
  in the session transcript. It MUST contain the `@QAIA-SEC-<NNN>` tag, the step-0 asset ranking,
  the authorization basis used above, and every finding with an explicit severity. Evidence files
  alone do not satisfy this bullet.
