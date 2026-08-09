# US-001 — Book a teleconsultation appointment

> **Pilot copy.** Original synthetic content (clean-room), MIT-licensed. Domain: health, patient portal.
>
> This file is the story **as a real ticket would reach you** — nothing more.
>
> Read it as you would any ticket that landed in your queue. What to produce, where to send it and
> who answers your questions are in `docs/PILOT-KIT.md`; everything you need about the *story* is
> below.

## User story

**As a** registered patient,
**I want** to book a teleconsultation slot with a practitioner of a chosen specialty,
**so that** I can get a consultation without traveling to the clinic.

## Acceptance criteria

1. The patient can only see slots of practitioners whose specialty matches the selected specialty filter.
2. Only slots starting at least 2 hours in the future can be booked.
3. A patient cannot hold more than 3 upcoming teleconsultation appointments at the same time.
4. Booking a slot makes it immediately unavailable to other patients; if two patients attempt the same slot, only the first confirmed booking succeeds and the other patient is informed the slot is gone.
5. On successful booking, the patient receives a confirmation containing the practitioner's name, date/time in the patient's timezone, and a connection link.
6. A patient can cancel an upcoming appointment up to 4 hours before its start; later cancellation is refused with an explanatory message.
7. Patients flagged as minors can only book with practitioners authorized for minors, and the confirmation is also sent to the legal guardian's contact.
8. All booking and cancellation events are recorded in an audit trail (who, what, when).
