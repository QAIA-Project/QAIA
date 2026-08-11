#!/usr/bin/env node
// MediBook Booking API — demonstration server for the QAIA API level (S39).
//
// It implements `sources/booking-api.openapi.yaml`, a specification written on 2026-07-25 for
// `oracle-generate`'s project-oracle demo — seventeen days before this server existed. The test
// book was derived from that document and never from this file: that is the whole point of the
// API entry point (`openapi-ingest`), and reading the code to write the tests would have copied
// whatever this file gets wrong.
//
// No dependency, no framework: `node app/server.js`. In-memory state, reset between tests.
'use strict';

const http = require('http');

const PORT = Number(process.env.PORT || 4600);
const TOKEN = 'valid-token';
const SPECIALTIES = ['general', 'pediatrics', 'cardiology', 'dermatology'];
const ALLOWED = ['slotId', 'patientId', 'specialty', 'startsAt', 'note'];
const REQUIRED = ['slotId', 'patientId', 'specialty'];
// `format: uuid` est declare sur slotId et patientId par le contrat. Le serveur ne l'appliquait
// pas : un identifiant quelconque etait accepte. Trouve le 2026-08-11 par le scenario
// QAIA-BOOK-API-018, ajoute apres qu'une relecture ait releve que le cahier traitait
// `format: date-time` comme contraignant et `format: uuid` comme decoratif -- le meme mot-cle du
// meme schema, lu dans deux sens opposes. La question tranchee (Q4), la clause s'applique.
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const UUID_FIELDS = ['slotId', 'patientId'];
const MAX_UPCOMING = 3;
const MIN_LEAD_MS = 2 * 60 * 60 * 1000; // "< 2h ahead" — responses.422 of the spec

// `now` is injectable so the 2-hour rule is testable without sleeping or depending on the clock
// of whoever runs the suite. Same reason `DEMO_NOW` exists in the expense demo's Makefile.
let state = { appointments: [], now: null };

const nowMs = () => (state.now === null ? Date.now() : state.now);

function reset(body) {
  state = {
    appointments: Array.isArray(body && body.appointments) ? body.appointments : [],
    now: body && typeof body.now === 'string' ? Date.parse(body.now) : null,
  };
}

function send(res, status, payload) {
  const body = payload === undefined ? '' : JSON.stringify(payload);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

// Returns null when the body satisfies the schema, or the name of the first violated clause.
// The message names the field, because a 400 that does not say what is wrong is a 400 the caller
// has to guess at — and the test book asserts on the named field, not only on the status.
function validate(body) {
  if (body === null || typeof body !== 'object' || Array.isArray(body)) {
    return { field: 'body', reason: 'expected a JSON object' };
  }
  for (const key of Object.keys(body)) {
    if (!ALLOWED.includes(key)) return { field: key, reason: 'additionalProperties: false' };
  }
  for (const key of REQUIRED) {
    if (!(key in body)) return { field: key, reason: 'required' };
  }
  for (const key of ['slotId', 'patientId', 'specialty']) {
    if (typeof body[key] !== 'string') return { field: key, reason: 'type: string' };
  }
  if (!SPECIALTIES.includes(body.specialty)) {
    return { field: 'specialty', reason: 'enum' };
  }
  for (const key of UUID_FIELDS) {
    if (!UUID_RE.test(body[key])) return { field: key, reason: 'format: uuid' };
  }
  if ('note' in body) {
    if (typeof body.note !== 'string') return { field: 'note', reason: 'type: string' };
    if (body.note.length > 280) return { field: 'note', reason: 'maxLength: 280' };
  }
  if ('startsAt' in body) {
    if (typeof body.startsAt !== 'string' || Number.isNaN(Date.parse(body.startsAt))) {
      return { field: 'startsAt', reason: 'format: date-time' };
    }
  }
  return null;
}

const server = http.createServer((req, res) => {
  let raw = '';
  req.on('data', (chunk) => {
    raw += chunk;
    if (raw.length > 1e6) req.destroy();
  });
  req.on('end', () => {
    // Test-support surface, deliberately OUTSIDE the contract: it exists so each test can seed
    // its own state declaratively instead of chaining requests to reach a precondition — the
    // controllability `automate`'s testability precheck looks for. It is not part of the API
    // under test and no scenario asserts on it.
    // Sonde de démarrage, hors contrat elle aussi : le lanceur doit savoir que le serveur écoute
    // avant de commencer, et le faire deviner par une requête métier mélangerait les deux.
    if (req.method === 'GET' && req.url === '/health') {
      return send(res, 200, { status: 'up' });
    }

    if (req.method === 'POST' && req.url === '/test/reset') {
      let parsed = {};
      try { parsed = raw ? JSON.parse(raw) : {}; } catch (_) { parsed = {}; }
      reset(parsed);
      return send(res, 204);
    }

    if (req.method !== 'POST' || req.url !== '/api/appointments') {
      return send(res, 404, { error: 'not found' });
    }

    // Order is the contract's own: authentication before shape, shape before conflict,
    // conflict before business rule. A server that validated the body first would leak the
    // existence of a slot to an unauthenticated caller.
    const auth = req.headers.authorization || '';
    if (auth !== `Bearer ${TOKEN}`) {
      return send(res, 401, { error: 'unauthenticated' });
    }

    let body;
    try {
      body = JSON.parse(raw || 'null');
    } catch (_) {
      return send(res, 400, { error: 'malformed body', field: 'body' });
    }

    const invalid = validate(body);
    if (invalid) {
      return send(res, 400, { error: `invalid ${invalid.field}`, field: invalid.field, clause: invalid.reason });
    }

    if (state.appointments.some((a) => a.slotId === body.slotId)) {
      return send(res, 409, { error: 'slot already taken', field: 'slotId' });
    }

    const upcoming = state.appointments.filter(
      (a) => a.patientId === body.patientId && Date.parse(a.startsAt) > nowMs()
    ).length;
    if (upcoming >= MAX_UPCOMING) {
      return send(res, 422, { error: 'too many upcoming appointments', rule: 'max-upcoming' });
    }

    if ('startsAt' in body && Date.parse(body.startsAt) - nowMs() < MIN_LEAD_MS) {
      return send(res, 422, { error: 'starts too soon', rule: 'min-lead-time' });
    }

    const appointment = {
      id: `apt-${state.appointments.length + 1}`,
      slotId: body.slotId,
      patientId: body.patientId,
      specialty: body.specialty,
      startsAt: body.startsAt || null,
    };
    state.appointments.push(appointment);
    res.writeHead(201, {
      'Content-Type': 'application/json',
      Location: `/api/appointments/${appointment.id}`,
    });
    res.end(JSON.stringify(appointment));
  });
});

server.listen(PORT, () => {
  console.log(`booking-api-demo listening on http://127.0.0.1:${PORT}`);
});
