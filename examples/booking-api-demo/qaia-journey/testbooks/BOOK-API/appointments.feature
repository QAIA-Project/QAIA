# Feature: BOOK-API — createAppointment (POST /api/appointments)
# Derived from sources/booking-api.openapi.yaml (sha256 009c4ecd...) by openapi-ingest +
# istqb-design. Every scenario is @api: each rests on a clause of the service contract,
# observable in HTTP without a browser (ADR 0008). Never derived from app/server.js.
Feature: Creating an appointment through the booking API

  Background:
    Given the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"

  # C1 — the one promise every other scenario is measured against
  @QAIA-BOOK-API-001 @AC1 @P1 @api @ep
  Scenario: A valid request creates the appointment
    # contract: createAppointment · responses.201
    Given an authenticated patient
    When they POST /api/appointments with a valid body for slot "S1"
    Then the response status is 201
    And the response body carries an appointment id
    And the Location header points at the created appointment

  # C2, C3 — security → 401
  @QAIA-BOOK-API-002 @AC1 @P1 @api @negative @ep
  Scenario Outline: A request without a usable credential is refused
    # contract: createAppointment · security → responses.401
    Given a client presenting "<credential>"
    When they POST /api/appointments with a valid body for slot "S1"
    Then the response status is 401

    Examples:
      | credential      |
      | no header       |
      | Bearer wrong    |
      | Basic dXNlcg==  |

  # C4 — required → 400, one field omitted at a time
  @QAIA-BOOK-API-003 @AC1 @P1 @api @negative @ep
  Scenario Outline: Omitting a required field is refused
    # contract: AppointmentCreate.required → responses.400
    Given an authenticated patient
    When they POST /api/appointments with "<field>" omitted
    Then the response status is 400
    And the response body names the field "<field>"

    Examples:
      | field     |
      | slotId    |
      | patientId |
      | specialty |

  # C5 — enum, every declared value
  @QAIA-BOOK-API-004 @AC1 @P2 @api @ep
  Scenario Outline: Every declared specialty is accepted
    # contract: AppointmentCreate.specialty.enum
    Given an authenticated patient
    When they POST /api/appointments with specialty "<specialty>"
    Then the response status is 201

    Examples:
      | specialty   |
      | general     |
      | pediatrics  |
      | cardiology  |
      | dermatology |

  # C6 — outside the enum
  @QAIA-BOOK-API-005 @AC1 @P1 @api @negative @ep
  Scenario: A specialty outside the enumeration is refused
    # contract: AppointmentCreate.specialty.enum → responses.400
    Given an authenticated patient
    When they POST /api/appointments with specialty "oncology"
    Then the response status is 400
    And the response body names the field "specialty"

  # C7 — additionalProperties: false
  @QAIA-BOOK-API-006 @AC1 @P2 @api @negative @ep
  Scenario: A property the schema does not declare is refused
    # contract: AppointmentCreate.additionalProperties: false → responses.400
    Given an authenticated patient
    When they POST /api/appointments with an undeclared property "priority"
    Then the response status is 400
    And the response body names the field "priority"

  # C8, C9 — maxLength boundary
  @QAIA-BOOK-API-007 @AC1 @P2 @api @boundary
  Scenario: A note of exactly 280 characters is accepted
    # contract: AppointmentCreate.note.maxLength
    Given an authenticated patient
    When they POST /api/appointments with a note of 280 characters
    Then the response status is 201

  @QAIA-BOOK-API-008 @AC1 @P2 @api @negative @boundary
  Scenario: A note of 281 characters is refused
    # contract: AppointmentCreate.note.maxLength → responses.400
    Given an authenticated patient
    When they POST /api/appointments with a note of 281 characters
    Then the response status is 400
    And the response body names the field "note"

  # C10 — format: date-time
  @QAIA-BOOK-API-009 @AC1 @P2 @api @negative @ep
  Scenario: A startsAt that is not a date-time is refused
    # contract: AppointmentCreate.startsAt.format → responses.400
    Given an authenticated patient
    When they POST /api/appointments with startsAt "next tuesday"
    Then the response status is 400
    And the response body names the field "startsAt"

  # C11 — type: string
  @QAIA-BOOK-API-010 @AC1 @P2 @api @negative @ep
  Scenario: A field of the wrong type is refused
    # contract: AppointmentCreate.slotId.type → responses.400
    Given an authenticated patient
    When they POST /api/appointments with slotId as the number 42
    Then the response status is 400
    And the response body names the field "slotId"

  # C12 — 409
  @QAIA-BOOK-API-011 @AC1 @P1 @api @negative @ep
  Scenario: A slot already taken is refused
    # contract: createAppointment · responses.409
    Given slot "S1" is already booked
    And an authenticated patient
    When they POST /api/appointments with a valid body for slot "S1"
    Then the response status is 409

  # C13, C14 — the upcoming-appointments ceiling, on the safe default of Q1
  @QAIA-BOOK-API-012 @AC1 @P1 @api @negative @boundary @low-confidence
  Scenario: A patient who already has three upcoming appointments is refused
    # contract: createAppointment · responses.422
    # open: Q1 -- the ceiling lives only in the prose of the 422 description, never in the
    # schema. Safe default applied: "more than 3 upcoming" refuses the fourth.
    Given patient "P1" already has 3 upcoming appointments
    And an authenticated patient
    When they POST /api/appointments for patient "P1" on slot "S9"
    Then the response status is 422

  @QAIA-BOOK-API-013 @AC1 @P2 @api @boundary @low-confidence
  Scenario: A patient who has two upcoming appointments is accepted
    # contract: createAppointment · responses.422
    # open: Q1 -- same undeclared ceiling; this is the inside of the same boundary.
    Given patient "P1" already has 2 upcoming appointments
    And an authenticated patient
    When they POST /api/appointments for patient "P1" on slot "S9"
    Then the response status is 201

  # C15, C16 — the two-hour lead time, on the safe default of Q1
  @QAIA-BOOK-API-014 @AC1 @P1 @api @negative @boundary @low-confidence
  Scenario: A slot starting in less than two hours is refused
    # contract: createAppointment · responses.422
    # open: Q1 -- the lead time is prose in the 422 description, absent from the schema.
    Given an authenticated patient
    When they POST /api/appointments with startsAt "2026-08-11T09:59:00Z"
    Then the response status is 422

  @QAIA-BOOK-API-015 @AC1 @P2 @api @boundary @low-confidence
  Scenario: A slot starting in exactly two hours is accepted
    # contract: createAppointment · responses.422
    # open: Q1 -- the bound is stated as "< 2h", so exactly 2h is inside. Safe default.
    Given an authenticated patient
    When they POST /api/appointments with startsAt "2026-08-11T10:00:00Z"
    Then the response status is 201

  # C-Q2 — the optional field the undeclared rule depends on
  @QAIA-BOOK-API-016 @AC1 @P3 @api @ep @low-confidence
  Scenario: A request omitting startsAt entirely is accepted
    # contract: AppointmentCreate.startsAt (optional, absent from `required`)
    # open: Q2 -- startsAt is optional while the two-hour rule depends on it; the contract
    # never says what happens when it is absent. Safe default: no lead-time rule applies.
    Given an authenticated patient
    When they POST /api/appointments without startsAt
    Then the response status is 201
