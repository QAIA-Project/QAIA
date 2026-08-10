Feature: Age floor, pediatric exception and override audit (US-002, AC5 and AC7)
  The age rule and its role-based exception, and what an override must record. AC5 is derived
  from a decision table over two conditions (age below floor, pediatric role); AC7 from boundary
  analysis on the 20-character justification.

  Background:
    Given the drug "DRUG-A" has a reference record with minimum effective dose 10 mg, maximum safe dose per intake 40 mg, maximum cumulative dose 100 mg per 24 h and an age floor of 12 years
    And "physician@demo" is a prescribing physician without the "pediatric specialist" role
    And "pediatrician@demo" is a prescribing physician with the "pediatric specialist" role

  @QAIA-US-002-014 @AC5 @P1 @decision-table @negative
  # condition: C14 [req-neg] — priority P1
  Scenario: A patient below the age floor is blocked for a non-pediatric prescriber
    Given patient "P3" is 11 years old with no renal insufficiency flag
    When "physician@demo" prescribes 20 mg of "DRUG-A" to "P3"
    Then the validation result is "blocked"
    And the prescription cannot be signed

  @QAIA-US-002-015 @AC5 @P2 @boundary
  # condition: C15 — priority P2
  Scenario: A patient exactly at the age floor is accepted
    Given patient "P4" is 12 years old with no renal insufficiency flag
    When "physician@demo" prescribes 20 mg of "DRUG-A" to "P4"
    Then the validation result is "pass"

  @QAIA-US-002-016 @AC5 @P2 @decision-table
  # condition: C16 — priority P2
  Scenario: A pediatric specialist gets an overridable warning instead of a block
    Given patient "P3" is 11 years old with no renal insufficiency flag
    When "pediatrician@demo" prescribes 20 mg of "DRUG-A" to "P3"
    Then the validation result is "warning"
    And the warning is overridable with a documented reason

  @QAIA-US-002-017 @AC5 @P1 @decision-table @negative
  # condition: C17 [req-neg] — priority P1
  Scenario: A pediatric override without justification is refused
    Given patient "P3" is 11 years old with no renal insufficiency flag
    And "pediatrician@demo" prescribes 20 mg of "DRUG-A" to "P3"
    When "pediatrician@demo" overrides the warning with no justification
    Then the override is refused
    And the prescription cannot be signed

  @QAIA-US-002-021 @AC5 @P1 @decision-table @low-confidence
  # condition: C21 — priority P1 — open: Q5 (AC5's role exception and AC6's renal reduction
  # can apply to the same patient; whether the role exception also converts a threshold block
  # into an overridable warning is not specified — read here as: it does not)
  Scenario: The pediatric exception does not convert a renal threshold block into a warning
    Given patient "P5" is 11 years old with a renal insufficiency flag
    When "pediatrician@demo" prescribes 30 mg of "DRUG-A" to "P5"
    Then the validation result is "blocked"

  @QAIA-US-002-022 @AC7 @P1 @boundary @negative
  # condition: C22 [req-neg] — priority P1
  Scenario: An override justified with 19 characters is refused
    Given patient "P1" is 30 years old with no renal insufficiency flag
    And "physician@demo" prescribes 9 mg of "DRUG-A" to "P1"
    When "physician@demo" overrides the warning with a justification of 19 characters
    Then the override is refused

  @QAIA-US-002-023 @AC7 @P2 @boundary
  # condition: C23 — priority P2 — assumption: length counted in Unicode code points after
  # trimming leading and trailing whitespace (Q10)
  Scenario: An override justified with 20 characters is accepted
    Given patient "P1" is 30 years old with no renal insufficiency flag
    And "physician@demo" prescribes 9 mg of "DRUG-A" to "P1"
    When "physician@demo" overrides the warning with a justification of 20 characters
    Then the override is accepted

  @QAIA-US-002-024 @AC7 @P3 @ep @negative @low-confidence
  # condition: C24 [req-neg] — priority P3 — open: Q10 (whether the 20-character rule is a
  # quality guard or a plain length check — read here as: whitespace alone does not qualify)
  Scenario: An override justified with 20 spaces is refused
    Given patient "P1" is 30 years old with no renal insufficiency flag
    And "physician@demo" prescribes 9 mg of "DRUG-A" to "P1"
    When "physician@demo" overrides the warning with a justification of 20 spaces
    Then the override is refused

  @QAIA-US-002-025 @AC7 @P3 @ep
  # condition: C25 — priority P3
  Scenario: An accepted override records identity, timestamp and justification
    Given patient "P1" is 30 years old with no renal insufficiency flag
    And "physician@demo" prescribes 9 mg of "DRUG-A" to "P1"
    When "physician@demo" overrides the warning with the reason "Deliberate low start dose for this patient"
    Then the audit trail contains an entry naming "physician@demo"
    And that entry carries a timestamp and the justification text
