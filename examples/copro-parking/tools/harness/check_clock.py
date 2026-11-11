#!/usr/bin/env python3
"""INV-008 -- `domain` and `application` never read the system date (ADR-0004), checked with `ast`.

Contract: --explain, --root <path>; one line per violation
`path:line: [INV-008] message -- remediation`; exit 0 ok, 1 error, 2 warn only.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

INVARIANT_ID = "INV-008"
SEVERITY = "warn"  # starts in warn; the humans decide when it becomes error.
PACKAGE = "copro_parking"
SRC = Path("src") / PACKAGE
RINGS = ("domain", "application")
# Fully-qualified names that read the system clock (called or merely referenced).
CLOCK_READS = {
    "datetime.date.today", "datetime.datetime.now", "datetime.datetime.today",
    "datetime.datetime.utcnow", "time.time", "time.time_ns", "time.localtime",
    "time.gmtime", "time.ctime",
}

EXPLANATION = f"""\
[{INVARIANT_ID}] The system date is read nowhere in `domain` or `application` (ADR-0004), severity {SEVERITY}.
  Banned (called or referenced, through any import alias): {', '.join(sorted(CLOCK_READS))}.
  Today comes from the `Clock` port declared in `application`; `infrastructure` implements it
  (`SystemClock`), tests inject a fixed clock.
Scans {SRC}/{{{','.join(RINGS)}}}/**/*.py with `ast`; resolves `import x as y` and `from x import y as z`.
A ring or file that does not exist yet is skipped.
Limit: dynamic access (getattr, importlib, __import__) and a clock reached through a third-party
module are not seen; `infrastructure` and `tests` are free.
"""


def aliases(tree: ast.AST) -> dict[str, str]:
    """Map each local name bound by an import to its dotted origin."""
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for a in node.names:
                out[a.asname or a.name] = f"{node.module}.{a.name}"
    return out


def dotted(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return parts[::-1]
    return None


def reads(tree: ast.AST):
    """Yield (line, qualified name) for each reference to a clock-reading function."""
    names = aliases(tree)
    inner = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Attribute, ast.Name)) or id(node) in inner:
            continue  # only the outermost node of a chain
        parts = dotted(node)
        if parts and parts[0] in names:
            full = ".".join([names[parts[0]], *parts[1:]])
            if full in CLOCK_READS:
                yield node.lineno, full


def check(root: Path) -> list[str]:
    out: list[str] = []
    base = root / SRC
    if not base.is_dir():
        print(f"{SRC}: no code yet, nothing to check", file=sys.stderr)
        return out
    for ring in RINGS:
        for path in sorted((base / ring).rglob("*.py")):
            rel = path.relative_to(root).as_posix()
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
            except SyntaxError as e:
                out.append(f"{rel}:{e.lineno or 1}: [{INVARIANT_ID}] file does not parse -- fix the syntax error")
                continue
            for line, full in reads(tree):
                out.append(f"{rel}:{line}: [{INVARIANT_ID}] `{full}` reads the system date in the {ring} ring -- "
                           "take today from the `Clock` port (`clock.today()`), injected by the caller; "
                           "the adapter in `infrastructure` is the only place that reads the host clock (see ADR-0004)")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="No system date in domain or application.")
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
