"use strict";
// PROBE 4 — documented promise (src/lang/en.json):
//   "Resend Notification if Down X times consecutively"
//   "resendEveryXTimes": "Resend every {0} times"   /  "resendDisabled": "Resend disabled" (value 0)
// A local webhook notification counts deliveries while the monitor stays DOWN.
const { Session, ctl, targetReset, targetLog, sleep, waitFor, TARGET } = require("./lib");

const RESEND = parseInt(process.argv[2] || "2", 10);
const BEATS = parseInt(process.argv[3] || "7", 10);
const INTERVAL = 20;

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();

    const notif = await sess.emit("addNotification", {
        name: "probe-webhook-" + Date.now(),
        type: "webhook",
        webhookURL: TARGET + "/hook",
        webhookContentType: "json",
        isDefault: false,
        applyExisting: false,
    }, null);
    if (!notif.ok) throw new Error("addNotification: " + JSON.stringify(notif));
    console.log("notification id " + notif.id);

    const id = await sess.addMonitor({
        name: "p4-resend-" + RESEND + "-" + Date.now(),
        maxretries: 0,
        interval: INTERVAL,
        retryInterval: INTERVAL,
        resendInterval: RESEND,
        timeout: 10,
        notificationIDList: { [notif.id]: true },
    });
    await waitFor(sess, id, (b) => b.some((x) => x.status === 1), 60000, "first UP");
    console.log(`monitor ${id} resendInterval=${RESEND} interval=${INTERVAL}s`);

    await targetReset();          // clears hook log; mode back to up
    await ctl("mode=down");
    const t0 = Date.now();
    await waitFor(sess, id, (b) => b.filter((x) => x.status === 0).length >= BEATS,
        (BEATS + 2) * INTERVAL * 1000, `${BEATS} DOWN beats`);
    await sleep(1500);

    const downBeats = sess.beatsOf(id).filter((b) => b.status === 0);
    const hooks = (await targetLog()).filter((h) => h.path === "/hook");
    console.log(`\nDOWN beats (${downBeats.length}):`);
    downBeats.forEach((b, i) => console.log(`  #${i + 1} +${((b.recvAt - t0) / 1000).toFixed(1)}s`));
    console.log(`webhook deliveries (${hooks.length}):`);
    hooks.forEach((h, i) => console.log(`  #${i + 1} +${((h.t - t0) / 1000).toFixed(1)}s`));

    // Map each delivery to the nearest preceding down beat index
    const idx = hooks.map((h) => {
        let best = -1;
        downBeats.forEach((b, i) => { if (b.recvAt - 3000 <= h.t) best = i + 1; });
        return best;
    });
    console.log(`\ndeliveries fired on DOWN beat numbers: [${idx.join(", ")}]`);
    const expected = [ 1 ];
    for (let n = 1 + RESEND; n <= downBeats.length; n += RESEND) expected.push(n);
    console.log(`expected (initial, then every ${RESEND}): [${expected.join(", ")}]`);
    console.log("RESULT: " + (JSON.stringify(idx) === JSON.stringify(expected) ? "CONFORM" : "DIFFERENT"));

    await sess.del(id);
    await sess.emit("deleteNotification", notif.id);
    await ctl("mode=up");
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
