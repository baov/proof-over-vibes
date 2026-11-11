---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_end_before_the_start_is_refused_as_an_invalid_period
status: covered
source: stories.md S1 AC3
---

# An end before the start is refused

Given an end date before the start date, when the owner offers, then it is refused as an invalid period and nothing changes. A missing or unreadable date is refused the same way.
