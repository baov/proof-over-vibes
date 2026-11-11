"""Refusals: one named application error per reason (D-14)."""


class Refusal(Exception):
    """Base of every refusal; the register is unchanged when one is raised."""


class ManagerOnly(Refusal):
    """Only the manager may change the register."""


class BlankValueRefused(Refusal):
    """An identifier, a number or an owner name is missing or blank."""


class DuplicateLotRefused(Refusal):
    """The lot identifier is already registered."""


class DuplicateSpaceRefused(Refusal):
    """The space number is already registered."""


class UnknownLotRefused(Refusal):
    """The lot of the space is not registered."""


class UnknownSpaceRefused(Refusal):
    """The space to correct is not registered."""


class SpaceRentedRefused(Refusal):
    """The space has a rental, existing or planned, and cannot be removed."""


class StoreUnreadable(Exception):
    """The stored register is corrupt or malformed (D-19).

    Not a Refusal: no rule of the register was broken, the store itself is
    unusable. Raised on every read and write; the file is never overwritten.
    """


class UnknownKindRefused(Refusal):
    """The kind of the rule is not on the closed list."""


class NoBoundRefused(Refusal):
    """A duration rule needs a minimum, a maximum or both."""


class InvalidDaysRefused(Refusal):
    """A bound is not a whole number of days above zero."""


class MinimumAboveMaximumRefused(Refusal):
    """The minimum is above the maximum."""


class InvalidParameterRefused(Refusal):
    """The parameter is not a mapping or has an unknown key."""


class DuplicateRuleRefused(Refusal):
    """The rule name is already registered."""


class UnknownRuleRefused(Refusal):
    """The rule to change or remove is not registered."""


class RulesUnreadable(StoreUnreadable):
    """The stored rules are corrupt or malformed (D-19, D-35)."""
