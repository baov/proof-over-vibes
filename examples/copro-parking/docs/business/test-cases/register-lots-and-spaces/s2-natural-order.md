---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_listing_orders_numbers_naturally_whatever_the_registration_order
status: covered
source: decisions.md D-20 (S1 carried over)
---

# Listing uses natural order

Given lots "A10", "a2" and spaces "P10", "p2" registered in any order, then the listing shows a2 before A10 and p2 before P10 (case-folded, digits compared as numbers).
