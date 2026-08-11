// Third pass: the empty-multi-value matrix.
// Doc gives ?= ?!= ?~ ?!~ ?> ?>= ?< ?<= a single, uniform gloss: "Any/At least one of <op>".
// A uniform quantifier must behave uniformly on an EMPTY array. This enumerates it.
const BASE = process.env.PB_URL || 'http://127.0.0.1:8090';
const q = encodeURIComponent;

// fixture recap (probe_items):
//   tags=[]  -> "100% pure", "back\slash"          opts=[] -> "100% pure"
//   tags=[alpha] -> "lorem lower"
//   tags=[alpha,beta] -> "Lorem ipsum"
//   tags=[gamma] -> "under_score"
//   tags=[beta,gamma] -> quote'd
//   tags=[alpha,beta,gamma] -> #emptytit
const EMPTY_REL = ['100% pure', 'back\\slash'];

async function run(filter) {
  const p = '/api/collections/probe_items/records?perPage=100&sort=id&filter=' + q(filter);
  const a = await fetch(BASE + p).then(r => r.json());
  const b = await fetch(BASE + p).then(r => r.json());
  const stable = JSON.stringify(a) === JSON.stringify(b);
  const t = (a.items || []).map(x => x.title === '' ? '#' + x.note : x.title).sort();
  return { t, stable, status: a.status || 200, raw: a };
}

(async () => {
  console.log('PocketBase probe pass 3 — ' + new Date().toISOString() + ' — pocketbase.exe 0.39.10');
  console.log('Question: for a record whose multi-valued field is EMPTY, does an "Any/At least one of X"');
  console.log('operator report a match? The documentation gives all 8 of them the same gloss, so the');
  console.log('answer must be the same for all 8.\n');

  const cases = [
    ['?=  Any/At least one of Equal',              'tags.label ?= "alpha"'],
    ['?!= Any/At least one of NOT equal',          'tags.label ?!= "alpha"'],
    ['?~  Any/At least one of Like/Contains',      'tags.label ?~ "alph"'],
    ['?!~ Any/At least one of NOT Like/Contains',  'tags.label ?!~ "alph"'],
    ['?>  Any/At least one of Greater than',       'tags.label ?> "alpha"'],
    ['?>= Any/At least one of Greater or equal',   'tags.label ?>= "alpha"'],
    ['?<  Any/At least one of Less than',          'tags.label ?< "alpha"'],
    ['?<= Any/At least one of Less or equal',      'tags.label ?<= "alpha"'],
  ];

  console.log('=== A. multi-RELATION (tags), empty for: ' + JSON.stringify(EMPTY_REL) + ' ===');
  const verdicts = {};
  for (const [gloss, f] of cases) {
    const r = await run(f);
    const hits = EMPTY_REL.filter(e => r.t.includes(e));
    verdicts[f] = hits.length;
    console.log('  ' + gloss.padEnd(46) + f.padEnd(28) +
      ' -> empty-relation records matched: ' + hits.length + '/2 ' + JSON.stringify(hits) +
      '   (stable=' + r.stable + ', total=' + r.t.length + ')');
  }

  console.log('\n=== B. same operators on a multi-SELECT (opts), empty for: ["100% pure"] ===');
  for (const [gloss, f0] of cases) {
    const f = f0.replace('tags.label', 'opts');
    const r = await run(f);
    console.log('  ' + gloss.padEnd(46) + f.padEnd(28) +
      ' -> "100% pure" matched: ' + r.t.includes('100% pure') + '   (stable=' + r.stable + ', total=' + r.t.length + ')');
  }

  console.log('\n=== C. control: the match-all (non-"?") counterparts on the same empty relation ===');
  for (const f of ['tags.label = "alpha"', 'tags.label != "alpha"', 'tags.label ~ "alph"', 'tags.label !~ "alph"']) {
    const r = await run(f);
    const hits = EMPTY_REL.filter(e => r.t.includes(e));
    console.log('  ' + f.padEnd(28) + ' -> empty-relation records matched: ' + hits.length + '/2   (total=' + r.t.length + ')');
  }

  console.log('\n=== D. control: the SAME operators on a value present on no record at all (no empty-set involved) ===');
  for (const f of ['tags.label ?= "zzz"', 'tags.label ?!= "zzz"', 'tags.label ?~ "zzz"', 'tags.label ?!~ "zzz"']) {
    const r = await run(f);
    console.log('  ' + f.padEnd(28) + ' -> ' + JSON.stringify(r.t) + '  (total=' + r.t.length + ')');
  }

  console.log('\n=== E. reproduction, 5 consecutive runs of the two operators that disagree ===');
  for (let i = 1; i <= 5; i++) {
    const a = await run('tags.label ?!= "alpha"');
    const b = await run('tags.label ?!~ "alph"');
    console.log('  run ' + i + ': ?!=  empty-rel matched=' + EMPTY_REL.filter(e => a.t.includes(e)).length +
      '/2  total=' + a.t.length + '   |   ?!~  empty-rel matched=' + EMPTY_REL.filter(e => b.t.includes(e)).length +
      '/2  total=' + b.t.length);
  }

  console.log('\nCONCLUSION SHAPE: ?!= counts an empty array as "at least one of them is not alpha";');
  console.log('?!~ does not. The documentation words them identically.');
})();
