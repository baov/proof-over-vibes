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
