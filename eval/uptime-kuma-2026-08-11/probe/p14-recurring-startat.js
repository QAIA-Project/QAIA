"use strict";
// PROBE 14 — A/B on the first occurrence of a "Recurring - Interval" maintenance window.
// Both maintenances have the SAME daily time range, opening a few minutes from now.
// They differ only in the start of their validity range (dateRange[0], the "Effective Date Range"
// field of the form):
//    A: validity starts today       -> the first occurrence falls on the same instant
//    B: validity started yesterday  -> the first occurrence is well after the validity start
// If A stays "scheduled" through its window while B goes "under-maintenance", the first
// occurrence is being skipped when it coincides with the start of the validity range.
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

const START_IN = 3, WATCH_MIN = 6;

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();
    const tr = [ at(START_IN), at(START_IN + 20) ];
    const status = {};
    sess.socket.on("maintenanceList", (list) => {
        for (const k in list) if (list[k].title.startsWith("p14-")) status[list[k].title] = list[k].status;
    });

    console.log(`now=${new Date().toTimeString().slice(0, 8)}  daily window=${pad(tr[0].hours)}:${pad(tr[0].minutes)}-${pad(tr[1].hours)}:${pad(tr[1].minutes)}\n`);

    const variants = [
        [ "p14-A-validity-starts-today", localDT(-30) ],
        [ "p14-B-validity-started-yesterday", localDT(-24 * 60 - 30) ],
    ];
    const made = [];
    for (const [ title, from ] of variants) {
        const res = await sess.emit("addMaintenance", {
            title, description: "", strategy: "recurring-interval", active: 1,
            cron: "30 3 * * *", durationMinutes: 60, intervalDay: 1,
            dateRange: [ from, localDT(3 * 24 * 60) ],
            timeRange: tr, weekdays: [], daysOfMonth: [], timezoneOption: "SAME_AS_SERVER",
        });
        if (!res.ok) throw new Error(title + ": " + JSON.stringify(res));
        const id = await sess.addMonitor({ name: title + "-mon-" + Date.now(), maxretries: 0, interval: 20, retryInterval: 20, timeout: 10 });
        const link = await sess.emit("addMonitorMaintenance", res.maintenanceID, [ { id, name: "m" } ]);
        if (!link.ok) throw new Error("link " + title + ": " + JSON.stringify(link));
        made.push({ title, mid: res.maintenanceID, id, from });
        console.log(`  ${title}: validity starts ${from}`);
    }

    const t0 = Date.now();
    const saw = {};
    while (Date.now() - t0 < WATCH_MIN * 60000) {
        await sleep(20000);
        await sess.emit("getMaintenanceList");
        await sleep(300);
        const parts = made.map((m) => {
            const b = sess.beatsOf(m.id).slice(-1)[0];
            if (b && b.status === 3) saw[m.title] = true;
            return `${m.title.slice(4, 5)}: ${status[m.title]}/${b ? b.statusName : "-"}`;
        });
        console.log(`  +${((Date.now() - t0) / 60000).toFixed(1)}min ${new Date().toTimeString().slice(0, 8)}  ${parts.join("   ")}`);
    }
    console.log("");
    for (const m of made) console.log(`RESULT ${m.title}: entered MAINTENANCE = ${saw[m.title] ? "YES" : "NO"}`);
    for (const m of made) { await sess.del(m.id); await sess.emit("deleteMaintenance", m.mid); }
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
