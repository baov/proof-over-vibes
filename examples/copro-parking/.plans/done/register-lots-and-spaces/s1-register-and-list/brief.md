---
role: orchestrator
status: done
reasons: []
---

# Brief: S1 Register lots and spaces and list them

- Type: prompt (no ticket). Story S1 of `../stories.md`; acceptance criteria are those of S1 there. Architecture: `../architect.md` and ADR-0001..0003. Decisions: `docs/business/decisions.md`.
- Constraints: Python 3.14, stdlib `unittest`, offline; run `bash tools/harness/run_all.sh` before handing over.
- Sensitive zones (invariants.md): manager-only role check; JSON store atomic write. A diff touching them escalates to the human.
- Iteration counter: 0 / limit 5.
- Carried over: none.
