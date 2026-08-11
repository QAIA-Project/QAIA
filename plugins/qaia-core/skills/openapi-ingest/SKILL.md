---
name: openapi-ingest
description: Ingest an OpenAPI or Swagger specification as the requirement source and derive test conditions from it - equivalence partitions from enums, boundaries from schema constraints, refusal paths from required fields and declared error codes, and the contradictions the specification carries. Use when an API has a formal spec instead of a user story, before istqb-design and testbook-generate.
---

# openapi-ingest — the specification as requirement

`us-ingest` takes a user story written for humans. This skill takes the other common entry point:
a **formal, machine-readable specification**. Same chain afterwards — `istqb-design`,
`prioritize`, `testbook-generate` all work unchanged, because the output shape is the same.

## Why this entry point earns its place

The external campaign kept in `eval/external-application-2026-08-08/` found two real
defects in a 75,000-star project by generating **from its documentation and never from its code**.
The defect that mattered most was a one-character mismatch between what the documentation promised
and what the implementation read. A suite written by looking at the code cannot find that class of
defect: it copies the mistake.

Most real APIs carry something better than prose — a schema. Enums, `required`, `minLength`,
`maximum`, `pattern`, declared response codes: each is a promise stated precisely enough that a
test condition falls out of it without interpretation. That is the opposite of the ambiguity tax
paid on prose, and it is why this skill exists.

## The rule that makes it honest

**A specification is a promise, not a fact.** It describes what the API is supposed to do; it is
routinely out of date with what it does. Every condition derived here is of the form *"the spec
promises X"* — never *"the API does X"*. Confirming or refuting is `contract-probe`'s job, and
mixing the two is how a specification becomes a rubber stamp.

## What is derived, and from what

| Source in the spec | Derived | ISTQB technique |
|---|---|---|
| `enum` | one valid partition per value, **plus one value outside the enum** | equivalence partitioning |
| `required` (schema or parameter) | one refusal path per required field, omitted in turn | equivalence partitioning, invalid class |
| `minimum` / `maximum` / `minLength` / `maxLength` | the bound, and just outside it | boundary value analysis |
| `pattern`, `format` | one conforming, one not | equivalence partitioning |
| declared `responses` codes | one condition per declared code — **including the error codes** | specification-based |
| `security` on an operation | absent credential, invalid credential, insufficient scope | specification-based |
| `type` (integer, boolean…) | one wrong-type case | equivalence partitioning, invalid class |
| prose in `description` | **never a condition** — an open question (see below) |  |

## The four contradictions to look for, every time

A specification is written by hand and drifts against itself. These four are common enough to be
worth a systematic pass, and each is an **ambiguity to raise**, never a defect to file:

1. **A required parameter that carries a default.** If it is required, the default is unreachable;
   if the default applies, it is not required. The spec does not say which wins.
2. **The same field constrained in one place and not in another.** A property with an `enum` in a
   schema, and a same-named query parameter typed only as `string`.
3. **`security` declared with no failure code declared.** An operation that requires a credential
   but never states what happens without one leaves the whole refusal path unspecified — and the
   refusal path is where the interesting defects live.
4. **A constraint stated in prose but absent from the schema.** `description: "IDs above 1000 will
   generate errors"` with no `maximum: 1000`. Machines read the schema, so the constraint is not
   enforced by anything.

Each becomes `# open: Qn` in the test book, resolved by a human, exactly as with an ambiguous user
story. **Do not guess which reading is right** — a specification-derived book that quietly picks
one interpretation is worse than a prose-derived one, because its precision is misleading.

## Steps

1. **Freeze the spec.** Copy it into the run's `sources/` and record its sha256 in
   `REQUIREMENT-SOURCE.json`, **at the run root, in this shape** — the file is read by tooling,
   so its keys are not free:

   ```json
   {
     "testbook": "<path to the .feature this source produced>",
     "note": "<why this source is frozen>",
     "sources": [
       { "label": "<what it is, and when it was fetched>",
         "path": "sources/<file>",
         "origin": "<the URL it came from>",
         "sha256": "<hex>" }
     ]
   }
   ```

   *This shape is spelled out since 2026-08-11. It was previously left implicit, and an agent
   following this step faithfully invented its own keys — the schema existed only inside a
   checker's source code, which an installer never sees. A step that names an artifact owes its
   form.* A spec is a URL that changes without warning; a test book whose
   requirement cannot be re-read at the version it was generated from cannot be argued about later.
   `check_requirement_drift.py` then fails the day it moves.
2. **Inventory.** Count paths, operations, schemas, declared codes. This is what the coverage
   matrix will be measured against.
3. **Resolve `$ref`.** A condition that depends on an unresolved reference is not a condition.
4. **Derive**, per the table above, one operation at a time.
5. **Run the contradiction pass**, per the four above.
6. **Emit** the same structure `us-ingest` emits, so `istqb-design` and the rest need no change —
   plus the two things only this entry point can supply:

   - **`[level: api]` on every derived condition.** A clause of a service contract is observable
     in HTTP by construction, so the level is not a judgment call here the way it is on prose
     ([ADR 0008](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0008-test-level-is-a-design-property.md)). `istqb-design` may still *raise* a condition to `e2e` — a spec clause whose
     real promise is what the user sees — but it does so explicitly and with a reason, rather than
     inheriting a blank.
   - **The clause reference, not just the operation.** Each condition cites `<operationId> ·
     <spec element>` — `requestBody.required`, `responses.404`, `security`,
     `parameters.limit.maximum`. `testbook-generate` carries it into the scenario's `# contract:`
     comment (`testbook-generate/references/api-steps.md`), which is what makes the chain **spec
     clause → condition → scenario → test → result** traceable end to end. Citing only the
     operation stops one link short: it says *where* the promise lives, never *which* promise.

## What this skill must refuse

- **Turning prose in a `description` into an assertion.** It is a hint written for a human reader.
  It becomes an open question, not a test.
- **Deriving from an operation whose `$ref` does not resolve.**
- **Probing the live server.** This skill reads a document. It never sends a request — and never to
  a host the user does not own or has not explicitly authorised.
- **Treating `default:` as documentation of behaviour.** It documents what the *client library*
  sends, which is not what the server does when the field is absent.

## Applied for real

Applied to the Swagger Petstore specification (OpenAPI 3.0.4, version 1.0.27, 13 paths, 19
operations): `eval/openapi-ingest-2026-08-08/`. The derivation found **all four contradiction
classes present in that single spec** — including nine operations that declare a security scheme
while **no operation in the whole document declares a 401 or a 403**.

No request was sent to the Petstore server: it is not ours.
