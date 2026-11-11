---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_an_overlap_refusal_changes_nothing_and_the_next_offer_gets_the_number_it_would_have_had
status: covered
source: stories.md S2 AC6
---

# An overlap refusal leaves the offers unchanged

After the refusal the list and the next number are unchanged, the offers file bytes are identical, and the next accepted offer gets the number it would have had.
