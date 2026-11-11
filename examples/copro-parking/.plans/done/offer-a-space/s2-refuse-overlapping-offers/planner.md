---
role: planner
status: done
reasons: []
---

# Planner: S2 Refuse overlapping offers

Answered by delegate, recorded as D-63 (Q1 A) and D-64 (Q2 A); `plan.md` is final. Two behaviors a consumer sees are decided by no document. Decision numbers: the log ends at D-62, so the next free number is D-63.

## Q1 (carried over M2). An offers file already holds two offers of one space sharing a day (S1 allowed it). What does S2 do with it?
- A. Tolerate: the file loads, the pair stays listed; only new offers are checked. **Recommended.** Nothing can repair such a file before S3 (withdrawal), so rejecting it stops offering and listing for good; the pair is an S1 artefact, not new corruption.
- B. Reject on load: `OffersUnreadable` on list and offer, as the architect's note says. Strict "no two open offers on a day", but the feature stays dead until someone edits the file by hand.
- C. Reject only if the overlapping pair is still open (past pairs ignored). Same dead end as B for live pairs.

Choosing A amends the line of `architect.md` and ADR-0004 "on load ... two offers of the same space sharing a day is unreadable" (the human's answer overrides it; the architect records it).

## Q2. A new offer overlaps several open offers of the space (for instance it spans two separate ones). Which one does the refusal name?
- A. The one with the earliest start (ties: lowest number), the first the owner sees in the list. **Recommended.**
- B. The lowest offer number (the oldest).
- C. All of them (a list of numbers).

Not a question (decided in the plan): the refusal carries the number of the named offer, the same number the listing shows.
