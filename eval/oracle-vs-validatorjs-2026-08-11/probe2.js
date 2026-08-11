// Seconde attaque, 2026-08-11 — après une première passe à zéro défaut.
//
// Ce qui change : on ne vise plus le coeur de compétence d'une bibliothèque mûre (Luhn, mod-97),
// mais **le code récent et les oracles parfaits**.
//
// « Oracle parfait » = une source de vérité qui ne se discute pas :
//   - isJson       -> `JSON.parse` du moteur lui-même définit ce qui est du JSON valide
//   - isISO31661   -> le registre ISO gelé
//   - isUUID       -> RFC 4122, une grammaire de longueur et de champs
'use strict';
const fs = require('fs');
const path = require('path');
const v = require('validator');

const ROOT = path.resolve(__dirname, '..', '..');
const iso = JSON.parse(fs.readFileSync(path.join(ROOT, 'eval/oracles-2026-08-09/iso-3166-4217.json'), 'utf8'));

const out = [];
const say = (s) => { out.push(s); console.log(s); };
say('# Seconde attaque — code récent et oracles parfaits — validator ' + require('validator/package.json').version);
say('');

// ------------------------------------------------------------- isJson vs JSON.parse
say('## isJson contre JSON.parse (le moteur est l\'oracle)');
say('');
const jsonCases = [
  '{}', '[]', 'null', 'true', 'false', '1', '1.5', '-0', '"a"', '""',
  '{"a":1}', '[1,2]', 'NaN', 'Infinity', '-Infinity', 'undefined',
  "{'a':1}", '{a:1}', '{"a":1,}', '[1,]', '01', '1.', '.5', '+1',
  '"\\u0000"', '{"a":1}{"b":2}', ' ', '', '\t', '{"__proto__":1}',
  '{"a":1,"a":2}', '"\\ud800"', '1e400', '[[[[[[[[[[1]]]]]]]]]]',
];
let jsonDiv = 0;
for (const s of jsonCases) {
  let truth;
  try { JSON.parse(s); truth = true; } catch (e) { truth = false; }
  let got;
  try { got = v.isJSON(s); } catch (e) { got = 'THROW:' + e.message; }
  if (truth !== got) { jsonDiv += 1; say('  ECART ' + JSON.stringify(s).padEnd(26) + 'JSON.parse=' + truth + '  isJson=' + got); }
}
say('  ' + jsonCases.length + ' cas, **' + jsonDiv + ' écart(s)**');
say('');

// ------------------------------------------------------------- ISO 3166 : Kosovo, ajouté 2026-02
say('## isISO31661 — le cas Kosovo, ajouté le 2026-02-06');
say('');
for (const [fn, codes] of [['isISO31661Alpha2', ['XK', 'FR', 'UK', 'EU', 'XX']],
                           ['isISO31661Alpha3', ['XXK', 'FRA', 'GBR', 'XXX']]]) {
  for (const c of codes) {
    const inRegistry = fn.endsWith('2') ? iso.alpha2.includes(c) : iso.alpha3.includes(c);
    const got = v[fn](c);
    const mark = inRegistry === got ? ' ' : '≠';
    say('  ' + mark + ' ' + fn + '("' + c + '") = ' + String(got).padEnd(6) + '| registre ISO gelé : ' + inRegistry);
  }
}
say('');

// ------------------------------------------------------------- isUUID, option "loose" 2025-04
say('## isUUID — option `loose`, ajoutée le 2025-04-14');
say('');
const uuids = [
  '00000000-0000-0000-0000-000000000000',
  'a1b2c3d4-e5f6-4789-8abc-def012345678',
  'A1B2C3D4-E5F6-4789-8ABC-DEF012345678',
  'a1b2c3d4e5f647898abcdef012345678',
  'a1b2c3d4-e5f6-4789-8abc-def01234567',
  'a1b2c3d4-e5f6-4789-8abc-def0123456789',
  'a1b2c3d4-e5f6-9789-8abc-def012345678',
  'g1b2c3d4-e5f6-4789-8abc-def012345678',
  'a1b2c3d4-e5f6-4789-cabc-def012345678',
];
for (const u of uuids) {
  let strict, loose;
  try { strict = v.isUUID(u); } catch (e) { strict = 'THROW'; }
  try { loose = v.isUUID(u, 'loose'); } catch (e) { loose = 'THROW:' + e.message; }
  say('  ' + u.padEnd(40) + 'defaut=' + String(strict).padEnd(6) + 'loose=' + loose);
}
say('');

// ------------------------------------------------------------- codes postaux recents
say('## Codes postaux ajoutés en 2025-2026 (AR, JO, MC, BD, PK, TW)');
say('');
const postal = {
  AR: [['C1425DKE', true], ['1425', true], ['X', false], ['C1425DK', false]],
  JO: [['11937', true], ['1193', false], ['119377', false]],
  MC: [['98000', true], ['98012', true], ['99000', false], ['9800', false]],
  BD: [['1000', true], ['100', false], ['10000', false]],
  PK: [['44000', true], ['4400', false]],
};
for (const [loc, cases] of Object.entries(postal)) {
  for (const [val, expected] of cases) {
    let got;
    try { got = v.isPostalCode(val, loc); } catch (e) { got = 'THROW'; }
    const mark = got === expected ? ' ' : '≠';
    say('  ' + mark + ' ' + loc + '  ' + String(val).padEnd(10) + 'attendu=' + String(expected).padEnd(6) + 'obtenu=' + got);
  }
}
say('');

// ------------------------------------------------------------- isTaxID en-IN, ajoute il y a une semaine
say('## isTaxID en-IN (PAN indien) — ajouté le 2026-08-04, il y a une semaine');
say('');
// Structure PAN : 5 lettres, 4 chiffres, 1 lettre. 4e caractere = type de detenteur
// (P individuel, C societe, H HUF, A AOP, B BOI, G gouvernement, J personne juridique,
// L autorite locale, F cabinet, T fiducie). 5e = premiere lettre du nom.
const pans = [
  ['ABCPE1234F', true, 'P = individuel, structure conforme'],
  ['ABCCE1234F', true, 'C = societe'],
  ['ABCZE1234F', false, 'Z n\'est pas un type de detenteur valide'],
  ['ABCPE1234', false, 'trop court'],
  ['ABCPE12345F', false, 'trop long'],
  ['abcpe1234f', false, 'minuscules'],
  ['ABC1E1234F', false, 'chiffre dans la zone alphabetique'],
  ['ABCPE12341', false, 'chiffre en derniere position'],
];
for (const [val, expected, why] of pans) {
  let got;
  try { got = v.isTaxID(val, 'en-IN'); } catch (e) { got = 'THROW:' + e.message.slice(0, 40); }
  const mark = got === expected ? ' ' : '≠';
  say('  ' + mark + ' ' + val.padEnd(13) + 'attendu=' + String(expected).padEnd(6) + 'obtenu=' + String(got).padEnd(6) + why);
}

fs.writeFileSync(path.join(__dirname, 'resultats2.txt'), out.join('\n') + '\n');
