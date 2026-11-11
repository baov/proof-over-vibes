---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_unknown_space_is_refused
status: covered
source: stories.md S1 AC2
---

# An offer on an unknown space is refused

Given no space P99 in the register, when an owner offers P99, then it is refused as unknown space and nothing changes. The number is compared ignoring case and surrounding spaces and shown as registered (D-11).
