import bootstrap  # noqa: F401  (must come first)
import json
import os
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from copro_parking.application import refusals
from copro_parking.application.offer_use_cases import (OfferRequest,
                                                       WithdrawRequest,
                                                       list_open_offers,
                                                       offer_space,
                                                       withdraw_offer)
from copro_parking.application.role import Role
from copro_parking.application.rule_use_cases import RuleSpec, add_rule
from copro_parking.application.use_cases import register_lot, register_space
from copro_parking.infrastructure.wiring import (json_offer_repository,
                                                 json_repository,
                                                 json_rule_repository,
                                                 system_clock)
from fakes import FixedClock

M = Role.MANAGER
O = Role.OWNER
TODAY = date(2026, 11, 11)
GOOD = {"number": 1, "space": "P1", "start": "2026-11-20", "end": "2026-11-25"}


def request(space="P1", offerer="Durand", start="2026-11-20", end="2026-11-25"):
    return OfferRequest(space, offerer, start, end)


class JsonOffers(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "offers.json"
        self.registers = json_repository(self.folder / "register.json")
        register_lot(self.registers, M, "A12", "Durand")
        register_space(self.registers, M, "P1", "A12")
        register_space(self.registers, M, "P2", "A12")
        self.offers = json_offer_repository(self.path)
        self.clock = FixedClock(TODAY)

    def offer(self, offers=None, role=O, **fields):
        return offer_space(self.registers, offers or self.offers, self.clock, role,
                           request(**fields))

    def listing(self, offers=None):
        return list_open_offers(self.registers, offers or self.offers, self.clock)

    def withdraw(self, offers=None, role=O, offerer="Durand", number=1):
        return withdraw_offer(self.registers, offers or self.offers, self.clock, role,
                              WithdrawRequest(offerer, number))

    def test_offers_survive_a_re_read_and_numbering_goes_on_after_a_restart(self):
        self.offer()
        self.offer(space="P2", start="2026-11-12")
        again = json_offer_repository(self.path)
        self.assertEqual(self.listing(), self.listing(again))
        self.assertEqual([2, 1], [e.number for e in self.listing(again)])
        self.assertEqual(3, self.offer(again, start="2026-12-01", end="2026-12-02").number)

    def test_the_first_successful_offer_creates_the_file_with_the_agreed_format(self):
        self.offer(space=" p1 ")
        self.assertEqual(
            {"next_number": 2, "offers": [GOOD]},
            json.loads(self.path.read_text(encoding="utf-8")))

    def test_an_offer_past_its_end_stays_in_the_file_and_numbers_are_not_reused(self):
        self.offer()
        self.clock.day = date(2026, 12, 1)
        self.assertEqual([], self.listing())
        self.assertEqual(2, self.offer(start="2026-12-02", end="2026-12-03").number)
        document = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual([1, 2], [o["number"] for o in document["offers"]])

    def test_offering_and_withdrawing_leave_the_register_file_and_the_rules_file_bytes_unchanged(self):
        rules = json_rule_repository(self.folder / "rules.json")
        add_rule(rules, M, "Short stay", RuleSpec("duration_bounds", {"minimum": 3}))
        register_path, rules_path = self.folder / "register.json", self.folder / "rules.json"
        before = (register_path.read_bytes(), rules_path.read_bytes())
        self.offer()
        self.listing()
        self.withdraw()
        self.assertEqual(before, (register_path.read_bytes(), rules_path.read_bytes()))

    def test_a_missing_or_blank_file_lists_nothing_and_is_not_created_by_reading(self):
        self.assertEqual([], self.listing())
        self.assertFalse(self.path.exists())
        for text in ("", "  \n", "{}"):
            self.path.write_text(text, encoding="utf-8")
            self.assertEqual([], self.listing())

    def test_a_refusal_leaves_the_file_identical_or_uncreated(self):
        for call in (lambda: self.offer(role=None),
                     lambda: self.offer(start="x"),
                     lambda: self.offer(space="P99"),
                     lambda: self.offer(offerer="Dupont"),
                     lambda: self.withdraw(number=1),
                     lambda: self.withdraw(role=None)):
            with self.assertRaises(refusals.Refusal):
                call()
        self.assertFalse(self.path.exists())
        self.offer()
        before = self.path.read_bytes()
        for call in (lambda: self.offer(role=Role.RESIDENT),
                     lambda: self.offer(end="2026-11-01"),
                     lambda: self.offer(space="P99"),
                     lambda: self.offer(offerer="Dupont"),
                     lambda: self.offer(offerer=" "),
                     lambda: self.offer(start="2026-11-22", end="2026-11-23"),
                     lambda: self.withdraw(role=Role.RESIDENT),
                     lambda: self.withdraw(number=0),
                     lambda: self.withdraw(offerer=" "),
                     lambda: self.withdraw(number=2),
                     lambda: self.withdraw(offerer="Dupont")):
            with self.assertRaises(refusals.Refusal):
                call()
            self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(2, self.offer(space="P2").number)

    def test_a_failed_write_leaves_the_previous_file_intact_and_no_leftover(self):
        self.offer()
        before = self.path.read_bytes()
        with mock.patch("os.replace", side_effect=OSError("disk")):
            for call in (lambda: self.offer(space="P2"), self.withdraw):
                with self.assertRaises(OSError):
                    call()
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(["offers.json", "register.json"], sorted(os.listdir(self.folder)))
        self.assertEqual(1, len(self.listing()))

    def test_a_stored_pair_of_overlapping_offers_loads_and_only_new_offers_are_checked(self):
        pair = [dict(GOOD), dict(GOOD, number=2, start="2026-11-22", end="2026-11-28")]
        self.path.write_text(json.dumps({"next_number": 3, "offers": pair}), encoding="utf-8")
        self.assertEqual([1, 2], [e.number for e in self.listing()])
        self.assertEqual(3, self.offer(start="2026-12-01", end="2026-12-02").number)
        with self.assertRaises(refusals.OverlapRefused) as caught:
            self.offer(start="2026-11-23", end="2026-11-24")
        self.assertEqual(1, caught.exception.offer_number)

    def test_a_withdrawal_survives_a_re_read_and_the_next_number_is_kept(self):
        self.offer()
        self.offer(space="P2", start="2026-11-12")
        self.withdraw(number=1)
        again = json_offer_repository(self.path)
        self.assertEqual([2], [e.number for e in self.listing(again)])
        document = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(3, document["next_number"])
        self.assertEqual([2], [o["number"] for o in document["offers"]])
        self.assertEqual(3, self.offer(again, start="2026-12-01", end="2026-12-02").number)
        self.withdraw(number=2)
        self.withdraw(number=3)
        self.assertEqual({"next_number": 4, "offers": []},
                         json.loads(self.path.read_text(encoding="utf-8")))

    def test_a_withdrawal_keeps_the_expired_offers_and_the_other_open_ones_in_the_file(self):
        self.offer(space="P2", start="2026-11-12", end="2026-11-13")
        self.offer()
        self.offer(start="2026-12-01", end="2026-12-02")
        self.clock.day = date(2026, 11, 14)
        self.withdraw(number=2)
        document = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual([1, 3], [o["number"] for o in document["offers"]])
        self.assertEqual(4, document["next_number"])
        self.assertEqual([3], [e.number for e in self.listing()])

    def test_a_stored_pair_is_listed_by_number_and_a_withdrawal_repairs_it(self):
        pair = [dict(GOOD, number=2, end="2026-11-24"), dict(GOOD, end="2026-11-22")]
        self.path.write_text(json.dumps({"next_number": 3, "offers": pair}), encoding="utf-8")
        self.assertEqual([1, 2], [e.number for e in self.listing()])
        self.withdraw(number=2)
        self.assertEqual([1], [e.number for e in self.listing()])
        with self.assertRaises(refusals.OverlapRefused) as caught:
            self.offer(start="2026-11-21", end="2026-11-22")
        self.assertEqual(1, caught.exception.offer_number)
        self.assertEqual(3, self.offer(start="2026-11-23", end="2026-11-24").number)
        self.withdraw(number=1)
        self.assertEqual([3], [e.number for e in self.listing()])
        self.assertEqual(4, self.offer(start="2026-11-20", end="2026-11-22").number)

    def test_the_system_clock_answers_a_date(self):
        today = system_clock().today()
        self.assertIs(date, type(today))


class UnreadableOffers(unittest.TestCase):
    NUMBER_MISSING = {k: v for k, v in GOOD.items() if k != "number"}

    @staticmethod
    def without(field):
        return json.dumps({"next_number": 2,
                           "offers": [{k: v for k, v in GOOD.items() if k != field}]})

    @staticmethod
    def with_(**changes):
        return json.dumps({"next_number": 2, "offers": [dict(GOOD, **changes)]})

    def bad_files(self):
        return ("not json {", "[]", '"text"', '{"offers": null}', '{"offers": "A"}',
                '{"next_number": 2, "offers": [3]}',
                '{"next_number": 2, "offers": {"number": 1}}',
                json.dumps({"next_number": "2", "offers": []}),
                json.dumps({"next_number": 0, "offers": []}),
                json.dumps({"next_number": -1, "offers": []}),
                json.dumps({"next_number": True, "offers": []}),
                json.dumps({"next_number": 1.5, "offers": []}),
                json.dumps({"next_number": None, "offers": []}),
                *(self.without(f) for f in GOOD),
                self.with_(number="1"), self.with_(number=True), self.with_(number=0),
                self.with_(number=1.0), self.with_(space="  "), self.with_(space=7),
                self.with_(start="2026-13-01"), self.with_(start=5),
                self.with_(start=None), self.with_(end="20261125"),
                self.with_(end="2026-11-19"),
                json.dumps({"next_number": 3, "offers": [GOOD, dict(GOOD, space="P2")]}),
                json.dumps({"next_number": 2, "offers": [GOOD, dict(GOOD, number=2)]}),
                json.dumps({"next_number": 1, "offers": [GOOD]}),
                json.dumps({"next_number": 2, "offers": [dict(GOOD, number=5)]}),
                json.dumps({"offers": [GOOD]}))

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "offers.json"
        self.repo = json_offer_repository(self.path)
        self.registers = json_repository(Path(folder.name) / "register.json")
        register_lot(self.registers, M, "A12", "Durand")
        register_space(self.registers, M, "P1", "A12")
        self.clock = FixedClock(TODAY)

    def calls(self):
        return (lambda: list_open_offers(self.registers, self.repo, self.clock),
                lambda: offer_space(self.registers, self.repo, self.clock, O,
                                    request(space="P1", start="2026-12-01", end="2026-12-02")),
                lambda: withdraw_offer(self.registers, self.repo, self.clock, O,
                                       WithdrawRequest("Durand", 1)))

    def test_unreadable_offers_are_reported_on_list_offer_and_withdrawal_and_never_overwritten(self):
        for text in self.bad_files():
            self.path.write_text(text, encoding="utf-8")
            for call in self.calls():
                with self.assertRaises(refusals.OffersUnreadable, msg=text):
                    call()
                self.assertEqual(text, self.path.read_text(encoding="utf-8"))

    def test_a_file_that_is_not_text_is_reported_as_unreadable_not_as_a_refusal(self):
        self.path.write_bytes(b"\xff\xfe\x00")
        for call in self.calls():
            with self.assertRaises(refusals.StoreUnreadable) as caught:
                call()
            self.assertNotIsInstance(caught.exception, refusals.Refusal)
            self.assertEqual(b"\xff\xfe\x00", self.path.read_bytes())

    def test_a_valid_file_reads_and_an_offer_in_the_past_is_still_readable(self):
        document = {"next_number": 3, "offers": [
            GOOD, dict(GOOD, number=2, space="P1", start="2020-01-01", end="2020-01-02")]}
        self.path.write_text(json.dumps(document), encoding="utf-8")
        self.assertEqual([1], [e.number for e in list_open_offers(
            self.registers, self.repo, self.clock)])
        self.assertEqual(3, offer_space(self.registers, self.repo, self.clock, O,
                                        request(start="2026-12-01", end="2026-12-02")).number)


if __name__ == "__main__":
    unittest.main()
