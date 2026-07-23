// cdp-qa.mjs — minimal Chrome DevTools Protocol driver for dashboard visual QA.
// Purpose: real mobile-emulation screenshots + layout measurement (horizontal-
//          overflow diagnostics) + real input events (click/hover/scroll), which
//          plain `chrome --headless --screenshot` cannot do. Zero dependencies
//          (Node 21+ global WebSocket). Lightweight replacement for the Playwright
//          screenshot harness dropped at the 2026-07-02 wrapup.
// Inputs:  1) start Chrome:  chrome --headless=new --remote-debugging-port=9222 //             --user-data-dir=<throwaway dir> about:blank
//          2) node scripts/cdp-qa.mjs <url> <outPng> [--width N] [--height N]
//             [--mobile] [--eval EXPR] [--fullpage] [--actions JSON]
//             actions: [{"type":"click|move|scroll|wait","x":..,"y":..,"dy":..,"ms":..}]
//             (x/y are CSS px in the emulated viewport)
// Outputs: PNG at <outPng>; DIAG line (innerWidth vs scrollWidth + overflowing
//          elements) and optional EVAL result on stdout.
// last_run: 2026-07-03 (visual-identity pass QA: all 5 pages, mobile + desktop,
//          toggle/hover/click-through event-path checks)

const args = process.argv.slice(2);
const url = args[0];
const outPng = args[1];
const opt = (name, dflt) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : dflt;
};
const has = (name) => args.includes(`--${name}`);

const width = Number(opt("width", 1440));
const height = Number(opt("height", 900));
const mobile = has("mobile");
const fullpage = has("fullpage");
const evalExpr = opt("eval", null);
const actionsJson = opt("actions", null);

const DEBUG_PORT = 9222;

async function httpJson(path, method = "GET") {
  const res = await fetch(`http://127.0.0.1:${DEBUG_PORT}${path}`, { method });
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  return res.json();
}

const target = await httpJson(`/json/new?about:blank`, "PUT");
const ws = new WebSocket(target.webSocketDebuggerUrl);
let msgId = 0;
const pending = new Map();
const events = [];

ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) {
    const { resolve, reject } = pending.get(m.id);
    pending.delete(m.id);
    m.error ? reject(new Error(m.error.message)) : resolve(m.result);
  } else if (m.method) {
    events.push(m.method);
  }
};

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

await new Promise((r) => (ws.onopen = r));
await send("Page.enable");
await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", {
  width, height, deviceScaleFactor: 2, mobile,
});
if (mobile) {
  await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 });
}
await send("Page.navigate", { url });
// Wait for load event, then settle for hydration.
for (let i = 0; i < 100 && !events.includes("Page.loadEventFired"); i++) await sleep(100);
await sleep(1200);

// Optional scripted actions before the screenshot: [{type:'move'|'click'|'scroll', x,y, dy}]
if (actionsJson) {
  const actions = JSON.parse(actionsJson);
  for (const a of actions) {
    if (a.type === "move") {
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: a.x, y: a.y });
    } else if (a.type === "click") {
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: a.x, y: a.y });
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x: a.x, y: a.y, button: "left", clickCount: 1 });
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x: a.x, y: a.y, button: "left", clickCount: 1 });
    } else if (a.type === "scroll") {
      await send("Input.dispatchMouseEvent", { type: "mouseWheel", x: a.x ?? 200, y: a.y ?? 200, deltaX: 0, deltaY: a.dy ?? 600 });
    } else if (a.type === "wait") {
      await sleep(a.ms ?? 500);
    }
  }
  await sleep(600);
}

// Layout diagnostics: does the page overflow its viewport horizontally?
const diag = await send("Runtime.evaluate", {
  expression: `JSON.stringify({
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    url: location.pathname,
    overflowers: [...document.querySelectorAll('*')].filter(el => el.scrollWidth > document.documentElement.clientWidth + 1).slice(0,8).map(el => el.tagName + '.' + String(el.className).slice(0,60) + ' sw=' + el.scrollWidth)
  })`,
  returnByValue: true,
});
console.log("DIAG:", diag.result.value);

if (evalExpr) {
  const r = await send("Runtime.evaluate", { expression: evalExpr, returnByValue: true });
  console.log("EVAL:", JSON.stringify(r.result.value));
}

let clip;
if (fullpage) {
  const metrics = await send("Page.getLayoutMetrics");
  const h = Math.min(Math.ceil(metrics.cssContentSize.height), 12000);
  await send("Emulation.setDeviceMetricsOverride", { width, height: h, deviceScaleFactor: 2, mobile });
  await sleep(400);
}
const shot = await send("Page.captureScreenshot", { format: "png", ...(clip ? { clip } : {}) });
const { writeFileSync } = await import("node:fs");
writeFileSync(outPng, Buffer.from(shot.data, "base64"));
console.log("WROTE:", outPng);

await send("Target.closeTarget", { targetId: target.id }).catch(() => {});
ws.close();
process.exit(0);
