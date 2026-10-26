# Export connector — TestRail (issue #35, remaining scope after the Xray connector)

How `testbook-export` projects a QAIA test book into a file TestRail can import. **Export-only,
file-only** (decision D29, portable-first): this connector never calls the TestRail API, never
stores or asks for an API key, and makes no network call. It writes a file; the user imports that
file themselves through TestRail's own **CSV/Excel import wizard**, on their own schedule, in their
own instance/project.

**Direction matters.** This is the test book → test-management-tool direction, the same direction as
`connectors/xray.md`, and the opposite of a hypothetical `us-ingest` TestRail *source* connector
(none exists). No live push exists here — file export only, same as Xray.

## What ships today: CSV, for TestRail's CSV/Excel importer, "Test Case (Text)" template

TestRail's own CSV import (`support.testrail.com`, "Import test cases from CSV or Excel", fetched
and read directly on 2026-07-25 — not recalled from training data) is **column-mapped
interactively**, unlike Xray's fixed-header CSV: there is no single required header row layout.
Step 1 of the wizard picks file/encoding/delimiter options and the case **template**; step 2 lets
the user map each CSV column heading to a TestRail field from a dropdown; step 3 maps field
*values* (e.g. a CSV `Priority` of `Highest` to TestRail's own priority list); step 4 previews and
runs the import. QAIA cannot drive that wizard and does not try to — it only writes a CSV whose
column headers are plausible interactive-mapping targets, using field names TestRail's docs use.

TestRail differentiates a **single-row layout** (one CSV row per test case — what this connector
produces) from a **multi-row layout** (one row per individual step, used by the separate "Test Case
(Steps)" template for step-by-step result tracking). This connector targets the simpler, broadly
compatible **Test Case (Text)** template: its docs state plainly that "your import file should use
the standard one row format" for that template, with `Preconditions`, `Steps` and `Expected Result`
each a single large text field per row — a natural fit for one CSV row per QAIA scenario. TestRail
also ships a native "Behaviour Driven Development" template with a Given/When/Then structure; a
future connector could target that template's own CSV shape directly instead of splitting Gherkin
into Text-template fields, but that path was **not** researched in this pass — flagged here rather
than assumed equivalent.

### Column mapping

One row per **scenario** (a `Scenario Outline` is exploded into one row per `Examples` line, ID
suffixed `-eN` — the same rule the XLSX deliverable and the Xray connector already use, kept
consistent across exports; the US-004 test book used for the proof below has no `Scenario Outline`,
so this path is documented but not exercised by that proof).

| CSV column | Value | Source |
|---|---|---|
| `Title` | scenario title, `- Examples N` appended for an exploded outline row | `Scenario:`/`Scenario Outline:` line |
| `Type` | `Automated` (constant) | QAIA default — **caveat below**, TestRail's `Type` dropdown values are project-customizable |
| `Priority` | `P1→Critical`, `P2→Medium`, `P3→Low` — **a QAIA default mapping, not a TestRail requirement**, chosen because TestRail's own default priority scale (`Low`/`Medium`/`High`/`Critical`, confirmed in the fetched docs) has 4 levels against QAIA's 3; `High` is deliberately left unused rather than guessed at | scenario's `@P1`/`@P2`/`@P3` tag |
| `Preconditions` | the flattened `Background` `Given`/`And` steps, plus the scenario's own `Given`/`And` lines that appear **before** its first `When` (verbatim Gherkin text) | `.feature` file — see "Given/When/Then split" below |
| `Steps` | the scenario's `When`/`And` lines from the first `When` up to (not including) the first `Then` | same |
| `Expected Result` | the scenario's `Then`/`And` lines from the first `Then` onward | same |
| `Section` | the `.feature` file's `Feature:` title | `.feature` file header |
| `References` | the QAIA scenario ID (unprefixed, e.g. `QAIA-US-004-008`), the priority and technique tags, plus the `# condition:` rationale comment and confidence flag folded in as trailing free text | scenario tags + `.feature` comment + `coverage-matrix.md` |

**Given/When/Then split, and why.** Unlike Xray's CSV (one opaque `Cucumber Scenario` text field, no
separate slot for setup), TestRail's Text template offers three purpose-built fields —
`Preconditions`, `Steps`, `Expected Result` — that line up naturally with Gherkin's own three clause
roles. So instead of Xray's forced Background-flattening-into-one-field, this connector **splits**
each scenario at its first `When` and first `Then`: everything up to the first `When` (including the
flattened `Background`) becomes `Preconditions`; the action steps become `Steps`; the assertions
become `Expected Result`. This is a QAIA-side transformation the same way Xray's Background
flattening is — it makes the export usable in TestRail's own field model, it does not invent content.
**Caveat**: a handful of US-004 scenarios have no `When` at all (pure state-check scenarios, e.g.
"A report just under €500 needs only the manager's approval" — `Given`s then straight to `Then`,
nothing done). For those, `Steps` comes out **empty**. That is an honest reflection of the scenario
having no action, not a mapping defect — flagged to the user rather than silently left blank with no
explanation.

**QAIA `#` comments are not left in `Preconditions`/`Steps`/`Expected Result`.** They are QAIA
conventions (`# condition: …`), not Gherkin steps — they are relocated to `References` (see table),
not dropped.

**No invented `Description` field.** The fetched TestRail docs describe `Preconditions`, `Steps` and
`Expected Result` as the Text template's content fields and do not document a further freeform
"Description"/notes field as a universal default. Rather than invent one, the rationale/confidence
content that Xray's connector puts in a dedicated `Description` column is folded into `References`
here instead — say so plainly in the export summary, since a TestRail project that *does* have a
custom description-like field would let the user remap this more cleanly than QAIA can guess at.

## Honesty on the exact format (D38 anti-fabrication discipline)

The field names above (`Title`, `Type`, `Priority`, `Preconditions`, `Steps`, `Expected Result`,
`Section`/`Sections Hierarchy`, `References`), the single-row-vs-multi-row distinction, the
Text-vs-Steps template distinction, and the default `Low`/`Medium`/`High`/`Critical` priority scale
all come from TestRail's own published docs (`support.testrail.com`, "Import test cases from CSV or
Excel" and "Test case templates", both fetched directly on 2026-07-25), not recalled from training
data. Several things are **not** verified firsthand and should be treated as caveats, not
certainties:

1. **No live TestRail instance was available to test the import end-to-end.** Exactly the same
   limitation as the Xray connector: the docs describe the wizard's behavior, but this connector's
   CSV has never actually been run through TestRail's own step-2/step-3 mapping screens. TestRail's
   docs explicitly note the importer "supports all typical CSV variants" and standard comma-delimited
   files — that reads as RFC 4180-compatible quoting for commas/newlines inside fields, but the docs
   do not use the term "RFC 4180" and this connector's quoting was never confirmed against a real
   import.
2. **`Type` field values are project-customizable, more so than Xray's `Test Type`.** TestRail ships
   with project-specific `Type` dropdowns (the docs' own example shows a source system using
   `MANUAL`/`AUTO` mapped to arbitrary target values like `Functional`/`Automated`) — there is no
   single universal default list to target. This connector writes the constant `Automated` and relies
   entirely on the wizard's step-3 value mapping to reconcile it with whatever the target project
   actually has configured; that reconciliation was never exercised against a live project.
3. **The Given/When/Then split is a QAIA design choice, not a TestRail-documented convention.**
   TestRail's docs describe `Preconditions`/`Steps`/`Expected Result` in general terms (setup vs.
   actions vs. expected response) but never discuss Gherkin specifically — the mapping of
   `Given`→`Preconditions`, `When`→`Steps`, `Then`→`Expected Result` is this connector's own
   reasonable-but-unverified reading of how those three fields correspond to Gherkin's three clause
   types, not a documented TestRail↔Gherkin mapping.
4. **A native "Behaviour Driven Development" template exists in current TestRail** (seen in the
   fetched "Test case templates" doc) that may import Given/When/Then scenarios more directly than
   splitting them across three Text-template fields. This connector does **not** target that
   template — it was noticed during research but not investigated further this pass, so it is named
   here as a plausible better future path, not assumed to be it.

Nothing here should be read as "QAIA verified this against a live TestRail instance" — none was
available. The demo in `examples/expense-demo/` (see below) validates that the **CSV QAIA writes is
well-formed and matches the mapping table above**; it does not validate that TestRail accepts it
through the real import wizard, because that would require the live instance this connector
deliberately does not call.

## Steps (used by `testbook-export` when TestRail is the chosen target)

1. Confirm with the user this is an opt-in export (not one of the default three D25 deliverables) —
   ask for the target file path, default
   `.qaia/testbooks/<US-ID>/export/testrail/<US-ID>-testrail-import.csv`.
2. Read the `.feature` files and `coverage-matrix.md` only — no regeneration, same rule as the rest
   of `testbook-export`.
3. Build one CSV row per scenario per the mapping table above (exploding Scenario Outlines, applying
   the Given/When/Then split, relocating `#` comments into `References`).
4. Write the CSV (UTF-8, comma-separated, fields containing commas/newlines quoted per RFC 4180 —
   QAIA's own writing convention, since TestRail's docs don't name that spec explicitly). In Claude
   Code, materialize and run a short one-off script to do the mechanical CSV writing + re-parse check
   (decision D42 — deterministic file work as a session-generated, jettable script, not shipped
   code); on surfaces without file/script tooling, produce the CSV as a fenced code block the user
   saves themselves, same degrade-gracefully rule as the XLSX deliverable.
5. Tell the user plainly: this file was never tested against a live TestRail instance, the `Type` and
   `Priority` values are QAIA defaults to reconcile in the wizard's step-3 value mapping, some
   scenarios legitimately produce an empty `Steps` field, and the native BDD template was not
   evaluated as an alternative path.

## Security

- No credentials requested or read — this connector has none to read.
- No network call.
- No internal TestRail instance URL, project ID or suite ID is invented or required — the user's own
  import wizard supplies that context.
