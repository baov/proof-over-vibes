// The side panel: the screen of the selected agent. It shows the report the role wrote.
import { renderMarkdown } from "./markdown.js";
import { STATE_COLORS, ago } from "./roles.js";

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

const STYLE = `
  .panel { position: fixed; top: 16px; right: 16px; bottom: 16px; width: var(--panel); max-width: calc(100vw - 32px); display: none; flex-direction: column;
    background: rgba(10,12,28,.92); border: 1px solid rgba(255,255,255,.14); border-radius: 14px; backdrop-filter: blur(8px); z-index: 4; overflow: hidden; }
  .panel.open { display: flex; }
  .panel header { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-bottom: 1px solid rgba(255,255,255,.1); }
  .panel header .swatch { width: 10px; height: 34px; border-radius: 5px; }
  .panel header h2 { margin: 0; font-size: 16px; line-height: 1.1; }
  .panel header .muted { font-size: 12px; opacity: .65; }
  .panel header .grow { flex: 1; }
  .panel button { font: inherit; color: inherit; cursor: pointer; }
  .panel .close { background: none; border: 0; font-size: 20px; opacity: .7; }
  .about { padding: 8px 14px 0; font-size: 12px; opacity: .72; line-height: 1.4; }
  .stateline { padding: 8px 14px 0; font-size: 13px; font-weight: 600; }
  .nav { display: flex; justify-content: space-between; gap: 8px; padding: 10px 14px 0; }
  .nav button { border: 1px solid rgba(255,255,255,.25); background: none; border-radius: 999px; padding: 3px 10px; font-size: 12px; max-width: 48%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .nav button:only-child { margin-left: auto; }
  .note { padding: 8px 14px 0; font-size: 12px; opacity: .72; line-height: 1.45; }
  .decision { margin: 10px 14px 0; padding: 8px 10px; border-radius: 8px; background: rgba(255,255,255,.06); border-left: 3px solid #64748b; font-size: 13px; line-height: 1.4; }
  .decision.pending { border-left-color: #f87171; }
  .decision .head { display: flex; justify-content: space-between; gap: 8px; font-weight: 600; }
  .decision .head small { opacity: .6; font-weight: 400; white-space: nowrap; }
  .decision .row { margin-top: 3px; opacity: .85; }
  .decision .row b { font-weight: 600; opacity: .7; }
  .decision button { margin-top: 6px; border: 1px solid rgba(255,255,255,.25); background: none; border-radius: 999px; padding: 2px 9px; font-size: 11px; }
  .doclist { flex: 1; overflow: auto; padding: 8px 0 14px; }
  .doclist button { display: block; width: 100%; text-align: left; background: none; border: 0; border-bottom: 1px solid rgba(255,255,255,.07); padding: 8px 14px; font-size: 13px; }
  .doclist button:hover { background: rgba(255,255,255,.07); }
  .doclist .path { display: block; font-size: 11px; opacity: .6; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .chips { display: flex; gap: 6px; flex-wrap: wrap; padding: 10px 14px 0; }
  .chip { font-size: 11px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; padding: 3px 8px; border-radius: 999px; color: #fff; }
  .frise { display: flex; gap: 6px; align-items: center; padding: 10px 14px 0; font-size: 12px; opacity: .95; }
  .frise button { width: 26px; height: 26px; border-radius: 50%; border: 2px solid transparent; background: rgba(255,255,255,.1); font-size: 12px; font-weight: 700; }
  .frise button.on { border-color: #fff; }
  .why { margin: 10px 14px 0; padding: 8px 10px; border-left: 3px solid #d97706; background: rgba(217,119,6,.12); font-size: 13px; border-radius: 4px; }
  .why b { display: block; font-size: 11px; letter-spacing: .06em; text-transform: uppercase; opacity: .8; }
  .body { flex: 1; overflow: auto; padding: 8px 14px 14px; font-size: 13px; line-height: 1.5; }
  .body h3, .body h4, .body h5, .body h6 { margin: 14px 0 4px; font-size: 14px; }
  .body p { margin: 6px 0; white-space: pre-line; }
  .body ul { margin: 6px 0; padding-left: 20px; }
  .body pre { background: rgba(255,255,255,.07); padding: 8px; border-radius: 6px; overflow: auto; font-size: 12px; }
  .body code { background: rgba(255,255,255,.1); padding: 1px 4px; border-radius: 4px; font-size: 12px; }
  .empty { flex: 1; padding: 18px 14px; opacity: .85; font-size: 13px; line-height: 1.5; }
  .empty code { background: rgba(255,255,255,.1); padding: 1px 4px; border-radius: 4px; }
  .panel footer { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 8px 14px; border-top: 1px solid rgba(255,255,255,.1); font-size: 12px; }
  .panel footer .grow { flex: 1 1 100%; opacity: .7; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .panel footer .spacer { flex: 1; }
  .body.question { margin: 10px 14px 0; border-left: 3px solid #d97706; background: rgba(217,119,6,.1); border-radius: 4px; flex: 0 1 auto; max-height: 45%; padding: 6px 12px 10px; }
  .body.question::before { content: "Waiting for an answer"; display: block; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; opacity: .8; margin-bottom: 2px; }
  .panel footer button { border: 1px solid rgba(255,255,255,.25); background: none; border-radius: 999px; padding: 3px 10px; }
  .panel footer button.on { background: #2563eb; border-color: #2563eb; }
  @media (max-width: 700px) { .panel { top: auto; left: 8px; right: 8px; bottom: 8px; width: auto; max-width: none; max-height: 55vh; } }
`;

export function createPanel({ onClose, onPick, onToggleFollow, onNavigate, onOpenDoc, onBackToDocs }) {
  document.head.append(Object.assign(document.createElement("style"), { textContent: STYLE }));
  const root = el("aside", "panel");
  root.setAttribute("aria-label", "Agent screen");
  document.body.append(root);

  function setOpen(open) {
    if (root.classList.contains("open") === open) return;
    root.classList.toggle("open", open);
    document.body.classList.toggle("panel-open", open);
    window.dispatchEvent(new Event("resize")); // the canvas changed width
  }

  function hide() {
    setOpen(false);
  }

  // model: { role, team, color, state, verdict, expects, history, index, report, loading, error, follow }
  function render(model) {
    const scroll = root.querySelector(".body")?.scrollTop ?? 0;
    root.replaceChildren();
    setOpen(true);

    const head = el("header");
    const swatch = el("div", "swatch");
    swatch.style.background = model.color;
    const title = el("div", "grow");
    title.append(el("h2", "", model.title), el("div", "muted", model.team));
    const close = el("button", "close", "×");
    close.setAttribute("aria-label", "Close");
    close.onclick = onClose;
    head.append(swatch, title, close);
    root.append(head);

    const chips = el("div", "chips");
    const chip = (text, color) => {
      const c = el("span", "chip", text);
      c.style.background = color;
      chips.append(c);
    };
    chip(model.state, STATE_COLORS[model.state] ?? STATE_COLORS.idle);
    if (model.verdict) chip(model.verdict, model.verdict === "GO" ? "#16a34a" : "#dc2626");
    const severity = model.report?.front?.severity;
    if (severity) chip(severity, "#7c3aed");
    root.append(chips);
    root.append(el("div", "stateline", model.stateLine));
    if (model.about) root.append(el("div", "about", model.about));
    if (model.prev || model.next) {
      const nav = el("div", "nav");
      if (model.prev) {
        const back = el("button", "", `◀ From ${model.prev.title}`);
        back.onclick = () => onNavigate(model.prev.role);
        nav.append(back);
      }
      if (model.next) {
        const onward = el("button", "", `To ${model.next.title} ▶`);
        onward.onclick = () => onNavigate(model.next.role);
        nav.append(onward);
      }
      root.append(nav);
    }

    if (model.history.length > 1) {
      const frise = el("div", "frise");
      frise.append(el("span", "", "Reports"));
      model.history.forEach((entry, i) => {
        const b = el("button", i === model.index ? "on" : "", String(i + 1));
        b.title = entry.name;
        b.style.background = STATE_COLORS[entry.status] ?? STATE_COLORS.idle;
        b.onclick = () => onPick(i === model.history.length - 1 ? null : i);
        frise.append(b);
      });
      root.append(frise);
    }

    const reasons = model.report?.front?.reasons;
    if (reasons && reasons !== "[]" && reasons !== "") {
      const why = el("div", "why");
      why.append(el("b", "", "Reasons"), document.createTextNode(reasons.replace(/^\[|\]$/g, "")));
      root.append(why);
    }

    const beingWritten = model.report && !Object.keys(model.report.front).length && model.report.body.trimStart().startsWith("---");
    if (model.report && !beingWritten) {
      const body = el("div", model.state === "blocked" ? "body question" : "body");
      body.append(renderMarkdown(model.report.body));
      if (model.report.truncated) body.append(el("p", "", "(The report is longer; only the beginning is shown.)"));
      root.append(body);
      body.scrollTop = scroll;
    } else {
      const empty = el("div", "empty");
      if (beingWritten) empty.textContent = "The report is being written right now.";
      else if (model.loading) empty.textContent = "Loading…";
      else if (model.error) empty.textContent = model.error;
      else if (!model.expects) empty.textContent = "This page does not read a file for this role.";
      else {
        empty.append(document.createTextNode(model.state === "working" ? "Working now. Its report appears here when it writes it." : "Nothing written yet. "), document.createTextNode(" Expected file: "), el("code", "", model.expects));
      }
      root.append(empty);
    }

    const foot = el("footer");
    foot.append(el("span", "grow", model.report ? `${model.report.name} · ${ago(model.report.mtime)}` : ""));
    foot.append(el("span", "spacer"));
    if (model.report?.path) {
      const copy = el("button", "", "Copy path");
      copy.onclick = () => {
        navigator.clipboard?.writeText(model.report.path).then(() => { copy.textContent = "Copied"; }, () => { copy.textContent = model.report.path; });
      };
      foot.append(copy);
    }
    const follow = el("button", model.follow ? "on" : "", "Follow activity");
    follow.setAttribute("aria-pressed", String(model.follow));
    follow.onclick = onToggleFollow;
    foot.append(follow);
    root.append(foot);
  }

  // The decisions of a run that nobody read yet, or that wait for a person. Read-only: the answer goes in the log.
  function renderDecisions(model) {
    root.replaceChildren();
    setOpen(true);
    const head = el("header");
    const swatch = el("div", "swatch");
    swatch.style.background = "#fbbf24";
    const title = el("div", "grow");
    title.append(el("h2", "", "Decisions to review"), el("div", "muted", model.run));
    const close = el("button", "close", "×");
    close.setAttribute("aria-label", "Close");
    close.onclick = onClose;
    head.append(swatch, title, close);
    root.append(head);

    const pending = model.entries.filter((e) => e.status === "human-needed").length;
    const unread = model.entries.length - pending;
    const chips = el("div", "chips");
    for (const [count, label, color] of [[pending, "waiting for you", "#dc2626"], [unread, "never read", "#64748b"]]) {
      if (count) {
        const chip = el("span", "chip", `${count} ${label}`);
        chip.style.background = color;
        chips.append(chip);
      }
    }
    root.append(chips);
    root.append(el("div", "note", "A delegated decision is a role's recommendation that was relayed without anyone reading it. If you disagree with one, add an `answered` entry to the log: this page never writes it."));

    const body = el("div", "body");
    body.style.padding = "0 0 14px";
    if (model.loading) body.append(el("div", "empty", "Loading…"));
    else if (!model.entries.length) body.append(el("div", "empty", "Nothing to review for this run."));
    for (const d of model.entries) {
      const card = el("div", `decision${d.status === "human-needed" ? " pending" : ""}`);
      const top = el("div", "head");
      top.append(el("span", "", d.title || d.id), el("small", "", d.id));
      card.append(top);
      const line = (label, value) => {
        if (!value || value === "none") return;
        const row = el("div", "row");
        row.append(el("b", "", `${label}: `), document.createTextNode(value));
        card.append(row);
      };
      line(d.status === "human-needed" ? "Status" : "Answer", d.status === "human-needed" ? "waiting for a person" : d.answer);
      line("Recommended", d.recommended);
      line("Source", d.source);
      const copy = el("button", "", "Copy reference");
      copy.onclick = () => {
        const ref = `${d.id} · ${model.path}`;
        navigator.clipboard?.writeText(ref).then(() => { copy.textContent = "Copied"; }, () => { copy.textContent = ref; });
      };
      card.append(copy);
      body.append(card);
    }
    root.append(body);

    const foot = el("footer");
    foot.append(el("span", "grow", model.path));
    root.append(foot);
  }

  // The Markdown documents of the project (docs/, .audit/): a list, then one document at a time.
  // model: { entries, doc, loading, error }
  function renderDocs(model) {
    const scroll = root.querySelector(".body")?.scrollTop ?? 0;
    root.replaceChildren();
    setOpen(true);
    const head = el("header");
    const swatch = el("div", "swatch");
    swatch.style.background = "#38bdf8";
    const title = el("div", "grow");
    title.append(el("h2", "", model.doc ? model.doc.title : "Documents"), el("div", "muted", model.doc ? model.doc.path : "Written during the session"));
    const close = el("button", "close", "×");
    close.setAttribute("aria-label", "Close");
    close.onclick = onClose;
    head.append(swatch, title, close);
    root.append(head);

    if (model.doc) {
      const nav = el("div", "nav");
      const back = el("button", "", "◀ All documents");
      back.onclick = onBackToDocs;
      nav.append(back);
      root.append(nav);
      const body = el("div", "body");
      body.append(renderMarkdown(model.doc.body));
      if (model.doc.truncated) body.append(el("p", "", "(The document is longer; only the beginning is shown.)"));
      root.append(body);
      body.scrollTop = scroll;
      const foot = el("footer");
      foot.append(el("span", "grow", `${model.doc.path} · ${ago(model.doc.mtime)}`));
      root.append(foot);
      return;
    }
    if (model.loading || model.error || !model.entries.length) {
      root.append(el("div", "empty", model.loading ? "Loading…" : model.error || "No document yet. The Markdown files a session writes under docs/ or .audit/ appear here."));
      return;
    }
    const list = el("div", "doclist");
    for (const entry of model.entries) {
      const row = el("button", "");
      row.append(document.createTextNode(`${entry.title} · ${ago(entry.mtime)}`), el("span", "path", entry.path));
      row.onclick = () => onOpenDoc(entry.path);
      list.append(row);
    }
    root.append(list);
  }

  return { render, renderDecisions, renderDocs, hide };
}
