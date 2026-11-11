---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_the_list_is_sorted_by_start_then_natural_space_order_keeping_creation_order_on_ties
status: covered
source: stories.md S1 AC8
---

# Open offers are listed by start then space

Given several offers, when anyone lists them, then they are ordered by start, then space number in natural case-folded order (p2 before P10), ties keeping offer-number order; with no offer the list is empty and two calls give the same list.
