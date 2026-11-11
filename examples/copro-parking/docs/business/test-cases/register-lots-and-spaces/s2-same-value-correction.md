---
feature: register-lots-and-spaces
type: functional
priority: high
automated_test: tests/test_use_cases.py::test_a_same_value_correction_is_accepted_and_stores_the_new_text
status: covered
source: decisions.md D-21
---

# A same-value correction is accepted

Given owner "Durand" and space "P1", when the manager changes the owner to " Durand " or the number to "p1", then it is accepted: the stored text becomes the new trimmed text ("Durand", "p1") and nothing else changes.
