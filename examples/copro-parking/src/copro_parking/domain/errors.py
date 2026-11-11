"""Domain errors: the rules of the register that a value can break."""


class DomainError(Exception):
    """Base of every error raised by the domain."""


class BlankValue(DomainError):
    """An identifier, a number or an owner name is missing or blank."""


class DuplicateLot(DomainError):
    """A lot with the same identifier is already registered."""


class DuplicateSpace(DomainError):
    """A space with the same number is already registered."""


class UnknownLot(DomainError):
    """The lot a space refers to is not registered."""


class UnknownSpace(DomainError):
    """The space to correct is not registered."""


class UnknownKind(DomainError):
    """The kind of a rule is not on the closed list."""


class NoBound(DomainError):
    """A duration rule has neither a minimum nor a maximum."""


class InvalidDays(DomainError):
    """A bound is not a whole number of days above zero."""


class MinimumAboveMaximum(DomainError):
    """The minimum of a duration rule is above its maximum."""


class InvalidParameter(DomainError):
    """The parameter of a rule is not a mapping or has an unknown key."""


class DuplicateRule(DomainError):
    """A rule with the same name is already registered."""


class UnknownRule(DomainError):
    """The rule to change or remove is not registered."""


class InvalidPeriod(DomainError):
    """A date is missing or unreadable, the end is before the start, or the start is past."""


class InconsistentOffers(DomainError):
    """Stored offers break a rule of the book: duplicate number, number not below the next one."""
