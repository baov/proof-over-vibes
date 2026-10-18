#!/usr/bin/env python3
"""Normalises a PIT mutations.xml into the harness output (INV-006). Internal helper of run_mutation.sh."""
import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True)
ap.add_argument("--scope", required=True)
ap.add_argument("--threshold", default="")
ap.add_argument("--severity", default="warn")
a = ap.parse_args()

path = Path(a.report)
if not path.is_file():
    print(f"MUTATION -- scope: {a.scope} · tool: PIT\nno report produced: nothing to mutate in scope yet")
    sys.exit(0)

muts = ET.parse(path).getroot().findall("mutation")
# NO_COVERAGE counts as survived for the score (no test reaches it); NON_VIABLE and errors are excluded.
status = lambda m: m.get("status")
scored = [m for m in muts if status(m) in ("KILLED", "SURVIVED", "NO_COVERAGE", "TIMED_OUT", "MEMORY_ERROR", "RUN_ERROR")]
killed = [m for m in scored if status(m) in ("KILLED", "TIMED_OUT", "MEMORY_ERROR")]
if not scored:
    print(f"MUTATION -- scope: {a.scope} · tool: PIT\nno mutation generated: nothing to mutate in scope yet")
    sys.exit(0)

score = 100.0 * len(killed) / len(scored)
verdict = "no threshold set yet (baseline to be recorded in invariants.md)"
code = 0
if a.threshold:
    t = float(a.threshold)
    if score < t:
        verdict = f"below threshold {t}%"
        code = 1 if a.severity == "error" else 2
    else:
        verdict = f"OK (threshold {t}%)"
print(f"MUTATION -- scope: {a.scope} · tool: PIT")
print(f"score: {score:.1f}% ({len(killed)} killed / {len(scored)} generated)  → {verdict}")
survivors = [m for m in scored if m not in killed]
if survivors:
    print("\nSurviving mutants:")
    for m in survivors[:20]:
        src = m.findtext("sourceFile") or "?"
        line = m.findtext("lineNumber") or "0"
        cls = (m.findtext("mutatedClass") or "").rsplit(".", 1)[0].replace(".", "/")
        mut = (m.findtext("mutator") or "").rsplit(".", 1)[-1]
        desc = m.findtext("description") or ""
        print(f"  src/main/kotlin/{cls}/{src}:{line}  [{mut}]  {desc} -- no test fails: add a test stating the unprotected behavior")
sys.exit(code)
