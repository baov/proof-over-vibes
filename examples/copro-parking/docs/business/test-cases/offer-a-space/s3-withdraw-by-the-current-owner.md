---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_after_a_correction_the_new_owner_withdraws_and_the_old_name_does_not
status: covered
source: decisions.md D-56
---

# The current owner of the lot withdraws

After the manager changes the owner of lot A12 to Moreau, "Durand" is refused as not the owner and "moreau" withdraws the offer.
