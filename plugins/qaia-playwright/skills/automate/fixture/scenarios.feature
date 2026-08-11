# Minimal excerpt, deliberately built for issue #41 (self-review lint validation).
# Not a real product US — three scenarios, each with a concrete, assertable Then,
# chosen to exercise the three violation classes step 5 must catch.

Feature: Booking cancellation window (fixture for automate's assertion self-review)

  @QAIA-FIXTURE-041-001 @AC6 @P1 @e2e
  Scenario: cancellation refused less than 4h before start
    Given a patient has booked a slot starting in 3 hours
    When the patient requests cancellation
    Then the system refuses the cancellation and shows "less than 4 hours"

  @QAIA-FIXTURE-041-002 @AC6 @P1 @e2e
  Scenario: cancel button is enabled once a slot is booked
    Given a patient has booked a slot starting in 26 hours
    When the booking confirmation is displayed
    Then the cancel button is visible and enabled

  @QAIA-FIXTURE-041-003 @AC1 @P2 @e2e
  Scenario: specialty filter shows only matching practitioners
    Given the practitioner list contains dermatology and cardiology slots
    When the patient filters by "dermatology"
    Then only dermatology slots are displayed

  # --- The five defect classes measured on real generated suites (D5-D9). Each scenario below
  # --- is written so that exactly one of them can be committed against it.

  @QAIA-FIXTURE-041-004 @AC7 @P1 @low-confidence @e2e
  # open: Q1 -- the specification does not say whether an unregistered address must be treated
  # identically to a registered one. Proposed default below; human arbitration required.
  Scenario: an unregistered address gives no signal distinguishing it from a registered one
    Given the password reset page is open
    When an address that is not registered is submitted
    Then the security question field is enabled, the same as for a registered address

  @QAIA-FIXTURE-041-005 @AC7 @P1 @negative @e2e
  Scenario: a cancellation without a reason is refused, and no cancellation is recorded
    Given a patient has booked a slot starting in 26 hours
    When cancellation is requested with no reason given
    Then the request is refused with a message naming the missing reason
    And no cancellation appears in the booking history
