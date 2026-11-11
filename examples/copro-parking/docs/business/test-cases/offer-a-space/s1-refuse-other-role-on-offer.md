---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_any_role_other_than_owner_is_refused_first_whatever_the_request_and_the_stores
status: covered
source: stories.md S1 AC6
---

# Any role other than owner is refused first

Given a manager, resident, missing or other role, when it offers a space, then it is refused as not allowed to offer, before any other check and before any store is read, even with bad dates or unreadable files.
