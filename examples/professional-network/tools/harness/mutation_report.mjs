#!/usr/bin/env node
// INV-010: turns Stryker's JSON report into the normalised harness output. Never edits the threshold.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseArgs } from "./lib.mjs";

const KILLED = new Set(["Killed", "Timeout"]);
const SURVIVED = new Set(["Survived", "NoCoverage"]);

/** Pure function, also used by the self-test. */
export function summarise(reportJson, config, scopeLabel) {
  const survivors = [];
  let killed = 0;
  let valid = 0;
  for (const [file, data] of Object.entries(reportJson.files ?? {})) {
    for (const m of data.mutants ?? []) {
      if (KILLED.has(m.status)) { killed += 1; valid += 1; }
      else if (SURVIVED.has(m.status)) { valid += 1; survivors.push({ file, line: m.location?.start?.line ?? 1, mutator: m.mutatorName, status: m.status }); }
    }
  }
  const score = valid === 0 ? null : (killed / valid) * 100;
  const lines = [`MUTATION — scope: ${scopeLabel} · tool: stryker (vitest runner)`];
  const threshold = config.threshold;
  let code = 0;
  if (score === null) {
    lines.push("score: n/a (no mutant generated in this scope)");
  } else {
    const verdict = threshold === null ? "no threshold yet (first baseline to record)" : score >= threshold ? "OK" : "BELOW THRESHOLD";
    lines.push(`score: ${score.toFixed(1)}% (${killed} killed / ${valid} generated)  threshold: ${threshold === null ? "none" : threshold + "%"}  → ${verdict}`);
    if (threshold !== null && score < threshold) code = config.severity === "error" ? 1 : 2;
  }
  if (survivors.length) {
    lines.push("", "Surviving mutants (add a test for the unprotected behavior, never one written only to kill the mutant):");
    for (const s of survivors.slice(0, 20)) lines.push(`  ${s.file}:${s.line}  [${s.mutator}]  ${s.status}`);
    if (survivors.length > 20) lines.push(`  … ${survivors.length - 20} more in reports/mutation/mutation.html`);
  }
  return { text: lines.join("\n"), code };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = parseArgs(process.argv.slice(2));
  const scope = process.argv.includes("--label") ? process.argv[process.argv.indexOf("--label") + 1] : "critical";
  const reportPath = path.join(args.root, "reports/mutation/mutation.json");
  if (!fs.existsSync(reportPath)) { console.error(`no report at ${reportPath}`); process.exit(1); }
  const config = JSON.parse(fs.readFileSync(path.join(args.root, "tools/harness/mutation-threshold.json"), "utf8"));
  const { text, code } = summarise(JSON.parse(fs.readFileSync(reportPath, "utf8")), config, scope);
  console.log(text);
  process.exit(code);
}
