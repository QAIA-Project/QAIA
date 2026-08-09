// Shared API helpers for declarative precondition seeding (T3/T4) — used by both the API
// spec and the E2E spec, which sets up state via the API and only exercises the SUT's UI
// for the actual step under test (atomic scenarios, no UI-chained setup).
async function apiLogin(request, baseURL, email, password = 'demo1234') {
  const r = await request.post(baseURL + '/api/login', { data: { email, password } });
  // Echouer ici, et le dire. Rendre `null` en silence produisait `Authorization: Bearer null`
  // et faisait echouer chaque assertion en aval sur un 401 qui se lisait comme un defaut
  // d'autorisation du SUT : le diagnostic coutait plus cher que le defaut (B4).
  if (!r.ok()) {
    throw new Error(`apiLogin: ${email} n'a pas pu s'authentifier (HTTP ${r.status()}) — `
      + `la demo tourne-t-elle sur ${baseURL} ? Corps : ${(await r.text()).slice(0, 200)}`);
  }
  return (await r.json()).token;
}

async function apiCreateDraft(request, baseURL, token, { currency = 'EUR', lines }) {
  const created = await request.post(baseURL + '/api/reports', { headers: { Authorization: 'Bearer ' + token } });
  // Les deux reponses etaient ignorees : un non-2xx a la creation faisait planter la
  // destructuration sur `undefined` (TypeError illisible), et l'echec du PUT passait
  // totalement inapercu -- le test continuait sur un brouillon vide (B5).
  if (!created.ok()) {
    throw new Error(`apiCreateDraft: creation refusee (HTTP ${created.status()}) — `
      + `${(await created.text()).slice(0, 200)}`);
  }
  const { report } = await created.json();
  const updated = await request.put(baseURL + '/api/reports/' + report.id, { headers: { Authorization: 'Bearer ' + token }, data: { currency, lines } });
  if (!updated.ok()) {
    throw new Error(`apiCreateDraft: amorcage des lignes refuse (HTTP ${updated.status()}) — `
      + `${(await updated.text()).slice(0, 200)}`);
  }
  return report.id;
}

async function apiSubmit(request, baseURL, token, id) {
  return request.post(baseURL + '/api/reports/' + id + '/submit', { headers: { Authorization: 'Bearer ' + token } });
}

async function apiCreateSubmittedReport(request, baseURL, token, opts) {
  const id = await apiCreateDraft(request, baseURL, token, opts);
  const r = await apiSubmit(request, baseURL, token, id);
  return { id, submitResponse: r };
}

async function apiDecide(request, baseURL, token, id, decision, comment) {
  return request.post(baseURL + '/api/reports/' + id + '/decide', { headers: { Authorization: 'Bearer ' + token }, data: { decision, comment } });
}

// La suite melangeait deux references temporelles : des dates relatives (« il y a 91 jours »,
// robustes) et des dates absolues imposees par la table de change du SUT (2026-07-21/25, qui
// perimaient le 2026-10-20). Figer l'horloge du serveur sans figer celle des tests aurait
// simplement deplace la bombe. Les deux cotes lisent maintenant DEMO_NOW quand il est pose,
// et l'horloge reelle sinon -- le comportement par defaut est inchange (B3).
const CLOCK = () => (process.env.DEMO_NOW ? Date.parse(process.env.DEMO_NOW) : Date.now());
function daysAgoISO(n) { return new Date(CLOCK() - n * 24 * 3600 * 1000).toISOString().slice(0, 10); }
function todayISO() { return daysAgoISO(0); }

module.exports = { apiLogin, apiCreateDraft, apiSubmit, apiCreateSubmittedReport, apiDecide, daysAgoISO, todayISO };
