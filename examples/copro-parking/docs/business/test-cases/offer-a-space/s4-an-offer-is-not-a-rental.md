---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offer_is_not_a_rental_and_a_rental_is_asked_first
status: covered
source: stories.md S4 AC3; decisions.md D-50
---

# An offer is not a rental

An open offer on a space with no rental gives the space offered refusal, never the space rented one. A rental and no offer gives space rented (unchanged). Both give space rented and the offers are not asked.
