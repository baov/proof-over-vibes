"""Rules: a named condition of a kind from a closed list, with a source note."""
from dataclasses import dataclass

from .errors import (DuplicateRule, InvalidDays, InvalidParameter,
                     MinimumAboveMaximum, NoBound, UnknownKind, UnknownRule)
from .text import clean, key, natural_key


def _days(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise InvalidDays(repr(value))
    return value


@dataclass(frozen=True)
class DurationBounds:
    """A minimum and/or a maximum number of days; `None` is no bound."""
    minimum: int | None
    maximum: int | None
    kind = "duration_bounds"

    @classmethod
    def from_parameter(cls, parameter: object) -> "DurationBounds":
        if parameter is None:
            parameter = {}
        if not isinstance(parameter, dict) or not set(parameter) <= {"minimum", "maximum"}:
            raise InvalidParameter(repr(parameter))
        minimum = _days(parameter.get("minimum"))
        maximum = _days(parameter.get("maximum"))
        if minimum is None and maximum is None:
            raise NoBound("a duration rule needs at least one bound")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise MinimumAboveMaximum(f"{minimum} > {maximum}")
        return cls(minimum, maximum)

    def parameter(self) -> dict:
        return {"minimum": self.minimum, "maximum": self.maximum}


KINDS = {DurationBounds.kind: DurationBounds}
"""The only list of kinds: a new kind is a class plus one line here."""


@dataclass(frozen=True)
class Rule:
    name: str
    condition: DurationBounds
    note: str | None

    @property
    def kind(self) -> str:
        return self.condition.kind


def _note(value: object) -> str | None:
    """The trimmed note; blank text means no note, a non-text note is refused."""
    if value is None:
        return None
    if not isinstance(value, str):
        clean(value)
    return value.strip() or None


def _condition(kind: object, parameter: object) -> DurationBounds:
    if not isinstance(kind, str) or kind not in KINDS:
        raise UnknownKind(repr(kind))
    return KINDS[kind].from_parameter(parameter)


class RuleSet:
    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}

    def add(self, name: object, kind: object, parameter: object,
            note: object = None) -> None:
        name = clean(name)
        condition = _condition(kind, parameter)
        if key(name) in self._rules:
            raise DuplicateRule(name)
        self._rules[key(name)] = Rule(name, condition, _note(note))

    def change(self, name: object, parameter: object = None,
               note: object = None) -> None:
        old = self._rules.get(key(clean(name)))
        if old is None:
            raise UnknownRule(name)
        condition = (old.condition if parameter is None
                     else _condition(old.kind, parameter))
        if note is None:
            new_note = old.note
        else:
            new_note = _note(note)
        self._rules[key(old.name)] = Rule(old.name, condition, new_note)

    def remove(self, name: object) -> None:
        if self._rules.pop(key(clean(name)), None) is None:
            raise UnknownRule(name)

    def in_registration_order(self) -> list[Rule]:
        return list(self._rules.values())

    def rules(self) -> list[Rule]:
        """Rules in natural name order; the sort is stable, so ties keep registration order."""
        return sorted(self._rules.values(), key=lambda rule: natural_key(rule.name))
