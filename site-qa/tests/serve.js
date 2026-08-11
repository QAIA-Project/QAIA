#!/usr/bin/env node
// Sert le site comme GitHub Pages le publie : `site/` a la racine, et
// `examples/expense-demo/static-demo/` sous `/demo/`. La regle d'assemblage vit aussi dans
// `.github/workflows/pages.yml` (etapes `cp -r`), faute de pouvoir appeler un workflow depuis
// un test.
//
// CE QUE CETTE DUPLICATION N'EST PAS COUVERTE PAR -- ecrit ici parce que ce fichier a affirme
// le contraire jusqu'au 2026-08-11. Il disait que le scenario QAIA-US-SITE-001-004 rattrapait
// toute divergence. C'est faux, et une relecture l'a demontre par quatre contre-exemples :
// supprimer l'etape demo de `pages.yml`, y ajouter un troisieme `cp -r`, ou changer le point de
// montage laissent la suite VERTE et la production cassee -- parce que le test compare le
// DISQUE au sitemap, et ne lit jamais `pages.yml`.
// Seul cas reellement couvert : un fichier ajoute ou retire DANS `site/`.
// Une garantie inventee dans un commentaire est la dette la plus chere : la personne suivante
// lui fait confiance. Le trou est donc ecrit, pas repare a moitie.
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
    // `startsWith` sur une chaine nue laissait sortir du montage : `…/QAIA/site` est un prefixe
    // de `…/QAIA/site-qa`, donc `/../site-qa/tests/serve.js` etait servi -- node_modules compris.
    // Trouve le 2026-08-11 par une relecture « developpeur », avec la requete qui le prouve.
    const inside = path.relative(mount.dir, target);
    if (inside.startsWith('..') || path.isAbsolute(inside)) return null;
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
  .listen(PORT, '127.0.0.1', () => console.log(`site served on http://127.0.0.1:${PORT}`));
