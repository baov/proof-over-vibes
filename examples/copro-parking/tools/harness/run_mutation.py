#!/usr/bin/env python3
"""INV-007 -- stdlib-only mutation testing (manual-grade tool, see --explain for its limits).

Contract: --explain, --root <path>; surviving mutants as
`path:line: [INV-007] mutant survived: <change> -- <remediation>`;
exit 0 ok / no threshold set, 2 score below --threshold (warn), 1 baseline suite not green.
"""
from __future__ import annotations

import argparse
import ast
import copy
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCOPES = {  # critical = where a silent bug costs most (rules, role check, atomic write)
    "critical": ["src/copro_parking/domain", "src/copro_parking/application",
                 "src/copro_parking/infrastructure"],
    "full": ["src"],
}
TEST_CMD = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
CMP = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.GtE, ast.GtE: ast.Lt,
       ast.Gt: ast.LtE, ast.LtE: ast.Gt, ast.In: ast.NotIn, ast.NotIn: ast.In,
       ast.Is: ast.IsNot, ast.IsNot: ast.Is}
ARITH = {ast.Add: ast.Sub, ast.Sub: ast.Add}

EXPLANATION = """\
[INV-007] Mutation testing, standard library only. For each source file in scope it applies ONE
small change at a time (comparison flipped, and<->or, `not` dropped, True<->False, +<->-,
integer constant +1, `return x` -> `return None`, `if c` -> `if not c`), runs the unittest suite
on a temporary copy, and reports mutants the suite did not notice (survivors).
  --scope critical|diff|full   critical = domain + application + infrastructure (default);
                               diff = changed files vs --base (default HEAD) among those; full = all of src/
  --threshold N                warn (exit 2) when the score is below N percent; none by default
What it can see: assertions too weak to notice a flipped condition, a skipped role check,
a dropped refusal, a persisted-or-not difference the tests never compare.
What it cannot see (honest limits):
  - equivalent mutants (no behavior change) count as survivors: read them, do not chase 100%;
  - removed statements, changed strings/messages/exception types, swapped arguments, wrong dict keys;
  - concurrency or crash-in-the-middle behavior (e.g. a missing os.replace atomicity) unless a test fakes the crash;
  - code that no test imports shows as all-survivors, which is a coverage signal, not a score;
  - the mutant source is re-printed by ast.unparse (comments and layout are not mutated).
Cost: one full unittest run per mutant, so keep the suite fast. A timeout counts as killed.
"""


class Mutator(ast.NodeTransformer):
    """Applies exactly the `target`-th applicable mutation (counted in visit order)."""

    def __init__(self, target: int):
        self.target, self.count, self.desc, self.line = target, -1, "", 0

    def _hit(self, node, desc) -> bool:
        self.count += 1
        if self.count == self.target:
            self.desc, self.line = desc, getattr(node, "lineno", 0)
            return True
        return False

    def visit_Compare(self, node):
        self.generic_visit(node)
        for i, op in enumerate(node.ops):
            if type(op) in CMP and self._hit(node, f"{type(op).__name__} -> {CMP[type(op)].__name__}"):
                node.ops[i] = CMP[type(op)]()
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        new = ast.Or if isinstance(node.op, ast.And) else ast.And
        if self._hit(node, f"{type(node.op).__name__} -> {new.__name__}"):
            node.op = new()
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Not) and self._hit(node, "`not x` -> `x`"):
            return node.operand
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if type(node.op) in ARITH and self._hit(node, f"{type(node.op).__name__} -> {ARITH[type(node.op)].__name__}"):
            node.op = ARITH[type(node.op)]()
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            if self._hit(node, f"{node.value} -> {not node.value}"):
                return ast.copy_location(ast.Constant(not node.value), node)
        elif isinstance(node.value, int) and self._hit(node, f"{node.value} -> {node.value + 1}"):
            return ast.copy_location(ast.Constant(node.value + 1), node)
        return node

    def visit_Return(self, node):
        self.generic_visit(node)
        if node.value is not None and not (isinstance(node.value, ast.Constant) and node.value.value is None) \
                and self._hit(node, "`return x` -> `return None`"):
            node.value = ast.Constant(None)
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if self._hit(node, "`if c` -> `if not c`"):
            node.test = ast.UnaryOp(ast.Not(), node.test)
        return node


def mutants_of(source: str):
    """Yield (index, line, description, mutated source)."""
    tree = ast.parse(source)
    total = 0
    probe = Mutator(-1)
    probe.visit(copy.deepcopy(tree))
    total = probe.count + 1
    for i in range(total):
        m = Mutator(i)
        mutated = m.visit(copy.deepcopy(tree))
        ast.fix_missing_locations(mutated)
        yield i, m.line, m.desc, ast.unparse(mutated)


def run_suite(cwd: Path, timeout: float):
    env = dict(os.environ, PYTHONPATH=str(cwd / "src"), PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run(TEST_CMD, cwd=cwd, env=env, capture_output=True, timeout=timeout)
        return r.returncode
    except subprocess.TimeoutExpired:
        return -1  # counts as killed


def select_files(root: Path, scope: str, base: str) -> list[Path]:
    dirs = SCOPES["full" if scope == "full" else "critical"]
    files = sorted(p for d in dirs if (root / d).is_dir() for p in (root / d).rglob("*.py")
                   if p.name != "__init__.py")
    if scope == "diff":
        r = subprocess.run(["git", "diff", "--name-only", base, "--", "src"], cwd=root,
                           capture_output=True, text=True)
        changed = {(root / n.strip()).resolve() for n in r.stdout.splitlines() if n.strip()}
        files = [f for f in files if f.resolve() in changed]
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Stdlib mutation testing.")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--root", default=".")
    ap.add_argument("--scope", choices=["critical", "diff", "full"], default="critical")
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--threshold", type=float, default=None)
    args = ap.parse_args(argv)
    if args.explain:
        print(EXPLANATION)
        return 0
    root = Path(args.root).resolve()
    files = select_files(root, args.scope, args.base)
    if not files:
        print(f"no source file in scope '{args.scope}': nothing to mutate", file=sys.stderr)
        return 0
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "p"
        shutil.copytree(root, work, ignore=shutil.ignore_patterns(".git", "__pycache__", ".plans"))
        t0 = time.time()
        if run_suite(work, 600) != 0:
            print("baseline: the unittest suite is not green (or finds no test) -- "
                  "mutation testing needs a green suite first", file=sys.stderr)
            return 1
        timeout = max(5.0, (time.time() - t0) * 5)
        killed = survived = 0
        for f in files:
            rel = f.relative_to(root).as_posix()
            target = work / rel
            original = f.read_text(encoding="utf-8")
            try:
                for _, line, desc, src in mutants_of(original):
                    target.write_text(src, encoding="utf-8")
                    if run_suite(work, timeout) == 0:
                        survived += 1
                        print(f"{rel}:{line}: [INV-007] mutant survived: {desc} -- find the "
                              f"behavior this change breaks and add a test asserting it; if no "
                              f"behavior is affected (equivalent mutant), say so in review")
                    else:
                        killed += 1
            finally:
                target.write_text(original, encoding="utf-8")
    total = killed + survived
    score = 100.0 * killed / total if total else 100.0
    print(f"\nmutation score {score:.1f}% ({killed} killed / {total} mutants, "
          f"scope {args.scope}, {len(files)} files)", file=sys.stderr)
    if args.threshold is not None and score < args.threshold:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
