"use strict";
// PROBE 2 — documented promise (src/lang/en.json): "timeoutAfter": "Timeout after {0} seconds"
// Monitor with an explicit timeout T against a target that never answers.
// Expectation: a DOWN beat arrives ~T seconds after the request leaves.
const { Session, ctl, targetReset, targetLog, sleep, waitFor } = require("./lib");

const T = parseInt(process.argv[2] || "5", 10);

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();
    const id = await sess.addMonitor({
        name: "p2-timeout-" + T + "-" + Date.now(),
        maxretries: 0,
        interval: 20,
        retryInterval: 20,
        timeout: T,
    });
    await waitFor(sess, id, (b) => b.some((x) => x.status === 1), 60000, "first UP");
    console.log(`monitor ${id} timeout=${T}s — UP established`);

    await ctl("mode=hang");
    const nBefore = (await targetLog()).length;
    await waitFor(sess, id, (b) => b.some((x) => x.status === 0), 90000, "DOWN after hang");
    const down = sess.beatsOf(id).find((b) => b.status === 0);
    const log = await targetLog();
    const req = log[nBefore]; // the first request made while hanging
    const elapsed = (down.recvAt - req.t) / 1000;
    console.log(`request sent at ${req.iso}; DOWN beat received ${elapsed.toFixed(2)}s later`);
    console.log(`DOWN msg = ${JSON.stringify(down.msg)}`);
    console.log(`RESULT: declared timeout ${T}s, observed ${elapsed.toFixed(2)}s, delta ${(elapsed - T).toFixed(2)}s`);

    await sess.del(id);
    await ctl("mode=up");
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
