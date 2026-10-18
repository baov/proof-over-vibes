// Self-test of the harness checks, on throwaway files only (never on project code).
// Run: npm run harness:selftest
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { check as layers } from "./check_layers.mjs";
import { check as shape } from "./check_shape.mjs";
import { check as bridge } from "./check_test_coverage.mjs";
import { check as serialized } from "./check_serialized.mjs";
import { summarise } from "./mutation_report.mjs";

function project(files) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "harness-"));
  for (const [name, content] of Object.entries(files)) {
    fs.mkdirSync(path.dirname(path.join(root, name)), { recursive: true });
    fs.writeFileSync(path.join(root, name), content);
  }
  return root;
}
const ids = (violations) => violations.map((v) => `${v.file}:${v.id}`).sort();

test("layers: clean hexagonal module passes", () => {
  const root = project({
    "src/connections/index.ts": 'export * from "./application/send";\n',
    "src/connections/domain/request.ts": 'import { MemberId } from "./member-id";\nexport const x = MemberId;\n',
    "src/connections/domain/member-id.ts": "export const MemberId = 1;\n",
    "src/connections/application/send.ts": 'import { x } from "../domain/request";\nexport const send = x;\n',
    "src/connections/infrastructure/memory.ts": 'import { send } from "../application/send";\nimport { x } from "../domain/request";\nimport pg from "pg";\nexport default [send, x, pg];\n',
    "src/posts/application/feed.ts": 'import { send } from "../../connections";\nexport default send;\n',
    "src/connections/domain/request.test.ts": 'import fs from "node:fs";\nexport default fs;\n',
  });
  assert.deepEqual(layers(root), []);
});

test("layers: each branch of ADR-0001 is caught with its own id", () => {
  const root = project({
    "src/connections/domain/a.ts": 'import fs from "node:fs";\nimport { s } from "../application/s";\nexport default [fs, s];\n',
    "src/connections/application/s.ts": 'import { m } from "../infrastructure/m";\nimport z from "zod";\nexport const s = [m, z];\n',
    "src/posts/application/f.ts": 'import { r } from "../../connections/domain/request";\nexport default r;\n',
  });
  const found = layers(root);
  assert.deepEqual(ids(found), [
    "src/connections/application/s.ts:INV-002",
    "src/connections/application/s.ts:INV-002",
    "src/connections/domain/a.ts:INV-001",
    "src/connections/domain/a.ts:INV-001",
    "src/posts/application/f.ts:INV-004",
  ]);
  assert.ok(found.every((v) => v.severity === "warn" && v.remediation.length > 20));
});

test("shape: thresholds fire, clean code passes", () => {
  const long = Array.from({ length: 45 }, (_, i) => `  const v${i} = ${i};`).join("\n");
  const root = project({
    "src/m/domain/bad.ts":
      `export function many(a: 1, b: 2, c: 3, d: 4, e: 5, f: 6) { return [a, b, c, d, e, f]; }\n` +
      `export function long() {\n${long}\n}\n` +
      `export function branchy(x: number) {\n  if (x === 1) return 1;\n  if (x === 2) return 2;\n  if (x === 3) return 3;\n  if (x === 4) return 4;\n  if (x === 5) return 5;\n  if (x === 6) return 6;\n  if (x === 7) return 7;\n  if (x === 8) return 8;\n  if (x === 9) return 9;\n  if (x === 10 && x > 0) return 10;\n  return 0;\n}\n` +
      `export function deep(x: number) {\n  if (x) { for (;;) { while (x) { if (x) { if (x) { return 1; } } } } }\n  return 0;\n}\n`,
    "src/m/domain/good.ts": "export function ok(a: number) {\n  if (a > 1) return 1;\n  else if (a > 0) return 2;\n  return 0;\n}\n",
  });
  assert.deepEqual(ids(shape(root)), ["src/m/domain/bad.ts:INV-005", "src/m/domain/bad.ts:INV-006", "src/m/domain/bad.ts:INV-007", "src/m/domain/bad.ts:INV-008"]);
});

test("bridge: ok, broken, pending, orphan", () => {
  const fm = (status, ref) => `---\nfeature: f\ntype: nominal\npriority: critical\nautomated_test: ${ref}\nstatus: ${status}\n---\n# case\nSource: PRD 5.1\n`;
  const root = project({
    "docs/business/test-cases/f/ok.md": fm("covered", "tests/a.test.ts::sends a request"),
    "docs/business/test-cases/f/broken.md": fm("covered", "tests/a.test.ts::missing name"),
    "docs/business/test-cases/f/pending.md": fm("pending", "null"),
    "tests/a.test.ts": 'it("sends a request", () => {});\n',
    "tests/b.test.ts": 'it("lonely", () => {});\n',
  });
  const r = bridge(root);
  assert.equal(r.ok, 1);
  assert.equal(r.broken.length, 1);
  assert.equal(r.pending.length, 1);
  assert.deepEqual(r.orphans, ["tests/b.test.ts"]);
  assert.equal(r.unsourced, 0);
});

test("mutation: score, threshold and exit codes", () => {
  const report = { files: { "src/a.ts": { mutants: [
    { status: "Killed", mutatorName: "X", location: { start: { line: 1 } } },
    { status: "Killed", mutatorName: "X", location: { start: { line: 2 } } },
    { status: "Survived", mutatorName: "ConditionalExpression", location: { start: { line: 7 } } },
    { status: "Ignored", mutatorName: "X", location: { start: { line: 9 } } },
  ] } } };
  const none = summarise(report, { threshold: null, severity: "warn" }, "critical");
  assert.equal(none.code, 0);
  assert.match(none.text, /66\.7%/);
  assert.match(none.text, /src\/a\.ts:7\s+\[ConditionalExpression\]/);
  assert.equal(summarise(report, { threshold: 60, severity: "warn" }, "critical").code, 0);
  assert.equal(summarise(report, { threshold: 70, severity: "warn" }, "critical").code, 2);
  assert.equal(summarise(report, { threshold: 70, severity: "error" }, "critical").code, 1);
});

test("serialized: pending without a queue file, clean when wired, caught when a method bypasses it", () => {
  const index = (body) =>
    'import { SerialQueue } from "./infrastructure/serial-queue.js";\n' +
    "export function createConnections(o: { ids: unknown }) {\n  const queue = new SerialQueue();\n  return {\n" + body + "\n  };\n}\n";
  const queueFile = { "src/connections/infrastructure/serial-queue.ts": "export class SerialQueue { run<T>(f: () => Promise<T>) { return f(); } }\n" };
  const quiet = (fn) => { const log = console.log; console.log = () => {}; try { return fn(); } finally { console.log = log; } };
  assert.deepEqual(quiet(() => serialized(project({ "src/connections/index.ts": index("    a: () => 1,") }))), []);
  const ok = project({ ...queueFile, "src/connections/index.ts": index("    a: (x) => queue.run(() => use(x)),\n    b: (y) => queue.run(async () => use(y)),") });
  assert.deepEqual(serialized(ok), []);
  const bad = project({ ...queueFile, "src/connections/index.ts": index("    a: (x) => queue.run(() => use(x)),\n    b: (y) => use(y),") });
  const found = serialized(bad);
  assert.deepEqual(ids(found), ["src/connections/index.ts:INV-011"]);
  assert.match(found[0].message, /`b`/);
  assert.ok(found[0].severity === "warn" && found[0].remediation.length > 20);
  const unwired = project({ ...queueFile, "src/connections/index.ts": "export function createConnections() { return { a: () => 1 }; }\n" });
  assert.deepEqual(ids(serialized(unwired)), ["src/connections/index.ts:INV-011"]);
});
