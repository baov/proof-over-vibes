from pathlib import Path

from ..application.ports import RentalCheck
from .json_repository import JsonRegisterRepository


def json_repository(path: Path) -> JsonRegisterRepository:
    """The repository the register uses in production: one JSON file."""
    return JsonRegisterRepository(path)


class NoRentalYet(RentalCheck):
    """No space has a rental until the rentals exist (E3)."""

    def has_rental(self, space_number: str) -> bool:
        return False


def rental_check() -> RentalCheck:
    """The rental check the register uses until rentals exist."""
    return NoRentalYet()
