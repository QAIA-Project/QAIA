# Meilisearch — defect-hunting campaign

| | |
|---|---|
| **Date** | 2026-08-11 |
| **Target** | Meilisearch **v1.53.0** — `meilisearch-windows-amd64.exe` |
| **Release** | published 2026-08-10T09:15:27Z, commit `979167f13b5f53c8a4e0bd3b3a0edddf37a2e137` (built 2026-08-10T08:29:59Z) |
| **Deployment** | self-hosted on `127.0.0.1:7700` and `:7701`, Windows 11, no Docker, no Meilisearch Cloud, no third-party service |
| **Oracle** | the prose documentation at `https://www.meilisearch.com/docs/` — never the source code |
| **Probe** | [`probe.js`](probe.js) — 45 checks, rejouable |
| **Raw output** | [`evidence.txt`](evidence.txt), [`run2.txt`](run2.txt), [`run3-freshdb.txt`](run3-freshdb.txt), [`run4.txt`](run4.txt), [`minimal-repro.txt`](minimal-repro.txt) |

## Version caveat, stated up front

`www.meilisearch.com/docs` is unversioned and describes the current release. v1.53.0 **is** the
current release (published the day before this campaign), so the online documentation and the
binary under test are the same generation. Every quoted promise below was fetched on 2026-08-11
from the live docs as raw Markdown (`<page>.md`), not paraphrased from memory.

## How to reproduce

```bash
curl -sL -o meilisearch.exe \
  https://github.com/meilisearch/meilisearch/releases/download/v1.53.0/meilisearch-windows-amd64.exe
./meilisearch.exe --http-addr 127.0.0.1:7700 --master-key QAIAmasterKey2026probe \
  --db-path ./data.ms --no-analytics &

MEILI_URL=http://127.0.0.1:7700 MEILI_KEY=QAIAmasterKey2026probe node probe.js
```

The probe is self-contained (Node 24, no dependencies), rebuilds its own fixtures, and prints the
verbatim documented sentence next to every deviation.

## Result

**45 numeric / semantic promises exercised — 42 matched, 3 deviated.**
Of the 3 deviations, **2 are one already-reported open bug** and **1 is a new, small documentation
defect**. Zero new *product* defects established.

Every deviation reproduced **four times**: probe run on instance A (`run2.txt`), probe run on a
fresh process with an empty database (`run3-freshdb.txt`), a repeat run on that instance
(`run4.txt`), and a standalone curl-only reproduction with 3 documents (`minimal-repro.txt`).
The 42 conforming checks were likewise stable across all four runs.

---

## Promises exercised

### Typo tolerance — 10 checks, 10 matched

Oracle: `/docs/learn/relevancy/typo_tolerance_settings`

> If the query word is between `1` and `4` characters, **no typo** is allowed. […] between `5` and
> `8` characters, **one typo** is allowed […] more than `8` characters, a maximum of **two typos**.
> Meilisearch considers a typo on a query's first character as two typos.
> `0 ≤ oneTypo ≤ twoTypos ≤ 255`

Both numeric thresholds were probed at the value and at the value ±1, using six disjoint invented
roots so no query could accidentally prefix-match a neighbouring fixture.

| Check | Boundary | Verdict |
|---|---|---|
| `TYPO-01` | 4-char query, 1 typo → no match | conforms |
| `TYPO-02` | 5-char query, 1 typo → match | conforms |
| `TYPO-03` | 8-char query, 1 typo → match | conforms |
| `TYPO-04` | 8-char query, 2 typos → no match | conforms |
| `TYPO-05` | 9-char query, 2 typos → match | conforms |
| `TYPO-06` | first-char typo at 5 chars costs 2 → no match | conforms |
| `TYPO-07` | first-char typo at 9 chars costs 2 → match | conforms |
| `TYPO-08` | `twoTypos = 255` accepted | conforms |
| `TYPO-09` | `twoTypos = 256` rejected | conforms (`invalid_settings_typo_tolerance`) |
| `TYPO-10` | `oneTypo = 9 > twoTypos = 5` rejected | conforms |

The documented typo model held exactly at every boundary, including the counter-intuitive
first-character rule. **Nothing to report.**

### Filter semantics — 12 checks, 12 matched

Oracle: `/docs/learn/filtering_and_sorting/filter_expression_reference`

The strongest claim here was worth the campaign on its own:

> The inequality operator (`!=`) returns all documents not selected by the equality operator.

Against a 10-document fixture spanning `"action"`, `"ACTION"`, `"drama"`, `null`, `""`, `[]`, `{}`,
an absent attribute, and `["action","adventure"]`: `cat = action` → `[1,3,9]`, `cat != action` →
`[2,4,5,6,7,8,10]`. The union is all 10 documents, the intersection is empty. `!=` **is** the exact
complement, including for the `null`, empty and missing-attribute documents — which is where this
kind of engine usually leaks. Confirmed conforming.

Also confirmed: undeclared attribute refused with `invalid_search_filter` (400); `=`/`!=`
case-insensitive; `=` reaching into arrays; `=` returning nothing for `null` and `[]`;
`EXISTS` counting `null`/`""`/`[]`/`{}` as existing; `IS EMPTY` matching exactly `""`, `[]`, `{}`
and *not* `null`; `IS NULL` matching exactly the `null` document; `TO` ≡ `>= AND <=`; `AND` binding
tighter than `OR`; `IN` ≡ a disjunction of equalities.

**Nothing to report.**

### `rankingScoreThreshold` — 7 checks, 7 matched

Oracle: `/docs/reference/api/search`

> Exclude from the results any document whose ranking score is below this value (between 0.0 and 1.0).
> Excluded hits do not count toward `estimatedTotalHits`, `totalHits`, or facet distribution.

Probed with a self-calibrating threshold taken from the observed score distribution rather than a
guessed constant. `hits`, `estimatedTotalHits` **and** `totalHits` all honoured the threshold.
Range boundaries `0.0` and `1.0` accepted; `1.1` and `-0.1` refused with
`invalid_search_ranking_score_threshold`.

This is worth stating explicitly because it is the *same* metadata-counting contract that Finding A
below violates — here it is honoured. **Nothing to report.**

### Faceting `maxValuesPerFacet` — 3 checks, 3 matched

Oracle: `/docs/reference/api/settings` — `default: 100`, `minimum: 0`.

With 150 distinct facet values indexed, the default returns exactly 100. `maxValuesPerFacet: 0` is
accepted (HTTP 202) and yields 0 facet values, honouring the documented `minimum: 0`.
**Nothing to report** — but see Finding B, which contrasts with this.

### Pagination — 13 checks, 10 matched, **3 deviations**

Oracle: `/docs/reference/api/search`, `/docs/reference/api/settings`, `/docs/guides/front_end/pagination`.

Conforming: `limit` default 20; `offset` default 0; `limit: 1000` → 1000 hits; `limit: 1001` →
silently clamped to 1000 (consistent with *"By default this endpoint returns at most 1000 results"*);
`offset: 995` → 5 hits, `offset: 999` → 1 hit, `offset: 1000` → 0 hits; `page: 11` past the cap →
0 hits; `page: 0` → 0 hits; `page`/`hitsPerPage` taking precedence over `offset`/`limit`; raising
`maxTotalHits` to 1200 immediately raising the ceiling to 1200 hits.

The three deviations follow.

---

## Deviations

### Finding A — `totalHits` / `totalPages` / `estimatedTotalHits` ignore `pagination.maxTotalHits`

**Status: CONFIRMED AND REPRODUCIBLE — but ALREADY REPORTED UPSTREAM. Not a new finding.**

Checks `PAG-07`, `PAG-08`.

**Promise.** `/docs/reference/api/settings`, on `pagination.maxTotalHits`:

> Maximum number of search results Meilisearch can return. Limit and offset cannot go beyond this value.

`/docs/guides/front_end/pagination` then makes the operational contract explicit:

> `totalHits` contains the exhaustive number of results for that query, and `totalPages` contains
> the exhaustive number of pages of search results for the same query.

> The `totalPages` field included in the response contains the exhaustive count of search result
> pages based on your query's `hitsPerPage`. **Use this to create a numbered list of pages.**

That same guide's own sample code builds the page selector with `for (let i = 0; i < totalPages; i += 1)`
and disables "next" with `results.page === results.totalPages`.

**Observed.** The `hits` array is correctly capped; the metadata is not. Following the guide's own
recommended code therefore renders page buttons that lead to empty pages.

**Reproduction** (fresh index, 3 documents, `maxTotalHits = 2`):

```bash
curl -X POST -H "$K" -H "$J" -d '{"uid":"repro","primaryKey":"id"}'   $U/indexes
curl -X POST -H "$K" -H "$J" -d '[{"id":1},{"id":2},{"id":3}]'        $U/indexes/repro/documents
curl -X PATCH -H "$K" -H "$J" -d '{"maxTotalHits":2}'                 $U/indexes/repro/settings/pagination

curl -X POST -H "$K" -H "$J" -d '{"q":"","page":1,"hitsPerPage":1}'   $U/indexes/repro/search
# observed: "totalPages":3,"totalHits":3      expected per doc: 2 and 2
curl -X POST -H "$K" -H "$J" -d '{"q":"","page":3,"hitsPerPage":1}'   $U/indexes/repro/search
# observed: "hits":[]                          -- the 3rd page it just advertised is empty

curl -X POST -H "$K" -H "$J" -d '{"q":""}'                            $U/indexes/repro/search
# observed: "hits":[{"id":1},{"id":2}]  (capped, correct)  "estimatedTotalHits":3  (uncapped)
```

At the campaign's own scale — 1200 documents, default `maxTotalHits: 1000`, `hitsPerPage: 10` —
the response advertises `totalPages: 120` while pages 101–120 all return `hits: []`.

**Prior art — this is the reason it is not reportable.**

- [meilisearch/meilisearch#6482](https://github.com/meilisearch/meilisearch/issues/6482) —
  ``​`totalHits` and `totalPages` ignore `pagination.maxTotalHits` with page-based pagination`` —
  **open**, labelled `bug`, filed 2026-06-30. Its reproduction is 3 documents with
  `maxTotalHits = 2`; identical to the one above, arrived at independently. It identifies the
  change as a regression between v1.46.0 and v1.48.3.
- [meilisearch/meilisearch#6496](https://github.com/meilisearch/meilisearch/pull/6496) —
  *Respect pagination.maxTotalHits in total hits metadata*, **open** PR filed 2026-07-06,
  `Fixes #6482`. It also covers the `estimatedTotalHits` half (`PAG-07`), attributing the
  divergence to single-index searches now routing through the federated search path.

**The only thing this campaign adds** is that the defect is still present in **v1.53.0**
(2026-08-10) — i.e. the fix has not shipped 5 weeks after the PR was opened. That is worth at most
a one-line "still reproduces in v1.53.0" comment on #6482, not a new issue.

### Finding B — `pagination.maxTotalHits` documents `minimum: 0` but rejects `0`

**Status: CONFIRMED AND REPRODUCIBLE, no prior art found. Documentation defect, low severity.**

Check `PAG-13`.

**Promise.** The published API reference schema for `PaginationSettings.maxTotalHits` declares:

```yaml
maxTotalHits:
  type: [integer, 'null']
  description: Maximum number of search results Meilisearch can return. Limit and offset cannot go beyond this value.
  default: 1000
  example: 1000
  minimum: 0
```

`minimum: 0` states that `0` is a legal value.

**Observed.** The server refuses `0`, and its error message states a *different* range than the one
documented — a non-zero lower bound, and an upper bound of `18446744073709551615` (u64 max) that
the documentation never mentions:

```bash
$ curl -X PATCH -H "$K" -H "$J" -d '{"maxTotalHits":0}' $U/indexes/repro/settings/pagination
{"message":"Invalid value at `.maxTotalHits`: a non-zero integer value lower than
 `18446744073709551615` was expected, but found a zero",
 "code":"invalid_settings_pagination","type":"invalid_request"}
HTTP 400
```

So the documented domain is `[0, ∞)` while the accepted domain is `[1, 2^64-1]`. Both bounds are
mis-documented; the lower one is a hard 400.

**Why this is a real inconsistency and not pedantry.** `faceting.maxValuesPerFacet` carries the
*identical* documented lower bound `minimum: 0` in the same reference document — and it **accepts**
`0` (HTTP 202, and 0 facet values are then returned; checks `FACET-02`/`FACET-03`). Two settings,
one documented contract, two behaviours. A client generated from this OpenAPI schema would consider
`0` valid for both.

**Prior art searched and not found.** `repo:meilisearch/meilisearch maxTotalHits zero` → 2 unrelated
hits. `repo:meilisearch/documentation maxTotalHits` → 13 hits, all closed and all about the
*performance* warnings on raising the value, none about the lower bound or the schema range.

**Honest severity assessment.** Nobody sets `maxTotalHits: 0` on purpose. The impact is confined to
generated clients and schema-driven validation. This is a documentation/schema fix, not a product
bug — and it belongs to `meilisearch/documentation` (or whatever generates the OpenAPI), not to the
engine.

---

## Non-deviations worth recording

Things that looked like deviations during the run and were **not**:

| Apparent finding | Resolution |
|---|---|
| `limit: 1001` accepted with HTTP 200 although the doc says *"The value cannot exceed the index maxTotalHits setting"* | Not a defect. It silently clamps to 1000, which satisfies the operative promise *"returns at most 1000 results"*. The reference sentence is loose prose about the effective ceiling, not a claimed validation rule. |
| `page: 0` returns HTTP 200 with 0 hits although `page` is documented *"1-indexed"* | Not a defect. The schema explicitly declares `minimum: 0`, so `0` is in-domain, and an empty page is a coherent answer for a page that cannot exist. |
| First deliberate run: `TYPO-07` reported 2 hits instead of 1 | **My own fixture bug**, not Meilisearch's. The two 9-character fixtures (`fantimexo`, `jantimexo`) differed only in their first character, so a single first-char-typo query legitimately matched both. Fixed to `jorbanexo`; the check then passed. Recorded here because it is exactly the class of error the campaign discipline exists to catch. |
| First deliberate run: `PAG-13` reported 20 hits with `maxTotalHits: 0` | **My own probe bug.** The whole-settings `PATCH` returned 400, and my `settle()` helper returned early on a body with no `taskUid`, so the failure was swallowed and the setting silently stayed at 1000. Rewritten against the dedicated `/settings/pagination` sub-route so the HTTP status is checked directly — which is what turned a phantom into Finding B. |

## Searched and not found

- **No deviation in typo tolerance.** All four documented thresholds (4/5, 8/9, the first-character
  double cost, and the `0 ≤ oneTypo ≤ twoTypos ≤ 255` setting range) held at the value and at the
  value ±1.
- **No leak in `!=`.** The documented complement property held over `null`, `""`, `[]`, `{}` and
  absent attributes — the specific place I expected to find one.
- **No deviation in `IS NULL` / `IS EMPTY` / `EXISTS`** against the exact JSON-value lists the doc
  enumerates, including the doc's explicit statement that `null` is not empty.
- **No deviation in operator precedence or in the `TO` / `IN` equivalences.**
- **No metadata-counting bug for `rankingScoreThreshold`**, despite it being the same contract that
  Finding A violates, and despite closed issue #5274 (*Total Hits is wrong when there is
  rankingScoreThreshold*) showing the area has a history.
- **Not probed** (out of the campaign's time box, no conclusion either way): `matchingStrategy`
  `last`/`all`/`frequency` term-dropping order; ranking-rules ordering and custom rule sets;
  `searchableAttributes` ordering effects on relevancy; `sortableAttributes`; `distinct`;
  `attributesToSearchOn`; geo search; multi-search / federated search; the whole AI/vector surface.

## Verdict

**One report is worth making, and it is a comment, not an issue:** confirm on
[#6482](https://github.com/meilisearch/meilisearch/issues/6482) that the defect still reproduces on
v1.53.0, since PR #6496 has been open for five weeks. Anything more would be duplicate noise.

Finding B is genuine and unreported but is a schema/doc inconsistency of very low impact; it is
worth a documentation issue only if raised without ceremony.

**Zero new product defects established — and that is the honest result.** The documented semantics
of Meilisearch's search, filtering and typo engine held at every boundary this campaign could
derive from the prose. The single real behavioural gap found was one the project had already found
itself.
