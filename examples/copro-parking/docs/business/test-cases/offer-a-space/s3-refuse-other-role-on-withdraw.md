---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_any_role_other_than_owner_is_refused_first_whatever_the_request_and_the_stores
status: covered
source: stories.md S3 AC4
---

# Any role other than owner is refused first

The manager, a resident, no role, a string and an integer are refused as not allowed, with the clock and both stores untouched, even when the stores are unreadable and the input invalid.
