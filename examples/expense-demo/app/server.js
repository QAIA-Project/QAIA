// ExpenseFlow — minimal but realistic expense-report approval workflow (SUT for QAIA).
// Implements the US-004 acceptance criteria so generated tests have a real target.
// No external deps: Node http only. Deterministic in-memory store, reset per boot.
// Domain: finance/HR (non-medical) — companion SUT to examples/medibook (US-001, medical).
const http = require('http');
const fs = require('fs');
const path = require('path');

// Horloge injectable. Les taux de change de cette demo sont des fixtures datees : sans
// cette couture, tout test qui les utilise porte une date de peremption -- cinq d'entre eux
// viraient au rouge le 2026-10-20 sans qu'une ligne de code ait bouge, et l'un avec le
// mauvais message d'erreur, ce qui est pire que rouge. Releve par la revue « developpeur »
// du 2026-08-09. En l'absence de DEMO_NOW le comportement est inchange.
const NOW = () => (process.env.DEMO_NOW ? Date.parse(process.env.DEMO_NOW) : Date.now());
const DAY = 24 * 3600 * 1000;

// --- ambiguity resolutions made explicit in code (full reasoning in
// qaia-journey/state/US-004/02-understanding.md — this block only summarizes the code-level effect) ---
// [open] Q1: thresholds are read as: <500 -> band A (1 approval), 500..5000 inclusive
//   both ends -> band B (manager+finance), >5000 -> band C (manager+finance+director).
//   i.e. exactly 500.00 and exactly 5000.00 both fall in band B. Flagged @low-confidence.
// [open] Q2: "skips straight to the next level up" is implemented as REPLACING the
//   submitter's own step by the next role up the fixed hierarchy (manager<finance<director),
//   not merely dropping it — see nextApproverRole() below for the full reasoning.
//   Flagged @low-confidence.
// [assumption] Q3: a `changes-requested` report that returns to `draft` CAN be edited and
//   re-submitted, but CANNOT be directly rejected from `draft` (rejection only happens from
//   `submitted`, per AC1's literal transition list — undeclared transitions are forbidden,
//   the standard state-machine reading). Flagged @low-confidence.
// [open]/[assumption] Q4: rate SOURCE is undefined by the US ([open] — a fixed synthetic
//   per-currency-per-date table is used here as a demo stand-in, no live network call). The
//   FALLBACK when no rate exists for the exact expense date (weekend/holiday gap simulated for
//   one seeded currency) is an [assumption]: the LAST available prior rate is used and the
//   report is flagged `rateStale: true` rather than blocking submission outright. Flagged
//   @low-confidence.

const FX = {
  // synthetic fixed rates to EUR, keyed by ISO date. USD has a deliberate gap (weekend) to
  // exercise Q4's stale-rate fallback.
  USD: { '2026-07-20': 0.92, '2026-07-21': 0.921, '2026-07-24': 0.919 }, // 2026-07-25/26 (weekend) missing on purpose
  GBP: { '2026-07-20': 1.17, '2026-07-21': 1.171, '2026-07-24': 1.169, '2026-07-25': 1.168 },
};

function fxRate(currency, isoDate) {
  if (currency === 'EUR') return { rate: 1, stale: false };
  const table = FX[currency];
  if (!table) return null; // unknown currency
  if (table[isoDate]) return { rate: table[isoDate], stale: false };
  // fallback: latest prior date with a rate (Q4 assumption)
  const dates = Object.keys(table).filter(d => d <= isoDate).sort();
  if (dates.length === 0) return null;
  return { rate: table[dates[dates.length - 1]], stale: true };
}

// --- AI/ML-style feature: expense category suggestion (#53) --------------------------------
// A simple, deterministic keyword-weighted classifier -- NOT a trained ML model, but it plays
// the same testing-relevant role: given free-text input, it infers a category + a confidence
// score without an exact expected output being directly statable from the input alone (the
// precondition CT-AI/metamorphic testing targets). Added specifically so istqb-design's CT-AI
// techniques (adversarial-input robustness, consistency/back-to-back, metamorphic relations)
// have a real, executable target in this repo instead of only living in prose (#53).
const CATEGORY_KEYWORDS = {
  travel: ['flight', 'flights', 'taxi', 'uber', 'train', 'hotel', 'airfare', 'mileage', 'parking'],
  meals: ['lunch', 'dinner', 'breakfast', 'restaurant', 'coffee', 'catering', 'meal'],
  office: ['stapler', 'paper', 'desk', 'chair', 'printer', 'supplies', 'furniture'],
  software: ['subscription', 'license', 'saas', 'software', 'app', 'cloud', 'hosting'],
};
function suggestCategory(description) {
  if (typeof description !== 'string') return { category: 'other', confidence: 0 };
  // adversarial-input guard: cap absurdly long input rather than let it degrade unboundedly
  // (CT-AI robustness expectation -- fail predictably, not silently or catastrophically).
  const text = description.slice(0, 2000).toLowerCase();
  const words = text.match(/[a-z]+/g) || [];
  const scores = {};
  for (const [cat, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    scores[cat] = words.filter(w => keywords.includes(w)).length;
  }
  let best = 'other', bestScore = 0;
  for (const [cat, score] of Object.entries(scores)) {
    if (score > bestScore) { best = cat; bestScore = score; }
  }
  const totalMatches = Object.values(scores).reduce((a, b) => a + b, 0);
  // confidence: fraction of matched keyword-words among all words, bounded (0, 1) -- a genuine
  // "can't state the exact number directly" output: it depends on both the matched-keyword
  // density AND total word count, not any single input field in isolation (metamorphic target).
  const confidence = words.length === 0 ? 0 : Math.round((totalMatches / words.length) * 100) / 100;
  return { category: best, confidence };
}

function freshState() {
  return {
    users: {
      'employee@demo': { pw: 'demo1234', role: 'employee', id: 'u1', manager: 'manager@demo', name: 'Elie Employee' },
      'manager@demo': { pw: 'demo1234', role: 'manager', id: 'u2', manager: 'finance@demo', name: 'Mona Manager' },
      // a manager who ALSO submits reports (AC3 self-approval / skip-level case)
      'finance@demo': { pw: 'demo1234', role: 'finance', id: 'u3', manager: 'director@demo', name: 'Fio Finance' },
      'director@demo': { pw: 'demo1234', role: 'director', id: 'u4', manager: null, name: 'Dara Director' },
    },
    reports: [], // {id, submitterId, status, currency, lines:[{category,amount,date,receipt}], total, totalEur, approvals:[], history:[]}
    audit: [],
    seq: 1,
  };
}
let db = freshState();
const tokens = {};

function audit(action, who, detail) { db.audit.push({ action, who, detail, at: NOW() }); }
function userById(id) { return Object.values(db.users).find(u => u.id === id); }
function json(res, code, obj) { res.writeHead(code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(obj)); }
function body(req) { return new Promise(r => { let d = ''; req.on('data', c => d += c); req.on('end', () => { try { r(JSON.parse(d || '{}')); } catch { r({}); } }); }); }
function authFrom(req) { const t = (req.headers.authorization || '').replace('Bearer ', ''); return tokens[t] ? { email: tokens[t], user: db.users[tokens[t]] } : null; }
function isoDaysAgo(n) { return new Date(NOW() - n * DAY).toISOString().slice(0, 10); }

// AC2: chain of approval roles required for a given EUR total (Q1 assumption: 500 & 5000 inclusive in band B)
function chainFor(totalEur) {
  if (totalEur < 500) return ['manager'];
  if (totalEur <= 5000) return ['manager', 'finance'];
  return ['manager', 'finance', 'director'];
}

// AC3: role of the person who must act next.
// Q2 assumption (planted ambiguity, "skips straight to the next level up"): when the
// submitter's own role sits inside the amount-based chain, that slot is REPLACED by the next
// role up the fixed hierarchy (manager < finance < director) rather than merely dropped — a
// manager submitting a <500 report (chain=[manager]) escalates straight to finance instead of
// being left with zero required approvers. If the escalated role is already required later in
// the chain, the self-slot is simply removed (chain shortens by one) — this is the reading
// that resolves both branches of the planted ambiguity consistently. Flagged @low-confidence.
const HIERARCHY = ['manager', 'finance', 'director'];
function nextApproverRole(report) {
  const chain = chainFor(report.totalEur).slice();
  const submitter = userById(report.submitterId);
  const idx = chain.indexOf(submitter.role);
  if (idx !== -1) {
    const escalated = HIERARCHY[HIERARCHY.indexOf(submitter.role) + 1];
    if (escalated && !chain.includes(escalated)) chain.splice(idx, 1, escalated);
    else chain.splice(idx, 1);
  }
  for (const role of chain) {
    if (report.approvals.some(a => a.role === role)) continue; // already done
    return role;
  }
  return null; // fully approved
}

function recomputeTotal(report) {
  let totalEur = 0; let rateStale = false; let error = null;
  for (const line of report.lines) {
    const fx = fxRate(report.currency, line.date);
    if (!fx) { error = 'no exchange rate available for ' + report.currency + ' on ' + line.date; break; }
    if (fx.stale) rateStale = true;
    totalEur += Math.round(line.amount * fx.rate * 100) / 100;
  }
  report.totalEur = Math.round(totalEur * 100) / 100;
  report.rateStale = rateStale;
  return error;
}

// [open] Q6 (02-understanding.md): AC5's "EUR 25" threshold is compared against the line's
// EUR-EQUIVALENT amount (converted at the line's own date, AC6), not its face value in the
// report's currency — a EUR-face-value reading would let a 30 USD line (~27.5 EUR) through
// without a receipt while a 24 EUR line would not. Flagged @low-confidence.
function validateLines(lines, currency) {
  for (const l of lines) {
    // Number.isFinite, not `typeof === 'number'`: CP-001 (contract-probe, 2026-08-01). JSON
    // parses 1e309 as Infinity, which IS a number and IS > 0, so it passed here — and then
    // serialised back to null, admitting a submitted report with a null amount and a null
    // total, i.e. inside the approval workflow with nothing to compare against AC2's
    // EUR500/EUR5000 thresholds. The same validator refused a literal null with a 422: two
    // identical end states, two opposite verdicts. NaN fails the same check for the same reason.
    if (!l.category || !Number.isFinite(l.amount) || l.amount <= 0 || !l.date) return 'each line needs a category, a positive amount and a date';
    const ageDays = Math.floor((NOW() - new Date(l.date + 'T00:00:00Z').getTime()) / DAY); // Q5: server clock (see 02-understanding.md)
    if (ageDays > 90) return 'line "' + l.category + '" dated ' + l.date + ' is more than 90 days old and is blocked at submission'; // AC4
    const fx = fxRate(currency, l.date);
    if (!fx) return 'no exchange rate available for ' + currency + ' on ' + l.date; // AC6
    const eurEquivalent = Math.round(l.amount * fx.rate * 100) / 100;
    if (eurEquivalent >= 25 && !l.receipt) return 'line "' + l.category + '" (EUR-equivalent ' + eurEquivalent + ' >= 25) requires an attached receipt'; // AC5, Q6
  }
  return null;
}

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://x');
  const p = u.pathname;

  if (p === '/api/reset' && req.method === 'POST') { db = freshState(); for (const k in tokens) delete tokens[k]; return json(res, 200, { ok: true }); }

  if (p === '/api/login' && req.method === 'POST') {
    const b = await body(req); const user = db.users[b.email];
    if (!user || user.pw !== b.password) { audit('login_failed', b.email, {}); return json(res, 401, { error: 'invalid credentials' }); }
    const tok = 'tok-' + (db.seq++); tokens[tok] = b.email; audit('login', b.email, {});
    return json(res, 200, { token: tok, role: user.role, name: user.name });
  }

  if (p === '/api/reports' && req.method === 'POST') { // create draft
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    const rpt = { id: 'r' + (db.seq++), submitterId: a.user.id, status: 'draft', currency: 'EUR', lines: [], approvals: [], history: [] };
    rpt.history.push({ event: 'created', who: a.email, at: NOW() });
    db.reports.push(rpt); audit('create_draft', a.email, { id: rpt.id });
    return json(res, 201, { report: rpt });
  }

  if (p.match(/^\/api\/reports\/[^/]+$/) && req.method === 'PUT') { // edit a draft (also used to re-edit changes-requested-turned-draft)
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    const id = p.split('/').pop();
    const rpt = db.reports.find(r => r.id === id);
    if (!rpt || rpt.submitterId !== a.user.id) return json(res, 404, { error: 'report not found' });
    if (rpt.status !== 'draft') return json(res, 409, { error: 'only a draft report can be edited' }); // AC7 (rejected is terminal, never draft again)
    const b = await body(req);
    if (b.currency) rpt.currency = b.currency;
    if (b.lines) rpt.lines = b.lines;
    return json(res, 200, { report: rpt });
  }

  if (p.match(/^\/api\/reports\/[^/]+\/submit$/) && req.method === 'POST') { // AC1 draft -> submitted
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    const id = p.split('/')[3];
    const rpt = db.reports.find(r => r.id === id);
    if (!rpt || rpt.submitterId !== a.user.id) return json(res, 404, { error: 'report not found' });
    if (rpt.status !== 'draft') return json(res, 409, { error: 'only a draft report can be submitted' });
    if (rpt.lines.length === 0) return json(res, 422, { error: 'a report needs at least one line item' });
    const lineErr = validateLines(rpt.lines, rpt.currency); // AC4 / AC5
    if (lineErr) return json(res, 422, { error: lineErr });
    const fxErr = recomputeTotal(rpt); // AC6
    if (fxErr) return json(res, 422, { error: fxErr });
    rpt.status = 'submitted';
    rpt.approvals = [];
    rpt.history.push({ event: 'submitted', who: a.email, at: NOW(), totalEur: rpt.totalEur, rateStale: rpt.rateStale });
    audit('submit', a.email, { id: rpt.id, totalEur: rpt.totalEur });
    return json(res, 200, { report: rpt });
  }

  if (p.match(/^\/api\/reports\/[^/]+\/decide$/) && req.method === 'POST') { // AC2/AC3 approve|reject|changes-requested
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    const id = p.split('/')[3];
    const rpt = db.reports.find(r => r.id === id);
    if (!rpt) return json(res, 404, { error: 'report not found' });
    if (rpt.status !== 'submitted') return json(res, 409, { error: 'only a submitted report can be decided' }); // covers AC7 (rejected terminal) and Q3
    const b = await body(req); // { decision: 'approve'|'reject'|'changes-requested', comment }
    if (rpt.submitterId === a.user.id) return json(res, 403, { error: 'cannot approve your own report' }); // AC3
    const expectedRole = nextApproverRole(rpt);
    if (!expectedRole) return json(res, 409, { error: 'report already fully approved' });
    if (a.user.role !== expectedRole) return json(res, 403, { error: 'report awaits approval from: ' + expectedRole }); // AC2/AC3 chain order
    if ((b.decision === 'reject' || b.decision === 'changes-requested') && (!b.comment || b.comment.trim().length < 10)) {
      return json(res, 422, { error: 'a comment of at least 10 characters is required for this decision' }); // AC8
    }
    if (b.decision === 'approve') {
      rpt.approvals.push({ role: a.user.role, who: a.email, at: NOW() });
      rpt.history.push({ event: 'approved', who: a.email, role: a.user.role, at: NOW() });
      audit('approve', a.email, { id: rpt.id, role: a.user.role });
      if (!nextApproverRole(rpt)) { rpt.status = 'approved'; rpt.history.push({ event: 'fully-approved', at: NOW() }); }
      return json(res, 200, { report: rpt });
    }
    if (b.decision === 'reject') {
      rpt.status = 'rejected'; // AC7: terminal
      rpt.history.push({ event: 'rejected', who: a.email, at: NOW(), comment: b.comment });
      audit('reject', a.email, { id: rpt.id, comment: b.comment });
      return json(res, 200, { report: rpt });
    }
    if (b.decision === 'changes-requested') {
      rpt.status = 'draft'; // AC1: returns to draft for editing
      rpt.approvals = [];
      rpt.history.push({ event: 'changes-requested', who: a.email, at: NOW(), comment: b.comment });
      audit('changes-requested', a.email, { id: rpt.id, comment: b.comment });
      return json(res, 200, { report: rpt });
    }
    return json(res, 400, { error: 'unknown decision' });
  }

  if (p === '/api/reports' && req.method === 'GET') { // AC list per role (mine / inbox)
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    const scope = u.searchParams.get('scope') || 'mine';
    if (scope === 'mine') return json(res, 200, { reports: db.reports.filter(r => r.submitterId === a.user.id) });
    if (scope === 'inbox') { // reports currently awaiting THIS user's role, excluding own reports (AC3)
      const inbox = db.reports.filter(r => r.status === 'submitted' && r.submitterId !== a.user.id && nextApproverRole(r) === a.user.role);
      return json(res, 200, { reports: inbox });
    }
    return json(res, 400, { error: 'unknown scope' });
  }

  if (p.match(/^\/api\/reports\/[^/]+$/) && req.method === 'GET') {
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    const rpt = db.reports.find(r => r.id === p.split('/').pop());
    // IDOR fix (found by usability/security review pass, 2026-07-26): reading a report was
    // never ownership-checked (unlike the PUT/edit path above), so any authenticated user
    // could read any other user's report by id, including unsubmitted drafts. Same visibility
    // rule as the /api/reports?scope=inbox listing: the submitter always sees their own report;
    // an approver only sees it once it is submitted and currently awaiting their role.
    const isOwner = rpt && rpt.submitterId === a.user.id;
    const isCurrentApprover = rpt && rpt.status === 'submitted' && rpt.submitterId !== a.user.id && nextApproverRole(rpt) === a.user.role;
    if (!rpt || !(isOwner || isCurrentApprover)) return json(res, 404, { error: 'report not found' });
    return json(res, 200, { report: rpt });
  }

  if (p === '/api/audit' && req.method === 'GET') {
    // Auth fix (found by the 2026-07-26 external audit workflow, live curl reproduction):
    // AC8 requires transitions to BE recorded (who/when on every event) but never specifies
    // WHO may read the trail back -- that gap was silently resolved as fully open ("demo-open")
    // instead of defaulting to authenticated-only, exposing every user's email, report totals
    // and rejection comments to an unauthenticated caller. Same class of silent-permissive
    // resolution as the D96 IDOR gap; same fix posture: default-deny, require a valid session.
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    return json(res, 200, { audit: db.audit });
  }

  if (p === '/api/whoami-clock' && req.method === 'GET') return json(res, 200, { now: NOW(), isoDaysAgo90: isoDaysAgo(90) }); // deterministic test helper

  if (p === '/api/suggest-category' && req.method === 'POST') { // AI/ML-style feature (#53)
    const a = authFrom(req); if (!a) return json(res, 401, { error: 'unauthenticated' });
    const b = await body(req);
    if (typeof b.description !== 'string' || b.description.length === 0) {
      return json(res, 422, { error: 'description is required' }); // AC-equivalent: no silent guess on empty input
    }
    return json(res, 200, suggestCategory(b.description));
  }

  // --- static ------------------------------------------------------------
  let file = p === '/' ? '/index.html' : p;
  const fp = path.join(__dirname, 'public', file);
  // Le separateur est indispensable : sans lui, un dossier voisin nomme `public-autre`
  // satisfait le prefixe et sort du repertoire servi. Severite faible dans cette demo,
  // mais c'est le motif qu'elle enseigne et qu'un lecteur recopiera (B7).
  const publicRoot = path.join(__dirname, 'public') + path.sep;
  if (fp.startsWith(publicRoot) && fs.existsSync(fp) && fs.statSync(fp).isFile()) {
    const ext = path.extname(fp); const ct = ext === '.html' ? 'text/html' : ext === '.js' ? 'text/javascript' : ext === '.css' ? 'text/css' : 'text/plain';
    res.writeHead(200, { 'Content-Type': ct }); return res.end(fs.readFileSync(fp));
  }
  json(res, 404, { error: 'not found' });
});

const PORT = process.env.PORT || 4500;
server.listen(PORT, () => console.log('ExpenseFlow SUT on http://localhost:' + PORT));
