---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_offer_use_cases.py::test_blank_missing_or_non_text_space_or_offerer_is_refused_as_invalid_input
status: covered
source: decisions.md D-59
---

# Blank space or offerer is refused as invalid input

A blank, missing or non-text space number or offerer name is refused as blank value, after the role check and before unknown space and not the owner.
