"use strict";
// Minimal socket.io client helper for Uptime Kuma 2.5.0 local instance.
// Requires socket.io-client, resolved from the cloned uptime-kuma node_modules.
const path = require("path");
const UK = process.env.UK_DIR || "C:/uk-eval/uk";
const { io } = require(path.join(UK, "node_modules", "socket.io-client"));

const URL = process.env.KUMA_URL || "http://127.0.0.1:3001";
const USER = process.env.KUMA_USER || "probeadmin";
const PASS = process.env.KUMA_PASS || "ProbePassw0rd!";

function connect() {
    return new Promise((resolve, reject) => {
        const socket = io(URL, { transports: [ "websocket" ] });
        socket.on("connect_error", reject);
        socket.on("connect", () => resolve(socket));
    });
}

function emit(socket, event, ...args) {
    return new Promise((resolve, reject) => {
        const t = setTimeout(() => reject(new Error("timeout on " + event)), 30000);
        socket.emit(event, ...args, (res) => {
            clearTimeout(t);
            resolve(res);
        });
    });
}

async function login(socket) {
    return emit(socket, "login", { username: USER, password: PASS, token: "" });
}

async function setupIfNeeded(socket) {
    const res = await emit(socket, "setup", USER, PASS);
    return res;
}

async function session() {
    const socket = await connect();
    let needSetup = false;
    await new Promise((r) => {
        socket.once("setup", () => { needSetup = true; r(); });
        setTimeout(r, 2500);
    });
    if (needSetup) {
        await setupIfNeeded(socket);
    }
    const res = await login(socket);
    if (!res || !res.ok) {
        throw new Error("login failed: " + JSON.stringify(res));
    }
    return socket;
}

module.exports = { connect, emit, login, session, URL, USER, PASS };
