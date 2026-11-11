---
feature: register-lots-and-spaces
type: functional
priority: medium
automated_test: tests/test_use_cases.py::test_listing_is_sorted_and_keeps_lots_without_space
status: covered
source: stories.md S1 AC7b
---

# List sorted, empty lots included

Given lots B2 (no space) and A1 with spaces P2 and P1, when listing, then A1 comes before B2, A1 shows P1 then P2, and B2 still appears.
