---
name: testbook-score
description: Score a QAIA test book against its source US with the ISTQB-grounded 10-dimension rubric (0/1/2 per dimension, /20) plus a top-3 fixes list, and record the score in the standardized run manifest. Read-only over test content - it judges, it never edits. Use to review a generated test book or gate a release candidate.
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

# testbook-score — the quality scorecard

Applies the embedded rubric (`rubric.md`, mirroring [`eval/RUBRIC.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/RUBRIC.md)) to **one** test book
against **its** source US, and writes the result into the `gate` block of the standardized run
manifest (shared output contract, `../../OUTPUT-CONTRACT.md`). It **scores only** — see the scoring-only guardrails
in `../README.md`. It is the LLM-judge of the project, packaged as an installable skill.

## Prerequisites

- A generated test book: `.feature` files, `synthesis.md`, `coverage-matrix.md` under
  `.qaia/testbooks/<US-ID>/`, and the source US (`00-source.md` / `01-extraction.md`).
- Ideally `.qaia/reports/<US-ID>/manifest.json` (from `qaia-core:report`) for the normalized
  counts. If absent, offer to run `report` first; do not score against guessed counts.

## Steps

0. **Deterministic structural pass FIRST — not an LLM self-note.**
   Before any LLM judgment, compute a **reproducible structural score** the same way every run.
   A structural score measures form, not substance: a test book can be perfectly shaped and still
   assert nothing (the founding project measured one at 100/100 by machine and 58/100 by a human
   reviewer). So this pass is a **gate** that can force a FAIL, not a vanity number, and it is
   kept **separate** from the LLM rubric (two numbers, never conflated).
   - **In Claude Code**: run the shipped scorer, do not re-implement it —
     `python "${CLAUDE_PLUGIN_ROOT}/scripts/structural_score.py" --batch <folder of .feature files>`
     (standard library only; JSON on stdout). It ships inside the plugin as of 2026-08-09; before
     that this skill asked you to materialise the algorithm in session, so two runs on the same
     file could legitimately disagree. **The algorithm below documents what the scorer does; it is
> Si `${CLAUDE_PLUGIN_ROOT}` n'est pas defini dans votre environnement, le fichier se
> trouve a cote de cette skill : `../../scripts/` depuis le dossier du SKILL.md.

     not a specification to re-implement.** Proof it discriminates:
     [`eval/tools/structural_score.py`](https://github.com/QAIA-Project/QAIA/blob/main/eval/tools/structural_score.py) + [`eval/baselines/structural-score.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/baselines/structural-score.md). **Those two paths
     live in the QAIA source repository, not in the installed plugin** — do not send a user
     looking for them in their own project. They exist so a maintainer can check this algorithm
     still discriminates; everything needed to run it is written out below, which is why the
     plugin ships no code.
   - **Without code execution**: execute the algorithm step-by-step (reproducible by construction
     of the prompt; say so — it is weaker than running the code).
   - **Algorithm (explicit budget /100):** readability 25 · completeness 30 (% of ACs covered by a
     scenario that *really* asserts) · coherence 20 (no truncated step) · traceability 25 (stable
     `@QAIA-*` ID + AC link). **Detectors that force FAIL regardless of score:**
     - **C1 — hollow AC**: a `Then` whose only evidence is an image/table/screenshot reference →
       the AC is **not** counted covered (the us-ingest "images = not analyzed" rule made visible).
     - **C2 — no expected result**: a `Then` that is empty or only restates success ("works",
       "responds correctly") with no verifiable value/state/status → a question, not a test.
     - **Fabrication sniffer**: technical literals (URL, host, port, id, amount) that do **not**
       trace to the source US or a cited oracle → penalty; plus `[À DÉFINIR]`/`TODO`/placeholder
       markers (−5 each). **≥3 hits → forced STOP.** The sniffer is only fully effective **with the
       source/oracle** to compare against — always feed it the source, never run it blind.
   - **Write the result into the manifest's `structural` block**, not only into the report prose:
     `{ score, max: 100, gate, forcedStop, findings, scoredBy, at }` — bands `PASS ≥80`,
     `CONCERNS ≥60`, `FAIL <60`, or `FAIL` outright on a forced stop, whatever the score.
     This block is separate from `gate` and the two are **never merged**: `structural` is the
     reproducible machine pass, `gate.score` is the /20 rubric below. A forced STOP caps the
     release verdict at FAIL no matter how good the LLM rubric looks — and because the verdict is
     decided by another skill, the finding has to survive in the file rather than in this
     session's prose. Until this block existed, the most binding gate of the product was computed,
     reported, and then lost.

1. **Assemble the judge inputs** — the source US, the `.feature` files, the synthesis and the
   coverage matrix. **Do not** load the generation session's reasoning: the rubric is a
   fresh-eyes judgment (protocol in `rubric.md`). If this same session generated the book, say
   so — a self-review is weaker evidence than a fresh-session judge, and that limitation is
   part of the output.
2. **Score each of the 10 dimensions** 0/1/2 per `rubric.md`. For every dimension:
   - cite the evidence (a scenario ID, a matrix row, a manifest count) in one sentence;
   - **default to the lower score** when hesitating;
   - never score dimension 3 on the raw negative *ratio* — score it on whether every
     **required** negative condition has a covering scenario; the ratio is context. (A ratio
     rewards volume: enough easy negatives will clear it while the refusal path the story
     actually specifies stays untested. The governing decision is ADR 0001, the required
     negative/refusal-path coverage gate, `https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0001-negative-coverage-gate.md`.)
3. **Verify literals independently** where a dimension depends on them (boundary ±1, string
   lengths, checksum/oracle values) — recompute, do not trust the book's own assertion. A
   wrong literal presented as correct is a dimension-5 hit (plausible-but-wrong).
4. **Total and top-3.** Sum to `/20`. Produce the **top-3 fixes**: the three changes that would
   most raise the score, each pointing at the artifact to change. This is advice for
   `qaia-core` — name the fix, never apply it here.
5. **Write the score into the manifest.** Merge into `gate` (contract rule 2 — never clobber
   `design`/`execution`/`status`): `score`, `max: 20`, `scoredBy: "qaia-score/testbook-score"`,
   `at`, and `dimensions` listing **only** the dimensions scored below 2 (with `n`, `name`,
   `score`). Do **not** set `verdict` here — the PASS/CONCERNS/FAIL/WAIVED decision is
   `aptitude-gate`'s job; leave any existing verdict for it to recompute. If no manifest
   exists, emit the scorecard and offer to run `report`.
6. **Report** the table (dimension, score, justification), the total, the top-3, and — when
   scoring against a baseline the user provides — the per-dimension delta, flagging any
   dimension that dropped ≥ 1 (a release-gate regression).

## Guardrails

- **Read-only over test content** — the only write is the manifest `gate` block. Never edit a
  scenario, matrix or synthesis (scoring-only guardrail 1).
- **No inflation.** Encouraging but wrong is a disservice; the lower score and the honest
  regression flag are the value. `simulated`/`[open]` items still pending human arbitration are
  reported as caveats, and cap the eventual verdict at CONCERNS (enforced by `aptitude-gate`).
- **Portable.** Reads markdown + JSON, writes JSON; no network, no API key. Without file
  tooling, emit the scorecard and the `gate` fragment as fenced blocks.
