---
name: testbook-export
description: Export the generated test book for human rework and reporting - .feature files as source of truth, a natural-language rendering readable without Gherkin (verified step by step against its source), plus an XLSX and Markdown synthesis with coverage matrix, review order and confidence scores, plus opt-in file-only Xray and TestRail CSV exports (git-master mode, no API key). Use when test cases must leave the repository - handed to a test manager, imported into Xray, TestRail or Jira, reviewed in a spreadsheet, or attached to a release report. Seventh step of the QAIA journey.
---

# testbook-export — hand the book to the humans

Follow the shared contract in `../README.md`. Prerequisite: a generated test book in
`.qaia/testbooks/<US-ID>/` (else offer `testbook-generate`).

**Export is a projection, never a second source.** Everything below is built from the checkpoint
and testbook files; nothing is regenerated, and no new content is invented on the way out.

## Deliverables

1. **`.feature` files** — already the source of truth, exported as-is (copied to the user-chosen
   location if outside the repo).

2. **Markdown synthesis** (`synthesis.md`) — the review aid. Its authoritative contract lives in
   `../README.md`, "Deliverable contract — synthesis.md". This skill **re-projects it; it never
   redefines it.**

3. **Natural-language rendering** (`testbook.<lang>.md`) — the same book for a reader who does
   not read Gherkin: a business analyst, a test manager, whoever signs. **A projection, never a
   second source**, and this one is *checked*: [`check_nl_projection.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/check_nl_projection.py) fails if a
   single step is invented, lost or reordered.

   Format — deliberately rigid, because the rigidity is what makes verification possible:

   ```
   ---
   language: en          <- closed list: fr | en
   source: booking.feature
   ---

   ### QAIA-US-001-014 · A valid request creates the appointment

   Requirement: AC2 · Priority: 1 (highest) · Level: API (service contract) · Technique: boundary values

   **Preconditions**

   1. an authenticated patient
   2. slot "S1" opens at 09:00

   **Action**

   3. they POST /appointments with slotId "S1"

   **Expected result**

   4. the response status is 201
   ```

   - `Given` → *Preconditions*, `When` → *Action*, `Then` → *Expected result*; `And`/`But` inherit
     the previous keyword's bucket. `Background` steps open every block's preconditions.
   - **The step text is copied verbatim.** Only the keyword is replaced by the heading. Rewriting
     a step "to read better" is exactly the drift the check exists to catch.
   - Tags become words (level, priority, technique, refusal path, open question) — a reader who
     needs the tag vocabulary explained is not the reader this file is for.
   - **`Scenario Outline` is exploded**: one block per `Examples` row, ID suffixed `-eN`, each
     `<parameter>` replaced by that row's value. Same convention as the XLSX, so the two count
     the same book.

   Why the rigidity is not bureaucracy: this is the document people will actually read, and
   therefore the one nobody re-checks against its source. `testbook-export` already carries the
   rule that an export is a projection; before 2026-08-11 nothing enforced it, and this repository
   has measured seven times in one session what a rule enforced by intention alone is worth.

4. **XLSX workbook**, for teams reviewing in spreadsheets:

   - *Scenarios* — ID, title, AC, condition, technique, priority, negative?, confidence,
     **Preconditions, Action, Expected result** (the three natural-language columns, same content
     as the Markdown rendering), and Gherkin text. **A `Scenario Outline` is exploded into one row
     per `Examples` line**, with the ID suffixed `-eN`.
   - *Coverage matrix*.
   - *Decisions & assumptions* — ID, type (`answered` / `assumption` / `open` / `simulated` /
     `waiver`), statement, source checkpoint. Aggregated from `02-understanding.md` **and** the
     waivers and scope decisions of `03`-`04`.

   In Claude Code, build it with the available spreadsheet tooling. On surfaces without file
   tooling, produce CSV blocks the user can paste — and say plainly that is what you did.

5. **Xray or TestRail CSV export (opt-in)** — *not* one of the four defaults. Offered when the
   user names Xray or TestRail as their test-management target.

   File-only, **git-master mode**: the `.feature` files in git stay the master copy, the CSV is a
   one-way projection, and nothing is ever read back from the tool. One row per scenario, for
   Jira's CSV/Test Case Importer (Xray) or TestRail's import wizard.

   Field mapping, `Background`-flattening and Given-When-Then split rules, and the honestly
   flagged format uncertainties live in `connectors/xray.md` and `connectors/testrail.md`.
   **Follow the matching file; do not improvise the column layout here.**

## Steps

1. **Ask target location** (default `.qaia/testbooks/<US-ID>/export/`) and which deliverables
   (default: all four). Mention the opt-in Xray or TestRail CSV if the user has a
   test-management tool to feed.
2. **Build from checkpoint and testbook files only.** Any discrepancy the export reveals is fixed
   **in the source files first**, then re-exported. For Xray follow `connectors/xray.md` step by
   step; for TestRail, `connectors/testrail.md`.
3. **Verify the natural-language rendering against its Gherkin before handing it over.** In the QAIA
   repository that is [`check_nl_projection.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/check_nl_projection.py); elsewhere it is the same three
   questions, one scenario at a time — is every scenario there, are its steps the same ones in the
   same order, is any step in the rendering absent from the `.feature`. **Never ship a rendering
   that has not been confronted with its source**: it is the copy people read.
4. **Confirm what was produced and where.** Remind the user the `.feature` files remain the
   source of truth and that manual edits there are preserved by regeneration.

   Repeat the connector's own caveats so the file is not mistaken for pre-verified:
   - **Xray** — version drift, Labels mapping, never tested against a live instance.
   - **TestRail** — Type and Priority are QAIA defaults to reconcile in the wizard, some
     scenarios legitimately produce an empty Steps field, never tested against a live instance.
5. **Update `journey.md`.** Next steps: reporting, then `feedback` after the review.

## Guardrails

- **Never export secrets or environment details** that may sit in the repo. The export contains
  only testbook and checkpoint content.
- **If the testbook and the matrix disagree** (hand-edited), stop and surface the discrepancy
  instead of exporting a lie.
- **Neither CSV export calls a live API** (Xray/Jira or TestRail) nor asks for a credential. Both
  are export-only; a live push stays a future opt-in tier, deliberately outside the core, and not
  this skill.
