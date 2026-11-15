"""A scripted run, written file by file, so the floor can be watched without a real run."""

from __future__ import annotations

import os
import time
from pathlib import Path

RUN = ".plans/in-progress/demo-feature"
STORY = f"{RUN}/story-1"
# Recent, so the page shows "just now" rather than a date in 1970; steps are 10 s apart.
BASE_MTIME = time.time() - 30


def _report(role: str, status: str = "done", verdict: str | None = None, reasons: str = "[]", body: str = "") -> str:
    lines = ["---", f"role: {role}", f"status: {status}"]
    if verdict:
        lines += [f"verdict: {verdict}", f"reasons: {reasons}", "severity: major" if verdict == "NO-GO" else "severity: minor"]
    return "\n".join(lines + ["---", body or f"## {role}\n\nDemo report written by the {role}.\n"]) + "\n"


def _qa(proof: str, reasons: str = "[]", body: str = "") -> str:
    lines = ["---", "role: qa", "status: done", f"proof: {proof}", f"reasons: {reasons}", "---"]
    return "\n".join(lines + [body or "## Acceptance proof\n\nEvery criterion PROVEN in the running app.\n"]) + "\n"


def _brief(iteration: int) -> str:
    return (
        "# Brief\n\n**Objective:** let a customer empty their cart in one click.\n\n"
        "## Acceptance criteria\n\n- The cart shows zero items afterwards.\n- A confirmation is asked first.\n\n"
        f"Iteration counter: {iteration}\nIteration limit: 5\n"
    )


EXAMPLE_MAP = """---
role: qa
status: done
reasons: []
---
# Example map - empty the cart

## Story 1 - Empty the cart in one click

### B1 The cart shows zero items afterwards - source: brief
- E1 Given a cart with 2 mugs, when the customer empties it and confirms, then the badge reads "0 items" - source: brief
- E2 Given an empty cart, when the customer empties it, then nothing changes and no error shows - source: proposed

### B2 A confirmation is asked first - source: D-2
- E3 Given a cart with 1 mug, when the customer clicks "Empty", then a confirmation is asked before anything is removed - source: D-2
- E4 Given the confirmation is open, when the customer cancels, then the cart still holds its mug - source: D-2

### Questions
None open: D-1 and D-2 settled the two points this map raised.
"""

DECISIONS = """# Decision log

Append only. `answered` = a person read and answered. `answered-by-delegate` = a role's recommendation, relayed, nobody read it.

### D-1 Which currency do the cart totals use
- status: answered-by-delegate
- answer: the cart's currency
- source: docs/business/glossary.md
- request: demo-feature

### D-2 Ask for a confirmation before emptying the cart
- status: answered-by-delegate
- answer: yes, one confirmation
- source: none
- request: demo-feature

### D-3 How are the totals rounded
- status: human-needed
- answer: pending
- source: none
- recommended: round half up, to the cent
- request: demo-feature
"""

FRAMING = """# Brief framing: empty the cart

## TL;DR

The brief asks for a one-click cart reset. Two points are open: whether a confirmation is asked, and how totals are rounded. Both are in the decision log.

## Flow

```mermaid
flowchart LR
  Customer --> Cart --> Confirmation --> EmptyCart
```

## Open questions

1. Is a confirmation required before emptying?
2. How are the totals rounded?
"""

# One entry per step: the files written, in order. A half-written report (an
# unclosed front-matter block) shows the role as working.
DEMO_STEPS: list[dict[str, str]] = [
    {f"{RUN}/brief.md": _brief(0), "docs/product/framing.md": FRAMING},
    {f"{RUN}/stories.md": "---\nrole: product-owner\n"},
    {f"{RUN}/stories.md": _report("product-owner"), "docs/business/decisions.md": DECISIONS},
    {f"{RUN}/architect.md": _report("architect")},
    {f"{RUN}/example-map.md": EXAMPLE_MAP},
    {f"{STORY}/brief.md": _brief(0), f"{STORY}/plan.md": _report("planner")},
    {f"{STORY}/developer-0.md": _report("developer")},
    {f"{STORY}/brief.md": _brief(1), f"{STORY}/qa-0.md": _qa(
        "NO-GO", reasons="[C2 DISPROVEN: the cart empties without asking for confirmation]",
        body="## Acceptance proof\n\n- **C1** The cart shows zero items afterwards: PROVEN, `qa-0/01-c1-after-click.png`\n- **C2** A confirmation is asked first: DISPROVEN, `qa-0/02-c2-after-click.png`. Expected a confirmation; observed the cart emptied at once.\n",
    ), f"{STORY}/qa-0/01-c1-after-click.png": "demo evidence\n", f"{STORY}/qa-0/02-c2-after-click.png": "demo evidence\n"},
    {f"{STORY}/developer-1.md": _report("developer")},
    {f"{STORY}/qa-1.md": _qa("GO")},
    {f"{STORY}/brief.md": _brief(2), ".reviews/demo-1.md": _report(
        "reviewer", verdict="NO-GO", reasons="[no test for an already empty cart]",
        body="## Findings\n\n- **major** No test covers an already empty cart.\n\n```\nclear_cart(cart)  # no guard\n```\n",
    )},
    {f"{STORY}/developer-2.md": _report("developer")},
    {f"{STORY}/qa-2.md": _qa("GO")},
    {".reviews/demo-2.md": _report("reviewer", verdict="GO", body="## Findings\n\nNone blocking. The major point of round 1 is fixed.\n")},
]


def apply_step(root: Path, index: int) -> None:
    """Write the files of step `index`, with modification times that grow with the step."""
    for offset, (relpath, text) in enumerate(DEMO_STEPS[index].items()):
        path = Path(root) / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        mtime = BASE_MTIME + index * 10 + offset
        os.utime(path, (mtime, mtime))


def run_demo(root: Path, step_seconds: float = 6.0, sleep=time.sleep) -> None:
    for index in range(len(DEMO_STEPS)):
        apply_step(root, index)
        sleep(step_seconds)
