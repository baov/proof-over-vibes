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
