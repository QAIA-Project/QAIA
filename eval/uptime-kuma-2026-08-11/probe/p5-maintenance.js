"use strict";
// PROBE 5 — documented promises (wiki "Maintenance"):
//   strategies "Active/Inactive Manually", "Single Maintenance Window", ...
//   affected monitors are shown as under maintenance during the window
//   "select a special timezone of the maintenance or use the default option Same as Server Timezone"
// Target stays UP throughout: a beat is MAINTENANCE iff the window applies, UP otherwise.
const { Session, ctl, targetReset, sleep, waitFor } = require("./lib");

const pad = (n) => String(n).padStart(2, "0");
const local = (offsetMin) => {
    const d = new Date(Date.now() + offsetMin * 60000);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const CASES = [
    [ "manual, active", { strategy: "manual", active: 1, dateRange: [ "", "" ] }, "MAINTENANCE" ],
    [ "manual, inactive", { strategy: "manual", active: 0, dateRange: [ "", "" ] }, "UP" ],
    [ "single window covering now", { strategy: "single", active: 1, dateRange: [ local(-5), local(30) ] }, "MAINTENANCE" ],
    [ "single window in the future", { strategy: "single", active: 1, dateRange: [ local(30), local(60) ] }, "UP" ],
    [ "single window already ended", { strategy: "single", active: 1, dateRange: [ local(-60), local(-30) ] }, "UP" ],
    // same wall-clock range, declared in UTC: server is UTC+2 in August, so in UTC these
    // wall-clock instants are still 2 h away -> must be "scheduled", monitor UP.
    [ "single window covering now but declared in UTC", { strategy: "single", active: 1, timezoneOption: "UTC", dateRange: [ local(-5), local(30) ] }, "depends on server tz" ],
];

const BASE = {
    title: "probe",
    description: "",
    strategy: "single",
    active: 1,
    cron: "30 3 * * *",
    durationMinutes: 60,
    intervalDay: 1,
    dateRange: [ "", "" ],
    timeRange: [ { hours: 2, minutes: 0 }, { hours: 3, minutes: 0 } ],
    weekdays: [],
    daysOfMonth: [],
    timezoneOption: "SAME_AS_SERVER",
};

(async () => {
    await targetReset();
    await ctl("mode=up");
    const sess = await Session.open();
    console.log("server local time: " + new Date().toString());

    const made = [];
    for (const [ name, ov ] of CASES) {
        const mres = await sess.emit("addMaintenance", Object.assign({}, BASE, ov, { title: "p5-" + name }));
        if (!mres.ok) throw new Error("addMaintenance " + name + ": " + JSON.stringify(mres));
        const id = await sess.addMonitor({
            name: "p5-" + Date.now() + "-" + made.length,
            maxretries: 0, interval: 20, retryInterval: 20, timeout: 10,
        });
        const link = await sess.emit("addMonitorMaintenance", mres.maintenanceID, [ { id, name: "m" } ]);
        if (!link.ok) throw new Error("link: " + JSON.stringify(link));
        made.push({ name, mid: mres.maintenanceID, id, expected: ov === undefined ? null : CASES.find((c) => c[0] === name)[2] });
    }

    // The very first beat fires at creation time, before addMonitorMaintenance has run,
    // so only beats from the 2nd on are meaningful for this probe.
    for (const m of made) await waitFor(sess, m.id, (b) => b.length > 1, 90000, m.name);
    await sleep(500);

    let diff = 0;
    console.log("");
    for (const m of made) {
        const b = sess.beatsOf(m.id).slice(-1)[0];
        const st = await sess.emit("getMaintenance", m.mid);
        const declared = st.ok ? st.maintenance.status : "?";
        const tag = (m.expected === b.statusName) ? "OK  " : (m.expected.startsWith("depends") ? "INFO" : "DIFF");
        if (tag === "DIFF") diff++;
        console.log(`${tag} ${m.name}\n       maintenance.status=${declared} firstBeat=${b.statusName} expected=${m.expected} msg=${JSON.stringify(b.msg)}`);
    }
    console.log(`\nRESULT: ${diff} deviation(s) among the ${CASES.length - 1} decidable cases`);

    for (const m of made) {
        await sess.del(m.id);
        await sess.emit("deleteMaintenance", m.mid);
    }
    sess.close();
    process.exit(0);
})().catch((e) => { console.error("ERR", e); process.exit(1); });
