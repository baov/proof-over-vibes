# PRD: F1.2 Register lots and spaces

Epic E1. Picked by the human. Decisions confirmed by the human.

## Problem
A manager of a co-ownership has no shared record of which parking spaces exist and which owner holds them; without it nothing can be offered or rented. Today: notice board, spreadsheet or chat (*unverified*).

## Goal and success
Goal: one reliable register of the spaces of one co-ownership. Success: every space is registered once, with an owner, and can be found in a list.

## Users and use
Manager (registers). Main path: the manager registers a lot with its owner, then registers the parking space(s) of that lot, then lists them.

## Scope
- In: lot, parking space, owner of a lot, listing, correcting an entry, removing an entry that has no rental.
- Out: offers, rentals, arbitration, prices, payments, French legal rules (E5), several co-ownerships (E6: one co-ownership assumed), accounts and login.

## Requirements
1. A lot has an identifier unique in the co-ownership; registering a duplicate is refused with a clear reason.
2. A parking space has a number unique in the co-ownership and belongs to exactly one lot.
3. A lot has exactly one owner, identified by a name; registering a lot without an owner is refused.
4. Registering a space on an unknown lot is refused.
5. The manager can list all lots and spaces, showing for each space its number, lot and owner.
6. The manager can change a lot's owner and a space's number; the uniqueness rules still hold afterwards.
7. The manager can remove a space; removal is refused if the space has an existing or planned rental (once rentals exist).
8. Only the manager can register, change or remove lots and spaces; any other role is refused.
9. Every refusal leaves the register unchanged.

## Dependencies
The glossary terms (lot, space, owner, manager) to confirm with the human. Nothing else.

## Risks and open questions
- Decided: a space always belongs to a lot; one owner per lot; only the manager registers and edits.
- For the architect: persistence, history of owner changes, concurrent edits, how identity of owner and manager will later be modeled.

## Questions for the human
None open.
