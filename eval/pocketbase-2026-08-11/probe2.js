// Second pass: targeted follow-ups on the candidates surfaced by probe.js.
// Same oracle rules: pocketbase.io/docs prose only, local instance only.
const BASE = process.env.PB_URL || 'http://127.0.0.1:8090';
const EMAIL = 'probe@example.com';
const PASS = 'Probe12345678';

async function req(method, path, body, token) {
  const h = {};
  if (body) h['Content-Type'] = 'application/json';
  if (token) h.Authorization = token;
  const r = await fetch(BASE + path, { method, headers: h, body: body ? JSON.stringify(body) : undefined });
  let j = null; try { j = await r.json(); } catch (_) {}
  return { status: r.status, body: j };
}
const q = encodeURIComponent;
async function show(id, promise, path, token, extract) {
  const a = await req('GET', path, null, token);
  const b = await req('GET', path, null, token);
  const stable = JSON.stringify(a.body) === JSON.stringify(b.body);
  console.log('--------------------------------------------------------------------');
  console.log('[' + id + ']  (2 identical runs: ' + stable + ')');
  console.log('  PROMISE : ' + promise);
  console.log('  REQUEST : GET ' + decodeURIComponent(path));
  console.log('  STATUS  : ' + a.status);
  console.log('  RESULT  : ' + (extract ? extract(a) : JSON.stringify(a.body).slice(0, 900)));
  return a;
}
const titles = r => JSON.stringify((r.body.items || []).map(x => x.title === '' ? '#' + x.note : x.title).sort()) + '  (totalItems=' + r.body.totalItems + ')';

(async () => {
  console.log('PocketBase probe pass 2 — ' + new Date().toISOString() + ' — pocketbase.exe 0.39.10');
  const auth = await req('POST', '/api/collections/_superusers/auth-with-password', { identity: EMAIL, password: PASS });
  const tok = auth.body.token;
  const I = '/api/collections/probe_items/records?perPage=100&sort=id&filter=';

  console.log('\n### A. Case sensitivity: the doc example "title ~ \\"Lorem%\\"" is said to return records whose title STARTS WITH "Lorem".');
  await show('A1', 'doc example verbatim: title ~ "Lorem%" -> "records where the title field value starts with \\"Lorem\\""', I + q('title ~ "Lorem%"'), null, titles);
  await show('A2', '"= Equal" — is it case sensitive? (doc does not say)', I + q('title = "lorem ipsum"'), null, titles);
  await show('A3', '"= Equal" exact case', I + q('title = "Lorem ipsum"'), null, titles);
  await show('A4', '":lower ... perform lower-case string comparisons" — documented as the way to get case-insensitive matching', I + q('title:lower = "lorem ipsum"'), null, titles);
  await show('A5', '~ against an upper-case operand', I + q('title ~ "LOREM"'), null, titles);
  await show('A6', 'non-ASCII: :lower "by default works only for ASCII characters, unless the ICU extension is loaded"', I + q('title:lower = "éé"'), null, titles);

  console.log('\n### B. :isset on a collection schema field — doc: "available only for the @request.* fields"');
  await show('B1', ':isset = true on a schema field', I + q('title:isset = true'), null, titles);
  await show('B2', ':isset = false on a schema field', I + q('title:isset = false'), null, titles);
  await show('B3', 'control: an unknown field is rejected with 400 ("Supported record filter fields: id, + any field from the collection schema")', I + q('nosuchfield = "x"'), null, r => JSON.stringify(r.body));
  await show('B4', ':changed on a schema field — doc: "available only for the @request.body.* fields"', I + q('title:changed = true'), null, titles);
  await show('B5', 'a completely made-up modifier', I + q('title:nosuchmodifier = true'), null, r => JSON.stringify(r.body));

  console.log('\n### C. "Any/At least one of" over an EMPTY multi-relation ("100% pure" and "back\\\\slash" have tags=[])');
  await show('C1', '"?= Any/At least one of Equal"', I + q('tags.label ?= "alpha"'), null, titles);
  await show('C2', '"?!= Any/At least one of NOT equal"', I + q('tags.label ?!= "alpha"'), null, titles);
  await show('C3', '"?~ Any/At least one of Like/Contains"', I + q('tags.label ?~ "alph"'), null, titles);
  await show('C4', '"?!~ Any/At least one of NOT Like/Contains"', I + q('tags.label ?!~ "alph"'), null, titles);
  await show('C5', 'a tag label that exists on NO record — ?!= must then be true for every record that has >=1 tag', I + q('tags.label ?!= "zzz"'), null, titles);
  await show('C6', 'De Morgan control: records NOT matching ?= "alpha"', I + q('tags.label ?= "alpha"'), null, titles);
  console.log('  ANALYSIS: if ?= excludes the empty-relation records but ?!= includes them, then for those records');
  console.log('            neither "at least one equal" nor its negation-free counterpart is grounded in an actual item.');

  console.log('\n### D. expand — doc: "Supports up to 6-levels depth nested relations expansion."');
  // build a chain n0 -> n1 -> ... -> n7 so that n0 can be expanded 7 levels deep
  for (let i = 7; i >= 0; i--) await req('DELETE', '/api/collections/chain' + i, null, tok);
  let prevId = null;
  for (let i = 7; i >= 0; i--) {
    const fields = [{ name: 'label', type: 'text' }];
    if (prevId) fields.push({ name: 'next', type: 'relation', collectionId: prevId, maxSelect: 1 });
    const r = await req('POST', '/api/collections', {
      name: 'chain' + i, type: 'base', fields,
      listRule: '', viewRule: '', createRule: '', updateRule: '', deleteRule: '',
    }, tok);
    if (r.status >= 400) { console.log('chain' + i + ' create failed', JSON.stringify(r.body)); break; }
    prevId = r.body.id;
  }
  let prevRec = null;
  for (let i = 7; i >= 0; i--) {
    const b = { label: 'L' + i };
    if (prevRec) b.next = prevRec;
    const r = await req('POST', '/api/collections/chain' + i + '/records', b, tok);
    if (r.status >= 400) { console.log('chain' + i + ' record failed', JSON.stringify(r.body)); break; }
    prevRec = r.body.id;
  }
  const depth = n => Array.from({ length: n }, () => 'next').join('.');
  function reached(r) {
    // count how many nested expand levels actually came back
    let node = (r.body.items || [])[0], d = 0;
    while (node && node.expand && node.expand.next) { d++; node = node.expand.next; }
    return 'levels expanded = ' + d + ' | deepest label = ' + (node ? node.label : 'n/a') + ' | status ' + r.status;
  }
  for (const n of [1, 5, 6, 7]) {
    await show('D' + n, '"Supports up to 6-levels depth nested relations expansion." — requesting ' + n + ' level(s)',
      '/api/collections/chain0/records?expand=' + q(depth(n)), null, reached);
  }
  await show('D8', 'requesting 7 levels — is the excess rejected (400) or silently truncated?',
    '/api/collections/chain0/records?expand=' + q(depth(7)), null, r => JSON.stringify(r.body).slice(0, 400));

  console.log('\n### E. expand of an unknown relation vs the 400 given for an unknown sort/filter field');
  await show('E1', 'unknown expand key', '/api/collections/probe_items/records?perPage=1&expand=nosuchrel', null, r => 'status ' + r.status + ' expandKeyPresent=' + ('expand' in (r.body.items[0] || {})));
  await show('E2', 'unknown sort field — doc lists the supported ones', '/api/collections/probe_items/records?perPage=1&sort=nosuchfield', null, r => JSON.stringify(r.body));
  await show('E3', 'expand a NON-relation field', '/api/collections/probe_items/records?perPage=1&expand=title', null, r => 'status ' + r.status + ' ' + JSON.stringify(r.body).slice(0, 200));

  console.log('\n### F. API rules: @request.query.* / @request.headers.* — doc: "the request query parameters as string values", "All header keys are normalized to lowercase and \\"-\\" is replaced with \\"_\\""');
  await req('PATCH', '/api/collections/probe_items', { listRule: '@request.headers.x_token = "secret"' }, tok);
  await (async () => {
    for (const [h, v] of [['X-Token', 'secret'], ['x-token', 'secret'], ['X-TOKEN', 'secret'], ['X-Token', 'wrong']]) {
      const r = await fetch(BASE + '/api/collections/probe_items/records?perPage=1', { headers: { [h]: v } });
      const j = await r.json();
      console.log('  header ' + h + ': ' + v + '  -> status ' + r.status + ' totalItems=' + j.totalItems);
    }
  })();
  await req('PATCH', '/api/collections/probe_items', { listRule: '@request.query.mytoken = "abc"' }, tok);
  for (const qs of ['mytoken=abc', 'mytoken=xyz', '']) {
    const r = await fetch(BASE + '/api/collections/probe_items/records?perPage=1&' + qs);
    const j = await r.json();
    console.log('  query "' + qs + '" -> status ' + r.status + ' totalItems=' + j.totalItems);
  }
  console.log('  PROMISE: "the API will return 200 empty items response in case a request doesn\'t satisfy a listRule"');
  await req('PATCH', '/api/collections/probe_items', { listRule: '' }, tok);

  console.log('\n### G. Documented rule status codes: 200 empty for listRule, 400 createRule, 404 view/update/deleteRule, 403 when locked');
  const one = (await req('GET', '/api/collections/probe_items/records?perPage=1')).body.items[0].id;
  for (const [name, rules] of [['unsatisfied', { listRule: 'num > 99999', viewRule: 'num > 99999', createRule: 'num > 99999', updateRule: 'num > 99999', deleteRule: 'num > 99999' }],
                               ['locked (null)', { listRule: null, viewRule: null, createRule: null, updateRule: null, deleteRule: null }]]) {
    await req('PATCH', '/api/collections/probe_items', rules, tok);
    const l = await req('GET', '/api/collections/probe_items/records?perPage=1');
    const v = await req('GET', '/api/collections/probe_items/records/' + one);
    const c = await req('POST', '/api/collections/probe_items/records', { title: 'x' });
    const u = await req('PATCH', '/api/collections/probe_items/records/' + one, { title: 'x' });
    const d = await req('DELETE', '/api/collections/probe_items/records/' + one);
    console.log('  ' + name + ': list=' + l.status + (l.status === 200 ? ' (items=' + l.body.items.length + ')' : '') +
      '  view=' + v.status + '  create=' + c.status + '  update=' + u.status + '  delete=' + d.status);
  }
  await req('PATCH', '/api/collections/probe_items', { listRule: '', viewRule: '', createRule: '', updateRule: '', deleteRule: '' }, tok);
  console.log('  EXPECTED per doc: unsatisfied -> list=200(0 items) create=400 view/update/delete=404 ; locked -> all 403');
})();
