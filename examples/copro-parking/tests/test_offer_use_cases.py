import bootstrap  # noqa: F401  (must come first)
import unittest
from datetime import date, datetime

from copro_parking.application import refusals
from copro_parking.application.offer_use_cases import (OfferEntry, OfferRequest,
                                                       _require_owner,
                                                       list_open_offers,
                                                       offer_space)
from copro_parking.application.ports import OfferRepository, RegisterRepository
from copro_parking.application.role import Role
from copro_parking.application.use_cases import (change_lot_owner, list_register,
                                                 register_lot, register_space,
                                                 remove_space)
from fakes import FixedClock, InMemoryOfferRepository, InMemoryRepository, StubRentals

M = Role.MANAGER
O = Role.OWNER
TODAY = date(2026, 11, 11)


def request(space="P1", offerer="Durand", start="2026-11-20", end="2026-11-25"):
    return OfferRequest(space, offerer, start, end)


class UnreadableRegister(RegisterRepository):
    def load(self):
        raise refusals.StoreUnreadable("register")

    def save(self, register):
        raise refusals.StoreUnreadable("register")


class UnreadableOffers(OfferRepository):
    def load(self):
        raise refusals.OffersUnreadable("offers")

    def save(self, book):
        raise refusals.OffersUnreadable("offers")


class OfferCase(unittest.TestCase):
    def setUp(self):
        self.registers = InMemoryRepository()
        register_lot(self.registers, M, "A12", "Durand")
        register_lot(self.registers, M, "B2", "Martin")
        for number, lot in (("P1", "A12"), ("p2", "A12"), ("P10", "A12"), ("P3", "B2")):
            register_space(self.registers, M, number, lot)
        self.offers = InMemoryOfferRepository()
        self.clock = FixedClock(TODAY)

    def offer(self, role=O, **fields):
        return offer_space(self.registers, self.offers, self.clock, role, request(**fields))

    def listing(self):
        return list_open_offers(self.registers, self.offers, self.clock)

    def assert_refused_and_unchanged(self, error, role=O, **fields):
        register_before = list_register(self.registers)
        listing_before = self.listing()
        with self.assertRaises(error):
            self.offer(role, **fields)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())


class OfferAndList(OfferCase):
    def test_an_owner_offers_a_space_of_their_lot_and_the_list_shows_it_with_all_its_fields(self):
        entry = self.offer()
        expected = OfferEntry(1, "P1", "A12", "Durand", date(2026, 11, 20), date(2026, 11, 25))
        self.assertEqual(expected, entry)
        self.assertEqual([expected], self.listing())

    def test_an_offer_is_listed_as_soon_as_it_is_made_even_when_it_starts_later(self):
        self.offer(start="2026-12-24", end="2026-12-31")
        self.assertEqual(1, len(self.listing()))

    def test_the_space_is_found_ignoring_case_and_spaces_and_shown_as_registered(self):
        entry = self.offer(space="  P2 ")
        self.assertEqual("p2", entry.space)
        self.assertEqual("p2", self.listing()[0].space)

    def test_the_same_request_twice_makes_two_offers_numbered_one_and_two(self):
        self.assertEqual(1, self.offer().number)
        self.assertEqual(2, self.offer().number)
        self.assertEqual([1, 2], [e.number for e in self.listing()])

    def test_an_offer_and_its_entry_carry_no_price(self):
        self.assertNotIn("price", OfferRequest.__dataclass_fields__)
        self.assertNotIn("price", OfferEntry.__dataclass_fields__)
        self.assertEqual({"space", "offerer", "start", "end"}, set(OfferRequest.__dataclass_fields__))
        self.assertEqual({"number", "space", "lot", "owner", "start", "end"},
                         set(OfferEntry.__dataclass_fields__))

    def test_offering_does_not_touch_the_register(self):
        before = list_register(self.registers)
        self.offer()
        self.assertEqual(before, list_register(self.registers))


class ListOrder(OfferCase):
    def test_nothing_offered_lists_an_empty_list_and_a_second_call_gives_the_same_list(self):
        self.assertEqual([], self.listing())
        self.offer()
        self.assertEqual(self.listing(), self.listing())

    def test_the_list_is_sorted_by_start_then_natural_space_order_keeping_creation_order_on_ties(self):
        self.offer(space="P10", start="2026-11-20")
        self.offer(space="p2", start="2026-11-20")
        self.offer(space="P1", start="2026-11-15")
        self.offer(space="P2", start="2026-11-20", end="2026-11-30")
        self.assertEqual([3, 2, 4, 1], [e.number for e in self.listing()])

    def test_listing_needs_no_role_and_does_not_write(self):
        self.offer()
        saves = self.offers.saves
        self.listing()
        self.assertEqual(saves, self.offers.saves)

    def test_an_offer_is_open_until_its_end_date_included_and_gone_the_day_after(self):
        self.offer(start="2026-11-20", end="2026-11-25")
        self.clock.day = date(2026, 11, 25)
        self.assertEqual(1, len(self.listing()))
        self.clock.day = date(2026, 11, 26)
        self.assertEqual([], self.listing())

    def test_the_owner_shown_is_the_current_owner_of_the_lot_after_a_correction(self):
        self.offer()
        change_lot_owner(self.registers, M, "A12", "Moreau")
        self.assertEqual("Moreau", self.listing()[0].owner)

    def test_after_a_correction_only_the_new_owner_may_offer_a_space_of_the_lot(self):
        change_lot_owner(self.registers, M, "A12", "Moreau")
        self.assert_refused_and_unchanged(refusals.NotTheOwner, offerer="Durand")
        self.assertEqual("Moreau", self.offer(offerer=" moreau ").owner)

    def test_an_offer_whose_space_left_the_register_is_not_listed(self):
        self.offer(space="P1")
        self.offer(space="P3", offerer="Martin")
        remove_space(self.registers, StubRentals(), M, "P1")
        self.assertEqual(["P3"], [e.space for e in self.listing()])

    def test_one_clock_read_per_call(self):
        self.offer()
        self.assertEqual(1, self.clock.reads)
        self.listing()
        self.assertEqual(2, self.clock.reads)


class PeriodRules(OfferCase):
    def test_a_one_day_offer_where_start_equals_end_is_valid(self):
        entry = self.offer(start="2026-11-20", end="2026-11-20")
        self.assertEqual((date(2026, 11, 20), date(2026, 11, 20)), (entry.start, entry.end))

    def test_an_end_before_the_start_is_refused_as_an_invalid_period(self):
        self.assert_refused_and_unchanged(
            refusals.InvalidPeriodRefused, start="2026-11-20", end="2026-11-19")

    def test_a_missing_or_unreadable_date_is_refused_as_an_invalid_period(self):
        for bad in (None, "", "  ", "tomorrow", "2026-02-30", "2026-13-01", "2026-1-5",
                    "20261120", "2026-11-20T10:00", "2026-W47-5", "２０２６-11-20",
                    20261120, 5.5, True, ["2026-11-20"]):
            for field in ("start", "end"):
                with self.subTest(bad=bad, field=field):
                    self.assert_refused_and_unchanged(
                        refusals.InvalidPeriodRefused, **{field: bad})

    def test_dates_are_date_objects_or_iso_text_with_surrounding_spaces_ignored(self):
        entry = self.offer(start=date(2026, 11, 20), end=" 2026-11-25 ")
        self.assertEqual((date(2026, 11, 20), date(2026, 11, 25)), (entry.start, entry.end))

    def test_a_datetime_is_not_a_date_and_is_refused(self):
        self.assert_refused_and_unchanged(
            refusals.InvalidPeriodRefused, start=datetime(2026, 11, 20, 9, 30))
        self.assert_refused_and_unchanged(
            refusals.InvalidPeriodRefused, end=datetime(2026, 11, 25, 9, 30))

    def test_a_start_before_today_is_refused_and_a_start_equal_to_today_is_accepted(self):
        self.assert_refused_and_unchanged(
            refusals.InvalidPeriodRefused, start="2026-11-10", end="2026-11-30")
        self.assertEqual(TODAY, self.offer(start="2026-11-11", end="2026-11-11").start)

    def test_today_comes_from_the_clock(self):
        self.clock.day = date(2026, 12, 1)
        self.assert_refused_and_unchanged(
            refusals.InvalidPeriodRefused, start="2026-11-20", end="2026-12-05")
        self.assertEqual(1, self.offer(start="2026-12-01", end="2026-12-05").number)


class OwnerAndSpaceRules(OfferCase):
    def test_an_unknown_space_is_refused(self):
        self.assert_refused_and_unchanged(refusals.UnknownSpaceRefused, space="P99")

    def test_an_offerer_that_is_not_the_lot_owner_is_refused_and_an_owner_of_another_lot_too(self):
        self.assert_refused_and_unchanged(refusals.NotTheOwner, offerer="Dupont")
        self.assert_refused_and_unchanged(refusals.NotTheOwner, space="P3", offerer="Durand")
        self.assert_refused_and_unchanged(refusals.NotTheOwner, space="P1", offerer="Martin")

    def test_the_owner_name_is_compared_ignoring_case_and_surrounding_spaces(self):
        self.assertEqual("Durand", self.offer(offerer="  dURAND ").owner)

    def test_blank_missing_or_non_text_space_or_offerer_is_refused_as_invalid_input(self):
        for bad in ("", "   ", None, 5, ["P1"]):
            for field in ("space", "offerer"):
                with self.subTest(bad=bad, field=field):
                    self.assert_refused_and_unchanged(
                        refusals.BlankValueRefused, **{field: bad})

    def test_a_refusal_is_not_an_unreadable_store(self):
        with self.assertRaises(refusals.Refusal):
            self.offer(offerer="Dupont")


class RoleRule(OfferCase):
    ROLES = (M, Role.RESIDENT, None, "owner", 3)

    def test_any_role_other_than_owner_is_refused_first_with_nothing_read_or_written(self):
        for role in self.ROLES:
            with self.subTest(role=role):
                with self.assertRaises(refusals.NotAllowedToOffer):
                    offer_space(UnreadableRegister(), UnreadableOffers(), self.clock, role,
                                request(start="nope", end=None, space=" ", offerer=None))
        self.assertEqual(0, self.clock.reads)
        self.assertEqual(0, self.offers.loads)

    def test_a_non_owner_role_is_refused_even_when_everything_else_is_valid(self):
        for role in self.ROLES:
            with self.subTest(role=role):
                self.assert_refused_and_unchanged(refusals.NotAllowedToOffer, role=role)

    def test_not_allowed_to_offer_is_a_refusal(self):
        self.assertTrue(issubclass(refusals.NotAllowedToOffer, refusals.Refusal))
        self.assertTrue(issubclass(refusals.NotTheOwner, refusals.Refusal))
        self.assertTrue(issubclass(refusals.InvalidPeriodRefused, refusals.Refusal))

    def test_the_owner_check_states_that_a_declared_name_is_not_an_authentication(self):
        for doc in (offer_space.__doc__, _require_owner.__doc__):
            self.assertIn("not an authentication", doc)


class RefusalOrder(OfferCase):
    def test_the_role_comes_before_invalid_input_unknown_space_and_not_the_owner(self):
        bad_period = dict(start="2026-11-20", end="2026-11-19")
        for role in (M, None):
            self.assert_refused_and_unchanged(refusals.NotAllowedToOffer, role=role, **bad_period)
            self.assert_refused_and_unchanged(refusals.NotAllowedToOffer, role=role, space="P99")
            self.assert_refused_and_unchanged(refusals.NotAllowedToOffer, role=role, offerer="Dupont")

    def test_invalid_input_comes_before_unknown_space_and_not_the_owner(self):
        bad_period = dict(start="2026-11-20", end="2026-11-19")
        self.assert_refused_and_unchanged(refusals.InvalidPeriodRefused, space="P99", **bad_period)
        self.assert_refused_and_unchanged(refusals.InvalidPeriodRefused, offerer="Dupont", **bad_period)
        self.assert_refused_and_unchanged(refusals.BlankValueRefused, space="P99", offerer=" ")
        self.assert_refused_and_unchanged(refusals.BlankValueRefused, space=" ", offerer="Dupont")
        self.assert_refused_and_unchanged(refusals.BlankValueRefused, offerer=" ", space="P3")

    def test_unknown_space_comes_before_not_the_owner(self):
        self.assert_refused_and_unchanged(
            refusals.UnknownSpaceRefused, space="P99", offerer="Dupont")

    def test_input_and_ownership_refusals_come_before_the_offers_file_is_read(self):
        stores = (self.registers, UnreadableOffers(), self.clock)
        for fields, error in ((dict(end="2026-11-01"), refusals.InvalidPeriodRefused),
                              (dict(space="P99"), refusals.UnknownSpaceRefused),
                              (dict(offerer="Dupont"), refusals.NotTheOwner)):
            with self.assertRaises(error):
                offer_space(*stores, O, request(**fields))


class UnreadableStores(OfferCase):
    def test_unreadable_offers_end_listing_and_offering_with_a_store_error_not_a_refusal(self):
        for call in (lambda: list_open_offers(self.registers, UnreadableOffers(), self.clock),
                     lambda: offer_space(self.registers, UnreadableOffers(), self.clock, O,
                                         request())):
            with self.assertRaises(refusals.OffersUnreadable) as caught:
                call()
            self.assertIsInstance(caught.exception, refusals.StoreUnreadable)
            self.assertNotIsInstance(caught.exception, refusals.Refusal)

    def test_an_unreadable_register_stops_offering_and_listing(self):
        with self.assertRaises(refusals.StoreUnreadable):
            offer_space(UnreadableRegister(), self.offers, self.clock, O, request())
        with self.assertRaises(refusals.StoreUnreadable):
            list_open_offers(UnreadableRegister(), self.offers, self.clock)
        self.assertEqual(0, self.offers.saves)


if __name__ == "__main__":
    unittest.main()
