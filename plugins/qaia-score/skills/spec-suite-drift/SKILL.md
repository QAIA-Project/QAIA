---
name: spec-suite-drift
description: Compare an OpenAPI specification against the test suite that claims to cover it - pure text, no running application. Reports status codes the suite uses that the spec never declares, error codes the spec promises that no test exercises, and endpoints the suite calls that the spec does not describe. Use when a project has both a formal API spec and an automated suite, and nobody has ever checked that they agree.
---

> **Ce que cette skill promet, et depuis quand.** La note vient d'un **programme fige, livre
> avec le plugin** (`scripts/`), pas d'un algorithme rejoue de memoire : deux passages sur le
> meme fichier donnent le meme resultat, et la note est comparable d'une semaine a l'autre.
>
> Ce n'etait pas vrai avant le 2026-08-09. La skill demandait alors de materialiser l'algorithme
> en session depuis sa propre prose -- ~300 lignes d'expressions regulieres re-derivees a chaque
> invocation. Une revue independante l'a releve ; le prix a d'abord ete ecrit, puis supprime.
> **Rien ne s'execute tout seul pour autant** : le fichier est lu et lance par Claude quand vous
> invoquez la skill, avec vos droits, et vous pouvez le diffier, l'epingler ou refuser.

# spec-suite-drift — the specification against the suite

Follow the shared contract in `../README.md`.

`contract-probe` compares a **running application** to its documentation. This skill compares the
**test suite** to that same documentation. Both halves are usually self-consistent when read
alone, which is precisely why nobody notices they disagree.

It reads two documents. **No application runs, no credential is used, no request leaves the
machine** — so unlike every other check in this plugin it can run on every commit, against any
project, including one you only have a copy of.

## The case that produced this skill

`realworld-apps/realworld` publishes an OpenAPI specification *and* a shared Playwright suite that
every implementation must pass. Crossing the two found this:

- the specification promises **409 Conflict** on `POST /users` and `POST /articles`;
- `error-handling.spec.ts:51` mocks that exact case — `email: ['is already taken']` — as a **400**;
- **none** of the suite's 150 behaviours exercises a 409.

For a project whose entire purpose is that many implementations honour one contract, the two
cannot both be right. Neither the specification review nor the suite review would find it: each is
internally coherent. Only the crossing shows it.

## What is reported

| Rule | Meaning |
|---|---|
| `undeclared-status` | The suite mocks or asserts a status the spec **does not declare** for that path. Either the suite tests a promise that does not exist, or the spec forgot a real case. |
| `unexercised-status` | The spec declares an error code that **no test mentions anywhere**. A promise nobody has ever checked. |
| `path-not-in-spec` | The suite calls an API path the spec does not describe. |

Success codes never raise `unexercised-status`: a nominal test exercises the happy path without
ever writing `200`.

## Steps

1. **Locate both inputs.** The specification (`.yml`, `.yaml` or `.json`) and the directory holding
   the suite. If the project has only one of the two, say so and stop — this skill has nothing to
   compare and must not improvise the missing half.

2. **Run the shipped comparator. Do not re-implement it.**

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/spec_suite_drift.py" --spec <openapi.yml> --tests-dir <suite>
   ```

   **Requires PyYAML** (`pip install pyyaml`) — it is the only third-party dependency in anything

> Si `${CLAUDE_PLUGIN_ROOT}` n'est pas defini dans votre environnement, le fichier se
> trouve a cote de cette skill : `../../scripts/` depuis le dossier du SKILL.md.

   QAIA ships. Without it the tool prints `BROKEN` and exits 2 rather than guessing.

   Nothing auto-executes: this is a pinned, readable file that Claude runs with your permissions
   when you invoke the skill. Until 2026-08-09 this skill instead asked you to reproduce its three
   rules in session — an LLM re-deriving a comparator from prose is the failure mode the
   deterministic pass exists to remove, and doing it from memory reintroduced exactly that.

   ```
   python <script> --spec <spec> --tests-dir <suite> --json drift.json
   ```

   Exit 0 = no drift, 1 = drift found, 2 = unreadable input.

3. **Read each finding before reporting it.** Open the cited file and line. The pairing of a path
   to a status is a **proximity heuristic**: within a test block, statuses are attributed to the
   single path that block cites, and a block citing two paths is skipped rather than guessed.
   That is deliberate: the first version of this comparison produced 22 findings on the founding
   target of which 14 were artefacts, and every one was removed by narrowing the rule rather than
   filtering the output.

4. **Classify, never merge.** A drift is an **open question for a human**, not a defect:
   - the specification may be wrong, and the suite right about the real behaviour;
   - the suite may be wrong, and the specification the contract of record;
   - both may describe an intended change nobody propagated.

   Emit `# open: Qn` in the test book, exactly as with an ambiguous user story. **Do not guess
   which side is right.** Deciding needs the people who own the contract.

5. **Report the counts alongside the findings** — paths in the spec, path/status pairs recovered
   from the suite, findings. A comparison that recovered three pairs from a suite of two hundred
   tests has found nothing; its silence must not read as agreement.

## What this skill must refuse

- **Deciding which side is right.** Every finding is a question, never a verdict.
- **Rewriting either artefact.** It reads; it does not repair. `testbook-generate` and the
  developers own the fixes.
- **Reporting a finding whose file and line were not opened.** The heuristic is honest about being
  a heuristic; the reporting must be too.
- **Calling an empty result a pass.** No pairs recovered means the suite's shape was not
  understood — say that, do not say "they agree".
- **Running anything.** No request to the application under test, no credential, no network. If a
  finding cannot be settled from the two documents, it stays open.

## Applied for real

[`drift.json`](https://github.com/QAIA-Project/QAIA/blob/main/eval/sdlc-realworld-2026-08-09/drift.json) — 12 specified paths, 8 findings, **0 false positives
after narrowing**: two contradictions where the suite mocks a `400` the specification never
declares, four `500`s the suite injects for resilience beyond the contract, and the two promises
nobody exercises (`409` on 2 paths, `422` on 12).

Both directions are held by [`selfcheck_spec_suite_drift.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/selfcheck_spec_suite_drift.py): a drifting fixture where
each rule must fire exactly once on the planted line, and an agreeing fixture where nothing may
fire. Four injected faults were each caught before this skill was written.
