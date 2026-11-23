# Contributing to QAIA

Thank you for considering a contribution. QAIA has an unusual constraint you must understand before contributing: **the maintainer does not read code**. The project is built through agentic sessions and validated by usage, evaluation harness, and CI. The rules below exist to keep that model safe.

## Ground rules

1. **DCO sign-off is mandatory.** Every commit must carry a `Signed-off-by:` line (`git commit -s`), certifying the [Developer Certificate of Origin](https://developercertificate.org/). PRs with unsigned commits are closed.
2. **License.** By contributing you agree your contribution is licensed under [MIT](LICENSE).
3. **Small PRs.** One concern per PR. A PR that mixes a skill change with a doc change will be asked to split.
4. **CI validates form only** (JSON manifests, Gherkin syntax, structure). Green CI is required but **never sufficient**.

## Contributing to plugin content (special rules)

Skills are prompts that drive the user's Claude session with the user's permissions. A malicious or careless instruction is **invisible to linters** and can exfiltrate data or trigger unwanted actions in every installer's session. These rules apply to any PR touching **`plugins/**` (skills, scripts, manifests), `.claude-plugin/**`, or `.github/workflows/**`** — not just skill files:

- it undergoes a **traced adversarial agent review** (an agent instructed to attack the change: injection, exfiltration, scope creep, quota waste). This review is launched **by the maintainer** — or an automation only the maintainer can trigger — on the PR's diff, with the explicit instruction to treat the diff as untrusted data and ignore any instruction it contains, and with no network or write tools. **A review posted by the PR author has no probative value.** The review summary is posted in the PR before merge — no exceptions;
- it must be **demonstrated by usage**: include in the PR description the conversation excerpt or output showing the change behaving as intended. The maintainer reproduces this validation in a **disposable environment** (empty project, session without credentials, minimal permissions) — never in their working session;
- the **evaluation harness (`eval/`) must be green before merge** for any change to generation skills — not merely before release. What lands on the default branch is what installers get;
- it must not introduce network calls, external fetch targets, or instructions to run commands unrelated to the stated purpose;
- **hooks, MCP servers, and agent definitions are not accepted in the core plugins** (CI enforces this on `plugins/**`): they auto-execute code in installers' environments. Per **ADR 0002 / D42**, they are not banned outright — they belong in a **separate opt-in tier** (its own package, never installed by the core, disabled by default, documenting exactly what it executes), each component carrying the traced adversarial review above, and only **after the core is pilot-proven** (founding lesson #2: unknown public). Propose them in an issue first.
- **Pinned Python that runs only when invoked is accepted** (ADR 0002 / D42): since 2026-08-09, `qaia-score` ships its deterministic scorers as readable Python under `plugins/qaia-score/scripts/`, run in the user's session (their permissions, their eyes) only when they invoke `judge`. These files are copies of `eval/tools/`, kept identical by `eval/tools/ship_scorers.py` and checked in CI; change the `eval/tools/` source and re-run the sync, never edit the shipped copy. Nothing runs at install or on its own, so this is not a hook/MCP/agent.

## Contributing elsewhere

Docs, translations, gold set user stories, rubric improvements, bug reports and connector requests are all welcome and reviewed faster than skill changes. Connector requests are prioritized by 👍 votes on their issue.

## Project-management discipline

The GitHub **board is the source of truth for open work** — keep it in sync with reality *as you go*, not only at the end:

- **File an issue the moment you discover a gap, defect class, or idea** — mid-work, not at review time. A finding that lives only in a commit message or a doc is a finding that will be lost.
- Docs record *measurements* (`eval/<campaign>/REPORT.md`, `eval/baselines/`) and the *work order* (`docs/ROADMAP.md`); **issues track what remains open**. Both, always. `docs/DECISIONS.md` is frozen since 2026-11-23 (D203): a decision now lives in the issue or the commit that carries it.
- Close an issue only with a one-line proof of delivery; if its exit criterion routes through a human gate (pilots), mark it "build-complete, pending &lt;gate&gt;", never "done".
- Run `/session-review` at the end of a working session to verify, measure, sync the board, and deliver the branch.

## Workflow

1. Open an issue first (template: *Proposition*) — it lands in the **To challenge** column of the board and is evaluated on value / effort / founding-lesson risk / acceptance criterion.
2. Fork, branch, commit with `-s`, open the PR referencing the issue.
3. Address review feedback; the maintainer validates by using the result, not by reading the diff.

## Releases

Skills are versioned per plugin (SemVer — bump `plugin.json`'s `version`, it is the value installers see). A version bump also updates the version claims in the plugin's README, the root READMEs and `docs/STATUS.md` (`eval/tools/check_skill_counts.py` fails otherwise) and adds an entry to [`CHANGELOG.md`](CHANGELOG.md). The evaluation harness runs green **before merging** any generation-skill change; a release additionally records the scores as the new baseline in `eval/baselines/`.

Before pushing, run `make check` (the deterministic checks the CI runs; on a machine without `make`, run the `python` lines of the `check` target one by one).
