---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_number_that_is_not_an_open_offer_is_an_unknown_offer_for_any_name
status: covered
source: decisions.md D-65, D-69
---

# An offer whose space is not registered is an unknown offer

Given a stored offer whose space is not registered, withdrawing it is refused as unknown offer, for any name.
