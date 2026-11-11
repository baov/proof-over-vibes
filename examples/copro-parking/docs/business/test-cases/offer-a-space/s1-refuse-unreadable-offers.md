---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_unreadable_offers_are_reported_on_list_offer_and_withdrawal_and_never_overwritten
status: covered
source: stories.md S1 AC12
---

# Unreadable offers are reported and never overwritten

Given an offers file that is invalid JSON, not UTF-8, of the wrong shape, with a missing field, a bad date, a duplicate number or a number at or above the next one, when listing or offering, then a named offers-unreadable error is raised (a store error, not a refusal) and the file is identical afterwards (D-19). A missing or blank file means no offers.
