Feature: Expense Report Lifecycle and Approval

  # AC1 — Core state transitions
  @QAIA-US-004-001 @AC1 @P2 @state-transition
  Scenario: Submit a valid draft report
    Given a report in state 'draft' with valid data
    When the submitter submits the report
    Then the report state becomes 'submitted'

  @QAIA-US-004-002 @AC1 @P2 @state-transition
  Scenario: Request changes to a submitted report and return to draft
    Given a report in state 'submitted'
    When an approver requests changes
    Then the report state becomes 'changes-requested'
    And the report is editable again

  @QAIA-US-004-003 @AC1 @P2 @state-transition
  Scenario: Edit and re-submit a report after changes-requested
    Given a report in state 'changes-requested'
    When the submitter edits the report and submits again
    Then the report state becomes 'submitted'

  @QAIA-US-004-004 @AC1 @P2 @state-transition @negative
  Scenario: Refuse submission when report is not in draft
    Given a report in state 'submitted'
    When the submitter attempts to submit the report
    Then the submission is refused with an error message

  @QAIA-US-004-005 @AC1 @P2 @state-transition @negative
  Scenario: Refuse editing when report is not in draft
    Given a report in state 'submitted'
    When the submitter attempts to edit the report
    Then the edit is refused with an error message

  @QAIA-US-004-006 @AC1 @P1 @state-transition @negative @low-confidence(Q3)
  Scenario: Refuse rejection when report is in draft
    Given a report in state 'draft'
    When an approver attempts to reject the report
    Then the rejection is refused with an error message

  # AC2 — Approval chain by amount (boundary + decision table)
  @QAIA-US-004-007 @AC2 @P1 @boundary
  Scenario: Approve a report under €500 with exactly one approval
    Given a report with total €499.99
    When the manager approves the report
    Then the report state becomes 'approved'

  @QAIA-US-004-008 @AC2 @P1 @boundary @negative @low-confidence(Q1)
  Scenario: Refuse approval at exactly €500.00 when only one approver is required
    Given a report with total €500.00
    When the manager attempts to approve the report
    Then the approval is refused with an error message

  @QAIA-US-004-009 @AC2 @P1 @boundary @negative @low-confidence(Q1)
  Scenario: Refuse approval at exactly €5000.00 when only two approvers are required
    Given a report with total €5000.00
    When the finance approver attempts to approve the report
    Then the approval is refused with an error message

  @QAIA-US-004-010 @AC2 @P1 @boundary
  Scenario: Approve a report above €5000 with three required approvals
    Given a report with total €5000.01
    When the manager approves the report
    Then the report state becomes 'approved'
    When the finance approver approves the report
    Then the report state becomes 'approved'
    When the director approves the report
    Then the report state becomes 'approved'

  @QAIA-US-004-011 @AC2 @P1 @decision-table @negative
  Scenario: Refuse out-of-order approval attempt
    Given a report requiring manager then finance approval
    When the finance approver attempts to approve before the manager
    Then the approval is refused with an error message

  # AC3 — Self-approval and skip-level escalation (decision table)
  @QAIA-US-004-012 @AC3 @P1 @decision-table @negative
  Scenario: Refuse self-approval attempt
    Given a report submitted by the current user
    When the submitter attempts to approve their own report
    Then the approval is refused with an error message

  @QAIA-US-004-013 @AC3 @P1 @decision-table @low-confidence(Q2)
  Scenario: Escalate manager step to finance for reports under €500
    Given a report with total €499.99 submitted by a manager
    When the manager attempts to approve
    Then the manager step is skipped and finance becomes the required approver

  @QAIA-US-004-014 @AC3 @P1 @decision-table @low-confidence(Q2)
  Scenario: Drop manager step for reports over €5000 when manager is submitter
    Given a report with total €5000.01 submitted by a manager
    When the manager attempts to approve
    Then the manager step is skipped and finance and director remain required

  @QAIA-US-004-015 @AC3 @P1 @decision-table @low-confidence(Q8)
  Scenario: Generalize skip/escalate rule for finance submitter
    Given a report requiring finance approval submitted by a finance user
    When the finance user attempts to approve
    Then the finance step is skipped and director becomes the required approver

  # AC4 — Line completeness and age boundary
  @QAIA-US-004-016 @AC4 @P3 @ep @negative
  Scenario: Refuse submission when line is missing category, amount, or date
    Given a report with a line missing category
    When the submitter attempts to submit the report
    Then the submission is refused with an error message
    Given a report with a line missing amount
    When the submitter attempts to submit the report
    Then the submission is refused with an error message
    Given a report with a line missing date
    When the submitter attempts to submit the report
    Then the submission is refused with an error message

  @QAIA-US-004-017 @AC4 @P2 @boundary @low-confidence(Q5)
  Scenario: Accept a line dated exactly 90 days ago
    Given a report with a line dated exactly 90 days ago
    When the submitter submits the report
    Then the report is accepted

  @QAIA-US-004-018 @AC4 @P2 @boundary @negative
  Scenario: Refuse a line dated 91 days ago
    Given a report with a line dated 91 days ago
    When the submitter attempts to submit the report
    Then the submission is refused with an explanatory message

  # AC5 — Receipt threshold boundary
  @QAIA-US-004-019 @AC5 @P2 @boundary
  Scenario: Accept a line just under €25 threshold without receipt
    Given a report with a line of €24.99 and no receipt
    When the submitter submits the report
    Then the report is accepted

  @QAIA-US-004-020 @AC5 @P1 @boundary @negative
  Scenario: Refuse a line at exactly €25 threshold without receipt
    Given a report with a line of €25.00 and no receipt
    When the submitter attempts to submit the report
    Then the submission is refused with an error message

  @QAIA-US-004-021 @AC5 @P3 @ep
  Scenario: Accept a line with receipt attached
    Given a report with a line of €30.00 and a receipt attached
    When the submitter submits the report
    Then the report is accepted

  @QAIA-US-004-022 @AC5 @P1 @boundary @negative @low-confidence(Q6)
  Scenario: Refuse non-EUR line under face-value threshold when EUR-equivalent ≥ €25
    Given a report with a line of 24.99 USD whose EUR-equivalent is €25.01 and no receipt
    When the submitter attempts to submit the report
    Then the submission is refused with an error message

  # AC6 — Currency conversion and rate handling
  @QAIA-US-004-023 @AC6 @P1 @ep
  Scenario: Convert non-EUR report total correctly to EUR for approval band
    Given a report with total 100 GBP
    And the EUR conversion rate is 1.20
    When the report is submitted
    Then the converted total is €120.00
    And the approval chain uses the €120.00 band

  @QAIA-US-004-024 @AC6 @P1 @error-guessing @negative @low-confidence(Q4)
  Scenario: Refuse submission when currency/date has no resolvable rate
    Given a report with a line in currency X on date Y with no available rate
    When the submitter attempts to submit the report
    Then the submission is refused with an explanatory message

  @QAIA-US-004-025 @AC6 @P1 @error-guessing @low-confidence(Q4)
  Scenario: Accept expense dated in weekend/holiday gap using last available prior rate
    Given a report with a line dated on a weekend
    And the last available rate prior to the weekend is 1.15
    When the report is submitted
    Then the report is accepted with flag 'rateStale'
    And the converted total uses the 1.15 rate

  @QAIA-US-004-026 @AC6 @P1 @decision-table @low-confidence(Q7)
  Scenario: Use stale fallback rate for band boundary and escalation decisions
    Given a manager-submitted foreign-currency report with converted total €5000.01 using a stale rate
    And the stale rate flag is set
    When the report is submitted
    Then the approval chain uses the €5000.01 band
    And the manager step is skipped due to the escalation rule

  # AC7 — Terminal state enforcement
  @QAIA-US-004-027 @AC7 @P2 @state-transition @negative
  Scenario: Refuse editing a rejected report
    Given a report in state 'rejected'
    When the submitter attempts to edit the report
    Then the edit is refused with an error message

  @QAIA-US-004-028 @AC7 @P2 @state-transition @negative
  Scenario: Refuse re-submission of a rejected report
    Given a report in state 'rejected'
    When the submitter attempts to submit the report
    Then the submission is refused with an error message

  # AC8 — Audit trail completeness
  @QAIA-US-004-029 @AC8 @P2 @boundary @negative
  Scenario: Refuse rejection without a comment or with comment under 10 characters
    Given a report in state 'submitted'
    When an approver attempts to reject without a comment
    Then the rejection is refused with an error message
    Given a report in state 'submitted'
    When an approver attempts to reject with a 9-character comment
    Then the rejection is refused with an error message

  @QAIA-US-004-030 @AC8 @P2 @boundary
  Scenario: Accept rejection with exactly 10-character comment
    Given a report in state 'submitted'
    When an approver rejects with a 10-character comment
    Then the report state becomes 'rejected'
    And the comment is recorded

  @QAIA-US-004-031 @AC8 @P3 @ep
  Scenario: Approve a report without a comment
    Given a report in state 'submitted'
    When an approver approves without a comment
    Then the report state becomes 'approved'

  @QAIA-US-004-032 @AC8 @P1 @error-guessing
  Scenario: Record audit trail for every transition
    Given a report in state 'draft'
    When the submitter submits the report
    Then the audit trail records 'submit' by the submitter at timestamp T1
    When an approver requests changes
    Then the audit trail records 'changes-requested' by the approver at timestamp T2
    When the submitter edits and submits again
    Then the audit trail records 'submit' by the submitter at timestamp T3
    When the manager approves
    Then the audit trail records 'approve' by the manager at timestamp T4
    When the report is rejected
    Then the audit trail records 'reject' by the approver at timestamp T5

  # AC-auth — Authorization and IDOR enforcement
  @QAIA-US-004-033 @AC-auth @P2 @error-guessing @negative
  Scenario: Refuse report creation without authentication
    Given no authenticated session
    When an anonymous user attempts to create a report
    Then the creation is refused with 401

  @QAIA-US-004-033 @AC-auth @P2 @error-guessing @negative
  Scenario: Refuse decision on a report without authentication
    Given a report in state 'submitted'
    When an unauthenticated user attempts to approve the report
    Then the decision is refused with 401

  @QAIA-US-004-034 @AC-auth @P1 @error-guessing @negative
  Scenario: Refuse edit of another employee's draft report without disclosure
    Given an authenticated employee attempting to edit another employee's draft report
    When the employee attempts to edit the report
    Then the edit is refused with 404 (not 403)

  # AC-list — List view
  @QAIA-US-004-035 @AC-list @P3 @ep
  Scenario: Show explicit empty state when employee has no reports
    Given an employee with no reports
    When the employee views "My reports"
    Then the UI displays "No reports found"
