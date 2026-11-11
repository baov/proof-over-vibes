from abc import ABC, abstractmethod

from ..domain.register import Register


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
