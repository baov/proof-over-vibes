#!/usr/bin/env node
// INV-009 — block B: test-case bridge to the real tests (port of the generic starter, no dependency).
// Every scenario under docs/business/test-cases/ points at a test that exists; reports tests with no test-case.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseArgs } from "./lib.mjs";

const ID = "INV-009";
const CASES_DIR = "docs/business/test-cases";
const VALID_STATUS = new Set(["covered", "pending", "manual"]);
const IGNORED = new Set([".git", "node_modules", "dist", "coverage", "reports", ".stryker-tmp", ".plans"]);

const EXPLANATION = `[${ID}] Test-case bridge to the real tests
Every scenario under ${CASES_DIR}/ carries a YAML front-matter whose \`automated_test\` field names its test as <path>::<test name>
(Vitest: the string given to it()/test()). This script checks the file and the test name exist, and reports test files no test-case mentions.
  error  covered_broken (broken reference), malformed front-matter
  warn   pending (scenario not automated), orphan test file (*.test.ts)
  info   test-cases naming no source (a \`source\` key, a "## Source" section or a "Source:" line): counted, never a warning
Known limit: this checks that a test EXISTS, not what it is worth. That is block D (mutation, INV-010).`;

function frontMatter(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
  if (lines[0]?.trim() !== "---") return { fields: null, end: 0 };
  const fields = {};
  for (let i = 1; i < lines.length; i += 1) {
    if (lines[i].trim() === "---") return { fields, end: i + 1 };
    const m = lines[i].match(/^([A-Za-z_][\w-]*)\s*:\s*(.*)$/);
    if (m) fields[m[1]] = m[2].replace(/\s+#.*$/, "").trim().replace(/^['"]|['"]$/g, "");
  }
  return { fields: null, end: 0 };
}

function walk(dir, accept, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORED.has(e.name)) continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walk(full, accept, out);
    else if (accept(e.name)) out.push(full);
  }
  return out;
}

const hasSource = (file, fields) => {
  if (fields.source?.trim()) return !["none", "null", "~"].includes(fields.source.trim().toLowerCase());
  const text = fs.readFileSync(file, "utf8");
  const m = /^\s*(?:#{1,6}\s*source\b|[-*]?\s*\*{0,2}source\*{0,2}\s*:)/im.exec(text);
  return Boolean(m) && !text.slice(m.index + m[0].length).replace(/^[\s*:]+/, "").toLowerCase().startsWith("none");
};

export function check(root) {
  const r = { ok: 0, broken: [], malformed: [], pending: [], manual: 0, orphans: [], unsourced: 0, total: 0 };
  const casesRoot = path.join(root, CASES_DIR);
  const referenced = new Set();
  for (const file of walk(casesRoot, (n) => n.endsWith(".md")).sort()) {
    r.total += 1;
    const rel = path.relative(root, file).split(path.sep).join("/");
    const { fields, end } = frontMatter(file);
    if (!fields) { r.malformed.push([rel, 1, "front-matter missing or unreadable"]); continue; }
    if (!hasSource(file, fields)) r.unsourced += 1;
    const status = (fields.status ?? "").toLowerCase();
    if (!VALID_STATUS.has(status)) { r.malformed.push([rel, end, `invalid \`status\` field (${status || "empty"})`]); continue; }
    if (status === "manual") { r.manual += 1; continue; }
    const ref = (fields.automated_test ?? "").trim();
    if (status === "pending" || ["", "null", "~"].includes(ref)) { r.pending.push([rel, end]); continue; }
    const [filePart, ...rest] = ref.split("::");
    const testName = rest.join("::").trim();
    const target = path.join(root, filePart.trim());
    if (!fs.existsSync(target)) { r.broken.push([rel, end, `the test file \`${filePart.trim()}\` does not exist`]); continue; }
    referenced.add(filePart.trim());
    if (testName && !fs.readFileSync(target, "utf8").includes(testName)) {
      r.broken.push([rel, end, `the test \`${testName}\` is nowhere to be found in \`${filePart.trim()}\``]); continue;
    }
    r.ok += 1;
  }
  for (const t of walk(root, (n) => /\.(test|spec)\.ts$/.test(n)).sort()) {
    const rel = path.relative(root, t).split(path.sep).join("/");
    if (!referenced.has(rel)) r.orphans.push(rel);
  }
  return r;
}

export function emit(r) {
  for (const [p, l, why] of r.broken) console.log(`${p}:${l}: [${ID}] test-case marked \`covered\` but ${why} — fix the \`automated_test\` field, or move the test-case back to \`status: pending\` if the test was deleted on purpose`);
  for (const [p, l, why] of r.malformed) console.log(`${p}:${l}: [${ID}] ${why} — add a conforming front-matter (feature, type, priority, automated_test, status)`);
  for (const [p, l] of r.pending) console.log(`${p}:${l}: [${ID}] test-case with no automated test — write the test then fill in \`automated_test\`, or set \`status: manual\` if it will never be automated`);
  for (const p of r.orphans) console.log(`${p}:1: [${ID}] test file with no test-case attached — create the matching test-case under ${CASES_DIR}/, or add the path to IGNORED in this script if it is a purely technical test`);
  console.error(`${r.total} test-cases: ${r.ok} covered_ok, ${r.broken.length} covered_broken, ${r.pending.length} pending, ${r.manual} manual, ${r.malformed.length} malformed. ${r.orphans.length} orphan test(s).`);
  if (r.unsourced) console.error(`${r.unsourced} of ${r.total} test-cases name no source (information only).`);
  if (r.broken.length || r.malformed.length) return 1;
  return r.pending.length || r.orphans.length ? 2 : 0;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = parseArgs(process.argv.slice(2));
  if (args.explain) console.log(EXPLANATION);
  else process.exit(emit(check(args.root)));
}
