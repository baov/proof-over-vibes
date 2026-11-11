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
        add_rule(self.repo, M, "Short stay", spec(30, None, " Bylaws art. 3 "))
        self.assertEqual([RuleEntry("Short stay", KIND, bounds(30, None), "Bylaws art. 3")],
                         list_rules(self.repo))

    def test_a_rule_added_without_note_lists_no_note(self):
        add_rule(self.repo, M, "Short stay", spec(30))
        self.assertIsNone(list_rules(self.repo)[0].note)

    def test_a_blank_note_on_add_means_no_note(self):
        add_rule(self.repo, M, "Short stay", spec(30, note="   "))
        self.assertIsNone(list_rules(self.repo)[0].note)

    def test_the_name_is_listed_trimmed_as_typed(self):
        add_rule(self.repo, M, "  Short STAY ", spec(30))
        self.assertEqual("Short STAY", list_rules(self.repo)[0].name)

    def test_a_minimum_only_a_maximum_only_or_both_are_accepted(self):
        for index, (low, high) in enumerate(
                [(30, None), (None, 90), (30, 90), (45, 45), (1, 1), (1, None), (None, 1)]):
            add_rule(self.repo, M, f"r{index}", spec(low, high))
            self.assertEqual(bounds(low, high), list_rules(self.repo)[index].parameter)

    def test_a_parameter_with_a_single_key_stores_both_keys(self):
        add_rule(self.repo, M, "A", RuleSpec(KIND, {"minimum": 30}))
        add_rule(self.repo, M, "B", RuleSpec(KIND, {"maximum": 90}))
        self.assertEqual([bounds(30, None), bounds(None, 90)],
                         [e.parameter for e in list_rules(self.repo)])

    def test_listing_follows_the_natural_case_folded_order(self):
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

    def test_listing_twice_gives_the_same_list_and_writes_nothing(self):
        add_rule(self.repo, M, "B", spec(30))
        add_rule(self.repo, M, "A", spec(30))
        saves = self.repo.saves
        self.assertEqual(list_rules(self.repo), list_rules(self.repo))
        self.assertEqual(saves, self.repo.saves)

    def test_a_new_installation_lists_no_rule(self):
        self.assertEqual([], list_rules(self.repo))

    def test_any_role_needs_no_role_to_list(self):
        add_rule(self.repo, M, "A", spec(30))
        self.assertEqual(1, len(list_rules(self.repo)))


class RefusedAdditions(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRuleRepository()
        add_rule(self.repo, M, "Short stay", spec(30, 365))
        self.before = list_rules(self.repo)

    def refused(self, error, name, rule_spec):
        with self.assertRaises(error):
            add_rule(self.repo, M, name, rule_spec)
        self.assertEqual(self.before, list_rules(self.repo))

    def test_a_rule_with_neither_bound_is_refused(self):
        for parameter in (None, {}, bounds(None, None)):
            self.refused(refusals.NoBoundRefused, "X", RuleSpec(KIND, parameter))

    def test_zero_negative_or_non_whole_days_are_refused(self):
        for value in (0, -3, 1.5, 30.0, "30", True, False, [30]):
            self.refused(refusals.InvalidDaysRefused, "X", RuleSpec(KIND, bounds(value, None)))
            self.refused(refusals.InvalidDaysRefused, "X", RuleSpec(KIND, bounds(None, value)))

    def test_a_valid_bound_does_not_excuse_an_invalid_other_one(self):
        self.refused(refusals.InvalidDaysRefused, "X", spec(30, 0))
        self.refused(refusals.InvalidDaysRefused, "X", spec(0, 30))

    def test_a_minimum_above_the_maximum_is_refused(self):
        self.refused(refusals.MinimumAboveMaximumRefused, "X", spec(31, 30))

    def test_another_key_or_a_non_mapping_is_an_invalid_parameter(self):
        for parameter in ({"minimum": 3, "other": 1}, {"min": 3}, "30", 30, [30]):
            self.refused(refusals.InvalidParameterRefused, "X", RuleSpec(KIND, parameter))

    def test_a_blank_or_missing_name_is_refused(self):
        for name in ("", "   ", None, 7):
            self.refused(refusals.BlankValueRefused, name, spec(30))

    def test_a_name_equal_ignoring_case_and_spaces_is_refused(self):
        self.refused(refusals.DuplicateRuleRefused, " short STAY ", spec(10))
        self.refused(refusals.DuplicateRuleRefused, "Short stay", spec(30, 365))

    def test_an_unknown_or_missing_kind_is_refused(self):
        for kind in ("owner_consent_required", "Duration_Bounds", "", None, 3, ["x"]):
            self.refused(refusals.UnknownKindRefused, "X", RuleSpec(kind, bounds(30)))

    def test_a_non_text_note_is_refused_as_a_blank_value(self):
        self.refused(refusals.BlankValueRefused, "X", RuleSpec(KIND, bounds(30), 5))

    def test_the_check_order_is_blank_name_then_kind_then_parameter_then_duplicate(self):
        bad = RuleSpec("nope", {"x": 1})
        self.refused(refusals.BlankValueRefused, " ", bad)
        self.refused(refusals.UnknownKindRefused, "Short stay", bad)
        self.refused(refusals.InvalidParameterRefused, "Short stay", RuleSpec(KIND, {"x": 1}))
        self.refused(refusals.NoBoundRefused, "Short stay", RuleSpec(KIND, None))

    def test_adding_the_same_rule_twice_refuses_the_second(self):
        add_rule(self.repo, M, "Long stay", spec(None, 90))
        with self.assertRaises(refusals.DuplicateRuleRefused):
            add_rule(self.repo, M, "Long stay", spec(None, 90))
        self.assertEqual(2, len(list_rules(self.repo)))


class ChangedRules(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRuleRepository()
        add_rule(self.repo, M, "Short stay", spec(30, 365, "Bylaws art. 3"))

    def only(self):
        (entry,) = list_rules(self.repo)
        return entry

    def test_a_given_parameter_replaces_the_whole_one(self):
        change_rule(self.repo, M, "Short stay", RuleChange(parameter=bounds(None, 200)))
        self.assertEqual(bounds(None, 200), self.only().parameter)

    def test_a_missing_parameter_keeps_it(self):
        change_rule(self.repo, M, "Short stay", RuleChange(note="Other"))
        self.assertEqual(bounds(30, 365), self.only().parameter)

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

    def test_a_same_value_change_is_accepted(self):
        before = list_rules(self.repo)
        change_rule(self.repo, M, "Short stay", RuleChange(parameter=bounds(30, 365)))
        self.assertEqual(before, list_rules(self.repo))

    def test_a_change_with_nothing_to_change_is_accepted_and_changes_nothing(self):
        before = list_rules(self.repo)
        change_rule(self.repo, M, "Short stay", RuleChange())
        self.assertEqual(before, list_rules(self.repo))

    def test_an_invalid_new_parameter_is_refused_as_on_addition(self):
        before = list_rules(self.repo)
        for parameter, error in ((bounds(None, None), refusals.NoBoundRefused),
                                 ({}, refusals.NoBoundRefused),
                                 (bounds(0, None), refusals.InvalidDaysRefused),
                                 (bounds("3", None), refusals.InvalidDaysRefused),
                                 (bounds(9, 3), refusals.MinimumAboveMaximumRefused),
                                 ({"x": 1}, refusals.InvalidParameterRefused),
                                 ("30", refusals.InvalidParameterRefused)):
            with self.assertRaises(error):
                change_rule(self.repo, M, "Short stay", RuleChange(parameter=parameter))
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
    def setUp(self):
        self.repo = InMemoryRuleRepository()
        add_rule(self.repo, M, "Short stay", spec(30))
        self.before = list_rules(self.repo)
        self.loads = self.repo.loads
        self.saves = self.repo.saves

    def test_any_other_role_is_refused_first_with_nothing_read_or_written(self):
        for role in (Role.OWNER, Role.RESIDENT, None, "manager", 1):
            for call in (lambda: add_rule(self.repo, role, " ", RuleSpec("nope", {"x": 1})),
                         lambda: add_rule(self.repo, role, "Short stay", spec(30)),
                         lambda: change_rule(self.repo, role, "Z9", RuleChange(parameter={})),
                         lambda: change_rule(self.repo, role, "Short stay", RuleChange(note="x")),
                         lambda: remove_rule(self.repo, role, "Z9"),
                         lambda: remove_rule(self.repo, role, "Short stay")):
                with self.assertRaises(refusals.ManagerOnly):
                    call()
                self.assertEqual((self.loads, self.saves), (self.repo.loads, self.repo.saves))
                self.assertEqual(self.before, list_rules(self.repo))
                self.loads = self.repo.loads

    def test_a_successful_write_loads_then_saves_once(self):
        add_rule(self.repo, M, "Other", spec(30))
        self.assertEqual((self.loads + 1, self.saves + 1), (self.repo.loads, self.repo.saves))

    def test_a_refusal_never_saves(self):
        with self.assertRaises(refusals.DuplicateRuleRefused):
            add_rule(self.repo, M, "Short stay", spec(30))
        with self.assertRaises(refusals.UnknownRuleRefused):
            remove_rule(self.repo, M, "Z9")
        with self.assertRaises(refusals.UnknownRuleRefused):
            change_rule(self.repo, M, "Z9", RuleChange())
        self.assertEqual(self.saves, self.repo.saves)
