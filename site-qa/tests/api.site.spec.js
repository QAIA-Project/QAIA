// Genere depuis ../qaia-journey/testbooks/US-SITE-001/published-contract.feature
// Un bloc par scenario, titre portant l'identifiant QAIA et l'AC. Statut asserte en premier.
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const SITE_DIR = path.resolve(__dirname, '..', '..', 'site');
const DEMO_DIR = path.resolve(__dirname, '..', '..', 'examples', 'expense-demo', 'static-demo');

const DECLARED = ['/', '/compare.html', '/walkthrough.html', '/demo/', '/llms.txt', '/robots.txt', '/sitemap.xml'];

for (const declaredPath of DECLARED) {
  test(`@QAIA-US-SITE-001-001 @AC5 "${declaredPath}" is served`, async ({ request }) => {
    const res = await request.get(declaredPath);
    expect(res.status()).toBe(200);
  });
}

test('@QAIA-US-SITE-001-002 @AC5 an address never published is not served', async ({ request }) => {
  const res = await request.get('/this-page-was-never-published.html');
  expect(res.status()).toBe(404);
});

test('@QAIA-US-SITE-001-003 @AC6 robots.txt points at a sitemap that answers', async ({ request }) => {
  const res = await request.get('/robots.txt');
  expect(res.status()).toBe(200);
  const body = await res.text();
  const declared = body.match(/^\s*Sitemap:\s*(\S+)\s*$/im);
  expect(declared, 'robots.txt must declare a Sitemap: line').not.toBeNull();
  // Le robots publie l'URL de PRODUCTION ; on verifie que le chemin qu'elle designe est servi.
  const sitemapPath = new URL(declared[1]).pathname.replace(/^\/QAIA/, '') || '/sitemap.xml';
  const sitemap = await request.get(sitemapPath);
  expect(sitemap.status()).toBe(200);
});

test('@QAIA-US-SITE-001-004 @AC6 the sitemap lists exactly the published entry points', async ({ request }) => {
  const res = await request.get('/sitemap.xml');
  expect(res.status()).toBe(200);
  const xml = await res.text();

  const listed = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)]
    .map((m) => new URL(m[1]).pathname.replace(/^\/QAIA/, '') || '/')
    .sort();

  // Ce que le site publie reellement, lu sur le disque comme `pages.yml` l'assemble : les pages
  // HTML de premier niveau, plus `/demo/`. Defaut sur applique a la question ouverte Q2 -- les
  // fichiers destines aux machines (robots, sitemap, llms) ne s'indexent pas eux-memes.
  const published = fs
    .readdirSync(SITE_DIR)
    .filter((f) => f.endsWith('.html'))
    .map((f) => (f === 'index.html' ? '/' : `/${f}`));
  if (fs.existsSync(path.join(DEMO_DIR, 'index.html'))) published.push('/demo/');
  published.sort();

  expect(listed, 'toute URL du sitemap doit etre publiee, et toute page publiee doit y figurer')
    .toEqual(published);

  for (const p of listed) {
    const page = await request.get(p);
    expect(page.status(), `${p} listed in the sitemap`).toBe(200);
  }
});

for (const htmlPath of ['/', '/compare.html', '/walkthrough.html']) {
  test(`@QAIA-US-SITE-001-005 @AC5 "${htmlPath}" is served as HTML`, async ({ request }) => {
    const res = await request.get(htmlPath);
    expect(res.status()).toBe(200);
    expect(res.headers()['content-type']).toContain('text/html');
  });
}

test('@QAIA-US-SITE-001-006 @AC6 llms.txt is served and is not empty', async ({ request }) => {
  const res = await request.get('/llms.txt');
  expect(res.status()).toBe(200);
  expect((await res.text()).length).toBeGreaterThan(200);
});

test('@QAIA-US-SITE-001-007 @AC5 the demo is served from the second assembly source', async ({ request }) => {
  const res = await request.get('/demo/index.html');
  expect(res.status()).toBe(200);
  expect((await res.text()).toLowerCase()).toContain('expense');
});
