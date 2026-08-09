---
name: rag-build
description: Create or enrich the team's git-versioned QAIA knowledge base (.qaia/knowledge/) - glossary, business rules, application map, anomaly history - with a mandatory master index and small focused files. Use when capturing project knowledge or when another skill hands over a reusable rule.
---

# rag-build — team knowledge base

Follow the shared contract in `../README.md`. The knowledge base is shared by the team through git: treat every change as something a teammate will review in a PR.

## Layout it maintains

- `knowledge/index.md` — **master index, mandatory**: one line per file — `path | topic | tags`. Every read by any skill goes through this index — selective loading is what keeps the knowledge base affordable — so a file absent from the index is invisible.
- `knowledge/*.md` — one concern per file (a business rule cluster, a glossary section, one application area), **≤ ~2k tokens each**. Split rather than grow.

## Steps

1. **Initialize** (first use): create `knowledge/` with `index.md` and offer the four starter files — `glossary.md`, `business-rules.md`, `application-map.md`, `anomaly-history.md` — asking the user 2-3 seed questions for each they accept.
2. **Enrich** (routine): given a candidate rule/term (from the user or handed over by `need-understanding` / `feedback` / `confirm-fix`, whose closed defects land in `anomaly-history.md` as the missing test condition rather than as the bug):
   - check the index for the right target file; check the file for duplicates or **contradictions** with existing content;
   - on contradiction: show both statements, ⚠ VALIDATION — the user arbitrates which is true (loser is removed or marked superseded, never both kept);
   - write the entry with its provenance (US-ID, date, decided-by);
   - update `index.md` (and split the file if it crossed the size budget).
3. **Report.** Summarize what changed so the user can commit it (suggest a one-line commit message). Do not run git commands yourself unless the user asks.

## Guardrails

- Never store secrets, credentials, URLs of internal environments, or personal data in knowledge files.
- Provenance is mandatory on every entry — an unsourced rule cannot be trusted or challenged later.
- Keep entries declarative and testable ("cancellation is refused < 4h before start"), not narrative.
