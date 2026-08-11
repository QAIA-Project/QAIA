// Oracle indépendant contre validator.js — 2026-08-11.
//
// La règle qui rend l'exercice honnête : on ne teste PAS validator.js contre lui-même. La vérité
// vient soit d'un corpus autoritaire gelé (isemail, 163 adresses avec verdict), soit d'un calcul
// que l'on refait ici (Luhn mod-10, IBAN mod-97), soit d'un registre gelé (ISO 3166 / 4217).
//
// Et la discipline que notre propre bibliothèque impose : « valide » n'est pas une seule
// catégorie. Une adresse syntaxiquement valide mais couramment refusée ne prouve rien contre un
// validateur qui la refuse. Seules deux catégories permettent d'affirmer quelque chose :
//   - ISEMAIL_ERR            -> invalide sans discussion. L'accepter est un défaut.
//   - ISEMAIL_VALID_CATEGORY -> valide sans discussion. La refuser est un défaut.
// Tout le reste est rapporté et n'est JAMAIS compté comme un écart.
'use strict';

const fs = require('fs');
const path = require('path');
const v = require('validator');

const ROOT = path.resolve(__dirname, '..', '..');
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));

const email = read('eval/oracles-2026-08-09/rfc5322-isemail.json');
const iso = read('eval/oracles-2026-08-09/iso-3166-4217.json');

const out = [];
const say = (s) => { out.push(s); console.log(s); };

say('# Oracle indépendant contre validator.js ' + require('validator/package.json').version);
say('');
say('Sources gelées :');
say('  isemail   ' + email._source + '  sha256 ' + email._source_sha256.slice(0, 16) + '…');
say('  ISO       ' + iso._source.split(' ')[0] + '  sha256 ' + iso._source_sha256.slice(0, 16) + '…');
say('');

// ---------------------------------------------------------------- 1. RFC 5322 / isEmail
const decisive = { ISEMAIL_ERR: false, ISEMAIL_VALID_CATEGORY: true };
const emailDiv = [];
let decided = 0;
const byCat = {};
for (const c of email.cases) {
  let got;
  try { got = v.isEmail(c.address); } catch (e) { got = 'THROW:' + e.message; }
  byCat[c.category] = byCat[c.category] || { n: 0, accepted: 0 };
  byCat[c.category].n += 1;
  if (got === true) byCat[c.category].accepted += 1;
  if (c.category in decisive) {
    decided += 1;
    if (got !== decisive[c.category]) {
      emailDiv.push({ id: c.id, address: c.address, cat: c.category, diag: c.diagnosis, expected: decisive[c.category], got });
    }
  }
}
say('## 1. isEmail contre le corpus isemail');
say('');
say('Cas tranchants (ERR + VALID_CATEGORY) : ' + decided + ' — écarts : **' + emailDiv.length + '**');
for (const d of emailDiv) {
  say('  [' + d.cat + ' #' + d.id + '] ' + JSON.stringify(d.address) + '  attendu=' + d.expected + ' obtenu=' + d.got + '  (' + d.diag + ')');
}
say('');
say('Catégories non tranchantes — rapportées, jamais comptées comme un écart :');
for (const [cat, s] of Object.entries(byCat)) {
  if (cat in decisive) continue;
  say('  ' + cat.padEnd(24) + s.accepted + '/' + s.n + ' acceptées par validator.js');
}
say('');

// ---------------------------------------------------------------- 2. ISO 3166
const a2 = iso.alpha2.filter((c) => !v.isISO31661Alpha2(c));
const a3 = iso.alpha3.filter((c) => !v.isISO31661Alpha3(c));
say('## 2. ISO 3166 contre le registre gelé');
say('');
say('alpha-2 : ' + iso.alpha2.length + ' codes du registre, **' + a2.length + '** refusés par validator.js' + (a2.length ? ' → ' + a2.join(' ') : ''));
say('alpha-3 : ' + iso.alpha3.length + ' codes du registre, **' + a3.length + '** refusés par validator.js' + (a3.length ? ' → ' + a3.join(' ') : ''));
say('');

// ---------------------------------------------------------------- 3. ISO 4217
// Le registre est indexé PAR PAYS : son silence ne prouve pas qu'un code n'est pas enregistré.
// On ne teste donc QUE dans le sens qui conclut : un code présent doit être accepté.
const cur = Object.keys(iso.currency_minor_units);
const curRej = cur.filter((c) => !v.isISO4217(c));
say('## 3. ISO 4217 contre le registre gelé (sens unique, cf. caveat du registre)');
say('');
say(cur.length + ' codes en usage dans le registre, **' + curRej.length + '** refusés par validator.js' + (curRej.length ? ' → ' + curRej.join(' ') : ''));
say('XXX (assigné par ISO 4217 à « aucune devise ») : validator.isISO4217("XXX") = ' + v.isISO4217('XXX'));
say('');

// ---------------------------------------------------------------- 4. Luhn — calculé, pas recopié
function luhnOk(num) {
  const d = num.replace(/\D/g, '');
  if (d.length < 2) return false;
  let sum = 0, dbl = false;
  for (let i = d.length - 1; i >= 0; i--) {
    let n = Number(d[i]);
    if (dbl) { n *= 2; if (n > 9) n -= 9; }
    sum += n; dbl = !dbl;
  }
  return sum % 10 === 0;
}
const pans = ['4111111111111111', '4012888888881881', '5555555555554444', '378282246310005',
  '6011111111111117', '4111111111111112', '1234567890123456', '0000000000000001',
  '4111111111111', '41111111111111111'];
say('## 4. Luhn (ISO/IEC 7812) — somme de contrôle recalculée ici');
say('');
const luhnDiv = [];
for (const p of pans) {
  const mine = luhnOk(p), theirs = v.isCreditCard(p);
  const mark = mine === theirs ? ' ' : '≠';
  say('  ' + mark + ' ' + p.padEnd(18) + 'luhn=' + String(mine).padEnd(6) + 'isCreditCard=' + theirs);
  if (mine !== theirs) luhnDiv.push(p);
}
say('');
say('  Note : un écart n\'est pas forcément un défaut — `isCreditCard` vérifie AUSSI la longueur');
say('  et le préfixe réseau, ce que Luhn seul ne fait pas. Seul le sens « Luhn faux mais accepté »');
say('  serait un vrai défaut.');
say('');

// ---------------------------------------------------------------- 5. IBAN — mod-97 recalculé
function ibanOk(iban) {
  const s = iban.replace(/\s+/g, '').toUpperCase();
  if (!/^[A-Z]{2}[0-9]{2}[A-Z0-9]+$/.test(s)) return false;
  const re = s.slice(4) + s.slice(0, 4);
  let rem = 0;
  for (const ch of re) {
    const val = /[0-9]/.test(ch) ? ch : String(ch.charCodeAt(0) - 55);
    for (const c of val) rem = (rem * 10 + Number(c)) % 97;
  }
  return rem === 1;
}
const ibans = ['FR1420041010050500013M02606', 'GB82WEST12345698765432', 'DE89370400440532013000',
  'FR1420041010050500013M02607', 'GB82WEST1234569876543', 'fr1420041010050500013m02606'];
say('## 5. IBAN (ISO 13616) — mod-97 recalculé ici');
say('');
const ibanDiv = [];
for (const i of ibans) {
  const mine = ibanOk(i), theirs = v.isIBAN(i);
  const mark = mine === theirs ? ' ' : '≠';
  say('  ' + mark + ' ' + i.padEnd(30) + 'mod97=' + String(mine).padEnd(6) + 'isIBAN=' + theirs);
  if (mine !== theirs) ibanDiv.push({ i, mine, theirs });
}
say('');
say('## Bilan des écarts DÉCISIFS');
say('');
say('  isEmail  : ' + emailDiv.length);
say('  ISO 3166 : ' + (a2.length + a3.length));
say('  ISO 4217 : ' + curRej.length);
say('  IBAN     : ' + ibanDiv.length);

fs.writeFileSync(path.join(__dirname, 'resultats.txt'), out.join('\n') + '\n');
