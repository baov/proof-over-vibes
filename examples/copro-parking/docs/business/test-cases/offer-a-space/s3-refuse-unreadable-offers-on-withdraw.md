---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_unreadable_offers_are_reported_on_list_offer_and_withdrawal_and_never_overwritten
status: covered
source: stories.md S3 AC5; decisions.md D-19, D-70
---

# Unreadable stores end a withdrawal with a named error

With unreadable offers a valid withdrawal ends with the offers unreadable error (a store error, not a refusal) and the file is never overwritten. With an unreadable register it ends with the store unreadable error, whatever the number (D-70, see the unknown-offer case). Invalid input and a non-owner role are refused before any store is read.
