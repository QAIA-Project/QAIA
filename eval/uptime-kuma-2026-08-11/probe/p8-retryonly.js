"use strict";
// PROBE 8 — documented promise (src/lang/en.json retryOnlyOnStatusCodeFailureDescription):
//   "If enabled, retries will only occur when the HTTP status code check fails (e.g., server is
//    down). If the status code check passes but the JSON query fails, the monitor will be marked
//    as down immediately without retries."
// maxretries=2 throughout; the question is only whether PENDING beats appear.
const { Session, ctl, targetReset, sleep, waitFor } = require("./lib");

const N = 2, INTERVAL = 20;

const CASES = [
    // name, retryOnly, target mode, expected first failing beat
    [ "status OK + JSON query fails, retryOnly=ON", true, "json-bad", "DOWN" ],
    [ "status OK + JSON query fails, retryOnly=OFF", false, "json-bad", "PENDING" ],
    [ "server unreachable, retryOnly=ON", true, "http-bad", "PENDING" ],
    [ "server unreachable, retryOnly=OFF", false, "http-bad", "PENDING" ],
];

(async () => {
    await targetReset();
    // body {"v":"good"}: monitors expect v == "good"; the bad ones point at a URL returning "bad"
    await ctl("mode=up&code=200&body=" + encodeURIComponent('{"v":"good"}'));
    const sess = await Session.open();
    const ids = [];
    for (const [ name, retryOnly, mode ] of CASES) {
        ids.push(await sess.addMonitor({
            name: "p8-" + Date.now() + "-" + ids.length,
            type: "json-query",
            jsonPath: "v", jsonPathOperator: "==", expectedValue: "good",
            url: mode === "http-bad" ? "http://127.0.0.1:1/down" : "http://127.0.0.1:3999/p",
            accepted_statuscodes: [ "200-299" ],
            retryOnlyOnStatusCodeFailure: retryOnly,
            maxretries: N, interval: INTERVAL, retryInterval: INTERVAL, timeout: 10,
        }));
    }
    // establish the healthy baseline for the two json-query cases
    await waitFor(sess, ids[0], (b) => b.length > 0, 60000, "baseline");
    await sleep(500);
    console.log("baseline beats: " + ids.map((id, i) => `${i}:${sess.beatsOf(id)[0].statusName}`).join(" "));

    // now break the JSON body for the /p monitors
    await ctl("mode=up&code=200&body=" + encodeURIComponent('{"v":"bad"}'));
    await sleep(200);
    for (let i = 0; i < ids.length; i++) {
        await waitFor(sess, ids[i], (b) => b.length > 1, 60000, CASES[i][0]);
    }
    await sleep(500);
    let diffs = 0;
    console.log("");
    for (let i = 0; i < ids.length; i++) {
        const beats = sess.beatsOf(ids[i]);
        const first = beats.slice(1).find((b) => b.status !== 1) || beats[1];
        const ok = first.statusName === CASES[i][3];
        if (!ok) diffs++;
        console.log(`${ok ? "OK  " : "DIFF"} ${CASES[i][0]}\n       expected first failing beat=${CASES[i][3]} got=${first.statusName} msg=${JSON.stringify(first.msg)}`);
    }
    console.log(`\nRESULT: ${diffs} deviation(s) / ${CASES.length}`);
    for (const id of ids) await sess.del(id);
    await ctl("mode=up&code=200&body=OK");
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
