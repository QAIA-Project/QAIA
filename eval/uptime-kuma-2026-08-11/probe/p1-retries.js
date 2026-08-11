"use strict";
// PROBE 1 — documented promise (src/lang/en.json):
//   "retriesDescription": "Maximum retries before the service is marked as down and a notification is sent"
//   "retryCheckEverySecond": "Retry every {0} seconds"
// Expectation: with maxretries = N, the N+1-th consecutive failure is the first DOWN;
// the N intermediate beats are PENDING, spaced by retryInterval (not interval).
const { Session, ctl, targetReset, sleep, waitFor, fmt } = require("./lib");

const N = parseInt(process.argv[2] || "2", 10);
const INTERVAL = parseInt(process.argv[3] || "20", 10);
const RETRY_INTERVAL = parseInt(process.argv[4] || "20", 10);

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();
    const id = await sess.addMonitor({
        name: "p1-retries-" + N + "-" + Date.now(),
        maxretries: N,
        interval: INTERVAL,
        retryInterval: RETRY_INTERVAL,
    });
    const t0 = Date.now();
    console.log(`monitor ${id} maxretries=${N} interval=${INTERVAL} retryInterval=${RETRY_INTERVAL}`);

    await waitFor(sess, id, (b) => b.some((x) => x.status === 1), 60000, "first UP");
    console.log("UP established at +" + ((Date.now() - t0) / 1000).toFixed(1) + "s");

    await ctl("mode=down");
    const tDown = Date.now();
    console.log("target switched to 500 at +" + ((tDown - t0) / 1000).toFixed(1) + "s");

    // wait for a DOWN beat, or give up after (N+2) intervals
    try {
        await waitFor(sess, id, (b) => b.some((x) => x.status === 0), (N + 3) * INTERVAL * 1000 + 20000, "DOWN");
    } catch (e) {
        console.log("NO DOWN: " + e.message);
    }
    await sleep(1000);
    const beats = sess.beatsOf(id);
    const after = beats.filter((b) => b.recvAt >= tDown - 500);
    console.log("--- beats after failure injection ---");
    for (const b of after) {
        console.log(`  +${((b.recvAt - tDown) / 1000).toFixed(1)}s ${b.statusName} important=${b.important} msg=${JSON.stringify(b.msg)}`);
    }
    const pendings = after.filter((b) => b.status === 2).length;
    const firstDown = after.find((b) => b.status === 0);
    console.log(`RESULT maxretries=${N}: pendingBeats=${pendings} expectedPending=${N} firstDown=${firstDown ? "yes" : "no"} downImportant=${firstDown ? firstDown.important : "n/a"}`);
    if (pendings >= 2) {
        const p = after.filter((b) => b.status === 2);
        console.log("  pending spacing (s): " + p.slice(1).map((x, i) => ((x.recvAt - p[i].recvAt) / 1000).toFixed(1)).join(", "));
    }
    if (firstDown && pendings >= 1) {
        const lastPending = after.filter((b) => b.status === 2).pop();
        console.log("  lastPending->DOWN gap (s): " + ((firstDown.recvAt - lastPending.recvAt) / 1000).toFixed(1));
    }
    await sess.del(id);
    await ctl("mode=up");
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
