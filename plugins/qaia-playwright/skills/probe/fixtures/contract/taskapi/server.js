// TaskAPI — minimal fixture SUT for contract-probe's validation. No external deps.
//
// DELIBERATE DEFECT (for the fixture only, never presented as production code): the GET
// /tasks/:id handler below looks up `tasks[id]` after `Number(id)` without checking the result
// is a valid, finite integer. A happy-path test ("GET /tasks/1" -> 200, "GET /tasks/999" -> 404)
// never notices anything wrong. An ADVERSARIAL probe against the README's promise #2 ("never a
// 5xx, for any input") does: sending a non-numeric, deeply-nested, or absurd id crashes the
// lookup (accessing an array with a NaN/negative index doesn't throw in JS, but the *next*
// line that reads `.title` off `undefined` after a malformed id slips past a naive `!id` guard
// does) -> unhandled exception -> Node's default error handling -> 500, violating the
// documented contract. This is the exact "contract violation, not just crash-vs-no-crash"
// distinction contract-probe is built to catch.
const http = require('http');

let tasks = []; // index 0 unused; ids are 1-based to make the defect reachable via id "0"

function json(res, code, obj) { res.writeHead(code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(obj)); }
function body(req) { return new Promise((r) => { let d = ''; req.on('data', (c) => (d += c)); req.on('end', () => { try { r(JSON.parse(d || '{}')); } catch { r({}); } }); }); }

async function route(req, res) {
  const u = new URL(req.url, 'http://x');
  const p = u.pathname;

  if (p === '/tasks' && req.method === 'POST') {
    const b = await body(req);
    const title = typeof b.title === 'string' ? b.title.trim() : '';
    if (!title) return json(res, 422, { error: 'title is required' });
    const id = tasks.length + 1;
    const task = { id, title };
    tasks[id] = task;
    return json(res, 201, task);
  }

  const m = p.match(/^\/tasks\/(.+)$/);
  if (m && req.method === 'GET') {
    const raw = m[1];
    const id = Number(raw); // <- the defect: no Number.isInteger/finite guard before use below
    if (!id) return json(res, 404, { error: 'not found' }); // catches 0/NaN/empty, looks safe...
    const task = tasks[id];
    // ...but a value like "1e2" or "1.5" or "99999999999999999999" passes the `!id` guard
    // (truthy, non-zero) yet is not a valid array index QAIA's own task ever created — `task`
    // is `undefined`, and this line's `.title` access throws.
    return json(res, 200, { id: task.id, title: task.title });
  }

  return json(res, 404, { error: 'unknown route' });
}

// A real production app almost always has SOME top-level error boundary (an Express error
// middleware, a process-level uncaughtException handler) that turns a thrown error into a
// 500 response rather than letting the whole process die — that boundary itself is not the
// injected defect and is kept here so the fixture demonstrates a clean, observable contract
// violation (500 instead of the promised 404) rather than a denial-of-service, which would be
// a different, cruder defect class than the one this skill targets.
const server = http.createServer((req, res) => {
  route(req, res).catch(() => json(res, 500, { error: 'internal error' }));
});

server.listen(4600, () => console.log('TaskAPI fixture on http://localhost:4600'));
