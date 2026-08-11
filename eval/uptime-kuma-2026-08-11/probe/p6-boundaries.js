"use strict";
// PROBE 6 — two crisp boundary promises from the monitor form (src/lang/en.json):
//   maxRedirectDescription:      "Maximum number of redirects to follow. Set to 0 to disable redirects."
//   responseMaxLengthDescription:"Maximum size of response data to store. Set to 0 for unlimited.
//                                 Larger responses will be truncated. Default: 1024 (1KB)"
// Redirects are checked against a local chain /r/2 -> /r/1 -> /r/0 (200).
// Response storage is read back from the webhook notification payload, which is the
// only place the server hands the stored body back out (monitor.js toJSONAsync decodeResponse).
const { Session, ctl, targetReset, targetLog, sleep, waitFor, TARGET } = require("./lib");

const BODY_N = 5000;

(async () => {
    await targetReset();
    const sess = await Session.open();

    // ---------- part A: maxredirects ----------
    const redirCases = [
        [ "chain of 2 redirects, maxredirects=0 (documented: redirects disabled)", 0, 2, "DOWN" ],
        [ "chain of 2 redirects, maxredirects=1", 1, 2, "DOWN" ],
        [ "chain of 2 redirects, maxredirects=2", 2, 2, "UP" ],
        [ "chain of 2 redirects, maxredirects=5", 5, 2, "UP" ],
        [ "no redirect, maxredirects=0", 0, 0, "UP" ],
    ];
    const rids = [];
    for (const [ name, mr, chain ] of redirCases) {
        rids.push(await sess.addMonitor({
            name: "p6r-" + Date.now() + "-" + rids.length,
            url: TARGET + "/r/" + chain,
            maxredirects: mr, maxretries: 0, interval: 20, retryInterval: 20, timeout: 10,
        }));
    }
    for (let i = 0; i < rids.length; i++) await waitFor(sess, rids[i], (b) => b.length > 0, 60000, redirCases[i][0]);
    console.log("=== A. maxredirects ===");
    let diffs = 0;
    for (let i = 0; i < rids.length; i++) {
        const b = sess.beatsOf(rids[i])[0];
        const ok = b.statusName === redirCases[i][3];
        if (!ok) diffs++;
        console.log(`${ok ? "OK  " : "DIFF"} ${redirCases[i][0]}\n       expected=${redirCases[i][3]} got=${b.statusName} msg=${JSON.stringify(b.msg)}`);
    }
    for (const id of rids) await sess.del(id);

    // ---------- part B: responseMaxLength ----------
    console.log("\n=== B. responseMaxLength (body is " + BODY_N + " chars) ===");
    const notif = await sess.emit("addNotification", {
        name: "p6-webhook-" + Date.now(), type: "webhook",
        webhookURL: TARGET + "/hook", webhookContentType: "json",
        isDefault: false, applyExisting: false,
    }, null);
    const lenCases = [
        [ "responseMaxLength=1024 (documented default)", 1024, 1024 ],
        [ "responseMaxLength=100", 100, 100 ],
        [ "responseMaxLength=0 (documented: unlimited)", 0, BODY_N ],
    ];
    await targetReset();
    const lids = [];
    for (const [ name, len ] of lenCases) {
        lids.push(await sess.addMonitor({
            name: "p6L-" + Date.now() + "-" + lids.length,
            url: TARGET + "/big?n=" + BODY_N,
            // 200 is treated as a failure so the *error* response is the one stored
            accepted_statuscodes: [ "500-599" ],
            saveResponse: true, saveErrorResponse: true, responseMaxLength: len,
            maxretries: 0, interval: 20, retryInterval: 20, timeout: 10,
            notificationIDList: { [notif.id]: true },
        }));
    }
    for (let i = 0; i < lids.length; i++) await waitFor(sess, lids[i], (b) => b.length > 0, 60000, lenCases[i][0]);
    await sleep(3000);
    const hooks = (await targetLog()).filter((h) => h.path === "/hook");
    for (let i = 0; i < lids.length; i++) {
        const h = hooks.find((x) => { try { return JSON.parse(x.body).monitor.id === lids[i]; } catch (e) { return false; } });
        if (!h) { console.log(`?    ${lenCases[i][0]} — no webhook payload captured`); continue; }
        const hb = JSON.parse(h.body).heartbeat;
        const stored = hb.response;
        const shown = stored === null || stored === undefined ? String(stored) : `len=${stored.length} truncatedMarker=${/\.\.\. \(truncated\)$/.test(stored)} head=${JSON.stringify(stored.slice(0, 12))}`;
        const expected = lenCases[i][2];
        const payload = stored ? stored.replace(/\.\.\. \(truncated\)$/, "").length : 0;
        const ok = payload === expected;
        if (!ok) diffs++;
        console.log(`${ok ? "OK  " : "DIFF"} ${lenCases[i][0]}\n       expected stored chars=${expected} got=${payload} (${shown})`);
    }
    for (const id of lids) await sess.del(id);
    await sess.emit("deleteNotification", notif.id);
    console.log(`\nRESULT: ${diffs} deviation(s)`);
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
