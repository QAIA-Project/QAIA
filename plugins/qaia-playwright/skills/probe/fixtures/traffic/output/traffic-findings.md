# traffic-replay findings -- fixture/demo-traffic.har

Entries parsed: 8 | Conditions derived: 7

## PII/secret masking summary (type -> placeholder -> count, no ledger, D37)

| Type | Placeholder | Count |
|---|---|---|
| auth-header | `[REDACTED:auth-header]` | 7 |
| card | `[REDACTED:card]` | 1 |
| cookie | `[REDACTED:cookie]` | 3 |
| email | `[REDACTED:email]` | 2 |
| name | `[REDACTED:name]` | 2 |
| phone | `[REDACTED:phone]` | 1 |
| query-token | `[REDACTED:query-token]` | 1 |
| secret | `[REDACTED:secret]` | 2 |

## Conditions

| ID | Method | Path | Query params | Samples | Status(es) | Response shape (keys:type) | Timing (ms) |
|---|---|---|---|---|---|---|---|
| @QAIA-TRAFFIC-001 | POST | /api/login | - | 1 *(single sample)* | 200 (1/1) | token:string, userId:number, email:string | 182 |
| @QAIA-TRAFFIC-002 | GET | /api/tasks | - | 1 *(single sample)* | 200 (1/1) | tasks:array, total:number | 95 |
| @QAIA-TRAFFIC-003 | GET | /api/tasks | status,token | 1 *(single sample)* | 200 (1/1) | tasks:array, total:number | 88 |
| @QAIA-TRAFFIC-004 | POST | /api/tasks | - | 1 *(single sample)* | 201 (1/1) | id:number, title:string, done:boolean, assignee:string | 140 |
| @QAIA-TRAFFIC-005 | GET | /api/tasks/1 | - | 2 | 200 (2/2) | id:number, title:string, done:boolean | 40, 250 |
| @QAIA-TRAFFIC-006 | DELETE | /api/tasks/999 | - | 1 *(single sample)* | 404 (1/1) | error:string | 30 |
| @QAIA-TRAFFIC-007 | POST | /api/checkout | - | 1 *(single sample)* | 200 (1/1) | status:string, transactionId:string | 310 |

## Known limitations of this run (stated, not hidden)
- Name detection is heuristic and key-based only; a name outside a matched JSON key is not caught.
- Card detection is Luhn-checksum + digit-length based; edge cases are possible (see SKILL.md Guardrails).
- National ID / SSN patterns are not covered in v1.
- Path-template inference (`/api/tasks/{id}`) is deliberately not performed (see SKILL.md Method step 3) -- each literal path is its own signature.
