Feature: US-004 Expense Report Workflow

# US-004 - AC1 - AC1-C1
@QAIA-US-004-001 @AC1 @P2 @state-transition
Scenario: Draft to submitted succeeds with valid data
  Given a report in draft state with valid data
  When the report is submitted
  Then the submission succeeds

# US-004 - AC1 - AC1-C2
@QAIA-US-004-002 @AC1 @P2 @state-transition
Scenario: Submitted to changes-requested then back to draft
  Given a report in submitted state
  When a reviewer requests changes
  Then the report moves to changes-requested state

# US-004 - AC1 - AC1-C3
@QAIA-US-004-003 @AC1 @P2 @state-transition
Scenario: Draft edited after changes-requested and resubmitted successfully
  Given a report in draft state that was previously changes-requested
  When the report is edited and submitted
  Then the submission succeeds

# US-004 - AC1 - AC1-C4
@QAIA-US-004-004 @AC1 @P2 @state-transition @negative
Scenario: Submitting a report that is not in draft is refused
  Given a report in submitted state
  When the report is submitted again
  Then the submission is refused

# US-004 - AC1 - AC1-C5
@QAIA-US-004-005 @AC1 @P2 @state-transition @negative
Scenario: Editing a report that is not in draft is refused
  Given a report in submitted state
  When an edit is attempted on the report
  Then the edit is refused

# US-004 - AC1 - AC1-C6
# open: Q3
@QAIA-US-004-006 @AC1 @P1 @state-transition @negative @low-confidence
Scenario: Rejecting a report in draft state is refused
  Given a report in draft state
  When a reject action is performed on the report
  Then the rejection is refused

# US-004 - AC2 - AC2-C1
@QAIA-US-004-007 @AC2 @P1 @boundary
Scenario: Total just under €500 requires one manager approval
  Given a report with total €499.99
  When the report is submitted
  Then exactly one approval from a manager is required

# US-004 - AC2 - AC2-C2
# open: Q1
@QAIA-US-004-008 @AC2 @P1 @boundary @low-confidence
Scenario: Total exactly €500 requires manager and finance approvals
  Given a report with total €500.00
  When the report is submitted
  Then approvals from manager and finance are required

# US-004 - AC2 - AC2-C3
# open: Q1
@QAIA-US-004-009 @AC2 @P1 @boundary @low-confidence
Scenario: Total exactly €5000 requires manager and finance approvals
  Given a report with total €5000.00
  When the report is submitted
  Then approvals from manager and finance are required

# US-004 - AC2 - AC2-C4
@QAIA-US-004-010 @AC2 @P1 @boundary
Scenario: Total just above €5000 requires three approvals and ends approved
  Given a report with total €5000.01
  When the report is submitted
  Then approvals from manager, finance, and director are required and the report reaches approved state

# US-004 - AC2 - AC2-C5
@QAIA-US-004-011 @AC2 @P1 @decision-table @negative
Scenario: Out-of-order approver is refused
  Given a report awaiting manager approval
  When a finance approver attempts to approve before manager
  Then the approval attempt is refused

# US-004 - AC3 - AC3-C1
@QAIA-US-004-012 @AC3 @P1 @decision-table @negative
Scenario: Self-approval is refused
  Given a report submitted by a manager
  When the same manager attempts to approve the report
  Then the approval is refused

# US-004 - AC3 - AC3-C2
# open: Q2
@QAIA-US-004-013 @AC3 @P1 @decision-table @low-confidence
Scenario: Manager submits <€500 report, finance steps in
  Given a report with total €400 submitted by a manager
  When the report reaches the approval step
  Then the finance approver performs the approval instead of the manager

# US-004 - AC3 - AC3-C3
# open: Q2
@QAIA-US-004-014 @AC3 @P1 @decision-table @low-confidence
Scenario: Manager submits >€5000 report, manager step dropped
  Given a report with total €6000 submitted by a manager
  When the approval chain is evaluated
  Then the manager step is omitted and finance and director approve

# US-004 - AC3 - AC3-C4
# open: Q8
@QAIA-US-004-015 @AC3 @P1 @decision-table @low-confidence
Scenario: Finance user submits report requiring finance sign-off
  Given a report with total €2000 submitted by a finance user
  When the approval chain is evaluated
  Then the finance step is replaced by director approval, or omitted if director already required

# US-004 - AC4 - AC4-C1
@QAIA-US-004-016 @AC4 @P3 @ep @negative
Scenario: Missing mandatory line fields are refused
  Given a report line missing category, amount, or date
  When the line is submitted
  Then the submission is refused

# US-004 - AC4 - AC4-C2
# open: Q5
@QAIA-US-004-017 @AC4 @P2 @boundary @low-confidence
Scenario: Line dated exactly 90 days ago is accepted
  Given a report line dated exactly 90 days before today
  When the line is submitted
  Then the submission is accepted

# US-004 - AC4 - AC4-C3
@QAIA-US-004-018 @AC4 @P2 @boundary @negative
Scenario: Line dated 91 days ago is blocked
  Given a report line dated 91 days before today
  When the line is submitted
  Then the submission is refused with an explanatory message

# US-004 - AC5 - AC5-C1
@QAIA-US-004-019 @AC5 @P2 @boundary
Scenario: Line just under €25 threshold without receipt is accepted
  Given a report line with EUR-equivalent amount €24.99 and no receipt
  When the line is submitted
  Then the submission is accepted

# US-004 - AC5 - AC5-C2
@QAIA-US-004-020 @AC5 @P1 @boundary @negative
Scenario: Line at exactly €25 threshold without receipt is refused
  Given a report line with EUR-equivalent amount €25.00 and no receipt
  When the line is submitted
  Then the submission is refused

# US-004 - AC5 - AC5-C3
@QAIA-US-004-021 @AC5 @P3 @ep
Scenario: Line ≥ €25 with receipt is accepted
  Given a report line with EUR-equivalent amount €30.00 and a receipt attached
  When the line is submitted
  Then the submission is accepted

# US-004 - AC5 - AC5-C4
# open: Q6
@QAIA-US-004-022 @AC5 @P1 @boundary @negative @low-confidence
Scenario: Non‑EUR line with EUR‑equivalent ≥ €25 but no receipt is refused
  Given a non‑EUR report line whose face value converts to €25.00, without receipt
  When the line is submitted
  Then the submission is refused

# US-004 - AC6 - AC6-C1
@QAIA-US-004-023 @AC6 @P1 @ep
Scenario: Non‑EUR total converted correctly drives approval band
  Given a non‑EUR report with total converted to €750
  When the report is submitted
  Then the appropriate approval band (manager + finance) is applied

# US-004 - AC6 - AC6-C2
# open: Q4
@QAIA-US-004-024 @AC6 @P1 @error-guessing @negative @low-confidence
Scenario: Submission with missing currency rate is refused
  Given a report with a currency/date pair for which no conversion rate exists
  When the report is submitted
  Then the submission is refused with an explanatory message

# US-004 - AC6 - AC6-C3
# open: Q4
@QAIA-US-004-025 @AC6 @P1 @error-guessing @low-confidence
Scenario: Weekend/holiday rate fallback is used and report flagged as rateStale
  Given a report dated on a weekend with no exact‑date rate, using the last available prior rate
  When the report is submitted
  Then the submission succeeds and the report is flagged rateStale

# US-004 - AC6 - AC6-C4
# open: Q7
@QAIA-US-004-026 @AC6 @P1 @decision-table @low-confidence
Scenario: Stale rate conversion near band boundary still drives approvals
  Given a manager‑submitted foreign‑currency report converted via a stale fallback rate resulting in €499.95
  When the report is submitted
  Then the approval chain follows the manager + finance path and self‑approval escalation applies

# US-004 - AC7 - AC7-C1
@QAIA-US-004-027 @AC7 @P2 @state-transition @negative
Scenario: Editing a rejected report is refused
  Given a report in rejected state
  When an edit is attempted on the report
  Then the edit is refused

# US-004 - AC7 - AC7-C2
@QAIA-US-004-028 @AC7 @P2 @state-transition @negative
Scenario: Re‑submitting a rejected report is refused
  Given a report in rejected state
  When a submit action is performed on the report
  Then the submission is refused

# US-004 - AC8 - AC8-C1
@QAIA-US-004-029 @AC8 @P2 @boundary @negative
Scenario: Rejecting without a comment or with short comment is refused
  Given a rejected action without a comment
  When the rejection is attempted
  Then the rejection is refused

# US-004 - AC8 - AC8-C2
@QAIA-US-004-030 @AC8 @P2 @boundary @negative
Scenario: Requesting changes without a comment or with short comment is refused
  Given a changes‑requested action without a comment
  When the request is attempted
  Then the request is refused

# US-004 - AC8 - AC8-C3
@QAIA-US-004-031 @AC8 @P2 @boundary
Scenario: Comment of exactly 10 characters is accepted
  Given a comment consisting of exactly ten characters
  When the comment is submitted with a changes‑requested action
  Then the action is accepted

# US-004 - AC8 - AC8-C4
@QAIA-US-004-032 @AC8 @P3 @ep
Scenario: Approving a report does not require a comment
  Given an approved action without any comment
  When the approval is performed
  Then the approval succeeds

# US-004 - AC8 - AC8-C5
@QAIA-US-004-033 @AC8 @P1 @error-guessing
Scenario: Every transition is recorded in the audit trail with actor and timestamp
  Given any transition (create, submit, approve, reject, changes‑requested) on a report
  When the transition occurs
  Then an audit‑trail entry with who and when is recorded

# US-004 - AC-auth - AC-auth-C1
@QAIA-US-004-034 @AC-auth @P2 @error-guessing @negative
Scenario: Creating a report without authentication is refused
  Given an unauthenticated user
  When the user attempts to create a report
  Then the creation is refused with status 401

# US-004 - AC-auth - AC-auth-C2
@QAIA-US-004-035 @AC-auth @P2 @error-guessing @negative
Scenario: Deciding on a report without authentication is refused
  Given an unauthenticated user
  When the user attempts to approve a report
  Then the approval is refused with status 401

# US-004 - AC-auth - AC-auth-C3
@QAIA-US-004-036 @AC-auth @P1 @error-guessing @negative
Scenario: Editing another employee's draft without proper authorization is refused with 404
  Given an authenticated employee A
  And a draft report owned by employee B
  When employee A attempts to edit employee B's draft
  Then the edit is refused with status 404

# US-004 - AC-list - AC-list-C1
@QAIA-US-004-037 @AC-list @P3 @ep
Scenario: Employee with no reports sees an empty list
  Given an authenticated employee with no reports
  When the employee views the "My reports" list
  Then the list is empty
