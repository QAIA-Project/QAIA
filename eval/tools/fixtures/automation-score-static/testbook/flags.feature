# Fixture for eval/tools/automation_score.py -- static checks `flag-dropped` and
# `single-sided-evidence`. Two scenarios rest on an open question and say so; two do not.
Feature: Fixture for the flag-drop and one-sided-evidence checks

  @QAIA-FIX-001 @P1 @low-confidence @api
  # open: Q1 -- the specification does not say whether exactly 25 is inside or outside the band.
  Scenario: A flagged scenario, whose test must carry the flag
    Given a request at exactly the boundary
    When it is submitted
    Then it is accepted

  @QAIA-FIX-002 @P2 @api
  Scenario: An unflagged scenario, whose test needs no flag
    Given a request well inside the band
    When it is submitted
    Then it is accepted

  @QAIA-FIX-003 @P1 @negative @api
  Scenario: A refusal that must be asserted by what it is, not only by what it is not
    Given a request missing a required field
    When it is submitted
    Then it is refused with a message naming the missing field

  @QAIA-FIX-004 @P2 @low-confidence @api
  Scenario: A second flagged scenario, whose test does carry the flag
    Given an ambiguous input
    When it is submitted
    Then the assumed behaviour applies
