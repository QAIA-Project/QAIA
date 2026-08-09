Feature: US-004 Report Management
  # Feature: US-004 Report Management

  # AC1 — state transition
  @QAIA-US-004-001 @AC1 @P2
  Scenario: Draft report is submitted successfully
    Given a report in draft state
    When the report is submitted
    Then the report is in submitted state

  # AC1 — state transition
  @QAIA-US-004-002 @AC1 @P2
  Scenario: Report is edited and re-submitted
    Given a report in submitted state
    When the report is edited and re-submitted
    Then the report is in submitted state

  # AC1 — state transition
  @QAIA-US-004-003 @AC1 @P2
  Scenario: Report is rejected
    Given a report in submitted state
    When the report is rejected
    Then the report is in rejected state

  # AC1 — state transition
  @QAIA-US-004-004 @AC1 @P2 @req-neg
  Scenario: Submitting a non-draft report is refused
    Given a report in submitted state
    When the report is submitted again
    Then the submission is refused

  # AC1 — state transition
  @QAIA-US-004-005 @AC1 @P2 @req-neg
  Scenario: Editing a non-draft report is refused
    Given a report in submitted state
    When the report is edited
    Then the edit is refused

  # AC1 — state transition
  @QAIA-US-004-006 @AC1 @P1 @req-neg
  Scenario: Rejecting a draft report is refused
    Given a report in draft state
    When the report is rejected
    Then the rejection is refused

  # AC2 — boundary / decision table
  @QAIA-US-004-007 @AC2 @P1
  Scenario: Report with total just under €500 requires one approval
    Given a report with total just under €500
    When the report is submitted
    Then the report requires one approval

  # AC2 — boundary / decision table
  @QAIA-US-004-008 @AC2 @P1 @req-neg-adjacent
  Scenario: Report with total exactly €500 requires two approvals
    Given a report with total exactly €500
    When the report is submitted
    Then the report requires two approvals

  # AC2 — boundary / decision table
  @QAIA-US-004-009 @AC2 @P1
  Scenario: Report with total exactly €5000 requires two approvals
    Given a report with total exactly €5000
    When the report is submitted
    Then the report requires two approvals

  # AC2 — boundary / decision table
  @QAIA-US-004-010 @AC2 @P1
  Scenario: Report with total just above €5000 requires three approvals
    Given a report with total just above €5000
    When the report is submitted
    Then the report requires three approvals

  # AC2 — boundary / decision table
  @QAIA-US-004-011 @AC2 @P1 @req-neg
  Scenario: Out-of-order approval is refused
    Given a report in submitted state
    When an out-of-order approval is attempted
    Then the approval is refused

  # AC3 — decision table
  @QAIA-US-004-012 @AC3 @P1 @req-neg
  Scenario: Self-approval is refused
    Given a report in submitted state
    When the submitter attempts to approve
    Then the approval is refused

  # AC3 — decision table
  @QAIA-US-004-013 @AC3 @P1
  Scenario: Escalation to finance for manager-submitted report
    Given a report submitted by a manager
    When the report is submitted
    Then the report is escalated to finance

  # AC3 — decision table
  @QAIA-US-004-014 @AC3 @P1
  Scenario: Escalation to director for manager-submitted report over €5000
    Given a report submitted by a manager with total over €5000
    When the report is submitted
    Then the report is escalated to director

  # AC4 — equivalence partitioning / boundary
  @QAIA-US-004-015 @AC4 @P2 @req-neg
  Scenario: Submitting a report with missing line items is refused
    Given a report with missing line items
    When the report is submitted
    Then the submission is refused

  # AC4 — equivalence partitioning / boundary
  @QAIA-US-004-016 @AC4 @P2
  Scenario: Report with line item dated exactly 90 days ago is accepted
    Given a report with a line item dated exactly 90 days ago
    When the report is submitted
    Then the report is accepted

  # AC4 — equivalence partitioning / boundary
  @QAIA-US-004-017 @AC4 @P2 @req-neg
  Scenario: Report with line item dated 91 days ago is refused
    Given a report with a line item dated 91 days ago
    When the report is submitted
    Then the report is refused

  # AC5 — boundary value analysis
  @QAIA-US-004-018 @AC5 @P2
  Scenario: Report with total just under €25 does not require a receipt
    Given a report with total just under €25
    When the report is submitted
    Then the report does not require a receipt

  # AC5 — boundary value analysis
  @QAIA-US-004-019 @AC5 @P1 @req-neg
  Scenario: Report with total exactly €25 requires a receipt
    Given a report with total exactly €25
    When the report is submitted
    Then the report requires a receipt

  # AC5 — boundary value analysis
  @QAIA-US-004-020 @AC5 @P3
  Scenario: Report with total over €25 and a receipt is accepted
    Given a report with total over €25 and a receipt
    When the report is submitted
    Then the report is accepted

  # AC5 — boundary value analysis
  @QAIA-US-004-021 @AC5 @P1 @req-neg
  Scenario: Report with total under €25 but over €25 in EUR-equivalent requires a receipt
    Given a report with total under €25 but over €25 in EUR-equivalent
    When the report is submitted
    Then the report requires a receipt

  # AC6 — equivalence partitioning / error guessing
  @QAIA-US-004-022 @AC6 @P1
  Scenario: Report with non-EUR total is converted correctly
    Given a report with non-EUR total
    When the report is submitted
    Then the report total is converted correctly

  # AC6 — equivalence partitioning / error guessing
  @QAIA-US-004-023 @AC6 @P1 @req-neg
  Scenario: Report with unknown currency is refused
    Given a report with unknown currency
    When the report is submitted
    Then the report is refused

  # AC6 — equivalence partitioning / error guessing
  @QAIA-US-004-024 @AC6 @P1
  Scenario: Report with stale rate is accepted with a warning
    Given a report with stale rate
    When the report is submitted
    Then the report is accepted with a warning

  # AC6 — equivalence partitioning / error guessing
  @QAIA-US-004-025 @AC6 @P1
  Scenario: Report with missing rate is accepted with a warning
    Given a report with missing rate
    When the report is submitted
    Then the report is accepted with a warning

  # AC7 — state transition
  @QAIA-US-004-026 @AC7 @P2 @req-neg
  Scenario: Rejecting a rejected report is refused
    Given a report in rejected state
    When the report is rejected again
    Then the rejection is refused

  # AC7 — state transition
  @QAIA-US-004-027 @AC7 @P2 @req-neg
  Scenario: Re-submitting a rejected report is refused
    Given a report in rejected state
    When the report is submitted again
    Then the submission is refused

  # AC8 — boundary / error guessing
  @QAIA-US-004-028 @AC8 @P2 @req-neg
  Scenario: Rejecting a report without a comment is refused
    Given a report in submitted state
    When the report is rejected without a comment
    Then the rejection is refused

  # AC8 — boundary / error guessing
  @QAIA-US-004-029 @AC8 @P2 @req-neg
  Scenario: Requesting changes without a comment is refused
    Given a report in submitted state
    When the changes are requested without a comment
    Then the request is refused

  # AC8 — boundary / error guessing
  @QAIA-US-004-030 @AC8 @P2
  Scenario: Comment with exactly 10 characters is accepted
    Given a report in submitted state
    When a comment with exactly 10 characters is added
    Then the comment is accepted

  # AC8 — boundary / error guessing
  @QAIA-US-004-031 @AC8 @P3
  Scenario: Approving a report does not require a comment
    Given a report in submitted state
    When the report is approved
    Then the approval is accepted

  # AC8 — boundary / error guessing
  @QAIA-US-004-032 @AC8 @P1
  Scenario: Every transition is recorded in the audit trail
    Given a report in submitted state
    When the report is transitioned
    Then the transition is recorded in the audit trail

  # AC-auth — authorization
  @QAIA-US-004-033 @AC-auth @P2 @req-neg
  Scenario: Creating a report without authentication is refused
    Given a report is created without authentication
    When the report is submitted
    Then the submission is refused

  # AC-auth — authorization
  @QAIA-US-004-034 @AC-auth @P2 @req-neg
  Scenario: Deciding on a report without authentication is refused
    Given a report in submitted state
    When a decision is made without authentication
    Then the decision is refused

  # AC-auth — authorization
  @QAIA-US-004-035 @AC-auth @P1 @req-neg
  Scenario: Editing another employee's draft is refused
    Given a report in draft state owned by another employee
    When the report is edited
    Then the edit is refused

  # AC-list — list view
  @QAIA-US-004-036 @AC-list @P3
  Scenario: An employee with no reports sees an empty state
    Given an employee with no reports
    When the employee views their reports
    Then the employee sees an empty state
