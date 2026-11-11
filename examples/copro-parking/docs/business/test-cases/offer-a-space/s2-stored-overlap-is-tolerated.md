---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_a_stored_pair_of_overlapping_offers_loads_and_only_new_offers_are_checked
status: covered
source: decisions.md D-63
---

# A stored overlapping pair is tolerated

Given a file written directly with two overlapping open offers of one space, listing shows both, a new offer on free days succeeds, and a new offer overlapping them is refused naming the earliest.
