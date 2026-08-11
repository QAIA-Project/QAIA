"use strict";
// PROBE 9 — documented promise for the status page slug (src/lang/en.json):
//   "Alphanumerical string and hyphens only"
// Each candidate slug is submitted through addStatusPage; accepted slugs are then fetched
// through the public API to see whether the page they created is reachable.
const { Session } = require("./lib");

const CASES = [
    [ "plain lowercase", "probe-slug-a", true ],
    [ "with hyphen", "probe-b-c", true ],
    [ "digits", "probe123", true ],
    [ "underscore", "probe_d", false ],
    [ "uppercase", "ProbeE", false ],
    [ "space", "probe f", false ],
    [ "accented letter", "probé", false ],
    [ "slash", "probe/g", false ],
    [ "dot", "probe.h", false ],
    [ "leading hyphen", "-probei", false ],
    [ "empty", "", false ],
];

(async () => {
    const sess = await Session.open();
    let notes = [];
    for (const [ name, slug, expectAccept ] of CASES) {
        let res;
        try {
            res = await sess.emit("addStatusPage", "probe " + name, slug);
        } catch (e) {
            res = { ok: false, msg: "exception: " + e.message };
        }
        const accepted = !!res.ok;
        let reachable = "n/a";
        if (accepted) {
            try {
                const r = await fetch("http://127.0.0.1:3001/api/status-page/" + encodeURIComponent(slug));
                reachable = r.status;
            } catch (e) { reachable = "fetch error"; }
        }
        const tag = accepted === expectAccept ? "OK  " : "DIFF";
        if (tag === "DIFF") notes.push(name);
        console.log(`${tag} ${name.padEnd(16)} slug=${JSON.stringify(slug)} accepted=${accepted} apiStatus=${reachable} msg=${JSON.stringify(res.msg || "")}`);
        if (accepted) await sess.emit("deleteStatusPage", slug);
    }
    console.log(`\nRESULT: ${notes.length} deviation(s): ${notes.join(", ") || "none"}`);
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
