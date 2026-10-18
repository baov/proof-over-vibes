#!/usr/bin/env node
// INV-001..INV-004: the dependency rule of ADR-0001 (modular monolith, hexagonal modules).
import path from "node:path";
import { pathToFileURL } from "node:url";
import ts from "typescript";
import { lineOf, parse, parseArgs, rel, report, sourceFiles } from "./lib.mjs";

const SEVERITY = "warn"; // ADR-0001 starts in warn; moving to error is a human decision (docs/technical/invariants.md)

const EXPLANATION = `Dependency rule of ADR-0001, checked on every production file under src/<module>/:
  [INV-001] domain imports nothing outside src/<module>/domain (no package, no Node API, no other layer).
  [INV-002] application imports only src/<module>/domain and src/<module>/application.
  [INV-003] infrastructure imports only src/<module>/{infrastructure,application,domain}.
  [INV-004] a module reaches another module only through src/<other>/index.ts (no deep import).
Test files (*.test.ts) are out of scope. Severity: ${SEVERITY}. Details: docs/technical/invariants.md`;

const ALLOWED = {
  domain: ["domain"],
  application: ["domain", "application"],
  infrastructure: ["domain", "application", "infrastructure"],
};
const LAYER_ID = { domain: "INV-001", application: "INV-002", infrastructure: "INV-003" };

/** All module specifiers of a file: import/export ... from, import(), require(). */
function specifiers(sf) {
  const found = [];
  const visit = (node) => {
    if ((ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) && node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier)) {
      found.push({ spec: node.moduleSpecifier.text, node });
    } else if (ts.isCallExpression(node) && node.arguments.length > 0 && ts.isStringLiteralLike(node.arguments[0])) {
      const callee = node.expression;
      if (callee.kind === ts.SyntaxKind.ImportKeyword || (ts.isIdentifier(callee) && callee.text === "require")) {
        found.push({ spec: node.arguments[0].text, node });
      }
    }
    ts.forEachChild(node, visit);
  };
  visit(sf);
  return found;
}

/** Where a file sits: { module, layer } for src/<module>/<layer>/..., { module, layer: null } for src/<module>/x.ts. */
function locate(srcRelative) {
  const parts = srcRelative.split("/");
  if (parts[0] === "") return null;
  const layer = parts.length >= 2 && ALLOWED[parts[1]] ? parts[1] : null;
  return { module: parts[0], layer, rest: parts.slice(1) };
}

export function check(root) {
  const violations = [];
  const srcDir = path.join(root, "src");
  for (const file of sourceFiles(root)) {
    const srcRelative = path.relative(srcDir, file).split(path.sep).join("/");
    if (!srcRelative.includes("/")) continue; // a file directly under src/ belongs to no module
    const here = locate(srcRelative);
    const sf = parse(file);
    for (const { spec, node } of specifiers(sf)) {
      const push = (id, message, remediation) =>
        violations.push({ file: rel(root, file), line: lineOf(sf, node), id, message, remediation, severity: SEVERITY });
      const isRelative = spec.startsWith(".");
      if (!isRelative) {
        // A package or Node API is an adapter's business; it is forbidden in domain and application only.
        if (here.layer === "domain" || here.layer === "application") {
          push(LAYER_ID[here.layer], `\`${spec}\` imported in the ${here.layer} layer of module \`${here.module}\``,
            `${here.layer} imports no package and no Node API: put the call in src/${here.module}/infrastructure and expose a port in ${here.layer === "domain" ? "domain" : "application"}`);
        }
        continue;
      }
      const target = path.relative(srcDir, path.resolve(path.dirname(file), spec)).split(path.sep).join("/");
      if (target.startsWith("..")) {
        if (here.layer) push(LAYER_ID[here.layer], `\`${spec}\` leaves src/`, `keep imports inside src/${here.module}/ (ADR-0001)`);
        continue;
      }
      const there = locate(target);
      if (!there) continue;
      if (there.module !== here.module) {
        const viaIndex = there.rest.length === 0 || (there.rest.length === 1 && /^index(\.[jt]s)?$/.test(there.rest[0]));
        if (!viaIndex) {
          push("INV-004", `deep import into module \`${there.module}\` (\`${spec}\`)`,
            `import from src/${there.module}/index.ts only; if it exposes too little, ask the owner of \`${there.module}\` to add it to its public entry point`);
        }
        continue;
      }
      if (here.layer && there.layer && !ALLOWED[here.layer].includes(there.layer)) {
        push(LAYER_ID[here.layer], `${here.layer} imports the ${there.layer} layer (\`${spec}\`)`,
          `${here.layer} may only import ${ALLOWED[here.layer].join(", ")} of module \`${here.module}\`: move the code, or expose a port in application and implement it in infrastructure`);
      } else if (here.layer && !there.layer) {
        push(LAYER_ID[here.layer], `${here.layer} imports the module root (\`${spec}\`)`,
          `${here.layer} may only import ${ALLOWED[here.layer].join(", ")} of module \`${here.module}\`, never the module's index.ts`);
      }
    }
  }
  return violations;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = parseArgs(process.argv.slice(2));
  if (args.explain) console.log(EXPLANATION);
  else process.exit(report(check(args.root), "check_layers"));
}
