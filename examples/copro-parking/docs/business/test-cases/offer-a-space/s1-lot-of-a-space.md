---
feature: offer-a-space
type: functional
priority: high
automated_test: tests/test_register.py::test_the_lot_of_a_space_is_found_ignoring_case_and_spaces
status: covered
source: architect.md (Register.lot_of)
---

# The register gives the lot of a space

The register gives the lot, with its current owner, of a space found ignoring case and surrounding spaces; an unknown space or a blank one is refused.
