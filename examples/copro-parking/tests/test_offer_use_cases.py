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
from copro_parking.application.ports import OfferRepository, RegisterRepository
from copro_parking.application.role import Role
from copro_parking.domain import errors
from copro_parking.domain.errors import OverlappingOffer
from copro_parking.domain.offers import Offer, OfferBook, Period
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


def withdrawal(offerer="Durand", number=1):
    return WithdrawRequest(offerer, number)


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
        self.assertEqual({"space", "offerer", "start", "end"}, set(OfferRequest.__dataclass_fields__))
        self.assertEqual({"number", "space", "lot", "owner", "start", "end"},
                         set(OfferEntry.__dataclass_fields__))


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

    def test_an_offer_whose_space_is_not_registered_is_not_listed(self):
        self.offer(space="P1")
        self.offer(space="P3", offerer="Martin")
        self.store_orphan("P8")
        self.assertEqual(["P1", "P3"], [e.space for e in self.listing()])


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
                    20261120, 5.5, True, ["2026-11-20"], datetime(2026, 11, 20, 9, 30)):
            for field in ("start", "end"):
                with self.subTest(bad=bad, field=field):
                    self.assert_refused_and_unchanged(
                        refusals.InvalidPeriodRefused, **{field: bad})

    def test_dates_are_date_objects_or_iso_text_with_surrounding_spaces_ignored(self):
        entry = self.offer(start=date(2026, 11, 20), end=" 2026-11-25 ")
        self.assertEqual((date(2026, 11, 20), date(2026, 11, 25)), (entry.start, entry.end))

    def test_a_start_before_today_is_refused_and_a_start_equal_to_today_is_accepted(self):
        self.assert_refused_and_unchanged(
            refusals.InvalidPeriodRefused, start="2026-11-10", end="2026-11-30")
        self.assertEqual(TODAY, self.offer(start="2026-11-11", end="2026-11-11").start)
        self.clock.day = date(2026, 12, 1)  # today is whatever the clock says
        self.assert_refused_and_unchanged(
            refusals.InvalidPeriodRefused, start="2026-11-20", end="2026-12-05")
        self.assertEqual(2, self.offer(start="2026-12-01", end="2026-12-05").number)


class OwnerAndSpaceRules(OfferCase):
    def test_an_unknown_space_is_refused(self):
        self.assert_refused_and_unchanged(refusals.UnknownSpaceRefused, space="P99")

    def test_an_offerer_that_is_not_the_lot_owner_is_refused_and_an_owner_of_another_lot_too(self):
        self.assert_refused_and_unchanged(refusals.NotTheOwner, offerer="Dupont")
        self.assert_refused_and_unchanged(refusals.NotTheOwner, space="P3", offerer="Durand")
        self.assert_refused_and_unchanged(refusals.NotTheOwner, space="P1", offerer="Martin")

    def test_blank_missing_or_non_text_space_or_offerer_is_refused_as_invalid_input(self):
        for bad in ("", "   ", None, 5, ["P1"]):
            for field in ("space", "offerer"):
                with self.subTest(bad=bad, field=field):
                    self.assert_refused_and_unchanged(
                        refusals.BlankValueRefused, **{field: bad})

    def test_the_owner_check_states_that_a_declared_name_is_not_an_authentication(self):
        """Kept for D-46: the limit of the owner check must be written down in the code."""
        for doc in (offer_space.__doc__, _require_owner.__doc__):
            self.assertIn("not an authentication", doc)


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
                self.assertIn("1", str(caught.exception))

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
        overlapping = dict(start="2026-11-22", end="2026-11-23")
        self.assert_refused_and_unchanged(refusals.NotAllowedToOffer, role=M, **overlapping)
        self.assert_refused_and_unchanged(refusals.InvalidPeriodRefused,
                                          start="2026-11-22", end="2026-11-21")
        self.assert_refused_and_unchanged(refusals.BlankValueRefused, offerer=" ", **overlapping)
        self.assert_refused_and_unchanged(refusals.UnknownSpaceRefused, space="P99", **overlapping)
        self.assert_refused_and_unchanged(refusals.NotTheOwner, offerer="Dupont", **overlapping)
        self.assert_refused_and_unchanged(refusals.OverlapRefused, **overlapping)

    def test_an_overlap_refusal_changes_nothing_and_the_next_offer_gets_the_number_it_would_have_had(self):
        self.offer_p1("2026-11-20", "2026-11-24")
        self.assert_refused_and_unchanged(refusals.OverlapRefused,
                                          start="2026-11-22", end="2026-11-23")
        self.assertEqual(2, self.offer_p1("2026-12-01", "2026-12-02").number)
        self.assertEqual([1, 2], [e.number for e in self.listing()])


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
        with self.assertRaises(error):
            self.withdraw(role, **fields)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())


class RulesSharedByOfferAndWithdraw(WithdrawCase):
    """The rules both use cases apply, tested once over a table of the two (offer 1 is open)."""

    KINDS = ("offer", "withdraw")
    ROLES = (M, Role.RESIDENT, None, "owner", 3)
    # Faults by tier, most urgent first; each is (expected refusal, request fields).
    FAULTS = {
        "offer": (
            ((refusals.NotAllowedToOffer, {"role": M}),),
            ((refusals.InvalidPeriodRefused, dict(start="2026-11-20", end="2026-11-19")),
             (refusals.BlankValueRefused, dict(offerer=" ")),
             (refusals.BlankValueRefused, dict(space=" "))),
            ((refusals.UnknownSpaceRefused, dict(space="P99")),),
            ((refusals.NotTheOwner, dict(offerer="Dupont")),)),
        "withdraw": (
            ((refusals.NotAllowedToOffer, {"role": M}),),
            ((refusals.InvalidOfferNumberRefused, dict(number=0)),
             (refusals.BlankValueRefused, dict(offerer=" "))),
            ((refusals.UnknownOfferRefused, dict(number=99)),),
            ((refusals.NotTheOwner, dict(offerer="Dupont")),)),
    }

    def attempt(self, kind, role=O, **fields):
        if kind == "offer":  # a period free of offer 1, so that only the fault under test refuses
            return self.offer(role, **{"start": "2026-12-01", "end": "2026-12-05", **fields})
        return self.withdraw(role, **fields)

    def refused_and_unchanged(self, kind, error, role=O, **fields):
        register_before, listing_before = list_register(self.registers), self.listing()
        with self.assertRaises(error):
            self.attempt(kind, role, **fields)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())

    def test_any_role_other_than_owner_is_refused_first_whatever_the_request_and_the_stores(self):
        calls = {
            "offer": lambda role: offer_space(
                UnreadableRegister(), UnreadableOffers(), self.clock, role,
                request(start="nope", end=None, space=" ", offerer=None)),
            "withdraw": lambda role: withdraw_offer(
                UnreadableRegister(), UnreadableOffers(), self.clock, role,
                withdrawal(offerer=None, number="x"))}
        for kind in self.KINDS:
            for role in self.ROLES:
                with self.subTest(kind=kind, role=role):
                    self.refused_and_unchanged(kind, refusals.NotAllowedToOffer, role=role)
                    with self.assertRaises(refusals.NotAllowedToOffer):
                        calls[kind](role)

    def test_refusals_are_reported_in_the_order_role_invalid_input_unknown_target_not_the_owner(self):
        for kind, tiers in self.FAULTS.items():
            for index, higher in enumerate(tiers):
                for lower in tiers[index + 1:]:
                    for error, high_fields in higher:
                        for _, low_fields in lower:
                            with self.subTest(kind=kind, error=error.__name__,
                                              high=high_fields, low=low_fields):
                                fields = {**low_fields, **high_fields}
                                role = fields.pop("role", O)
                                self.refused_and_unchanged(kind, error, role=role, **fields)

    def test_the_owner_name_is_compared_ignoring_case_and_surrounding_spaces(self):
        for kind in self.KINDS:
            with self.subTest(kind=kind):
                self.assertEqual("Durand", self.attempt(kind, offerer="  dURAND ").owner)

    def test_after_a_correction_of_the_lot_owner_only_the_new_name_may_offer_or_withdraw(self):
        change_lot_owner(self.registers, M, "A12", "Moreau")
        for kind in self.KINDS:
            with self.subTest(kind=kind):
                self.refused_and_unchanged(kind, refusals.NotTheOwner, offerer="Durand")
                self.assertEqual("Moreau", self.attempt(kind, offerer=" moreau ").owner)

    def test_neither_use_case_touches_the_register(self):
        before = list_register(self.registers)
        for kind in self.KINDS:
            self.attempt(kind)
        self.assertEqual(before, list_register(self.registers))

    def test_invalid_input_and_ownership_refusals_come_before_any_store_is_read(self):
        unreadable = UnreadableOffers()
        cases = [(lambda: offer_space(self.registers, unreadable, self.clock, O, request(end="2026-11-01")),
                  refusals.InvalidPeriodRefused),
                 (lambda: offer_space(self.registers, unreadable, self.clock, O, request(space="P99")),
                  refusals.UnknownSpaceRefused),
                 (lambda: offer_space(self.registers, unreadable, self.clock, O, request(offerer="Dupont")),
                  refusals.NotTheOwner),
                 (lambda: withdraw_offer(UnreadableRegister(), unreadable, self.clock, O,
                                         withdrawal(offerer=" ")), refusals.BlankValueRefused),
                 (lambda: withdraw_offer(UnreadableRegister(), unreadable, self.clock, O,
                                         withdrawal(number=0)), refusals.InvalidOfferNumberRefused)]
        for call, error in cases:
            with self.subTest(error=error.__name__):
                with self.assertRaises(error):
                    call()

    def test_unreadable_offers_end_every_use_case_with_a_store_error_not_a_refusal(self):
        unreadable = UnreadableOffers()
        check = offer_check(unreadable, self.clock)
        calls = {
            "list": lambda: list_open_offers(self.registers, unreadable, self.clock),
            "offer": lambda: offer_space(self.registers, unreadable, self.clock, O, request()),
            "withdraw": lambda: withdraw_offer(self.registers, unreadable, self.clock, O, withdrawal()),
            "remove": lambda: remove_space(self.registers, StubRentals(), check, M, "P1"),
            "renumber": lambda: change_space_number(self.registers, check, M, "P1", "P9"),
            "check": lambda: check.has_open_offer("P1")}
        for name, call in calls.items():
            with self.subTest(use_case=name):
                before = list_register(self.registers)
                with self.assertRaises(refusals.OffersUnreadable) as caught:
                    call()
                self.assertIsInstance(caught.exception, refusals.StoreUnreadable)
                self.assertNotIsInstance(caught.exception, refusals.Refusal)
                self.assertEqual(before, list_register(self.registers))

    def test_an_unreadable_register_ends_every_use_case_with_a_store_error_and_nothing_is_saved(self):
        calls = {
            "list": lambda: list_open_offers(UnreadableRegister(), self.offers, self.clock),
            "offer": lambda: offer_space(UnreadableRegister(), self.offers, self.clock, O, request()),
            "withdraw": lambda: withdraw_offer(UnreadableRegister(), self.offers, self.clock, O,
                                               withdrawal())}
        for name, call in calls.items():
            with self.subTest(use_case=name):
                saves = self.offers.saves
                with self.assertRaises(refusals.StoreUnreadable) as caught:
                    call()
                self.assertNotIsInstance(caught.exception, refusals.Refusal)
                self.assertEqual(saves, self.offers.saves)
        self.assertEqual(1, len(self.listing()))


class WithdrawRules(WithdrawCase):
    def test_a_withdrawal_returns_the_entry_it_withdrew_as_the_listing_showed_it(self):
        shown = self.listing()[0]
        entry = self.withdraw()
        self.assertEqual(shown, entry)
        self.assertEqual(OfferEntry(1, "P1", "A12", "Durand", date(2026, 11, 20),
                                    date(2026, 11, 25)), entry)
        self.assertEqual([], self.listing())

    def test_withdrawing_one_of_three_offers_leaves_the_other_two_in_the_same_order(self):
        self.offer(start="2026-12-01", end="2026-12-05")
        self.offer(start="2026-12-10", end="2026-12-15")
        before = self.listing()
        self.withdraw(number=2)
        self.assertEqual([before[0], before[2]], self.listing())

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

    def test_any_open_offer_is_withdrawn_whatever_its_number_or_start_and_in_any_order(self):
        self.offer(start="2027-03-01", end="2027-03-10")
        self.offer(start="2026-12-10", end="2026-12-15")
        self.clock.day = date(2026, 11, 25)  # offer 1 ends today: still open
        self.assertEqual(3, self.withdraw(number=3).number)
        self.assertEqual(1, self.withdraw(number=1).number)
        self.assertEqual([2], [e.number for e in self.listing()])

    def test_a_number_that_is_not_an_open_offer_is_an_unknown_offer_for_any_name(self):
        orphan = self.store_orphan("P8")
        ended = self.offer(space="P3", offerer="Martin", start="2026-11-12", end="2026-11-12")
        self.offer(space="p2", start="2026-11-26", end="2026-11-27")
        self.withdraw(number=4)
        cases = {"never existed": (99, "Durand"), "withdrawn": (4, "Durand"),
                 "orphan": (orphan.number, "Durand"), "orphan other name": (orphan.number, "Dupont")}
        for label, (number, offerer) in cases.items():
            with self.subTest(label):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.UnknownOfferRefused, offerer=offerer, number=number)
        self.clock.day = date(2026, 11, 13)
        with self.subTest("end date has passed"):
            self.assert_withdraw_refused_and_unchanged(
                refusals.UnknownOfferRefused, offerer="Martin", number=ended.number)
        with self.subTest("it hides its context"):
            for number in (99, orphan.number, ended.number):
                with self.assertRaises(refusals.UnknownOfferRefused) as caught:
                    self.withdraw(number=number)
                self.assertIsNone(caught.exception.__cause__)
                self.assertTrue(caught.exception.__suppress_context__)

    def test_a_number_that_is_not_a_whole_number_from_one_is_refused_as_invalid_input(self):
        for bad in (None, "1", 1.0, 1.5, True, False, 0, -1, "", [1], (1,)):
            with self.subTest(bad=bad):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.InvalidOfferNumberRefused, number=bad)

    def test_a_blank_missing_or_non_text_offerer_is_refused_as_invalid_input(self):
        for bad in ("", "   ", None, 5, ["Durand"]):
            with self.subTest(bad=bad):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.BlankValueRefused, offerer=bad)

    def test_a_blank_offerer_is_reported_before_a_bad_number(self):
        for offerer in (" ", None):
            with self.subTest(offerer=offerer):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.BlankValueRefused, offerer=offerer, number=None)

    def test_a_name_that_is_not_the_owner_is_refused_and_the_offer_stays_listed(self):
        self.offer(space="P3", offerer="Martin")
        for offerer in ("Dupont", "Martin", "manager"):
            with self.subTest(offerer=offerer):
                self.assert_withdraw_refused_and_unchanged(
                    refusals.NotTheOwner, offerer=offerer)
        self.assert_withdraw_refused_and_unchanged(refusals.NotTheOwner, offerer="Durand", number=2)

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

    def test_withdraw_deletes_only_that_offer_and_keeps_expired_ones_and_the_next_number(self):
        book = self.book()
        withdrawn = book.withdraw(1, TODAY)
        self.assertEqual(1, withdrawn.number)
        self.assertEqual([2, 4], [o.number for o in book.offers()])
        self.assertEqual(5, book.next_number)
        with self.assertRaises(errors.UnknownOffer):
            book.withdraw(1, TODAY)

    def test_the_open_offers_of_a_stored_pair_with_the_same_start_are_ordered_by_number(self):
        period = Period(date(2026, 11, 20), date(2026, 11, 25))
        book = OfferBook.restore([Offer(2, "P1", period), Offer(1, "P1", period)], 3)
        self.assertEqual([1, 2], [o.number for o in book.open_offers(TODAY)])


class StoredOfferCheckQuestions(OfferCase):
    def setUp(self):
        super().setUp()
        self.check = offer_check(self.offers, self.clock)

    def test_a_space_has_an_open_offer_until_its_last_day_found_ignoring_case_and_spaces(self):
        self.assertIs(False, self.check.has_open_offer("P1"))  # no offer yet
        self.offer(space="p2")
        self.offer(start="2026-11-12", end="2026-11-12")
        self.offer(space="P3", offerer="Martin", start="2027-01-10", end="2027-01-12")
        for asked in ("p2", " P2 ", "P1", "P3"):
            with self.subTest(asked=asked):
                self.assertIs(True, self.check.has_open_offer(asked))  # today, later, ignoring case
        self.assertIs(False, self.check.has_open_offer("P10"))  # another space
        self.clock.day = date(2026, 11, 13)
        self.assertIs(False, self.check.has_open_offer("P1"))  # ended yesterday

    def test_it_follows_the_offers_file_between_two_questions(self):
        self.assertIs(False, self.check.has_open_offer("P1"))
        self.offer()
        self.assertIs(True, self.check.has_open_offer("P1"))


class RemovalWithOffers(OfferCase):
    def setUp(self):
        super().setUp()
        self.check = offer_check(self.offers, self.clock)
        self.rentals = StubRentals()

    def remove(self, number, role=M, rentals=None, check=None):
        return remove_space(self.registers, rentals or self.rentals, check or self.check,
                            role, number)

    def withdraw_offer_number(self, number):
        withdraw_offer(self.registers, self.offers, self.clock, O, withdrawal(number=number))

    def spaces(self):
        return [s for e in list_register(self.registers) for s in e.spaces]

    def assert_removal_refused_and_unchanged(self, error, number, **kwargs):
        register_before, listing_before = list_register(self.registers), self.listing()
        with self.assertRaises(error) as caught:
            self.remove(number, **kwargs)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())
        return caught.exception

    def test_an_open_offer_refuses_the_removal_as_space_offered_and_other_spaces_go(self):
        self.offer()
        self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, " p1 ")
        self.remove("P3")
        self.assertEqual(["P1", "p2", "P10"], self.spaces())

    def test_the_removal_waits_for_every_open_offer_of_the_space_to_be_withdrawn(self):
        self.offer()
        self.offer(start="2026-12-01", end="2026-12-05")
        self.withdraw_offer_number(1)
        self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")
        self.withdraw_offer_number(2)
        self.assertIsNone(self.remove("P1"))
        self.assertNotIn("P1", self.spaces())

    def test_an_offer_is_not_a_rental_and_a_rental_is_asked_first(self):
        self.offer()
        refused = self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")
        self.assertNotIsInstance(refused, refusals.SpaceRentedRefused)
        unasked = FailingOffers(RuntimeError("the offers must not be asked"))
        self.assert_removal_refused_and_unchanged(refusals.SpaceRentedRefused, "P1",
                                                  rentals=StubRentals("P1"), check=unasked)
        self.assertEqual([], unasked.asked)

    def test_an_offer_ended_yesterday_does_not_block_and_is_not_purged(self):
        self.offer()
        self.clock.day = date(2026, 11, 26)
        self.remove("P1")
        self.assertEqual([1], [o.number for o in self.offers.load().offers()])

    def test_an_offer_ending_today_or_starting_later_blocks_even_beside_an_ended_one(self):
        self.offer()
        for day in (date(2026, 11, 25), TODAY):
            self.clock.day = day
            self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")
        self.clock.day = date(2026, 11, 26)
        self.offer(start="2026-11-27", end="2026-11-30")
        self.assert_removal_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1")


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
        with self.assertRaises(error):
            self.change(number, new_number, **kwargs)
        self.assertEqual(register_before, list_register(self.registers))
        self.assertEqual(listing_before, self.listing())

    def test_an_open_offer_refuses_the_renumbering_as_space_offered_and_other_spaces_go(self):
        self.offer()
        self.assert_change_refused_and_unchanged(refusals.SpaceOfferedRefused, " p1 ", "P9")
        self.change("P3", "P7")
        self.assertIn("P7", self.spaces())

    def test_a_same_value_or_case_only_change_is_refused_only_while_the_space_is_offered(self):
        self.change("P1", "p1")
        self.assertIn("p1", self.spaces())
        self.offer(space="p1")
        for new_number in ("P1", "p1", " P1 "):
            self.assert_change_refused_and_unchanged(refusals.SpaceOfferedRefused, "P1", new_number)

    def test_the_renumbering_is_allowed_once_the_offer_is_withdrawn_or_ended(self):
        self.offer()
        withdraw_offer(self.registers, self.offers, self.clock, O, withdrawal())
        self.change("P1", "P9")
        self.offer(space="P9", start="2026-12-01", end="2026-12-05")
        self.clock.day = date(2026, 12, 6)
        self.change("P9", "P11")
        self.assertIn("P11", self.spaces())


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

    def test_a_number_registered_again_brings_the_orphan_back_and_blocks_until_its_owner_withdraws_it(self):
        register_space(self.registers, M, "P8", "B2")
        self.assertEqual([OfferEntry(1, "P8", "B2", "Martin", date(2026, 11, 20),
                                     date(2026, 11, 25))], self.listing())
        with self.assertRaises(refusals.SpaceOfferedRefused):
            remove_space(self.registers, StubRentals(), self.check, M, "P8")
        with self.assertRaises(refusals.SpaceOfferedRefused):
            change_space_number(self.registers, self.check, M, "P8", "P9")
        self.assertEqual(1, withdraw_offer(self.registers, self.offers, self.clock, O,
                                           withdrawal(offerer="martin", number=1)).number)
        change_space_number(self.registers, self.check, M, "P8", "P9")
        remove_space(self.registers, StubRentals(), self.check, M, "P9")


if __name__ == "__main__":
    unittest.main()
