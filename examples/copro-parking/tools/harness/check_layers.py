#!/usr/bin/env python3
"""INV-001 -- ADR-0001 dependency rule, checked on `import` statements (stdlib `ast`).

Contract: --explain, --root <path>; one line per violation
`path:line: [INV-001] message -- remediation`; exit 0 ok, 1 error, 2 warn only.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

INVARIANT_ID = "INV-001"
SEVERITY = "warn"  # ADR-0001 rule starts in warn; the humans decide when it becomes error.
PACKAGE = "copro_parking"
SRC = Path("src") / PACKAGE
RINGS = ("domain", "application", "infrastructure")
# Stdlib modules that perform I/O or touch the environment: banned in `domain`.
IO_MODULES = {
    "json", "os", "pathlib", "sqlite3", "io", "shutil", "tempfile", "socket", "subprocess",
    "urllib", "http", "sys", "logging", "glob", "fnmatch", "pickle", "shelve", "csv",
    "ssl", "smtplib", "sched", "threading", "multiprocessing", "asyncio", "builtins",
}
STDLIB = set(sys.stdlib_module_names)

EXPLANATION = f"""\
[{INVARIANT_ID}] Dependency rule of ADR-0001 (clean architecture), severity {SEVERITY}.
  domain          imports only the standard library, no I/O module ({', '.join(sorted(IO_MODULES))}),
                  and nothing from application or infrastructure.
  application     imports domain and the standard library; never infrastructure.
  infrastructure  may import application and domain.
  tests           may import any ring (not scanned).
Scans every `import` / `from ... import` (also inside functions) of {SRC}/<ring>/**/*.py with `ast`.
Limit: dynamic imports (importlib, __import__) are not seen.
"""


def ring_of(path: Path, root: Path) -> str | None:
    parts = path.relative_to(root / SRC).parts
    return parts[0] if parts and parts[0] in RINGS else None


def imported_modules(tree: ast.AST, package_parts: list[str]):
    """Yield (line, absolute dotted module) for each import; relative ones are resolved."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package_parts[: len(package_parts) - (node.level - 1)]
                mod = ".".join(base + ([node.module] if node.module else []))
            else:
                mod = node.module or ""
            yield node.lineno, mod
            # `from copro_parking import infrastructure` imports a ring by name.
            if mod == PACKAGE:
                for alias in node.names:
                    yield node.lineno, f"{PACKAGE}.{alias.name}"


def judge(ring: str, module: str) -> tuple[str, str] | None:
    top = module.split(".")[0]
    if top == PACKAGE:
        target = module.split(".")[1] if "." in module else None
        if ring == "domain" and target in ("application", "infrastructure"):
            return (f"`{module}` imported in the domain ring",
                    "invert the dependency: define the need as a port in `application` "
                    "(abstract interface) and implement it in `infrastructure`")
        if ring == "application" and target == "infrastructure":
            return (f"`{module}` imported in the application ring",
                    "depend on a port declared in `application` instead; the adapter is "
                    "wired in `infrastructure`")
        return None
    if ring == "domain" and top in IO_MODULES:
        return (f"I/O module `{module}` imported in the domain ring",
                "move the I/O to an adapter in `infrastructure` behind a port declared in "
                "`application`; keep the domain pure")
    if ring in ("domain", "application") and top not in STDLIB:
        return (f"non-standard-library module `{module}` imported in the {ring} ring",
                "this project allows the standard library only (no dependency); "
                "remove the import")
    return None


def check(root: Path) -> list[str]:
    out: list[str] = []
    base = root / SRC
    if not base.is_dir():
        print(f"{SRC}: no code yet, nothing to check", file=sys.stderr)
        return out
    for path in sorted(base.rglob("*.py")):
        ring = ring_of(path, root)
        if ring is None:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as e:
            out.append(f"{rel}:{e.lineno or 1}: [{INVARIANT_ID}] file does not parse -- fix the syntax error")
            continue
        pkg = list(path.relative_to(root / "src").with_suffix("").parts)
        pkg = pkg[:-1]  # package that contains the file (same for __init__.py)
        for line, module in imported_modules(tree, pkg):
            verdict = judge(ring, module)
            if verdict:
                out.append(f"{rel}:{line}: [{INVARIANT_ID}] {verdict[0]} -- {verdict[1]} (see ADR-0001)")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ADR-0001 dependency rule.")
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
