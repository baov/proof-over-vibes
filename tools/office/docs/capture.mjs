// Regenerates the screenshots of the README, sharp, from the scripted demo.
//
//   node tools/office/docs/capture.mjs [name ...]
//
// Needs node 22 (global WebSocket and fetch), Google Chrome, and python3. It builds throwaway project
// folders from tools/office/floor/demo.py, serves them on local ports, drives a headless Chrome over its
// DevTools protocol, and writes the images next to this file. No dependency to install.
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const OFFICE = resolve(HERE, "..");
const CHROME = process.env.CHROME ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const WIDTH = 1280;
const HEIGHT = 800;
const SCALE = 1.5; // 1920 x 1200 pixels
const FORMAT = "webp";
const QUALITY = 86;

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));

// A throwaway project folder, named like a project, since its name shows in the page.
function freshRoot() {
  return join(mkdtempSync(join(tmpdir(), "office-shot-")), "acme-shop");
}

// A project folder holding the scripted run, up to a given step (all of them by default).
function project(steps, extra = "") {
  const root = freshRoot();
  const script = `import sys; sys.path.insert(0, ${JSON.stringify(OFFICE)})
from pathlib import Path
from floor.demo import DEMO_STEPS, apply_step
root = Path(${JSON.stringify(root)})
for i in range(${steps} if ${steps} >= 0 else len(DEMO_STEPS)): apply_step(root, i)
${extra}`;
  const run = spawnSync("python3", ["-c", script], { encoding: "utf8" });
  if (run.status !== 0) throw new Error(run.stderr);
  return root;
}

// A story whose planner is blocked on a question.
function blockedProject() {
  const root = freshRoot();
  const script = `import os, time
from pathlib import Path
b = Path(${JSON.stringify(root)}) / ".plans/in-progress/checkout-cart"
b.mkdir(parents=True)
(b / "brief.md").write_text("# Brief\\n\\n**Objective:** let a customer empty the cart in one click.\\n\\nIteration counter: 0\\nIteration limit: 5\\n")
(b / "plan.md").write_text("---\\nrole: planner\\nstatus: blocked\\n---\\nWhich currency should the totals use, the cart's or the customer's?\\n")
now = time.time()
for f in b.iterdir(): os.utime(f, (now - 40, now - 40))`;
  const run = spawnSync("python3", ["-c", script], { encoding: "utf8" });
  if (run.status !== 0) throw new Error(run.stderr);
  return root;
}

function serve(root, port) {
  const child = spawn("python3", [join(OFFICE, "serve.py"), "--root", root, "--no-open", "--port", String(port)], { stdio: "ignore" });
  return child;
}

// A minimal DevTools client over the browser's WebSocket.
async function connect(port) {
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" });
      target = await response.json();
    } catch {
      await sleep(200);
    }
  }
  if (!target) throw new Error("Chrome did not start");
  const socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((open) => socket.addEventListener("open", open, { once: true }));
  let id = 0;
  const waiting = new Map();
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && waiting.has(message.id)) {
      const { resolve: ok, reject } = waiting.get(message.id);
      waiting.delete(message.id);
      message.error ? reject(new Error(message.error.message)) : ok(message.result);
    }
  });
  const send = (method, params = {}) => new Promise((ok, reject) => {
    const mine = ++id;
    waiting.set(mine, { resolve: ok, reject });
    socket.send(JSON.stringify({ id: mine, method, params }));
  });
  return { send, close: () => socket.close() };
}

const key = (name) => `window.dispatchEvent(new KeyboardEvent("keydown", { key: ${JSON.stringify(name)} }))`;

// Each scene: where to look, what to do, and what to wait for.
const SCENES = {
  night: { project: () => project(-1), url: "?time=23:00" },
  day: { project: () => project(-1), url: "?time=13:00" },
  "cool-theme": { project: () => project(-1), url: "?time=23:00", actions: [key("t")] },
  "agent-report": {
    project: () => project(-1),
    url: "?time=13:00",
    actions: [...Array(8).fill(key("ArrowRight")), `document.querySelector(".frise button").click()`],
  },
  decisions: { project: () => project(-1), url: "?time=13:00", actions: [key("d")] },
  blocked: { project: blockedProject, url: "?time=23:00", actions: [key("f")] },
  // Live: the run is written step by step while the page is open, so the journal fills and an agent walks.
  "journal-dawn": { project: () => project(1), url: "?time=06:30", live: true },
};

// The server answers, then the page is drawn: a blank page (a reset connection) is tried again.
async function ready(port) {
  for (let i = 0; i < 60; i++) {
    try {
      if ((await fetch(`http://127.0.0.1:${port}/api/snapshot`)).ok) return;
    } catch {
      /* not listening yet */
    }
    await sleep(250);
  }
  throw new Error(`nothing on port ${port}`);
}

async function load(browser, url) {
  for (let attempt = 0; attempt < 4; attempt++) {
    await browser.send("Page.navigate", { url });
    await sleep(5000);
    const { result } = await browser.send("Runtime.evaluate", { expression: 'Boolean(document.querySelector(".card"))' });
    if (result.value) return;
  }
  throw new Error(`the page did not draw: ${url}`);
}

async function shoot(name, scene, port, chromePort) {
  const root = scene.project();
  const server = serve(root, port);
  await ready(port);
  const browser = await connect(chromePort);
  try {
    await browser.send("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: HEIGHT, deviceScaleFactor: SCALE, mobile: false });
    await load(browser, `http://127.0.0.1:${port}/${scene.url}`);
    if (scene.live) {
      const steps = `import sys; sys.path.insert(0, ${JSON.stringify(OFFICE)})
import time
from pathlib import Path
from floor.demo import apply_step
for i in range(1, 7):
    apply_step(Path(${JSON.stringify(root)}), i); time.sleep(1.3)`;
      spawnSync("python3", ["-c", steps]);
      await sleep(1500);
    }
    // The shortcuts fold on the first interaction: do it, so that the help block is not in every picture.
    await browser.send("Runtime.evaluate", { expression: key("Shift") });
    for (const action of scene.actions ?? []) {
      await browser.send("Runtime.evaluate", { expression: action });
      await sleep(120);
    }
    await sleep(1800);
    const { data } = await browser.send("Page.captureScreenshot", { format: FORMAT, quality: QUALITY });
    writeFileSync(join(HERE, `${name}.${FORMAT}`), Buffer.from(data, "base64"));
    console.log(`${name}.${FORMAT}`);
  } finally {
    browser.close();
    server.kill();
    rmSync(dirname(root), { recursive: true, force: true });
  }
}

const wanted = process.argv.slice(2);
const names = wanted.length ? wanted : Object.keys(SCENES);
const profile = mkdtempSync(join(tmpdir(), "office-chrome-"));
const chromePort = 9333;
const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${chromePort}`, `--user-data-dir=${profile}`,
  "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--hide-scrollbars", "about:blank",
], { stdio: "ignore" });
try {
  let port = 8790;
  for (const name of names) {
    if (!SCENES[name]) throw new Error(`unknown scene: ${name}`);
    await shoot(name, SCENES[name], port++, chromePort);
  }
} finally {
  chrome.kill();
  await new Promise((done) => (chrome.exitCode === null ? chrome.once("exit", done) : done()));
  rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 300 });
}
