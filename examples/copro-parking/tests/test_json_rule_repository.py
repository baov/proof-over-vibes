import bootstrap  # noqa: F401  (must come first)
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from copro_parking.application import refusals
from copro_parking.application.role import Role
from copro_parking.application.rule_use_cases import (RuleChange, RuleSpec,
                                                      add_rule, change_rule,
                                                      list_rules, remove_rule)
from copro_parking.infrastructure.wiring import json_rule_repository

M = Role.MANAGER
KIND = "duration_bounds"


def spec(minimum=None, maximum=None, note=None):
    return RuleSpec(KIND, {"minimum": minimum, "maximum": maximum}, note)


class JsonRules(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "rules.json"
        self.repo = json_rule_repository(self.path)

    def test_rules_survive_a_re_read_after_add_change_and_remove(self):
        add_rule(self.repo, M, "b", spec(30))
        add_rule(self.repo, M, "a01", spec(None, 90, "Art. 1"))
        add_rule(self.repo, M, "A1", spec(5))
        add_rule(self.repo, M, "gone", spec(5))
        change_rule(self.repo, M, "a01", RuleChange({"minimum": 2}, " new "))
        remove_rule(self.repo, M, "gone")
        again = json_rule_repository(self.path)
        self.assertEqual(list_rules(self.repo), list_rules(again))
        self.assertEqual(["a01", "A1", "b"], [e.name for e in list_rules(again)])
        self.assertEqual(({"minimum": 2, "maximum": None}, "new"),
                         (list_rules(again)[0].parameter, list_rules(again)[0].note))

    def test_a_missing_or_blank_file_lists_nothing_and_is_not_created_by_reading(self):
        self.assertEqual([], list_rules(self.repo))
        self.assertFalse(self.path.exists())
        for text in ("", "  \n"):
            self.path.write_text(text, encoding="utf-8")
            self.assertEqual([], list_rules(self.repo))

    def test_the_first_successful_write_creates_the_file_and_the_file_keeps_the_registration_order(self):
        add_rule(self.repo, M, "Short stay", spec(30, None, "n"))
        self.assertEqual(
            {"rules": [{"name": "Short stay", "kind": KIND,
                        "parameter": {"minimum": 30, "maximum": None}, "note": "n"}]},
            json.loads(self.path.read_text(encoding="utf-8")))
        add_rule(self.repo, M, "a", spec(1))  # registration order kept, a missing note stored as null
        document = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(["Short stay", "a"], [r["name"] for r in document["rules"]])
        self.assertIsNone(document["rules"][1]["note"])

    def test_a_refusal_leaves_the_file_identical_or_uncreated(self):
        with self.assertRaises(refusals.Refusal):
            add_rule(self.repo, Role.OWNER, "X", spec(1))
        with self.assertRaises(refusals.Refusal):
            remove_rule(self.repo, M, "X")
        self.assertFalse(self.path.exists())
        add_rule(self.repo, M, "Short stay", spec(30))
        before = self.path.read_bytes()
        for call in (lambda: add_rule(self.repo, M, " short stay ", spec(1)),
                     lambda: add_rule(self.repo, M, "X", spec()),
                     lambda: add_rule(self.repo, Role.OWNER, "X", spec(1)),
                     lambda: change_rule(self.repo, M, "Z9", RuleChange()),
                     lambda: change_rule(self.repo, M, "Short stay", RuleChange({"minimum": 0})),
                     lambda: change_rule(self.repo, Role.RESIDENT, "Short stay", RuleChange()),
                     lambda: remove_rule(self.repo, M, "Z9"),
                     lambda: remove_rule(self.repo, None, "Short stay")):
            with self.assertRaises(refusals.Refusal):
                call()
            self.assertEqual(before, self.path.read_bytes())

    def test_a_failed_write_leaves_the_previous_file_intact_and_no_leftover(self):
        add_rule(self.repo, M, "A", spec(1))
        before = self.path.read_bytes()
        with mock.patch("os.replace", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                add_rule(self.repo, M, "B", spec(1))
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(["rules.json"], os.listdir(self.folder))
        self.assertEqual(["A"], [e.name for e in list_rules(self.repo)])


class UnreadableRules(unittest.TestCase):
    GOOD = {"name": "A", "kind": KIND, "parameter": {"minimum": 3, "maximum": None},
            "note": None}
    BAD = ("not json {", "[]", '"text"', '{"rules": null}', '{"rules": "A"}',
           '{"rules": [3]}', '{"rules": {"name": "A"}}',
           json.dumps({"rules": [{k: v for k, v in GOOD.items() if k != "name"}]}),
           json.dumps({"rules": [{k: v for k, v in GOOD.items() if k != "kind"}]}),
           json.dumps({"rules": [{k: v for k, v in GOOD.items() if k != "parameter"}]}),
           json.dumps({"rules": [{k: v for k, v in GOOD.items() if k != "note"}]}),
           json.dumps({"rules": [dict(GOOD, name="  ")]}),
           json.dumps({"rules": [dict(GOOD, name=7)]}),
           json.dumps({"rules": [dict(GOOD, kind="mystery")]}),
           json.dumps({"rules": [dict(GOOD, parameter={"minimum": 0, "maximum": None})]}),
           json.dumps({"rules": [dict(GOOD, parameter={"minimum": None, "maximum": None})]}),
           json.dumps({"rules": [dict(GOOD, parameter={"minimum": 9, "maximum": 3})]}),
           json.dumps({"rules": [dict(GOOD, parameter={"minimum": 3, "x": 1})]}),
           json.dumps({"rules": [dict(GOOD, parameter="3")]}),
           json.dumps({"rules": [dict(GOOD, note=5)]}),
           json.dumps({"rules": [GOOD, dict(GOOD, name=" a ")]}))

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "rules.json"
        self.repo = json_rule_repository(self.path)

    def test_unreadable_rules_are_reported_on_read_and_every_write_and_never_overwritten(self):
        for text in self.BAD:
            self.path.write_text(text, encoding="utf-8")
            for call in (lambda: list_rules(self.repo),
                         lambda: add_rule(self.repo, M, "B", spec(1)),
                         lambda: change_rule(self.repo, M, "A", RuleChange({"minimum": 2})),
                         lambda: remove_rule(self.repo, M, "A")):
                with self.assertRaises(refusals.RulesUnreadable, msg=text):
                    call()
                self.assertEqual(text, self.path.read_text(encoding="utf-8"))

    def test_a_file_that_is_not_text_is_reported_as_unreadable_not_as_a_refusal(self):
        self.path.write_bytes(b"\xff\xfe\x00")
        with self.assertRaises(refusals.StoreUnreadable) as caught:
            list_rules(self.repo)
        self.assertNotIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(b"\xff\xfe\x00", self.path.read_bytes())

    def test_the_role_comes_before_the_store_and_the_store_before_any_value_error(self):
        self.path.write_text("not json", encoding="utf-8")
        with self.assertRaises(refusals.ManagerOnly):
            add_rule(self.repo, Role.OWNER, "B", spec(1))
        with self.assertRaises(refusals.RulesUnreadable):
            add_rule(self.repo, M, " ", spec())
        with self.assertRaises(refusals.RulesUnreadable):
            change_rule(self.repo, M, "Z9", RuleChange({"x": 1}))
        with self.assertRaises(refusals.RulesUnreadable):
            remove_rule(self.repo, M, "Z9")

    def test_a_valid_file_with_no_rules_key_or_a_null_note_still_reads(self):
        self.path.write_text("{}", encoding="utf-8")
        self.assertEqual([], list_rules(self.repo))
        self.path.write_text(json.dumps({"rules": [self.GOOD]}), encoding="utf-8")
        self.assertEqual(["A"], [e.name for e in list_rules(self.repo)])
