# Using QAIA with BMAD

QAIA and [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) are complementary: BMAD structures *how a team builds software with AI agents* (brief → PRD → architecture → stories → dev); QAIA turns *requirements into professional test books and automation* (ISTQB techniques, atomic Gherkin, stable-ID traceability, diff-based regeneration). BMAD's TEA module architects testing from the **code**; QAIA designs tests from the **requirements** — you can run both.

## Where QAIA plugs into the BMAD cycle

| BMAD phase | QAIA skill to use | What you get |
|---|---|---|
| Phase 2-3 — PRD / epics & stories written | `us-ingest` → `need-understanding` | Ambiguity hunt on stories *before* dev starts (cross-AC interactions, type-specific adversarial pass) — cheaper than finding them in review |
| Phase 4 — story in implementation | full journey → `testbook-generate` | Prioritized atomic Gherkin book with coverage matrix, generated from the story file's ACs |
| Phase 4 — QA / code review | `testbook-validate` | Scored audit + PASS/CONCERNS/FAIL gate on any existing `.feature` set — including books QAIA didn't generate |
| Retrospective | `feedback` + `rag-build` | Corrections promoted (validated) into a git-versioned team knowledge base reused by the next generation |

Practical setup: install both (BMAD via its installer, QAIA via `/plugin marketplace add QAIA-Project/QAIA`).

**Checked against BMAD-METHOD v6.10.0 on 2026-08-09** — the two claims this paragraph used to make were both wrong, so here is what the source actually says:

- **Story files are not named `story-*.md`.** `bmad-create-story` builds the name from the story key, `{epic}-{story}-{title}.md` — e.g. `1-2-user-authentication.md`. The earlier instruction to glob `story-*.md` would have matched nothing. The location is configurable, so point `us-ingest` at the path your install actually uses.
- **BMAD writes its outputs to `_bmad-output/`**, not `_bmad/` — the latter is where the framework and its config live. The no-collision conclusion still holds (`.qaia/` touches neither), but for a different reason than previously stated.
- **The AC section is compatible, the rest of the file is not.** The template's `## Acceptance Criteria` is a numbered list, which is what QAIA wants. But the same file also carries `## Tasks / Subtasks`, `## Dev Notes` and `## Dev Agent Record` — implementation record, not requirement. `us-ingest` captures the designated source *whole* and by design adds nothing; it will therefore ingest those sections too. Extract the story statement and AC block into the source you hand it, or expect the downstream book to treat dev notes as requirement.

Not verified: no end-to-end run of BMAD-then-QAIA on a real project. The points above are read from BMAD's own skill definitions and template, not from a completed cycle.

## Differences to keep in mind

- QAIA validates **with the tester at every step** (regulated-context contract); BMAD has unsupervised loops — don't pipe QAIA outputs into an auto-loop if you need the audit trail.
- QAIA is Gherkin/Playwright-native and requirement-first; TEA is framework-scaffolding and code-first. Use TEA to stand up the automation infra, QAIA to decide *what deserves testing and why*.
- QAIA runs entirely in your Claude session (no API key, quota honesty) — same philosophy as BMAD's "the LLM is the engine".
