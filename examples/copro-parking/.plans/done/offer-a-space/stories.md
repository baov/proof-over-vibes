---
role: product-owner
status: done
reasons: []
---

# Stories: owner offers a space (F2.1)

PRD: `docs/product/prd/offer-a-space.md` (PRD n = requirement n). Decisions: `docs/business/decisions.md` (D-45..D-51 record the human's answers Q1 to Q7, D-52..D-58 the later ones). Order: S1, then S2, then S3, then S4. Cut by business rule: the thinnest path first (offer and see it), then one rule or action per story.

D-52..D-56 settle the five points raised on the first cut.

## S1 Offer a space and list the open offers
Value: an owner publishes that a space is available for a period, and anyone sees the open offers. First story: it brings the offer store, the role and owner checks and persistence that the others rely on; the journey (pick a space, give dates, see the offer) closes here.

- AC1: an owner offers a registered space of their lot with a start date and an end date; the offer then appears in the list. (PRD 1, 9, D-45)
- AC2: an offer on a space not in the register is refused as "unknown space"; space numbers compared ignoring case and surrounding spaces. (PRD 2, D-11)
- AC3: the period is counted in whole calendar days, both dates included: an offer whose start and end are the same day is valid. An end date before the start date, or a missing or unreadable date, is refused as invalid. (PRD 3)
- AC4: a start date before today is refused; a start date equal to today is accepted. (PRD 4, D-47, D-53)
- AC5: an offer by a name that is not the lot owner's, compared ignoring case and surrounding spaces, is refused as "not the owner". (PRD 5, D-45, D-46, D-11)
- AC6: a role other than owner, the manager included, is refused as not allowed to offer, before any other check. (PRD 6, 15, D-45, D-16, D-18)
- AC7: an offer carries no price. (PRD 8, D-49)
- AC8: anyone lists the open offers; each shows an offer number, space number, lot, owner, start and end, ordered by start date, then space number in natural order, case-folded. (PRD 9, D-17, D-20, D-54)
- AC9: an offer is open from its creation until the day after its end date, or until withdrawn; after that it leaves the list. The owner shown is the current owner of the lot in the register, also after a correction. (PRD 9, D-52, D-56)
- AC10: refusals apply in this order when several fit: not allowed to offer, invalid input, unknown space, not the owner. (PRD 15)
- AC11: every refusal leaves the offers and the register unchanged. (PRD 12)
- AC12: if the stored offers cannot be read, listing and offering end with a named "offers unreadable" error and the stored offers are never overwritten. (PRD 12, D-19)
- AC13: offers are still there after a restart; the register file and the rules file are not modified. (PRD 13)
- AC14: the owner check states its limit: without accounts the name proves nothing about who is typing. (PRD, Security; D-46)

## S2 Refuse overlapping offers of the same space
Relies on S1. Value: a space is never offered twice for the same day, so a resident never sees two competing offers.

- AC1: an offer sharing at least one day with an open offer of the same space, both dates included, is refused; the reason names the existing offer. (PRD 7, 3, D-48)
- AC2: an offer of another space on the same days is accepted. (PRD 7)
- AC3: an offer that touches no day of the existing one, even the day before or after, is accepted. (PRD 7, 3)
- AC4: an offer whose end date is past no longer blocks another offer of the same space. (PRD 7, D-52)
- AC5: the overlap is the last refusal: it applies only to an offer that passed the checks of S1 AC10. (PRD 15)
- AC6: the refusal leaves the offers unchanged. (PRD 12)

## S3 Withdraw an offer
Relies on S1 and S2. Value: the owner takes back an offer that no longer holds, and the dates become free again.

- AC1: the owner who made an offer withdraws it, designating it by its offer number from the list; the owner is checked as when offering (name compared ignoring case and surrounding spaces); it no longer appears in the list. (PRD 10, D-46, D-51, D-54)
- AC2: a withdrawn offer no longer blocks another offer of the same space on the same days (S2 AC1). (PRD 10, 7)
- AC3: withdrawing an unknown offer, an offer already withdrawn, or an offer whose end date has passed (no longer open), is refused as "unknown offer". (PRD 10, D-52, D-55, D-58)
- AC4: a name that is not the owner of the offer is refused as "not the owner"; a role other than owner is refused as not allowed, before any other check. (PRD 5, 6, D-45, D-46, D-54)
- AC5: every refusal leaves the offers unchanged; the withdrawal survives a restart; if the stored offers cannot be read, withdrawing ends with the named "offers unreadable" error and the stored offers are never overwritten. (PRD 12, 13, D-19)

## S4 A space with an open offer cannot be removed or renumbered
Relies on S1 and S3 (a withdrawn offer frees the space). Value: the register cannot lose a space that people can see on offer.

- AC1: removing a space that has an open offer is refused with a named reason ("space offered"), as for a rental; the space stays registered and the register and its file are unchanged. (PRD 11, D-51)
- AC2: once the offer is withdrawn, the space can be removed again, if nothing else forbids it. (PRD 10, 11, D-51)
- AC3: the "no rental" answer of the rental check is unchanged: an offer is not a rental. A space with an offer and no rental is refused for the offer, never as "rented". (PRD 14, D-50)
- AC4: an offer whose end date is past is no longer open: it does not block the removal. (PRD 11, D-52)
- AC5: the removal of a space with no open offer behaves as before. (PRD 11, F1.2)
- Note: until this story ships, an open offer whose space is no longer in the register is skipped by the listing (D-62); for new data the case disappears once removal is blocked (AC1), but not for files written before S4 (D-69).
- AC6: changing the number of a space that has an open offer is refused as "space offered"; the space keeps its number and the register is unchanged; once the offer is withdrawn or past, the number can be changed again. (D-57, D-52)

## Open points
None. The five points of the first cut are D-52..D-56.

Note, not a question: `docs/product/story-map.md` still shows F1.2 as todo while the brief says it is built; the story map belongs to the product manager.
