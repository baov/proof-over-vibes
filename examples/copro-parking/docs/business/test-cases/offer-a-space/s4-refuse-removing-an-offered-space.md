---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_open_offer_refuses_the_removal_as_space_offered_and_other_spaces_go
status: covered
source: stories.md S4 AC1
---

# An offered space cannot be removed

Given an open offer on P1, when the manager removes P1 (in any case, with surrounding spaces), then the removal is refused as space offered, P1 is still listed, the register and the offers file are unchanged. A space without an offer is removed normally in the same register.
