import bootstrap  # noqa: F401  (must come first)
from datetime import date

from copro_parking.application.ports import (Clock, OfferCheck, OfferRepository,
                                             RegisterRepository, RentalCheck,
                                             RuleRepository)
from copro_parking.domain.offers import Offer, OfferBook, Period
from copro_parking.domain.register import Register
from copro_parking.domain.rules import RuleSet


class InMemoryRepository(RegisterRepository):
    """Keeps the register in memory; stores a copy of the entries, like a file."""

    def __init__(self) -> None:
        self._entries: list[tuple] = []

    def load(self) -> Register:
        register = Register()
        for kind, first, second in self._entries:
            if kind == "lot":
                register.add_lot(first, second)
            else:
                register.add_space(first, second)
        return register

    def save(self, register: Register) -> None:
        self._entries = [("lot", l.identifier, l.owner.name) for l in register.lots()]
        for lot in register.lots():
            self._entries += [("space", s.number, lot.identifier)
                              for s in register.spaces_of(lot)]


class StubRentals(RentalCheck):
    """Answers "rented" for the given numbers and records every question asked."""

    def __init__(self, *rented: str) -> None:
        self._rented = set(rented)
        self.asked: list[str] = []

    def has_rental(self, space_number: str) -> bool:
        self.asked.append(space_number)
        return space_number in self._rented


class StubOffers(OfferCheck):
    """Answers "has an open offer" for the given numbers and records every question asked."""

    def __init__(self, *offered: str) -> None:
        self._offered = set(offered)
        self.asked: list[str] = []

    def has_open_offer(self, space_number: str) -> bool:
        self.asked.append(space_number)
        return space_number in self._offered


class FailingOffers(OfferCheck):
    """Raises the given error when asked: an offers store that cannot answer."""

    def __init__(self, error: Exception) -> None:
        self._error = error
        self.asked: list[str] = []

    def has_open_offer(self, space_number: str) -> bool:
        self.asked.append(space_number)
        raise self._error


class InMemoryRuleRepository(RuleRepository):
    """Keeps the rules in memory; stores a copy of the entries, like a file."""

    def __init__(self) -> None:
        self._entries: list[tuple] = []
        self.loads = 0
        self.saves = 0

    def load(self) -> RuleSet:
        self.loads += 1
        rules = RuleSet()
        for name, kind, parameter, note in self._entries:
            rules.add(name, kind, dict(parameter), note)
        return rules

    def save(self, rules: RuleSet) -> None:
        self.saves += 1
        self._entries = [(r.name, r.kind, r.condition.parameter(), r.note)
                         for r in rules.in_registration_order()]


class FixedClock(Clock):
    """Always answers the same day; a test moves it by assigning `day`."""

    def __init__(self, day: date) -> None:
        self.day = day
        self.reads = 0

    def today(self) -> date:
        self.reads += 1
        return self.day


class InMemoryOfferRepository(OfferRepository):
    """Keeps the offers in memory; stores a copy of the entries, like a file."""

    def __init__(self) -> None:
        self._next_number = 1
        self._entries: list[tuple] = []
        self.loads = 0
        self.saves = 0

    def load(self) -> OfferBook:
        self.loads += 1
        return OfferBook.restore(
            [Offer(n, space, Period(start, end)) for n, space, start, end in self._entries],
            self._next_number)

    def save(self, book: OfferBook) -> None:
        self.saves += 1
        self._next_number = book.next_number
        self._entries = [(o.number, o.space_number, o.period.start, o.period.end)
                         for o in book.offers()]
