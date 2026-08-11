## Summary

For a record whose **multiple relation is empty**, `?!=` matches it and `?!~` does not — although the docs describe both operators with the same "any / at least one of" wording. Whatever the intended semantics, the two cannot both be right.

## Steps to reproduce

Version: **0.39.10** (`pocketbase_0.39.10_windows_amd64`), fresh `pb_data`, single process.

Two collections: `repro_cats` (field `name`) and `repro_posts` with a **multiple** relation `cats` → `repro_cats`. Three posts:

| Post | `cats` |
|---|---|
| `A_has_news` | one category named `news` |
| `B_has_tech` | one category named `tech` |
| `C_has_NOTHING` | **empty** |

```
GET /api/collections/repro_posts/records?filter=cats.name ?=  "news"   -> A
GET /api/collections/repro_posts/records?filter=cats.name ?!= "news"   -> B, C_has_NOTHING
GET /api/collections/repro_posts/records?filter=cats.name ?~  "news"   -> A
GET /api/collections/repro_posts/records?filter=cats.name ?!~ "news"   -> B
```

`?!=` returns the record with no related rows at all; `?!~` does not.

## Why this is a report and not a preference

The docs give both operators the same shape of description:

> `?!=` — Any/At least one of NOT equal
> `?!~` — Any/At least one of NOT Like/Contains

Two readings are possible, and **neither makes both results correct**:

- *"at least one related row satisfies the negated comparison"* → a record with **zero** related rows satisfies neither, so both should exclude `C_has_NOTHING`. `?!=` disagrees.
- *"`!=` is the boolean complement of `=`"* (the reading in #7193, where an empty relation behaves as a zero value `''`) → then `'' != 'news'` **and** `'' NOT LIKE '%news%'` are both true, so both should include `C_has_NOTHING`. `?!~` disagrees.

So one of the two is unintended, and only you can say which. If the answer is "`?!=` is right and `?!~` is the bug", or the reverse, the useful outcome may simply be a sentence in the docs — today nothing there lets a user predict the difference.

## Practical consequence

The natural way to write "posts not in the `news` category" is `cats.name ?!= "news"`, and it silently includes every post with **no category at all**. Used in an API rule, that widens access beyond what the author intended.

## Prior art I checked before filing

#6647 (closed — JSON field without `:each`, a different question), #7193 (empty relation as zero value — states the model but not this asymmetry), #2444, #7474. Discussions searched as well. None describes `?!=` and `?!~` disagreeing.

Reproduced on four independent fixtures, and on a second instance started on another port from the same `pb_data`.

<sub>Found while using PocketBase as a target for an open-source QA tooling project: conditions were derived from the prose of pocketbase.io/docs and the source was never read to write them. Everything ran locally on `127.0.0.1`. For what it's worth in the other direction — the API-rule status codes, `expand` depth limit, `skipTotal`, header normalisation and all 16 filter operators matched the documentation exactly.</sub>
