# TaskAPI — fixture SUT for `contract-probe` validation

A deliberately tiny app (self-hosted, no external deps) whose **documented contract** below is
the target of the `contract-probe` skill's proof run. One defect is injected on purpose (see
`server.js`'s comment) — this file is the "README/help text" the skill reads to know what's
promised, exactly the input the real skill's step 1 (extract the contract) would read from a
real target app.

## What this API promises

1. `POST /tasks` with a JSON body `{ "title": "..." }` creates a task and returns it with a
   positive integer `id` and the `title` trimmed of leading/trailing whitespace.
2. `GET /tasks/:id` returns the task if it exists, or **HTTP 404** if it does not — for *any*
   input in the `:id` position, malformed or not. It never returns a 5xx.
3. `POST /tasks` with a missing or empty `title` is refused with **HTTP 422**, never accepted
   as a task with an empty title.

## Run it

```
node server.js   # http://localhost:4600
```
