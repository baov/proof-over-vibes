import bootstrap  # noqa: F401  (must come first)
import unittest

from copro_parking.domain.errors import (BlankValue, DuplicateLot,
                                         DuplicateSpace, UnknownLot,
                                         UnknownSpace)
from copro_parking.domain.register import Register


class RegisterRules(unittest.TestCase):
    def test_a_lot_keeps_its_trimmed_text_and_its_owner(self):
        register = Register()
        lot = register.add_lot("  a12 ", " Durand ")
        self.assertEqual(("a12", "Durand"), (lot.identifier, lot.owner.name))

    def test_a_lot_identifier_is_compared_ignoring_case_and_spaces(self):
        register = Register()
        register.add_lot("A12", "Durand")
        with self.assertRaises(DuplicateLot):
            register.add_lot(" a12 ", "Martin")

    def test_a_space_number_is_unique_across_lots(self):
        register = Register()
        register.add_lot("A12", "Durand")
        register.add_lot("B1", "Martin")
        register.add_space("P1", "A12")
        with self.assertRaises(DuplicateSpace):
            register.add_space(" p1 ", "B1")

    def test_a_space_refers_to_the_lot_by_any_spelling(self):
        register = Register()
        register.add_lot("A12", "Durand")
        space = register.add_space("P1", " a12")
        self.assertEqual("A12", space.lot_identifier)

    def test_a_space_on_an_unknown_lot_is_refused(self):
        with self.assertRaises(UnknownLot):
            Register().add_space("P1", "Z9")

    def test_blank_or_missing_values_are_refused(self):
        register = Register()
        register.add_lot("A12", "Durand")
        for call in (lambda: register.add_lot("  ", "Durand"),
                     lambda: register.add_lot(None, "Durand"),
                     lambda: register.add_lot("B1", ""),
                     lambda: register.add_lot("B1", None),
                     lambda: register.add_space(" ", "A12"),
                     lambda: register.add_space(None, "A12"),
                     lambda: register.add_space("P1", "  "),
                     lambda: register.add_space("P1", None)):
            with self.assertRaises(BlankValue):
                call()

    def test_a_refused_lot_leaves_no_trace(self):
        register = Register()
        with self.assertRaises(BlankValue):
            register.add_lot("A12", " ")
        self.assertEqual([], register.lots())
        register.add_lot("A12", "Durand")

    def test_lots_and_spaces_are_sorted_whatever_the_registration_order(self):
        register = Register()
        register.add_lot("B2", "Martin")
        register.add_lot("A1", "Durand")
        register.add_space("P2", "A1")
        register.add_space("P1", "A1")
        lots = register.lots()
        self.assertEqual(["A1", "B2"], [l.identifier for l in lots])
        self.assertEqual(["P1", "P2"], [s.number for s in register.spaces_of(lots[0])])
        self.assertEqual([], register.spaces_of(lots[1]))


class Corrections(unittest.TestCase):
    def setUp(self):
        self.register = Register()
        self.register.add_lot("A12", "Durand")
        self.register.add_lot("B1", "Martin")
        self.register.add_space("P1", "A12")
        self.register.add_space("P2", "B1")

    def numbers(self, identifier):
        lot = next(l for l in self.register.lots() if l.identifier == identifier)
        return [s.number for s in self.register.spaces_of(lot)]

    def test_the_owner_of_a_lot_found_by_any_spelling_is_replaced(self):
        lot = self.register.change_owner(" a12 ", " Dupont ")
        self.assertEqual(("A12", "Dupont"), (lot.identifier, lot.owner.name))
        owners = {l.identifier: l.owner.name for l in self.register.lots()}
        self.assertEqual({"A12": "Dupont", "B1": "Martin"}, owners)
        self.assertEqual(["P1"], self.numbers("A12"))

    def test_a_space_number_is_replaced_and_the_space_stays_on_its_lot(self):
        space = self.register.change_space_number(" p1 ", " P9 ")
        self.assertEqual(("P9", "A12"), (space.number, space.lot_identifier))
        self.assertEqual(["P9"], self.numbers("A12"))
        self.assertEqual(["P2"], self.numbers("B1"))
        self.register.add_space("P1", "B1")

    def test_a_renamed_space_is_found_by_its_new_number_only(self):
        self.register.change_space_number("P1", "P9")
        with self.assertRaises(UnknownSpace):
            self.register.change_space_number("P1", "P3")
        with self.assertRaises(DuplicateSpace):
            self.register.add_space("p9", "A12")

    def test_a_number_may_become_its_own_in_another_case(self):
        self.register.change_space_number("P1", "p1")
        self.assertEqual(["p1"], self.numbers("A12"))

    def test_a_number_already_used_on_any_lot_is_refused_and_nothing_moves(self):
        with self.assertRaises(DuplicateSpace):
            self.register.change_space_number("P1", " p2 ")
        self.assertEqual(["P1"], self.numbers("A12"))
        self.assertEqual(["P2"], self.numbers("B1"))

    def test_blank_or_missing_corrections_are_refused_and_nothing_changes(self):
        for value in (None, "", "   "):
            with self.assertRaises(BlankValue):
                self.register.change_owner("A12", value)
            with self.assertRaises(BlankValue):
                self.register.change_space_number("P1", value)
        self.assertEqual("Durand", self.register.lots()[0].owner.name)
        self.assertEqual(["P1"], self.numbers("A12"))

    def test_an_unknown_target_is_refused(self):
        with self.assertRaises(UnknownLot):
            self.register.change_owner("Z9", "X")
        with self.assertRaises(UnknownSpace):
            self.register.change_space_number("P7", "P8")

    def test_blank_is_checked_before_unknown_and_unknown_before_duplicate(self):
        with self.assertRaises(BlankValue):
            self.register.change_owner("Z9", " ")
        with self.assertRaises(BlankValue):
            self.register.change_space_number("P7", " ")
        with self.assertRaises(UnknownSpace):
            self.register.change_space_number("P7", "P2")


class Removal(unittest.TestCase):
    def setUp(self):
        self.register = Register()
        self.register.add_lot("A12", "Durand")
        self.register.add_lot("B1", "Martin")
        self.register.add_space("P1", "A12")
        self.register.add_space("P2", "B1")

    def numbers(self, identifier):
        lot = next(l for l in self.register.lots() if l.identifier == identifier)
        return [s.number for s in self.register.spaces_of(lot)]

    def test_a_space_is_found_by_any_spelling_with_its_stored_text(self):
        space = self.register.space(" p1 ")
        self.assertEqual(("P1", "A12"), (space.number, space.lot_identifier))

    def test_a_blank_or_unknown_space_is_refused_blank_first(self):
        for value in (None, "", "   "):
            with self.assertRaises(BlankValue):
                self.register.space(value)
        with self.assertRaises(UnknownSpace):
            self.register.space("P7")

    def test_a_removed_space_leaves_its_lot_and_the_others_untouched(self):
        self.register.remove_space(" p1 ")
        self.assertEqual([], self.numbers("A12"))
        self.assertEqual(["P2"], self.numbers("B1"))
        self.assertEqual(["A12", "B1"], [l.identifier for l in self.register.lots()])
        self.assertEqual("Durand", self.register.lots()[0].owner.name)

    def test_a_removed_number_is_free_again_and_no_longer_found(self):
        self.register.remove_space("P1")
        with self.assertRaises(UnknownSpace):
            self.register.space("P1")
        with self.assertRaises(UnknownSpace):
            self.register.remove_space("P1")
        self.register.add_space("p1", "B1")
        self.assertEqual(["p1", "P2"], self.numbers("B1"))

    def test_a_blank_or_unknown_removal_changes_nothing(self):
        for value in (None, " ", "P7"):
            with self.assertRaises((BlankValue, UnknownSpace)):
                self.register.remove_space(value)
        self.assertEqual(["P1"], self.numbers("A12"))
        self.assertEqual(["P2"], self.numbers("B1"))


class NaturalOrder(unittest.TestCase):
    def test_digits_are_compared_as_numbers_and_case_is_ignored(self):
        register = Register()
        for identifier in ("A10", "a2", "a1"):
            register.add_lot(identifier, "X")
        for number in ("P10", "p2", "P1"):
            register.add_space(number, "a1")
        lots = register.lots()
        self.assertEqual(["a1", "a2", "A10"], [l.identifier for l in lots])
        self.assertEqual(["P1", "p2", "P10"],
                         [s.number for s in register.spaces_of(lots[0])])

    def test_text_before_digits_still_orders_first(self):
        register = Register()
        for identifier in ("B1", "A20", "A3", "A"):
            register.add_lot(identifier, "X")
        self.assertEqual(["A", "A3", "A20", "B1"],
                         [l.identifier for l in register.lots()])

    def test_the_lot_of_a_space_is_found_ignoring_case_and_spaces(self):
        register = Register()
        register.add_lot("A12", "Durand")
        register.add_space("P1", "a12")
        self.assertEqual(("A12", "Durand"),
                         (register.lot_of(" p1 ").identifier, register.lot_of("P1").owner.name))

    def test_the_lot_of_an_unknown_or_blank_space_is_refused(self):
        register = Register()
        with self.assertRaises(UnknownSpace):
            register.lot_of("P1")
        with self.assertRaises(BlankValue):
            register.lot_of(" ")

    def test_the_lot_of_a_space_shows_the_owner_after_a_correction(self):
        register = Register()
        register.add_lot("A12", "Durand")
        register.add_space("P1", "A12")
        register.change_owner("A12", "Martin")
        self.assertEqual("Martin", register.lot_of("P1").owner.name)
