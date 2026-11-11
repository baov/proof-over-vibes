---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_a_stored_pair_is_listed_by_number_and_a_withdrawal_repairs_it
status: covered
source: decisions.md D-63, D-64
---

# A stored overlapping pair is ordered by number and a withdrawal repairs it

Given a file with two open offers of one space with the same start, the list orders them by offer number. Withdrawing one leaves the other listed, and the freed days accept a new offer unless the remaining one still shares them.
