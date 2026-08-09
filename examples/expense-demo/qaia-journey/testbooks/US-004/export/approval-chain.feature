# Feature: approval chain by amount band (AC2), self-approval / skip-level (AC3), and
# currency conversion feeding the chain (AC6). Boundaries and decision-table cells.
Feature: Approval chain routing

  Background:
    Given the ExpenseFlow SUT is reset to its seed state
    And the roles "manager" < "finance" < "director" form a fixed approval hierarchy

  @QAIA-US-004-008 @AC2 @P1 @boundary
  # condition: AC2-C1 — priority P1
  Scenario: A report just under €500 needs only the manager's approval
    Given a submitted report "R" by "employee@demo" totalling exactly 499.99 EUR
    Then report "R" awaits approval from "manager" only

  @QAIA-US-004-009 @AC2 @P1 @boundary @low-confidence
  # condition: AC2-C2 — priority P1 — open: Q1 (exact-€500 boundary — read as inclusive
  # in band B: manager then finance)
  Scenario: A report of exactly €500.00 needs manager then finance
    Given a submitted report "R" by "employee@demo" totalling exactly 500.00 EUR
    When "manager@demo" approves report "R"
    Then report "R" still awaits approval from "finance"

  @QAIA-US-004-010 @AC2 @P1 @boundary @low-confidence
  # condition: AC2-C3 — priority P1 — open: Q1 (exact-€5000 boundary — read as inclusive
  # in band B: manager then finance, no director)
  Scenario: A report of exactly €5000.00 still needs only manager then finance
    Given a submitted report "R" by "employee@demo" totalling exactly 5000.00 EUR
    When "manager@demo" approves report "R" and "finance@demo" approves report "R"
    Then report "R" status is "approved"

  @QAIA-US-004-011 @AC2 @P1 @boundary
  # condition: AC2-C4 — priority P1
  Scenario: A report just above €5000 needs manager, finance, then director
    Given a submitted report "R" by "employee@demo" totalling exactly 5000.01 EUR
    When "manager@demo" approves report "R" and "finance@demo" approves report "R" and "director@demo" approves report "R"
    Then report "R" status is "approved"

  @QAIA-US-004-012 @AC2 @P1 @negative @decision-table
  # condition: AC2-C5 [req-neg] — priority P1 — Q10: the AC states refusal, not a status; SUT answers 403
  Scenario: An approver acting out of chain order is refused
    Given a submitted report "R" by "employee@demo" totalling exactly 5000.01 EUR
    When "finance@demo" attempts to approve report "R" before the manager has
    Then the attempt is refused

  @QAIA-US-004-013 @AC3 @P1 @negative @decision-table
  # condition: AC3-C1 [req-neg] — priority P1 — Q10: the AC states refusal, not a status; SUT answers 403
  Scenario: An approver cannot decide on their own report
    Given a submitted report "R" by "manager@demo" totalling exactly 499.99 EUR
    When "manager@demo" attempts to approve report "R"
    Then the attempt is refused

  @QAIA-US-004-014 @AC3 @P1 @decision-table @low-confidence
  # condition: AC3-C2 — priority P1 — open: Q2 (a manager's own <€500 report escalates
  # straight to finance rather than being left with zero required approvers)
  Scenario: A manager's own small report escalates directly to finance
    Given a submitted report "R" by "manager@demo" totalling exactly 100.00 EUR
    Then report "R" awaits approval from "finance" only

  @QAIA-US-004-015 @AC3 @P1 @decision-table @low-confidence
  # condition: AC3-C3 — priority P1 — open: Q2 (a manager's own >€5000 report drops the
  # manager step; finance and director remain, in that order)
  Scenario: A manager's own large report skips the manager step but keeps finance and director
    Given a submitted report "R" by "manager@demo" totalling exactly 5000.01 EUR
    When "finance@demo" approves report "R"
    Then report "R" awaits approval from "director" only

  @QAIA-US-004-016 @AC3 @P1 @decision-table @low-confidence
  # condition: AC3-C4 — priority P1 — open: Q8 (the self-approval-skip rule generalizes
  # beyond the manager example: finance submitting a report requiring finance's own
  # sign-off escalates to director)
  Scenario: A finance user's own large report escalates the finance step to director
    Given a submitted report "R" by "finance@demo" totalling exactly 5000.01 EUR
    When "manager@demo" approves report "R"
    Then report "R" awaits approval from "director" only

  @QAIA-US-004-024 @AC6 @P1 @ep
  # condition: AC6-C1 — priority P1
  # rate-assumption: input chosen (543.00 USD) so its converted total crosses the 500 EUR
  # band threshold at a fixture rate of ~0.9210 — the rate itself is not sourced anywhere
  # in the US/design, so no converted-total figure is asserted below, only the band
  # behavior the AC actually requires (issue #46)
  Scenario: A non-EUR report's converted total drives the approval band
    Given "employee@demo" has a draft report in "USD" with one line "hotel" of 543.00 dated 2026-07-21, receipt attached
    When "employee@demo" submits the report
    Then the report awaits approval from "manager" and "finance"

  @QAIA-US-004-025 @AC6 @P1 @negative @error-guessing @low-confidence
  # condition: AC6-C2 [req-neg] — priority P1 — open: Q4 (rate source undefined; no — Q10: the AC states refusal, not a status; SUT answers 422
  # resolvable rate for an unsupported currency is refused at submission)
  Scenario: Submitting in a currency with no resolvable rate is refused
    Given "employee@demo" has a draft report in "CHF" with one line "hotel" of 100.00 dated 2026-07-21, receipt attached
    When "employee@demo" submits the report
    Then the attempt is refused

  @QAIA-US-004-026 @AC6 @P1 @error-guessing @low-confidence
  # condition: AC6-C3 — priority P1 — open: Q4 (fallback: an expense date in a
  # weekend/holiday gap uses the last available prior rate and is flagged stale)
  # rate-assumption: no converted-total figure is asserted — the fallback rate itself is
  # not sourced anywhere in the US/design, only the staleness flag the AC requires is a
  # grounded behavior (issue #46)
  Scenario: An expense dated in a weekend rate gap uses the last available rate
    Given "employee@demo" has a draft report in "USD" with one line "hotel" of 100.00 dated 2026-07-25, receipt attached
    When "employee@demo" submits the report
    Then the report is flagged as using a stale exchange rate

  @QAIA-US-004-027 @AC2 @AC3 @AC6 @P1 @decision-table @low-confidence
  # condition: AC6-C4 — priority P1 — open: Q7 (triple intersection AC2×AC3×AC6: a
  # manager's own foreign-currency report converted via a stale fallback rate still
  # drives both the band and the self-approval escalation from that flagged total)
  Scenario: A manager's stale-rate foreign report still drives band and escalation together
    Given "manager@demo" has a draft report in "USD" with one line "conference" of 550.00 dated 2026-07-25, receipt attached
    When "manager@demo" submits the report
    Then the report is flagged as using a stale exchange rate
    And the report awaits approval from "finance" only
