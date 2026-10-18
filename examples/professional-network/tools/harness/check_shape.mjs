#!/usr/bin/env node
// INV-005..INV-008: shape thresholds (function size, complexity, nesting, parameters).
import { pathToFileURL } from "node:url";
import ts from "typescript";
import { lineOf, parse, parseArgs, rel, report, sourceFiles } from "./lib.mjs";

const SEVERITY = "warn";
const LIMITS = { lines: 40, complexity: 10, nesting: 4, params: 5 };

const EXPLANATION = `Shape thresholds on every function of src/ (tests excluded). Tangled code slows agents down and widens their diffs.
  [INV-005] at most ${LIMITS.lines} lines per function
  [INV-006] cyclomatic complexity at most ${LIMITS.complexity} (1 + if, loops, case, catch, ?:, &&, ||, ??)
  [INV-007] nesting depth at most ${LIMITS.nesting} (if/loops/switch/try blocks inside one function)
  [INV-008] at most ${LIMITS.params} parameters
Nested functions are measured on their own. Severity: ${SEVERITY}. Details: docs/technical/invariants.md`;

const isFunction = (n) =>
  ts.isFunctionDeclaration(n) || ts.isFunctionExpression(n) || ts.isArrowFunction(n) || ts.isMethodDeclaration(n) ||
  ts.isConstructorDeclaration(n) || ts.isGetAccessor(n) || ts.isSetAccessor(n);

const NESTING = (n) =>
  ts.isIfStatement(n) || ts.isForStatement(n) || ts.isForInStatement(n) || ts.isForOfStatement(n) ||
  ts.isWhileStatement(n) || ts.isDoStatement(n) || ts.isSwitchStatement(n) || ts.isTryStatement(n);

function complexityOf(fn) {
  let count = 1;
  const visit = (n) => {
    if (n !== fn && isFunction(n)) return;
    if (ts.isIfStatement(n) || ts.isForStatement(n) || ts.isForInStatement(n) || ts.isForOfStatement(n) ||
        ts.isWhileStatement(n) || ts.isDoStatement(n) || ts.isCaseClause(n) || ts.isCatchClause(n) || ts.isConditionalExpression(n)) count += 1;
    if (ts.isBinaryExpression(n) && [ts.SyntaxKind.AmpersandAmpersandToken, ts.SyntaxKind.BarBarToken, ts.SyntaxKind.QuestionQuestionToken].includes(n.operatorToken.kind)) count += 1;
    ts.forEachChild(n, visit);
  };
  visit(fn);
  return count;
}

function nestingOf(fn) {
  let max = 0;
  const visit = (n, depth) => {
    if (n !== fn && isFunction(n)) return;
    // `else if` continues the same level
    const continuesElse = n.parent && ts.isIfStatement(n.parent) && n.parent.elseStatement === n && ts.isIfStatement(n);
    const next = NESTING(n) && !continuesElse ? depth + 1 : depth;
    max = Math.max(max, next);
    ts.forEachChild(n, (c) => visit(c, next));
  };
  visit(fn, 0);
  return max;
}

function nameOf(fn, sf) {
  if (fn.name) return fn.name.getText(sf);
  const p = fn.parent;
  if (p && ts.isVariableDeclaration(p)) return p.name.getText(sf);
  if (p && ts.isPropertyAssignment(p)) return p.name.getText(sf);
  return "<anonymous>";
}

export function check(root) {
  const violations = [];
  for (const file of sourceFiles(root)) {
    const sf = parse(file);
    const visit = (n) => {
      if (isFunction(n) && n.body) {
        const line = lineOf(sf, n);
        const push = (id, message, remediation) => violations.push({ file: rel(root, file), line, id, message, remediation, severity: SEVERITY });
        const name = nameOf(n, sf);
        const lines = sf.getLineAndCharacterOfPosition(n.getEnd()).line + 1 - line + 1;
        if (lines > LIMITS.lines) push("INV-005", `\`${name}\` is ${lines} lines (max ${LIMITS.lines})`, "extract named steps into small functions, one intention each");
        const cx = complexityOf(n);
        if (cx > LIMITS.complexity) push("INV-006", `\`${name}\` has complexity ${cx} (max ${LIMITS.complexity})`, "split the branches into separate functions, or replace conditionals by a lookup or a polymorphic rule");
        const depth = nestingOf(n);
        if (depth > LIMITS.nesting) push("INV-007", `\`${name}\` nests ${depth} levels deep (max ${LIMITS.nesting})`, "return early (guard clauses) or extract the inner block into a function");
        const params = n.parameters.length;
        if (params > LIMITS.params) push("INV-008", `\`${name}\` takes ${params} parameters (max ${LIMITS.params})`, "group related parameters into one object or value object");
      }
      ts.forEachChild(n, visit);
    };
    visit(sf);
  }
  return violations;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = parseArgs(process.argv.slice(2));
  if (args.explain) console.log(EXPLANATION);
  else process.exit(report(check(args.root), "check_shape"));
}
