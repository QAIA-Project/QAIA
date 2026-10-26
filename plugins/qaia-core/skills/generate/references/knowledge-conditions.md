# Step 3d — knowledge-driven conditions

**This is the RAG in use, and it is what breaks step 3c's honest-recall ceiling.** The config-
and policy-driven coverage a thin US cannot yield is exactly what the knowledge base holds.

Follow the shared retrieval protocol (`../README.md`, "Knowledge retrieval & citation"): route
through `knowledge/index.md`, match the current AC's entities, domain and verbs, and open **only**
the matched files.

---

## Decompose composite rules first — do not skip

Before deriving conditions from a matched entry, check whether it is **composite**: a single
numbered item in `business-rules.md` bundling several distinct sub-facts under one heading — a
per-tier or per-category table folded into prose, an enumeration of thresholds each attached to a
different case, several independent properties of the same entity.

If it is, **write out each sub-fact as its own clause first**, then derive conditions per clause,
not per rule item.

Worked example — a tiered-allowance rule yields **7 clauses, not 1**:

| # | Clause |
|---|---|
| 1 | Basic: 8 credits/month |
| 2 | Basic: no rollover |
| 3 | Premium: 20 credits/month |
| 4 | Premium: rollover capped at 10 |
| 5 | Premium: rollover beyond 10 forfeited |
| 6 | Unlimited: uncapped credits |
| 7 | Unlimited: 1 active booking/day cap |

**The measured failure this closes** ([`eval/baselines/rag-recall-gain.md`](https://github.com/QAIA-Project/QAIA/blob/main/eval/baselines/rag-recall-gain.md)): `BR-KB-203` bundles
those 7 tier sub-facts in one paragraph. An unguided pass derived conditions only for the two
most **boundary-shaped** sub-facts — the rollover cap and the daily cap — and silently dropped
the four flatter baseline grants and properties. The rule was matched, open, and cited. Shape
attracted attention; substance did not.

---

## Deriving the conditions

For every applicable entry — **and every sub-clause of a composite entry** — derive a concrete
test condition. Applicable entries include: a role that may not perform the action, a config or
feature flag that changes the outcome, a threshold or rounding the US left implicit, an anomaly
from `anomaly-history.md` worth a regression condition.

**One condition per sub-clause, not one per rule item.** A composite rule with N distinct
sub-facts yields N cited conditions, unless a sub-fact is genuinely not independently observable.

Each condition:

- **cites its source rule** (`# rule: BR-KB-nnn`) and is numbered like any other (`AC3-C5`). When
  several conditions come from sub-clauses of the same composite item, **each still gets its own
  ID and its own citation** — never collapse them into one catch-all condition;
- is **`[req-neg]`** when the rule denies or refuses;
- inherits `[assumption]` / `@low-confidence` **only if the rule itself is uncertain**. A
  promoted, human-validated rule is *not* an assumption — it is project truth;
- **if it contradicts the source**, is raised as a question for `need-understanding` rather than
  applied silently. The US wins unless the user says otherwise.

## The one legitimate exception, and its guard

If a sub-clause genuinely cannot be exercised independently of another — its only observable
effect is inside a combined scenario — it may share a condition with that other sub-clause. **Say
so explicitly** ("sub-clauses X and Y are not independently observable, tested together") rather
than defaulting to it.

The rule cuts both ways: do not **inflate** the count by fabricating a condition for a sub-fact
with no observable behavior of its own, and do not **deflate** it by folding testable sub-facts
together for convenience.

## Recording

Record the applied rule IDs so `report` can populate `design.knowledgeApplied`.

**Knowledge base absent** → record "knowledge base absent" and proceed on the source alone. Do
not invent its content; that is the fabrication step 3c forbids.
