# Feature: audit trail and mandatory comments (AC8), plus cross-cutting authorization
# and IDOR conditions surfaced by the 3c systematic-expansion checklist (not literally
# named per-AC in the source, but a reflex expansion for any authenticated, multi-actor
# approval workflow). One list-view empty-state condition (AC-list-C1).
Feature: Audit trail, mandatory comments and access control

  Background:
    Given the ExpenseFlow SUT is reset to its seed state

  @QAIA-US-004-030 @AC8 @P2 @negative @api @boundary
  # condition: AC8-C1 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 422
  Scenario: Rejecting without a sufficient comment is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" attempts to reject report "R" with comment "too short"
    Then the attempt is refused

  @QAIA-US-004-031 @AC8 @P2 @negative @api @boundary
  # condition: AC8-C2 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 422
  Scenario: Requesting changes without a sufficient comment is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" attempts to request changes on report "R" with comment "too short"
    Then the attempt is refused

  @QAIA-US-004-032 @AC8 @P2 @api @boundary
  # condition: AC8-C3 — priority P2
  Scenario: A comment of exactly 10 characters is accepted
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" rejects report "R" with a comment of exactly 10 characters
    Then report "R" status is "rejected"

  @QAIA-US-004-033 @AC8 @P3 @api @ep
  # condition: AC8-C4 — priority P3
  Scenario: Approving a report does not require a comment
    Given a submitted report "R" by "employee@demo" totalling exactly 499.99 EUR
    When "manager@demo" approves report "R" without a comment
    Then report "R" status is "approved"

  @QAIA-US-004-034 @AC8 @P1 @api @error-guessing
  # condition: AC8-C5 — priority P1
  Scenario: Every transition is recorded in the audit trail with who and when
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" approves report "R"
    Then the audit trail contains a "submit" event by "employee@demo" and an "approve" event by "manager@demo", both timestamped

  @QAIA-US-004-035 @AC-auth @P2 @negative @api @error-guessing
  # condition: AC-auth-C1 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 401
  Scenario: Creating a report without authentication is refused
    When an unauthenticated request attempts to create a report
    Then the attempt is refused

  @QAIA-US-004-036 @AC-auth @P2 @negative @api @error-guessing
  # condition: AC-auth-C2 [req-neg] — priority P2 — Q10: the AC states refusal, not a status; SUT answers 401
  Scenario: Deciding on a report without authentication is refused
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When an unauthenticated request attempts to approve report "R"
    Then the attempt is refused

  @QAIA-US-004-037 @AC-auth @P1 @negative @api @error-guessing
  # condition: AC-auth-C3 [req-neg] — priority P1 — Q10: the AC states refusal, not a status; SUT answers 404
  Scenario: An employee cannot edit another employee's draft report
    Given "manager@demo" has a draft report of their own, "M"
    When "employee@demo" attempts to edit report "M"
    Then the attempt is refused

  @QAIA-US-004-038 @AC-list @P3 @e2e @ep
  # condition: AC-list-C1 — priority P3
  Scenario: An employee with no reports sees an empty "My reports" list
    Given "employee@demo" is signed in with no reports of their own
    When "employee@demo" views "My reports"
    Then the list is empty

  @QAIA-US-004-039 @AC-auth @P1 @negative @api @error-guessing
  # condition: AC-auth-C4 [req-neg] — priority P1 — chemin de LECTURE, ajoute le 2026-07-26 :
  # l'ecriture etait couverte (037), la lecture ne l'etait par rien. Q10 : l'AC enonce un refus,
  # pas un statut ; le SUT repond 404 pour ne pas divulguer l'existence du rapport.
  Scenario: A manager cannot read an employee's unsubmitted draft
    Given "employee@demo" has a draft report "D" that has never been submitted
    When "manager@demo" attempts to read report "D"
    Then the attempt is refused

  @QAIA-US-004-040 @AC-auth @P2 @api
  # condition: AC-auth-C5 — priority P2 — le pendant positif de 039 et 041 : sans lui, les deux
  # refus seraient satisfaits par un SUT qui refuse tout le monde tout le temps.
  Scenario: The current approver can read a report once it awaits their role
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "manager@demo" reads report "R"
    Then the report is returned with its lines and its total

  @QAIA-US-004-041 @AC-auth @P2 @negative @api @error-guessing
  # condition: AC-auth-C6 [req-neg] — priority P2 — etre approbateur ne suffit pas : il faut
  # etre l'approbateur ATTENDU a cet instant de la chaine.
  Scenario: An approver not yet in the chain cannot read a submitted report
    Given a submitted report "R" by "employee@demo" awaiting manager approval
    When "finance@demo" attempts to read report "R"
    Then the attempt is refused

  @QAIA-US-004-042 @AC8 @P1 @negative @api @error-guessing
  # condition: AC8-C4 [req-neg] — priority P1 — trouve le 2026-07-26 : GET /api/audit n'avait
  # aucun controle d'authentification et exposait le journal complet a n'importe qui.
  Scenario: Reading the audit trail without authentication is refused
    Given at least one report has been submitted and decided
    When an unauthenticated request attempts to read the audit trail
    Then the attempt is refused
