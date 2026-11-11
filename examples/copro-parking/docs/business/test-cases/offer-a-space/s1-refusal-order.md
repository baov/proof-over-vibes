---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_refusals_are_reported_in_the_order_role_invalid_input_unknown_target_not_the_owner
status: covered
source: stories.md S1 AC10
---

# Refusals apply in a fixed order

When several refusals fit, the order is: not allowed to offer, invalid input, unknown space, not the owner. Each pair is tested with both fitting.
