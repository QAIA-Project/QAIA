"use strict";
// PROBE 3 — several documented semantics, checked in parallel against one controlled target.
// Promises (src/lang/en.json):
//   acceptedStatusCodesDescription: "Select status codes which are considered as a successful response."
//   upsideDownModeDescription: "Flip the status upside down. If the service is reachable, it is DOWN."
//   keywordDescription: "Search keyword in plain HTML or JSON response. The search is case-sensitive."
//   invertKeywordDescription: "Look for the keyword to be absent rather than present."
const { Session, ctl, targetReset, sleep, waitFor } = require("./lib");

const CASES = [
    // name, monitor overrides, expected first non-pending status
    [ "status 503 vs accepted 200-299", { accepted_statuscodes: [ "200-299" ] }, "DOWN" ],
    [ "status 503 vs accepted 500-599", { accepted_statuscodes: [ "500-599" ] }, "UP" ],
    [ "status 503 vs accepted 503", { accepted_statuscodes: [ "503" ] }, "UP" ],
    [ "status 503 vs accepted 502", { accepted_statuscodes: [ "502" ] }, "DOWN" ],
    [ "upsideDown, reachable+accepted(500-599)", { accepted_statuscodes: [ "500-599" ], upsideDown: true }, "DOWN" ],
    [ "upsideDown, reachable+rejected(200-299)", { accepted_statuscodes: [ "200-299" ], upsideDown: true }, "UP" ],
    [ "keyword 'needle' present (case exact)", { type: "keyword", keyword: "needle", accepted_statuscodes: [ "500-599" ] }, "UP" ],
    [ "keyword 'NEEDLE' wrong case -> case-sensitive", { type: "keyword", keyword: "NEEDLE", accepted_statuscodes: [ "500-599" ] }, "DOWN" ],
    [ "keyword 'needle' inverted", { type: "keyword", keyword: "needle", invertKeyword: true, accepted_statuscodes: [ "500-599" ] }, "DOWN" ],
    [ "keyword 'absent' inverted", { type: "keyword", keyword: "absent", invertKeyword: true, accepted_statuscodes: [ "500-599" ] }, "UP" ],
];

(async () => {
    await targetReset();
    // one fixed response for every case: HTTP 503 with a body containing "needle"
    await ctl("mode=up&code=503&body=" + encodeURIComponent('{"k":"a needle in the body"}'));
    const sess = await Session.open();
    const ids = [];
    for (const [ name, ov ] of CASES) {
        const id = await sess.addMonitor(Object.assign({
            name: "p3-" + Date.now() + "-" + ids.length,
            maxretries: 0,
            interval: 20,
            retryInterval: 20,
            timeout: 10,
        }, ov));
        ids.push(id);
    }
    for (let i = 0; i < ids.length; i++) {
        await waitFor(sess, ids[i], (b) => b.length > 0, 90000, CASES[i][0]);
    }
    await sleep(500);
    let fails = 0;
    console.log("target: HTTP 503, body {\"k\":\"a needle in the body\"}\n");
    for (let i = 0; i < ids.length; i++) {
        const b = sess.beatsOf(ids[i])[0];
        const got = b.statusName;
        const exp = CASES[i][2];
        const ok = got === exp ? "OK  " : "DIFF";
        if (got !== exp) fails++;
        console.log(`${ok} ${CASES[i][0]}\n       expected=${exp} got=${got} msg=${JSON.stringify(b.msg)}`);
    }
    console.log(`\nRESULT: ${CASES.length - fails}/${CASES.length} conform`);
    for (const id of ids) await sess.del(id);
    await ctl("mode=up&code=200&body=OK");
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
