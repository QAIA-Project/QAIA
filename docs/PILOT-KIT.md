# QAIA pilot kit — try it in 15 minutes

Lowers a pilot's effort from "1 hour on my own US" to "15 guided minutes". Give this to a candidate tester; it needs only Claude Code and this repo.

## What you'll do

Run the QAIA journey on a ready-made user story, get a Gherkin test book, and tell us where it's wrong. That's the whole point — your judgment is the product.

## Prerequisites (2 min)

- Claude Code installed, with a Claude subscription (the tool runs in *your* session — no API key).
- This repo cloned locally.

## Step 1 — Install the plugin (2 min)

```
/plugin marketplace add QAIA-Project/QAIA
/plugin install qaia-core@qaia
/reload-plugins
/qaia-core:hello        # should confirm it's installed
```

## Step 2 — Pick a story (1 min)

Two ways:
- **Fastest**: use the ready story `docs/pilot/US-001-appointment-booking.md` (a teleconsultation booking — 8 acceptance criteria).
  Do **not** open anything under `eval/gold-set/` while you are running the pilot: those files carry the answers, and reading one turns your run into a recall exercise. They are in the repository because the project needs them; they are not for you today.
- **Most useful to us**: bring one *real* user story of your own (anonymize anything sensitive — the tool will also redact PII, but you know your context best).

## Step 3 — Run the journey (8 min)

In Claude Code, just say:

> Use the QAIA `us-ingest` skill on `docs/pilot/US-001-appointment-booking.md`, then walk me through the journey.

> **Pourquoi cette copie et pas le fichier du gold set.** L'original porte une section
> `## Judge reference` qui **liste les ambiguïtés plantées exprès**. L'ingérer vous donnerait la
> réponse à la question que ce formulaire vous pose ensuite — la première mesure humaine du
> projet serait faussée par construction. Les critères d'acceptation des deux fichiers sont
> identiques à l'octet près.

The tool will, step by step, ask you to validate each stage: the captured source, the extraction, the ambiguities it found (answer or say "not specified"), the ISTQB techniques, the priorities, and finally generate the test book. **Say yes/no/correct as a real reviewer would** — that's exactly the conversational path we need to validate.

You end with `.qaia/testbooks/US-001/` containing `.feature` files, a coverage matrix, and a synthesis.

## Step 4 — Tell us what's wrong (2 min)

Open [a feedback discussion](https://github.com/QAIA-Project/QAIA/discussions) or fill the short form below and paste it there. **Negative feedback is the most valuable** — where did it guess wrong, miss a case, or annoy you?

```
### QAIA pilot feedback
- Story used: (gold set US-001 / my own)
- Time spent: __ min
- Scenarios generated: __   | kept as-is: __ %   | rewritten: __
- Best thing it did:
- Worst thing it did (be blunt):
- One ambiguity it should have caught but didn't:
- Would you use it again as-is? (yes / no / only if ___)
- Surface used: (Claude Code / Desktop / claude.ai)
```

## Optional — see automation run for real (5 min)

If you're curious, the `examples/medibook/` folder has a running demo app + Playwright tests (E2E, API, a11y, perf, security, visual — 26 tests, 32 executions). `cd examples/medibook/app && node server.js`, then in another shell `cd ../tests && npm i && npx playwright test`.

---

**Thank you.** Five testers who do this unblock the whole project — every real correction makes the tool sharper than any amount of automated evaluation could.
