# Feature: line-item data-quality gates at submission (AC4 age, AC5 receipts).
Feature: Expense line item validation

  Background:
    Given the ExpenseFlow SUT is reset to its seed state
    And "employee@demo" is signed in

  @QAIA-US-004-017 @AC4 @P3 @negative @ep
  # condition: AC4-C1 [req-neg] — priority P3 — Q10: the AC states refusal, not a status; SUT answers 422
  Scenario: A line missing required fields is refused at submission
    Given "employee@demo" has a draft report with one incomplete line missing its category
    When "employee@demo" submits the report
    Then the attempt is refused

  @QAIA-US-004-018 @AC4 @P2 @boundary @low-confidence
  # condition: AC4-C2 — priority P2 — assumption: Q5 (90-day boundary measured against
  # the server/UTC clock; inclusive — exactly 90 days old is accepted)
  Scenario: A line dated exactly 90 days ago is accepted
    Given "employee@demo" has a draft report with one EUR line "supplies" of 10.00 dated exactly 90 days ago, receipt attached
    When "employee@demo" submits the report
    Then the report status is "submitted"

  @QAIA-US-004-019 @AC4 @P2 @negative @boundary
  # condition: AC4-C3 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 422
  Scenario: A line dated 91 days ago is blocked with an explanatory message
    Given "employee@demo" has a draft report with one EUR line "supplies" of 10.00 dated 91 days ago, receipt attached
    When "employee@demo" submits the report
    Then the attempt is refused and a message mentioning "90 days"

  @QAIA-US-004-020 @AC5 @P2 @boundary
  # condition: AC5-C1 — priority P2
  Scenario: A line just under the receipt threshold needs no receipt
    Given "employee@demo" has a draft report with one EUR line "coffee" of 24.99 dated today, no receipt attached
    When "employee@demo" submits the report
    Then the report status is "submitted"

  @QAIA-US-004-021 @AC5 @P1 @negative @boundary
  # condition: AC5-C2 [req-neg] — priority P1 — Q10: the AC states refusal, not a status; SUT answers 422
  Scenario: A line at exactly the receipt threshold without a receipt is refused
    Given "employee@demo" has a draft report with one EUR line "gear" of 25.00 dated today, no receipt attached
    When "employee@demo" submits the report
    Then the attempt is refused and a message mentioning "receipt"

  @QAIA-US-004-022 @AC5 @P3 @ep
  # condition: AC5-C3 — priority P3
  Scenario: A line at or above the receipt threshold with a receipt is accepted
    Given "employee@demo" has a draft report with one EUR line "gear" of 25.00 dated today, receipt attached
    When "employee@demo" submits the report
    Then the report status is "submitted"

  @QAIA-US-004-023 @AC5 @AC6 @P1 @negative @boundary @low-confidence
  # condition: AC5-C4 [req-neg] — priority P1 — open: Q6 (the receipt threshold is — Q10: the AC states refusal, not a status; SUT answers 422
  # compared on the EUR-converted amount, not the face value: a 30 USD line converts to
  # roughly 27.6 EUR and crosses the threshold even though its face value alone would not
  # obviously read as "≥ 25" to a naive currency-unaware check)
  Scenario: A non-EUR line whose EUR-equivalent crosses the receipt threshold is refused
    Given "employee@demo" has a draft report in "USD" with one line "gear" of 30.00 dated 2026-07-21, no receipt attached
    When "employee@demo" submits the report
    Then the attempt is refused and a message mentioning "receipt"
