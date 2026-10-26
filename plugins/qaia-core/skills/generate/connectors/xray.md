# Export connector — Xray for Jira (issue #35, D10 v1 test-repo target: Xray, git-master mode)

How `testbook-export` projects a QAIA test book into a file Xray for Jira can import. **Export-only,
file-only** (decision D29, portable-first): this connector never calls the Xray or Jira API, never
stores or asks for an API token, and makes no network call. It writes a file; the user imports that
file themselves through Jira's own import wizard, on their own schedule, in their own instance.

**Direction matters — do not confuse with `us-ingest/connectors/jira.md`.** That connector is a
*source* connector: it may, opt-in, fetch one designated issue on the live path. This connector is
the opposite direction (test book → test-management tool) and stays 100 % file export, always — no
opt-in live path exists here yet. A future live push (real API call, credentials held by the user,
never in the core) is exactly the "M2 connectors" placeholder this file replaces; it is not built.

## What ships today: CSV, for Jira's CSV/Test Case Importer

Xray Test issues are plain Jira issues of issue type `Test`, so they import through Jira's regular
CSV importer once the CSV carries Xray's own Test-specific columns. This is the git-master path:
commit the CSV next to the test book, the user runs Jira's **System → External System Import → CSV**
wizard (or Xray's dedicated Test Case Importer, which the source docs recommend specifically when a
file mixes Manual and Cucumber tests) and maps columns interactively — QAIA does not (and cannot)
drive that wizard; it only produces a CSV the wizard can consume.

### Column mapping

One row per **scenario** (a `Scenario Outline` is exploded into one row per `Examples` line, ID
suffixed `-eN` — the same rule the XLSX deliverable already uses, kept consistent across exports).

| CSV column | Value | Source |
|---|---|---|
| `Issue Type` | `Test` | constant |
| `Test Type` | `Automated[Cucumber]` | constant — **version caveat below** |
| `Cucumber Test Type` | `Scenario` or `Scenario Outline` | the Gherkin keyword actually used |
| `Summary` | scenario title, `- Examples N` appended for an exploded outline row | `Scenario:`/`Scenario Outline:` line |
| `Cucumber Scenario` | the scenario's Gherkin **steps only** (`Given`/`When`/`Then`/`And`/`But`), with any `Background` steps flattened in ahead of the scenario's own steps | `.feature` file — see "Background flattening" below |
| `Labels` | one label per QAIA scenario ID with the leading `@` stripped (Jira labels reject `@`), plus the priority tag (`P1`/`P2`/`P3`) and the technique tag | scenario tags |
| `Priority` | `P1→Highest`, `P2→Medium`, `P3→Low` — **a QAIA default mapping, not an Xray requirement**; say so to the user and let them override it to match their project's real Jira priority scheme | `coverage-matrix.md` priority column |
| `Description` | the `# condition:` comment (rationale) plus the confidence flag (`@low-confidence` → "low confidence — see open question `Qn`") | `.feature` comment + `coverage-matrix.md` rationale/confidence columns |

**Background flattening, and why.** QAIA `.feature` files put shared setup in a `Background:` block
(one block, reused by every `Scenario` in the file — see `../../README.md`
project-layout convention). Xray's per-Test `Cucumber Scenario` CSV field holds one scenario's steps,
not a whole feature with a shared `Background` — there's no separate "background" field documented
for the CSV path. So each row must prepend the Background's `Given`/`And` steps to that scenario's own
steps before writing `Cucumber Scenario`, or an Xray reviewer opening the Test in isolation sees a
scenario with a dangling `When` and no `Given`. This is a QAIA-side transformation to make the export
usable, not a fabricated Xray field — flag it in the export summary so the user knows the per-row
Gherkin was expanded, not copied verbatim.

**QAIA `#` comments are stripped from `Cucumber Scenario`.** They are QAIA conventions
(`# condition: …`), not valid Gherkin — Xray's Cucumber parser is not guaranteed to tolerate them the
way a `.feature` file consumer would. Their content is preserved, just moved to `Description` (see
table above), so nothing is lost, only relocated to a field built for prose.

## Honesty on the exact format (D38 anti-fabrication discipline)

The column names and `Test Type` values above (`Automated[Cucumber]`, `Cucumber Test Type`,
`Cucumber Scenario`) come from Xray's own published CSV-import documentation (Xray Server/Data
Center "Importing Tests with CSV" and the Test Case Importer pages, `getxraydocs.atlassian.net`),
fetched and read directly rather than recalled from training data. Two things are **not** verified
firsthand and should be treated as caveats, not certainties:

1. **Version drift.** Xray has shipped several CSV-import generations (3.0 archive, 4.0, 7.x Server/DC,
   Cloud) and the exact `Test Type` literal has varied across them (some older docs show bare
   `Cucumber` rather than `Automated[Cucumber]`). Before a real import, export Xray's own CSV template
   from the target instance (Test Case Importer → "download template") and diff it against this
   connector's header row — do not assume the header above is byte-exact for every Xray version.
2. **Multi-value columns (`Labels`).** Jira's CSV importer maps multi-value fields like `Labels`
   either as one label per repeated `Labels` column or via the wizard's per-cell split — which one
   depends on the importer/wizard version. This connector writes one `Labels` column with
   space-separated values (a common convention) and calls this out explicitly in the export summary
   so the user checks the mapping step of the wizard rather than assuming it "just works."

Nothing here should be read as "QAIA verified this against a live Xray instance" — no live Xray
instance was available to test the import end-to-end. The demo in `examples/expense-demo/` (see
below) validates that the **CSV QAIA writes is well-formed and matches the mapping table above**; it
does not validate that Jira/Xray accepts it, because that would require the live API call this
connector deliberately does not make.

## What does not ship today: TestRail

TestRail's CSV import is **column-mapped interactively** in its own wizard (no single fixed header
row — the user maps arbitrary CSV columns to TestRail fields such as `Title`, `Type`, `Priority`,
`Preconditions`, `Steps`, `Expected Result` in step 2 of the import wizard, per TestRail's own support
docs). A QAIA CSV using those field names as headers would very likely work, but this was **not**
built or exercised in this pass — time went to verifying the Xray path firsthand instead of adding a
second connector on secondhand confidence. Honest status: **not covered**, not "assumed to work like
Xray." A future pass should build `connectors/testrail.md` the same way this file was built — read
TestRail's own docs, map the fields, then generate and structurally validate a real CSV from a real
test book before calling it done.

## Steps (used by `testbook-export` when Xray is the chosen target)

1. Confirm with the user this is an opt-in export (not one of the default three D25 deliverables) —
   ask for the target file path, default `.qaia/testbooks/<US-ID>/export/xray/<US-ID>-xray-import.csv`.
2. Read the `.feature` files and `coverage-matrix.md` only — no regeneration, same rule as the rest of
   `testbook-export`.
3. Build one CSV row per scenario per the mapping table above (exploding Scenario Outlines,
   flattening Background, stripping `#` comments into `Description`).
4. Write the CSV (UTF-8, comma-separated, fields containing commas/newlines quoted per RFC 4180). In
   Claude Code, materialize and run a short one-off script to do the mechanical CSV writing +
   re-parse check (decision D42 — deterministic file work as a session-generated, jettable script,
   not shipped code); on surfaces without file/script tooling, produce the CSV as a fenced code block
   the user saves themselves, same degrade-gracefully rule as the XLSX deliverable.
5. Tell the user plainly: the caveats above (version drift, Labels mapping), that this file was never
   tested against a live Xray instance, and that TestRail is not covered.

## Security

- No credentials requested or read — this connector has none to read.
- No network call.
- No internal Jira/Xray instance URL is invented or required; the user's own import wizard supplies
  the project/instance context.
