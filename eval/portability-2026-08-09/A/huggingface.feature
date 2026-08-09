# US-004 Expense Report Workflow
Feature: US-004 Expense Report Workflow

  # US-004 AC1-C1
  @QAIA-US-004-001 @AC1 @P2 @state-transition
  Scenario: draft to submitted succeeds with valid data
    Given a draft expense report with valid data
    When the report is submitted
    Then the report transitions to submitted state

  # US-004 AC1-C2
  @QAIA-US-004-002 @AC1 @P2 @state-transition
  Scenario: changes-requested to draft re‑enters edit mode
    Given a submitted expense report that is marked changes‑requested
    When the report is returned to draft
    Then the report returns to draft state and is editable again

  # US-004 AC1-C3
  @QAIA-US-004-003 @AC1 @P2 @state-transition
  Scenario: edited draft after changes‑requested is resubmitted successfully
    Given a draft expense report that was previously changes‑requested
    When the report is edited and submitted
    Then the report transitions to submitted state

  # US-004 AC1-C4
  @QAIA-US-004-004 @AC1 @P2 @state-transition @negative
  Scenario: submitting a non‑draft report is refused
    Given an expense report that is not in draft state
    When the report is submitted
    Then the submission is refused

  # US-004 AC1-C5
  @QAIA-US-004-005 @AC1 @P2 @state-transition @negative
  Scenario: editing a non‑draft report is refused
    Given an expense report that is not in draft state
    When an attempt is made to edit the report
    Then the edit operation is refused

  # US-004 AC1-C6
  @QAIA-US-004-006 @AC1 @P1 @state-transition @negative @low-confidence
  # open: Q3
  Scenario: rejecting a draft report is refused
    Given a draft expense report (including one reached via changes‑requested)
    When an attempt is made to reject the report
    Then the rejection is refused

  # US-004 AC2-C1
  @QAIA-US-004-007 @AC2 @P1 @boundary
  Scenario: total just under €500 requires one manager approval
    Given an expense report with a total of €499.99
    When the report is submitted for approval
    Then exactly one approval (manager) is required

  # US-004 AC2-C2
  @QAIA-US-004-008 @AC2 @P1 @boundary @low-confidence
  # open: Q1
  Scenario: total exactly €500 requires manager and finance approvals
    Given an expense report with a total of €500.00
    When the report is submitted for approval
    Then two approvals (manager and finance) are required

  # US-004 AC2-C3
  @QAIA-US-004-009 @AC2 @P1 @boundary @low-confidence
  # open: Q1
  Scenario: total exactly €5000 requires manager and finance approvals
    Given an expense report with a total of €5000.00
    When the report is submitted for approval
    Then two approvals (manager and finance) are required

  # US-004 AC2-C4
  @QAIA-US-004-010 @AC2 @P1 @boundary
  Scenario: total just above €5000 requires three approvals and reaches approved state
    Given an expense report with a total of €5000.01
    When the report is submitted for approval
    Then three approvals (manager, finance, director) are required and the report reaches approved state

  # US-004 AC2-C5
  @QAIA-US-004-011 @AC2 @P1 @decision-table @negative
  Scenario: out‑of‑order approver is refused
    Given an expense report awaiting approval and an approver whose role is not the next expected role
    When the out‑of‑order approver attempts to approve
    Then the approval attempt is refused

  # US-004 AC3-C1
  @QAIA-US-004-012 @AC3 @P1 @decision-table @negative
  Scenario: self‑approval is refused
    Given an expense report and an approver who is also the submitter
    When the approver attempts to decide on the report
    Then the decision is refused

  # US-004 AC3-C2
  @QAIA-US-004-013 @AC3 @P1 @decision-table @low-confidence
  # open: Q2
  Scenario: manager submits <€500 report, finance escalates
    Given a manager submits an expense report with total less than €500
    When the approval chain is processed
    Then the finance approver replaces the manager step

  # US-004 AC3-C3
  @QAIA-US-004-014 @AC3 @P1 @decision-table @low-confidence
  # open: Q2
  Scenario: manager submits >€5000 report, manager step is dropped
    Given a manager submits an expense report with total greater than €5000
    When the approval chain is processed
    Then the manager step is omitted, leaving finance and director approvals

  # US-004 AC3-C4
  @QAIA-US-004-015 @AC3 @P1 @decision-table @low-confidence
  # open: Q8
  Scenario: finance user submits report requiring finance’s own sign‑off
    Given a finance user submits an expense report where finance approval is required
    When the approval chain is processed
    Then the finance step is replaced by director approval (or dropped if director already required)

  # US-004 AC4-C1
  @QAIA-US-004-016 @AC4 @P3 @ep @negative
  Scenario: missing line fields are refused at submission
    Given an expense report line missing category, amount, or date
    When the report is submitted
    Then the submission is refused

  # US-004 AC4-C2
  @QAIA-US-004-017 @AC4 @P2 @boundary @low-confidence
  # open: Q5
  Scenario: line dated exactly 90 days ago is accepted
    Given an expense report line dated exactly 90 days before today
    When the report is submitted
    Then the line is accepted

  # US-004 AC4-C3
  @QAIA-US-004-018 @AC4 @P2 @boundary @negative
  Scenario: line dated 91 days ago is blocked at submission
    Given an expense report line dated 91 days before today
    When the report is submitted
    Then the submission is refused with an explanatory message

  # US-004 AC5-C1
  @QAIA-US-004-019 @AC5 @P2 @boundary
  Scenario: line just under €25 threshold without receipt is accepted
    Given an expense report line with amount just below the €25 threshold and no receipt
    When the report is submitted
    Then the line is accepted

  # US-004 AC5-C2
  @QAIA-US-004-020 @AC5 @P1 @boundary @negative
  Scenario: line at exactly €25 threshold without receipt is refused
    Given an expense report line with amount exactly €25 and no receipt
    When the report is submitted
    Then the submission is refused

  # US-004 AC5-C3
  @QAIA-US-004-021 @AC5 @P3 @boundary
  Scenario: line ≥ €25 with receipt is accepted
    Given an expense report line with amount at least €25 and a receipt attached
    When the report is submitted
    Then the line is accepted

  # US-004 AC5-C4
  @QAIA-US-004-022 @AC5 @P1 @boundary @negative @low-confidence
  # open: Q6
  Scenario: non‑EUR line with EUR‑equivalent ≥ €25 without receipt is refused
    Given a non‑EUR expense report line whose EUR‑equivalent amount is €25 or more, without a receipt
    When the report is submitted
    Then the submission is refused

  # US-004 AC6-C1
  @QAIA-US-004-023 @AC6 @P1 @ep
  Scenario: correct currency conversion drives amount band
    Given a non‑EUR expense report with a convertible total
    When the total is converted to EUR
    Then the converted total determines the approval band

  # US-004 AC6-C2
  @QAIA-US-004-024 @AC6 @P1 @error-guessing @negative @low-confidence
  # open: Q4
  Scenario: missing conversion rate is refused at submission
    Given a currency/date pair for which no conversion rate can be resolved
    When the expense report is submitted
    Then the submission is refused with an explanatory message

  # US-004 AC6-C3
  @QAIA-US-004-025 @AC6 @P1 @error-guessing @low-confidence
  # open: Q4
  Scenario: weekend/holiday rate fallback is used and flagged as rateStale
    Given a non‑EUR expense dated on a weekend or holiday with no exact‑date rate
    When the conversion uses the last available prior rate
    Then the report is accepted and flagged as rateStale

  # US-004 AC6-C4
  @QAIA-US-004-026 @AC6 @P1 @decision-table @low-confidence
  # open: Q7
  Scenario: stale fallback rate near boundary still drives band and escalation
    Given a manager‑submitted foreign‑currency report converted via a stale rate that lands near a band boundary
    When the report is processed for approval
    Then the appropriate band is selected and the escalation rules are applied based on the flagged total

  # US-004 AC7-C1
  @QAIA-US-004-027 @AC7 @P2 @state-transition @negative
  Scenario: editing a rejected report is refused
    Given a rejected expense report
    When an attempt is made to edit the report
    Then the edit operation is refused

  # US-004 AC7-C2
  @QAIA-US-004-028 @AC7 @P2 @state-transition @negative
  Scenario: re‑submitting a rejected report is refused
    Given a rejected expense report
    When an attempt is made to re‑submit the report
    Then the submission is refused

  # US-004 AC8-C1
  @QAIA-US-004-029 @AC8 @P2 @boundary @negative
  Scenario: rejecting without a comment or with <10‑char comment is refused
    Given a rejection attempt with no comment or a comment shorter than ten characters
    When the report is rejected
    Then the rejection is refused

  # US-004 AC8-C2
  @QAIA-US-004-030 @AC8 @P2 @boundary @negative
  Scenario: requesting changes without a comment or with <10‑char comment is refused
    Given a changes‑request attempt with no comment or a comment shorter than ten characters
    When changes are requested
    Then the request is refused

  # US-004 AC8-C3
  @QAIA-US-004-031 @AC8 @P2 @boundary
  Scenario: comment of exactly 10 characters is accepted
    Given a comment exactly ten characters long accompanying a rejection or changes‑request
    When the action is performed
    Then the comment is accepted

  # US-004 AC8-C4
  @QAIA-US-004-032 @AC8 @P3 @ep
  Scenario: approving a report does not require a comment
    Given an expense report pending approval
    When the report is approved
    Then the approval succeeds without a comment

  # US-004 AC8-C5
  @QAIA-US-004-033 @AC8 @P1 @error-guessing
  Scenario: every transition is recorded in the audit trail
    Given any transition event (create, submit, approve, reject, changes‑requested) on an expense report
    When the event occurs
    Then the audit trail records who performed the transition and when

  # US-004 AC-auth-C1
  @QAIA-US-004-034 @AC-auth @P2 @error-guessing @negative
  Scenario: creating a report without authentication is refused
    Given an unauthenticated user attempts to create an expense report
    When the creation request is received
    Then the request is refused with a 401 response

  # US-004 AC-auth-C2
  @QAIA-US-004-035 @AC-auth @P2 @error-guessing @negative
  Scenario: deciding on a report without authentication is refused
    Given an unauthenticated user attempts to decide on an expense report
    When the decision request is received
    Then the request is refused with a 401 response

  # US-004 AC-auth-C3
  @QAIA-US-004-036 @AC-auth @P1 @error-guessing @negative @low-confidence
  # open: Q8
  Scenario: editing another employee's draft is refused without revealing existence
    Given an employee attempts to edit another employee's draft expense report
    When the edit request is processed
    Then the request is refused with a 404 response

  # US-004 AC-list-C1
  @QAIA-US-004-037 @AC-list @P3 @ep
  Scenario: employee with no reports sees an empty list
    Given an employee who has no expense reports
    When the employee views the "My reports" list
    Then the list is empty

  # Journey end‑to‑end scenario
  @QAIA-US-004-038 @smoke
  Scenario: complete expense report lifecycle from creation to approval
    Given an authenticated employee creates a draft expense report with valid data
    When the employee submits the report
    And the required approvals are performed in order
    And the report is approved
    Then the report reaches the approved state and all transitions are recorded in the audit trail
