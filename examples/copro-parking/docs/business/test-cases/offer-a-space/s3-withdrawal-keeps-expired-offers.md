---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_a_withdrawal_keeps_the_expired_offers_and_the_other_open_ones_in_the_file
status: covered
source: stories.md S3 AC5; decisions.md D-61
---

# A withdrawal drops nothing else from the file

An expired offer of another space stays in the offers file after a withdrawal (no purge), and so do the other open offers.
