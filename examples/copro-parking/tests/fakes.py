import bootstrap  # noqa: F401  (must come first)
from copro_parking.application.ports import (RegisterRepository, RentalCheck,
                                             RuleRepository)
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
