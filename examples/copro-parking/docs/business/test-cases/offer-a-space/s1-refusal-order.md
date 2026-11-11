---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_invalid_input_comes_before_unknown_space_and_not_the_owner
status: covered
source: stories.md S1 AC10
---

# Refusals apply in a fixed order

When several refusals fit, the order is: not allowed to offer, invalid input, unknown space, not the owner. Each pair is tested with both fitting.
