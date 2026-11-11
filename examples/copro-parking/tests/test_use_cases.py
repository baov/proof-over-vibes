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


class RegisterLotsAndSpaces(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()

    def test_the_manager_registers_a_lot_with_its_owner(self):
        register_lot(self.repo, M, "A12", "Durand")
        self.assertEqual([LotEntry("A12", "Durand", ())], list_register(self.repo))

    def test_listing_shows_the_trimmed_text_as_typed_case_kept(self):
        register_lot(self.repo, M, " a12 ", " Durand ")
        register_space(self.repo, M, " p1 ", "A12")
        self.assertEqual([LotEntry("a12", "Durand", ("p1",))], list_register(self.repo))

    def test_the_manager_registers_a_space_under_an_existing_lot(self):
        register_lot(self.repo, M, "A12", "Durand")
        register_space(self.repo, M, "P1", "A12")
        self.assertEqual([LotEntry("A12", "Durand", ("P1",))], list_register(self.repo))

    def test_listing_is_sorted_and_keeps_lots_without_space(self):
        register_lot(self.repo, M, "B2", "Martin")
        register_lot(self.repo, M, "A1", "Durand")
        register_space(self.repo, M, "P2", "A1")
        register_space(self.repo, M, "P1", "A1")
        self.assertEqual([LotEntry("A1", "Durand", ("P1", "P2")),
                          LotEntry("B2", "Martin", ())], list_register(self.repo))

    def test_an_empty_register_lists_nothing(self):
        self.assertEqual([], list_register(self.repo))


class Refusals(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()
        register_lot(self.repo, M, "A12", "Durand")
        register_space(self.repo, M, "P1", "A12")
        self.before = list_register(self.repo)

    def assert_refused(self, reason, call):
        with self.assertRaises(reason) as caught:
            call()
        self.assertIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(self.before, list_register(self.repo))

    def test_a_duplicate_lot_is_refused(self):
        self.assert_refused(refusals.DuplicateLotRefused,
                            lambda: register_lot(self.repo, M, " a12 ", "Martin"))

    def test_a_duplicate_space_is_refused_on_any_lot(self):
        register_lot(self.repo, M, "B1", "Martin")
        self.before = list_register(self.repo)
        self.assert_refused(refusals.DuplicateSpaceRefused,
                            lambda: register_space(self.repo, M, " p1 ", "B1"))

    def test_a_lot_without_owner_is_refused(self):
        for owner in (None, "", "   "):
            self.assert_refused(refusals.BlankValueRefused,
                                lambda: register_lot(self.repo, M, "B1", owner))

    def test_a_blank_lot_identifier_or_space_number_is_refused(self):
        for value in (None, "", "  "):
            self.assert_refused(refusals.BlankValueRefused,
                                lambda: register_lot(self.repo, M, value, "Martin"))
            self.assert_refused(refusals.BlankValueRefused,
                                lambda: register_space(self.repo, M, value, "A12"))

    def test_a_space_on_an_unknown_lot_is_refused(self):
        self.assert_refused(refusals.UnknownLotRefused,
                            lambda: register_space(self.repo, M, "P2", "Z9"))

    def test_any_other_role_is_refused_on_both_registrations(self):
        for role in (Role.OWNER, Role.RESIDENT):
            self.assert_refused(refusals.ManagerOnly,
                                lambda: register_lot(self.repo, role, "B1", "Martin"))
            self.assert_refused(refusals.ManagerOnly,
                                lambda: register_space(self.repo, role, "P2", "A12"))

    def test_a_missing_or_unknown_role_is_refused(self):
        self.assert_refused(refusals.ManagerOnly,
                            lambda: register_lot(self.repo, None, "B1", "Martin"))
        self.assert_refused(refusals.ManagerOnly,
                            lambda: register_space(self.repo, "manager", "P2", "A12"))

    def test_the_manager_only_refusal_wins_over_blank_and_duplicate(self):
        self.assert_refused(refusals.ManagerOnly,
                            lambda: register_lot(self.repo, Role.OWNER, "A12", ""))
        self.assert_refused(refusals.ManagerOnly,
                            lambda: register_space(self.repo, Role.OWNER, "P1", "Z9"))


class Corrections(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()
        self.offers = StubOffers()
        register_lot(self.repo, M, "A12", "Durand")
        register_lot(self.repo, M, "B1", "Martin")
        register_space(self.repo, M, "P1", "A12")
        register_space(self.repo, M, "P2", "B1")
        self.before = list_register(self.repo)

    def assert_refused(self, reason, call):
        with self.assertRaises(reason) as caught:
            call()
        self.assertIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(self.before, list_register(self.repo))

    def test_the_manager_changes_the_owner_keeping_the_spaces(self):
        change_lot_owner(self.repo, M, " a12 ", " Martin ")
        self.assertEqual([LotEntry("A12", "Martin", ("P1",)),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))

    def test_the_manager_changes_a_space_number_keeping_its_lot(self):
        change_space_number(self.repo, self.offers, M, " p1 ", " P9 ")
        self.assertEqual([LotEntry("A12", "Durand", ("P9",)),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))

    def test_a_corrected_space_is_listed_in_natural_order(self):
        change_space_number(self.repo, self.offers, M, "P1", "P10")
        register_space(self.repo, M, "p2x", "A12")
        self.assertEqual(("p2x", "P10"), list_register(self.repo)[0].spaces)

    def test_a_same_value_correction_is_accepted_and_stores_the_new_text(self):
        change_lot_owner(self.repo, M, "A12", " Durand ")
        change_space_number(self.repo, self.offers, M, "P1", "p1")
        self.assertEqual([LotEntry("A12", "Durand", ("p1",)),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))

    def test_a_new_number_already_used_is_refused(self):
        self.assert_refused(refusals.DuplicateSpaceRefused,
                            lambda: change_space_number(self.repo, self.offers, M, "P2", " p1 "))

    def test_a_blank_new_owner_or_number_is_refused(self):
        for value in (None, "", "   "):
            self.assert_refused(refusals.BlankValueRefused,
                                lambda: change_lot_owner(self.repo, M, "A12", value))
            self.assert_refused(refusals.BlankValueRefused,
                                lambda: change_space_number(self.repo, self.offers, M, "P1", value))

    def test_an_unknown_lot_or_space_is_refused(self):
        self.assert_refused(refusals.UnknownLotRefused,
                            lambda: change_lot_owner(self.repo, M, "Z9", "X"))
        self.assert_refused(refusals.UnknownSpaceRefused,
                            lambda: change_space_number(self.repo, self.offers, M, "P7", "P8"))

    def test_any_other_role_is_refused_on_both_corrections(self):
        for role in (Role.OWNER, Role.RESIDENT, None, "manager"):
            self.assert_refused(refusals.ManagerOnly,
                                lambda: change_lot_owner(self.repo, role, "A12", "X"))
            self.assert_refused(refusals.ManagerOnly,
                                lambda: change_space_number(self.repo, self.offers, role, "P1", "P9"))

    def test_the_manager_only_refusal_wins_over_blank_unknown_and_duplicate(self):
        self.assert_refused(refusals.ManagerOnly,
                            lambda: change_lot_owner(self.repo, Role.OWNER, "Z9", " "))
        self.assert_refused(refusals.ManagerOnly,
                            lambda: change_space_number(self.repo, self.offers, Role.OWNER, "P1", "p2"))
        self.assert_refused(refusals.ManagerOnly,
                            lambda: change_space_number(self.repo, self.offers, Role.OWNER, "P7", " "))

    def test_an_offered_space_is_refused_as_space_offered_even_for_a_same_value_change(self):
        offered = StubOffers("P1")
        for new_number in ("P9", "p1", " P1 "):
            self.assert_refused(refusals.SpaceOfferedRefused,
                                lambda: change_space_number(self.repo, offered, M, " p1 ",
                                                            new_number))
        self.assertEqual(["P1"] * 3, offered.asked)

    def test_a_space_without_an_offer_is_renumbered_while_another_one_is_offered(self):
        change_space_number(self.repo, StubOffers("P1"), M, "P2", "P7")
        self.assertEqual(("P7",), list_register(self.repo)[1].spaces)

    def test_the_register_refusals_come_before_space_offered_and_the_offers_are_not_asked(self):
        offered = StubOffers("P1", "P2")
        self.assert_refused(refusals.BlankValueRefused,
                            lambda: change_space_number(self.repo, offered, M, "P1", " "))
        self.assert_refused(refusals.BlankValueRefused,
                            lambda: change_space_number(self.repo, offered, M, "P7", None))
        self.assert_refused(refusals.UnknownSpaceRefused,
                            lambda: change_space_number(self.repo, offered, M, "P7", "P9"))
        self.assert_refused(refusals.DuplicateSpaceRefused,
                            lambda: change_space_number(self.repo, offered, M, "P1", " p2 "))
        self.assertEqual([], offered.asked)

    def test_any_other_role_is_refused_first_and_the_offers_are_not_asked(self):
        offered = StubOffers("P1")
        for role in (Role.OWNER, Role.RESIDENT, None, "manager"):
            self.assert_refused(refusals.ManagerOnly,
                                lambda: change_space_number(self.repo, offered, role, "P1", "P9"))
            self.assert_refused(
                refusals.ManagerOnly,
                lambda: change_space_number(self.repo, FailingOffers(RuntimeError()), role,
                                            "P7", " "))
        self.assertEqual([], offered.asked)

    def test_the_offers_are_asked_once_with_the_old_number_as_registered(self):
        offers = StubOffers()
        change_space_number(self.repo, offers, M, " p2 ", "P7")
        self.assertEqual(["P2"], offers.asked)

    def test_an_offers_check_that_cannot_answer_stops_the_renumbering(self):
        for error in (refusals.OffersUnreadable("offers"), RuntimeError("boom")):
            with self.assertRaises(type(error)):
                change_space_number(self.repo, FailingOffers(error), M, "P1", "P9")
            self.assertEqual(self.before, list_register(self.repo))

    def test_an_unreadable_offers_check_is_a_store_error_not_a_refusal(self):
        with self.assertRaises(refusals.StoreUnreadable) as caught:
            change_space_number(self.repo, FailingOffers(refusals.OffersUnreadable("x")), M,
                                "P1", "P9")
        self.assertNotIsInstance(caught.exception, refusals.Refusal)


class Removal(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRepository()
        self.rentals = StubRentals()
        self.offers = StubOffers()
        register_lot(self.repo, M, "A12", "Durand")
        register_lot(self.repo, M, "B1", "Martin")
        register_space(self.repo, M, "P1", "A12")
        register_space(self.repo, M, "P2", "B1")
        self.before = list_register(self.repo)

    def assert_refused(self, reason, call):
        with self.assertRaises(reason) as caught:
            call()
        self.assertIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(self.before, list_register(self.repo))

    def test_the_manager_removes_a_space_found_ignoring_case_and_spaces(self):
        result = remove_space(self.repo, self.rentals, self.offers, M, " p1 ")
        self.assertIsNone(result)
        self.assertEqual([LotEntry("A12", "Durand", ()),
                          LotEntry("B1", "Martin", ("P2",))], list_register(self.repo))

    def test_removing_a_space_never_removes_its_lot(self):
        remove_space(self.repo, self.rentals, self.offers, M, "P1")
        remove_space(self.repo, self.rentals, self.offers, M, "P2")
        self.assertEqual([LotEntry("A12", "Durand", ()), LotEntry("B1", "Martin", ())],
                         list_register(self.repo))

    def test_a_removed_number_can_be_registered_again_on_any_lot(self):
        remove_space(self.repo, self.rentals, self.offers, M, "P1")
        register_space(self.repo, M, "P1", "A12")
        remove_space(self.repo, self.rentals, self.offers, M, "P1")
        register_space(self.repo, M, " p1 ", "B1")
        self.assertEqual([LotEntry("A12", "Durand", ()),
                          LotEntry("B1", "Martin", ("p1", "P2"))], list_register(self.repo))

    def test_an_unknown_space_is_refused_and_so_is_a_second_removal(self):
        self.assert_refused(refusals.UnknownSpaceRefused,
                            lambda: remove_space(self.repo, self.rentals, self.offers, M, "P7"))
        remove_space(self.repo, self.rentals, self.offers, M, "P1")
        self.before = list_register(self.repo)
        self.assert_refused(refusals.UnknownSpaceRefused,
                            lambda: remove_space(self.repo, self.rentals, self.offers, M, "P1"))

    def test_a_blank_number_is_refused_as_blank(self):
        for value in (None, "", "   "):
            self.assert_refused(refusals.BlankValueRefused,
                                lambda: remove_space(self.repo, self.rentals, self.offers, M, value))

    def test_a_rented_space_is_refused_and_stays_listed(self):
        rentals = StubRentals("P1")
        self.assert_refused(refusals.SpaceRentedRefused,
                            lambda: remove_space(self.repo, rentals, self.offers, M, " p1 "))
        self.assertEqual(["P1"], rentals.asked)

    def test_the_rental_port_is_asked_the_number_as_stored_and_only_for_a_known_space(self):
        remove_space(self.repo, self.rentals, self.offers, M, " p2 ")
        self.assertEqual(["P2"], self.rentals.asked)
        for value in ("P7", " ", None):
            with self.assertRaises(refusals.Refusal):
                remove_space(self.repo, self.rentals, self.offers, M, value)
        self.assertEqual(["P2"], self.rentals.asked)

    def test_the_default_rental_check_answers_no_rental_for_every_space(self):
        self.assertIs(False, rental_check().has_rental("P1"))

    def test_the_default_rental_check_never_blocks_a_removal(self):
        remove_space(self.repo, rental_check(), self.offers, M, "P1")
        self.assertEqual(((), ("P2",)), tuple(e.spaces for e in list_register(self.repo)))

    def test_any_other_role_is_refused_first_and_the_port_is_not_asked(self):
        rentals = StubRentals("P1")
        for role in (Role.OWNER, Role.RESIDENT, None, "manager"):
            for number in ("P2", "P7", " ", None, "P1"):
                self.assert_refused(refusals.ManagerOnly,
                                    lambda: remove_space(self.repo, rentals, self.offers, role, number))
        self.assertEqual([], rentals.asked)

    def test_an_offered_space_is_refused_as_space_offered_and_stays_listed(self):
        offered = StubOffers("P1")
        self.assert_refused(refusals.SpaceOfferedRefused,
                            lambda: remove_space(self.repo, self.rentals, offered, M, " p1 "))
        self.assertEqual(["P1"], offered.asked)

    def test_a_rented_and_offered_space_is_refused_as_rented_and_the_offers_are_not_asked(self):
        offered = StubOffers("P1")
        self.assert_refused(refusals.SpaceRentedRefused,
                            lambda: remove_space(self.repo, StubRentals("P1"), offered, M, "P1"))
        self.assertEqual([], offered.asked)

    def test_space_offered_is_not_space_rented(self):
        with self.assertRaises(refusals.SpaceOfferedRefused) as caught:
            remove_space(self.repo, self.rentals, StubOffers("P1"), M, "P1")
        self.assertNotIsInstance(caught.exception, refusals.SpaceRentedRefused)

    def test_the_offers_are_asked_once_with_the_number_as_stored_and_only_for_a_kept_space(self):
        remove_space(self.repo, self.rentals, self.offers, M, " p2 ")
        self.assertEqual(["P2"], self.offers.asked)
        for value in ("P7", " ", None):
            with self.assertRaises(refusals.Refusal):
                remove_space(self.repo, self.rentals, self.offers, M, value)
        with self.assertRaises(refusals.SpaceRentedRefused):
            remove_space(self.repo, StubRentals("P1"), self.offers, M, "P1")
        self.assertEqual(["P2"], self.offers.asked)

    def test_a_blank_number_and_an_unknown_space_are_refused_before_the_offers_are_read(self):
        broken = FailingOffers(refusals.OffersUnreadable("offers"))
        for value, reason in ((None, refusals.BlankValueRefused),
                              (" ", refusals.BlankValueRefused),
                              ("P7", refusals.UnknownSpaceRefused)):
            self.assert_refused(reason,
                                lambda: remove_space(self.repo, self.rentals, broken, M, value))
        self.assertEqual([], broken.asked)

    def test_an_offers_check_that_cannot_answer_stops_the_removal(self):
        for error in (refusals.OffersUnreadable("offers"), RuntimeError("boom")):
            with self.assertRaises(type(error)):
                remove_space(self.repo, self.rentals, FailingOffers(error), M, "P1")
            self.assertEqual(self.before, list_register(self.repo))

    def test_unreadable_offers_are_a_store_error_not_a_refusal(self):
        with self.assertRaises(refusals.StoreUnreadable) as caught:
            remove_space(self.repo, self.rentals,
                         FailingOffers(refusals.OffersUnreadable("x")), M, "P1")
        self.assertNotIsInstance(caught.exception, refusals.Refusal)

    def test_an_old_call_without_the_offers_fails_loudly(self):
        with self.assertRaises(TypeError):
            remove_space(self.repo, self.rentals, M, "P1")
        with self.assertRaises(TypeError):
            change_space_number(self.repo, M, "P1", "P9")


class NaturalListing(unittest.TestCase):
    def test_listing_orders_numbers_naturally_whatever_the_registration_order(self):
        repo = InMemoryRepository()
        for identifier in ("A10", "a2"):
            register_lot(repo, M, identifier, "X")
        for number in ("P10", "p2"):
            register_space(repo, M, number, "a2")
        entries = list_register(repo)
        self.assertEqual(["a2", "A10"], [e.identifier for e in entries])
        self.assertEqual(("p2", "P10"), entries[0].spaces)


class SuperscriptDigits(unittest.TestCase):
    def test_an_identifier_or_number_with_a_superscript_digit_registers_and_lists(self):
        repo = InMemoryRepository()
        for identifier in ("P1²", "²", "P2"):
            register_lot(repo, M, identifier, "X")
        register_space(repo, M, "S1²", "P2")
        register_space(repo, M, "S1", "P2")
        entries = list_register(repo)
        self.assertEqual({"P1²", "²", "P2"}, {e.identifier for e in entries})
        self.assertEqual(("S1", "S1²"), next(e for e in entries if e.identifier == "P2").spaces)
