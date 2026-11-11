---
role: orchestrator
status: done
reasons: []
---

# Brief: owner offers a space (F2.1)

- Type: prompt (no ticket)
- Objective: F2.1 "Owner offers a space for a period" (backlog item 2, picked by the human). First step: the Product Manager writes its PRD, `docs/product/prd/offer-a-space.md`. Then the usual route: product-owner, architect, each story: planner, developer, reviewer.
- Acceptance criteria: the numbered requirements of that PRD, once it exists.
- Constraints (the human's): Python 3.14; stdlib `unittest`; no dependency, offline; project language: English.
- Project state: F1.2 register and E5 S1 (duration-bounds rules) are built. The rental check of F1.2 requirement 7 is a port that always answers "no rental"; an offer must give it real content or leave it, and the PRD says which.
- Iteration counter: 0 / limit 5.
- Carried over: none (E5 S1 review 05 had two minors, no major).
