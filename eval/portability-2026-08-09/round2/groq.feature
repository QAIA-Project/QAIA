Feature: Report management
  # US-004

  @QAIA-US-004-001 @AC1 @P2
  Scenario: Submit a report with valid data
    Given a report with valid data
    When the user submits the report
    Then the report is submitted successfully

  @QAIA-US-004-002 @AC1 @P2
  Scenario: Submit a report without authentication
    Given a report with valid data
    When the user submits the report without authentication
    Then the submission is refused with a 401 error

  @QAIA-US-004-003 @AC2 @P1
  Scenario: Total just under €500 requires one approval
    Given a report with a total just under €500
    When the user submits the report
    Then the report requires one approval

  @QAIA-US-004-004 @AC2 @P1
  Scenario: Total exactly €500 requires two approvals
    Given a report with a total exactly €500
    When the user submits the report
    Then the report requires two approvals

  @QAIA-US-004-005 @AC3 @P1
  Scenario: Self-approval is refused
    Given a report submitted by a user
    When the user attempts to approve their own report
    Then the approval is refused

  @QAIA-US-004-006 @AC4 @P2
  Scenario: Line missing category, amount, or date is refused
    Given a report with a line missing category, amount, or date
    When the user submits the report
    Then the submission is refused

  @QAIA-US-004-007 @AC5 @P1
  Scenario: Total just under the EUR-equivalent €25 threshold, no receipt, is accepted
    Given a report with a total just under the EUR-equivalent €25 threshold
    When the user submits the report
    Then the report is accepted

  @QAIA-US-004-008 @AC6 @P1
  Scenario: Total just above the EUR-equivalent €25 threshold, with receipt, is accepted
    Given a report with a total just above the EUR-equivalent €25 threshold
    When the user submits the report with a receipt
    Then the report is accepted

  @QAIA-US-004-009 @AC7 @P2
  Scenario: Rejecting a report without a comment is refused
    Given a report submitted by a user
    When the user attempts to reject the report without a comment
    Then the rejection is refused

  @QAIA-US-004-010 @AC8 @P1
  Scenario: Audit trail completeness across multiple event types
    Given a report submitted by a user
    When the user performs multiple actions on the report
    Then the audit trail is complete and accurate

  @QAIA-US-004-011 @AC-auth @P2
  Scenario: IDOR class - IDs are IDOR-guessable
    Given a report submitted by a user
    When the user attempts to access another user's report
    Then the access is refused

  @QAIA-US-004-012 @AC-list @P3
  Scenario: Cosmetic empty state
    Given a user with no reports
    When the user views their reports
    Then the user sees an explicit empty state

  # ... (les autres scenarios)

Note: Il est important de noter que ce fichier est généré automatiquement à partir des spécifications fournies et que les numéros de scénario (@QAIA-US-004-XXX) sont uniques et doivent être conservés pour assurer la traçabilité. De plus, les étiquettes (@ACX, @PX) sont utilisées pour lier les scénarios aux exigences et priorités respectives.
