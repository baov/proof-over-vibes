---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offer_sharing_a_day_with_an_open_offer_of_the_space_is_refused_naming_it
status: covered
source: stories.md S2 AC1
---

# An offer sharing a day with an open offer of the space is refused

Given an open offer of P1 from 10 to 14, when the owner offers P1 from 14 to 20, from 8 to 10, from 11 to 12 or from 5 to 30, then it is refused as an overlap that names offer 1; sharing a single day is enough, in either order of creation. The same request twice is refused naming the first offer.
