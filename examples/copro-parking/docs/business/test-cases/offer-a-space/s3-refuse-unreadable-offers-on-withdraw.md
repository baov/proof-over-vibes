---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_an_unreadable_offers_file_ends_a_withdrawal_and_is_never_overwritten
status: covered
source: stories.md S3 AC5; decisions.md D-19
---

# Unreadable stores end a withdrawal with a named error

With unreadable offers a valid withdrawal ends with the offers unreadable error (a store error, not a refusal) and the file is never overwritten. With an unreadable register it ends with the store unreadable error. Invalid input and a non-owner role are refused before any store is read.
