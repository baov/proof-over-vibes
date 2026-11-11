---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_the_manager_adds_a_rule_and_the_listing_shows_it_with_a_trimmed_note
status: covered
source: stories.md S1 AC1
---

# The manager adds a duration-bounds rule

Given no rule, when the manager adds "Short stay" as duration bounds with a minimum of 30 days and the note " Bylaws art. 3 ", then the listing shows the rule with that name, kind, parameter and the trimmed note. The name is shown trimmed as typed, case kept (D-15); a rule added without note shows no note.
