// Fixtures des scenarios @api (restful-booker). Aucun navigateur n'est lance ici.
const base = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.RB_BASE_URL || 'https://restful-booker.herokuapp.com';
// Justificatifs publics du bac a sable, publies par sa propre documentation. Pas un secret :
// un secret ne serait jamais commite (regle "secrets and environments").
const CREDENTIALS = {
  username: process.env.RB_USERNAME || 'admin',
  password: process.env.RB_PASSWORD || 'password123',
};

/**
 * Empreinte reseau : la consigne de campagne interdit toute charge. On COMPTE les requetes
 * plutot que de l'affirmer, et le total est ecrit sur disque a la fin du run.
 */
const COUNT_FILE = path.join(__dirname, 'request-count.json');
let requestCount = 0;
process.on('exit', () => {
  if (requestCount === 0) return;
  // Playwright redemarre le processus worker apres CHAQUE echec (retries: 0). Un simple
  // compteur en memoire est donc remis a zero plusieurs fois par run et le fichier ecrit par
  // le dernier worker ne represente qu'une fraction du trafic. On cumule : lire, ajouter,
  // reecrire. (Constate sur ce run meme : 10 requetes annoncees pour 55 tests.)
  let previous = { httpRequests: 0, workers: 0 };
  try { previous = JSON.parse(fs.readFileSync(COUNT_FILE, 'utf8')); } catch { /* premier worker */ }
  fs.writeFileSync(COUNT_FILE, JSON.stringify({
    target: BASE_URL,
    httpRequests: (previous.httpRequests || 0) + requestCount,
    workers: (previous.workers || 0) + 1,
    at: new Date().toISOString(),
  }, null, 2));
});

function counting(ctx) {
  const wrap = (method) => (...args) => { requestCount += 1; return ctx[method](...args); };
  return {
    get: wrap('get'), post: wrap('post'), put: wrap('put'),
    patch: wrap('patch'), delete: wrap('delete'), fetch: wrap('fetch'),
    raw: ctx,
  };
}

/**
 * Corps de reservation de reference.
 * PROVENANCE : les sept champs obligatoires declares par le contrat apidoc de CreateBooking,
 * repris de `21-restfulbooker.feature`. Les valeurs sont arbitraires et propres au test
 * (`marker` rend la reservation retrouvable par filtre sans collision avec celles d'autrui).
 */
function bookingPayload(overrides = {}) {
  const marker = `QAIA${Date.now()}${Math.floor(Math.random() * 1000)}`;
  return {
    firstname: marker,
    lastname: 'Testeur',
    totalprice: 111,
    depositpaid: true,
    bookingdates: { checkin: '2018-01-01', checkout: '2019-01-01' },
    additionalneeds: 'Breakfast',
    ...overrides,
  };
}

/** Retire un champ, y compris imbrique ("bookingdates.checkin"), sans muter l'original. */
function omit(payload, dottedPath) {
  const copy = JSON.parse(JSON.stringify(payload));
  const parts = dottedPath.split('.');
  let node = copy;
  for (const p of parts.slice(0, -1)) node = node[p];
  delete node[parts[parts.length - 1]];
  return copy;
}

const SEVEN_FIELDS = ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates', 'additionalneeds'];

const test = base.test.extend({
  api: [async ({ playwright }, use) => {
    const ctx = await playwright.request.newContext({ baseURL: BASE_URL });
    await use(counting(ctx));
    await ctx.dispose();
  }, { scope: 'worker' }],

  /** Un seul jeton pour tout le worker : le renouveler par test serait du bruit reseau pur. */
  token: [async ({ api }, use) => {
    const res = await api.post('/auth', { data: CREDENTIALS });
    const body = await res.json();
    await use(body.token);
  }, { scope: 'worker' }],

  /**
   * Precondition atomique et declarative : chaque test qui MUTE une reservation cree la
   * sienne par l'API, jamais en enchainant des appels d'un autre test.
   */
  booking: async ({ api }, use) => {
    const payload = bookingPayload();
    const res = await api.post('/booking', { data: payload });
    const body = await res.json();
    await use({ id: body.bookingid, payload });
  },

  /**
   * Reservation partagee par les scenarios STRICTEMENT EN LECTURE. Le partage est un choix
   * assume pour borner l'empreinte reseau sur un service public tiers (consigne de campagne) :
   * aucun de ces tests n'ecrit, donc il n'y a pas d'etat mutable partage a serialiser.
   */
  readOnlyBooking: [async ({ api }, use) => {
    const payload = bookingPayload();
    const res = await api.post('/booking', { data: payload });
    const body = await res.json();
    await use({ id: body.bookingid, payload });
  }, { scope: 'worker' }],
});

module.exports = {
  test, expect: base.expect,
  CREDENTIALS, BASE_URL, bookingPayload, omit, SEVEN_FIELDS,
};
