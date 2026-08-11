"use strict";
// PROBE 15 — the mechanism behind D-2, isolated from Uptime Kuma.
// server/model/maintenance.js builds the recurring-interval job as
//     startAt = dayjs(start_date).hour(H).minute(M).toISOString()
//     new Cron(`${M} ${H}  * * *`, { timezone, startAt }, ...)
// where start_date is the beginning of the form's effective date range and H:M the daily window
// start. When the effective date range begins TODAY, startAt lands exactly on today's occurrence.
// This script asks croner (the version vendored by the project) what it schedules in that case.
const path = require("path");
const UK = process.env.UK_DIR || "C:/uk-eval/uk";
const { Cron } = require(path.join(UK, "node_modules", "croner"));

const H = 14, M = 55, TZ = "Europe/Paris";
const pattern = `${M} ${H}  * * *`;

for (const [ label, startAt ] of [
    [ "effective date range starts TODAY    (startAt == today's occurrence)", "2026-08-11T14:55:00" ],
    [ "effective date range started YESTERDAY", "2026-08-10T14:55:00" ],
]) {
    const job = new Cron(pattern, { timezone: TZ, startAt: new Date(startAt).toISOString() }, () => {});
    console.log(`${label}\n   startAt=${startAt}  nextRun=${job.nextRun()}`);
    job.stop();
}
console.log(`\ncroner version: ${require(path.join(UK, "node_modules", "croner", "package.json")).version}`);
