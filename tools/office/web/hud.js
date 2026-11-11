// Everything around the floor: the run card and its switcher, the pipeline strip, the banner and the tooltip.
import { STATE_COLORS, STATE_GLYPHS, roleShort, took } from "./roles.js";

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
  .card .docs { display: block; width: 100%; margin-top: 8px; padding: 5px 8px; text-align: left; font: inherit; font-size: 12px; color: inherit; cursor: pointer; border-radius: 8px; border: 1px solid rgba(56,189,248,.5); background: rgba(56,189,248,.1); }
  .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; background: #22c55e; }
  .dot.reconnecting { background: #f59e0b; }
  .strip { position: fixed; left: 50%; bottom: 78px; transform: translateX(-50%); display: flex; align-items: center; gap: 0; z-index: 3; max-width: calc(100% - 32px); overflow-x: auto; padding: 6px 10px; border-radius: 999px; background: rgba(10,12,28,.78); border: 1px solid rgba(255,255,255,.12); backdrop-filter: blur(6px); }
  .strip:empty { display: none; }
  .strip button { font: inherit; color: inherit; cursor: pointer; background: none; border: 0; display: flex; flex-direction: column; align-items: center; gap: 3px; padding: 0 6px; }
  .strip .node { width: 22px; height: 22px; border-radius: 50%; border: 2px solid rgba(255,255,255,.25); display: flex; align-items: center; justify-content: center; box-sizing: border-box; font-size: 13px; font-weight: 800; line-height: 1; color: #fff; }
  .strip .node.gate { border-radius: 6px; }
  .strip .active .node { animation: pulse 1.2s infinite; border-color: #fff; }
  .strip .sel .node { box-shadow: 0 0 0 3px rgba(255,255,255,.45); }
  .strip .label { font-size: 11px; opacity: .85; white-space: nowrap; }
  .strip .took { font-size: 10px; opacity: .6; white-space: nowrap; margin-top: -3px; }
  .strip .link { width: 18px; height: 2px; background: rgba(255,255,255,.25); margin-bottom: 14px; }
  .strip .link.done { background: #16a34a; }
  @keyframes pulse { 50% { transform: scale(1.18); } }
  .tip { position: fixed; display: none; z-index: 5; pointer-events: none; padding: 7px 11px; background: rgba(10,12,28,.95); border: 1px solid rgba(255,255,255,.18); border-radius: 8px; font-size: 12px; max-width: 260px; line-height: 1.35; }
  .tip b { display: block; font-size: 13px; }
  .tip .muted { opacity: .65; }
  .hint { position: fixed; left: 16px; bottom: 52px; width: 210px; font-size: 12px; line-height: 1.5; color: #cbd5e1; padding: 8px 12px; border-radius: 12px; background: rgba(10,12,28,.84); border: 1px solid rgba(255,255,255,.12); pointer-events: none; }
  .hint.quiet, body.panel-open .hint { display: none; }
  .hintbtn { position: fixed; left: 16px; bottom: 14px; width: 30px; height: 30px; border-radius: 50%; font: inherit; font-size: 14px; font-weight: 700; color: #cbd5e1; cursor: pointer; background: rgba(10,12,28,.82); border: 1px solid rgba(255,255,255,.2); padding: 0; }
  body.panel-open .banner, body.panel-open .strip { left: calc((100% - var(--panel) - 32px) / 2); }
  @media (max-width: 700px) { body.panel-open .banner, body.panel-open .strip { left: 50%; } .hint, .hintbtn { display: none; } }
  .banner { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); padding: 10px 22px; border-radius: 999px; font-weight: 700; font-size: 15px; letter-spacing: .03em; white-space: nowrap; max-width: calc(100% - 32px); overflow: hidden; text-overflow: ellipsis; }
  .banner.human { background: #dc2626; color: #fff; box-shadow: 0 0 24px #dc2626aa; }
  .banner.blocked { background: #d97706; color: #fff; box-shadow: 0 0 24px #d97706aa; }
  .banner.ready { background: #16a34a; color: #fff; box-shadow: 0 0 24px #16a34aaa; }
  .banner.idle { background: rgba(10,12,28,.78); color: #cbd5e1; font-weight: 500; }
`;

export function createHud(root, { onSelectRole, onPickRun, onOpenDecisions, onOpenDocs }) {
  document.head.append(Object.assign(el("style"), { textContent: STYLE }));
  const card = el("div", "card");
  const strip = el("div", "strip");
  const banner = el("div", "banner idle");
  const tip = el("div", "tip");
  const hint = el("div", "hint");
  const hintButton = el("button", "hintbtn", "?");
  hintButton.title = "Keyboard shortcuts (?)";
  hintButton.setAttribute("aria-label", "Show the keyboard shortcuts");
  root.append(card);
  document.body.append(strip, banner, tip, hint, hintButton);

  // The shortcuts show until the first interaction, then fold into the "?" button, which brings them back.
  const toggleHint = () => hint.classList.toggle("quiet");
  if (window.innerWidth < 900) hint.classList.add("quiet"); // too narrow to leave beside the strip
  hintButton.onclick = toggleHint;
  const fold = () => {
    hint.classList.add("quiet");
    window.removeEventListener("pointerdown", fold, true);
    window.removeEventListener("keydown", fold, true);
  };
  window.addEventListener("pointerdown", fold, true);
  window.addEventListener("keydown", fold, true);

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
      // Who is at work is told once, by the banner: the card only says which run this is.
      card.append(el("div", "muted", `${run.kind} · ${run.stage} · iteration ${run.iteration}/${run.limit}`));
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
    const docs = el("button", "docs", "▤ Documents (M)");
    docs.title = "Markdown documents written under docs/ and .audit/";
    docs.onclick = onOpenDocs;
    card.append(docs);
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
    hint.replaceChildren(...["Click an agent or a step", "←/→  switch agent", "D  decisions", "M  documents", "N  time of day", `F  follow ${m.follow ? "on" : "off"}`, "T  theme", "?  this help", "Esc  close"].map((line) => el("div", "", line)));

    strip.replaceChildren();
    if (run) {
      run.route.forEach((role, i) => {
        const info = run.roles[role];
        if (i > 0) strip.append(el("div", `link${info.state === "done" || run.roles[run.route[i - 1]].state === "done" && info.state !== "idle" ? " done" : ""}`));
        const b = el("button", `${role === run.active_role ? "active" : ""} ${role === m.selected ? "sel" : ""}`);
        const node = el("div", "node", STATE_GLYPHS[info.state] ?? "");
        node.style.background = STATE_COLORS[info.state] ?? STATE_COLORS.idle;
        const duration = info.state === "done" ? took(info.reports.at(-1)?.duration) : null;
        b.append(node, el("div", "label", roleShort(role)));
        if (duration) b.append(el("div", "took", duration));
        b.title = `${role} · ${info.state}${duration ? ` · took ${duration}` : ""}`;
        b.onclick = () => onSelectRole(role);
        strip.append(b);
      });
      strip.append(el("div", "link"));
      const gate = el("button", "");
      const gateNode = el("div", "node gate", run.human_needed ? "!" : run.ready_to_merge ? "✓" : "");
      gateNode.style.background = run.human_needed ? STATE_COLORS.escalate : run.ready_to_merge ? STATE_COLORS.done : STATE_COLORS.idle;
      gate.append(gateNode, el("div", "label", run.human_needed ? "Human" : "Merge"));
      gate.style.cursor = "default";
      strip.append(gate);
    }

    banner.className = "banner";
    if (run?.human_needed) {
      banner.classList.add("human");
      const waiting = run.decisions?.pending;
      banner.textContent = waiting ? `Human needed · ${waiting} decision${waiting > 1 ? "s" : ""} waiting` : "Human needed";
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
  return { show, showTip, hideTip, toggleHint };
}
