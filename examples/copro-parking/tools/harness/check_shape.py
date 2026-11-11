#!/usr/bin/env python3
"""INV-003..INV-006 -- shape thresholds on functions of src/ (stdlib `ast`).

Contract: --explain, --root <path>; `path:line: [INV-NNN] message -- remediation`;
exit 0 ok, 1 error, 2 warn only.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

SEVERITY = "warn"
MAX_LINES, MAX_COMPLEXITY, MAX_DEPTH, MAX_PARAMS = 40, 10, 4, 5
BRANCH = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp,
          ast.Assert, ast.comprehension, ast.match_case)
NEST = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)
FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)

EXPLANATION = f"""\
Shape thresholds on every function under src/ (severity {SEVERITY}):
  INV-003 lines per function    <= {MAX_LINES}
  INV-004 cyclomatic complexity <= {MAX_COMPLEXITY}  (1 + if/for/while/except/ternary/assert/comprehension/case + each and/or operand)
  INV-005 nesting depth         <= {MAX_DEPTH}  (if/for/while/try/with/match, per function)
  INV-006 parameters            <= {MAX_PARAMS}  (self and cls excluded)
Why: tangled code costs agents repeated passes and wide diffs. Nested functions are measured on their own.
"""


def own_nodes(fn):
    """Nodes of fn's body, not descending into nested functions or classes."""
    stack = list(fn.body)
    while stack:
        n = stack.pop()
        yield n
        for c in ast.iter_child_nodes(n):
            if not isinstance(c, FUNC + (ast.ClassDef, ast.Lambda)):
                stack.append(c)


def complexity(fn) -> int:
    c = 1
    for n in own_nodes(fn):
        if isinstance(n, BRANCH):
            c += 1
        elif isinstance(n, ast.BoolOp):
            c += len(n.values) - 1
    return c


def depth(node, level=0) -> int:
    best = level
    for c in ast.iter_child_nodes(node):
        if isinstance(c, FUNC + (ast.ClassDef, ast.Lambda)):
            continue
        best = max(best, depth(c, level + 1 if isinstance(c, NEST) else level))
    return best


def params(fn) -> int:
    a = fn.args
    names = [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs]
    n = len(names) + (a.vararg is not None) + (a.kwarg is not None)
    return n - (1 if names and names[0] in ("self", "cls") else 0)


def check(root: Path) -> list[str]:
    out: list[str] = []
    src = root / "src"
    if not src.is_dir():
        print("src/: no code yet, nothing to check", file=sys.stderr)
        return out
    for path in sorted(src.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as e:
            out.append(f"{rel}:{e.lineno or 1}: [INV-003] file does not parse -- fix the syntax error")
            continue
        for fn in (n for n in ast.walk(tree) if isinstance(n, FUNC)):
            lines = fn.end_lineno - fn.lineno + 1
            checks = (
                ("INV-003", lines, MAX_LINES, f"{lines} lines",
                 "extract cohesive steps into named helper functions"),
                ("INV-004", complexity(fn), MAX_COMPLEXITY, f"complexity {complexity(fn)}",
                 "split the branches into smaller functions or use early returns / a lookup table"),
                ("INV-005", depth(fn), MAX_DEPTH, f"nesting depth {depth(fn)}",
                 "flatten with guard clauses (early return) or extract the inner block"),
                ("INV-006", params(fn), MAX_PARAMS, f"{params(fn)} parameters",
                 "group related parameters into a value object or dataclass"),
            )
            for inv, value, limit, what, fix in checks:
                if value > limit:
                    out.append(f"{rel}:{fn.lineno}: [{inv}] `{fn.name}` has {what} (limit {limit}) -- {fix}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Shape thresholds.")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)
    if args.explain:
        print(EXPLANATION)
        return 0
    violations = check(Path(args.root).resolve())
    for v in violations:
        print(v)
    if not violations:
        return 0
    return 1 if SEVERITY == "error" else 2


if __name__ == "__main__":
    sys.exit(main())
