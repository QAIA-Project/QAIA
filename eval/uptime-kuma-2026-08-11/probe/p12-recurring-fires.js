"use strict";
// PROBE 12 — the decisive question left open by probe 11: a "Recurring - Interval" maintenance
// whose daily time range starts a couple of minutes from now. Does the window actually open?
// wiki "Maintenance": during the window "these monitors will be displayed in blue on the Dashboard".
const { Session, ctl, targetReset, sleep } = require("./lib");

const pad = (n) => String(n).padStart(2, "0");
const at = (offsetMin) => {
    const d = new Date(Date.now() + offsetMin * 60000);
    return { hours: d.getHours(), minutes: d.getMinutes() };
};
const localDT = (offsetMin) => {
    const d = new Date(Date.now() + offsetMin * 60000);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const START_IN = 2;    // minutes
const WATCH_MIN = 5;

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();
    const tr = [ at(START_IN), at(START_IN + 20) ];
    console.log(`now=${new Date().toTimeString().slice(0, 8)}  window=${pad(tr[0].hours)}:${pad(tr[0].minutes)}-${pad(tr[1].hours)}:${pad(tr[1].minutes)} (recurring-interval, every 1 day)`);

    const res = await sess.emit("addMaintenance", {
        title: "p12-recurring", description: "", strategy: "recurring-interval", active: 1,
        cron: "30 3 * * *", durationMinutes: 60, intervalDay: 1,
        dateRange: [ localDT(-120), localDT(1440) ],
        timeRange: tr, weekdays: [], daysOfMonth: [], timezoneOption: "SAME_AS_SERVER",
    });
    if (!res.ok) throw new Error(JSON.stringify(res));
    const id = await sess.addMonitor({ name: "p12-" + Date.now(), maxretries: 0, interval: 20, retryInterval: 20, timeout: 10 });
    const link = await sess.emit("addMonitorMaintenance", res.maintenanceID, [ { id, name: "m" } ]);
    if (!link.ok) throw new Error(JSON.stringify(link));

    const t0 = Date.now();
    let sawMaintenance = false;
    while (Date.now() - t0 < WATCH_MIN * 60000) {
        await sleep(20000);
        const st = await sess.emit("getMaintenance", res.maintenanceID);
        const b = sess.beatsOf(id).slice(-1)[0];
        if (b && b.status === 3) sawMaintenance = true;
        console.log(`  +${((Date.now() - t0) / 60000).toFixed(1)}min  clock=${new Date().toTimeString().slice(0, 8)}  maintenance.status=${st.maintenance.status}  lastBeat=${b ? b.statusName : "-"}`);
    }
    console.log(`\nRESULT: monitor entered MAINTENANCE during the window: ${sawMaintenance ? "YES" : "NO"}`);
    await sess.del(id);
    await sess.emit("deleteMaintenance", res.maintenanceID);
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
