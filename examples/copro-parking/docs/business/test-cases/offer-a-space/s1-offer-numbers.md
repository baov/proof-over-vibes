---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_the_same_request_twice_makes_two_offers_numbered_one_and_two
status: covered
source: decisions.md D-61
---

# Offers are numbered from 1

The same request twice makes two offers, numbered 1 and 2 (overlap is refused from S2).
