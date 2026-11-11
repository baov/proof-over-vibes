from abc import ABC, abstractmethod
from datetime import date

from ..domain.offers import OfferBook
from ..domain.register import Register
from ..domain.rules import RuleSet


class RegisterRepository(ABC):
    """Stores the whole register; it enforces no rule itself (ADR-0002)."""

    @abstractmethod
    def load(self) -> Register:
        """The stored register; an empty one when nothing is stored yet."""

    @abstractmethod
    def save(self, register: Register) -> None:
        """Replace the stored register."""


class RentalCheck(ABC):
    """Tells whether a space has a rental, existing or planned (rentals arrive with E3)."""

    @abstractmethod
    def has_rental(self, space_number: str) -> bool:
        """True when the space, given by its registered number, is rented."""


class RuleRepository(ABC):
    """Stores the whole rule set; it enforces no rule itself (ADR-0002)."""

    @abstractmethod
    def load(self) -> RuleSet:
        """The stored rules; an empty set when nothing is stored yet."""

    @abstractmethod
    def save(self, rules: RuleSet) -> None:
        """Replace the stored rules."""


class OfferRepository(ABC):
    """Stores the whole offer book; it enforces no rule itself (ADR-0004)."""

    @abstractmethod
    def load(self) -> OfferBook:
        """The stored offers; an empty book when nothing is stored yet."""

    @abstractmethod
    def save(self, book: OfferBook) -> None:
        """Replace the stored offers."""


class Clock(ABC):
    """Tells today's date; the domain and the use cases never read the system date."""

    @abstractmethod
    def today(self) -> date:
        """The current calendar day."""
