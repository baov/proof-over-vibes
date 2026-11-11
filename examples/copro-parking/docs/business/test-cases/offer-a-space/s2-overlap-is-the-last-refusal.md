---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_the_overlap_is_the_last_refusal
status: covered
source: stories.md S2 AC5
---

# The overlap is the last refusal

When a request overlaps an open offer and also fits an earlier refusal (role, invalid period, blank field, unknown space, not the owner), the earlier refusal wins.
