## Summary

`POST /booking` returns **500 Internal Server Error** when the request body is missing required fields, where a 4xx would be expected. A malformed client request is answered as a server fault.

I am aware this API is a deliberate practice target and that some of its behaviour is teaching material. If this one is intentional, please close — I looked for an existing report and an explanatory note first and did not find either.

## Reproduction (2026-08-11, `restful-booker.herokuapp.com`)

```
$ curl -i -X POST https://restful-booker.herokuapp.com/booking \
    -H 'Content-Type: application/json' -d '{}'

HTTP/1.1 500 Internal Server Error
Content-Type: text/plain; charset=utf-8
Content-Length: 21
X-Powered-By: Express
```

Same result with a partially populated body:

```
$ curl -i -X POST https://restful-booker.herokuapp.com/booking \
    -H 'Content-Type: application/json' -d '{"firstname":"X"}'

HTTP/1.1 500 Internal Server Error
```

A complete body works as documented and returns `200` with the created booking.

## Expected

A body that fails the documented requirements is a client error: **`400`**, ideally naming the missing field. The apidoc documents `CreateBooking` with `firstname`, `lastname`, `totalprice`, `depositpaid` and `bookingdates` as non-optional, so the server already holds everything it needs to reject the request deliberately.

## Why it is worth a line, beyond the status number

A 5xx is not just a wrong number — it is a different **class** of signal, and infrastructure reacts to the class rather than the code:

- retry-on-5xx clients will re-send a request that can never succeed;
- alerting and error-budget dashboards count it as a service fault;
- rate limiters and WAFs treat 4xx and 5xx differently.

For an API whose purpose is to teach API testing, this also means a learner writing `expect(status).toBe(400)` — the reasonable assertion — gets a red test for the right expectation.

## Good news, checked rather than assumed

**The response body leaks nothing.** It is 21 bytes of `text/plain`, no stack trace, no framework internals, no path. I checked specifically because a 500 on malformed input is a common place for that to happen. Only the status class is wrong.

## Related, and possibly the same root cause — but I have not established that

`POST /auth` with wrong credentials also answers **`200 OK`**, with `{"reason":"Bad credentials"}` in the body:

```
$ curl -i -X POST https://restful-booker.herokuapp.com/auth \
    -H 'Content-Type: application/json' -d '{"username":"admin","password":"wrong"}'

HTTP/1.1 200 OK
{"reason":"Bad credentials"}
```

A client checking `response.ok` treats a refused authentication as a success. I am mentioning it here rather than opening a second issue because both look like the same underlying habit — the outcome is carried in the body and the status is not load-bearing — but I have not read the source, so treat that as a guess, not a diagnosis. Happy to split it out if you would rather track them separately.

## Environment

`restful-booker.herokuapp.com`, 2026-08-11, plain `curl`. Read-only apart from the documented `POST /booking` calls above; nothing was updated or deleted.

<sub>Found while using this API as a practice target for an open-source QA tooling project — deriving test conditions from the published apidoc, then executing them. Thanks for keeping this running; it is a genuinely useful thing to have.</sub>
