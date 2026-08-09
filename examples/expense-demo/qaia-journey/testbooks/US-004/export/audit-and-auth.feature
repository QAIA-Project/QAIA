# Feature: audit trail and mandatory comments (AC8), plus cross-cutting authorization
# and IDOR conditions surfaced by the 3c systematic-expansion checklist (not literally
# named per-AC in the source, but a reflex expansion for any authenticated, multi-actor
# approval workflow). One list-view empty-state condition (AC-list-C1).
Feature: Audit trail, mandatory comments and access control

  Background:
    Given the ExpenseFlow SUT is reset to its seed state

  @QAIA-US-004-030 @AC8 @P2 @negative @boundary
  # condition: AC8-C1 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 422
  Scenario: Rejecting without a sufficient comment is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" attempts to reject report "R" with comment "too short"
    Then the attempt is refused

  @QAIA-US-004-031 @AC8 @P2 @negative @boundary
  # condition: AC8-C2 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 422
  Scenario: Requesting changes without a sufficient comment is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" attempts to request changes on report "R" with comment "too short"
    Then the attempt is refused

  @QAIA-US-004-032 @AC8 @P2 @boundary
  # condition: AC8-C3 — priority P2
  Scenario: A comment of exactly 10 characters is accepted
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" rejects report "R" with a comment of exactly 10 characters
    Then report "R" status is "rejected"

  @QAIA-US-004-033 @AC8 @P3 @ep
  # condition: AC8-C4 — priority P3
  Scenario: Approving a report does not require a comment
    Given a submitted report "R" by "employee@demo" totalling exactly 499.99 EUR
    When "manager@demo" approves report "R" without a comment
    Then report "R" status is "approved"

  @QAIA-US-004-034 @AC8 @P1 @error-guessing
  # condition: AC8-C5 — priority P1
  Scenario: Every transition is recorded in the audit trail with who and when
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" approves report "R"
    Then the audit trail contains a "submit" event by "employee@demo" and an "approve" event by "manager@demo", both timestamped

  @QAIA-US-004-035 @AC-auth @P2 @negative @error-guessing
  # condition: AC-auth-C1 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 401
  Scenario: Creating a report without authentication is refused
    When an unauthenticated request attempts to create a report
    Then the attempt is refused

  @QAIA-US-004-036 @AC-auth @P2 @negative @error-guessing
  # condition: AC-auth-C2 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 401
  Scenario: Deciding on a report without authentication is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When an unauthenticated request attempts to approve report "R"
    Then the attempt is refused

  @QAIA-US-004-037 @AC-auth @P1 @negative @error-guessing
  # condition: AC-auth-C3 [req-neg] — priority P1 — Q10: the AC states refusal, not a status; SUT answers 404
  Scenario: An employee cannot edit another employee's draft report
    Given "manager@demo" has a draft report of their own, "M"
    When "employee@demo" attempts to edit report "M"
    Then the attempt is refused

  @QAIA-US-004-038 @AC-list @P3 @ep
  # condition: AC-list-C1 — priority P3
  Scenario: An employee with no reports sees an empty "My reports" list
    Given "employee@demo" is signed in with no reports of their own
    When "employee@demo" views "My reports"
    Then the list is empty
