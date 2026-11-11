---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_one_day_offer_where_start_equals_end_is_valid
status: covered
source: stories.md S1 AC3
---

# A one-day offer is valid

Given a start date equal to the end date, when the owner offers the space, then the offer is accepted: both dates are included.
