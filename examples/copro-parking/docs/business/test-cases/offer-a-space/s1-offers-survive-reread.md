---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_json_offer_repository.py::test_offers_survive_a_re_read_and_numbering_goes_on_after_a_restart
status: covered
source: stories.md S1 AC13
---

# Offers survive a restart

A new repository on the same file lists the same offers, and numbering goes on (first number 1, never reused, D-61).
