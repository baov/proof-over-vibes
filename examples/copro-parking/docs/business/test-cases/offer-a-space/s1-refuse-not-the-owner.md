---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offerer_that_is_not_the_lot_owner_is_refused_and_an_owner_of_another_lot_too
status: covered
source: stories.md S1 AC5
---

# A name that is not the lot owner is refused

Given lot A12 owned by Durand, when another name, or the owner of another lot, offers a space of A12, then it is refused as not the owner. The name is compared ignoring case and surrounding spaces (D-46).
