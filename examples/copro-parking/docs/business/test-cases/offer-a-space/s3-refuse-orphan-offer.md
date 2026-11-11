---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offer_whose_space_left_the_register_is_an_unknown_offer_for_any_name
status: covered
source: decisions.md D-65
---

# An offer whose space left the register is an unknown offer

Given an open offer whose space was removed from the register, withdrawing it is refused as unknown offer, for any name.
