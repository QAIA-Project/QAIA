#!/usr/bin/env node
/**
 * QAIA — Meilisearch defect-hunting probe
 * Campaign: 2026-08-11
 * Target  : self-hosted Meilisearch v1.53.0 on 127.0.0.1:7700
 *
 * ORACLE = the prose documentation at https://www.meilisearch.com/docs/
 * Every check below carries the verbatim documented promise it derives from.
 * The probe NEVER reads Meilisearch source. It compares observed to promised.
 *
 * Usage:
 *   MEILI_URL=http://127.0.0.1:7700 MEILI_KEY=<master-key> node probe.js
 */

const URL_BASE = process.env.MEILI_URL || 'http://127.0.0.1:7700';
const KEY = process.env.MEILI_KEY || 'QAIAmasterKey2026probe';
const H = { 'Content-Type': 'application/json', Authorization: `Bearer ${KEY}` };

const results = [];
let pass = 0, fail = 0;

function log(...a) { console.log(...a); }

/**
 * Record an observation.
 * @param id      stable check id
 * @param promise verbatim documented sentence (the oracle)
 * @param expect  what the promise implies, in the probe's terms
 * @param actual  what was observed
 * @param ok      whether observed matches promised
 */
function check(id, promise, expect, actual, ok) {
  results.push({ id, promise, expect, actual, ok });
  if (ok) { pass++; log(`  [PASS] ${id}  expected=${expect} actual=${actual}`); }
  else { fail++; log(`  [DEVIATION] ${id}  expected=${expect} actual=${actual}\n             promise: "${promise}"`); }
}

async function api(method, path, body) {
  const r = await fetch(URL_BASE + path, {
    method, headers: H, body: body === undefined ? undefined : JSON.stringify(body),
  });
  let j = null;
  const text = await r.text();
  if (text) { try { j = JSON.parse(text); } catch { j = text; } }
  return { status: r.status, body: j };
}

async function waitTask(taskUid) {
  for (let i = 0; i < 300; i++) {
    const { body } = await api('GET', `/tasks/${taskUid}`);
    if (body.status === 'succeeded') return body;
    if (body.status === 'failed' || body.status === 'canceled') {
      throw new Error(`task ${taskUid} ${body.status}: ${JSON.stringify(body.error)}`);
    }
    await new Promise((s) => setTimeout(s, 200));
  }
  throw new Error(`task ${taskUid} timed out`);
}

async function settle(res) {
  if (res.body && res.body.taskUid !== undefined) return waitTask(res.body.taskUid);
  return res;
}

// Deleting an index that does not exist is a failed task, not an error we care about.
async function dropIndex(uid) {
  try { await settle(await api('DELETE', `/indexes/${uid}`)); } catch { /* absent */ }
}

const search = (index, q) => api('POST', `/indexes/${index}/search`, q);

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

async function setupPagination() {
  await dropIndex('pag');
  await settle(await api('POST', '/indexes', { uid: 'pag', primaryKey: 'id' }));
  const docs = Array.from({ length: 1200 }, (_, i) => ({ id: i + 1, title: `doc number ${i + 1}` }));
  await settle(await api('POST', '/indexes/pag/documents', docs));
}

async function setupFilter() {
  await dropIndex('filt');
  await settle(await api('POST', '/indexes', { uid: 'filt', primaryKey: 'id' }));
  // 10 documents spanning every JSON shape the filter doc makes a promise about.
  const docs = [
    { id: 1, cat: 'action', num: 80 },                 // plain match
    { id: 2, cat: 'drama', num: 85 },                  // plain non-match
    { id: 3, cat: 'ACTION', num: 89 },                 // case variant
    { id: 4, cat: null, num: 90 },                     // null
    { id: 5, cat: '', num: 79 },                       // empty string
    { id: 6, cat: [], num: 100 },                      // empty array
    { id: 7, cat: {}, num: 1 },                        // empty object
    { id: 8, num: 50 },                                // attribute absent
    { id: 9, cat: ['action', 'adventure'], num: 60 },  // array containing the value
    { id: 10, cat: 'comedy', num: 70 },                // plain non-match
  ];
  await settle(await api('POST', '/indexes/filt/documents', docs));
  await settle(await api('PATCH', '/indexes/filt/settings', {
    filterableAttributes: ['cat', 'num'],
  }));
}

async function setupTypo() {
  await dropIndex('typo');
  await settle(await api('POST', '/indexes', { uid: 'typo', primaryKey: 'id' }));
  // Each target word is a disjoint invented root, so no query can accidentally
  // prefix-match a neighbouring fixture.
  const docs = [
    { id: 1, w: 'brik' },        // 4 chars
    { id: 2, w: 'cralo' },       // 5 chars
    { id: 3, w: 'dantimex' },    // 8 chars
    { id: 4, w: 'fantimexo' },   // 9 chars
    { id: 5, w: 'gralo' },       // 5 chars, first-char-typo target
    { id: 6, w: 'jorbanexo' },   // 9 chars, first-char-typo target
  ];
  // NB: id 6 must differ from id 4 ("fantimexo") in more than its first
  // character, otherwise a single first-char-typo query matches both and the
  // check below counts 2 hits for reasons that have nothing to do with the
  // documented rule. This bit us on the first run.
  await settle(await api('POST', '/indexes/typo/documents', docs));
}

// ---------------------------------------------------------------------------
// Probe 1 — typo tolerance thresholds
// ORACLE: /docs/learn/relevancy/typo_tolerance_settings
// ---------------------------------------------------------------------------

async function probeTypo() {
  log('\n=== PROBE 1: typo tolerance thresholds ===');
  const P_1_4 = 'If the query word is between `1` and `4` characters, **no typo** is allowed.';
  const P_5_8 = 'If the query word is between `5` and `8` characters, **one typo** is allowed';
  const P_9 = 'If the query word contains more than `8` characters, a maximum of **two typos** is allowed';
  const P_FIRST = "Meilisearch considers a typo on a query's first character as two typos.";

  const n = async (q) => (await search('typo', { q, limit: 20 })).body.hits.length;

  // Lower boundary of the 1-typo window: 4 chars must NOT tolerate a typo, 5 must.
  check('TYPO-01-len4-1typo', P_1_4, '0 hits (len 4, 1 typo)', `${await n('brok')} hits`, (await n('brok')) === 0);
  check('TYPO-02-len5-1typo', P_5_8, '1 hit (len 5, 1 typo)', `${await n('crolo')} hits`, (await n('crolo')) === 1);

  // Upper boundary of the 1-typo window: 8 chars tolerate 1 but not 2 typos.
  check('TYPO-03-len8-1typo', P_5_8, '1 hit (len 8, 1 typo)', `${await n('dontimex')} hits`, (await n('dontimex')) === 1);
  check('TYPO-04-len8-2typos', P_5_8, '0 hits (len 8, 2 typos)', `${await n('dontemex')} hits`, (await n('dontemex')) === 0);

  // Lower boundary of the 2-typo window: 9 chars tolerate 2 typos.
  check('TYPO-05-len9-2typos', P_9, '1 hit (len 9, 2 typos)', `${await n('fontemexo')} hits`, (await n('fontemexo')) === 1);

  // First character costs two typos: forbidden at len 5, allowed at len 9.
  check('TYPO-06-firstchar-len5', P_FIRST, '0 hits (len 5, first-char typo = 2 typos)', `${await n('hralo')} hits`, (await n('hralo')) === 0);
  check('TYPO-07-firstchar-len9', P_FIRST, '1 hit (len 9, first-char typo = 2 typos, allowed)', `${await n('korbanexo')} hits`, (await n('korbanexo')) === 1);

  // Setting-level constraints: "0 <= oneTypo <= twoTypos <= 255"
  const P_RANGE = '`oneTypo` must be greater than or equal to 0 and less than or equal to `twoTypos`; `twoTypos` ... less than or equal to `255`';

  const r255 = await api('PATCH', '/indexes/typo/settings', {
    typoTolerance: { minWordSizeForTypos: { oneTypo: 255, twoTypos: 255 } },
  });
  let ok255 = false;
  try { await settle(r255); ok255 = true; } catch { ok255 = false; }
  check('TYPO-08-bound-255', P_RANGE, 'accepted (255 is the documented max)', ok255 ? 'accepted' : 'rejected', ok255);

  const r256 = await api('PATCH', '/indexes/typo/settings', {
    typoTolerance: { minWordSizeForTypos: { oneTypo: 5, twoTypos: 256 } },
  });
  let rejected256 = r256.status >= 400;
  if (!rejected256) { try { await settle(r256); } catch { rejected256 = true; } }
  check('TYPO-09-bound-256', P_RANGE, 'rejected (256 > documented max 255)', rejected256 ? 'rejected' : 'accepted', rejected256);

  const rInv = await api('PATCH', '/indexes/typo/settings', {
    typoTolerance: { minWordSizeForTypos: { oneTypo: 9, twoTypos: 5 } },
  });
  let rejectedInv = rInv.status >= 400;
  let invErr = rInv.body && rInv.body.code;
  if (!rejectedInv) { try { await settle(rInv); } catch (e) { rejectedInv = true; invErr = String(e.message).slice(0, 120); } }
  check('TYPO-10-oneTypo-gt-twoTypos', P_RANGE, 'rejected (oneTypo must be <= twoTypos)',
    rejectedInv ? `rejected (${invErr})` : 'accepted', rejectedInv);

  // restore defaults for any later probe
  await settle(await api('PATCH', '/indexes/typo/settings', {
    typoTolerance: { minWordSizeForTypos: { oneTypo: 5, twoTypos: 9 } },
  }));
}

// ---------------------------------------------------------------------------
// Probe 2 — pagination limits
// ORACLE: /docs/reference/api/search (+ settings)
// ---------------------------------------------------------------------------

async function probePagination() {
  log('\n=== PROBE 2: pagination and maxTotalHits ===');
  const P_1000 = 'By default this endpoint returns at most 1000 results. Configure `pagination.maxTotalHits` in index settings to change this limit.';
  const P_LIMIT_CAP = 'This parameter is ignored when `page` or `hitsPerPage` is set. The value cannot exceed the index maxTotalHits setting.';
  const P_MTH = 'Maximum number of search results Meilisearch can return. Limit and offset cannot go beyond this value.';
  const P_DEF_LIMIT = 'limit ... default: 20';
  const P_PREC = '`page` and `hitsPerPage` take precedence over `offset` and `limit`.';

  // default limit
  let r = await search('pag', { q: '' });
  check('PAG-01-default-limit', P_DEF_LIMIT, '20 hits', `${r.body.hits.length} hits`, r.body.hits.length === 20);

  // the documented cap itself
  r = await search('pag', { q: '', limit: 1000 });
  check('PAG-02-limit-1000', P_1000, '1000 hits', `${r.body.hits.length} hits`, r.body.hits.length === 1000);

  // cap + 1: doc says the value cannot exceed maxTotalHits, and at most 1000 come back
  r = await search('pag', { q: '', limit: 1001 });
  check('PAG-03-limit-1001', P_1000 + ' / ' + P_LIMIT_CAP,
    'at most 1000 hits (or a 400 rejecting limit > maxTotalHits)',
    `status=${r.status} ${r.body.hits ? r.body.hits.length + ' hits' : JSON.stringify(r.body).slice(0, 120)}`,
    r.status >= 400 || (r.body.hits && r.body.hits.length <= 1000));

  // offset walks up to the cap
  r = await search('pag', { q: '', offset: 995, limit: 20 });
  check('PAG-04-offset-995', P_MTH, '5 hits (1000 - 995)', `${r.body.hits.length} hits`, r.body.hits.length === 5);

  r = await search('pag', { q: '', offset: 999, limit: 20 });
  check('PAG-05-offset-999', P_MTH, '1 hit', `${r.body.hits.length} hits`, r.body.hits.length === 1);

  r = await search('pag', { q: '', offset: 1000, limit: 20 });
  check('PAG-06-offset-1000', P_MTH, '0 hits (offset cannot go beyond maxTotalHits)', `${r.body.hits.length} hits`, r.body.hits.length === 0);

  // estimatedTotalHits under the cap
  r = await search('pag', { q: '', limit: 20 });
  check('PAG-07-estimatedTotalHits', P_MTH, 'estimatedTotalHits <= 1000',
    `estimatedTotalHits=${r.body.estimatedTotalHits}`, r.body.estimatedTotalHits <= 1000);

  // page/hitsPerPage branch
  r = await search('pag', { q: '', hitsPerPage: 100, page: 10 });
  check('PAG-08-page10', P_MTH, '100 hits, totalHits<=1000, totalPages<=10',
    `hits=${r.body.hits.length} totalHits=${r.body.totalHits} totalPages=${r.body.totalPages}`,
    r.body.hits.length === 100 && r.body.totalHits <= 1000 && r.body.totalPages <= 10);

  r = await search('pag', { q: '', hitsPerPage: 100, page: 11 });
  check('PAG-09-page11', P_MTH, '0 hits (past the 1000-result cap)', `${r.body.hits.length} hits`, r.body.hits.length === 0);

  // page is documented "1-indexed" but the schema allows minimum 0
  r = await search('pag', { q: '', hitsPerPage: 10, page: 0 });
  check('PAG-10-page-0', 'Request a specific results page (1-indexed). ... minimum: 0',
    'either 0 hits or a 400 — page 0 does not exist in a 1-indexed scheme',
    `status=${r.status} hits=${r.body.hits ? r.body.hits.length : 'n/a'}`,
    r.status >= 400 || (r.body.hits && r.body.hits.length === 0));

  // precedence of page/hitsPerPage over offset/limit
  r = await search('pag', { q: '', limit: 5, offset: 500, hitsPerPage: 3, page: 1 });
  check('PAG-11-precedence', P_PREC, '3 hits and totalHits present (offset/limit ignored)',
    `hits=${r.body.hits.length} totalHits=${r.body.totalHits} firstId=${r.body.hits[0] && r.body.hits[0].id}`,
    r.body.hits.length === 3 && r.body.totalHits !== undefined);

  // raising the cap must raise the ceiling
  await settle(await api('PATCH', '/indexes/pag/settings', { pagination: { maxTotalHits: 1200 } }));
  r = await search('pag', { q: '', limit: 1200 });
  check('PAG-12-raised-cap', P_MTH, '1200 hits after maxTotalHits=1200', `${r.body.hits.length} hits`, r.body.hits.length === 1200);

  // Lower bound of the setting. The published reference schema for
  // pagination.maxTotalHits declares "minimum: 0", so 0 must be a legal value.
  // Checked on the dedicated sub-route so the HTTP status is not hidden behind
  // a whole-settings PATCH.
  const zero = await api('PATCH', '/indexes/pag/settings/pagination', { maxTotalHits: 0 });
  check('PAG-13-cap-zero-accepted',
    'maxTotalHits ... default: 1000, example: 1000, minimum: 0',
    'HTTP 2xx — 0 is inside the documented range [0, ...]',
    `status=${zero.status} ${zero.status >= 400 ? JSON.stringify(zero.body.message) : 'accepted'}`,
    zero.status < 400);

  await settle(await api('PATCH', '/indexes/pag/settings/pagination', { maxTotalHits: 1000 }));
}

// ---------------------------------------------------------------------------
// Probe 3 — filter semantics
// ORACLE: /docs/learn/filtering_and_sorting/filter_expression_reference
// ---------------------------------------------------------------------------

async function probeFilter() {
  log('\n=== PROBE 3: filter operator semantics ===');
  const ids = async (filter) => {
    const r = await search('filt', { q: '', filter, limit: 100 });
    if (r.status >= 400) return { err: r.body };
    return r.body.hits.map((h) => h.id).sort((a, b) => a - b);
  };
  const j = (x) => JSON.stringify(x);

  const P_NOTFILT = 'By default, `filterableAttributes` is empty. Filters do not work without first explicitly adding attributes to the `filterableAttributes` list.';
  const P_EQ_CASE = 'When operating on strings, `=` is case-insensitive.';
  const P_EQ_NULL = 'The equality operator does not return any results for `null` and empty arrays.';
  const P_NEQ = 'The inequality operator (`!=`) returns all documents not selected by the equality operator.';
  const P_EXISTS = 'The `EXISTS` operator checks for the existence of a field. Fields with empty or `null` values count as existing.';
  const P_EMPTY = 'The `IS EMPTY` operator selects documents in which the specified attribute exists but contains empty values. `IS EMPTY` matches the following JSON values: `""`, `[]`, `{}`';
  const P_NULL = 'The `IS NULL` operator selects documents in which the specified attribute exists but contains a `null` value.';
  const P_TO = '`TO` is equivalent to `>= AND <=`.';
  const P_PREC = 'This happens because `AND` takes precedence over `OR`.';

  // filtering on an undeclared attribute must be refused
  const undeclared = await search('filt', { q: '', filter: 'title = whatever' });
  check('FILT-01-undeclared', P_NOTFILT, 'HTTP 4xx refusal',
    `status=${undeclared.status} code=${undeclared.body && undeclared.body.code}`, undeclared.status >= 400);

  // = is case-insensitive and reaches into arrays
  const eqAction = await ids('cat = action');
  const eqACTION = await ids('cat = ACTION');
  check('FILT-02-eq-case', P_EQ_CASE, 'same id set for "action" and "ACTION"',
    `${j(eqAction)} vs ${j(eqACTION)}`, j(eqAction) === j(eqACTION));
  check('FILT-03-eq-array', 'if a document has "genres": ["action","adventure"], the filter genres = action will match',
    'id 9 included', j(eqAction), Array.isArray(eqAction) && eqAction.includes(9));

  // = returns nothing for null / empty array
  check('FILT-04-eq-no-null', P_EQ_NULL, 'ids 4 (null) and 6 ([]) absent',
    j(eqAction), Array.isArray(eqAction) && !eqAction.includes(4) && !eqAction.includes(6));

  // != must be the exact complement of = over the index
  const neqAction = await ids('cat != action');
  const all = await ids('num >= 0');
  const union = Array.isArray(eqAction) && Array.isArray(neqAction)
    ? [...new Set([...eqAction, ...neqAction])].sort((a, b) => a - b) : null;
  const total = 10;
  check('FILT-05-neq-complement', P_NEQ,
    `|= action| + |!= action| == ${total} (every document is on exactly one side)`,
    `|=|=${eqAction.length} ${j(eqAction)} |!=|=${neqAction.length} ${j(neqAction)} union=${j(union)}`,
    union !== null && union.length === total);

  // NOT = should agree with !=
  const notEq = await ids('NOT cat = action');
  check('FILT-06-not-eq-vs-neq', P_NEQ, '`NOT cat = action` == `cat != action`',
    `${j(notEq)} vs ${j(neqAction)}`, j(notEq) === j(neqAction));

  // EXISTS counts empty and null as existing
  const exists = await ids('cat EXISTS');
  check('FILT-07-exists', P_EXISTS, 'ids 1-7,9,10 present (all but id 8), i.e. null/""/[]/{} count as existing',
    j(exists), Array.isArray(exists) && j(exists) === j([1, 2, 3, 4, 5, 6, 7, 9, 10]));

  // IS EMPTY matches exactly "" , [] and {}
  const empty = await ids('cat IS EMPTY');
  check('FILT-08-is-empty', P_EMPTY, 'exactly ids 5 (""), 6 ([]), 7 ({})',
    j(empty), Array.isArray(empty) && j(empty) === j([5, 6, 7]));

  // IS NULL matches exactly the null document
  const isnull = await ids('cat IS NULL');
  check('FILT-09-is-null', P_NULL, 'exactly id 4', j(isnull),
    Array.isArray(isnull) && j(isnull) === j([4]));

  // TO is >= AND <=
  const to = await ids('num 80 TO 89');
  const gte = await ids('num >= 80 AND num <= 89');
  check('FILT-10-to-equivalence', P_TO, '`num 80 TO 89` == `num >= 80 AND num <= 89`',
    `${j(to)} vs ${j(gte)}`, j(to) === j(gte));

  // AND binds tighter than OR
  const noParen = await ids('num >= 85 AND cat = action OR cat = comedy');
  const withParen = await ids('(num >= 85 AND cat = action) OR cat = comedy');
  check('FILT-11-and-precedence', P_PREC, '`a AND b OR c` == `(a AND b) OR c`',
    `${j(noParen)} vs ${j(withParen)}`, j(noParen) === j(withParen));

  // IN is a disjunction of equalities
  const inOp = await ids('cat IN [action, comedy]');
  const orOp = await ids('cat = action OR cat = comedy');
  check('FILT-12-in-equivalence',
    '`IN` combines equality operators ... It selects all documents whose chosen field contains at least one of the specified values.',
    '`cat IN [action, comedy]` == `cat = action OR cat = comedy`',
    `${j(inOp)} vs ${j(orOp)}`, j(inOp) === j(orOp));

  return { eqAction, neqAction, all };
}

// ---------------------------------------------------------------------------
// Probe 4 — rankingScoreThreshold
// ORACLE: /docs/reference/api/search
// ---------------------------------------------------------------------------

async function probeScoreThreshold() {
  log('\n=== PROBE 4: rankingScoreThreshold ===');
  const P_RANGE = 'Exclude from the results any document whose ranking score is below this value (between 0.0 and 1.0).';
  const P_COUNT = 'Excluded hits do not count toward `estimatedTotalHits`, `totalHits`, or facet distribution.';

  await dropIndex('score');
  await settle(await api('POST', '/indexes', { uid: 'score', primaryKey: 'id' }));
  await settle(await api('POST', '/indexes/score/documents', [
    { id: 1, t: 'quick brown fox' },
    { id: 2, t: 'quick brown' },
    { id: 3, t: 'quick' },
    { id: 4, t: 'brown fox quick' },
    { id: 5, t: 'a fox' },
    { id: 6, t: 'quick brown fox jumps over the lazy dog' },
  ]));

  // Calibrate on the observed score distribution rather than a guessed constant.
  const base = await search('score', { q: 'quick brown fox', limit: 20, showRankingScore: true });
  const scores = base.body.hits.map((h) => h._rankingScore);
  log(`  observed scores: ${JSON.stringify(scores)}`);
  const thr = scores.length > 1 ? scores[Math.floor(scores.length / 2)] : 0.5;
  const expectedAbove = scores.filter((s) => s >= thr).length;

  // The hits array must honour the threshold...
  const filtered = await search('score', { q: 'quick brown fox', limit: 20, showRankingScore: true, rankingScoreThreshold: thr });
  check('SCORE-01-hits-filtered', P_RANGE, `${expectedAbove} hits with score >= ${thr}`,
    `${filtered.body.hits.length} hits`, filtered.body.hits.length === expectedAbove);

  // ...and so must estimatedTotalHits.
  check('SCORE-02-estimated-total', P_COUNT, `estimatedTotalHits == ${expectedAbove}`,
    `estimatedTotalHits=${filtered.body.estimatedTotalHits}`, filtered.body.estimatedTotalHits === expectedAbove);

  // ...and totalHits in the page-based branch.
  const paged = await search('score', { q: 'quick brown fox', page: 1, hitsPerPage: 20, rankingScoreThreshold: thr });
  check('SCORE-03-total-hits', P_COUNT, `totalHits == ${expectedAbove}`,
    `totalHits=${paged.body.totalHits} totalPages=${paged.body.totalPages}`, paged.body.totalHits === expectedAbove);

  // Documented range boundaries: 0.0 and 1.0 legal, outside it refused.
  for (const [id, v, legal] of [['SCORE-04-thr-0', 0.0, true], ['SCORE-05-thr-1', 1.0, true],
    ['SCORE-06-thr-above-1', 1.1, false], ['SCORE-07-thr-below-0', -0.1, false]]) {
    const r = await search('score', { q: 'quick brown fox', rankingScoreThreshold: v });
    check(id, P_RANGE, legal ? 'HTTP 2xx (inside 0.0-1.0)' : 'HTTP 4xx (outside 0.0-1.0)',
      `status=${r.status} ${r.status >= 400 ? r.body.code : (r.body.hits.length + ' hits')}`,
      legal ? r.status < 400 : r.status >= 400);
  }
}

// ---------------------------------------------------------------------------
// Probe 5 — faceting maxValuesPerFacet
// ORACLE: /docs/reference/api/settings
// ---------------------------------------------------------------------------

async function probeFaceting() {
  log('\n=== PROBE 5: faceting maxValuesPerFacet ===');
  const P_FACET = 'Maximum number of facet values returned per facet. ... default: 100 ... minimum: 0';

  await dropIndex('facet');
  await settle(await api('POST', '/indexes', { uid: 'facet', primaryKey: 'id' }));
  // 150 documents, each with its own distinct facet value: more values than the
  // documented default cap of 100.
  await settle(await api('POST', '/indexes/facet/documents',
    Array.from({ length: 150 }, (_, i) => ({ id: i + 1, g: `genre${i + 1}` }))));
  await settle(await api('PATCH', '/indexes/facet/settings', { filterableAttributes: ['g'] }));

  let r = await search('facet', { q: '', facets: ['g'], limit: 0 });
  let n = Object.keys(r.body.facetDistribution.g).length;
  check('FACET-01-default-100', P_FACET, '100 facet values returned (the default cap)', `${n} values`, n === 100);

  // The documented lower bound of the setting.
  const zero = await api('PATCH', '/indexes/facet/settings/faceting', { maxValuesPerFacet: 0 });
  check('FACET-02-zero-accepted', P_FACET, 'HTTP 2xx — 0 is inside the documented range',
    `status=${zero.status} ${zero.status >= 400 ? JSON.stringify(zero.body.message) : 'accepted'}`, zero.status < 400);
  if (zero.status < 400) {
    await settle(zero);
    r = await search('facet', { q: '', facets: ['g'], limit: 0 });
    n = Object.keys(r.body.facetDistribution.g).length;
    check('FACET-03-zero-effect', P_FACET, '0 facet values when maxValuesPerFacet=0', `${n} values`, n === 0);
  }

  await settle(await api('PATCH', '/indexes/facet/settings/faceting', { maxValuesPerFacet: 100 }));
}

// ---------------------------------------------------------------------------

(async () => {
  const v = await api('GET', '/version');
  log(`Meilisearch ${v.body.pkgVersion}  commit ${v.body.commitSha}  built ${v.body.commitDate}`);
  log(`Probe run at ${new Date().toISOString()}`);

  log('\nBuilding fixtures...');
  await setupPagination();
  await setupFilter();
  await setupTypo();
  log('Fixtures ready.');

  await probeTypo();
  await probePagination();
  await probeFilter();
  await probeScoreThreshold();
  await probeFaceting();

  log(`\n===== SUMMARY =====\nchecks=${results.length}  matched=${pass}  deviations=${fail}`);
  for (const r of results.filter((x) => !x.ok)) {
    log(`\nDEVIATION ${r.id}\n  promise : ${r.promise}\n  expected: ${r.expect}\n  actual  : ${r.actual}`);
  }
  process.exit(0);
})().catch((e) => { console.error('PROBE ERROR', e); process.exit(1); });
