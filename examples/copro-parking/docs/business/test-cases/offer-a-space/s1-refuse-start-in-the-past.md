---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_start_before_today_is_refused_and_a_start_equal_to_today_is_accepted
status: covered
source: stories.md S1 AC4
---

# A start before today is refused

Given today from the clock, when the owner offers with a start the day before, then it is refused as invalid; a start equal to today is accepted (D-47, D-53).
