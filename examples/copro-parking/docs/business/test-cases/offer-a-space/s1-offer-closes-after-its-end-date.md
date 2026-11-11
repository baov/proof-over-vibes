---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offer_is_open_until_its_end_date_included_and_gone_the_day_after
status: covered
source: stories.md S1 AC9
---

# An offer leaves the list the day after its end

Given an offer ending 2026-11-25, then it is listed on that day and gone the day after (D-52).
