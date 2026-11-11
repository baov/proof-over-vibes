---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_the_removal_waits_for_every_open_offer_of_the_space_to_be_withdrawn
status: covered
source: stories.md S4 AC2
---

# Removal is allowed once the offer is withdrawn

Given an open offer on P1 that its owner withdraws, when the manager removes P1, then it is removed. When P1 had two offers, it stays refused until both are withdrawn. The decision survives a restart from the same files.
