"use strict";
// Controllable local HTTP target for Uptime Kuma probes. 127.0.0.1 only.
// Control:  GET /ctl?mode=up|down|slow|hang|keyword&code=NNN&delay=MS&body=...
// Probe:    GET /p            -> behaves per current mode
// Log:      GET /log          -> JSON list of {t, path, mode} for every /p hit
// Reset:    GET /reset
const http = require("http");
const url = require("url");

const PORT = parseInt(process.env.TARGET_PORT || "3999", 10);
let state = { mode: "up", code: 200, delay: 0, body: "OK" };
let hits = [];

const server = http.createServer((req, res) => {
    const u = url.parse(req.url, true);
    if (u.pathname === "/ctl") {
        for (const k of [ "mode", "body" ]) {
            if (u.query[k] !== undefined) state[k] = u.query[k];
        }
        for (const k of [ "code", "delay" ]) {
            if (u.query[k] !== undefined) state[k] = parseInt(u.query[k], 10);
        }
        res.writeHead(200, { "content-type": "application/json" });
        return res.end(JSON.stringify(state));
    }
    if (u.pathname === "/log") {
        res.writeHead(200, { "content-type": "application/json" });
        return res.end(JSON.stringify(hits));
    }
    if (u.pathname === "/reset") {
        hits = [];
        state = { mode: "up", code: 200, delay: 0, body: "OK" };
        res.writeHead(200);
        return res.end("reset");
    }
    // /hook: notification receiver — always 200, records the JSON body
    if (u.pathname === "/hook") {
        let raw = "";
        req.on("data", (c) => { raw += c; });
        return req.on("end", () => {
            hits.push({ t: Date.now(), iso: new Date().toISOString(), path: "/hook", mode: "hook", body: raw });
            res.writeHead(200, { "content-type": "application/json" });
            res.end("{}");
        });
    }
    // /r/<n> redirects n times then answers 200 with "final"
    const m = /^\/r\/(\d+)$/.exec(u.pathname);
    if (m) {
        const n = parseInt(m[1], 10);
        hits.push({ t: Date.now(), iso: new Date().toISOString(), path: u.pathname, mode: "redirect" });
        if (n === 0) {
            res.writeHead(200, { "content-type": "text/plain" });
            return res.end("final");
        }
        res.writeHead(302, { location: "/r/" + (n - 1) });
        return res.end("redirecting");
    }
    // /big?n=N returns a body of N 'x' characters
    if (u.pathname === "/big") {
        const n = parseInt(u.query.n || "5000", 10);
        res.writeHead(200, { "content-type": "text/plain" });
        return res.end("x".repeat(n));
    }
    // probe path
    const now = Date.now();
    hits.push({ t: now, iso: new Date(now).toISOString(), path: u.pathname, mode: state.mode });
    const finish = () => {
        if (state.mode === "hang") return; // never answer, never close
        if (state.mode === "down") {
            res.writeHead(state.code === 200 ? 500 : state.code, { "content-type": "text/plain" });
            return res.end("DOWN");
        }
        res.writeHead(state.code, { "content-type": "application/json" });
        res.end(state.body);
    };
    if (state.delay > 0) setTimeout(finish, state.delay);
    else finish();
});

server.on("connection", (s) => s.setTimeout(0));
server.listen(PORT, "127.0.0.1", () => {
    console.log("target listening on http://127.0.0.1:" + PORT);
});
