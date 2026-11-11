---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_unreadable_register_wins_over_an_unknown_offer_whatever_the_number
status: covered
source: decisions.md D-70
---

# A store error wins over an unknown offer on withdrawal

With an unreadable register, a valid withdrawal ends with the store unreadable error whatever the number: unknown, ended, withdrawn or open. With both stores unreadable it ends with the offers unreadable error. A blank offerer is reported before a bad offer number; invalid input and a role other than owner are refused before any store is read.
