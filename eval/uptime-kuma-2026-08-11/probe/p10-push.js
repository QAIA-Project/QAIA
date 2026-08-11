"use strict";
// PROBE 10 — documented promises for the push monitor.
//   wiki "Internal API": /api/push/<pushToken>, "status" defaults to "up", "msg" defaults to "OK",
//     "Max length approx. 250 chars", "ping (number, optional) ... parsed as float",
//     error response { ok:false, msg:"Monitor not found or not active." }
//   src/lang/en.json needPushEvery: "You should call this URL every {0} seconds."
const { Session, sleep, waitFor } = require("./lib");

const INTERVAL = 20;
const KUMA = "http://127.0.0.1:3001";

const push = async (token, qs) => {
    const r = await fetch(`${KUMA}/api/push/${token}?${qs}`);
    let body;
    try { body = await r.json(); } catch (e) { body = await r.text(); }
    return { status: r.status, body };
};

(async () => {
    const sess = await Session.open();
    const id = await sess.addMonitor({
        name: "p10-push-" + Date.now(), type: "push",
        // the UI generates the 32-char push token client-side (EditMonitor.vue genSecret)
        pushToken: Array.from({ length: 32 }, () => "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[Math.floor(Math.random() * 62)]).join(""),
        maxretries: 0, interval: INTERVAL, retryInterval: INTERVAL,
    });
    const mres = await sess.emit("getMonitor", id);
    const token = mres.monitor.pushToken;
    if (!token) throw new Error("no push token on monitor");
    console.log(`push monitor ${id}, token ${token}, interval ${INTERVAL}s\n`);

    console.log("--- unknown token ---");
    console.log(JSON.stringify(await push("nosuchtoken00", "")));

    console.log("\n--- defaults (no query string) ---");
    console.log(JSON.stringify(await push(token, "")));
    await sleep(800);
    let b = sess.beatsOf(id).slice(-1)[0];
    console.log(`  beat: ${b.statusName} msg=${JSON.stringify(b.msg)} ping=${b.ping}   [documented: status defaults to up, msg defaults to "OK"]`);

    console.log("\n--- status=down ---");
    await push(token, "status=down&msg=bye");
    await sleep(800);
    b = sess.beatsOf(id).slice(-1)[0];
    console.log(`  beat: ${b.statusName} msg=${JSON.stringify(b.msg)}`);

    console.log("\n--- msg length ---");
    for (const n of [ 250, 251, 1000, 10000 ]) {
        const res = await push(token, "status=up&msg=" + "m".repeat(n));
        await sleep(800);
        b = sess.beatsOf(id).slice(-1)[0];
        console.log(`  sent ${n} chars -> http ${res.status} ${JSON.stringify(res.body)} ; stored msg length = ${b.msg ? b.msg.length : b.msg}`);
    }

    console.log("\n--- ping parsing ---");
    for (const p of [ "123.5", "abc", "-1", "1e3", "" ]) {
        const res = await push(token, "status=up&ping=" + encodeURIComponent(p));
        await sleep(800);
        b = sess.beatsOf(id).slice(-1)[0];
        console.log(`  ping=${JSON.stringify(p)} -> http ${res.status} ${JSON.stringify(res.body)} ; stored ping = ${b.ping}`);
    }

    console.log("\n--- stop pushing: documented 'call this URL every " + INTERVAL + " seconds' ---");
    await push(token, "status=up&msg=last");
    const tLast = Date.now();
    await waitFor(sess, id, (b2) => b2.some((x) => x.status === 0 && x.recvAt > tLast), 3 * INTERVAL * 1000 + 20000, "DOWN after silence");
    const down = sess.beatsOf(id).filter((x) => x.status === 0 && x.recvAt > tLast)[0];
    console.log(`  DOWN ${((down.recvAt - tLast) / 1000).toFixed(1)}s after the last push (interval=${INTERVAL}s) msg=${JSON.stringify(down.msg)}`);

    await sess.del(id);
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
