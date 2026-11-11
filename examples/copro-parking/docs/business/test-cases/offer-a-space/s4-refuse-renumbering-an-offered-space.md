---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_open_offer_refuses_the_renumbering_as_space_offered
status: covered
source: stories.md S4 AC6; decisions.md D-57, D-71
---

# An offered space cannot be given another number

Given an open offer on P1, giving P1 another number is refused as space offered, P1 keeps its number and the register and the offers file are unchanged. A same-value or case-only change of the number is refused too. A space without an offer is renumbered as before.
