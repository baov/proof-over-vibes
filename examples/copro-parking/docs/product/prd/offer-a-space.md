# PRD: F2.1 Owner offers a space for a period

Epic E2. Picked by the human (backlog item 2). Decisions Q1 to Q7 are answered by the human (see the end). Every statement about French law is *unverified*; none is asserted.

## Problem
The vision starts with owners offering unused spaces, but nothing records that a space is available, by whom, or when. Without an offer, a resident has nothing to request (F2.2) and the manager nothing to arbitrate (E3). Today: notice board, chat or word of mouth (*unverified*).

## Goal and success
Goal: an owner can publish that one of their spaces is available for a period, and everyone can see the open offers. Success: every open offer names a registered space, its owner and a period, and no two open offers cover the same space on the same day (subject to).

## Users and use
Owner (offers). Manager. Resident (reads offers; requests come with F2.2). Main path: the owner picks a space of their lot, gives a start and an end date, the offer appears in the list of open offers, and the owner can withdraw it.

## Scope
- In: create an offer, list offers, withdraw an offer, the refusals of these.
- Out: requests and rentals (F2.2), arbitration (E3), overlapping *rentals* (F2.3), ending a rental (F2.4), price and amount due (E4), French legal rules and their check (E5), notifications, payment, several co-ownerships (E6), accounts and login.

## Requirements
1. An offer refers to a registered space (F1.2), and has a start date and an end date.
2. An offer on an unknown space is refused with a clear reason.
3. The period is counted in whole calendar days, both dates included, as in E5. An end date before the start date, or a missing or unreadable date, is refused as invalid.
4. A start date in the past is refused.
5. Only the owner of the space's lot can offer that space; any other owner is refused.
6. A role other than owner is refused as not allowed to offer; the manager cannot offer.
7. Two open offers of the same space may not share a day; the second is refused with a reason naming the first.
8. An offer carries no price.
9. Anyone can list the open offers, each showing space number, lot, owner, start and end; the order is by start date, then space number in natural order, case-folded (as D-20). (Reads are open, as D-17.)
10. The owner who made an offer can withdraw it; a withdrawn offer no longer appears and no longer blocks other offers. Withdrawing an unknown offer is refused.
11. A space with an open offer cannot be removed from the register; removal is refused with a named reason, as for a rental.
12. Every refusal leaves offers and register unchanged. Unreadable storage ends with a named error and never overwrites the stored offers (as D-19).
13. Offers survive a restart. The register file and the rules file are not modified by this feature.
14. The "no rental" answer of F1.2 requirement 7 is unchanged: an offer is not a rental.
15. Refusal order when several apply: not allowed to offer first (as D-16), then invalid input, then unknown space, then the owner check, then the overlap.

## Security and performance targets
- Security: who may do what is requirements 5, 6 and 9; the owner check (Q2) is only as strong as the identity available (D-18: a role, no accounts), which is a limit to state, not to hide. No personal data beyond the owner name already in the register.
- Performance: none stated; none given by the human or the market watch, none invented.

## Dependencies
- F1.2 register: built (space, lot, owner name).
- E5 rules: built as a skeleton; it is not applied at offer time (Q6).
- Identity of the offering owner: absent (no accounts); see the architect.

## Risks and open questions
- Bet: owners will offer spaces for a period given as dates. If offers are recurring (every weekend, nights only), a period of dates is the wrong shape. *Unverified*.
- For the architect: how the offering owner is identified without accounts; today's date for requirement 4 (a clock the tests control); storage of offers, apart from the register and the rules; how "space has an open offer" reaches the register's removal without breaking the `RentalCheck` port; concurrent offers on the same space; public type of an offer, as F1.2 and E5 types are public (ADR-0003); date and time-zone handling.

## Answered (by the human)
- Q1: only the owner of the space's lot may offer it (requirements 5, 6).
- Q2: the offerer gives a name, compared with the lot owner ignoring case and surrounding spaces (D-11). Limit: without accounts this proves nothing about who is typing.
- Q3: a start date in the past is refused (requirement 4).
- Q4: a second offer sharing a day with an existing offer of the same space is refused (requirement 7).
- Q5: no price in F2.1 (requirement 8; F4.1 later).
- Q6: the `no rental` answer of F1.2 is untouched; E5 rules are not applied at offer time (requirement 14).
- Q7: the owner can withdraw an offer, and a space with an open offer cannot be removed (requirements 10, 11).

## Questions for the human
None open.
