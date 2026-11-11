---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_another_key_or_a_non_mapping_is_an_invalid_parameter
status: covered
source: decisions.md D-41
---

# An invalid parameter shape is refused

Given the manager, when adding or changing a duration rule with a parameter that has any key other than minimum and maximum, or is not a mapping, then it is refused as an invalid parameter; text, decimals and booleans as days are refused as invalid days. The listing and the file always show both keys, None for no bound. Rules are unchanged.
