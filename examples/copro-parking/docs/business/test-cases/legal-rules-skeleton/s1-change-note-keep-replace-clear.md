---
feature: legal-rules-skeleton
type: functional
priority: high
automated_test: tests/test_rule_use_cases.py::test_a_missing_note_keeps_it_text_replaces_it_blank_clears_it
status: covered
source: decisions.md D-40
---

# A change keeps, replaces or clears the note

Given a rule with a note, when the manager changes it giving no note, the note is kept; giving text, it is replaced by the trimmed text; giving blank text, it is cleared (listed as no note). Adding a rule with a blank note stores no note.
