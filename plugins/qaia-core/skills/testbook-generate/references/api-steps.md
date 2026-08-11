# The shape of an `@api` scenario

A scenario tagged `@api` ([ADR 0008](https://github.com/QAIA-Project/QAIA/blob/main/docs/adr/0008-test-level-is-a-design-property.md)) verifies a clause of the service contract, observable
in HTTP without a browser. This file gives its **shape**, to copy.

It is a shape and not a description on purpose. The emission contract of `SKILL.md` records the
measurement behind that choice: given a rule in prose, one model out of four indented one level
short throughout; given the shape, models copied it. **Prose describing a form gets interpreted;
a form gets copied.**

## The shape

```
  # AC2 — POST /appointments, operation createAppointment
  @QAIA-US-001-014 @AC2 @P1 @api @boundary
  Scenario: A slot booked at exactly the opening minute is created
    # contract: createAppointment · requestBody.slotId · responses.201
    Given an authenticated patient
    And slot "S1" opens at 09:00
    When they POST /appointments with slotId "S1" and startTime "09:00"
    Then the response status is 201
    And the response body carries the created appointment id
    And the Location header points at the created appointment
```

Five rules, all visible above:

1. **One `When`, and it is the request.** Method and path, literal. Never "the client calls the
   API" — a step that does not name the operation cannot be automated without guessing.
2. **`Given` is declarative state, never a warm-up request.** "Given an authenticated patient",
   not "Given the client POSTs /login". Seeding belongs to the automation layer; the same rule as
   everywhere else in the book, and the reason generated tests can run standalone.
3. **The first `Then` is the status.** Always. It is the one assertion every API contract makes,
   and the one whose absence makes a test pass on a 500.
4. **Then the body, then the headers** — in that order, one claim per step, and **only what the
   contract states**. A field the spec never declares is not asserted; if it matters, it is an
   open question, not a silent expectation.
5. **The `# contract:` comment cites the clause**, not just the AC — operation, then the exact
   spec element the scenario rests on (`requestBody.required`, `responses.404`, `security`,
   `parameters.limit.maximum`). This is what makes the chain *spec clause → condition → scenario →
   test → result* traceable end to end; the `@AC<n>` tag alone stops one link short.

## Refusal paths — the reason the level tag matters at all

```
  @QAIA-US-001-019 @AC2 @P1 @api @negative @ep
  Scenario Outline: Omitting a required field is refused
    # contract: createAppointment · requestBody.required → responses.400
    Given an authenticated patient
    When they POST /appointments with "<field>" omitted
    Then the response status is 400
    And the response body names the missing field

    Examples:
      | field     |
      | slotId    |
      | patientId |
```

A `[req-neg]` condition carrying `[level: api]` is **discharged only by an `@api` scenario**. A UI
scenario showing an error message does not verify the contract's 400: the promise was made in
HTTP, and nothing checked it there. This is the third consequence listed in ADR 0008's context,
and the one that made a gate read green over a promise nobody had verified.

## What an `@api` scenario must not do

- **Assert a status the specification never declares.** `openapi-ingest` derives conditions from
  the declared `responses`; a scenario expecting a 409 that appears nowhere in the spec is an
  invention. If the refusal path is real but undeclared, that is contradiction class 3 of
  `openapi-ingest` — an open question, tagged `@low-confidence` with its `# open: Qn`.
- **Describe a screen.** "Then the error message is displayed" in an `@api` scenario is the
  disagreement `automate` is required to report rather than route around. Fix the level or fix the
  step; do not ship both readings.
- **Chain two requests to reach one assertion.** Two requests means either a declarative `Given`
  is missing, or the scenario is verifying two promises — the atomicity rule already forbids the
  second.
- **Assert on timing.** Latency budgets belong to `perf-check`, which has the instrument for them.
  A `Then the response is fast` is unfalsifiable.

## Where the level comes from

Not from this file, and not from the wording of the steps: `istqb-design` assigned it to the
**condition**, with its justification, in `03-design.md`. This document only says what the
scenario looks like once that decision has been made.
