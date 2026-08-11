// MINIMAL STANDALONE REPRODUCTION — independent of the rest of the campaign fixture.
// Creates its own two collections and three records, runs the filters, prints the table.
//
//   1) download pocketbase 0.39.10, then:
//        ./pocketbase superuser upsert probe@example.com Probe12345678
//        ./pocketbase serve --http=127.0.0.1:8090
//   2) node repro.js
//
// Oracle: https://pocketbase.io/docs/api-rules-and-filters/ (prose only).
const BASE = process.env.PB_URL || 'http://127.0.0.1:8090';
const EMAIL = 'probe@example.com';
const PASS = 'Probe12345678';
const q = encodeURIComponent;

async function api(m, p, b, t) {
  const h = {};
  if (b) h['Content-Type'] = 'application/json';
  if (t) h.Authorization = t;
  const r = await fetch(BASE + p, { method: m, headers: h, body: b ? JSON.stringify(b) : undefined });
  let j = null; try { j = await r.json(); } catch (_) {}
  return { status: r.status, body: j };
}

(async () => {
  console.log('MINIMAL REPRO — ' + new Date().toISOString() + ' — pocketbase.exe 0.39.10 (windows_amd64)');
  const tok = (await api('POST', '/api/collections/_superusers/auth-with-password', { identity: EMAIL, password: PASS })).body.token;
  for (const c of ['repro_posts', 'repro_cats']) await api('DELETE', '/api/collections/' + c, null, tok);
  const R = { listRule: '', viewRule: '', createRule: '', updateRule: '', deleteRule: '' };

  const cats = (await api('POST', '/api/collections', { name: 'repro_cats', type: 'base', fields: [{ name: 'name', type: 'text' }], ...R }, tok)).body;
  await api('POST', '/api/collections', {
    name: 'repro_posts', type: 'base',
    fields: [{ name: 'title', type: 'text' }, { name: 'cats', type: 'relation', collectionId: cats.id, maxSelect: 3, required: false }],
    ...R,
  }, tok);

  const news = (await api('POST', '/api/collections/repro_cats/records', { name: 'news' }, tok)).body.id;
  const tech = (await api('POST', '/api/collections/repro_cats/records', { name: 'tech' }, tok)).body.id;
  await api('POST', '/api/collections/repro_posts/records', { title: 'A_has_news', cats: [news] }, tok);
  await api('POST', '/api/collections/repro_posts/records', { title: 'B_has_tech', cats: [tech] }, tok);
  await api('POST', '/api/collections/repro_posts/records', { title: 'C_has_NOTHING', cats: [] }, tok);

  console.log('\nFixture: 3 posts.   A_has_news -> [news]   B_has_tech -> [tech]   C_has_NOTHING -> [] (empty relation)\n');

  const filters = [
    'cats.name ?= "news"', 'cats.name ?!= "news"', 'cats.name ?~ "news"', 'cats.name ?!~ "news"',
    'cats.name ?> "news"', 'cats.name ?>= "news"', 'cats.name ?< "news"', 'cats.name ?<= "news"',
    'cats.name = "news"', 'cats.name != "news"', 'cats.name ~ "news"', 'cats.name !~ "news"',
  ];
  const rows = [];
  for (const f of filters) {
    const p = '/api/collections/repro_posts/records?perPage=10&sort=title&filter=' + q(f);
    const a = (await api('GET', p)).body;
    const b = (await api('GET', p)).body;               // second identical run
    const t = (a.items || []).map(x => x.title);
    rows.push([f, JSON.stringify(t), t.includes('C_has_NOTHING') ? 'YES' : 'no', String(JSON.stringify(a) === JSON.stringify(b))]);
  }

  console.log('filter'.padEnd(22) + '| matched'.padEnd(44) + '| C (empty rel) matched? | 2 runs identical');
  console.log('-'.repeat(112));
  for (const r of rows) console.log(r[0].padEnd(22) + '| ' + r[1].padEnd(42) + '| ' + r[2].padEnd(22) + ' | ' + r[3]);

  console.log('\nPer https://pocketbase.io/docs/api-rules-and-filters/ the eight "?" operators share one gloss:');
  console.log('  "?!= Any/At least one of NOT equal"   /   "?!~ Any/At least one of NOT Like/Contains"  (etc.)');
  console.log('\nOBSERVED: of the eight, ?!= alone reports a match for a record whose relation is empty.');
  console.log('Its match-all counterpart != does the same, while !~ / ?!~ do not.');
  console.log('A record with zero related items has no item that "is not news", so ?= and ?!= both being');
  console.log('false for C would be self-consistent; ?= false + ?!= true is not.');
})();
