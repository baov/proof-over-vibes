// Everything around the floor: the run card and its switcher, the pipeline strip, the banner and the tooltip.
import { STATE_COLORS, roleShort } from "./roles.js";

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

const STYLE = `
  .card { background: rgba(10,12,28,.78); border: 1px solid rgba(255,255,255,.12); border-radius: 12px; padding: 12px 14px; width: 230px; backdrop-filter: blur(6px); pointer-events: auto; }
  .card .title { font-size: 15px; font-weight: 700; margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .card .row { font-size: 14px; margin-top: 4px; }
  .card .muted { opacity: .65; font-size: 12px; margin-top: 2px; }
  .card .runs { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
  .card .runs button { font: inherit; font-size: 11px; color: inherit; cursor: pointer; padding: 2px 8px; border-radius: 999px; border: 1px solid rgba(255,255,255,.25); background: none; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .card .runs button.on { background: rgba(255,255,255,.18); border-color: #fff; }
  .card .decisions { display: block; width: 100%; margin-top: 8px; padding: 5px 8px; text-align: left; font: inherit; font-size: 12px; color: inherit; cursor: pointer; border-radius: 8px; border: 1px solid rgba(251,191,36,.55); background: rgba(251,191,36,.12); }
  .card .decisions.waiting { border-color: rgba(248,113,113,.7); background: rgba(248,113,113,.14); }
  .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; background: #22c55e; }
  .dot.reconnecting { background: #f59e0b; }
  .strip { position: fixed; left: 50%; bottom: 78px; transform: translateX(-50%); display: flex; align-items: center; gap: 0; z-index: 3; max-width: calc(100% - 32px); overflow-x: auto; padding: 6px 10px; border-radius: 999px; background: rgba(10,12,28,.78); border: 1px solid rgba(255,255,255,.12); backdrop-filter: blur(6px); }
  .strip:empty { display: none; }
  .strip button { font: inherit; color: inherit; cursor: pointer; background: none; border: 0; display: flex; flex-direction: column; align-items: center; gap: 3px; padding: 0 6px; }
  .strip .node { width: 22px; height: 22px; border-radius: 50%; border: 2px solid rgba(255,255,255,.25); }
  .strip .active .node { animation: pulse 1.2s infinite; border-color: #fff; }
  .strip .sel .node { box-shadow: 0 0 0 3px rgba(255,255,255,.45); }
  .strip .label { font-size: 11px; opacity: .85; white-space: nowrap; }
  .strip .link { width: 18px; height: 2px; background: rgba(255,255,255,.25); margin-bottom: 14px; }
  .strip .link.done { background: #16a34a; }
  @keyframes pulse { 50% { transform: scale(1.18); } }
  .tip { position: fixed; display: none; z-index: 5; pointer-events: none; padding: 7px 11px; background: rgba(10,12,28,.95); border: 1px solid rgba(255,255,255,.18); border-radius: 8px; font-size: 12px; max-width: 260px; line-height: 1.35; }
  .tip b { display: block; font-size: 13px; }
  .tip .muted { opacity: .65; }
  .hint { position: fixed; left: 16px; bottom: 14px; font-size: 12px; opacity: .6; pointer-events: none; }
  body.panel-open .hint { display: none; }
  body.panel-open .banner, body.panel-open .strip { left: calc((100% - var(--panel) - 32px) / 2); }
  @media (max-width: 700px) { body.panel-open .banner, body.panel-open .strip { left: 50%; } .hint { display: none; } }
  .banner { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); padding: 10px 22px; border-radius: 999px; font-weight: 700; font-size: 15px; letter-spacing: .03em; white-space: nowrap; max-width: calc(100% - 32px); overflow: hidden; text-overflow: ellipsis; }
  .banner.human { background: #dc2626; color: #fff; box-shadow: 0 0 24px #dc2626aa; }
  .banner.blocked { background: #d97706; color: #fff; box-shadow: 0 0 24px #d97706aa; }
  .banner.ready { background: #16a34a; color: #fff; box-shadow: 0 0 24px #16a34aaa; }
  .banner.idle { background: rgba(10,12,28,.78); color: #cbd5e1; font-weight: 500; }
`;

export function createHud(root, { onSelectRole, onPickRun, onOpenDecisions }) {
  document.head.append(Object.assign(el("style"), { textContent: STYLE }));
  const card = el("div", "card");
  const strip = el("div", "strip");
  const banner = el("div", "banner idle");
  const tip = el("div", "tip");
  const hint = el("div", "hint");
  root.append(card);
  document.body.append(strip, banner, tip, hint);

  function showTip(title, lines, x, y) {
    tip.replaceChildren(el("b", "", title), ...lines.map((line) => el("div", "muted", line)));
    tip.style.left = `${Math.min(x + 14, window.innerWidth - 280)}px`;
    tip.style.top = `${y + 14}px`;
    tip.style.display = "block";
  }
  const hideTip = () => { tip.style.display = "none"; };

  // m: { project, run, runs, viewed, status, follow, selected }
  function show(m) {
    const { run, runs, status } = m;
    card.replaceChildren();
    const top = el("div", "muted");
    top.append(el("span", `dot ${status}`), document.createTextNode(m.project || "Office floor"));
    card.append(top);
    if (run) {
      card.append(el("div", "title", run.slug));
      card.append(el("div", "muted", `${run.kind} · ${run.stage} · iteration ${run.iteration}/${run.limit}`));
      card.append(el("div", "row", run.active_role ? `Working: ${run.active_role}` : "No role working"));
    } else {
      card.append(el("div", "muted", status === "live" ? "Start your agent workflow: its run appears here." : status));
    }
    const decisions = run?.decisions;
    if (decisions && (decisions.pending || decisions.unread)) {
      const parts = [];
      if (decisions.pending) parts.push(`${decisions.pending} waiting for you`);
      if (decisions.unread) parts.push(`${decisions.unread} never read`);
      const chip = el("button", `decisions${decisions.pending ? " waiting" : ""}`, `⚑ ${parts.join(" · ")}`);
      chip.title = "Decisions of this run to review (D)";
      chip.onclick = onOpenDecisions;
      card.append(chip);
    }
    if (runs.length > 1) {
      const chips = el("div", "runs");
      for (const r of runs.slice(0, 5)) {
        const b = el("button", r.slug === run?.slug ? "on" : "", r.slug);
        b.title = `${r.stage} · ${r.kind}`;
        b.onclick = () => onPickRun(r.slug === m.viewed ? null : r.slug);
        chips.append(b);
      }
      card.append(chips);
    }
    hint.textContent = `Click an agent or a step · ←/→ switch · D decisions · N time · F follow ${m.follow ? "on" : "off"} · T theme · Esc close`;

    strip.replaceChildren();
    if (run) {
      run.route.forEach((role, i) => {
        const info = run.roles[role];
        if (i > 0) strip.append(el("div", `link${info.state === "done" || run.roles[run.route[i - 1]].state === "done" && info.state !== "idle" ? " done" : ""}`));
        const b = el("button", `${role === run.active_role ? "active" : ""} ${role === m.selected ? "sel" : ""}`);
        const node = el("div", "node");
        node.style.background = STATE_COLORS[info.state] ?? STATE_COLORS.idle;
        b.append(node, el("div", "label", roleShort(role)));
        b.title = `${role} · ${info.state}`;
        b.onclick = () => onSelectRole(role);
        strip.append(b);
      });
      strip.append(el("div", "link"));
      const gate = el("button", "");
      const gateNode = el("div", "node");
      gateNode.style.background = run.human_needed ? STATE_COLORS.escalate : run.ready_to_merge ? STATE_COLORS.done : STATE_COLORS.idle;
      gate.append(gateNode, el("div", "label", run.human_needed ? "Human" : "Merge"));
      gate.style.cursor = "default";
      strip.append(gate);
    }

    banner.className = "banner";
    if (run?.human_needed) {
      banner.classList.add("human");
      banner.textContent = "Human needed";
    } else if (run?.ready_to_merge) {
      banner.classList.add("ready");
      banner.textContent = "Ready to merge";
    } else if (!run) {
      banner.classList.add("idle");
      banner.textContent = `Waiting for a request in ${m.project || "the project"}`;
    } else if (run.active_role && run.roles[run.active_role].state === "blocked") {
      banner.classList.add("blocked");
      banner.textContent = `${run.active_role} is blocked`;
    } else {
      banner.classList.add("idle");
      banner.textContent = run.active_role ? `${run.active_role} at work` : "Idle";
    }

    const tag = run ? (run.human_needed ? "⚠" : run.ready_to_merge ? "✔" : run.active_role ? "●" : "○") : "○";
    document.title = run ? `${tag} ${run.active_role ?? (run.ready_to_merge ? "ready to merge" : "idle")} · ${run.slug}` : "Office floor";
  }
  return { show, showTip, hideTip };
}
