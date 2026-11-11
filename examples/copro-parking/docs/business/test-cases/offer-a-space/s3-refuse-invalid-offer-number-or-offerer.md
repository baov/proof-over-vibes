---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_a_number_that_is_not_a_whole_number_from_one_is_refused_as_invalid_input
status: covered
source: decisions.md D-66
---

# An unusable number or offerer is invalid input

A number that is not a whole number from 1 (nothing, text, decimal, true, zero, negative) and a blank, missing or non-text offerer are refused as invalid input. A whole number matching no open offer stays an unknown offer.
