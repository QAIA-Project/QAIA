// PocketBase documentation-vs-behaviour probe.
//
// ORACLE: https://pocketbase.io/docs/api-rules-and-filters/ and
//         https://pocketbase.io/docs/api-records/ (prose only).
//         The PocketBase source code was NOT consulted to derive any expectation here.
// TARGET: a LOCAL, self-hosted instance on 127.0.0.1 only. Single process, no concurrent writer,
//         so state is stable between requests (no data mutation happens after setup.js).
//
// Usage:  node setup.js && node probe.js > evidence.txt
//
// Each check carries:
//   promise : the documented sentence being tested (verbatim or near-verbatim)
//   expect  : the record set / property the prose entails, or null when the prose is silent
//             (silent checks are recorded as OBSERVED-ONLY and are never called defects)

const BASE = process.env.PB_URL || 'http://127.0.0.1:8090';
const EMAIL = 'probe@example.com';
const PASS = 'Probe12345678';
const REPEATS = 2; // the protocol requires reproducing every observation at least twice

let TOKEN = null;

async function get(path, token) {
  const h = {};
  if (token) h.Authorization = token;
  const r = await fetch(BASE + path, { headers: h });
  let j = null;
  try { j = await r.json(); } catch (_) {}
  return { status: r.status, body: j };
}

// Records are identified in the report by "title", or by "#note" when the title is empty.
function key(rec) { return rec.title === '' ? '#' + rec.note : rec.title; }
function names(body) {
  if (!body || !Array.isArray(body.items)) return null;
  return body.items.map(key).sort();
}
function q(s) { return encodeURIComponent(s); }

const results = [];

// run a list request twice and require identical results before reporting anything
async function listTwice(path, token) {
  const runs = [];
  for (let i = 0; i < REPEATS; i++) runs.push(await get(path, token));
  const a = JSON.stringify(runs[0]);
  const stable = runs.every(r => JSON.stringify(r) === a);
  return { ...runs[0], stable, runs: REPEATS };
}

async function check({ id, promise, filter, path, expect, note, token, sortAgnostic }) {
  const p = path || ('/api/collections/probe_items/records?perPage=100&sort=id&filter=' + q(filter));
  const res = await listTwice(p, token === undefined ? null : token);
  const got = names(res.body);
  let verdict;
  if (!res.stable) verdict = 'UNSTABLE';
  else if (expect === null || expect === undefined) verdict = 'OBSERVED-ONLY';
  else if (typeof expect === 'function') verdict = expect(res) ? 'MATCH' : 'DEVIATION';
  else verdict = JSON.stringify(got) === JSON.stringify([...expect].sort()) ? 'MATCH' : 'DEVIATION';

  results.push({ id, verdict, promise, request: p, filter, expect, got, status: res.status, note, body: res.body });

  console.log('--------------------------------------------------------------------');
  console.log('[' + id + '] ' + verdict + '   (' + REPEATS + ' identical runs: ' + res.stable + ')');
  console.log('  PROMISE : ' + promise);
  if (filter) console.log('  FILTER  : ' + filter);
  console.log('  REQUEST : GET ' + p);
  console.log('  STATUS  : ' + res.status);
  if (expect && typeof expect !== 'function') console.log('  EXPECT  : ' + JSON.stringify([...expect].sort()));
  if (got) console.log('  GOT     : ' + JSON.stringify(got));
  else console.log('  BODY    : ' + JSON.stringify(res.body));
  if (note) console.log('  NOTE    : ' + note);
}

(async () => {
  console.log('PocketBase probe — ' + new Date().toISOString());
  const ver = await get('/api/health');
  console.log('health: ' + JSON.stringify(ver.body));
  console.log('binary: pocketbase.exe version 0.39.10 (windows_amd64)');
  console.log('target: ' + BASE + '  (local, single process)');
  console.log('');

  const auth = await fetch(BASE + '/api/collections/_superusers/auth-with-password', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identity: EMAIL, password: PASS }),
  }).then(r => r.json());
  TOKEN = auth.token;

  const ALL = ['Lorem ipsum', 'lorem lower', '100% pure', 'under_score', 'quote\'d "both"', '#emptytit', 'back\\slash'];

  // ================= comparison operators on scalars =================
  await check({ id: 'F01', promise: '"= Equal"', filter: 'title = "Lorem ipsum"', expect: ['Lorem ipsum'] });
  await check({ id: 'F02', promise: '"!= NOT equal"', filter: 'title != "Lorem ipsum"', expect: ALL.filter(x => x !== 'Lorem ipsum') });
  await check({ id: 'F03', promise: '"> Greater than"', filter: 'num > 7', expect: ['Lorem ipsum', 'quote\'d "both"'] });
  await check({ id: 'F04', promise: '">= Greater than or equal"', filter: 'num >= 7', expect: ['Lorem ipsum', 'quote\'d "both"', 'back\\slash'] });
  await check({ id: 'F05', promise: '"< Less than"', filter: 'num < 5', expect: ['lorem lower', '100% pure', '#emptytit'] });
  await check({ id: 'F06', promise: '"<= Less than or equal"', filter: 'num <= 5', expect: ['lorem lower', '100% pure', '#emptytit', 'under_score'] });
  await check({ id: 'F07', promise: 'OPERAND could be a number; negative numbers compare as numbers', filter: 'num < 0', expect: ['100% pure'] });

  // ================= like / wildcard =================
  await check({
    id: 'F10',
    promise: '"~ Like/Contains (if not specified auto wraps the right string OPERAND in a \\"%\\" for wildcard match)"',
    filter: 'note ~ "lai"', expect: ['Lorem ipsum'],
    note: 'note="plain" — substring match proves the auto-wrapping on both sides.',
  });
  await check({
    id: 'F11',
    promise: 'Doc example: \'Allow access by anyone and return only the records where the title field value starts with "Lorem" (ex. "Lorem ipsum")\' with filter title ~ "Lorem%"',
    filter: 'title ~ "Lorem%"', expect: ['Lorem ipsum'],
    note: 'The prose says "starts with Lorem". The fixture also contains "lorem lower" (lower-case l). If it comes back too, the documented example is case-insensitive while the prose is not qualified.',
  });
  await check({
    id: 'F12', promise: '"!~ NOT Like/Contains"', filter: 'note !~ "lai"',
    expect: ALL.filter(x => x !== 'Lorem ipsum'),
  });
  await check({
    id: 'F13',
    promise: 'The doc names "%" as THE wildcard character for ~ and never mentions "_" as a wildcard.',
    filter: 'title ~ "u_der_score"', expect: null,
    note: 'If "under_score" is returned, "_" is also acting as a single-character wildcard — a behaviour the documentation never states.',
  });
  await check({
    id: 'F14',
    promise: 'A literal "%" in the right operand — doc gives no escaping rule.',
    filter: 'title ~ "100%"', expect: null,
    note: 'OBSERVED-ONLY: doc silent on escaping literal wildcards.',
  });
  await check({
    id: 'F15', promise: '"= Equal" on a value containing a literal %', filter: 'title = "100% pure"', expect: ['100% pure'],
  });

  // ================= multi-valued fields: match-all vs any =================
  await check({
    id: 'M01',
    promise: '"Field expressions with array-like value or nested fields that originate from a source with multiple records will apply a match-all constraint by default."',
    filter: 'tags.label = "alpha"', expect: ['lorem lower'],
    note: 'Only "lorem lower" has alpha as its ONLY tag. "Lorem ipsum" (alpha+beta) and "#emptytit" (alpha+beta+gamma) must NOT match under a match-all reading.',
  });
  await check({
    id: 'M02',
    promise: '"?= Any/At least one of Equal" — doc example: allowed_users.id ?= @request.auth.id',
    filter: 'tags.label ?= "alpha"', expect: ['Lorem ipsum', 'lorem lower', '#emptytit'],
  });
  await check({
    id: 'M03',
    promise: '"?!= Any/At least one of NOT equal"',
    filter: 'tags.label ?!= "alpha"', expect: null,
    note: 'OBSERVED-ONLY: prose does not state what "at least one of" yields for records with an EMPTY relation ("100% pure", "back\\\\slash"). Recording the answer.',
  });
  await check({
    id: 'M04',
    promise: 'match-all default applied to != on a multi-relation',
    filter: 'tags.label != "alpha"', expect: null,
    note: 'OBSERVED-ONLY: doc states the match-all default but not its interaction with an empty array.',
  });
  await check({
    id: 'M05',
    promise: '":length modifier could be used to check the number of items in an array field (multiple file, select, relation)"',
    filter: 'tags:length = 3', expect: ['#emptytit'],
  });
  await check({
    id: 'M06', promise: ':length on an empty array field', filter: 'opts:length = 0', expect: ['100% pure'],
  });
  await check({
    id: 'M07',
    promise: '":each ... apply a condition on each item from the field array" — doc example: someSelectField:each ~ "pb_%"',
    filter: 'opts:each ~ "pb_%"', expect: null,
    note: 'OBSERVED-ONLY on the empty-array record. "under_score" (pb_x,pb_y) must be in the result under any reading; whether "100% pure" (opts=[]) is included is not stated.',
  });
  await check({
    id: 'M08',
    promise: '":lower ... perform lower-case string comparisons ... match existing records with lower-cased title equal to "test" ("Test", "tEsT", etc.)"',
    filter: 'title:lower = "lorem ipsum"', expect: ['Lorem ipsum'],
  });
  await check({
    id: 'M09',
    promise: '":isset field modifier is available only for the @request.* fields"',
    filter: 'title:isset = true', expect: null,
    note: 'OBSERVED-ONLY: expecting a rejection since the modifier is documented as @request.*-only.',
  });

  // ================= null / empty / bool =================
  await check({ id: 'N01', promise: 'OPERAND could be ... null', filter: 'when = null', expect: null, note: 'OBSERVED-ONLY; "quote\'d" has an empty date.' });
  await check({ id: 'N02', promise: 'OPERAND could be ... a string', filter: 'when = ""', expect: null, note: 'OBSERVED-ONLY.' });
  await check({ id: 'N03', promise: 'OPERAND could be ... true / false', filter: 'flag = true', expect: ['Lorem ipsum', 'under_score', '#emptytit'] });
  await check({ id: 'N04', promise: 'OPERAND could be ... true / false', filter: 'flag = false', expect: ['lorem lower', '100% pure', 'quote\'d "both"', 'back\\slash'] });
  await check({ id: 'N05', promise: 'text field equality against empty string', filter: 'title = ""', expect: ['#emptytit'] });

  // ================= grouping, comments =================
  await check({
    id: 'G01', promise: '"To group and combine several expressions you can use parenthesis (...), && (AND) and || (OR) tokens." Doc example: @request.auth.id != "" && (status = "active" || status = "pending")',
    filter: 'num > 6 && (flag = true || title ~ "quote")', expect: ['Lorem ipsum', 'quote\'d "both"'],
  });
  await check({
    id: 'G02', promise: '"Single line comments are also supported: // Example comment."',
    filter: '// leading comment\nnum > 90', expect: ['quote\'d "both"'],
  });
  await check({
    id: 'G03', promise: 'Single line comment placed after an expression',
    filter: 'num > 90 // trailing comment', expect: ['quote\'d "both"'],
  });

  // ================= datetime macros =================
  await check({ id: 'D01', promise: '"@now - the current datetime as string"', filter: 'when != "" && when < @now', expect: null, note: 'OBSERVED-ONLY (time dependent).' });
  await check({ id: 'D02', promise: '"@yearStart - beginning of the current year as datetime string" (current year 2026)', filter: 'when != "" && when < @yearStart', expect: ['100% pure'] });
  await check({ id: 'D03', promise: '"@year - @now year number"', filter: '@year = 2026', expect: ALL, note: 'a constant-true expression must not filter anything out' });
  await check({ id: 'D04', promise: '"@todayStart / @todayEnd"', filter: 'when >= @todayStart && when <= @todayEnd', expect: null, note: 'OBSERVED-ONLY.' });

  // ================= strftime / geoDistance =================
  await check({
    id: 'S01', promise: '"strftime(format, [time-value, ...]) returns a date string formatted according to the specified format argument"',
    filter: 'strftime(\'%Y-%m\', when) = "2026-01"', expect: ['Lorem ipsum'],
  });
  await check({
    id: 'S02', promise: '"The second (time-value) argument is optional ... If not set the function fallbacks to the current datetime."',
    filter: 'strftime(\'%Y\') = "2026"', expect: ALL,
  });
  await check({
    id: 'S03', promise: '"If the identifier cannot be resolved and converted to a numeric value, it resolves to null" (geoDistance)',
    filter: 'geoDistance(num, num, 23.32, 42.69) < 999999', expect: null, note: 'OBSERVED-ONLY: plain numbers are accepted per the doc ("the accepted arguments could be any plain number or collection field identifier").',
  });

  // ================= documented error responses =================
  await check({
    id: 'E01', promise: 'Documented 400 response for an invalid filter: {"status":400,"message":"Something went wrong while processing your request. Invalid filter.","data":{}}',
    filter: 'this is not a filter', expect: r => r.status === 400, note: 'checking status AND the documented message shape',
  });
  await check({
    id: 'E02', promise: 'Documented 403: {"status":403,"message":"Only superusers can filter by \'@collection.*\'"}',
    filter: '@collection.probe_tags.label ?= "alpha"', expect: r => r.status === 403,
  });
  await check({
    id: 'E03', promise: 'Same @collection filter, authenticated AS a superuser, must be allowed',
    filter: '@collection.probe_tags.label ?= "alpha"', token: TOKEN, expect: null, note: 'OBSERVED-ONLY.',
  });
  await check({
    id: 'E04', promise: '"Supported record sort fields: @random, @rowid, id, and any other collection field." — an unsupported one should not silently pass',
    path: '/api/collections/probe_items/records?perPage=100&sort=nosuchfield', expect: r => r.status === 400,
  });
  await check({
    id: 'E05', promise: '"Supported record filter fields: id, + any field from the collection schema." — an unknown field should not silently pass',
    filter: 'nosuchfield = "x"', expect: r => r.status === 400,
  });

  // ================= pagination =================
  await check({
    id: 'P01', promise: '"perPage Number The max returned records per page (default to 30)."',
    path: '/api/collections/probe_items/records', expect: r => r.body.perPage === 30,
    note: 'observed perPage value is printed below',
  });
  await check({
    id: 'P02', promise: '"page Number The page (aka. offset) of the paginated list (default to 1)."',
    path: '/api/collections/probe_items/records', expect: r => r.body.page === 1,
  });
  await check({
    id: 'P03', promise: 'perPage caps the number of returned records; totalItems counts all matches',
    path: '/api/collections/probe_items/records?perPage=3&sort=id',
    expect: r => r.body.items.length === 3 && r.body.totalItems === 7 && r.body.totalPages === 3,
  });
  await check({
    id: 'P04', promise: 'page beyond the last page',
    path: '/api/collections/probe_items/records?perPage=3&page=99&sort=id', expect: null, note: 'OBSERVED-ONLY: doc does not state the behaviour past the last page.',
  });
  await check({
    id: 'P05', promise: '"skipTotal Boolean If it is set the total counts query will be skipped and the response fields totalItems and totalPages will have -1 value."',
    path: '/api/collections/probe_items/records?perPage=3&skipTotal=1&sort=id',
    expect: r => r.body.totalItems === -1 && r.body.totalPages === -1,
  });
  await check({
    id: 'P06', promise: 'skipTotal=true (boolean spelling)',
    path: '/api/collections/probe_items/records?perPage=3&skipTotal=true&sort=id',
    expect: r => r.body.totalItems === -1 && r.body.totalPages === -1,
  });
  await check({
    id: 'P07', promise: 'skipTotal=false must NOT skip the totals (documented as "If it is set")',
    path: '/api/collections/probe_items/records?perPage=3&skipTotal=false&sort=id',
    expect: r => r.body.totalItems === 7,
    note: 'the doc says "If it is set" — the natural reading of skipTotal=false is: do not skip.',
  });
  await check({
    id: 'P08', promise: 'skipTotal=0 must NOT skip the totals',
    path: '/api/collections/probe_items/records?perPage=3&skipTotal=0&sort=id',
    expect: r => r.body.totalItems === 7,
  });
  await check({
    id: 'P09', promise: 'perPage=0 — doc gives no rule',
    path: '/api/collections/probe_items/records?perPage=0&sort=id', expect: null, note: 'OBSERVED-ONLY.',
  });
  await check({
    id: 'P10', promise: 'perPage negative — doc gives no rule',
    path: '/api/collections/probe_items/records?perPage=-1&sort=id', expect: null, note: 'OBSERVED-ONLY.',
  });
  await check({
    id: 'P11', promise: 'page=0 — doc gives no rule',
    path: '/api/collections/probe_items/records?perPage=3&page=0&sort=id', expect: null, note: 'OBSERVED-ONLY.',
  });

  // ================= sort =================
  await check({
    id: 'T01', promise: '"Add - / + (default) in front of the attribute for DESC / ASC order, eg. ?sort=-created,id"',
    path: '/api/collections/probe_items/records?perPage=100&sort=-num',
    expect: r => JSON.stringify(r.body.items.map(x => x.num)) === JSON.stringify([100, 10, 7, 5, 2, 0, -5]),
  });
  await check({
    id: 'T02', promise: '"+ (default)" — an explicit + prefix means ASC',
    path: '/api/collections/probe_items/records?perPage=100&sort=' + q('+num'),
    expect: r => JSON.stringify(r.body.items.map(x => x.num)) === JSON.stringify([-5, 0, 2, 5, 7, 10, 100]),
  });
  await check({
    id: 'T03', promise: '"Supported record sort fields: @random, @rowid, id"',
    path: '/api/collections/probe_items/records?perPage=100&sort=@rowid', expect: r => r.status === 200 && r.body.items.length === 7,
  });
  await check({
    id: 'T04', promise: '"Supported record sort fields: @random"',
    path: '/api/collections/probe_items/records?perPage=100&sort=@random', expect: r => r.status === 200 && r.body.items.length === 7,
    note: 'intentionally NOT compared across runs — @random is documented as random, so instability here is expected and is not a finding.',
  });

  // ================= expand =================
  await check({
    id: 'X01', promise: '"expand ... The expanded relations will be appended to the record under the expand property (e.g. \\"expand\\": {\\"relField1\\": {...}, ...})"',
    path: '/api/collections/probe_items/records?perPage=100&sort=id&expand=tags&filter=' + q('title = "Lorem ipsum"'),
    expect: r => r.body.items[0].expand && Array.isArray(r.body.items[0].expand.tags) && r.body.items[0].expand.tags.length === 2,
  });
  await check({
    id: 'X02', promise: 'expand of a relation field that is empty for that record',
    path: '/api/collections/probe_items/records?perPage=100&sort=id&expand=tags&filter=' + q('title = "100% pure"'),
    expect: null, note: 'OBSERVED-ONLY: doc does not state whether an empty relation yields an absent or empty expand key.',
  });
  await check({
    id: 'X03', promise: 'expand of a non-existing relation field — doc gives no rule',
    path: '/api/collections/probe_items/records?perPage=100&sort=id&expand=nosuchrel', expect: null, note: 'OBSERVED-ONLY.',
  });

  // ================= fields =================
  await check({
    id: 'C01', promise: '"fields String Comma separated string of the fields to return in the JSON response (by default returns all fields)."',
    path: '/api/collections/probe_items/records?perPage=100&sort=id&fields=title,num',
    expect: r => r.body.items.every(x => JSON.stringify(Object.keys(x).sort()) === JSON.stringify(['num', 'title'])),
  });
  await check({
    id: 'C02', promise: '":excerpt(maxLength, withEllipsis?) Returns a short plain text version of the field string value. Ex.: ?fields=*,description:excerpt(200,true)"',
    path: '/api/collections/probe_items/records?perPage=100&sort=id&fields=' + q('title:excerpt(4,true)') + '&filter=' + q('title = "Lorem ipsum"'),
    expect: null, note: 'OBSERVED-ONLY: the doc does not say whether maxLength counts the ellipsis. Recording the exact string.',
  });
  await check({
    id: 'C03', promise: ':excerpt without the ellipsis flag',
    path: '/api/collections/probe_items/records?perPage=100&sort=id&fields=' + q('title:excerpt(4)') + '&filter=' + q('title = "Lorem ipsum"'),
    expect: null, note: 'OBSERVED-ONLY.',
  });
  await check({
    id: 'C04', promise: '"* targets all keys from the specific depth level" — ?fields=*,expand.relField.name',
    path: '/api/collections/probe_items/records?perPage=100&sort=id&expand=tags&fields=' + q('*,expand.tags.label') + '&filter=' + q('title = "Lorem ipsum"'),
    expect: r => {
      const it = r.body.items[0];
      return it.expand && it.expand.tags.every(t => JSON.stringify(Object.keys(t)) === JSON.stringify(['label']));
    },
  });

  // ================= raw dumps for the checks above that print bodies =================
  console.log('\n==================== RAW BODIES FOR OBSERVED-ONLY CHECKS ====================');
  for (const r of results) {
    if (r.verdict === 'OBSERVED-ONLY' || r.verdict === 'DEVIATION') {
      console.log('\n[' + r.id + '] ' + r.request);
      console.log(JSON.stringify(r.body).slice(0, 2000));
    }
  }

  console.log('\n==================== SUMMARY ====================');
  const by = {};
  for (const r of results) by[r.verdict] = (by[r.verdict] || 0) + 1;
  console.log(JSON.stringify(by));
  for (const r of results) console.log(r.verdict.padEnd(14) + r.id + '  ' + (r.filter || r.request));
})();
