---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offer_of_another_space_on_the_same_days_is_accepted
status: covered
source: stories.md S2 AC2
---

# Another space on the same days is accepted

Given an open offer of P1, when the owner offers P2 on the same days, then it is accepted. A space written ` p1 ` is the same space as P1.
