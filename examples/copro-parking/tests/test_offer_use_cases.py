import bootstrap  # noqa: F401  (must come first)
import unittest
from datetime import date, datetime

from copro_parking.application import refusals
from copro_parking.application.offer_use_cases import (OfferEntry, OfferRequest,
                                                       WithdrawRequest,
                                                       _require_owner,
                                                       list_open_offers,
                                                       offer_space,
                                                       withdraw_offer)
from copro_parking.application.ports import (OfferCheck, OfferRepository,
                                             RegisterRepository)
from copro_parking.application.role import Role
from copro_parking.domain import errors
from copro_parking.domain.errors import OverlappingOffer
from copro_parking.domain.offers import Offer, OfferBook, Period, offer_number
from copro_parking.application.use_cases import (change_lot_owner,
                                                 change_space_number,
                                                 list_register, register_lot,
                                                 register_space, remove_space)
from copro_parking.infrastructure.wiring import offer_check
from fakes import (FailingOffers, FixedClock, InMemoryOfferRepository,
                   InMemoryRepository, StubRentals)

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

    def store_orphan(self, space, start="2026-11-20", end="2026-11-25"):
        """An offer for a number the register does not hold, as a file written before S4 may."""
        book = self.offers.load()
        offer = book.add(space, Period.of(start, end), TODAY)
        self.offers.save(book)
        return offer

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

    def test_two_offers_of_distinct_periods_are_numbered_one_and_two(self):
        self.assertEqual(1, self.offer().number)
        self.assertEqual(2, self.offer(start="2026-12-01", end="2026-12-05").number)
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

    def test_the_list_is_sorted_by_start_then_natural_space_order(self):
        self.offer(space="P10", start="2026-11-20")
        self.offer(space="p2", start="2026-11-20")
        self.offer(space="P1", start="2026-11-15")
        self.offer(space="P3", offerer="Martin", start="2026-11-20")
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

    def test_an_offer_whose_space_is_not_registered_is_not_listed(self):
        self.offer(space="P1")
        self.offer(space="P3", offerer="Martin")
        self.store_orphan("P8")
        self.assertEqual(["P1", "P3"], [e.space for e in self.listing()])

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


class OverlapRule(OfferCase):
    def offer_p1(self, start, end, **fields):
        return self.offer(space="P1", start=start, end=end, **fields)

    def test_an_offer_sharing_a_day_with_an_open_offer_of_the_space_is_refused_naming_it(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        for start, end in (("2026-11-24", "2026-11-30"), ("2026-11-18", "2026-11-20"),
                           ("2026-11-21", "2026-11-22"), ("2026-11-15", "2026-12-30"),
                           ("2026-11-20", "2026-11-24")):
            with self.subTest(start=start, end=end):
                with self.assertRaises(refusals.OverlapRefused) as caught:
                    self.offer_p1(start, end)
                self.assertEqual(1, caught.exception.offer_number)
                self.assertIsInstance(caught.exception, refusals.Refusal)
                self.assertIn("1", str(caught.exception))

    def test_the_later_period_offered_first_gives_the_same_refusal(self):
        self.offer_p1("2026-11-24", "2026-11-30")
        with self.assertRaises(refusals.OverlapRefused) as caught:
            self.offer_p1("2026-11-20", "2026-11-24")
        self.assertEqual(1, caught.exception.offer_number)

    def test_the_refusal_names_the_earliest_start_offer_and_the_lowest_number_on_ties(self):
        self.offer_p1("2026-11-24", "2026-11-26")
        self.offer_p1("2026-11-20", "2026-11-22")
        with self.assertRaises(refusals.OverlapRefused) as caught:
            self.offer_p1("2026-11-21", "2026-11-25")
        self.assertEqual(2, caught.exception.offer_number)
        stored = OfferBook.restore(
            [Offer(1, "P1", Period(date(2026, 11, 20), date(2026, 11, 22))),
             Offer(2, "P1", Period(date(2026, 11, 20), date(2026, 11, 23)))], 3)
        with self.assertRaises(OverlappingOffer) as tie:
            stored.add("P1", Period(date(2026, 11, 21), date(2026, 11, 21)), TODAY)
        self.assertEqual(1, tie.exception.offer_number)

    def test_an_offer_of_another_space_on_the_same_days_is_accepted(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        self.assertEqual(2, self.offer(space="p2", start="2026-11-20", end="2026-11-24").number)
        self.assertEqual("P1", self.listing()[0].space)

    def test_the_space_is_compared_as_registered_ignoring_case_and_spaces(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        with self.assertRaises(refusals.OverlapRefused):
            self.offer(space=" p1 ", start="2026-11-22", end="2026-11-23")

    def test_offers_on_the_days_next_to_an_offer_are_accepted_and_a_one_day_offer_inside_is_refused(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        self.offer_p1("2026-11-25", "2026-11-30")
        self.offer_p1("2026-11-15", "2026-11-19")
        for day in ("2026-11-24", "2026-11-22"):
            with self.assertRaises(refusals.OverlapRefused):
                self.offer_p1(day, day)

    def test_an_offer_whose_end_has_passed_no_longer_blocks_and_one_ending_today_still_does(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        self.clock.day = date(2026, 11, 24)
        with self.assertRaises(refusals.OverlapRefused):
            self.offer_p1("2026-11-24", "2026-11-26")
        self.clock.day = date(2026, 11, 25)
        self.assertEqual(2, self.offer_p1("2026-11-25", "2026-11-26").number)
        stored = OfferBook.restore(
            [Offer(1, "P1", Period(date(2026, 11, 1), date(2026, 11, 24)))], 2)
        stored.add("P1", Period(date(2026, 11, 20), date(2026, 11, 28)), date(2026, 11, 25))

    def test_the_overlap_is_the_last_refusal(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        bad_period = dict(start="2026-11-22", end="2026-11-21")
        self.assert_refused_and_unchanged(refusals.NotAllowedToOffer, role=M,
                                          start="2026-11-22", end="2026-11-23")
        self.assert_refused_and_unchanged(refusals.InvalidPeriodRefused, **bad_period)
        self.assert_refused_and_unchanged(refusals.BlankValueRefused, offerer=" ",
                                          start="2026-11-22", end="2026-11-23")
        self.assert_refused_and_unchanged(refusals.UnknownSpaceRefused, space="P99",
                                          start="2026-11-22", end="2026-11-23")
        self.assert_refused_and_unchanged(refusals.NotTheOwner, offerer="Dupont",
                                          start="2026-11-22", end="2026-11-23")
        self.assert_refused_and_unchanged(refusals.OverlapRefused,
                                          start="2026-11-22", end="2026-11-23")

    def test_an_overlap_refusal_changes_nothing_and_the_next_offer_gets_the_number_it_would_have_had(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        saves = self.offers.saves
        self.assert_refused_and_unchanged(refusals.OverlapRefused,
                                          start="2026-11-22", end="2026-11-23")
        self.assertEqual(saves, self.offers.saves)
        self.assertEqual(2, self.offer_p1("2026-12-01", "2026-12-02").number)
        self.assertEqual([1, 2], [e.number for e in self.listing()])


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


def withdrawal(offerer="Durand", number=1):
    return WithdrawRequest(offerer, number)


class WithdrawCase(OfferCase):
    """Offer 1 of P1 by Durand (lot A12) from 20 to 25 is open."""

    def setUp(self):
        super().setUp()
        self.offer()

    def withdraw(self, role=O, **fields):
        return withdraw_offer(self.registers, self.offers, self.clock, role, withdrawal(**fields))

    def assert_withdraw_refused_and_unchanged(self, error, role=O, **fields):
        register_before = list_register(self.registers)
        listing_before = self.listing()
        saves = self.offers.saves
        with self.assertRaises(error):
            self.withdraw(role, **fields)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())
        self.assertEqual(saves, self.offers.saves)


class OfferBookWithdrawal(unittest.TestCase):
    def book(self):
        return OfferBook.restore(
            [Offer(1, "P1", Period(date(2026, 11, 20), date(2026, 11, 25))),
             Offer(2, "P1", Period(date(2026, 11, 1), date(2026, 11, 5))),
             Offer(4, "P2", Period(date(2026, 11, 20), date(2026, 11, 25)))], 5)

    def test_open_offer_finds_an_open_offer_by_its_number_only(self):
        book = self.book()
        self.assertEqual(1, book.open_offer(1, TODAY).number)
        self.assertEqual("P2", book.open_offer(4, TODAY).space_number)
        for number in (2, 3, 5, 99):
            with self.subTest(number=number):
                with self.assertRaises(errors.UnknownOffer):
                    book.open_offer(number, TODAY)

    def test_an_offer_is_open_on_its_end_day_and_not_the_day_after(self):
        book = self.book()
        self.assertEqual(1, book.open_offer(1, date(2026, 11, 25)).number)
        with self.assertRaises(errors.UnknownOffer):
            book.open_offer(1, date(2026, 11, 26))
        with self.assertRaises(errors.UnknownOffer):
            book.withdraw(1, date(2026, 11, 26))
        self.assertEqual([1, 2, 4], [o.number for o in book.offers()])

    def test_withdraw_deletes_only_that_offer_and_keeps_expired_ones_and_the_next_number(self):
        book = self.book()
        withdrawn = book.withdraw(1, TODAY)
        self.assertEqual(1, withdrawn.number)
        self.assertEqual([2, 4], [o.number for o in book.offers()])
        self.assertEqual(5, book.next_number)
        with self.assertRaises(errors.UnknownOffer):
            book.withdraw(1, TODAY)

    def test_offer_number_accepts_whole_numbers_from_one_only(self):
        self.assertEqual(7, offer_number(7))
        for bad in (None, "1", 1.0, 1.5, True, False, 0, -1, "", [1], (1,)):
            with self.subTest(bad=bad):
                with self.assertRaises(errors.InvalidOfferNumber):
                    offer_number(bad)

    def test_the_open_offers_of_a_stored_pair_with_the_same_start_are_ordered_by_number(self):
        period = Period(date(2026, 11, 20), date(2026, 11, 25))
        book = OfferBook.restore([Offer(2, "P1", period), Offer(1, "P1", period)], 3)
        self.assertEqual([1, 2], [o.number for o in book.open_offers(TODAY)])


class OfferBookOpenOffer(unittest.TestCase):
    def book(self):
        return OfferBook.restore(
            [Offer(1, "P1", Period(date(2026, 11, 20), date(2026, 11, 25))),
             Offer(2, "P2", Period(date(2026, 11, 1), date(2026, 11, 10))),
             Offer(3, "p3", Period(date(2026, 12, 1), date(2026, 12, 5)))], 4)

    def test_a_space_with_an_offer_ending_today_or_later_has_an_open_offer(self):
        book = self.book()
        self.assertIs(True, book.has_open_offer("P1", TODAY))
        self.assertIs(True, book.has_open_offer("P1", date(2026, 11, 25)))
        self.assertIs(True, book.has_open_offer("p3", TODAY))

    def test_an_offer_ended_yesterday_is_not_open(self):
        book = self.book()
        self.assertIs(False, book.has_open_offer("P1", date(2026, 11, 26)))
        self.assertIs(False, book.has_open_offer("P2", TODAY))

    def test_a_space_without_an_offer_and_an_empty_book_have_no_open_offer(self):
        self.assertIs(False, self.book().has_open_offer("P9", TODAY))
        self.assertIs(False, OfferBook().has_open_offer("P1", TODAY))

    def test_the_space_number_is_matched_ignoring_case_and_surrounding_spaces(self):
        book = self.book()
        self.assertIs(True, book.has_open_offer("  p1 ", TODAY))
        self.assertIs(True, book.has_open_offer("P3", TODAY))

    def test_asking_changes_nothing(self):
        book = self.book()
        book.has_open_offer("P1", TODAY)
        self.assertEqual([1, 2, 3], [o.number for o in book.offers()])
        self.assertEqual(4, book.next_number)


class WithdrawRules(WithdrawCase):
    def test_an_owner_withdraws_an_open_offer_by_its_number_and_it_leaves_the_list(self):
        self.withdraw()
        self.assertEqual([], self.listing())

    def test_the_owner_name_is_compared_ignoring_case_and_surrounding_spaces(self):
        self.withdraw(offerer="  dURAND ")
        self.assertEqual([], self.listing())

    def test_a_withdrawal_returns_the_entry_it_withdrew_as_the_listing_showed_it(self):
        shown = self.listing()[0]
        entry = self.withdraw()
        self.assertEqual(shown, entry)
        self.assertEqual(OfferEntry(1, "P1", "A12", "Durand", date(2026, 11, 20),
                                    date(2026, 11, 25)), entry)

    def test_withdrawing_one_of_three_offers_leaves_the_other_two_in_the_same_order(self):
        self.offer(start="2026-12-01", end="2026-12-05")
        self.offer(start="2026-12-10", end="2026-12-15")
        before = self.listing()
        self.withdraw(number=2)
        self.assertEqual([before[0], before[2]], self.listing())
        self.assertEqual([1, 3], [e.number for e in self.listing()])

    def test_after_a_correction_the_new_owner_withdraws_and_the_old_name_does_not(self):
        change_lot_owner(self.registers, M, "A12", "Moreau")
        self.assert_withdraw_refused_and_unchanged(refusals.NotTheOwner, offerer="Durand")
        self.assertEqual("Moreau", self.withdraw(offerer=" moreau ").owner)
        self.assertEqual([], self.listing())

    def test_a_withdrawn_offer_no_longer_blocks_its_days_and_the_new_offer_gets_the_next_number(self):
        with self.assertRaises(refusals.OverlapRefused):
            self.offer(start="2026-11-22", end="2026-11-30")
        other = self.offer(space="P3", offerer="Martin")
        self.withdraw()
        self.assertEqual(3, self.offer(start="2026-11-22", end="2026-11-30").number)
        self.assertEqual([other.number, 3], [e.number for e in self.listing()])
        self.assertEqual(other, self.listing()[0])

    def test_numbers_are_never_reused_after_a_withdrawal(self):
        self.withdraw()
        self.assertEqual(2, self.offer().number)
        self.withdraw(number=2)
        self.assertEqual(3, self.offer().number)

    def test_withdrawing_does_not_touch_the_register(self):
        before = list_register(self.registers)
        self.withdraw()
        self.assertEqual(before, list_register(self.registers))

    def test_one_clock_read_per_call(self):
        reads = self.clock.reads
        self.withdraw()
        self.assertEqual(reads + 1, self.clock.reads)

    def test_a_withdrawal_is_one_save(self):
        saves = self.offers.saves
        self.withdraw()
        self.assertEqual(saves + 1, self.offers.saves)


class WithdrawUnknownOffer(WithdrawCase):
    def test_a_number_that_never_existed_is_an_unknown_offer(self):
        for number in (2, 99):
            with self.subTest(number=number):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.UnknownOfferRefused, number=number)

    def test_an_offer_already_withdrawn_is_an_unknown_offer(self):
        self.withdraw()
        self.assert_withdraw_refused_and_unchanged(refusals.UnknownOfferRefused)

    def test_an_offer_whose_end_date_has_passed_is_an_unknown_offer(self):
        self.clock.day = date(2026, 11, 26)
        self.assert_withdraw_refused_and_unchanged(refusals.UnknownOfferRefused)

    def test_an_offer_ending_today_is_still_open_and_is_withdrawn(self):
        self.clock.day = date(2026, 11, 25)
        self.assertEqual(1, self.withdraw().number)

    def test_an_offer_that_starts_in_the_future_is_withdrawn_like_any_other(self):
        self.offer(start="2027-03-01", end="2027-03-10")
        self.assertEqual(2, self.withdraw(number=2).number)
        self.assertEqual([1], [e.number for e in self.listing()])

    def test_an_offer_whose_space_is_not_registered_is_an_unknown_offer_for_any_name(self):
        orphan = self.store_orphan("P8")
        for offerer in ("Durand", "Dupont"):
            with self.subTest(offerer=offerer):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.UnknownOfferRefused, offerer=offerer, number=orphan.number)

    def test_the_unknown_offer_refusal_has_no_cause_and_hides_its_context(self):
        orphan = self.store_orphan("P8")
        ended = self.offer(space="P3", offerer="Martin", start="2026-11-12", end="2026-11-12")
        self.clock.day = date(2026, 11, 13)
        for number in (99, orphan.number, ended.number):
            with self.subTest(number=number):
                with self.assertRaises(refusals.UnknownOfferRefused) as caught:
                    self.withdraw(number=number)
                self.assertIsNone(caught.exception.__cause__)
                self.assertTrue(caught.exception.__suppress_context__)

    def test_an_unknown_offer_is_a_refusal_not_a_store_error(self):
        self.assertTrue(issubclass(refusals.UnknownOfferRefused, refusals.Refusal))
        self.assertTrue(issubclass(refusals.InvalidOfferNumberRefused, refusals.Refusal))
        self.assertFalse(issubclass(refusals.UnknownOfferRefused, refusals.StoreUnreadable))


class WithdrawInvalidInput(WithdrawCase):
    def test_a_number_that_is_not_a_whole_number_from_one_is_refused_as_invalid_input(self):
        for bad in (None, "1", 1.0, 1.5, True, 0, -1, "", [1]):
            with self.subTest(bad=bad):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.InvalidOfferNumberRefused, number=bad)

    def test_a_blank_missing_or_non_text_offerer_is_refused_as_invalid_input(self):
        for bad in ("", "   ", None, 5, ["Durand"]):
            with self.subTest(bad=bad):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.BlankValueRefused, offerer=bad)

    def test_a_whole_number_matching_no_open_offer_is_an_unknown_offer_not_invalid_input(self):
        self.assert_withdraw_refused_and_unchanged(refusals.UnknownOfferRefused, number=2)

    def test_a_blank_offerer_is_reported_before_a_bad_number(self):
        self.assert_withdraw_refused_and_unchanged(
            refusals.BlankValueRefused, offerer=" ", number=None)

    def test_a_request_with_nothing_in_it_is_invalid_input(self):
        self.assert_withdraw_refused_and_unchanged(
            refusals.BlankValueRefused, offerer=None, number=None)
        self.assert_withdraw_refused_and_unchanged(
            refusals.InvalidOfferNumberRefused, number=None)


class WithdrawNotTheOwner(WithdrawCase):
    def test_a_name_that_is_not_the_owner_is_refused_and_the_offer_stays_listed(self):
        self.offer(space="P3", offerer="Martin")
        for offerer in ("Dupont", "Martin"):
            with self.subTest(offerer=offerer):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.NotTheOwner, offerer=offerer)
        self.assert_withdraw_refused_and_unchanged(refusals.NotTheOwner, offerer="Durand", number=2)

    def test_the_manager_name_cannot_withdraw_either(self):
        self.assert_withdraw_refused_and_unchanged(refusals.NotTheOwner, offerer="manager")


class WithdrawRoleRule(WithdrawCase):
    def test_any_role_other_than_owner_is_refused_first_with_nothing_read_or_written(self):
        reads, loads = self.clock.reads, self.offers.loads
        for role in RoleRule.ROLES:
            with self.subTest(role=role):
                with self.assertRaises(refusals.NotAllowedToOffer):
                    withdraw_offer(UnreadableRegister(), UnreadableOffers(), self.clock, role,
                                   withdrawal(offerer=None, number="x"))
        self.assertEqual(reads, self.clock.reads)
        self.assertEqual(loads, self.offers.loads)

    def test_a_non_owner_role_is_refused_even_when_everything_else_is_valid(self):
        for role in RoleRule.ROLES:
            with self.subTest(role=role):
                self.assert_withdraw_refused_and_unchanged(refusals.NotAllowedToOffer, role=role)


class WithdrawRefusalOrder(WithdrawCase):
    def test_the_role_comes_before_invalid_input_unknown_offer_and_not_the_owner(self):
        for role in (M, None):
            self.assert_withdraw_refused_and_unchanged(
                refusals.NotAllowedToOffer, role=role, number=None)
            self.assert_withdraw_refused_and_unchanged(
                refusals.NotAllowedToOffer, role=role, offerer=" ")
            self.assert_withdraw_refused_and_unchanged(
                refusals.NotAllowedToOffer, role=role, number=99)
            self.assert_withdraw_refused_and_unchanged(
                refusals.NotAllowedToOffer, role=role, offerer="Dupont")

    def test_invalid_input_comes_before_unknown_offer_and_not_the_owner(self):
        self.assert_withdraw_refused_and_unchanged(
            refusals.InvalidOfferNumberRefused, offerer="Dupont", number=0)
        self.assert_withdraw_refused_and_unchanged(
            refusals.BlankValueRefused, offerer=" ", number=99)
        self.clock.day = date(2026, 11, 26)
        self.assert_withdraw_refused_and_unchanged(
            refusals.BlankValueRefused, offerer=" ", number=1)

    def test_unknown_offer_comes_before_not_the_owner(self):
        self.assert_withdraw_refused_and_unchanged(
            refusals.UnknownOfferRefused, offerer="Dupont", number=99)
        self.withdraw()
        self.assert_withdraw_refused_and_unchanged(
            refusals.UnknownOfferRefused, offerer="Dupont")

    def test_a_non_owner_naming_a_closed_offer_gets_unknown_offer_not_the_owner(self):
        self.clock.day = date(2026, 11, 26)
        self.assert_withdraw_refused_and_unchanged(
            refusals.UnknownOfferRefused, offerer="Dupont")

    def test_not_the_owner_is_the_last_refusal(self):
        self.assert_withdraw_refused_and_unchanged(refusals.NotTheOwner, offerer="Dupont")


class WithdrawStores(WithdrawCase):
    def test_invalid_input_comes_before_any_store_is_read(self):
        for fields, error in ((dict(offerer=" "), refusals.BlankValueRefused),
                              (dict(number=0), refusals.InvalidOfferNumberRefused)):
            with self.assertRaises(error):
                withdraw_offer(UnreadableRegister(), UnreadableOffers(), self.clock, O,
                               withdrawal(**fields))

    def test_unreadable_offers_end_a_valid_withdrawal_with_a_store_error_not_a_refusal(self):
        with self.assertRaises(refusals.OffersUnreadable) as caught:
            withdraw_offer(self.registers, UnreadableOffers(), self.clock, O, withdrawal())
        self.assertIsInstance(caught.exception, refusals.StoreUnreadable)
        self.assertNotIsInstance(caught.exception, refusals.Refusal)

    def test_an_unreadable_register_ends_a_valid_withdrawal_and_nothing_is_saved(self):
        saves = self.offers.saves
        with self.assertRaises(refusals.StoreUnreadable):
            withdraw_offer(UnreadableRegister(), self.offers, self.clock, O, withdrawal())
        self.assertEqual(saves, self.offers.saves)
        self.assertEqual(1, len(self.listing()))

    def test_an_unreadable_register_wins_over_an_unknown_offer_whatever_the_number(self):
        self.offer(start="2026-11-12", end="2026-11-12")
        withdrawn = self.offer(space="P3", offerer="Martin").number
        self.withdraw(offerer="Martin", number=withdrawn)
        self.clock.day = date(2026, 11, 13)
        for number in (1, 2, 3, 99):
            with self.subTest(number=number):
                with self.assertRaises(refusals.StoreUnreadable) as caught:
                    withdraw_offer(UnreadableRegister(), self.offers, self.clock, O,
                                   withdrawal(number=number))
                self.assertNotIsInstance(caught.exception, refusals.Refusal)

    def test_both_stores_unreadable_gives_the_offers_unreadable_error(self):
        with self.assertRaises(refusals.OffersUnreadable):
            withdraw_offer(UnreadableRegister(), UnreadableOffers(), self.clock, O, withdrawal())

    def test_the_stores_are_read_once_each_for_any_valid_withdrawal(self):
        loads = self.offers.loads
        with self.assertRaises(refusals.UnknownOfferRefused):
            self.withdraw(number=99)
        self.assertEqual(loads + 1, self.offers.loads)


class WithdrawEdges(WithdrawCase):
    def test_withdrawing_the_same_offer_twice_refuses_the_second_call(self):
        self.withdraw()
        with self.assertRaises(refusals.UnknownOfferRefused):
            self.withdraw()

    def test_the_highest_number_is_withdrawn_and_the_lowest_too(self):
        self.offer(start="2026-12-01", end="2026-12-05")
        self.assertEqual(2, self.withdraw(number=2).number)
        self.assertEqual(1, self.withdraw(number=1).number)
        self.assertEqual([], self.listing())

    def test_withdrawing_in_either_order_gives_the_same_final_list(self):
        self.offer(start="2026-12-01", end="2026-12-05")
        self.offer(start="2026-12-10", end="2026-12-15")
        kept = self.listing()[2]
        self.withdraw(number=1)
        self.withdraw(number=2)
        self.assertEqual([kept], self.listing())

    def test_withdrawing_the_same_pair_in_the_other_order_gives_the_same_final_list(self):
        self.offer(start="2026-12-01", end="2026-12-05")
        self.offer(start="2026-12-10", end="2026-12-15")
        kept = self.listing()[2]
        self.withdraw(number=2)
        self.withdraw(number=1)
        self.assertEqual([kept], self.listing())

    def test_withdrawing_then_offering_again_on_the_same_days_works_repeatedly(self):
        for expected in (2, 3):
            self.withdraw(number=expected - 1)
            self.assertEqual(expected, self.offer().number)


if __name__ == "__main__":
    unittest.main()


class StoredOfferCheckQuestions(OfferCase):
    def setUp(self):
        super().setUp()
        self.check = offer_check(self.offers, self.clock)

    def test_it_is_the_offer_check_port(self):
        self.assertIsInstance(self.check, OfferCheck)

    def test_a_space_with_an_open_offer_answers_true_found_ignoring_case_and_spaces(self):
        self.offer(space="p2")
        for asked in ("p2", " P2 "):
            self.assertIs(True, self.check.has_open_offer(asked))

    def test_no_offer_another_space_or_an_offer_ended_yesterday_answer_exactly_false(self):
        self.offer(start="2026-11-12", end="2026-11-12")
        self.assertIs(False, self.check.has_open_offer("P3"))
        self.assertIs(True, self.check.has_open_offer("P1"))
        self.clock.day = date(2026, 11, 13)
        self.assertIs(False, self.check.has_open_offer("P1"))
        self.assertIs(False, offer_check(InMemoryOfferRepository(), self.clock)
                      .has_open_offer("P1"))

    def test_an_offer_ending_today_or_starting_later_counts(self):
        self.offer(start="2026-11-11", end="2026-11-11")
        self.offer(space="P3", offerer="Martin", start="2027-01-10", end="2027-01-12")
        self.assertIs(True, self.check.has_open_offer("P1"))
        self.assertIs(True, self.check.has_open_offer("P3"))

    def test_it_reads_the_clock_once_and_the_offers_once_per_question(self):
        self.offer()
        reads, loads = self.clock.reads, self.offers.loads
        self.check.has_open_offer("P1")
        self.assertEqual((reads + 1, loads + 1), (self.clock.reads, self.offers.loads))

    def test_it_follows_the_offers_file_between_two_questions(self):
        self.assertIs(False, self.check.has_open_offer("P1"))
        self.offer()
        self.assertIs(True, self.check.has_open_offer("P1"))

    def test_unreadable_offers_raise_the_offers_unreadable_error_and_never_answer_false(self):
        with self.assertRaises(refusals.OffersUnreadable):
            offer_check(UnreadableOffers(), self.clock).has_open_offer("P1")


class RemovalWithOffers(OfferCase):
    def setUp(self):
        super().setUp()
        self.check = offer_check(self.offers, self.clock)
        self.rentals = StubRentals()

    def remove(self, number, role=M, rentals=None, check=None):
        return remove_space(self.registers, rentals or self.rentals, check or self.check,
                            role, number)

    def assert_removal_refused_and_unchanged(self, error, number, **kwargs):
        register_before, listing_before = list_register(self.registers), self.listing()
        saves = self.offers.saves
        with self.assertRaises(error) as caught:
            self.remove(number, **kwargs)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())
        self.assertEqual(saves, self.offers.saves)
        return caught.exception

    def test_an_open_offer_refuses_the_removal_as_space_offered_and_other_spaces_go(self):
        self.offer()
        refused = self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, " p1 ")
        self.assertIsInstance(refused, refusals.Refusal)
        self.remove("P3")
        self.assertEqual(["P1", "p2", "P10"], [s for e in list_register(self.registers)
                                              for s in e.spaces])

    def test_removal_is_allowed_once_the_offer_is_withdrawn(self):
        self.offer()
        withdraw_offer(self.registers, self.offers, self.clock, O, withdrawal())
        self.assertIsNone(self.remove("P1"))
        self.assertNotIn("P1", [s for e in list_register(self.registers) for s in e.spaces])

    def test_with_two_offers_the_removal_waits_for_both_withdrawals(self):
        self.offer()
        self.offer(start="2026-12-01", end="2026-12-05")
        withdraw_offer(self.registers, self.offers, self.clock, O, withdrawal(number=1))
        self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")
        withdraw_offer(self.registers, self.offers, self.clock, O, withdrawal(number=2))
        self.remove("P1")

    def test_an_offer_is_not_a_rental_and_a_rental_is_asked_first(self):
        self.offer()
        refused = self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")
        self.assertNotIsInstance(refused, refusals.SpaceRentedRefused)
        unasked = FailingOffers(RuntimeError("the offers must not be asked"))
        self.assert_removal_refused_and_unchanged(refusals.SpaceRentedRefused, "P1",
                                                  rentals=StubRentals("P1"), check=unasked)
        self.assertEqual([], unasked.asked)

    def test_a_rental_without_an_offer_is_still_refused_as_rented(self):
        self.assert_removal_refused_and_unchanged(refusals.SpaceRentedRefused, "P3",
                                                  rentals=StubRentals("P3"))

    def test_an_offer_ended_yesterday_does_not_block_and_is_not_purged(self):
        self.offer()
        self.clock.day = date(2026, 11, 26)
        self.remove("P1")
        self.assertEqual([1], [o.number for o in self.offers.load().offers()])

    def test_an_offer_ending_today_or_starting_later_blocks(self):
        self.offer()
        self.clock.day = date(2026, 11, 25)
        self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")
        self.clock.day = TODAY
        self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")

    def test_one_ended_and_one_open_offer_of_the_space_block(self):
        self.offer()
        self.clock.day = date(2026, 11, 26)
        self.offer(start="2026-11-27", end="2026-11-30")
        self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")

    def test_unreadable_offers_end_the_removal_with_a_store_error_and_nothing_is_removed(self):
        before = list_register(self.registers)
        with self.assertRaises(refusals.OffersUnreadable) as caught:
            self.remove("P1", check=offer_check(UnreadableOffers(), self.clock))
        self.assertNotIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(before, list_register(self.registers))

    def test_a_blank_number_and_an_unknown_space_are_refused_before_the_offers_are_read(self):
        unreadable = offer_check(UnreadableOffers(), self.clock)
        for number, reason in ((" ", refusals.BlankValueRefused),
                               (None, refusals.BlankValueRefused),
                               ("P7", refusals.UnknownSpaceRefused)):
            with self.assertRaises(reason):
                self.remove(number, check=unreadable)
        for role in (O, Role.RESIDENT, None):
            with self.assertRaises(refusals.ManagerOnly):
                self.remove("P1", role=role, check=unreadable)


class RenumberingWithOffers(OfferCase):
    def setUp(self):
        super().setUp()
        self.check = offer_check(self.offers, self.clock)

    def change(self, number, new_number, role=M, check=None):
        change_space_number(self.registers, check or self.check, role, number, new_number)

    def spaces(self):
        return [s for e in list_register(self.registers) for s in e.spaces]

    def assert_change_refused_and_unchanged(self, error, number, new_number, **kwargs):
        register_before, listing_before = list_register(self.registers), self.listing()
        saves = self.offers.saves
        with self.assertRaises(error) as caught:
            self.change(number, new_number, **kwargs)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())
        self.assertEqual(saves, self.offers.saves)
        return caught.exception

    def test_an_open_offer_refuses_the_renumbering_as_space_offered(self):
        self.offer()
        refused = self.assert_change_refused_and_unchanged(refusals.SpaceOfferedRefused,
                                                           " p1 ", "P9")
        self.assertIsInstance(refused, refusals.Refusal)
        self.assertIn("P1", self.spaces())

    def test_a_same_value_or_case_only_change_of_an_offered_space_is_refused_too(self):
        self.offer()
        for new_number in ("P1", "p1", " P1 "):
            self.assert_change_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1",
                                                     new_number)

    def test_without_an_offer_a_same_value_change_is_accepted_and_stores_the_new_text(self):
        self.change("P1", "p1")
        self.assertIn("p1", self.spaces())

    def test_another_space_is_renumbered_while_p1_has_an_offer(self):
        self.offer()
        self.change("P3", "P7")
        self.assertIn("P7", self.spaces())

    def test_the_renumbering_is_allowed_once_the_offer_is_withdrawn_or_ended(self):
        self.offer()
        withdraw_offer(self.registers, self.offers, self.clock, O, withdrawal())
        self.change("P1", "P9")
        self.offer(space="P9", start="2026-12-01", end="2026-12-05")
        self.clock.day = date(2026, 12, 6)
        self.change("P9", "P11")
        self.assertIn("P11", self.spaces())

    def test_the_register_refusals_come_before_space_offered(self):
        self.offer()
        self.offer(space="p2", start="2026-12-01", end="2026-12-05")
        unreadable = offer_check(UnreadableOffers(), self.clock)
        for number, new_number, reason in (("P1", " ", refusals.BlankValueRefused),
                                           ("P7", None, refusals.BlankValueRefused),
                                           ("P7", "P9", refusals.UnknownSpaceRefused),
                                           ("P1", "P3", refusals.DuplicateSpaceRefused)):
            self.assert_change_refused_and_unchanged(reason, number, new_number)
            self.assert_change_refused_and_unchanged(reason, number, new_number,
                                                     check=unreadable)

    def test_any_other_role_is_refused_first_even_with_unreadable_offers(self):
        unreadable = offer_check(UnreadableOffers(), self.clock)
        for role in (O, Role.RESIDENT, None, "manager"):
            self.assert_change_refused_and_unchanged(refusals.ManagerOnly, "P1", "P9",
                                                     role=role, check=unreadable)

    def test_unreadable_offers_end_a_valid_renumbering_and_the_register_is_unchanged(self):
        before = list_register(self.registers)
        with self.assertRaises(refusals.OffersUnreadable) as caught:
            self.change("P1", "P9", check=offer_check(UnreadableOffers(), self.clock))
        self.assertNotIsInstance(caught.exception, refusals.Refusal)
        self.assertEqual(before, list_register(self.registers))

    def test_an_offers_check_that_raises_another_error_propagates(self):
        before = list_register(self.registers)
        with self.assertRaises(RuntimeError):
            self.change("P1", "P9", check=FailingOffers(RuntimeError("boom")))
        self.assertEqual(before, list_register(self.registers))

    def test_the_offers_are_read_once_and_only_after_the_register_checks_passed(self):
        loads = self.offers.loads
        self.change("P1", "P9")
        self.assertEqual(loads + 1, self.offers.loads)
        loads = self.offers.loads
        for number, new_number in (("P7", "P8"), ("P3", "P9"), (" ", "P5")):
            with self.assertRaises(refusals.Refusal):
                self.change(number, new_number)
        self.assertEqual(loads, self.offers.loads)


class OrphanOffersAlreadyStored(OfferCase):
    """A file written before S4 may hold an offer on a number the register does not hold (D-69)."""

    def setUp(self):
        super().setUp()
        self.check = offer_check(self.offers, self.clock)
        self.orphan = self.store_orphan("P8")

    def test_the_orphan_is_neither_listed_nor_removable_nor_withdrawable(self):
        self.assertEqual([], self.listing())
        with self.assertRaises(refusals.UnknownSpaceRefused):
            remove_space(self.registers, StubRentals(), self.check, M, "P8")
        with self.assertRaises(refusals.UnknownOfferRefused):
            withdraw_offer(self.registers, self.offers, self.clock, O,
                           withdrawal(offerer="Martin", number=self.orphan.number))

    def test_a_number_registered_again_brings_the_orphan_back_under_the_new_lot(self):
        register_space(self.registers, M, "P8", "B2")
        self.assertEqual([OfferEntry(1, "P8", "B2", "Martin", date(2026, 11, 20),
                                     date(2026, 11, 25))], self.listing())

    def test_it_then_blocks_removal_and_renumbering_until_its_owner_withdraws_it(self):
        register_space(self.registers, M, "P8", "B2")
        with self.assertRaises(refusals.SpaceOfferedRefused):
            remove_space(self.registers, StubRentals(), self.check, M, "P8")
        with self.assertRaises(refusals.SpaceOfferedRefused):
            change_space_number(self.registers, self.check, M, "P8", "P9")
        self.assertEqual(1, withdraw_offer(self.registers, self.offers, self.clock, O,
                                           withdrawal(offerer="martin", number=1)).number)
        change_space_number(self.registers, self.check, M, "P8", "P9")
        remove_space(self.registers, StubRentals(), self.check, M, "P9")
