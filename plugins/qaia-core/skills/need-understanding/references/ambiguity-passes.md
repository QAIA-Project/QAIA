# The three mandatory passes, and how to classify what they find

## Step 3 — adversarial pass by AC type

Run the type-specific checklist on **every** AC, before the cross-AC pass.

### State machine / lifecycle

- **Re-entrance** — can a state be reached **more than once**? `corrected` → `corrected` again, a
  chain of corrections?
- For any "supersedes / references predecessor" rule: does it point to the **immediate**
  predecessor, or to the **whole chain**?
- Forbidden transitions. Terminal states.

### Auth / tokens / permissions

Revocation versus expiration · scope change mid-session · indistinguishability rules under every
response path.

### Sorting / pagination

Tie-break on equal keys · out-of-range pages · the degenerate case where filters remove 100 % of
results (the **shape** of the empty response).

### Thresholds / quantities

Inclusive versus exclusive at every bound · rounding · units · reference clock.

### Two hard rules from this pass

**Any test-data choice that sidesteps an undefined case is forbidden without a Q-item.** If you
pick distinct dates to avoid an unspecified tie-break, the tie-break becomes a numbered question
first. Choosing data that dodges the ambiguity is how an ambiguity disappears without anyone
deciding it.

**Access boundary → question, never assumption.** When the US does not state whether an action
needs authentication or is public, it is `[open]`. Never assert "unauthenticated → redirect to
sign-in" when the source implies public read access — that is a scenario contradicting real
behavior. Generate the guessed side only as `@low-confidence`, citing the question.

---

## Step 4 — cross-AC interaction pass

For **every pair of ACs** sharing a resource, entity or time window — a slot, a counter, a
document state — ask: *what happens when the outcome of rule A feeds rule B at B's boundary?*

Example: an item freed by a cancellation rule re-entering an availability rule inside its cutoff
window.

Log each interaction as covered, `[assumption]`, or `[open]`. **Intra-AC hunting alone misses
exactly these.**

---

## Step 4a — triple-AC contradiction pass

Pairs are not enough: some contradictions only appear when **three rules meet**.

Explicitly enumerate triplets where a *protected/restricted state* rule, a *filtering/scoping*
rule, and an *anti-disclosure / error-shape* rule apply to the same entity — and ask which wins at
their intersection.

**Calibration example.** A patient whose lab results are **all marked `restricted`** by one AC,
requested by an **org-scoped** token per a second AC, under a third AC's **"return 404 so the
resource's existence is not disclosed"** rule. Is the answer an empty `200` list, or a `404`?

Each rule is unambiguous alone. The pairs are consistent. **Only the triple is undecided** — and
that is a mandatory question, never a silently chosen default.

---

## Step 5a — classification decision tree

Apply in this order, **stop at the first match**.

### 1. The source answers it literally, for the exact case at hand → **answered** (cite the line)

**A citation is not an answer when the US does not cover the symmetric or edge case.** Quoting
"maximum thresholds are reduced by 50 %" does not answer "does the reduction also apply to the
*minimum* threshold?". That stays a question — never `answered`.

### 1b. Out-of-slice answer (sibling story)

If the answer plausibly lives in another backlog story (per `00-source.md` `dependencies:`) but
not in the ingested slice, it stays a **question tagged `[out-of-slice]`** — not `answered` (you
do not have the text) and not silently defaulted. Note which sibling story likely holds it.

### 2. Protected domain + source silent → **`[open]`**

Minors or protected populations, money or billing, health-data access or retention, legal or
compliance evidence. Any default there is a product decision.

*Exception — money-mechanical versus money-policy.* A money-adjacent point whose answer is
**mechanically forced** rather than a policy choice ("a fine stops growing once the item is
returned" — the opposite is absurd) is `[assumption]`, not `[open]`. Reserve `[open]` for genuine
money **policy**: rate, cap, rounding, grace.

### 3. A safe default a reasonable practitioner would accept without escalation → **`[assumption]`**

### 4. Otherwise → **`[open]`**

### Calibration

| Question | Step | Outcome |
|---|---|---|
| "Does returning an item restore the loyalty points it earned?" | 3 | `[assumption]` — safe default: yes, flagged |
| "Is a declined payment attempt a reportable event?" | 2 (compliance evidence) | `[open]` |
| "No billing address on file for a corporate account" | 2 (regulated counterparty) | `[open]` |

<!-- These examples are deliberately drawn from a retail domain. An earlier version used three
     ambiguities from `US-001-appointment-booking`, which is the story handed to pilot testers:
     every run of this pass loaded them pre-identified and pre-classified, so the pilot measured
     recall of the reference file rather than analysis of the requirement. A calibration example
     must never come from a corpus the tool is evaluated on. -->

---

## Why silence on a category is itself the defect

Step 5 requires walking every category of step 2 and recording, for each, either the question you
are asking **or** an explicit "not applicable here: `<reason>`".

**A worked example of the cost.** On an API story, the response's timestamp format was an
unspecified data rule — step 2's very first category — and received no question. Downstream,
`istqb-design` promoted an example value into an ISO-8601 oracle, and the real API returned epoch
milliseconds. **A false oracle shipped in the test book**: a scenario asserting a format the
system never promised.

Silence on a category is what let it through. A category simply absent from your output is
indistinguishable from one you forgot, and the reader cannot tell the difference.
