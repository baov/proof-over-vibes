---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_owner_offers_a_space_of_their_lot_and_the_list_shows_it_with_all_its_fields
status: covered
source: stories.md S1 AC1
---

# An owner offers a registered space of their lot

Given lot A12 owned by Durand with space P1, when Durand (owner role) offers P1 from 2026-11-20 to 2026-11-25, then the call returns the offer and the list shows it with number, space, lot, owner, start and end, even when it starts later than today.
