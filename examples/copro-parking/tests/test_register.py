import bootstrap  # noqa: F401  (must come first)
import unittest

from copro_parking.domain.errors import (BlankValue, DuplicateSpace,
                                         UnknownSpace)
from copro_parking.domain.register import Register

# The rules of the register that a use case already shows (duplicates, blanks, unknown targets,
# sorting, trimmed text) are tested through the use cases; this file keeps what only the domain
# can show.


class RegisterRules(unittest.TestCase):
    def test_a_space_refers_to_the_lot_by_any_spelling(self):
        register = Register()
        register.add_lot("A12", "Durand")
        space = register.add_space("P1", " a12")
        self.assertEqual("A12", space.lot_identifier)

    def test_a_refused_lot_leaves_no_trace(self):
        register = Register()
        with self.assertRaises(BlankValue):
            register.add_lot("A12", " ")
        self.assertEqual([], register.lots())
        register.add_lot("A12", "Durand")


    def test_every_registration_and_correction_returns_the_entry_it_stored(self):
        register = Register()
        lot = register.add_lot("  a12 ", " Durand ")
        self.assertEqual(("a12", "Durand"), (lot.identifier, lot.owner.name))
        space = register.add_space(" P1 ", "A12")
        self.assertEqual(("P1", "a12"), (space.number, space.lot_identifier))
        lot = register.change_owner(" A12 ", " Dupont ")
        self.assertEqual(("a12", "Dupont"), (lot.identifier, lot.owner.name))
        space = register.change_space_number(" p1 ", " P9 ")
        self.assertEqual(("P9", "a12"), (space.number, space.lot_identifier))


class Corrections(unittest.TestCase):
    def setUp(self):
        self.register = Register()
        self.register.add_lot("A12", "Durand")
        self.register.add_lot("B1", "Martin")
        self.register.add_space("P1", "A12")
        self.register.add_space("P2", "B1")

    def test_a_renamed_space_is_found_by_its_new_number_only_and_its_old_number_is_free(self):
        self.register.change_space_number("P1", "P9")
        with self.assertRaises(UnknownSpace):
            self.register.change_space_number("P1", "P3")
        with self.assertRaises(DuplicateSpace):
            self.register.add_space("p9", "A12")
        self.register.add_space("P1", "B1")

    def test_blank_is_checked_before_unknown_and_unknown_before_duplicate(self):
        from copro_parking.domain.errors import UnknownLot
        with self.assertRaises(BlankValue):
            self.register.change_owner("Z9", " ")
        with self.assertRaises(BlankValue):
            self.register.change_space_number("P7", " ")
        with self.assertRaises(UnknownSpace):
            self.register.change_space_number("P7", "P2")
        with self.assertRaises(UnknownLot):
            self.register.change_owner("Z9", "X")


class Removal(unittest.TestCase):
    def test_a_blank_or_unknown_space_is_refused_blank_first(self):
        register = Register()
        for value in (None, "", "   "):
            with self.assertRaises(BlankValue):
                register.space(value)
        with self.assertRaises(UnknownSpace):
            register.space("P7")


class NaturalOrder(unittest.TestCase):
    def test_digits_are_compared_as_numbers_and_case_is_ignored(self):
        register = Register()
        for identifier in ("A10", "a2", "a1", "B1", "A20", "A3", "A"):
            register.add_lot(identifier, "X")
        for number in ("P10", "p2", "P1"):
            register.add_space(number, "a1")
        lots = register.lots()
        self.assertEqual(["A", "a1", "a2", "A3", "A10", "A20", "B1"], [l.identifier for l in lots])
        self.assertEqual(["P1", "p2", "P10"],
                         [s.number for s in register.spaces_of(register.lots()[1])])

    def test_the_lot_of_a_space_is_found_ignoring_case_and_spaces(self):
        register = Register()
        register.add_lot("A12", "Durand")
        register.add_space("P1", "a12")
        self.assertEqual(("A12", "Durand"),
                         (register.lot_of(" p1 ").identifier, register.lot_of("P1").owner.name))
