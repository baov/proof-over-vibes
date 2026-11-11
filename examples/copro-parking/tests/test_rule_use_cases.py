import bootstrap  # noqa: F401  (must come first)
import unittest

from copro_parking.application import refusals
from copro_parking.application.role import Role
from copro_parking.application.rule_use_cases import (RuleChange, RuleEntry,
                                                      RuleSpec, add_rule,
                                                      change_rule, list_rules,
                                                      remove_rule)
from fakes import InMemoryRuleRepository

M = Role.MANAGER
KIND = "duration_bounds"


def bounds(minimum=None, maximum=None):
    return {"minimum": minimum, "maximum": maximum}


def spec(minimum=None, maximum=None, note=None):
    return RuleSpec(KIND, bounds(minimum, maximum), note)


class AddAndListRules(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRuleRepository()

    def test_the_manager_adds_a_rule_and_the_listing_shows_it_with_a_trimmed_note(self):
        add_rule(self.repo, M, "  Short STAY ", spec(30, None, " Bylaws art. 3 "))
        self.assertEqual([RuleEntry("Short STAY", KIND, bounds(30, None), "Bylaws art. 3")],
                         list_rules(self.repo))

    def test_a_rule_added_without_note_or_with_a_blank_one_lists_no_note(self):
        add_rule(self.repo, M, "A", spec(30))
        add_rule(self.repo, M, "B", spec(30, note="   "))
        self.assertEqual([None, None], [e.note for e in list_rules(self.repo)])

    def test_a_minimum_only_a_maximum_only_or_both_are_accepted_and_both_keys_are_stored(self):
        for index, (low, high) in enumerate(
                [(30, None), (None, 90), (30, 90), (45, 45), (1, 1), (1, None), (None, 1)]):
            add_rule(self.repo, M, f"r{index}", spec(low, high))
            self.assertEqual(bounds(low, high), list_rules(self.repo)[index].parameter)
        add_rule(self.repo, M, "A", RuleSpec(KIND, {"minimum": 30}))
        add_rule(self.repo, M, "B", RuleSpec(KIND, {"maximum": 90}))
        stored = {e.name: e.parameter for e in list_rules(self.repo)}
        self.assertEqual([bounds(30, None), bounds(None, 90)], [stored["A"], stored["B"]])

    def test_listing_follows_the_natural_case_folded_order(self):
        self.assertEqual([], list_rules(self.repo))
        for name in ("R10", "r2", "r11", "R1"):
            add_rule(self.repo, M, name, spec(30))
        self.assertEqual(["R1", "r2", "R10", "r11"], [e.name for e in list_rules(self.repo)])

    def test_ties_keep_the_registration_order(self):
        add_rule(self.repo, M, "a01", spec(30))
        add_rule(self.repo, M, "A1", spec(30))
        self.assertEqual(["a01", "A1"], [e.name for e in list_rules(self.repo)])
        other = InMemoryRuleRepository()
        add_rule(other, M, "A1", spec(30))
        add_rule(other, M, "a01", spec(30))
        self.assertEqual(["A1", "a01"], [e.name for e in list_rules(other)])

    def test_listing_needs_no_role_and_gives_the_same_list_twice(self):
        add_rule(self.repo, M, "B", spec(30))
        add_rule(self.repo, M, "A", spec(30))
        self.assertEqual(list_rules(self.repo), list_rules(self.repo))


class RefusedAdditions(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRuleRepository()
        add_rule(self.repo, M, "Short stay", spec(30, 365))
        self.before = list_rules(self.repo)

    def refused(self, error, name, rule_spec):
        with self.assertRaises(error):
            add_rule(self.repo, M, name, rule_spec)
        self.assertEqual(self.before, list_rules(self.repo))

    def refused_parameter(self, error, parameter):
        """A rule parameter is validated the same way when a rule is added and when it is changed."""
        self.refused(error, "X", RuleSpec(KIND, parameter))
        if parameter is not None:  # no parameter on a change means "keep the current one"
            with self.assertRaises(error):
                change_rule(self.repo, M, "Short stay", RuleChange(parameter=parameter))
            self.assertEqual(self.before, list_rules(self.repo))

    def test_a_rule_with_neither_bound_is_refused(self):
        for parameter in (None, {}, bounds(None, None)):
            self.refused_parameter(refusals.NoBoundRefused, parameter)

    def test_zero_negative_or_non_whole_days_are_refused(self):
        for value in (0, -3, 1.5, 30.0, "30", True, False, [30]):
            self.refused_parameter(refusals.InvalidDaysRefused, bounds(value, None))
            self.refused_parameter(refusals.InvalidDaysRefused, bounds(None, value))
        for parameter in (bounds(30, 0), bounds(0, 30)):  # a valid bound excuses nothing
            self.refused_parameter(refusals.InvalidDaysRefused, parameter)

    def test_a_minimum_above_the_maximum_is_refused(self):
        self.refused_parameter(refusals.MinimumAboveMaximumRefused, bounds(31, 30))

    def test_another_key_or_a_non_mapping_is_an_invalid_parameter(self):
        for parameter in ({"minimum": 3, "other": 1}, {"min": 3}, "30", 30, [30]):
            self.refused_parameter(refusals.InvalidParameterRefused, parameter)

    def test_a_blank_or_missing_name_and_a_non_text_note_are_refused_as_a_blank_value(self):
        for name in ("", "   ", None, 7):
            self.refused(refusals.BlankValueRefused, name, spec(30))
        self.refused(refusals.BlankValueRefused, "X", RuleSpec(KIND, bounds(30), 5))

    def test_a_name_equal_ignoring_case_and_spaces_is_refused(self):
        self.refused(refusals.DuplicateRuleRefused, " short STAY ", spec(10))
        self.refused(refusals.DuplicateRuleRefused, "Short stay", spec(30, 365))
        add_rule(self.repo, M, "Long stay", spec(None, 90))
        with self.assertRaises(refusals.DuplicateRuleRefused):
            add_rule(self.repo, M, "Long stay", spec(None, 90))
        self.assertEqual(2, len(list_rules(self.repo)))

    def test_an_unknown_or_missing_kind_is_refused(self):
        for kind in ("owner_consent_required", "Duration_Bounds", "", None, 3, ["x"]):
            self.refused(refusals.UnknownKindRefused, "X", RuleSpec(kind, bounds(30)))

    def test_the_check_order_is_blank_name_then_kind_then_parameter_then_duplicate(self):
        bad = RuleSpec("nope", {"x": 1})
        self.refused(refusals.BlankValueRefused, " ", bad)
        self.refused(refusals.UnknownKindRefused, "Short stay", bad)
        self.refused(refusals.InvalidParameterRefused, "Short stay", RuleSpec(KIND, {"x": 1}))
        self.refused(refusals.NoBoundRefused, "Short stay", RuleSpec(KIND, None))


class ChangedRules(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRuleRepository()
        add_rule(self.repo, M, "Short stay", spec(30, 365, "Bylaws art. 3"))

    def only(self):
        (entry,) = list_rules(self.repo)
        return entry

    def test_a_given_parameter_replaces_the_whole_one_and_a_missing_one_keeps_it(self):
        change_rule(self.repo, M, "Short stay", RuleChange(parameter=bounds(None, 200)))
        self.assertEqual(bounds(None, 200), self.only().parameter)
        change_rule(self.repo, M, "Short stay", RuleChange(note="Other"))
        self.assertEqual(bounds(None, 200), self.only().parameter)

    def test_a_missing_note_keeps_it_text_replaces_it_blank_clears_it(self):
        change_rule(self.repo, M, "Short stay", RuleChange(parameter=bounds(40)))
        self.assertEqual("Bylaws art. 3", self.only().note)
        change_rule(self.repo, M, "Short stay", RuleChange(note="  Art. 4 "))
        self.assertEqual("Art. 4", self.only().note)
        change_rule(self.repo, M, "Short stay", RuleChange(note="   "))
        self.assertIsNone(self.only().note)

    def test_the_name_is_found_ignoring_case_and_spaces_and_name_and_kind_stay(self):
        change_rule(self.repo, M, " SHORT stay ", RuleChange(parameter=bounds(40)))
        self.assertEqual(RuleEntry("Short stay", KIND, bounds(40), "Bylaws art. 3"), self.only())

    def test_a_changed_rule_keeps_its_registration_position(self):
        repo = InMemoryRuleRepository()
        for name in ("a01", "A1", "b"):
            add_rule(repo, M, name, spec(30))
        change_rule(repo, M, "a01", RuleChange(parameter=bounds(40)))
        self.assertEqual(["a01", "A1", "b"], [e.name for e in list_rules(repo)])

    def test_a_change_that_leaves_the_rule_as_it_is_is_accepted_and_changes_nothing(self):
        before = list_rules(self.repo)
        for change in (RuleChange(parameter=bounds(30, 365)), RuleChange()):
            change_rule(self.repo, M, "Short stay", change)
            self.assertEqual(before, list_rules(self.repo))

    def test_an_unknown_rule_is_refused(self):
        before = list_rules(self.repo)
        with self.assertRaises(refusals.UnknownRuleRefused):
            change_rule(self.repo, M, "Z9", RuleChange(parameter=bounds(40)))
        with self.assertRaises(refusals.UnknownRuleRefused):
            change_rule(self.repo, M, "Z9", RuleChange())
        self.assertEqual(before, list_rules(self.repo))

    def test_a_blank_name_is_refused_before_an_unknown_rule_before_the_parameter(self):
        with self.assertRaises(refusals.BlankValueRefused):
            change_rule(self.repo, M, " ", RuleChange(parameter={"x": 1}))
        with self.assertRaises(refusals.UnknownRuleRefused):
            change_rule(self.repo, M, "Z9", RuleChange(parameter={"x": 1}))

    def test_a_non_text_note_is_refused_as_a_blank_value(self):
        with self.assertRaises(refusals.BlankValueRefused):
            change_rule(self.repo, M, "Short stay", RuleChange(note=5))
        self.assertEqual("Bylaws art. 3", self.only().note)


class RemovedRules(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRuleRepository()
        add_rule(self.repo, M, "Short stay", spec(30))
        add_rule(self.repo, M, "Long stay", spec(None, 90))

    def test_a_removed_rule_disappears_and_its_name_is_free_again(self):
        remove_rule(self.repo, M, " short STAY ")
        self.assertEqual(["Long stay"], [e.name for e in list_rules(self.repo)])
        add_rule(self.repo, M, "Short stay", spec(10))
        self.assertEqual(2, len(list_rules(self.repo)))

    def test_a_removed_and_re_added_rule_counts_as_registered_last(self):
        add_rule(self.repo, M, "a01", spec(1))
        add_rule(self.repo, M, "A1", spec(1))
        remove_rule(self.repo, M, "a01")
        add_rule(self.repo, M, "a01", spec(1))
        self.assertEqual(["A1", "a01"], [e.name for e in list_rules(self.repo)][:2])

    def test_an_unknown_or_already_removed_rule_is_refused(self):
        before = list_rules(self.repo)
        with self.assertRaises(refusals.UnknownRuleRefused):
            remove_rule(self.repo, M, "Z9")
        self.assertEqual(before, list_rules(self.repo))
        remove_rule(self.repo, M, "Long stay")
        with self.assertRaises(refusals.UnknownRuleRefused):
            remove_rule(self.repo, M, "Long stay")

    def test_a_blank_name_is_refused(self):
        for name in ("", "  ", None):
            with self.assertRaises(refusals.BlankValueRefused):
                remove_rule(self.repo, M, name)
        self.assertEqual(2, len(list_rules(self.repo)))


class OnlyTheManagerWrites(unittest.TestCase):
    def test_any_other_role_is_refused_first_whatever_the_request(self):
        repo = InMemoryRuleRepository()
        add_rule(repo, M, "Short stay", spec(30))
        before = list_rules(repo)
        for role in (Role.OWNER, Role.RESIDENT, None, "manager", 1):
            for call in (lambda: add_rule(repo, role, " ", RuleSpec("nope", {"x": 1})),
                         lambda: add_rule(repo, role, "Short stay", spec(30)),
                         lambda: change_rule(repo, role, "Z9", RuleChange(parameter={})),
                         lambda: change_rule(repo, role, "Short stay", RuleChange(note="x")),
                         lambda: remove_rule(repo, role, "Z9"),
                         lambda: remove_rule(repo, role, "Short stay")):
                with self.assertRaises(refusals.ManagerOnly):
                    call()
                self.assertEqual(before, list_rules(repo))
