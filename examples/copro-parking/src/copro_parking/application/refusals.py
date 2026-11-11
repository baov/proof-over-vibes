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


class NotAllowedToOffer(Refusal):
    """Only an owner may offer a space."""


class NotTheOwner(Refusal):
    """The offerer is not the owner of the space's lot."""


class InvalidPeriodRefused(Refusal):
    """A date is missing or unreadable, the end is before the start, or the start is past."""


class OffersUnreadable(StoreUnreadable):
    """The stored offers are corrupt or malformed (D-19, ADR-0004)."""


class OverlapRefused(Refusal):
    """The period shares a day with an open offer of the same space."""

    def __init__(self, message: str, offer_number: int) -> None:
        super().__init__(message)
        self.offer_number = offer_number


class UnknownOfferRefused(Refusal):
    """The number designates no open offer: never made, withdrawn, ended, or without a space."""


class InvalidOfferNumberRefused(Refusal):
    """The offer number is not a whole number from 1."""
