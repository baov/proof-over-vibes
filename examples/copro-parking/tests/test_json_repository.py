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
                                                       offer_space,
                                                       withdraw_offer)
from copro_parking.application.role import Role
from copro_parking.application.use_cases import (change_lot_owner,
                                                 change_space_number,
                                                 list_register, register_lot,
                                                 register_space, remove_space)
from copro_parking.infrastructure.wiring import (json_offer_repository,
                                                 json_repository, offer_check,
                                                 rental_check)
from fakes import FixedClock, StubOffers, StubRentals

M = Role.MANAGER
TODAY = date(2026, 11, 11)


class JsonRegister(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "register.json"
        self.repo = json_repository(self.path)
        self.offers_path = self.folder / "offers.json"
        self.offers = json_offer_repository(self.offers_path)
        self.clock = FixedClock(TODAY)
        self.check = offer_check(self.offers, self.clock)

    def seed(self):
        register_lot(self.repo, M, "A12", "Durand")
        register_lot(self.repo, M, "B1", "Martin")
        register_space(self.repo, M, "P1", "A12")
        register_space(self.repo, M, "P2", "B1")

    def offer(self, space="P1", offerer="Durand"):
        offer_space(self.repo, self.offers, self.clock, Role.OWNER,
                    OfferRequest(space, offerer, "2026-11-20", "2026-11-25"))

    def reread(self):
        return [(e.identifier, e.owner, e.spaces)
                for e in list_register(json_repository(self.path))]

    def test_entries_corrections_and_removals_survive_a_re_read_from_the_same_file(self):
        repo = json_repository(self.path)
        register_lot(repo, M, "B2", "Martin")
        register_lot(repo, M, " a1 ", "Durand")
        register_space(repo, M, "P2", "A1")
        register_space(repo, M, "P1", "A1")
        register_space(repo, M, "P3", "B2")
        self.assertEqual(list_register(repo), list_register(json_repository(self.path)))
        self.assertEqual([("a1", "Durand", ("P1", "P2")), ("B2", "Martin", ("P3",))], self.reread())
        change_lot_owner(repo, M, "b2", " Dupont ")
        change_space_number(repo, self.check, M, "p1", " P9 ")
        remove_space(repo, rental_check(), self.check, M, " p3 ")
        self.assertEqual([("a1", "Durand", ("P2", "P9")), ("B2", "Dupont", ())], self.reread())

    def test_a_missing_or_empty_file_is_an_empty_register(self):
        self.assertEqual([], list_register(json_repository(self.path)))
        self.path.write_text("  ", encoding="utf-8")
        self.assertEqual([], list_register(json_repository(self.path)))

    def test_a_refusal_leaves_the_file_identical_or_uncreated(self):
        with self.assertRaises(refusals.Refusal):
            register_lot(self.repo, Role.OWNER, "A12", "Durand")
        self.assertFalse(self.path.exists())
        self.seed()
        self.offer()
        files = lambda: (self.path.read_bytes(), self.offers_path.read_bytes())
        before = files()
        rented = StubRentals("P2")
        for call in (lambda: register_lot(self.repo, M, " a12 ", "X"),
                     lambda: register_lot(self.repo, M, "B3", " "),
                     lambda: register_space(self.repo, M, "P1", "Z9"),
                     lambda: change_lot_owner(self.repo, M, "Z9", "X"),
                     lambda: change_lot_owner(self.repo, Role.OWNER, "A12", "X"),
                     lambda: change_space_number(self.repo, self.check, M, "P2", " p1 "),
                     lambda: change_space_number(self.repo, self.check, M, "P1", "P9"),
                     lambda: remove_space(self.repo, rental_check(), self.check, M, " p1 "),
                     lambda: remove_space(self.repo, rented, self.check, M, "P2"),
                     lambda: remove_space(self.repo, rented, self.check, M, " p7 "),
                     lambda: remove_space(self.repo, rented, self.check, Role.OWNER, "P2")):
            with self.assertRaises(refusals.Refusal):
                call()
            self.assertEqual(before, files())

    def test_a_failed_write_leaves_the_previous_file_intact_and_no_leftover(self):
        register_lot(self.repo, M, "A12", "Durand")
        before = self.path.read_bytes()
        with mock.patch("os.replace", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                register_lot(self.repo, M, "B1", "Martin")
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(["register.json"], os.listdir(self.folder))
        self.assertEqual(["A12"], [e.identifier for e in list_register(self.repo)])

    def test_the_file_is_one_json_document(self):
        register_lot(self.repo, M, "A12", "Durand")
        self.assertEqual({"lots": [{"identifier": "A12", "owner": "Durand"}],
                          "spaces": []}, json.loads(self.path.read_text()))

    def test_unreadable_offers_stop_a_renumbering_and_a_removal_and_both_files_stay_identical(self):
        self.seed()
        self.offer()
        for text in ("not json {", '{"next_number": 1, "offers": [{"number": 1}]}'):
            self.offers_path.write_text(text, encoding="utf-8")
            for call in (lambda: change_space_number(self.repo, self.check, M, "P1", "P9"),
                         lambda: remove_space(self.repo, rental_check(), self.check, M, "P1")):
                before = self.path.read_bytes()
                with self.assertRaises(refusals.OffersUnreadable):
                    call()
                self.assertEqual(before, self.path.read_bytes())
                self.assertEqual(text, self.offers_path.read_text(encoding="utf-8"))

    def test_a_renumbering_or_a_removal_allowed_by_a_withdrawal_survives_a_restart(self):
        self.seed()
        self.offer()
        self.offer("P2", "Martin")
        for offerer, number in (("Durand", 1), ("Martin", 2)):
            withdraw_offer(self.repo, self.offers, self.clock, Role.OWNER,
                           WithdrawRequest(offerer, number))
        change_space_number(self.repo, self.check, M, "P1", "P9")
        remove_space(self.repo, rental_check(), self.check, M, "P2")
        self.assertEqual([("A12", "Durand", ("P9",)), ("B1", "Martin", ())], self.reread())


class CorruptStore(unittest.TestCase):
    BAD = ("not json {", "[]", '"text"', '{"lots": null}', '{"lots": "A12"}',
           '{"lots": [{"identifier": "A12"}]}',
           '{"lots": [{"identifier": "A12", "owner": 7}]}',
           '{"lots": [{"identifier": "A12", "owner": "  "}]}',
           '{"lots": [{"identifier": "A12", "owner": "D"}, '
           '{"identifier": "a12", "owner": "E"}]}',
           '{"lots": [], "spaces": [{"number": "P1", "lot": "Z9"}]}',
           '{"lots": [], "spaces": [3]}')

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "register.json"
        self.repo = json_repository(self.path)

    def test_a_corrupt_store_is_reported_on_read_and_on_every_write_and_never_overwritten(self):
        for text in self.BAD:
            self.path.write_text(text, encoding="utf-8")
            for call in (lambda: list_register(self.repo),
                         lambda: register_lot(self.repo, M, "B1", "X"),
                         lambda: register_space(self.repo, M, "P1", "A12"),
                         lambda: change_lot_owner(self.repo, M, "A12", "X"),
                         lambda: change_space_number(self.repo, StubOffers(), M, "P1", "P2"),
                         lambda: remove_space(self.repo, rental_check(), StubOffers(), M, "P1")):
                with self.assertRaises(refusals.StoreUnreadable, msg=text):
                    call()
                self.assertEqual(text, self.path.read_text(encoding="utf-8"))

    def test_a_file_that_is_not_text_is_reported_as_unreadable_not_as_a_refusal(self):
        self.path.write_bytes(b"\xff\xfe\x00")
        with self.assertRaises(refusals.StoreUnreadable) as caught:
            list_register(self.repo)
        self.assertNotIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(b"\xff\xfe\x00", self.path.read_bytes())

    def test_a_valid_store_with_only_lots_or_only_spaces_still_reads(self):
        self.path.write_text('{"lots": [{"identifier": "A1", "owner": "D"}]}')
        self.assertEqual(["A1"], [e.identifier for e in list_register(self.repo)])
        self.path.write_text("{}")
        self.assertEqual([], list_register(self.repo))
