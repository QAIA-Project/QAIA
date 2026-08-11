"use strict";
// PROBE 13 — same question as p12, but observed through the right channel.
// p11/p12 read the status through the socket event "getMaintenance", which reloads the row from
// the database (maintenance-socket-handler.js: R.findOne) and therefore always shows an empty
// beanMeta -> "unknown". The live status lives in the in-memory bean and is broadcast through the
// "maintenanceList" event, which is what this probe listens to; the monitor heartbeat is the
// second, independent witness.
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

const START_IN = 2, WATCH_MIN = 5;

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();
    let listStatus = "(none yet)";
    sess.socket.on("maintenanceList", (list) => {
        for (const k in list) if (list[k].title === "p13-recurring") listStatus = list[k].status;
    });

    const tr = [ at(START_IN), at(START_IN + 20) ];
    console.log(`now=${new Date().toTimeString().slice(0, 8)}  window=${pad(tr[0].hours)}:${pad(tr[0].minutes)}-${pad(tr[1].hours)}:${pad(tr[1].minutes)}  strategy=recurring-interval intervalDay=1`);

    const res = await sess.emit("addMaintenance", {
        title: "p13-recurring", description: "", strategy: "recurring-interval", active: 1,
        cron: "30 3 * * *", durationMinutes: 60, intervalDay: 1,
        dateRange: [ localDT(-120), localDT(1440) ],
        timeRange: tr, weekdays: [], daysOfMonth: [], timezoneOption: "SAME_AS_SERVER",
    });
    if (!res.ok) throw new Error(JSON.stringify(res));
    const id = await sess.addMonitor({ name: "p13-" + Date.now(), maxretries: 0, interval: 20, retryInterval: 20, timeout: 10 });
    const link = await sess.emit("addMonitorMaintenance", res.maintenanceID, [ { id, name: "m" } ]);
    if (!link.ok) throw new Error(JSON.stringify(link));
    await sess.emit("getMaintenanceList");
    await sleep(500);
    console.log(`  right after creation: maintenanceList.status=${listStatus}`);

    const t0 = Date.now();
    let sawMaintenance = false;
    while (Date.now() - t0 < WATCH_MIN * 60000) {
        await sleep(20000);
        await sess.emit("getMaintenanceList");
        await sleep(300);
        const b = sess.beatsOf(id).slice(-1)[0];
        if (b && b.status === 3) sawMaintenance = true;
        console.log(`  +${((Date.now() - t0) / 60000).toFixed(1)}min  clock=${new Date().toTimeString().slice(0, 8)}  maintenanceList.status=${listStatus}  lastBeat=${b ? b.statusName : "-"}`);
    }
    console.log(`\nRESULT: monitor entered MAINTENANCE during the window: ${sawMaintenance ? "YES" : "NO"}`);
    await sess.del(id);
    await sess.emit("deleteMaintenance", res.maintenanceID);
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
