---
role: orchestrator
status: done
reasons: []
---

# Brief: S1 Offer a space and list the open offers

- Type: prompt (no ticket). Story S1 of `../stories.md`; acceptance criteria are those of S1 there. Architecture: `../architect.md` and ADR-0001..0004. Decisions: `docs/business/decisions.md` (D-45..D-58).
- Constraints: Python 3.14, stdlib `unittest`, offline; run `bash tools/harness/run_all.sh` before handing over.
- Sensitive zones (invariants.md): manager-only role check; JSON store atomic write; rules store; and, new for offers, the owner role check in `offer_use_cases.py` and the offers write path. A diff touching them escalates to the human.
- Iteration counter: 0 / limit 5.
- Carried over: none.
