#!/usr/bin/env node
// Sert le site EXACTEMENT comme GitHub Pages le publie : `site/` a la racine, et
// `examples/expense-demo/static-demo/` sous `/demo/`. La regle vit aussi dans
// `.github/workflows/pages.yml` (etapes `cp -r`) : c'est une duplication assumee, faute de
// pouvoir appeler un workflow depuis un test. Ce qui la garde honnete est le scenario
// QAIA-US-SITE-001-004 -- si les deux assemblages cessent de coincider, le sitemap et
// l'ensemble publie divergent et le test le dit.
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const MOUNTS = [
  { prefix: '/demo/', dir: path.join(ROOT, 'examples', 'expense-demo', 'static-demo') },
  { prefix: '/', dir: path.join(ROOT, 'site') },
];
const PORT = Number(process.env.PORT || 4700);

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.json': 'application/json; charset=utf-8',
};

function resolve(urlPath) {
  const clean = decodeURIComponent(urlPath.split('?')[0]);
  // `site/` n'est servi que par ce qu'il contient. Les artefacts QA vivent dans `site-qa/`,
  // volontairement HORS de `site/` : `pages.yml` copie `site/.` en entier, donc y deposer un
  // `node_modules` de test aurait publie des milliers de fichiers tiers sans que personne ne
  // le decide.
  for (const mount of MOUNTS) {
    if (!clean.startsWith(mount.prefix)) continue;
    let rel = clean.slice(mount.prefix.length);
    if (rel === '' || rel.endsWith('/')) rel += 'index.html';
    const target = path.join(mount.dir, rel);
    if (!target.startsWith(mount.dir)) return null; // traversee de chemin
    if (fs.existsSync(target) && fs.statSync(target).isFile()) return target;
  }
  return null;
}

http
  .createServer((req, res) => {
    const file = resolve(req.url);
    if (!file) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('404');
    }
    const body = fs.readFileSync(file);
    res.writeHead(200, {
      'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream',
      'Content-Length': body.length,
    });
    res.end(body);
  })
  .listen(PORT, () => console.log(`site served on http://127.0.0.1:${PORT}`));
