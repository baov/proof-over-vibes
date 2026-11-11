---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offer_whose_end_has_passed_no_longer_blocks_and_one_ending_today_still_does
status: covered
source: stories.md S2 AC4
---

# An expired offer does not block

Given an offer of P1 whose end date has passed, when the owner offers P1 over those days, then it is accepted. An offer ending today still blocks today.
