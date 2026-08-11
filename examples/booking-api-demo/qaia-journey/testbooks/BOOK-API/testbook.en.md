---
language: en
source: appointments.feature
---

# Booking API — createAppointment: the test book in plain language

Projection of appointments.feature. Same scenarios, same steps, same order — readable without knowing Gherkin. The .feature file stays the source of truth; this file is checked against it step by step, and a single divergence fails the build.

### QAIA-BOOK-API-001 · A valid request creates the appointment

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with a valid body for slot "S1"

**Expected result**

4. the response status is 201
5. the response body carries an appointment id
6. the Location header points at the created appointment

### QAIA-BOOK-API-002-e1 · A request without a usable credential is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. a client presenting "no header"

**Action**

3. they POST /api/appointments with a valid body for slot "S1"

**Expected result**

4. the response status is 401

### QAIA-BOOK-API-002-e2 · A request without a usable credential is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. a client presenting "Bearer wrong"

**Action**

3. they POST /api/appointments with a valid body for slot "S1"

**Expected result**

4. the response status is 401

### QAIA-BOOK-API-002-e3 · A request without a usable credential is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. a client presenting "Basic dXNlcg=="

**Action**

3. they POST /api/appointments with a valid body for slot "S1"

**Expected result**

4. the response status is 401

### QAIA-BOOK-API-003-e1 · Omitting a required field is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with "slotId" omitted

**Expected result**

4. the response status is 400
5. the response body names the field "slotId"

### QAIA-BOOK-API-003-e2 · Omitting a required field is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with "patientId" omitted

**Expected result**

4. the response status is 400
5. the response body names the field "patientId"

### QAIA-BOOK-API-003-e3 · Omitting a required field is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with "specialty" omitted

**Expected result**

4. the response status is 400
5. the response body names the field "specialty"

### QAIA-BOOK-API-004-e1 · Every declared specialty is accepted

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with specialty "general"

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-004-e2 · Every declared specialty is accepted

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with specialty "pediatrics"

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-004-e3 · Every declared specialty is accepted

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with specialty "cardiology"

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-004-e4 · Every declared specialty is accepted

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with specialty "dermatology"

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-005 · A specialty outside the enumeration is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with specialty "oncology"

**Expected result**

4. the response status is 400
5. the response body names the field "specialty"

### QAIA-BOOK-API-006 · A property the schema does not declare is refused

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with an undeclared property "priority"

**Expected result**

4. the response status is 400
5. the response body names the field "priority"

### QAIA-BOOK-API-007 · A note of exactly 280 characters is accepted

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Technique: boundary values

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with a note of 280 characters

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-008 · A note of 281 characters is refused

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Refusal path · Technique: boundary values

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with a note of 281 characters

**Expected result**

4. the response status is 400
5. the response body names the field "note"

### QAIA-BOOK-API-009 · A startsAt that is not a date-time is refused

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with startsAt "next tuesday"

**Expected result**

4. the response status is 400
5. the response body names the field "startsAt"

### QAIA-BOOK-API-010 · A field of the wrong type is refused

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with slotId as the number 42

**Expected result**

4. the response status is 400
5. the response body names the field "slotId"

### QAIA-BOOK-API-011 · A slot already taken is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. slot "S1" is already booked
3. an authenticated patient

**Action**

4. they POST /api/appointments with a valid body for slot "S1"

**Expected result**

5. the response status is 409

### QAIA-BOOK-API-012 · A patient who already has three upcoming appointments is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: boundary values · Rests on an unanswered question

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. patient "P1" already has 3 upcoming appointments
3. an authenticated patient

**Action**

4. they POST /api/appointments for patient "P1" on slot "S9"

**Expected result**

5. the response status is 422

### QAIA-BOOK-API-013 · A patient who has two upcoming appointments is accepted

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Technique: boundary values · Rests on an unanswered question

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. patient "P1" already has 2 upcoming appointments
3. an authenticated patient

**Action**

4. they POST /api/appointments for patient "P1" on slot "S9"

**Expected result**

5. the response status is 201

### QAIA-BOOK-API-014 · A slot starting in less than two hours is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: boundary values · Rests on an unanswered question

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with startsAt "2026-08-11T09:59:00Z"

**Expected result**

4. the response status is 422

### QAIA-BOOK-API-015 · A slot starting in exactly two hours is accepted

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Technique: boundary values · Rests on an unanswered question

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with startsAt "2026-08-11T10:00:00Z"

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-016 · A request omitting startsAt entirely is accepted

Requirement: AC1 · Priority: 3 · Level: API (service contract) · Technique: equivalence partitioning · Rests on an unanswered question

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments without startsAt

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-017 · An identifier conforming to the declared UUID format is accepted

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with a slotId in UUID form

**Expected result**

4. the response status is 201

### QAIA-BOOK-API-018 · An identifier that is not a UUID is refused

Requirement: AC1 · Priority: 1 (highest) · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with slotId "not-a-uuid"

**Expected result**

4. the response status is 400
5. the response body names the field "slotId"

### QAIA-BOOK-API-019 · A request with no body at all is refused

Requirement: AC1 · Priority: 2 · Level: API (service contract) · Refusal path · Technique: equivalence partitioning

**Preconditions**

1. the booking API is reset with no appointment and the clock at "2026-08-11T08:00:00Z"
2. an authenticated patient

**Action**

3. they POST /api/appointments with no body

**Expected result**

4. the response status is 400

