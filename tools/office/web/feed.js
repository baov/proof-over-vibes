// A short journal of what just happened, built from the changes between two snapshots of a run.
import { roleTitle } from "./roles.js";

// Pure: the events that took us from `before` to `after` (either may be null).
export function diffEvents(before, after) {
  if (!after) return [];
  if (!before || before.slug !== after.slug) {
    return [{ text: `Following ${after.slug}`, tone: "info" }];
  }
  const events = [];
  for (const [role, now] of Object.entries(after.roles)) {
    const was = before.roles[role];
    if (!was || was.state === now.state) {
      if (was && now.verdict && was.verdict !== now.verdict) events.push({ text: `${roleTitle(role)}: ${now.verdict}`, tone: now.verdict === "GO" ? "good" : "bad" });
      continue;
    }
    const file = now.reports?.at(-1)?.name;
    if (now.state === "working") events.push({ text: `${roleTitle(role)} started`, tone: "info" });
    else if (now.state === "done") events.push({ text: `${roleTitle(role)} finished${file ? ` · ${file}` : ""}`, tone: "good" });
    else if (now.state === "blocked") events.push({ text: `${roleTitle(role)} is blocked`, tone: "warn" });
    else if (now.state === "escalate") events.push({ text: `${roleTitle(role)} needs a human`, tone: "bad" });
    if (now.verdict && was.verdict !== now.verdict) events.push({ text: `${roleTitle(role)}: ${now.verdict}`, tone: now.verdict === "GO" ? "good" : "bad" });
  }
  if (after.iteration > before.iteration) events.push({ text: `Iteration ${after.iteration}/${after.limit}`, tone: "warn" });
  if (after.ready_to_merge && !before.ready_to_merge) events.push({ text: "Ready to merge", tone: "good" });
  if (after.human_needed && !before.human_needed) events.push({ text: "A human is needed", tone: "bad" });
  return events;
}

const TONES = { info: "#93c5fd", good: "#4ade80", warn: "#fbbf24", bad: "#f87171" };

export function createFeed() {
  const box = document.createElement("div");
  box.className = "feed";
  document.head.append(Object.assign(document.createElement("style"), {
    textContent: `
      .feed { position: fixed; right: 16px; top: 16px; width: 250px; display: flex; flex-direction: column; gap: 4px; pointer-events: none; z-index: 3; }
      .feed div { font-size: 12px; padding: 4px 9px; border-radius: 8px; background: rgba(10,12,28,.78); border-left: 3px solid; animation: feed-in .3s ease-out; }
      .feed small { opacity: .55; margin-right: 6px; }
      @keyframes feed-in { from { opacity: 0; transform: translateY(6px); } }
      body.panel-open .feed { display: none; }
    `,
  }));
  document.body.append(box);
  const entries = [];

  function push(event) {
    const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    entries.push({ ...event, time });
    if (entries.length > 5) entries.shift();
    box.replaceChildren(...entries.map((e) => {
      const row = document.createElement("div");
      row.style.borderColor = TONES[e.tone] ?? TONES.info;
      const stamp = document.createElement("small");
      stamp.textContent = e.time;
      row.append(stamp, document.createTextNode(e.text));
      return row;
    }));
  }
  return { push };
}
