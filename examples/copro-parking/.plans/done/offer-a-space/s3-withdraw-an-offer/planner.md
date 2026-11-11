---
role: planner
status: done
reasons: []
---

# Planner: S3 Withdraw an offer

Answered by delegate, recorded as D-65 (Q1 A), D-66 (Q2 A) and D-67 (Q3 A); `plan.md` is final. Three behaviors a consumer sees were decided by no document. Not a question (decided in the plan): the owner is the lot's current owner (D-54, D-56); withdrawing twice, an ended offer and a stranger's number are "unknown offer" (D-55, D-58); the offer is deleted from the file, `next_number` is never reused, expired offers stay (ADR-0004); a non-owner role is refused as not allowed, first (S3 AC4).

## Q1. Which refusal wins when several fit, and what of an offer whose space left the register?
A non-owner names an offer that is withdrawn, ended, never existed, or whose space is gone from the register (the listing skips it, D-62; its owner cannot be known).
- A. Role, then invalid input, then unknown offer (not open, or its space left the register), then not the owner. **Recommended.** Mirrors the offer order (unknown space before not the owner, PRD 15); a closed offer looks the same to everyone; no withdrawal without a name check.
- B. As A, but an offer whose space left the register can be withdrawn by any owner (no name to compare). Cleans orphans before S4, but opens a withdrawal with no ownership check, in a sensitive zone.
- C. Not the owner before unknown offer whenever the offer is still stored (ended, orphan). Tells a stranger which numbers exist in the file, and contradicts D-58 for the owner of an ended offer only by accident of identity.

## Q2. What if the offer number or the offerer is not a usable value (nothing, text, decimal, true, 0, negative, blank name)?
- A. A number that is not a whole number from 1, or a blank or non-text offerer, is refused as invalid input (a new named refusal for the number; the blank name reuses D-59's refusal); a whole number that matches no open offer is unknown offer. **Recommended.** A consumer passing `"3"` or `None` has a bug in its call, not a missing offer, and learns it.
- B. Only a blank or non-text offerer is invalid input; any number that designates no open offer, whatever its type, is unknown offer. Fewer refusals, but `"3"` reads as "offer 3 does not exist".
- C. As A, but numeric text such as `"3"` is read as 3 (a form field). Friendlier for a screen, but a second accepted form of the number to document and test (like D-60 for dates).

## Q3. What does a successful withdrawal return?
- A. The `OfferEntry` of the withdrawn offer (number, space, lot, owner, start, end, as the listing showed it). **Recommended.** Same shape as `offer_space`; the caller can confirm what was withdrawn without listing first.
- B. Nothing, like the register writes (D-14): the list is the proof.
- C. The offer number only.

## Notes for the Product Owner
- M2 of review 07: add one line to `docs/business/decisions.md` saying consumers rely on `offer_number` on the overlap refusal, not on its sentence; the same line can cover the refusals of S3.
- M1 (orphan offers): deferred to S4, said in the plan; S1 to S3 must not be released without S4.
