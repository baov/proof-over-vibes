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
  .panel header .grow { flex: 1; min-width: 0; }
  .panel header .muted { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .panel button { font: inherit; color: inherit; cursor: pointer; }
  .panel .close { background: none; border: 0; font-size: 20px; opacity: .7; }
  .about { padding: 8px 14px 0; font-size: 12px; opacity: .72; line-height: 1.4; }
  .stateline { padding: 8px 14px 0; font-size: 13px; font-weight: 600; }
  .nav { display: flex; justify-content: space-between; gap: 8px; padding: 10px 14px 0; }
  .nav button { border: 1px solid rgba(255,255,255,.25); background: none; border-radius: 999px; padding: 3px 10px; font-size: 12px; max-width: 48%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .nav button:only-child { margin-left: auto; }
  .nav button:first-child:not(:only-child) { margin-right: auto; }
  .nav .crumb { margin-right: auto; min-width: 0; flex: 0 1 auto; opacity: .8; border-style: dashed; }
  .nav .crumb + button { margin-left: 0; }
  .note { padding: 8px 14px 0; font-size: 12px; opacity: .72; line-height: 1.45; }
  .decision { margin: 10px 14px 0; padding: 8px 10px; border-radius: 8px; background: rgba(255,255,255,.06); border-left: 3px solid #64748b; font-size: 13px; line-height: 1.4; }
  .decision.pending { border-left-color: #f87171; }
  .decision .head { display: flex; justify-content: space-between; gap: 8px; font-weight: 600; }
  .decision .head small { opacity: .6; font-weight: 400; white-space: nowrap; }
  .decision .row { margin-top: 3px; opacity: .85; }
  .decision .row b { font-weight: 600; opacity: .7; }
  .decision button { margin-top: 6px; border: 1px solid rgba(255,255,255,.25); background: none; border-radius: 999px; padding: 2px 9px; font-size: 11px; }
  .docfind { padding: 8px 14px 6px; }
  .docfind input { width: 100%; box-sizing: border-box; font: inherit; font-size: 13px; color: inherit; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.16); border-radius: 8px; padding: 6px 10px; }
  .docfind input:focus { outline: 2px solid #38bdf8; outline-offset: 0; }
  .doclist { flex: 1; overflow: auto; padding: 0 0 14px; }
  .doclist button { display: block; width: 100%; text-align: left; background: none; border: 0; color: inherit; font: inherit; cursor: pointer; }
  .doclist button:focus-visible { outline: 2px solid #38bdf8; outline-offset: -2px; }
  .dochead { position: sticky; top: 0; z-index: 1; display: flex !important; align-items: baseline; gap: 8px; padding: 7px 14px !important; background: rgba(20,24,48,.97) !important; border-bottom: 1px solid rgba(255,255,255,.1) !important; font-size: 12px; font-weight: 600; }
  .dochead .chev { width: 10px; opacity: .6; }
  .dochead .dir { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; opacity: .9; }
  .dochead .count { font-weight: 600; font-size: 11px; min-width: 18px; text-align: center; padding: 0 6px; border-radius: 999px; background: rgba(255,255,255,.12); }
  .dochead .when { font-weight: 400; font-size: 11px; opacity: .55; white-space: nowrap; }
  .docrow { display: grid !important; grid-template-columns: 1fr auto; column-gap: 8px; padding: 7px 14px 7px 28px !important; border-bottom: 1px solid rgba(255,255,255,.06) !important; font-size: 13px; line-height: 1.3; }
  .docrow:hover, .dochead:hover { background: rgba(255,255,255,.07) !important; }
  .docrow .t { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .docrow .when { font-size: 11px; opacity: .55; white-space: nowrap; }
  .docrow .path { grid-column: 1 / -1; font-size: 11px; opacity: .55; margin-top: 1px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .docrow .fresh { display: inline-block; width: 7px; height: 7px; margin: 0 6px 1px -13px; border-radius: 50%; background: #38bdf8; }
  .docnone { padding: 18px 14px; font-size: 13px; opacity: .75; }
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
    title.append(el("h2", "", model.doc ? model.doc.title : "Documents"), el("div", "muted", model.doc ? model.doc.path.slice(model.doc.path.lastIndexOf("/") + 1) : "Written during the session"));
    title.title = model.doc ? model.doc.path : "";
    const close = el("button", "close", "×");
    close.setAttribute("aria-label", "Close");
    close.onclick = onClose;
    head.append(swatch, title, close);
    root.append(head);

    if (model.doc) {
      const nav = el("div", "nav");
      const back = el("button", "", "◀ All");
      back.onclick = onBackToDocs;
      nav.append(back);
      // The folder as a crumb: one click lists its documents.
      const cut = model.doc.path.lastIndexOf("/");
      if (cut > 0) {
        const dir = model.doc.path.slice(0, cut);
        const crumb = el("button", "crumb", dir.split("/").pop());
        crumb.title = `List ${dir}`;
        back.title = "All documents";
        crumb.onclick = () => {
          docView.filter = `${dir}/`;
          docView.scroll = 0;
          onBackToDocs();
        };
        nav.append(crumb);
      }
      // Neighbours in the order of the list (grouped, filtered), to read a series without going back.
      const at = docView.order.indexOf(model.doc.path);
      for (const [label, to] of [["◀", docView.order[at - 1]], ["▶", docView.order[at + 1]]]) {
        if (at < 0 || !to) continue;
        const step = el("button", "", label);
        step.setAttribute("aria-label", label === "◀" ? "Previous document" : "Next document");
        step.onclick = () => onOpenDoc(to);
        nav.append(step);
      }
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
    renderDocList(model);
  }

  // The list of documents: grouped by folder, filterable, walkable with the arrows.
  // The filter, the collapsed folders and the scroll survive the refresh every few seconds.
  const docView = { filter: "", collapsed: new Set(), scroll: 0, order: [] };
  const finder = el("input");
  finder.type = "search";
  finder.placeholder = "Filter documents ( / )";
  finder.setAttribute("aria-label", "Filter documents");
  finder.onkeydown = (event) => {
    if (event.key === "ArrowDown") root.querySelector(".doclist button")?.focus();
    if (event.key === "Escape" && finder.value) { finder.value = ""; docView.filter = ""; event.stopPropagation(); if (lastDocsModel) renderDocs(lastDocsModel); }
  };
  finder.oninput = () => {
    docView.filter = finder.value;
    docView.scroll = 0;
    if (lastDocsModel) renderDocs(lastDocsModel);
  };
  let lastDocsModel = null;

  function renderDocList(model) {
    lastDocsModel = model;
    const hadFocus = document.activeElement === finder;
    const caret = finder.selectionStart;
    const kept = root.querySelector(".doclist")?.scrollTop ?? docView.scroll;
    const query = docView.filter.trim().toLowerCase();
    const since = model.since ?? Infinity;
    const shown = model.entries.filter((e) => !query || `${e.title} ${e.path}`.toLowerCase().includes(query));

    const groups = new Map();
    for (const entry of shown) {
      const cut = entry.path.lastIndexOf("/");
      const dir = cut < 0 ? "" : entry.path.slice(0, cut);
      if (!groups.has(dir)) groups.set(dir, []);
      groups.get(dir).push({ ...entry, file: entry.path.slice(cut + 1) });
    }
    const ordered = [...groups.entries()].sort((x, y) => y[1][0].mtime - x[1][0].mtime || x[0].localeCompare(y[0]));

    docView.order = ordered.flatMap(([dir, items]) => (query || !docView.collapsed.has(dir) ? items.map((e) => e.path) : []));
    const fresh = model.entries.filter((e) => e.mtime > since).length;
    const sub = root.querySelector("header .muted");
    if (sub) sub.textContent = `${model.entries.length} documents${fresh ? ` · ${fresh} new` : ""}`;

    const find = el("div", "docfind");
    finder.value = docView.filter;
    find.append(finder);
    root.append(find);

    const list = el("div", "doclist");
    list.onkeydown = (event) => moveFocus(event, list);
    if (!shown.length) list.append(el("div", "docnone", `No document matches “${docView.filter.trim()}”.`));
    for (const [dir, items] of ordered) {
      const open = Boolean(query) || !docView.collapsed.has(dir);
      const head = el("button", "dochead");
      head.setAttribute("aria-expanded", String(open));
      head.append(el("span", "chev", open ? "▾" : "▸"));
      // Long folders keep their last two segments: the tail is what tells two folders apart.
      const parts = dir.split("/").filter(Boolean);
      const label = el("span", "dir", parts.length ? parts.slice(-2).join(" › ") : "(root)");
      label.title = dir;
      head.append(label, el("span", "count", String(items.length)), el("span", "when", ago(items[0].mtime)));
      head.onclick = () => {
        if (docView.collapsed.has(dir)) docView.collapsed.delete(dir);
        else docView.collapsed.add(dir);
        renderDocs(model);
      };
      list.append(head);
      if (!open) continue;
      for (const entry of items) {
        const row = el("button", "docrow");
        const t = el("span", "t");
        if (entry.mtime > since) {
          const dot = el("i", "fresh");
          dot.title = "Written since you opened this list";
          t.append(dot);
        }
        t.append(document.createTextNode(entry.title));
        row.append(t, el("span", "when", ago(entry.mtime)), el("span", "path", entry.file));
        row.title = entry.path;
        row.onclick = () => {
          docView.scroll = list.scrollTop; // the list comes back where it was
          onOpenDoc(entry.path);
        };
        list.append(row);
      }
    }
    root.append(list);
    list.scrollTop = kept;
    if (hadFocus) {
      finder.focus();
      if (caret != null) finder.setSelectionRange(caret, caret);
    }
  }

  function moveFocus(event, list) {
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
    const stops = [finder, ...list.querySelectorAll("button")];
    const at = stops.indexOf(document.activeElement);
    const next = stops[Math.max(0, Math.min(stops.length - 1, at + (event.key === "ArrowDown" ? 1 : -1)))];
    if (next) {
      event.preventDefault();
      next.focus();
      next.scrollIntoView({ block: "nearest" });
    }
  }

  function focusFilter() {
    if (!finder.isConnected) return false;
    finder.focus();
    finder.select();
    return true;
  }

  return { render, renderDecisions, renderDocs, focusFilter, hide };
}
