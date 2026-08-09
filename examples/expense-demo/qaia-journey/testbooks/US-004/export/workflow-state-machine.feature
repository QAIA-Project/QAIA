# Feature: report lifecycle state machine (AC1, AC7). Preconditions declarative — data
# seeding is the automation layer's concern (T3/T4).
Feature: Expense report lifecycle

  Background:
    Given the ExpenseFlow SUT is reset to its seed state
    And "employee@demo" is an employee whose direct manager is "manager@demo"

  @QAIA-US-004-001 @AC1 @AC2 @AC8 @P1 @smoke @use-case
  # journey: end-to-end happy path across the full chain up to first approval
  Scenario: End-to-end journey — draft to first approval on a small report
    Given "employee@demo" has a draft report with one EUR line "taxi" of 40.00 dated today, receipt attached
    When "employee@demo" submits the report
    Then the report is "submitted" awaiting "manager" approval
    And when "manager@demo" approves it the report becomes "approved"

  @QAIA-US-004-002 @AC1 @P2 @ep
  # condition: AC1-C1 — priority P2 (foundational, simple)
  Scenario: A complete draft is submitted successfully
    Given "employee@demo" has a draft report with one EUR line "meal" of 20.00 dated today, receipt attached
    When "employee@demo" submits the report
    Then the report status is "submitted"

  @QAIA-US-004-003 @AC1 @P2 @state-transition
  # condition: AC1-C2 — priority P2 (re-entrant loop)
  Scenario: A changes-requested report returns to draft
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" requests changes on report "R" with comment "please add a receipt scan"
    Then report "R" status is "draft"

  @QAIA-US-004-004 @AC1 @P2 @state-transition
  # condition: AC1-C3 — priority P2
  Scenario: A changes-requested-turned-draft report is edited and re-submitted
    Given report "R" was returned to draft via changes-requested with comment "please add a receipt scan"
    When "employee@demo" edits report "R" to add a receipt and re-submits it
    Then report "R" status is "submitted"

  @QAIA-US-004-005 @AC1 @P2 @negative @state-transition
  # condition: AC1-C4 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 409
  Scenario: Submitting an already-submitted report is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "employee@demo" attempts to submit report "R" again
    Then the attempt is refused

  @QAIA-US-004-006 @AC1 @P2 @negative @state-transition
  # condition: AC1-C5 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 409
  Scenario: Editing a submitted (non-draft) report is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "employee@demo" attempts to edit report "R"
    Then the attempt is refused

  @QAIA-US-004-007 @AC1 @AC7 @P1 @negative @state-transition @low-confidence
  # condition: AC1-C6 [req-neg] — priority P1 — open: Q3 (reject only from `submitted`, — Q10: the AC states refusal, not a status; SUT answers 409
  # not from a `changes-requested`-turned-`draft` report; safe default per the standard
  # state-machine convention that undeclared transitions are forbidden)
  Scenario: A draft reached via changes-requested cannot be rejected directly
    Given report "R" was returned to draft via changes-requested with comment "please add a receipt scan"
    When "manager@demo" attempts to reject report "R" with comment "not acceptable at all"
    Then the attempt is refused

  @QAIA-US-004-028 @AC7 @P2 @negative @state-transition
  # condition: AC7-C1 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 409
  Scenario: A rejected report cannot be edited
    Given a report "R" by "employee@demo" that was rejected by its manager with comment "not a business expense"
    When "employee@demo" attempts to edit report "R"
    Then the attempt is refused

  @QAIA-US-004-029 @AC7 @P2 @negative @state-transition
  # condition: AC7-C2 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 409
  Scenario: A rejected report cannot be re-submitted
    Given a report "R" by "employee@demo" that was rejected by its manager with comment "not a business expense"
    When "employee@demo" attempts to submit report "R"
    Then the attempt is refused
