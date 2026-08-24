# QAIA test-book quality rubric (10 dimensions, /20)

The scoring reference embedded in `qaia-score` so the plugin is self-contained. It mirrors the
project's canonical judge rubric ([`eval/RUBRIC.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/RUBRIC.md)); when the two ever diverge, [`eval/RUBRIC.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/RUBRIC.md)
is authoritative and this copy is updated to match.

Applied to **one** generated test book against **its** source US. Each dimension scores
**0 / 1 / 2**. **Maximum 20.** Default to the **lower** score when hesitating; justify every
score in one sentence citing the artifact (scenario ID, matrix row, manifest count).

## Dimensions

| # | Dimension | 2 | 1 | 0 |
|---|---|---|---|---|
| 1 | **Atomicity** | Every scenario verifies exactly one behavior; one `When`; no UI-step chaining. **Exemption:** at most one `@smoke` journey scenario per US, single journey-level outcome, excluded from this dimension — a second journey, or a journey re-verifying atomically-covered behaviors, is a violation | Isolated violations (≤ 10 % of scenarios) | Chained or multi-behavior scenarios are common |
| 2 | **AC coverage** | Every acceptance criterion covered by ≥ 1 scenario, and the coverage matrix proves it | One AC uncovered or matrix gaps | Multiple AC uncovered |
| 3 | **Negative-path coverage** (ADR 0001) | Every required negative condition (a rule that can refuse/error/deny) has a covering scenario; the negative ratio is reported as context | One required negative condition uncovered | Several uncovered (happy-path bias). *The raw negative ratio is a reported signal, not a threshold — never score on it.* |
| 4 | **ISTQB technique fit** | Techniques chosen fit the AC types and each choice is justified | Techniques applied but justification weak/generic | No identifiable technique or misapplied |
| 5 | **Business correctness** | No scenario contradicts the US; extrapolations flagged as assumptions | Minor unflagged extrapolations | A scenario asserts behavior the US contradicts (dangerous: plausible-but-wrong) |
| 6 | **Ambiguity handling** | Ambiguities surfaced as questions or flagged assumptions, not silently resolved | Some ambiguities silently resolved | Ambiguities invented into firm requirements |
| 7 | **Stable IDs & traceability** | Every scenario tagged `@QAIA-xxx`, unique, linked to its AC; matrix consistent | IDs present but gaps/duplicates | No stable IDs |
| 8 | **Gherkin form** | Valid Gherkin, English keywords, consistent vocabulary, correct `Background`/`Scenario Outline` use | Minor inconsistencies | Invalid or inconsistent Gherkin |
| 9 | **Prioritization** | Every scenario carries a risk-based priority with a stated rationale; human arbitration points identified | Priorities present without rationale | No prioritization |
| 10 | **Review support** | Synthesis by technique, review order by risk, confidence score marking extrapolated scenarios (D31) | Synthesis present but no confidence marking | Raw scenario dump |

## Output

A table (dimension, score, one-line justification), the total `/20`, and a **top-3 fixes**
list — the three changes that would most improve the score. The top-3 is what `qaia-core`
consumes to iterate; `qaia-score` only names the fixes, never applies them.

## Release-gate reminder (feeds `aptitude-gate`)

The project release gate is **median ≥ 16, no dimension at 0, and no dimension dropping ≥ 1
versus the previous baseline.** A single book's score of ≥ 16 with no 0-dimension is a PASS
candidate; a 0 on any dimension is a hard FAIL regardless of total.
