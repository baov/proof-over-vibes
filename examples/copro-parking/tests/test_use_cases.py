import bootstrap  # noqa: F401  (must come first)
import unittest

from copro_parking.application import refusals
from copro_parking.application.role import Role
from copro_parking.application.use_cases import (LotEntry, change_lot_owner,
                                                 change_space_number,
                                                 list_register, register_lot,
                                                 register_space, remove_space)
from copro_parking.infrastructure.wiring import rental_check
from fakes import FailingOffers, InMemoryRepository, StubOffers, StubRentals

M = Role.MANAGER
BLANKS = (None, "", "   ")


class RegisterLotsAndSpaces(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()

    def test_the_manager_registers_a_lot_with_its_owner(self):
        register_lot(self.repo, M, "A12", "Durand")
        self.assertEqual([LotEntry("A12", "Durand", ())], list_register(self.repo))

    def test_the_manager_registers_a_space_under_an_existing_lot(self):
        register_lot(self.repo, M, "A12", "Durand")
        register_space(self.repo, M, "P1", "A12")
        self.assertEqual([LotEntry("A12", "Durand", ("P1",))], list_register(self.repo))

    def test_listing_shows_the_trimmed_text_as_typed_case_kept(self):
        register_lot(self.repo, M, " a12 ", " Durand ")
        register_space(self.repo, M, " p1 ", "A12")
        self.assertEqual([LotEntry("a12", "Durand", ("p1",))], list_register(self.repo))

    def test_listing_is_sorted_and_keeps_lots_without_space(self):
        self.assertEqual([], list_register(self.repo))
        register_lot(self.repo, M, "B2", "Martin")
        register_lot(self.repo, M, "A1", "Durand")
        register_space(self.repo, M, "P2", "A1")
        register_space(self.repo, M, "P1", "A1")
        self.assertEqual([LotEntry("A1", "Durand", ("P1", "P2")),
                          LotEntry("B2", "Martin", ())], list_register(self.repo))

    def test_listing_orders_numbers_naturally_whatever_the_registration_order(self):
        for identifier in ("A10", "a2"):
            register_lot(self.repo, M, identifier, "X")
        for number in ("P10", "p2"):
            register_space(self.repo, M, number, "a2")
        entries = list_register(self.repo)
        self.assertEqual(["a2", "A10"], [e.identifier for e in entries])
        self.assertEqual(("p2", "P10"), entries[0].spaces)

    def test_an_identifier_or_number_with_a_superscript_digit_registers_and_lists(self):
        for identifier in ("P1\u00b2", "\u00b2", "P2"):
            register_lot(self.repo, M, identifier, "X")
        register_space(self.repo, M, "S1\u00b2", "P2")
        register_space(self.repo, M, "S1", "P2")
        entries = list_register(self.repo)
        self.assertEqual({"P1\u00b2", "\u00b2", "P2"}, {e.identifier for e in entries})
        self.assertEqual(("S1", "S1\u00b2"), next(e for e in entries if e.identifier == "P2").spaces)


class RulesSharedByEveryUseCase(unittest.TestCase):
    """Rules of the register applied by every use case, tested once over a table of them.

    The offers are never readable here: a refusal reported anyway was reported before they were asked.
    """

    def setUp(self):
        self.repo = InMemoryRepository()
        self.offers = FailingOffers(RuntimeError("the offers must not be asked"))
        self.rentals = StubRentals()
        register_lot(self.repo, M, "A12", "Durand")
        register_lot(self.repo, M, "B1", "Martin")
        register_space(self.repo, M, "P1", "A12")
        register_space(self.repo, M, "P2", "B1")
        self.before = list_register(self.repo)
        # use case -> call(role, first, second); the arguments are the ones the use case takes
        self.use_cases = {
            "register_lot": lambda role, a, b: register_lot(self.repo, role, a, b),
            "register_space": lambda role, a, b: register_space(self.repo, role, a, b),
            "change_lot_owner": lambda role, a, b: change_lot_owner(self.repo, role, a, b),
            "change_space_number": lambda role, a, b: change_space_number(
                self.repo, self.offers, role, a, b),
            "remove_space": lambda role, a, b: remove_space(
                self.repo, self.rentals, self.offers, role, a)}
        self.blank = [(name, args) for blank in BLANKS for name, args in (
            ("register_lot", (blank, "Martin")), ("register_lot", ("B3", blank)),
            ("register_space", (blank, "A12")), ("change_lot_owner", ("A12", blank)),
            ("change_space_number", ("P1", blank)), ("remove_space", (blank, None)))]
        self.unknown = [("register_space", ("P9", "Z9"), refusals.UnknownLotRefused),
                        ("change_lot_owner", ("Z9", "X"), refusals.UnknownLotRefused),
                        ("change_space_number", ("P7", "P8"), refusals.UnknownSpaceRefused),
                        ("remove_space", ("P7", None), refusals.UnknownSpaceRefused)]
        self.duplicate = [("register_lot", (" a12 ", "Martin"), refusals.DuplicateLotRefused),
                          ("register_space", (" p1 ", "B1"), refusals.DuplicateSpaceRefused),
                          ("change_space_number", ("P2", " p1 "), refusals.DuplicateSpaceRefused)]

    def assert_refused(self, error, name, role, args):
        with self.assertRaises(error) as caught:
            self.use_cases[name](role, *args)
        self.assertIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(self.before, list_register(self.repo))

    def test_a_blank_value_is_refused_as_blank(self):
        for name, args in self.blank:
            with self.subTest(use_case=name, args=args):
                self.assert_refused(refusals.BlankValueRefused, name, M, args)

    def test_an_unknown_lot_or_space_is_refused(self):
        for name, args, error in self.unknown:
            with self.subTest(use_case=name):
                self.assert_refused(error, name, M, args)

    def test_a_number_or_identifier_already_used_is_refused_on_any_lot(self):
        for name, args, error in self.duplicate:
            with self.subTest(use_case=name):
                self.assert_refused(error, name, M, args)

    def test_any_other_role_is_refused_first_whatever_the_request(self):
        valid = {"register_lot": ("B3", "Y"), "register_space": ("P9", "A12"),
                 "change_lot_owner": ("A12", "X"), "change_space_number": ("P1", "P9"),
                 "remove_space": ("P1", None)}
        refused = [(name, args) for name, args in self.blank]
        refused += [(name, args) for name, args, _ in self.unknown + self.duplicate]
        refused += list(valid.items())
        for role in (Role.OWNER, Role.RESIDENT, None, "manager"):
            for name, args in refused:
                with self.subTest(role=role, use_case=name, args=args):
                    self.assert_refused(refusals.ManagerOnly, name, role, args)

    def test_an_offers_check_that_cannot_answer_stops_the_renumbering_and_the_removal(self):
        for error in (refusals.OffersUnreadable("offers"), RuntimeError("boom")):
            for call in (lambda: change_space_number(self.repo, FailingOffers(error), M, "P1", "P9"),
                         lambda: remove_space(self.repo, self.rentals, FailingOffers(error), M, "P1")):
                with self.subTest(error=error):
                    with self.assertRaises(type(error)):
                        call()
                    self.assertEqual(self.before, list_register(self.repo))


class Corrections(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()
        self.offers = StubOffers()
        register_lot(self.repo, M, "A12", "Durand")
        register_lot(self.repo, M, "B1", "Martin")
        register_space(self.repo, M, "P1", "A12")
        register_space(self.repo, M, "P2", "B1")

    def test_the_manager_changes_the_owner_keeping_the_spaces(self):
        change_lot_owner(self.repo, M, " a12 ", " Martin ")
        self.assertEqual([LotEntry("A12", "Martin", ("P1",)),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))

    def test_the_manager_changes_a_space_number_keeping_its_lot(self):
        change_space_number(self.repo, self.offers, M, " p1 ", " P9 ")
        self.assertEqual([LotEntry("A12", "Durand", ("P9",)),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))

    def test_a_same_value_correction_is_accepted_and_stores_the_new_text(self):
        change_lot_owner(self.repo, M, "A12", " Durand ")
        change_space_number(self.repo, self.offers, M, "P1", "p1")
        self.assertEqual([LotEntry("A12", "Durand", ("p1",)),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))


class Removal(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()
        self.rentals = StubRentals()
        self.offers = StubOffers()
        register_lot(self.repo, M, "A12", "Durand")
        register_lot(self.repo, M, "B1", "Martin")
        register_space(self.repo, M, "P1", "A12")
        register_space(self.repo, M, "P2", "B1")

    def remove(self, number, rentals=None):
        return remove_space(self.repo, rentals or self.rentals, self.offers, M, number)

    def test_the_manager_removes_a_space_found_ignoring_case_and_spaces_and_never_its_lot(self):
        self.assertIsNone(self.remove(" p1 "))
        self.assertEqual([LotEntry("A12", "Durand", ()),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))
        self.remove("P2")
        self.assertEqual([LotEntry("A12", "Durand", ()), LotEntry("B1", "Martin", ())],
                         list_register(self.repo))

    def test_a_removed_number_can_be_registered_again_on_any_lot(self):
        self.remove("P1")
        register_space(self.repo, M, "P1", "A12")
        self.remove("P1")
        register_space(self.repo, M, " p1 ", "B1")
        self.assertEqual([LotEntry("A12", "Durand", ()),
                          LotEntry("B1", "Martin", ("p1", "P2"))], list_register(self.repo))

    def test_an_unknown_space_is_refused_and_so_is_a_second_removal(self):
        with self.assertRaises(refusals.UnknownSpaceRefused):
            self.remove("P7")
        self.remove("P1")
        before = list_register(self.repo)
        with self.assertRaises(refusals.UnknownSpaceRefused):
            self.remove("P1")
        self.assertEqual(before, list_register(self.repo))

    def test_a_rented_space_is_refused_and_stays_listed(self):
        before = list_register(self.repo)
        with self.assertRaises(refusals.SpaceRentedRefused):
            self.remove(" p1 ", rentals=StubRentals("P1"))
        self.assertEqual(before, list_register(self.repo))

    def test_the_default_rental_check_answers_no_rental_and_never_blocks_a_removal(self):
        self.assertIs(False, rental_check().has_rental("P1"))
        self.remove("P1", rentals=rental_check())
        self.assertEqual(((), ("P2",)), tuple(e.spaces for e in list_register(self.repo)))
