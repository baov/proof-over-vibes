---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_withdrawal_returns_the_entry_it_withdrew_as_the_listing_showed_it
status: covered
source: decisions.md D-67
---

# A withdrawal returns the entry it withdrew

A successful withdrawal returns the offer entry (number, space, lot, owner, start, end) exactly as the listing showed it.
