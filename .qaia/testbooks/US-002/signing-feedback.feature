Feature: Validation feedback in the signing screen (US-002, AC8)
  What the prescriber sees, where, and with which rule identifiers. The scenario-based test of
  this user story lives here — one per US, per the technique palette.

  Background:
    Given the drug "DRUG-A" has a reference record with minimum effective dose 10 mg, maximum safe dose per intake 40 mg, maximum cumulative dose 100 mg per 24 h and an age floor of 12 years
    And "physician@demo" is a prescribing physician without the "pediatric specialist" role
    And patient "P1" is 30 years old with no renal insufficiency flag

  @QAIA-US-002-026 @AC8 @P3 @e2e @use-case @smoke
  # condition: C26 — priority P3 — the single scenario-based test of this US
  Scenario: A prescriber sees the verdict in the signing screen without a page reload
    Given "physician@demo" is on the signing screen for a prescription of "DRUG-A" to "P1"
    When "physician@demo" enters a dose of 41 mg
    Then the validation result "blocked" appears in the signing screen
    And the rule identifier that produced it is shown
    And the page is not reloaded

  @QAIA-US-002-027 @AC8 @P3 @e2e @ep
  # condition: C27 — priority P3
  Scenario: A prescription breaking two rules at once reports both rule identifiers
    Given "P1" has already received 61 mg of "DRUG-A" in the last 24 hours
    When "physician@demo" prescribes 41 mg of "DRUG-A" to "P1"
    Then the validation result is "blocked"
    And the rule identifiers shown include both the per-intake rule and the cumulative rule
