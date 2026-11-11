import { createAgents } from "./agents.js";
import { createDayBox } from "./daybox.js";
import { createDayClock } from "./daylight.js";
import { createFeed, diffEvents } from "./feed.js";
import { createHud } from "./hud.js";
import { TEAM_COLORS, createLayout } from "./layout.js";
import { connect } from "./live.js";
import { createPanel } from "./panel.js";
import { createPicker } from "./pick.js";
import { ago, roleTitle, took } from "./roles.js";
import { createScene } from "./scene.js";

const first = await (await fetch("/api/snapshot")).json();
const layout = createLayout(first.role_teams);
const canvas = document.getElementById("floor");
const view = createScene(canvas, layout);
const agents = createAgents(view.scene, layout, view.stations);
const aboutRole = first.role_about ?? {};

// The hour follows the machine's clock, unless a period or an hour is picked by hand (or ?time=HH:MM).
const clock = createDayClock({ search: location.search });
let shownHour = -1;
function refreshDay(force = false) {
  const hour = clock.hour();
  if (!force && Math.abs(hour - shownHour) < 0.002) return;
  shownHour = hour;
  view.setDaylight(hour);
  daybox.update({ mode: clock.mode(), label: clock.label(), hour });
}

const feed = createFeed();
const hud = createHud(document.getElementById("hud"), {
  onSelectRole: (role) => setSelected(role === selected ? null : role, true),
  onPickRun: (slug) => {
    viewed = slug;
    applyRun(currentRun());
  },
  onOpenDecisions: () => toggleDecisions(),
  onOpenDocs: () => toggleDocs(),
});
const daybox = createDayBox(document.getElementById("hud"), {
  onPeriod: (period) => { clock.setPeriod(period); refreshDay(true); },
  onAuto: () => { clock.setAuto(); refreshDay(true); },
  onHour: (hour) => { clock.setHour(hour); refreshDay(true); },
});
refreshDay(true);
const roles = [...layout.seats.keys()];

let status = "live";
let project = first.project ?? "";
let lastRun = null;
let allRuns = [];
let viewed = null; // a run picked by hand; null shows the most recent one

let hovered = null;
let selected = null;
let pinnedIndex = null; // null follows the newest report of the role
let follow = false;
let loaded = null; // { key, report } of the report on screen
let loadingKey = null;
let error = null;
let ticket = 0;
let decisionsOpen = false;
let decisionsLoaded = null; // { key, entries }
let decisionsLoading = null;
let docsOpen = false;
let docsList = []; // the Markdown documents of the project, newest first
let docsError = null;
let docsLoaded = false;
let openDocPath = null;
let openDoc = null; // the document on screen
let docsTicket = 0;
let docsSince = Date.now() / 1000; // what was written after this is new to the reader

const panel = createPanel({
  onClose: () => {
    decisionsOpen = false;
    if (docsOpen) docsSince = Date.now() / 1000;
    docsOpen = false;
    setSelected(null, true);
  },
  onPick: (index) => {
    pinnedIndex = index;
    sync();
  },
  onToggleFollow: () => setFollow(!follow),
  onNavigate: (role) => setSelected(role, true),
  onOpenDoc: (path) => {
    openDocPath = path;
    openDoc = null;
    syncDocs();
  },
  onBackToDocs: () => {
    openDocPath = null;
    openDoc = null;
    syncDocs();
  },
});

function showHud() {
  hud.show({ project, run: lastRun, runs: allRuns, viewed, status, follow, selected });
}

const currentRun = () => allRuns.find((run) => run.slug === viewed) ?? allRuns[0] ?? null;

function applyRun(next) {
  for (const event of diffEvents(lastRun, next)) feed.push(event);
  lastRun = next;
  agents.apply(lastRun);
  if (follow && lastRun?.active_role && lastRun.active_role !== selected) {
    selected = lastRun.active_role;
    pinnedIndex = null;
    marks();
  }
  showHud();
  sync();
}

function marks() {
  agents.setHighlight(hovered, selected);
  document.body.dataset.selected = selected ?? "";
}

function setSelected(role, manual) {
  if (role) {
    decisionsOpen = false; // an agent, the decisions and the documents share the same panel
    docsOpen = false;
  }
  if (manual) follow = false;
  if (role !== selected) pinnedIndex = null;
  selected = role;
  marks();
  showHud();
  sync();
}

function setFollow(on) {
  follow = on;
  if (on && lastRun?.active_role) setSelected(lastRun.active_role, false);
  else sync();
  showHud();
}

// Draw the panel for the selected role, fetching its report when the file on screen is stale.
// The decisions of the run on screen that nobody read, fetched again when their counts change.
function syncDecisions() {
  const run = lastRun;
  const key = run ? `${run.slug}|${run.decisions?.pending}|${run.decisions?.unread}` : "none";
  if (run && decisionsLoaded?.key !== key && decisionsLoading !== key) {
    decisionsLoading = key;
    fetch(`/api/decisions?run=${encodeURIComponent(run.slug)}`)
      .then((response) => (response.ok ? response.json() : []))
      .then((entries) => { decisionsLoaded = { key, entries }; })
      .catch(() => { decisionsLoaded = { key, entries: [] }; })
      .finally(() => {
        decisionsLoading = null;
        if (decisionsOpen && !selected) syncDecisions();
      });
  }
  panel.renderDecisions({
    run: run?.slug ?? "no run",
    entries: decisionsLoaded?.key === key ? decisionsLoaded.entries : [],
    loading: Boolean(run && decisionsLoaded?.key !== key),
    path: "docs/business/decisions.md",
  });
}

function toggleDecisions() {
  decisionsOpen = !decisionsOpen;
  if (decisionsOpen) {
    docsOpen = false;
    selected = null;
    marks();
  }
  showHud();
  sync();
}

// The documents are listed again each time the panel opens and every few seconds while it stays open.
function syncDocs() {
  const mine = ++docsTicket;
  fetch("/api/docs")
    .then((response) => (response.ok ? response.json() : Promise.reject(new Error(`Documents unavailable (${response.status}).`))))
    .then((entries) => { docsList = entries; docsError = null; })
    .catch((failure) => { docsError = failure.message; })
    .finally(() => {
      docsLoaded = true;
      drawDocs();
    });
  if (openDocPath) {
    const path = openDocPath;
    fetch(`/api/doc?path=${encodeURIComponent(path)}`)
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error("This document is gone."))))
      .then((doc) => { if (path === openDocPath) openDoc = doc; })
      .catch((failure) => { if (path === openDocPath) { docsError = failure.message; openDocPath = null; } })
      .finally(() => { if (mine === docsTicket) drawDocs(); });
  }
  drawDocs();
}

function drawDocs() {
  if (!docsOpen) return;
  panel.renderDocs({ entries: docsList, since: docsSince, doc: openDoc, loading: !docsLoaded || Boolean(openDocPath && !openDoc), error: docsError });
}

function toggleDocs() {
  docsOpen = !docsOpen;
  if (!docsOpen) docsSince = Date.now() / 1000; // what was on screen is read
  if (docsOpen) {
    decisionsOpen = false;
    selected = null;
    openDocPath = null;
    openDoc = null;
    docsLoaded = false;
    marks();
    showHud();
    syncDocs();
    return;
  }
  showHud();
  sync();
}

function sync() {
  if (!selected) {
    if (docsOpen) drawDocs();
    else if (decisionsOpen) syncDecisions();
    else panel.hide();
    return;
  }
  const info = lastRun?.roles?.[selected];
  const history = info?.reports ?? [];
  const index = pinnedIndex ?? history.length - 1;
  const entry = history[index];
  const key = entry ? `${lastRun.slug}|${selected}|${index}|${entry.name}|${entry.mtime}|${history.length}` : null;

  if (key && loaded?.key !== key && loadingKey !== key) {
    loadingKey = key;
    error = null;
    const mine = ++ticket;
    const query = `run=${encodeURIComponent(lastRun.slug)}&role=${encodeURIComponent(selected)}&i=${index}`;
    fetch(`/api/report?${query}`)
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error(`Report unavailable (${response.status}).`))))
      .then((report) => {
        if (mine === ticket) loaded = { key, report };
      })
      .catch((failure) => {
        if (mine === ticket) error = failure.message;
      })
      .finally(() => {
        if (mine === ticket) {
          loadingKey = null;
          sync();
        }
      });
  }

  const seat = layout.seats.get(selected);
  const route = lastRun?.route ?? [];
  const at = route.indexOf(selected);
  const neighbour = (role) => (role ? { role, title: roleTitle(role) } : null);
  const state = (index === history.length - 1 ? info?.state : entry?.status) ?? "idle";
  const when = entry ? ago(entry.mtime) : null;
  const stateLine = {
    working: "Working now",
    blocked: "Blocked: it asked a question and waits for the answer",
    escalate: "Needs a human decision",
    done: when ? `Finished ${when}${entry?.duration != null ? ` · took ${took(entry.duration)}` : ""}` : "Done",
    idle: when ? `Idle since ${when}` : "Has not started in this run",
  }[state];
  panel.render({
    role: selected,
    title: roleTitle(selected),
    about: aboutRole[selected] ?? null,
    stateLine,
    prev: neighbour(at > 0 ? route[at - 1] : null),
    next: neighbour(at >= 0 && at < route.length - 1 ? route[at + 1] : null),
    team: seat.team,
    color: TEAM_COLORS[seat.team],
    // An earlier report shows its own status and verdict, not the role's current ones.
    state,
    verdict: entry?.verdict ?? info?.verdict ?? null,
    expects: info?.expects ?? null,
    history,
    index,
    report: key && loaded?.key === key ? loaded.report : null,
    loading: Boolean(key && loaded?.key !== key && !error),
    error: key ? error : null,
    follow,
  });
}

connect(
  (snapshot) => {
    project = snapshot.project ?? project;
    allRuns = snapshot.runs;
    applyRun(currentRun());
  },
  (next) => {
    status = next;
    showHud();
  },
);
showHud();

createPicker({
  canvas,
  camera: view.camera,
  targets: agents.targets,
  onHover(role, event) {
    hovered = role;
    marks();
    if (!role || !event) {
      hud.hideTip();
      return;
    }
    const info = lastRun?.roles?.[role];
    const last = info?.reports?.at(-1);
    const lines = [[layout.seats.get(role).team, info?.state ?? "idle", info?.verdict].filter(Boolean).join(" · ")];
    if (aboutRole[role]) lines.push(aboutRole[role].length > 110 ? `${aboutRole[role].slice(0, 110).replace(/\s+\S*$/, "")}…` : aboutRole[role]);
    if (last) lines.push(`${last.name} · ${ago(last.mtime)}${last.duration != null ? ` · took ${took(last.duration)}` : ""}`);
    hud.showTip(roleTitle(role), lines, event.clientX, event.clientY);
  },
  onSelect: (role) => setSelected(role === selected ? null : role, true),
});

window.addEventListener("keydown", (event) => {
  if (event.target instanceof HTMLInputElement) {
    if (event.key === "Escape" && !event.target.value) event.target.blur(); // the filter keeps its own keys
    return;
  }
  if (event.key === "/" && docsOpen && panel.focusFilter()) {
    event.preventDefault();
    return;
  }
  const key = event.key.toLowerCase();
  if (key === "t") view.toggleTheme();
  if (key === "f") setFollow(!follow);
  if (key === "d") toggleDecisions();
  if (key === "m") toggleDocs();
  if (key === "n") {
    clock.cycle();
    refreshDay(true);
  }
  if (event.key === "Escape") {
    decisionsOpen = false;
    if (docsOpen) docsSince = Date.now() / 1000;
    docsOpen = false;
    setSelected(null, true);
  }
  // Arrows switch agent, so Tab keeps moving between the buttons of the page.
  if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
    event.preventDefault();
    const at = selected ? roles.indexOf(selected) : -1;
    setSelected(roles[(at + (event.key === "ArrowLeft" ? -1 : 1) + roles.length) % roles.length], true);
  }
});

// Relative times in the panel ("5s ago") move on even when no file changes.
setInterval(() => {
  if (docsOpen && !selected) syncDocs(); // a document may have been written or changed
  else sync();
}, 5000);

let last = performance.now();
function frame(now) {
  const dt = Math.min(0.1, (now - last) / 1000);
  last = now;
  refreshDay();
  agents.update(dt);
  view.render(dt);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
