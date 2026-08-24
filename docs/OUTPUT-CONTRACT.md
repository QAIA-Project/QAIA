# QAIA output contract — the run manifest (v1)

Every QAIA plugin, whatever its job, emits **the same machine-readable envelope** so the
work of one plugin can be read, scored and reported by any other without bespoke glue
(decision D39). The envelope is a single JSON file per user story:

```
.qaia/reports/<US-ID>/manifest.json
```

It never replaces the human-facing artifacts (`.feature`, `synthesis.md`,
`coverage-matrix.md`, JUnit/Cucumber/HTML). It is a **projection** of them into one stable
schema: a normalized index of what was produced, by whom, and the metrics a reviewer or a
gate needs. Any discrepancy between the manifest and its source artifacts is a bug in the
producer — fix the source, re-project the manifest, never hand-edit the manifest to agree.

## Principles

1. **One envelope, every plugin.** `qaia-core`, `qaia-playwright`, and any future plugin
   write to the *same* file with the *same* schema. A consumer (`qaia-score`, an export, a
   dashboard) reads one contract, not N formats.
2. **Append-provenance, never clobber.** A producer merges its section and appends itself to
   `producers[]`; it never drops another plugin's contribution. Re-running a producer
   replaces only its own section.
3. **Additive, versioned.** `contract` is SemVer. New optional fields are a minor bump;
   removing or repurposing a field is a major bump. A consumer ignores unknown fields.
4. **Portable.** The manifest is plain JSON a skill assembles by reading its own outputs —
   no runtime, no network, no API key. On surfaces without file tooling, the same object is
   emitted as a fenced ```json block and the user saves it.
5. **No secrets, no PII.** The manifest carries counts, IDs, paths and verdicts — never raw
   source text, credentials, environment URLs, or personal data. PII masking (shared
   contract rule 5) has already happened upstream; the manifest only ever sees placeholders.

## Schema (contract 1.1)

```jsonc
{
  "contract": "1.1",                       // SemVer of THIS schema
  "usId": "US-001",                        // journey key (shared contract)
  "title": "Appointment booking",          // short, non-sensitive
  "status": "review",                       // draft | review | validated
  "generatedAt": "2026-07-23T10:00:00Z",    // ISO 8601, last write
  "base": ".qaia",                          // configurable output root (shared rule 9)

  "producers": [                            // provenance chain, append-only
    { "plugin": "qaia-core", "version": "0.2.3", "skill": "testbook-generate", "at": "2026-07-23T09:58:00Z" },
    { "plugin": "qaia-playwright", "version": "0.1.1", "skill": "run-report", "at": "2026-07-23T10:00:00Z" }
  ],

  "artifacts": [                            // pointers to the human-facing outputs
    { "kind": "feature",   "format": "gherkin",  "path": "testbooks/US-001/booking.feature" },
    { "kind": "synthesis", "format": "markdown", "path": "testbooks/US-001/synthesis.md" },
    { "kind": "matrix",    "format": "markdown", "path": "testbooks/US-001/coverage-matrix.md" },
    { "kind": "validation","format": "markdown", "path": "reports/US-001/testbook-validate-report.md" },
    { "kind": "execution", "format": "junit",    "path": "reports/US-001/junit.xml" }
  ],

  "design": {                               // filled by qaia-core (the test book)
    "scenarios": { "total": 22, "byPriority": { "P1": 9, "P2": 8, "P3": 5 },
                   "negative": 9, "smoke": 1, "outlines": 3 },
    // `total` = les CAS EXECUTABLES : un `Scenario Outline` a N lignes d'`Examples` en vaut N,
    // ce qu'un lanceur executera et ce que `testbook-export` projette deja en N lignes.
    // `outlines` = le nombre de blocs `Scenario Outline`, non eclates.
    // La convention est nommee ici parce qu'elle ne l'etait pas : le scoreur comptait les blocs,
    // l'export comptait les cas, et `aptitude-gate` decidait d'une release sur le premier des
    // deux sans que rien ne dise lequel (2026-08-10). Un cahier de 10 Outlines a 6 exemples fait
    // 60 et non 10 ; tout ratio (negatif, confiance) se calcule sur ce denominateur.
    "byLevel": { "e2e": 14, "api": 8 },     // 1.1 — ADR 0008, the level DESIGNED per scenario
    // Cles fermees : `e2e` | `api`, rien d'autre. Somme == `scenarios.total`, meme denominateur
    // que ci-dessus (un Outline a N exemples compte N). C'est le pendant conception de
    // `execution.byType` : sans lui, byType est le rangement de l'automaticien et ne se compare
    // a aucune intention. Optionnel en 1.1 pour ne pas invalider les manifestes 1.0 existants.
    "coverage": { "acTotal": 6, "acCovered": 6,
                  "reqNegTotal": 7, "reqNegCovered": 7,   // ADR 0001 — the real gate
                  "negativeRatio": 0.41 },                 // D20 — reported signal, not a gate
    "confidence": { "lowConfidence": 3, "openQuestions": 2, "assumptions": 4, "simulated": 1 },
    "techniques": ["ep", "boundary", "decision-table", "state-transition", "pairwise"],
    "oracles": ["luhn", "iso-8601"],        // @oracle:* provenance seen in the book
    "knowledgeApplied": ["BR-KB-004", "BR-KB-011"]  // knowledge-base rules that shaped the book
  },                                        // (D38 RAG-in-use); empty on a rich domain = thin KB signal

  "execution": {                            // filled by qaia-playwright (optional)
    "total": 31, "passed": 31, "failed": 0, "blocked": 0,
    "byType": { "e2e-desktop": 12, "e2e-mobile": 8, "api": 6, "a11y": 3, "perf": 1, "security": 1 },
    "traceability": { "scenariosAutomated": 18, "scenariosTotal": 22 }
  },

  "openArbitrations": [                      // pending human decisions, from the checkpoints
    { "id": "Q5", "kind": "open",      "about": "cancellation window when < 4h",
      "sourceCheckpoint": "state/US-001/02-understanding.md" },
    { "id": "AC3-C2", "kind": "simulated", "about": "default applied non-interactively",
      "sourceCheckpoint": "state/US-001/04-priorities.md" }
  ],

  "structural": {                           // deterministic pass, run BEFORE any LLM judgment
    "score": 85, "max": 100,                // readability 25 · completeness 30 · coherence 20 · traceability 25
    "gate": "PASS",                         // PASS ≥80 | CONCERNS ≥60 | FAIL <60 — or FAIL on a forced stop
    "forcedStop": false,                    // C1 hollow-Then / C2 no-expected-result / fabrication sniffer
    "findings": [],                         // the forced-stop findings, verbatim, when there are any
    "scoredBy": "qaia-score/testbook-score", "at": "2026-07-23T10:04:00Z"
  },

  "gate": {                                 // filled ONLY by qaia-score — never self-scored
    "verdict": "CONCERNS",                  // PASS | CONCERNS | FAIL | WAIVED
    "score": 18, "max": 20,
    "scoredBy": "qaia-score/testbook-score", "at": "2026-07-23T10:05:00Z",
    "dimensions": [ { "n": 3, "name": "negative-path", "score": 1 } ],  // only non-2 dims listed
    "reasons": ["1 required-negative condition uncovered (AC4)"],
    "waiver": null                          // { by, reason, at } when verdict = WAIVED
  }
}
```

### Field rules

- **`status`** is owned by the producing journey: `draft` while generating, `review` once a
  synthesis exists, `validated` only after a human sign-off is recorded. A gate verdict does
  **not** change `status` — a human does.
- **`design.coverage.reqNegCovered / reqNegTotal`** is the ADR 0001 negative-path gate (the
  one that blocks). **`negativeRatio`** is the D20 signal — reported, never a threshold.
- **`design.byLevel`** (1.1, [ADR 0008](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0008-test-level-is-a-design-property.md)) carries the level **decided at design time** by
  `istqb-design` and tagged by `testbook-generate` — closed keys `e2e` / `api`, summing to
  `design.scenarios.total`. It is the design-side counterpart of `execution.byType`: comparing the
  two is what makes "12 API conditions designed, 4 automated" sayable, which no QAIA artifact could
  say before. **Optional**, so 1.0 manifests stay valid; when present it must be complete and
  consistent — a partial or non-summing `byLevel` is an error, not a hint.
- **`design` is optional, but all-or-nothing.** Omit it entirely when there is no test book
  (a run-only or traffic-only manifest); do **not** ship a partial `design` block. Two shipped
  fixtures did exactly that and failed this contract's own validator for months (skill-eval
  wave A, 2026-07-31, pattern P1). Completing such a block with invented coverage/confidence
  numbers to satisfy the validator is the fabrication D38 forbids — remove the block instead.
- **`artifacts[].kind`** is a closed enum: `feature`, `synthesis`, `matrix`, `validation`,
  `execution`, `export`, `flakiness` (`flaky-detect`, D80 — read by `aptitude-gate` as a
  CONCERNS signal), `trafficReplay` (`traffic-replay`, D88), `dataset` and `dataset-map`
  (`qaia-testdata:dataset-generate`, D137/D142). All four of the last were emitted by real
  producers long before being declared here; a kind not in this list is an error, so a new
  producer must extend the enum **and** this line together. That this keeps happening is the
  argument for the CI job validating `eval/**` as well as `plugins/**`.
- **`artifacts[].path` stays inside the run.** It is relative to the run's own report
  directory. A path that climbs out (`../../another-run/x.json`) or is absolute is refused by
  the validator, whether or not the file exists. A manifest describes what *this* run produced;
  the moment it can point anywhere, `--check-paths` resolves against whatever root it is handed
  and the manifest stops being self-contained. Found in wave A, where a producer declared a
  deliverable living two directories up, inside a different run (#67).
- **Never write into a manifest you did not produce.** A producer merges into the manifest of
  the run it is part of, and only that one. Emitting into another run's manifest — even to
  declare something real — makes that run claim work it did not do, and its provenance stops
  being readable. This rule existed only in some evaluation briefs before being written here,
  which is why an agent broke it without being at fault (#67).

- **A `gate` block may legitimately be partial.** Two skills fill it, in order:
  `qaia-score:testbook-score` writes `score`/`dimensions`/`max`, then `qaia-score:aptitude-gate`
  writes `verdict`/`reasons`/`waiver`. Between them sits a real intermediate state — a scored,
  not-yet-gated candidate — and a `gate` without `verdict` is **valid**. Requiring one there
  would force the only honest producer of that state either to fabricate a verdict it must not
  own (no producer scores itself) or to fail validation for obeying this contract. A `verdict`
  that **is** written is still fully checked, including the rule that WAIVED needs a `waiver`
  object naming its grantor.
- **Provenance-weak items have no dedicated `kind`.** `openArbitrations[].kind` stays
  `open | assumption | simulated`. An item whose *source* is weak rather than whose *answer* is
  unknown — a value corroborated only by third-party write-ups, never by the designated
  source — is recorded as `assumption`, with the weakness stated explicitly in `about`. The
  distinction is real but is carried in prose rather than in the enum, because a fourth kind
  would ripple through every producer and consumer for a case the `about` field already
  expresses. (Such an item is also a signal worth chasing upstream: it usually means content
  entered the capture that `us-ingest`'s source-fidelity rule forbids.)
- **`artifacts[].path`** must resolve to a file that really exists. `validate_manifest.py`
  checks this under `--check-paths <root>`; it is opt-in because a manifest is often validated
  away from the tree it describes, where a missing file would be a false alarm rather than a
  finding.
- **`design.confidence.*`** — operational definitions, so two conforming runs cannot report
  different numbers for the same book (the ambiguity wave A raised against `report`):
  - `openQuestions` — count of distinct `[open]` markers in the checkpoints, i.e. questions
    put to a human and **not** answered. A question answered before generation is not counted.
  - `assumptions` — count of distinct `[assumption]` markers: a gap the journey closed itself
    and labelled as such.
  - `lowConfidence` — count of **scenarios** tagged `@low-confidence` in the emitted
    `.feature` files. Counted by tag in the artifact, never estimated from prose.
  - `simulated` — count of validation points passed without a human, recorded per
    `openArbitrations[].kind = "simulated"`. Zero in an interactive session.
  Each is a literal count over a named artifact, never a judgement: if the number cannot be
  obtained by counting, it does not belong in the manifest.
- **`gate`** is written **only** by a scoring plugin. No producer may score itself (shared
  contract rule 3). Its absence means "not yet scored".
- **`structural` and `gate` are two scores and they are never merged.** `structural` is the
  reproducible machine pass over the `.feature` files; `gate.score` is the LLM rubric's /20. The
  founding case is why: the same test book measured **100/100 by machine and 58/100 by a human
  reviewer** — a book can be structurally impeccable and assert nothing. Summing them, averaging
  them, or reporting one as "the score" hides exactly the failure the pair exists to expose.
- **`structural.forcedStop` outranks every number in this file.** A C1 (a `Then` whose only
  evidence is an image or a table), a C2 (no verifiable expected result) or the fabrication
  sniffer force `structural.gate = "FAIL"` whatever the score, and cap `gate.verdict` at FAIL
  regardless of the rubric total. The validator enforces the pair: a `forcedStop: true` with any
  gate other than FAIL is rejected, as is a gate that contradicts its own score band.
  *Added 2026-07-31: this block did not exist. The most binding gate of the product — the one
  that can fail a book independently of any score — was computed, reported in prose, and then
  lost, because the manifest had exactly one score field and the rubric owned it.*
- **`openArbitrations`** mirrors every `⚠ VALIDATION` point still pending — including every
  `simulated` entry from non-interactive runs, which must all surface here for human review.
- Every count in the manifest must equal what the artifacts actually contain. Producers
  compute counts, they do not estimate them.

## Who writes what

| Section | Owner | When |
|---|---|---|
| `contract`, `usId`, `title`, `base`, `producers[]`, `artifacts[]` | whichever skill runs (merge) | every write |
| `design.*`, `openArbitrations` | `qaia-core:report` (from checkpoints + test book) | after generation/export |
| `execution.*` | `qaia-playwright:run-report` | after an automated run |
| `gate` | `qaia-score:*` | when a book/run is scored |
| `status` | the human-facing skill recording the sign-off | on validation |

`qaia-core:report` is the canonical assembler for the `design` side; other producers merge
their own section in place and leave the rest untouched.

## Consuming the manifest

A consumer reads `manifest.json`, checks `contract` major version, and uses only the fields
it needs. Recommended reads:

- **`qaia-score`** → `design.*`, `execution.*`, `artifacts[]`; writes `gate`.
- **an export / dashboard** → `producers`, `artifacts`, headline metrics, `gate.verdict`.
- **CI** → `gate.verdict` (PASS/WAIVED to proceed) and `execution` (pass/fail).

## Versioning

- **1.0** — initial contract: `design`, `execution`, `gate`, `openArbitrations`, provenance,
  and `design.knowledgeApplied` (the RAG-in-use provenance, D38). Introduced together
  pre-release, so this is one 1.0 surface rather than a 1.0→1.1 step.
- **1.1** (2026-08-11) — `design.byLevel`, the test level decided at design time
  ([ADR 0008](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0008-test-level-is-a-design-property.md)). **Additive and optional**: every 1.0 manifest remains valid and no
  consumer is required to read it. Minor bump per rule 3. Motive: `execution.byType` had shipped
  in 1.0 with an `api` key that nothing on the design side ever produced — the contract described a
  split the chain never decided.

Changes are logged here and in [`docs/DECISIONS.md`](https://github.com/QAIA-Project/QAIA/blob/main/docs/DECISIONS.md). A consumer that needs a field a producer
did not write treats it as absent (degraded mode, shared contract rule 8), never as an error.

## Programmatic validation

[`docs/schemas/output-contract-v1.schema.json`](https://github.com/QAIA-Project/QAIA/blob/main/docs/schemas/output-contract-v1.schema.json) is a formal JSON Schema (draft 2020-12) copy of
the rules above, and [`eval/tools/validate_manifest.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/validate_manifest.py) is a stdlib-only, dependency-free
validator against the same rules (hand-rolled rather than a generic JSON Schema engine, to stay
consistent with `structural_score.py`/`second_judge.py`). *Correction du 2026-08-24 : cette
parenthese disait « maintainer eval tooling, never shipped to installers », ce qui a cesse d'etre
vrai le 2026-08-09 (ADR 0002) -- les trois scoreurs sont livres dans `plugins/qaia-score/scripts/`
et une porte les y maintient identiques. `validate_manifest.py`, lui, ne l'est pas.* Both are a second, executable copy of this document, not a new source of
truth — if they ever disagree with the prose above, the prose wins and the tooling is a bug.

```
python3 [eval/tools/validate_manifest.py](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/validate_manifest.py) .qaia/reports/US-001/manifest.json
python3 [eval/tools/validate_manifest.py](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/validate_manifest.py) --batch .qaia/reports/   # recursive
```

D104 (2026-07-28): added in response to the external Gemini audit's Phase 1 recommendation to
formalize a validation schema for this contract, so a producer's drift from the documented
shape is caught by a linter before a commit rather than discovered later by a consumer.
