# Feature: US-004 - Expense Report Submission and Approval Workflow
Feature: Expense Report Submission and Approval Workflow

  # AC1-C1
  @QAIA-US-004-001 @AC1 @P2 @ep
  Scenario: Submit a draft expense report with valid data
    Given an employee has an expense report in "draft" status with valid details
    When the employee submits the expense report
    Then the expense report status changes to "submitted"

  # AC1-C2
  @QAIA-US-004-002 @AC1 @P2 @state-transition
  Scenario: Transition a submitted report to changes requested and back to draft
    Given an expense report in "submitted" status
    When the manager requests changes on the expense report with a valid comment
    Then the expense report status becomes "draft" and is editable again

  # AC1-C3
  @QAIA-US-004-003 @AC1 @P2 @state-transition
  Scenario: Re-submit an edited report previously in changes requested status
    Given an expense report in "draft" status updated after changes were requested
    When the employee submits the expense report
    Then the expense report status changes to "submitted"

  # AC1-C4
  @QAIA-US-004-004 @AC1 @P2 @negative @state-transition
  Scenario: Attempt to submit an expense report that is not in draft status
    Given an expense report currently in "submitted" status
    When the employee attempts to submit the expense report
    Then the submission is refused with an error indicating the report is not in draft status

  # AC1-C5
  @QAIA-US-004-005 @AC1 @P2 @negative @state-transition
  Scenario: Attempt to edit an expense report that is not in draft status
    Given an expense report currently in "submitted" status
    When the employee attempts to modify an expense line on the report
    Then the modification is refused with an error indicating the report is locked

  # AC1-C6 - open: Q3
  @QAIA-US-004-006 @AC1 @P1 @negative @low-confidence @state-transition
  Scenario: Rejecting a draft report directly is refused
    Given an expense report currently in "draft" status
    When an approver attempts to reject the expense report
    Then the rejection is refused because only submitted reports accept approval decisions

  # AC2-C1
  @QAIA-US-004-007 @AC2 @P1 @boundary
  Scenario: Report total under 500 EUR requires only manager approval
    Given an expense report submitted with a total of 499.99 EUR
    When the approval chain is generated
    Then the approval chain requires exactly 1 approval from the manager

  # AC2-C2 - open: Q1
  @QAIA-US-004-008 @AC2 @P1 @low-confidence @boundary
  Scenario: Report total of exactly 500 EUR requires manager and finance approval
    Given an expense report submitted with a total of 500.00 EUR
    When the approval chain is generated
    Then the approval chain requires 2 approvals from the manager and finance

  # AC2-C3 - open: Q1
  @QAIA-US-004-009 @AC2 @P1 @low-confidence @boundary
  Scenario: Report total of exactly 5000 EUR requires manager and finance approval
    Given an expense report submitted with a total of 5000.00 EUR
    When the approval chain is generated
    Then the approval chain requires 2 approvals from the manager and finance

  # AC2-C4
  @QAIA-US-004-010 @AC2 @P1 @boundary
  Scenario: Report total over 5000 EUR requires manager, finance, and director approval
    Given an expense report submitted with a total of 5000.01 EUR
    When all required roles manager, finance, and director approve in sequence
    Then the expense report status becomes "approved"

  # AC2-C5
  @QAIA-US-004-011 @AC2 @P1 @negative @decision-table
  Scenario: Out-of-order approval attempt by non-expected role is refused
    Given an expense report in "submitted" status awaiting manager approval in a multi-level chain
    When a finance user attempts to approve the report before the manager
    Then the approval decision is refused as out of order

  # AC3-C1
  @QAIA-US-004-012 @AC3 @P1 @negative @decision-table
  Scenario: Approver attempting to decide on their own expense report is refused
    Given a manager who submitted their own expense report
    When the manager attempts to approve their own expense report
    Then the decision is refused due to self-approval prohibition

  # AC3-C2 - open: Q2
  @QAIA-US-004-013 @AC3 @P1 @low-confidence @decision-table
  Scenario: Manager submits report under 500 EUR with step escalated to finance
    Given a manager submits an expense report with a total of 300.00 EUR
    When the approval chain is generated
    Then the manager step is replaced by finance escalation requiring sign-off from finance

  # AC3-C3 - open: Q2
  @QAIA-US-004-014 @AC3 @P1 @low-confidence @decision-table
  Scenario: Manager submits report over 5000 EUR dropping manager step
    Given a manager submits an expense report with a total of 6000.00 EUR
    When the approval chain is generated
    Then the manager step is dropped leaving finance and director in the approval chain

  # AC3-C4 - open: Q8
  @QAIA-US-004-015 @AC3 @P1 @low-confidence @decision-table
  Scenario: Finance user submits report requiring finance approval with step escalated
    Given a finance user submits an expense report requiring finance sign-off
    When the approval chain is generated
    Then the finance step is escalated to director to eliminate self-approval

  # AC4-C1
  @QAIA-US-004-016 @AC4 @P3 @negative @ep
  Scenario Outline: Submit expense report with incomplete line details is refused
    Given a draft expense report with a line having category "<category>", amount "<amount>", and date "<date>"
    When the employee attempts to submit the expense report
    Then the submission is refused due to missing mandatory line fields

    Examples:
      | category | amount | date       |
      |          | 50.00  | 2026-07-01 |
      | Meals    |        | 2026-07-01 |
      | Meals    | 50.00  |            |

  # AC4-C2 - open: Q5
  @QAIA-US-004-017 @AC4 @P2 @low-confidence @boundary
  Scenario: Expense line dated exactly 90 days ago is accepted
    Given a draft expense report containing a line dated exactly 90 days prior to server date
    When the employee submits the expense report
    Then the submission succeeds and the expense report status becomes "submitted"

  # AC4-C3
  @QAIA-US-004-018 @AC4 @P2 @negative @boundary
  Scenario: Expense line dated 91 days ago is blocked at submission
    Given a draft expense report containing a line dated 91 days prior to server date
    When the employee attempts to submit the expense report
    Then the submission is blocked with an error message stating expenses older than 90 days are not allowed

  # AC5-C1
  @QAIA-US-004-019 @AC5 @P2 @boundary
  Scenario: Expense line under 25 EUR equivalent without receipt is accepted
    Given a draft expense report with a line amounting to 24.99 EUR and no receipt attached
    When the employee submits the expense report
    Then the submission succeeds

  # AC5-C2
  @QAIA-US-004-020 @AC5 @P1 @negative @boundary
  Scenario: Expense line of exactly 25 EUR equivalent without receipt is refused
    Given a draft expense report with a line amounting to 25.00 EUR and no receipt attached
    When the employee attempts to submit the expense report
    Then the submission is refused with an error requiring a receipt for expenses of 25 EUR or more

  # AC5-C3
  @QAIA-US-004-021 @AC5 @P3 @ep
  Scenario: Expense line of 25 EUR or more with receipt attached is accepted
    Given a draft expense report with a line amounting to 50.00 EUR and a valid receipt attached
    When the employee submits the expense report
    Then the submission succeeds

  # AC5-C4 - open: Q6
  @QAIA-US-004-022 @AC5 @P1 @negative @low-confidence @boundary
  Scenario: Foreign currency expense line reaching 25 EUR equivalent without receipt is refused
    Given a draft expense report with a USD line of face value 22.00 USD converting to 25.50 EUR and no receipt
    When the employee attempts to submit the expense report
    Then the submission is refused because the converted EUR value equals or exceeds 25 EUR threshold

  # AC6-C1
  @QAIA-US-004-023 @AC6 @P1 @ep
  Scenario: Foreign currency total drives approval band after conversion
    Given a draft expense report with lines in USD converting to a total of 600.00 EUR
    When the employee submits the expense report
    Then the total is converted to 600.00 EUR and requires manager and finance approvals

  # AC6-C2 - open: Q4
  @QAIA-US-004-024 @AC6 @P1 @negative @low-confidence @error-guessing
  Scenario: Submission with unresolvable exchange rate is refused
    Given a draft expense report with an expense line in an unknown currency with no available exchange rate
    When the employee attempts to submit the expense report
    Then the submission is refused with an error message stating currency conversion rate is unavailable

  # AC6-C3 - open: Q4
  @QAIA-US-004-025 @AC6 @P1 @low-confidence @error-guessing
  Scenario: Expense dated on weekend uses last available exchange rate and sets stale flag
    Given a draft foreign currency expense dated on a Sunday with no exchange rate published for that date
    When the employee submits the expense report
    Then the system converts the amount using Friday exchange rate and marks the report with rateStale flag

  # AC6-C4 - open: Q7
  @QAIA-US-004-026 @AC6 @P1 @low-confidence @decision-table
  Scenario: Manager foreign currency report converted via stale rate drives band and self approval rules
    Given a manager submits a foreign currency report converted via stale rate landing at 510.00 EUR
    When the approval chain is generated
    Then the approval chain is evaluated on 510.00 EUR total and manager self-approval step is escalated to finance

  # AC7-C1
  @QAIA-US-004-027 @AC7 @P2 @negative @state-transition
  Scenario: Attempting to edit a rejected expense report is refused
    Given an expense report in "rejected" status
    When an employee attempts to edit the expense report details
    Then the modification is refused because rejected reports cannot be edited

  # AC7-C2
  @QAIA-US-004-028 @AC7 @P2 @negative @state-transition
  Scenario: Attempting to resubmit a rejected expense report is refused
    Given an expense report in "rejected" status
    When an employee attempts to submit the expense report
    Then the submission is refused because rejected reports cannot be resubmitted

  # AC8-C1
  @QAIA-US-004-029 @AC8 @P2 @negative @boundary
  Scenario Outline: Rejecting an expense report with missing or short comment is refused
    Given an expense report in "submitted" status
    When an approver attempts to reject the expense report with comment "<comment>"
    Then the rejection is refused requiring a comment of at least 10 characters

    Examples:
      | comment   |
      |           |
      | Too high  |

  # AC8-C2
  @QAIA-US-004-030 @AC8 @P2 @negative @boundary
  Scenario: Requesting changes with comment shorter than 10 characters is refused
    Given an expense report in "submitted" status
    When an approver attempts to request changes with comment "Fix this"
    Then the action is refused requiring a comment of at least 10 characters

  # AC8-C3
  @QAIA-US-004-031 @AC8 @P2 @boundary
  Scenario: Requesting changes with exactly 10 characters comment is accepted
    Given an expense report in "submitted" status
    When an approver requests changes with comment "1234567890"
    Then the request is accepted and status changes to "draft"

  # AC8-C4
  @QAIA-US-004-032 @AC8 @P3 @ep
  Scenario: Approving an expense report without a comment succeeds
    Given an expense report in "submitted" status
    When an authorized approver approves the expense report without providing a comment
    Then the expense report approval succeeds

  # AC8-C5
  @QAIA-US-004-033 @AC8 @P1 @error-guessing
  Scenario: Audit trail records actor and timestamp for all workflow transitions
    Given an expense report undergoing creation, submission, and approval decisions
    When workflow actions occur on the expense report
    Then every transition is recorded in the audit trail with the actor identity and timestamp

  # AC-auth-C1
  @QAIA-US-004-034 @AC-auth @P2 @negative @error-guessing
  Scenario: Creating an expense report without authentication is refused
    Given an unauthenticated user request to create an expense report
    When the create expense report endpoint is invoked
    Then the request is refused with HTTP status 401 Unauthorized

  # AC-auth-C2
  @QAIA-US-004-035 @AC-auth @P2 @negative @error-guessing
  Scenario: Deciding on an expense report without authentication is refused
    Given an unauthenticated user request to approve an expense report
    When the approval endpoint is invoked
    Then the request is refused with HTTP status 401 Unauthorized

  # AC-auth-C3
  @QAIA-US-004-036 @AC-auth @P1 @negative @error-guessing
  Scenario: Employee attempting to edit another employee draft report returns 404
    Given an employee authenticated as User A
    When User A attempts to edit a draft expense report belonging to User B
    Then the request returns HTTP status 404 Not Found without disclosing report existence

  # AC-list-C1
  @QAIA-US-004-037 @AC-list @P3 @ep
  Scenario: Employee with no expense reports sees empty state
    Given an employee who has created zero expense reports
    When the employee views the "My reports" list
    Then an explicit empty state message is displayed
