---
role: orchestrator
status: done
reasons: []
---

# Brief: S3 Remove a space

- Type: prompt (no ticket). Acceptance criteria are those of this story in `../stories.md`. Architecture: `../architect.md`, ADR-0001..0003. Decisions: `docs/business/decisions.md` (D-1..D-18). S1 is merged: code in `src/copro_parking`, see `.plans/done/register-lots-and-spaces/s1-register-and-list/`.
- Constraints: Python 3.14, stdlib `unittest`, offline; run `bash tools/harness/run_all.sh` before handing over. Tests first.
- Sensitive zones: manager-only role check; JSON store atomic write. A diff touching them escalates to the human.
- Iteration counter: 0 / limit 5.
- Carried over: none open (S2 closed the S1 majors). Open minor: runs of more than 4300 digits in an identifier raise a raw ValueError (natural sort); do not widen scope for it.
