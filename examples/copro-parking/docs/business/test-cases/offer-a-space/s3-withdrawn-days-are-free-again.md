---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_withdrawn_offer_no_longer_blocks_its_days_and_the_new_offer_gets_the_next_number
status: covered
source: stories.md S3 AC2
---

# A withdrawn offer no longer blocks its days

Given offer 1 of P1 from 20 to 25, once it is withdrawn an offer of P1 from 22 to 30 is accepted and gets the next number, not 1. The other space and the other offers are untouched.
