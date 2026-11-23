# Contract source — json-server (alpha v1) on http://localhost:3010

Source: `README.target.md` (local copy, the target's only documentation). Captured 2026-11-23.
Authorization: case (a) — self-hosted, local, disposable instance owned by the operator (as stated in the task brief).

Every checkable promise below is quoted verbatim with its README section and line number.
Vague/non-checkable or out-of-scope items are listed at the end.

| ID | Section (line) | Verbatim quote | Checkable promise |
|---|---|---|---|
| P01 | Routes (103) | `GET    /posts` | Collection list route exists |
| P02 | Routes (104) | `GET    /posts/:id` | Item route exists |
| P03 | Routes (105) | `POST   /posts` | Create route exists |
| P04 | Routes (106) | `PUT    /posts/:id` | Replace route exists |
| P05 | Routes (107) | `PATCH  /posts/:id` | Partial-update route exists |
| P06 | Routes (108) | `DELETE /posts/:id` | Delete route exists |
| P07 | Routes (110) | `# Same for comments` | P01–P06 also hold for `/comments` |
| P08 | Routes (114) | `GET   /profile` | Singular resource read |
| P09 | Routes (115) | `PUT   /profile` | Singular resource replace |
| P10 | Routes (116) | `PATCH /profile` | Singular resource partial update |
| P11 | Usage (69-73) | `$ curl http://localhost:3000/posts/1` → `{ "id": "1", "title": "a title" }` | GET item returns the stored record (example abbreviated: omits `views`) |
| P12 | Params > Conditions (123) | `` ` ` → `==` `` | `field=v` filters equality |
| P13 | Params > Conditions (124) | `` `lt` → `<` `` | `field_lt=v` |
| P14 | Params > Conditions (125) | `` `lte` → `<=` `` | `field_lte=v` |
| P15 | Params > Conditions (126) | `` `gt` → `>` `` | `field_gt=v` |
| P16 | Params > Conditions (127) | `` `gte` → `>=` `` | `field_gte=v` |
| P17 | Params > Conditions (128) | `` `ne` → `!=` `` | `field_ne=v` |
| P18 | Params > Conditions (131) | `GET /posts?views_gt=9000` | Example query works |
| P19 | Params > Range (136-142) | `` `start` `` `` `end` `` `` `limit` `` ; `GET /posts?_start=10&_end=20` | `_start`/`_end` slice |
| P20 | Params > Range (142) | `GET /posts?_start=10&_limit=10` | `_start`/`_limit` slice |
| P21 | Params > Paginate (147-151) | `` `page` `` ; `` `per_page` (default = 10) `` ; `GET /posts?_page=1&_per_page=25` | Pagination, default page size 10 |
| P22 | Params > Sort (156-159) | `` `_sort=f1,f2` `` ; `GET /posts?_sort=id,-views` | Multi-field sort, `-` = descending |
| P23 | Params > Nested and array fields (164-168) | `` `x.y.z...` `` ; `GET /foo?a.b=bar` | Dotted path filtering |
| P24 | Params > Nested and array fields (169) | `GET /foo?x.y_lt=100` | Operators on nested fields |
| P25 | Params > Nested and array fields (165, 170) | `` `x.y.z[i]...` `` ; `GET /foo?arr[0]=bar` | Array index filtering |
| P26 | Embed (176) | `GET /posts?_embed=comments` | Embed children (one-to-many) |
| P27 | Embed (177) | `GET /comments?_embed=post` | Embed parent (many-to-one) |
| P28 | Delete (183) | `DELETE /posts/1` | Plain delete |
| P29 | Delete (184) | `DELETE /posts/1?_dependent=comments` | Delete option `_dependent` (documented as a distinct request from plain delete; no prose describes its effect — semantics inferred from the name) |
| P30 | Notable differences (200) | `` `id` is always a string and will be generated for you if missing `` | id type invariant + id generation |
| P31 | Notable differences (201) | `` use `_per_page` with `_page` instead of `_limit`for pagination `` | Pagination via `_page`+`_per_page` |

Not extracted as checkable / out of scope:
- Static files (`./public`, `-s/--static`, lines 189-195): CLI startup options; the running instance's launch flags are not ours to change and no `public` directory content is documented. Not probed.
- `json-server --help`, install, JSON5 input format, sponsorship/licence, `--delay` removal (line 202): not HTTP-observable contract of this instance.
