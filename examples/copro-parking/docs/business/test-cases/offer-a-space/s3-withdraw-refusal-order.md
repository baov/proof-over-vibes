---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_unknown_offer_comes_before_not_the_owner
status: covered
source: stories.md S3 AC4; decisions.md D-65
---

# Withdrawal refusals apply in a fixed order

When several refusals fit, the order is: not allowed, invalid input, unknown offer, not the owner. Each pair is tested with both fitting.
