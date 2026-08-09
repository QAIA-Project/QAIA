Feature: Create appointment — API contract oracle (POST /api/appointments)
  # Conditions derived by oracle-generate from booking-api.openapi.yaml (the project oracle,
  # issue #16). Every scenario cites the operation and the spec element it is grounded in.
  # Expected statuses come from the contract's documented `responses`, not from extrapolation.

  @QAIA-SHOP-DEMO-201 @P1 @oracle:openapi
  Scenario: Valid request creates the appointment
    # oracle: openapi createAppointment 201
    Given an authenticated patient and an available slot
    When they POST a body with slotId, patientId and specialty "cardiology"
    Then the API responds 201

  @QAIA-SHOP-DEMO-202 @P1 @negative @oracle:openapi @error-guessing
  Scenario: Unauthenticated request is refused
    # oracle: openapi createAppointment security -> 401
    Given no bearer token
    When they POST a valid appointment body
    Then the API responds 401

  @QAIA-SHOP-DEMO-203 @P1 @negative @oracle:openapi @decision-table
  Scenario Outline: Omitting a required field is rejected
    # oracle: openapi createAppointment requestBody.required -> 400
    Given an authenticated patient
    When they POST a body missing "<field>"
    Then the API responds 400

    Examples:
      | field     |
      | slotId    |
      | patientId |
      | specialty |

  @QAIA-SHOP-DEMO-204 @P2 @negative @oracle:openapi @ep
  Scenario: A specialty outside the enum is rejected
    # oracle: openapi createAppointment specialty.enum -> 400
    Given an authenticated patient
    When they POST specialty "astrology"
    Then the API responds 400

  @QAIA-SHOP-DEMO-205 @P2 @negative @oracle:openapi @boundary
  Scenario: A note longer than 280 characters is rejected
    # oracle: openapi createAppointment note.maxLength=280 -> 400
    Given an authenticated patient
    When they POST a note of 281 characters
    Then the API responds 400

  @QAIA-SHOP-DEMO-206 @P2 @negative @oracle:openapi @oracle:iso-8601 @boundary
  Scenario: An impossible startsAt date is rejected
    # oracle: openapi createAppointment startsAt.format=date-time -> chains to ISO 8601 oracle -> 400
    Given an authenticated patient
    When they POST startsAt "2023-02-29T10:00:00Z"
    Then the API responds 400

  @QAIA-SHOP-DEMO-207 @P1 @negative @oracle:openapi @state-transition
  Scenario: Booking an already-taken slot loses the race
    # oracle: openapi createAppointment 409
    Given a slot just booked by another patient
    When they POST the same slotId
    Then the API responds 409
