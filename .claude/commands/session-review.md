---
description: End-of-session review for QAIA — verify, measure, update project management, deliver the branch
disable-model-invocation: true
allowed-tools: Bash, Read, Edit, Grep, Glob
---

You are running the **QAIA end-of-session review**. Produce a faithful review of what changed this session and leave the project in a clean, honest, delivered state. Do not flatter; surface regressions and gaps plainly. Follow these steps in order.

## 1. What changed
- `git log --oneline` since the session start (or last review) and `git diff --stat`.
- List, in plain language: skills added/changed (with version bumps), new plugins, new examples, docs touched.

## 2. Verify (no green claim without proof)
- `claude plugin validate <each plugin> --strict` — all must pass.
- Run the CI-equivalent locally: JSON manifests valid, supply-chain guards (no `hooks/`, `agents/`, `.mcp.json` in plugins; marketplace sources local), skill frontmatter, `gherkin-lint` on any `.feature`.
- Confirm no secrets/PII committed: grep for the sensitive patterns; confirm redaction rules intact.

## 3. Measure (the QAIA discipline — measured, not asserted)
- For any skill change: state whether it was run against the `eval/` harness and what the number was. **No skill change ships as "done" without a harness number.**
- Report honestly: recall/precision are **noisy** (LLM judge ±15-20 pts) — trust only same-run comparisons (train vs held-out, precision), never absolute deltas between waves.
- If a measurement was skipped, say so — a skipped measurement is a gap, not a pass.

## 4. Regression & overfitting check
- Did any prior baseline regress? (`eval/baselines/`). A regression blocks "done".
- If skills were tuned on examples, was a held-out set measured? Held-out ≥ train ⇒ generalization; held-out ≪ train ⇒ overfitting (flag it).

## 5. Update project management — the GitHub board must reflect reality
- **Standing rule (founder's instruction): file findings as GitHub issues *as they are discovered*, not only at review time.** Every new gap, defect class, or idea uncovered mid-work gets its own issue when found — the board, not just the docs, is the source of truth for what remains. Docs (`DECISIONS.md`, `eval/baselines/`) record *what was decided/measured*; issues track *what is open*. If this review finds work that was tracked only in docs, backfill the missing issues now.
- Sync `docs/ROADMAP.md` (tick what shipped, with its commit; say why anything slipped) and `docs/STATUS.md` (the two numbers, only when re-measured). `docs/DECISIONS.md` is frozen since 2026-11-23: a decision now lives in the issue or the commit that carries it.
- Sync GitHub issues: close what's genuinely delivered (with a one-line proof + the attribution footer), update in-progress ones, open issues for every new gap found. Be frugal with comment noise, not with issue coverage.

## 6. Deliver the branch
- Commit with `git commit -s` (DCO), a faithful message ending with the required co-author and session-link trailers.
- `git push -u origin <branch>` with retry/backoff. **No PR unless explicitly asked.**
- Confirm `git status` clean and remote in sync.

## 7. Honest closing summary
Report to the user: what shipped, what was measured (with the numbers and the noise caveat), what regressed (if anything), what remains (the RAF — separating agent-doable from owner/human-only, especially the pilots gate G2), and the single highest-value next lever. End with the resume prompt location (`docs/STATUS.md`).

Never mark a milestone "closed" if its exit criterion routes through the pilots or another human gate — say "build-complete, pending <human gate>" instead.
