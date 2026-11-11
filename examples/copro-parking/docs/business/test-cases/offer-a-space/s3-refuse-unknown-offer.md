---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_number_that_is_not_an_open_offer_is_an_unknown_offer_for_any_name
status: covered
source: stories.md S3 AC3
---

# A number that is not an open offer is an unknown offer

A number that never existed, an offer already withdrawn and an offer whose end date has passed are each refused as unknown offer. An offer ending today is withdrawn, and so is an offer that starts in the future.
