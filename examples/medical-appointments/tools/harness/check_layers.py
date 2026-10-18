#!/usr/bin/env python3
"""INV-001 -- dependency rule of ADR-0001 (hexagonal architecture).

Runs the ArchUnit rules of src/test/java/**/ArchitectureTest.java through Maven
(profile `invariants`) and prints one line per violation:
    path:line: [INV-001] message -- remediation

Contract (see docs/technical/invariants.md):
  --explain      describes the rule without checking anything
  --root <path>  project root (default: current directory)
  exit 0 no violation, 1 error (or the check could not run), 2 warn violations only

It fixes nothing and never edits the rule or its severity. Needs Maven
(`mvn` on the PATH, $MVN_CMD, or a distribution under ~/.m2/wrapper/dists).
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

INV = "INV-001"
SEVERITY = "warn"  # warn | error. Changing it is a human decision recorded in invariants.md.
REMEDIATION = ("move the dependency behind a port owned by `application` and implemented in "
               "`adapters` (see INV-001 in docs/technical/invariants.md, ADR-0001)")

EXPLANATION = f"""\
[{INV}] Hexagonal dependency rule (ADR-0001), severity {SEVERITY}
  - `domain` imports nothing but java.* and itself
  - `application` depends on `domain` and the JDK only
  - nothing in `domain` or `application` imports `adapters`
Checked by ArchUnit (src/test/java/**/ArchitectureTest.java), run via Maven profile `invariants`.
Remediation: {REMEDIATION}
"""

VIOLATION_RE = re.compile(r"^(?P<what>.*?)\s*\((?P<file>[\w$]+\.java):(?P<line>\d+)\)\s*$")


def find_mvn():
    here = Path(__file__).resolve().parent
    out = subprocess.run(["bash", "-c", f'. "{here}/_maven.sh"; resolve_mvn'],
                         capture_output=True, text=True)
    return out.stdout.strip() or None


def locate(root: Path, name: str) -> str:
    for path in sorted((root / "src").rglob(name)):
        return path.relative_to(root).as_posix()
    return name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    if args.explain:
        print(EXPLANATION)
        return 0
    root = Path(args.root).resolve()
    mvn = find_mvn()
    if not mvn:
        print(f"pom.xml:1: [{INV}] Maven not found -- put `mvn` on the PATH or set MVN_CMD")
        return 1
    cmd = [mvn, "-B", "-q", "test", "-Pinvariants"]
    if os.environ.get("MVN_OFFLINE") == "1":
        cmd.insert(1, "-o")
    run = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    text = run.stdout + run.stderr
    if run.returncode == 0:
        return 0

    violations = []
    in_rule = False
    for raw in text.splitlines():
        line = raw.replace("[ERROR]", "").strip()
        if f"[{INV}]" in line and "was violated" in line:
            in_rule = True
            continue
        if in_rule:
            m = VIOLATION_RE.match(line)
            if m and not line.startswith("at "):
                what = re.sub(r"\s+in$", "", m["what"].strip())
                item = (m["file"], int(m["line"]), what)
                if item not in violations:  # the build prints each violation twice
                    violations.append(item)
            elif not line:
                in_rule = False
    if not violations:
        # The build failed for another reason: not a rule violation, never reported as a pass.
        tail = "\n".join(text.splitlines()[-15:])
        print(f"pom.xml:1: [{INV}] the check could not run (build failure) -- fix the build first:\n{tail}")
        return 1
    for file, number, what in violations:
        print(f"{locate(root, file)}:{number}: [{INV}] {what} -- {REMEDIATION}")
    return 1 if SEVERITY == "error" else 2


if __name__ == "__main__":
    sys.exit(main())
