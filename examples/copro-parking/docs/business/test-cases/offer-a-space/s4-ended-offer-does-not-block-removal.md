---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_offer_ended_yesterday_does_not_block_and_is_not_purged
status: covered
source: stories.md S4 AC4; decisions.md D-52
---

# An ended offer does not block removal

An offer that ended yesterday does not block the removal and stays in the offers file. An offer ending today blocks it, as does one starting in the future, and as does a space with one ended and one open offer.
