"use strict";
// PROBE 11 — recurring maintenance windows (wiki "Maintenance": "Recurring - Interval").
// A window whose daily time range already contains "now" at creation time: is the monitor
// under maintenance, as a reader of the wiki would expect, or only from the next occurrence?
const { Session, ctl, targetReset, sleep, waitFor } = require("./lib");

const pad = (n) => String(n).padStart(2, "0");
const at = (offsetMin) => {
    const d = new Date(Date.now() + offsetMin * 60000);
    return { hours: d.getHours(), minutes: d.getMinutes() };
};
const localDT = (offsetMin) => {
    const d = new Date(Date.now() + offsetMin * 60000);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const BASE = {
    title: "probe", description: "", strategy: "recurring-interval", active: 1,
    cron: "30 3 * * *", durationMinutes: 60, intervalDay: 1,
    dateRange: [ localDT(-120), localDT(1440) ],
    timeRange: [ { hours: 2, minutes: 0 }, { hours: 3, minutes: 0 } ],
    weekdays: [], daysOfMonth: [], timezoneOption: "SAME_AS_SERVER",
};

const CASES = [
    [ "daily window that already contains now (started 3 min ago, ends in 30 min)", [ at(-3), at(30) ] ],
    [ "daily window starting in 30 min", [ at(30), at(60) ] ],
    [ "daily window that ended 30 min ago", [ at(-60), at(-30) ] ],
];

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();
    console.log("server local time: " + new Date().toString() + "\n");
    const made = [];
    for (const [ name, tr ] of CASES) {
        const res = await sess.emit("addMaintenance", Object.assign({}, BASE, { title: "p11-" + name, timeRange: tr }));
        if (!res.ok) throw new Error("addMaintenance: " + JSON.stringify(res));
        const id = await sess.addMonitor({ name: "p11-" + Date.now() + "-" + made.length, maxretries: 0, interval: 20, retryInterval: 20, timeout: 10 });
        const link = await sess.emit("addMonitorMaintenance", res.maintenanceID, [ { id, name: "m" } ]);
        if (!link.ok) throw new Error("link: " + JSON.stringify(link));
        made.push({ name, mid: res.maintenanceID, id, tr });
    }
    for (const m of made) await waitFor(sess, m.id, (b) => b.length > 1, 90000, m.name);
    await sleep(500);
    for (const m of made) {
        const b = sess.beatsOf(m.id).slice(-1)[0];
        const st = await sess.emit("getMaintenance", m.mid);
        const mm = st.maintenance;
        console.log(`${m.name}\n   timeRange=${pad(m.tr[0].hours)}:${pad(m.tr[0].minutes)}-${pad(m.tr[1].hours)}:${pad(m.tr[1].minutes)}  status=${mm.status}  durationMinutes=${mm.durationMinutes}  beat=${b.statusName}  msg=${JSON.stringify(b.msg)}`);
    }
    for (const m of made) { await sess.del(m.id); await sess.emit("deleteMaintenance", m.mid); }
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
