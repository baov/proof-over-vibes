---
role: orchestrator
status: done
reasons: []
---

# Brief: S2 Correct a lot's owner and a space's number

- Type: prompt (no ticket). Acceptance criteria are those of this story in `../stories.md`. Architecture: `../architect.md`, ADR-0001..0003. Decisions: `docs/business/decisions.md` (D-1..D-18). S1 is merged: code in `src/copro_parking`, see `.plans/done/register-lots-and-spaces/s1-register-and-list/`.
- Constraints: Python 3.14, stdlib `unittest`, offline; run `bash tools/harness/run_all.sh` before handing over. Tests first.
- Sensitive zones: manager-only role check; JSON store atomic write. A diff touching them escalates to the human.
- Iteration counter: 1 / limit 5 (the human asked to fix review major M1 before accepting).
- Carried over (open majors of S1): a corrupt or malformed store file raises a raw error, no decision says what the manager sees; the sort is plain case-folded text so "p10" lists before "p2" (D-13 does not say how to sort).
