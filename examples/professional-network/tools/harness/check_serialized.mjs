#!/usr/bin/env node
// INV-011: every operation of `Connections` built in createConnections goes through the module's queue (ADR-0002).
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import ts from "typescript";
import { lineOf, parse, parseArgs, rel, report } from "./lib.mjs";

const SEVERITY = "warn"; // ADR-0002 starts in warn; moving to error is a human decision (docs/technical/invariants.md)
const QUEUE_FILE = "src/connections/infrastructure/serial-queue.ts";
const ENTRY_FILE = "src/connections/index.ts";
const FACTORY = "createConnections";

const EXPLANATION = `Serialization rule of ADR-0002, checked on ${ENTRY_FILE}:
  [INV-011] every method of the object returned by ${FACTORY} goes through the queue of ${QUEUE_FILE}:
            the file imports the queue, ${FACTORY} creates it, and each method body uses it.
Pending: while ${QUEUE_FILE} does not exist, the check prints a "pending" status and passes (exit 0).
Severity: ${SEVERITY}. Details: docs/technical/invariants.md`;

const hasName = (node, names) => {
  let found = false;
  const visit = (n) => {
    if (found) return;
    if (ts.isIdentifier(n) && names.has(n.text)) found = true;
    else ts.forEachChild(n, visit);
  };
  visit(node);
  return found;
};

/** Local names imported from the queue module. */
function queueImports(sf) {
  const names = new Set();
  for (const st of sf.statements) {
    if (!ts.isImportDeclaration(st) || !ts.isStringLiteral(st.moduleSpecifier)) continue;
    if (!/(^|\/)serial-queue(\.[jt]s)?$/.test(st.moduleSpecifier.text)) continue;
    const bindings = st.importClause?.namedBindings;
    if (st.importClause?.name) names.add(st.importClause.name.text);
    if (bindings && ts.isNamedImports(bindings)) bindings.elements.forEach((e) => names.add(e.name.text));
    if (bindings && ts.isNamespaceImport(bindings)) names.add(bindings.name.text);
  }
  return names;
}

function findFactory(sf) {
  let found = null;
  const visit = (n) => {
    if (found) return;
    if (ts.isFunctionDeclaration(n) && n.name?.text === FACTORY) found = n;
    else if (ts.isVariableDeclaration(n) && ts.isIdentifier(n.name) && n.name.text === FACTORY && n.initializer &&
      (ts.isArrowFunction(n.initializer) || ts.isFunctionExpression(n.initializer))) found = n.initializer;
    else ts.forEachChild(n, visit);
  };
  visit(sf);
  return found;
}

/** Object literals returned by the factory (return statement or expression body). */
function returnedObjects(fn) {
  const out = [];
  const unwrap = (e) => (e && (ts.isParenthesizedExpression(e) || ts.isAsExpression(e) || ts.isSatisfiesExpression(e)) ? unwrap(e.expression) : e);
  const visit = (n) => {
    if (n !== fn && (ts.isFunctionLike(n))) return;
    if (ts.isReturnStatement(n)) {
      const e = unwrap(n.expression);
      if (e && ts.isObjectLiteralExpression(e)) out.push(e);
    }
    ts.forEachChild(n, visit);
  };
  visit(fn);
  if (!ts.isBlock(fn.body)) {
    const e = unwrap(fn.body);
    if (ts.isObjectLiteralExpression(e)) out.push(e);
  }
  return out;
}

const propName = (p) => (p.name && (ts.isIdentifier(p.name) || ts.isStringLiteralLike(p.name)) ? p.name.text : "<computed>");

export function check(root) {
  const violations = [];
  if (!fs.existsSync(path.join(root, QUEUE_FILE))) {
    console.log(`check_serialized: pending - ${QUEUE_FILE} does not exist yet (ADR-0002 queue not built); INV-011 not evaluated.`);
    return violations;
  }
  const entry = path.join(root, ENTRY_FILE);
  const push = (sf, node, message, remediation) =>
    violations.push({ file: ENTRY_FILE, line: sf && node ? lineOf(sf, node) : 1, id: "INV-011", message, remediation, severity: SEVERITY });
  if (!fs.existsSync(entry)) {
    push(null, null, `${QUEUE_FILE} exists but ${ENTRY_FILE} does not`, `create ${ENTRY_FILE} with ${FACTORY} wiring every operation through the queue (ADR-0002)`);
    return violations;
  }
  const sf = parse(entry);
  const fn = findFactory(sf);
  const names = queueImports(sf);
  if (!fn) {
    push(sf, sf, `\`${FACTORY}\` not found in ${ENTRY_FILE}`, `define \`${FACTORY}\` in ${ENTRY_FILE} and route each operation through the queue (ADR-0002)`);
    return violations;
  }
  if (names.size === 0 || !hasName(fn, names)) {
    push(sf, fn, `\`${FACTORY}\` does not use the queue of ${QUEUE_FILE}`,
      `import the queue from ./infrastructure/serial-queue and create it inside \`${FACTORY}\` (one queue per instance, ADR-0002)`);
    return violations;
  }
  for (const obj of returnedObjects(fn)) {
    for (const p of obj.properties) {
      const body = ts.isShorthandPropertyAssignment(p) ? p.name : ts.isPropertyAssignment(p) ? p.initializer : p;
      if (!hasName(body, names) && !queueAlias(fn, names, body)) {
        push(sf, p, `operation \`${propName(p)}\` of ${FACTORY} does not go through the queue`,
          `wrap its whole use case in the queue (\`queue.run(() => useCase(...))\`): the rule check and the write must never be split (ADR-0002)`);
      }
    }
  }
  return violations;
}

/** Locals of the factory initialised from a queue name (`const run = queue.run.bind(queue)`), used by the body. */
function queueAlias(fn, names, body) {
  const aliases = new Set();
  const visit = (n) => {
    if (ts.isVariableDeclaration(n) && ts.isIdentifier(n.name) && n.initializer && hasName(n.initializer, names)) aliases.add(n.name.text);
    ts.forEachChild(n, visit);
  };
  visit(fn);
  return aliases.size > 0 && hasName(body, aliases);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = parseArgs(process.argv.slice(2));
  if (args.explain) console.log(EXPLANATION);
  else process.exit(report(check(args.root), "check_serialized"));
}
