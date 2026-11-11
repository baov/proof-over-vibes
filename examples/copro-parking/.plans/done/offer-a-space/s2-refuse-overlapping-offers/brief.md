---
role: orchestrator
status: done
reasons: []
---

# Brief: S2 Refuse overlapping offers of the same space

- Type: prompt (no ticket). Story S2 of `../stories.md`; acceptance criteria are those of S2 there. Architecture: `../architect.md` and ADR-0001..0004. Decisions: `docs/business/decisions.md` (D-45..D-62).
- Constraints: Python 3.14, stdlib `unittest`, offline; run `bash tools/harness/run_all.sh` before handing over.
- Sensitive zones (invariants.md): the role checks, the JSON stores' write paths, and the offers write path. A diff touching them escalates to the human.
- Iteration counter: 0 / limit 5.
- Carried over (open majors of the review of S1, `reviews/06-f2-s1-offer-a-space.md`):
  - M2: S1 lets overlapping offers of one space be stored. The load-time check that S2 adds would make such a file `OffersUnreadable` and stop the feature. Plan its fix in S2: ask the human whether a file already holding an overlapping pair is rejected on load or tolerated.
  - M1: orphan offers (space gone from the register) reappear under another owner when the number is registered again or the space is renumbered. S4 closes it (removal and renumbering blocked); defer it to S4, say so in the plan.
