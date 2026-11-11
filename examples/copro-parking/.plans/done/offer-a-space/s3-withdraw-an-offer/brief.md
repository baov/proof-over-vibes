---
role: orchestrator
status: done
reasons: []
---

# Brief: S3 Withdraw an offer

- Type: prompt (no ticket). Story S3 of `../stories.md`; acceptance criteria are those of S3 there. Architecture: `../architect.md` (withdraw_offer, WithdrawRequest) and ADR-0001..0004. Decisions: `docs/business/decisions.md` (D-45..D-64).
- Constraints: Python 3.14, stdlib `unittest`, offline; run `bash tools/harness/run_all.sh` before handing over.
- Sensitive zones: the owner role check and the offers write path. A diff touching them escalates to the human.
- Iteration counter: 0 / limit 5.
- Carried over (open majors of the reviews of S1 and S2):
  - M1: orphan offers (space gone from the register) reappear under another owner, or block a re-registered number. S4 closes it; defer to S4 and say so.
  - M2 of review 07: the wording of the overlap refusal is decided by no document. Add one line to `docs/business/decisions.md` (the Product Owner will do it; the planner only notes it) saying consumers rely on `offer_number`, not on the sentence.
  - Minor worth taking here: pin the tie order of a tolerated stored overlapping pair (review 07 m1), since a withdrawal is what can repair such a pair.
