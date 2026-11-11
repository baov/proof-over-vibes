---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_offers_on_the_days_next_to_an_offer_are_accepted_and_a_one_day_offer_inside_is_refused
status: covered
source: stories.md S2 AC3
---

# Adjacent days do not overlap

Given an offer of P1 from 10 to 14, when offering 15 to 20 or 5 to 9 then it is accepted; a one-day offer on 14 is refused.
