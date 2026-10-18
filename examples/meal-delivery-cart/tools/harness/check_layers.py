#!/usr/bin/env python3
"""INV-001 to INV-004 -- the ArchUnit rules of ADR-0001 and ADR-0002.

Runs src/test/kotlin/**/ArchitectureTest.kt through Maven (profile `invariants`) and prints one line per violation:
    path:line: [INV-NNN] message -- remediation

  INV-001 dependency rule (ADR-0001)      INV-002 single rounding point (ADR-0001)
  INV-003 no Double/Float/BigDecimal (ADR-0002)      INV-004 purity of the core (architect note)

Contract (see docs/technical/invariants.md):
  --explain      describes the rules without checking anything
  --root <path>  project root (default: current directory)
  exit 0 no violation, 1 error (or the check could not run), 2 warn violations only

It fixes nothing and never edits a rule or its severity. Needs Maven (`mvn` on the PATH, $MVN_CMD, or a
distribution under ~/.m2/wrapper/dists). Set MVN_OFFLINE=1 to run Maven with -o.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# warn | error, per invariant. Changing one is a human decision recorded in invariants.md, in the same commit.
SEVERITY = {"INV-001": "warn", "INV-002": "warn", "INV-003": "warn", "INV-004": "warn"}

EXPLANATION = """\
[INV-001] Hexagonal dependency rule (ADR-0001), severity {INV-001}
  - `domain` imports only the Kotlin and JDK standard library and itself
  - `application` depends on `domain` and the standard library only
  - nothing in `domain` or `application` imports `adapters`
[INV-002] Single rounding point (ADR-0001), severity {INV-002}
  - no rounding API (Math.round/floor/ceil/floorDiv, kotlin.math rounding, BigDecimal.setScale, RoundingMode)
    called or used outside `domain.money`. Known limit: it cannot tell that rounding is done by hand with integer
    arithmetic, nor that `domain.money` has more than one rounding function.
[INV-003] No floating point for money (ADR-0002), severity {INV-003}
  - no Double, Float or BigDecimal in a field, signature or call of `domain` or `application`. Known limit: a
    local variable that is never passed to a call or a signature is not seen by bytecode analysis.
[INV-004] Purity of the core (architect note), severity {INV-004}
  - `domain` and `application` use no java.time, java.io, java.nio, java.net, java.util.concurrent, kotlin.random,
    kotlin.io, kotlin.time, System, Thread, Runtime, Random, Date, Calendar
Checked by ArchUnit (src/test/kotlin/**/ArchitectureTest.kt), run via Maven profile `invariants`.
"""

REMEDIATION = {
    "INV-001": "move the dependency behind a port owned by `application` and implemented in an adapter (see INV-001, ADR-0001)",
    "INV-002": "call the single rounding function of `domain.money` (see INV-002, ADR-0001)",
    "INV-003": "hold amounts as `Money` (Long minor units) and rates as `Percentage` (see INV-003, ADR-0002)",
    "INV-004": "pass the value in as an argument, or define a port in `application` (see INV-004)",
}

# "what (File.kt:12)" -- the location may come last or be followed by more text.
LOCATION_RE = re.compile(r"\((?P<file>[\w$]+\.kt):(?P<line>\d+)\)")
RULE_RE = re.compile(r"\[(?P<inv>INV-\d{3})\].*was violated")


def find_mvn():
    here = Path(__file__).resolve().parent
    out = subprocess.run(["bash", "-c", f'. "{here}/_maven.sh"; resolve_mvn'], capture_output=True, text=True)
    return out.stdout.strip() or None


def locate(root: Path, name: str) -> str:
    for path in sorted((root / "src").rglob(name)):
        return path.relative_to(root).as_posix()
    return name


def parse(text: str):
    violations = []
    inv = None
    for raw in text.splitlines():
        line = raw.replace("[ERROR]", "").strip()
        m = RULE_RE.search(line)
        if m:
            inv = m["inv"]
            continue
        if inv is None:
            continue
        if not line:
            inv = None
            continue
        loc = LOCATION_RE.search(line)
        if loc and not line.startswith("at "):
            what = LOCATION_RE.sub("", line).strip()
            what = re.sub(r"\s+in$", "", what)
            item = (inv, loc["file"], int(loc["line"]), what)
            if item not in violations:  # the build prints each violation twice
                violations.append(item)
    return violations


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    if args.explain:
        print(EXPLANATION.format(**SEVERITY))
        return 0
    root = Path(args.root).resolve()
    mvn = find_mvn()
    if not mvn:
        print("pom.xml:1: [INV-001] Maven not found -- put `mvn` on the PATH or set MVN_CMD")
        return 1
    cmd = [mvn, "-B", "-q", "test", "-Pinvariants"]
    if os.environ.get("MVN_OFFLINE") == "1":
        cmd.insert(1, "-o")
    run = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    text = run.stdout + run.stderr
    if run.returncode == 0:
        return 0
    violations = parse(text)
    if not violations:
        # The build failed for another reason: not a rule violation, never reported as a pass.
        tail = "\n".join(text.splitlines()[-15:])
        print(f"pom.xml:1: [INV-001] the check could not run (build failure) -- fix the build first:\n{tail}")
        return 1
    worst = 2
    for inv, file, number, what in violations:
        print(f"{locate(root, file)}:{number}: [{inv}] {what} -- {REMEDIATION[inv]}")
        if SEVERITY.get(inv) == "error":
            worst = 1
    return worst


if __name__ == "__main__":
    sys.exit(main())
