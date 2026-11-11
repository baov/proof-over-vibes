---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_a_withdrawal_survives_a_re_read_and_the_next_number_is_kept
status: covered
source: stories.md S3 AC5
---

# A withdrawal survives a restart

With the real repository, the withdrawn offer is gone after a re-read, the next number is unchanged and the next offer gets the number it would have had.
