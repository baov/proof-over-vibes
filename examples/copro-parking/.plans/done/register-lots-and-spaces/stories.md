---
role: product-owner
status: done
reasons: []
---

# Stories: register lots and spaces

PRD: `docs/product/prd/register-lots-and-spaces.md` (PRD n = requirement n). Decisions: `docs/business/decisions.md`. Order: S1, then S2, then S3.

## S1 Register lots and spaces and list them
Value: the manager gets the first usable register: an owned lot, its spaces, a list. Closes the journey end to end. Includes the role check and the register's persistence, which every later story relies on.

- AC1: the manager registers a lot with an identifier and one owner. (PRD 3, D-2)
- AC2: a lot whose identifier already exists is refused with a clear reason; identifiers are compared ignoring case and surrounding spaces. (PRD 1, D-11)
- AC3: a lot with no owner, or with a blank owner name, is refused. (PRD 3, D-2, D-12)
- AC4: the manager registers a space with a number on an existing lot. (PRD 2, D-1)
- AC5: a space whose number already exists is refused with a clear reason; numbers are compared ignoring case and surrounding spaces. (PRD 2, D-11)
- AC6: a space on an unknown lot is refused. (PRD 4, D-1)
- AC7: the manager lists all lots and spaces; each space shows its number, lot and owner. (PRD 5)
- AC7b: the list shows lots sorted by identifier with their owner, then each lot's spaces sorted by number; a lot with no space still appears. (PRD 5, D-13)
- AC7c: a blank lot identifier or space number is refused. (D-12)
- AC8: any other role is refused with a manager-only refusal on every registration. (PRD 8, D-3, D-4)
- AC9: every refusal leaves the register unchanged. (PRD 9)
- AC10: registered entries are still there when the register is read again. (PRD goal "reliable register"; ADR-0002)

## S2 Correct a lot's owner and a space's number
Relies on S1. Value: the manager fixes an entry without removing it.

- AC1: the manager changes a lot's owner. (PRD 6, D-2)
- AC2: the manager changes a space's number. (PRD 6)
- AC3: a new number already used by another space (ignoring case and surrounding spaces) is refused; the register is unchanged. (PRD 6, PRD 2, PRD 9, D-11)
- AC3b: a blank new number or a blank new owner name is refused; the register is unchanged. (PRD 6, PRD 9, D-12)
- AC4: changing an unknown lot or space is refused. (PRD 4, PRD 9)
- AC5: any other role is refused with a manager-only refusal. (PRD 8, D-3, D-4)
- AC6: the listing shows the changed owner or number. (PRD 5, PRD 6)

## S3 Remove a space
Relies on S1. Value: the manager drops a space registered by mistake. The rental check is a port answering "no rental" until E3 (architect.md).

- AC1: the manager removes a space; it no longer appears in the listing. (PRD 7, PRD 5)
- AC2: removing an unknown space is refused. (PRD 7, PRD 9)
- AC3: a space with an existing or planned rental is refused and stays registered; checked against the rental port, which answers "no rental" for now. (PRD 7, PRD 9)
- AC4: any other role is refused with a manager-only refusal. (PRD 8, D-3, D-4)
- AC5: the removed number can be registered again. (PRD 2, PRD 7)
- AC6: removal never removes a lot; a lot left with no space still appears in the listing. (D-10, D-13)

## Out of the stories
Removing a lot (D-10), offers, rentals, prices, French legal rules (D-5), several co-ownerships, accounts.
