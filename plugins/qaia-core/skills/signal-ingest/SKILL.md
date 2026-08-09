---
name: signal-ingest
description: Ingest an exported production signal - an access-log extract, an error-rate table, a status-code breakdown, an APM export or a HAR capture - and attach it as evidence to the open questions a test book already carries. Answers nothing on its own - it turns a blind open question into an informed one. Use when a test book has open questions that observed behaviour could inform, or when production data exists and nobody has connected it to the test design.
---

# signal-ingest — observed behaviour as evidence, never as an answer

Follow the shared contract in `../README.md`.

`need-understanding` raises the ambiguities a requirement leaves open, and `openapi-ingest` raises
the ones a specification leaves open: *is `limit` bounded?*, *which status does a duplicate
registration return?*. Both hand those questions to a human, who then arbitrates them blind — while
the running system answers them a thousand times a day and nobody writes it down.

This skill closes that gap **without ever deciding anything**. It attaches observed evidence to an
existing question so the human who arbitrates it stops arbitrating blind.

## The line this skill does not cross

**It reads a file the user exports and hands over. It never connects to anything.** No endpoint,
no credential, no APM token, no log stream, no polling. The project's scope decision keeps
production *monitoring* out; ingesting an artefact someone chose to export is the same shape as
`traffic-replay` reading a HAR, and stays inside it.

If asked to fetch the data itself, refuse and say what to export instead.

## Accepted inputs

| Input | What is extracted |
|---|---|
| access-log extract | path, method, status, count |
| status-code breakdown (CSV/JSON) | path × status frequency |
| error-rate or APM export | error class, endpoint, frequency, first/last seen |
| HAR capture | request/response pairs — hand to `traffic-replay` for test generation, here only for evidence |
| a table pasted by the user | whatever it actually contains, and nothing inferred |

Anything else: say it is not supported rather than guessing at a format.

## The rule that makes it honest

**Observed is not specified.** Traffic shows what the system *does*, under the load and the
population it happened to see. It never shows what the system *must* do. A signal is therefore
always recorded as *"observed X over period P, N occurrences"* — never as *"the answer to Q3 is X"*.

Three ways an observation misleads, to be stated whenever they apply:

- **Absence proves nothing.** No 409 in 30 days may mean the case cannot occur, or that the client
  prevents it, or that the export was filtered. Never write "the 409 is dead code".
- **A maximum is not a bound.** The largest `limit` ever seen was 100; that says nothing about what
  the server accepts, only about what clients asked for.
- **Production is not the population.** Whatever the sample under-represents — a locale, a role, a
  device — is exactly where the untested behaviour lives.

## Steps

1. **Take the artefact and freeze it.** Copy it into the run's `sources/`, record its sha256 and
   the period it covers. An evidence file whose provenance cannot be re-read is an opinion.

2. **Take the open questions.** Read the `# open: Qn` entries in the test book. **No open
   questions, no work** — say so and stop. This skill informs existing questions; it does not
   invent new ones from data, which would be reading tea leaves.

3. **Match evidence to questions, conservatively.** A signal attaches to a question only when it
   speaks to the same endpoint, field or status. When it does not, leave the question untouched:
   an unrelated fact attached to a question makes the question harder to answer, not easier.

4. **Write the evidence next to the question, never in place of it.** The question stays `# open`.

   ```
   # open: Q3 — is `limit` bounded above?
   #   evidence (signal-ingest, <period start>..<period end>, access-log.csv sha256 a1b2…):
   #     max observed value 100 over 41 812 requests; 3 responses 422 above it.
   #     Observed only — does not establish the specified bound.
   ```

5. **Report what the evidence did NOT reach.** List the open questions no signal informed. That
   list is the real output: it is the set of things production cannot tell you, and it is where
   human arbitration is genuinely required.

6. **Hand durable findings to `rag-build`.** A recurring observed behaviour is a candidate entry
   for `knowledge/application-map.md`, with its provenance and its period. One-offs stay in the
   run.

## What this skill must refuse

- **Closing an open question.** It attaches evidence; a human decides. Not overridable by "the data
  is obvious".
- **Connecting to anything.** No fetch, no credential, no live endpoint — the user exports, this
  reads.
- **Inventing questions from data.** Without an existing `# open: Qn`, there is nothing to inform.
- **Treating absence as a negative.** "Never observed" is recorded as never observed, with the
  period and the sample size, and never as "does not happen".
- **Ingesting raw personal data.** Access logs carry IPs, user IDs, tokens and emails. Mask before
  writing anything, exactly as `us-ingest` does, and never persist a mapping from the original
  value to its placeholder.
- **Generating tests directly.** Evidence feeds design; `traffic-replay` is the skill that turns
  captured traffic into tests, and the two must not be merged.
