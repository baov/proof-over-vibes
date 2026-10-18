// Shared helpers of the harness scripts. No dependency beyond TypeScript (compiler API).
import fs from "node:fs";
import path from "node:path";
import ts from "typescript";

/** Parses `--explain` and `--root <path>`; the contract shared by every script. */
export function parseArgs(argv) {
  const args = { explain: false, root: process.cwd() };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--explain") args.explain = true;
    else if (argv[i] === "--root") args.root = path.resolve(argv[(i += 1)] ?? ".");
  }
  return args;
}

/** Production TypeScript files under <root>/src (tests and declaration files excluded). */
export function sourceFiles(root) {
  const out = [];
  const walk = (dir) => {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name !== "node_modules") walk(full);
      } else if (/\.ts$/.test(entry.name) && !/\.(test|spec)\.ts$/.test(entry.name) && !/\.d\.ts$/.test(entry.name)) {
        out.push(full);
      }
    }
  };
  walk(path.join(root, "src"));
  return out.sort();
}

export function parse(file) {
  return ts.createSourceFile(file, fs.readFileSync(file, "utf8"), ts.ScriptTarget.Latest, true);
}

export function lineOf(sf, node) {
  return sf.getLineAndCharacterOfPosition(node.getStart(sf)).line + 1;
}

export const rel = (root, file) => path.relative(root, file).split(path.sep).join("/");

/** Prints the violations, then returns the exit code: 0 none, 1 error, 2 warn only. */
export function report(violations, name) {
  for (const v of violations) {
    console.log(`${v.file}:${v.line}: [${v.id}] ${v.message} — ${v.remediation}`);
  }
  console.error(`${name}: ${violations.length} violation(s).`);
  if (violations.some((v) => v.severity === "error")) return 1;
  return violations.length > 0 ? 2 : 0;
}
