Feature: Per-intake dosage thresholds (US-002, AC1-AC3)
  Validation of a prescribed dose against the drug's reference record, before signature.
  Scenarios tagged @low-confidence rest on an open question named in the tag comment; they
  assert an assumption, not a confirmed rule.

  Background:
    Given the drug "DRUG-A" has a reference record with minimum effective dose 10 mg, maximum safe dose per intake 40 mg, maximum cumulative dose 100 mg per 24 h and an age floor of 12 years
    And "physician@demo" is a prescribing physician without the "pediatric specialist" role
    And patient "P1" is 30 years old with no renal insufficiency flag

  @QAIA-US-002-001 @AC1 @P3 @ep
  # condition: C01 — priority P3
  Scenario: A drug with a complete reference record can be validated
    When "physician@demo" prescribes 20 mg of "DRUG-A" to "P1"
    Then the validation result is "pass"

  @QAIA-US-002-002 @AC1 @P1 @error-guessing @negative @low-confidence
  # condition: C02 [req-neg] — priority P1 — open: Q7 (no reference record: blocked, warned
  # or passed is not specified; asserted as blocking because passing an unknown drug is the
  # worst available failure mode)
  Scenario: A drug with no reference record cannot be silently accepted
    Given the drug "DRUG-X" has no reference record
    When "physician@demo" prescribes 20 mg of "DRUG-X" to "P1"
    Then the validation result is not "pass"

  @QAIA-US-002-003 @AC1 @P3 @error-guessing @low-confidence
  # condition: C03 — priority P3 — open: Q7 (incomplete record — age floor missing)
  Scenario: A reference record missing its age floor does not silently skip the age rule
    Given the drug "DRUG-B" has a reference record with no age floor
    When "physician@demo" prescribes 20 mg of "DRUG-B" to "P1"
    Then the validation result is not "pass"

  @QAIA-US-002-004 @AC2 @P2 @boundary
  # condition: C04 — priority P2
  Scenario: A dose just below the minimum effective dose raises an overridable warning
    When "physician@demo" prescribes 9 mg of "DRUG-A" to "P1"
    Then the validation result is "warning"
    And the warning is overridable with a documented reason

  @QAIA-US-002-005 @AC2 @P2 @boundary
  # condition: C05 — priority P2
  Scenario: A dose exactly at the minimum effective dose raises no warning
    When "physician@demo" prescribes 10 mg of "DRUG-A" to "P1"
    Then the validation result is "pass"

  @QAIA-US-002-006 @AC2 @P3 @ep @low-confidence
  # condition: C06 — priority P3 — open: Q9 (which physician may override is not specified)
  Scenario: An overridden low-dose warning allows the prescription to be signed
    Given "physician@demo" prescribes 9 mg of "DRUG-A" to "P1"
    When "physician@demo" overrides the warning with the reason "Deliberate low start dose for this patient"
    Then the prescription can be signed

  @QAIA-US-002-007 @AC3 @P2 @boundary
  # condition: C07 — priority P2
  Scenario: A dose just below the maximum safe dose per intake is accepted
    When "physician@demo" prescribes 39 mg of "DRUG-A" to "P1"
    Then the validation result is "pass"

  @QAIA-US-002-008 @AC3 @P1 @boundary @low-confidence
  # condition: C08 — priority P1 — open: Q1 (AC3 says "above the maximum safe dose" while AC2
  # says "strictly below"; whether the maximum itself is allowed is undecided — read here as
  # inclusive, meaning exactly the maximum passes)
  Scenario: A dose exactly at the maximum safe dose per intake is accepted
    When "physician@demo" prescribes 40 mg of "DRUG-A" to "P1"
    Then the validation result is "pass"

  @QAIA-US-002-009 @AC3 @P1 @boundary @negative
  # condition: C09 [req-neg] — priority P1
  Scenario: A dose above the maximum safe dose per intake blocks the signature
    When "physician@demo" prescribes 41 mg of "DRUG-A" to "P1"
    Then the validation result is "blocked"
    And the prescription cannot be signed

  @QAIA-US-002-028 @AC2 @P2 @error-guessing @negative @low-confidence
  # condition: C28 [req-neg] — priority P2 — open: Q2 (no dose unit is named anywhere in the
  # source; a comparison across unlike units would be a silent false pass)
  Scenario: A dose expressed in a unit other than the reference record's is not compared as-is
    When "physician@demo" prescribes 20 micrograms of "DRUG-A" to "P1"
    Then the validation result is not "pass"
