---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_the_refusal_names_the_earliest_start_offer_and_the_lowest_number_on_ties
status: covered
source: decisions.md D-64
---

# The refusal names the earliest-start offer

Given open offers 1 (10-12) and 2 (14-16) of P1, when an offer spans 11-15, the refusal names offer 1. On equal starts it names the lowest number. The number is the one the listing shows.
