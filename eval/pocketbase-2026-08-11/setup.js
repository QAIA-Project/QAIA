// Campaign setup: builds the fixture schema + records on a LOCAL PocketBase instance.
// Oracle = https://pocketbase.io/docs/ only. No PocketBase source was read.
const BASE = process.env.PB_URL || 'http://127.0.0.1:8090';
const EMAIL = 'probe@example.com';
const PASS = 'Probe12345678';

async function req(method, path, body, token) {
  const h = { 'Content-Type': 'application/json' };
  if (token) h.Authorization = token;
  const r = await fetch(BASE + path, { method, headers: h, body: body ? JSON.stringify(body) : undefined });
  let j = null;
  try { j = await r.json(); } catch (_) {}
  return { status: r.status, body: j };
}

(async () => {
  const auth = await req('POST', '/api/collections/_superusers/auth-with-password', { identity: EMAIL, password: PASS });
  if (!auth.body || !auth.body.token) { console.error('AUTH FAILED', JSON.stringify(auth)); process.exit(1); }
  const tok = auth.body.token;

  // wipe previous fixtures if present
  for (const c of ['probe_items', 'probe_tags']) {
    await req('DELETE', '/api/collections/' + c, null, tok);
  }

  let r = await req('POST', '/api/collections', {
    name: 'probe_tags', type: 'base',
    fields: [{ name: 'label', type: 'text' }],
    listRule: '', viewRule: '', createRule: '', updateRule: '', deleteRule: '',
  }, tok);
  console.log('create probe_tags', r.status, r.status >= 400 ? JSON.stringify(r.body) : '');
  const tagsId = r.body.id;

  r = await req('POST', '/api/collections', {
    name: 'probe_items', type: 'base',
    fields: [
      { name: 'title', type: 'text' },
      { name: 'note', type: 'text' },
      { name: 'num', type: 'number' },
      { name: 'flag', type: 'bool' },
      { name: 'when', type: 'date' },
      { name: 'opts', type: 'select', maxSelect: 5, values: ['a', 'b', 'c', 'pb_x', 'pb_y'] },
      { name: 'tags', type: 'relation', collectionId: tagsId, maxSelect: 5 },
    ],
    listRule: '', viewRule: '', createRule: '', updateRule: '', deleteRule: '',
  }, tok);
  console.log('create probe_items', r.status, r.status >= 400 ? JSON.stringify(r.body) : '');

  const tagIds = {};
  for (const label of ['alpha', 'beta', 'gamma']) {
    const t = await req('POST', '/api/collections/probe_tags/records', { label }, tok);
    tagIds[label] = t.body.id;
  }

  const items = [
    { title: 'Lorem ipsum',      note: 'plain',    num: 10,  flag: true,  when: '2026-01-15 10:00:00Z', opts: ['a', 'b'],       tags: [tagIds.alpha, tagIds.beta] },
    { title: 'lorem lower',      note: '',         num: 0,   flag: false, when: '2026-02-15 10:00:00Z', opts: ['a'],            tags: [tagIds.alpha] },
    { title: '100% pure',        note: 'pct',      num: -5,  flag: false, when: '2025-12-31 23:59:59Z', opts: [],               tags: [] },
    { title: 'under_score',      note: 'us',       num: 5,   flag: true,  when: '2026-03-01 00:00:00Z', opts: ['pb_x', 'pb_y'], tags: [tagIds.gamma] },
    { title: "quote'd \"both\"", note: 'q',        num: 100, flag: false, when: '', opts: ['c'],         tags: [tagIds.beta, tagIds.gamma] },
    { title: '',                 note: 'emptytit', num: 2,   flag: true,  when: '2026-04-01 12:00:00Z', opts: ['b', 'c'],       tags: [tagIds.alpha, tagIds.beta, tagIds.gamma] },
    { title: 'back\\slash',      note: 'bs',       num: 7,   flag: false, when: '2026-05-01 12:00:00Z', opts: ['a', 'c'],       tags: [] },
  ];
  for (const it of items) {
    const res = await req('POST', '/api/collections/probe_items/records', it, tok);
    if (res.status >= 400) console.log('item fail', JSON.stringify(it.title), res.status, JSON.stringify(res.body));
  }
  const all = await req('GET', '/api/collections/probe_items/records?perPage=100&sort=num', null, tok);
  console.log('records created:', all.body.totalItems);
  console.log('TAGS', JSON.stringify(tagIds));
})();
