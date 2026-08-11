Still reproduces on the hosted instance today (2026-08-11), five months after this was closed as completed — so this may be a regression rather than a stale report.

**Reproduction, just now:**

```
$ curl -s -X POST https://restful-booker.herokuapp.com/booking \
    -H 'Content-Type: application/json' \
    -d '{"firstname":"Filt","lastname":"Probe2708","totalprice":1,"depositpaid":false,
         "bookingdates":{"checkin":"2027-07-08","checkout":"2027-07-09"}}'
{"bookingid":7485,"booking":{...,"bookingdates":{"checkin":"2027-07-08","checkout":"2027-07-09"}}}

$ curl -s 'https://restful-booker.herokuapp.com/booking?lastname=Probe2708'
[{"bookingid":7485}]          <- the name filter finds it

$ curl -s 'https://restful-booker.herokuapp.com/booking?checkin=2027-07-08'
[]                            <- the date filter does not
```

The useful detail for whoever picks this up: **`firstname` and `lastname` filter correctly on the same booking**, so the query-string plumbing works and the problem is specific to the date comparison. That is a narrower target than the original report could offer.

Environment: `restful-booker.herokuapp.com`, 2026-08-11, plain `curl`, no auth (none required for `GET /booking`).

Happy to leave this here rather than open a duplicate — reopening or not is your call. If the fix landed only in the Docker image (`Restful-Booker-Platform`) and the hosted instance is running an older build, that is itself worth knowing for anyone using the hosted API to practise against, since the documented filter is one of the first things a learner tries.

<sub>Found while using this API as a practice target for an open-source QA tooling project (deriving test conditions from the published apidoc, then executing them). Read-only checks plus the one booking created above; nothing was modified or deleted.</sub>
