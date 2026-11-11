---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_it_then_blocks_removal_and_renumbering_until_its_owner_withdraws_it
status: covered
source: decisions.md D-69
---

# Orphan offers already stored are left as they are

Given a stored offer on a number that is not registered (a file written before S4), the listing skips it and withdrawing it is an unknown offer. If that number is registered again, the offer is listed under the new lot, blocks removal and renumbering of the space, and its new owner can withdraw it.
