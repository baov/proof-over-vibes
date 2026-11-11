// A small, safe markdown renderer for reports: headings, lists, code, bold and inline code.
// Everything goes through textContent, so a report can never inject HTML.
function el(tag, text) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
}

function inline(parent, text) {
  let last = 0;
  for (const match of text.matchAll(/(`[^`]+`|\*\*[^*]+\*\*)/g)) {
    if (match.index > last) parent.append(text.slice(last, match.index));
    const token = match[0];
    parent.append(token.startsWith("`") ? el("code", token.slice(1, -1)) : el("strong", token.slice(2, -2)));
    last = match.index + token.length;
  }
  if (last < text.length) parent.append(text.slice(last));
}

export function renderMarkdown(text) {
  const out = document.createDocumentFragment();
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  let paragraph = [];
  let list = null;
  const flush = () => {
    if (paragraph.length) {
      const p = el("p");
      inline(p, paragraph.join("\n"));
      out.append(p);
      paragraph = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^```/.test(line)) {
      flush();
      list = null;
      const code = [];
      while (++i < lines.length && !/^```/.test(lines[i])) code.push(lines[i]);
      out.append(el("pre", code.join("\n")));
      continue;
    }
    if (/^\s*\|/.test(line)) {
      // Tables stay monospace, as written.
      flush();
      list = null;
      const rows = [line];
      while (i + 1 < lines.length && /^\s*\|/.test(lines[i + 1])) rows.push(lines[++i]);
      out.append(el("pre", rows.join("\n")));
      continue;
    }
    const heading = /^(#{1,4})\s+(.*)$/.exec(line);
    if (heading) {
      flush();
      list = null;
      const h = el(`h${heading[1].length + 2}`);
      inline(h, heading[2]);
      out.append(h);
      continue;
    }
    const item = /^\s*(?:[-*]|\d+\.)\s+(.*)$/.exec(line);
    if (item) {
      flush();
      if (!list) {
        list = el("ul");
        out.append(list);
      }
      const li = el("li");
      inline(li, item[1]);
      list.append(li);
      continue;
    }
    if (!line.trim()) {
      flush();
      list = null;
      continue;
    }
    paragraph.push(line.trim());
  }
  flush();
  return out;
}
