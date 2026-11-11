---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_withdrawing_one_of_three_offers_leaves_the_other_two_in_the_same_order
status: covered
source: stories.md S3 AC1
---

# An owner withdraws an open offer by its number

Given offer 1 of P1 by Durand (lot A12), when the owner role withdraws number 1 as "Durand" (case and surrounding spaces ignored), the list is empty. With offers 1, 2 and 3, withdrawing 2 leaves 1 and 3 in the same order.
