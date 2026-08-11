// Généré par qaia-playwright:automate depuis
// ../qaia-journey/testbooks/BOOK-API/appointments.feature — un bloc par scénario, le titre
// portant l'identifiant QAIA et l'AC, comme la traçabilité l'exige.
//
// Chaque test affirme le STATUT en premier, puis le corps, puis les en-têtes — l'ordre du
// scénario (qaia-core:testbook-generate/references/api-steps.md). Un test API dont la seule
// assertion porte sur un champ du corps passe sur un 500 qui renvoie du JSON.
const { test, expect } = require('@playwright/test');

const NOW = '2026-08-11T08:00:00Z';
const TOKEN = { Authorization: 'Bearer valid-token' };
const VALID = { slotId: 'S1', patientId: 'P1', specialty: 'cardiology', startsAt: '2026-08-12T09:00:00Z' };

async function reset(request, appointments = []) {
  const res = await request.post('/test/reset', { data: { appointments, now: NOW } });
  expect(res.status(), 'le harnais de remise à zéro doit répondre 204').toBe(204);
}

const upcoming = (n, patientId = 'P1') =>
  Array.from({ length: n }, (_, i) => ({
    id: `seed-${i}`,
    slotId: `SEED-${i}`,
    patientId,
    specialty: 'general',
    startsAt: '2026-08-20T09:00:00Z',
  }));

test.beforeEach(async ({ request }) => {
  await reset(request);
});

test('@QAIA-BOOK-API-001 @AC1 a valid request creates the appointment', async ({ request }) => {
  const res = await request.post('/api/appointments', { headers: TOKEN, data: VALID });
  expect(res.status()).toBe(201);
  const body = await res.json();
  expect(body.id, "le corps porte l'identifiant du rendez-vous créé").toBeTruthy();
  expect(res.headers()['location']).toBe(`/api/appointments/${body.id}`);
});

for (const credential of ['no header', 'Bearer wrong', 'Basic dXNlcg==']) {
  test(`@QAIA-BOOK-API-002 @AC1 a request presenting "${credential}" is refused`, async ({ request }) => {
    const headers = credential === 'no header' ? {} : { Authorization: credential };
    const res = await request.post('/api/appointments', { headers, data: VALID });
    expect(res.status()).toBe(401);
  });
}

for (const field of ['slotId', 'patientId', 'specialty']) {
  test(`@QAIA-BOOK-API-003 @AC1 omitting "${field}" is refused`, async ({ request }) => {
    const data = { ...VALID };
    delete data[field];
    const res = await request.post('/api/appointments', { headers: TOKEN, data });
    expect(res.status()).toBe(400);
    // Le scénario dit « names the field » : asserter le seul statut laisserait passer un 400
    // générique qui ne dit pas au client ce qu'il a manqué.
    expect((await res.json()).field).toBe(field);
  });
}

for (const specialty of ['general', 'pediatrics', 'cardiology', 'dermatology']) {
  test(`@QAIA-BOOK-API-004 @AC1 specialty "${specialty}" is accepted`, async ({ request }) => {
    const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, specialty } });
    expect(res.status()).toBe(201);
  });
}

test('@QAIA-BOOK-API-005 @AC1 a specialty outside the enumeration is refused', async ({ request }) => {
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, specialty: 'oncology' } });
  expect(res.status()).toBe(400);
  expect((await res.json()).field).toBe('specialty');
});

test('@QAIA-BOOK-API-006 @AC1 an undeclared property is refused', async ({ request }) => {
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, priority: 'high' } });
  expect(res.status()).toBe(400);
  expect((await res.json()).field).toBe('priority');
});

test('@QAIA-BOOK-API-007 @AC1 a note of exactly 280 characters is accepted', async ({ request }) => {
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, note: 'x'.repeat(280) } });
  expect(res.status()).toBe(201);
});

test('@QAIA-BOOK-API-008 @AC1 a note of 281 characters is refused', async ({ request }) => {
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, note: 'x'.repeat(281) } });
  expect(res.status()).toBe(400);
  expect((await res.json()).field).toBe('note');
});

test('@QAIA-BOOK-API-009 @AC1 a startsAt that is not a date-time is refused', async ({ request }) => {
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, startsAt: 'next tuesday' } });
  expect(res.status()).toBe(400);
  expect((await res.json()).field).toBe('startsAt');
});

test('@QAIA-BOOK-API-010 @AC1 a field of the wrong type is refused', async ({ request }) => {
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, slotId: 42 } });
  expect(res.status()).toBe(400);
  expect((await res.json()).field).toBe('slotId');
});

test('@QAIA-BOOK-API-011 @AC1 a slot already taken is refused', async ({ request }) => {
  await reset(request, [{ id: 'seed', slotId: 'S1', patientId: 'PX', specialty: 'general', startsAt: '2026-08-20T09:00:00Z' }]);
  const res = await request.post('/api/appointments', { headers: TOKEN, data: VALID });
  expect(res.status()).toBe(409);
});

test('@QAIA-BOOK-API-012 @AC1 @low-confidence a patient with three upcoming appointments is refused', async ({ request }) => {
  // open: Q1 — le plafond ne vit que dans la prose de la description du 422. Défaut sûr appliqué.
  await reset(request, upcoming(3));
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, slotId: 'S9' } });
  expect(res.status()).toBe(422);
});

test('@QAIA-BOOK-API-013 @AC1 @low-confidence a patient with two upcoming appointments is accepted', async ({ request }) => {
  // open: Q1 — intérieur de la même borne non déclarée.
  await reset(request, upcoming(2));
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, slotId: 'S9' } });
  expect(res.status()).toBe(201);
});

test('@QAIA-BOOK-API-014 @AC1 @low-confidence a slot starting in less than two hours is refused', async ({ request }) => {
  // open: Q1 — délai minimal en prose, absent du schéma.
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, startsAt: '2026-08-11T09:59:00Z' } });
  expect(res.status()).toBe(422);
});

test('@QAIA-BOOK-API-015 @AC1 @low-confidence a slot starting in exactly two hours is accepted', async ({ request }) => {
  // open: Q1 — la borne est écrite « < 2h », donc exactement 2h est à l'intérieur.
  const res = await request.post('/api/appointments', { headers: TOKEN, data: { ...VALID, startsAt: '2026-08-11T10:00:00Z' } });
  expect(res.status()).toBe(201);
});

test('@QAIA-BOOK-API-016 @AC1 @low-confidence a request omitting startsAt is accepted', async ({ request }) => {
  // open: Q2 — startsAt est optionnel alors que la règle des deux heures en dépend.
  const data = { ...VALID };
  delete data.startsAt;
  const res = await request.post('/api/appointments', { headers: TOKEN, data });
  expect(res.status()).toBe(201);
});
