"use strict";
// PROBE 7 — focused reproduction of the responseMaxLength=0 deviation.
// Documented (src/lang/en.json responseMaxLengthDescription):
//   "Maximum size of response data to store. Set to 0 for unlimited. Larger responses
//    will be truncated. Default: 1024 (1KB)"
// The monitor form input carries min="0", so 0 is a value the form invites the user to enter.
const { Session, targetReset, targetLog, sleep, waitFor, TARGET } = require("./lib");

const CASES = [
    [ "responseMaxLength=0, body 10 chars", 0, 10, 10 ],
    [ "responseMaxLength=0, body 5000 chars", 0, 5000, 5000 ],
    [ "responseMaxLength=1024, body 10 chars (control)", 1024, 10, 10 ],
];

(async () => {
    await targetReset();
    const sess = await Session.open();
    const notif = await sess.emit("addNotification", {
        name: "p7-webhook-" + Date.now(), type: "webhook",
        webhookURL: TARGET + "/hook", webhookContentType: "json",
        isDefault: false, applyExisting: false,
    }, null);

    const ids = [];
    for (const [ , len, body ] of CASES) {
        ids.push(await sess.addMonitor({
            name: "p7-" + Date.now() + "-" + ids.length,
            url: TARGET + "/big?n=" + body,
            accepted_statuscodes: [ "500-599" ],   // force the error path so the body is stored
            saveResponse: true, saveErrorResponse: true, responseMaxLength: len,
            maxretries: 0, interval: 20, retryInterval: 20, timeout: 10,
            notificationIDList: { [notif.id]: true },
        }));
    }
    for (let i = 0; i < ids.length; i++) await waitFor(sess, ids[i], (b) => b.length > 0, 60000, CASES[i][0]);
    await sleep(3000);
    const hooks = (await targetLog()).filter((h) => h.path === "/hook");
    let diffs = 0;
    for (let i = 0; i < ids.length; i++) {
        const h = hooks.find((x) => { try { return JSON.parse(x.body).monitor.id === ids[i]; } catch (e) { return false; } });
        const stored = h ? JSON.parse(h.body).heartbeat.response : undefined;
        const payload = stored ? stored.replace(/\.\.\. \(truncated\)$/, "").length : 0;
        const ok = payload === CASES[i][3];
        if (!ok) diffs++;
        console.log(`${ok ? "OK  " : "DIFF"} ${CASES[i][0]}\n       expected stored chars=${CASES[i][3]} got=${payload} raw=${JSON.stringify(stored)}`.slice(0, 400));
    }
    console.log(`\nRESULT: ${diffs} deviation(s) / ${CASES.length}`);
    for (const id of ids) await sess.del(id);
    await sess.emit("deleteNotification", notif.id);
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
