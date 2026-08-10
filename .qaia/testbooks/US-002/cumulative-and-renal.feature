Feature: Cumulative 24 h dose and renal adjustment (US-002, AC4 and AC6)
  The cumulative ceiling over 24 h, and the 50 % reduction applied for patients carrying a
  renal insufficiency flag. AC6 is covered by a metamorphic relation rather than an exact
  expected value, because the source states no rounding rule.

  Background:
    Given the drug "DRUG-A" has a reference record with minimum effective dose 10 mg, maximum safe dose per intake 40 mg, maximum cumulative dose 100 mg per 24 h and an age floor of 12 years
    And "physician@demo" is a prescribing physician without the "pediatric specialist" role
    And patient "P1" is 30 years old with no renal insufficiency flag

  @QAIA-US-002-010 @AC4 @P1 @boundary @low-confidence
  # condition: C10 — priority P1 — open: Q1 (inclusivity of the ceiling), Q3 (24 h window
  # rolling or calendar) — read here as: exactly the ceiling is allowed
  Scenario: Intakes summing exactly to the cumulative ceiling are accepted
    Given "P1" has already received 60 mg of "DRUG-A" in the last 24 hours
    When "physician@demo" prescribes 40 mg of "DRUG-A" to "P1"
    Then the validation result is "pass"

  @QAIA-US-002-011 @AC4 @P1 @boundary @negative @low-confidence
  # condition: C11 [req-neg] — priority P1 — open: Q3 (which clock and which window)
  Scenario: Intakes summing above the cumulative ceiling block the signature
    Given "P1" has already received 61 mg of "DRUG-A" in the last 24 hours
    When "physician@demo" prescribes 40 mg of "DRUG-A" to "P1"
    Then the validation result is "blocked"
    And the prescription cannot be signed

  @QAIA-US-002-012 @AC4 @P2 @domain-analysis @low-confidence
  # condition: C12 — priority P2 — open: Q3 (a rolling window blocks this case, a calendar
  # day accepts it; the two readings give opposite verdicts on the same prescription)
  Scenario: Intakes straddling midnight are counted against the same 24 h window
    Given "P1" received 60 mg of "DRUG-A" at 23:00 on the previous day
    When "physician@demo" prescribes 60 mg of "DRUG-A" to "P1" at 01:00
    Then the validation result is "blocked"

  @QAIA-US-002-013 @AC4 @P2 @domain-analysis @negative @low-confidence
  # condition: C13 [req-neg] — priority P2 — open: Q8 (concurrency is not specified)
  Scenario: Two prescriptions signed concurrently cannot together exceed the ceiling
    Given "physician@demo" and "physician2@demo" each prepare a 60 mg prescription of "DRUG-A" for "P1"
    When both prescriptions are signed at the same time
    Then at most one of them is accepted

  @QAIA-US-002-018 @AC6 @P2 @metamorphic
  # condition: C18 — priority P2 — relation asserted instead of an exact value, because the
  # rounding rule is absent from the source
  Scenario: A renal-flagged patient never gets a more permissive verdict than an unflagged one
    Given patient "P2" is 30 years old with a renal insufficiency flag
    When "physician@demo" prescribes 30 mg of "DRUG-A" to "P1"
    And "physician@demo" prescribes 30 mg of "DRUG-A" to "P2"
    Then the verdict for "P2" is at least as restrictive as the verdict for "P1"

  @QAIA-US-002-019 @AC6 @P2 @metamorphic @low-confidence
  # condition: C19 — priority P2 — open: Q6 (halving an odd threshold has no stated rounding
  # rule; rounding up admits a dose that rounding down blocks)
  Scenario: Halving an odd threshold does not admit a dose above the reduced ceiling
    Given the drug "DRUG-C" has a reference record with maximum safe dose per intake 7 mg
    And patient "P2" is 30 years old with a renal insufficiency flag
    When "physician@demo" prescribes 4 mg of "DRUG-C" to "P2"
    Then the validation result is not "pass"

  @QAIA-US-002-020 @AC6 @P1 @decision-table @low-confidence
  # condition: C20 — priority P1 — open: Q4 (when the reduced maximum falls below the minimum
  # effective dose, every dose is both under the minimum and over the maximum; the source does
  # not say which verdict wins — read here as: the blocking rule wins)
  Scenario: A reduced maximum falling below the minimum effective dose does not silently pass
    Given the drug "DRUG-D" has a reference record with minimum effective dose 10 mg and maximum safe dose per intake 15 mg
    And patient "P2" is 30 years old with a renal insufficiency flag
    When "physician@demo" prescribes 10 mg of "DRUG-D" to "P2"
    Then the validation result is "blocked"
