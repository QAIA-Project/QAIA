"use strict";
const k = require("./kuma");

const TARGET = process.env.TARGET_URL || "http://127.0.0.1:3999";

const DEFAULTS = {
    type: "http",
    name: "probe",
    parent: null,
    url: TARGET + "/p",
    method: "GET",
    interval: 20,
    retryInterval: 20,
    resendInterval: 0,
    maxretries: 0,
    retryOnlyOnStatusCodeFailure: false,
    notificationIDList: {},
    ignoreTls: false,
    upsideDown: false,
    expiryNotification: false,
    maxredirects: 10,
    accepted_statuscodes: [ "200-299" ],
    saveResponse: false,
    saveErrorResponse: true,
    responseMaxLength: 1024,
    timeout: 16,
    httpBodyEncoding: "json",
    conditions: [],
    active: true,
};

// Heartbeat status codes (server/util.js): DOWN=0 UP=1 PENDING=2 MAINTENANCE=3
const S = { 0: "DOWN", 1: "UP", 2: "PENDING", 3: "MAINTENANCE" };

async function ctl(qs) {
    const res = await fetch(TARGET + "/ctl?" + qs);
    return res.json();
}
async function targetLog() {
    return (await fetch(TARGET + "/log")).json();
}
async function targetReset() {
    await fetch(TARGET + "/reset");
}

class Session {
    constructor(socket) {
        this.socket = socket;
        this.beats = {}; // monitorID -> [{status, time, msg, ms, recvAt}]
        socket.on("heartbeat", (b) => {
            const arr = this.beats[b.monitorID] || (this.beats[b.monitorID] = []);
            arr.push({
                status: b.status,
                statusName: S[b.status],
                time: b.time,
                msg: b.msg,
                ping: b.ping,
                important: b.important,
                recvAt: Date.now(),
            });
        });
    }
    static async open() {
        const socket = await k.session();
        return new Session(socket);
    }
    emit(ev, ...a) {
        return k.emit(this.socket, ev, ...a);
    }
    async addMonitor(overrides) {
        const m = Object.assign({}, DEFAULTS, overrides);
        const res = await this.emit("add", m);
        if (!res.ok) throw new Error("add failed: " + JSON.stringify(res));
        this.beats[res.monitorID] = [];
        return res.monitorID;
    }
    async del(id) {
        return this.emit("deleteMonitor", id);
    }
    async pause(id) {
        return this.emit("pauseMonitor", id);
    }
    beatsOf(id) {
        return this.beats[id] || [];
    }
    close() {
        this.socket.close();
    }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Wait until predicate(beats) is true or timeout
async function waitFor(sess, id, pred, ms, label) {
    const t0 = Date.now();
    while (Date.now() - t0 < ms) {
        if (pred(sess.beatsOf(id))) return true;
        await sleep(250);
    }
    throw new Error("waitFor timeout: " + (label || "") + " beats=" + JSON.stringify(sess.beatsOf(id).map((b) => b.statusName)));
}

function fmt(beats, t0) {
    return beats.map((b) => `+${((b.recvAt - t0) / 1000).toFixed(1)}s ${b.statusName} ${JSON.stringify(b.msg)}`);
}

module.exports = { Session, ctl, targetLog, targetReset, sleep, waitFor, fmt, S, TARGET, DEFAULTS };
