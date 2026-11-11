from datetime import date
from pathlib import Path

from ..application.ports import Clock, RentalCheck
from .json_offer_repository import JsonOfferRepository
from .json_repository import JsonRegisterRepository
from .json_rule_repository import JsonRuleRepository


def json_repository(path: Path) -> JsonRegisterRepository:
    """The repository the register uses in production: one JSON file."""
    return JsonRegisterRepository(path)


def json_rule_repository(path: Path) -> JsonRuleRepository:
    """The repository the rules use in production: one JSON file, apart from the register."""
    return JsonRuleRepository(path)


class NoRentalYet(RentalCheck):
    """No space has a rental until the rentals exist (E3)."""

    def has_rental(self, space_number: str) -> bool:
        return False


def rental_check() -> RentalCheck:
    """The rental check the register uses until rentals exist."""
    return NoRentalYet()


def json_offer_repository(path: Path) -> JsonOfferRepository:
    """The repository the offers use in production: one JSON file, apart from the others."""
    return JsonOfferRepository(path)


class SystemClock(Clock):
    """The local date of the machine; the only place that reads the system date."""

    def today(self) -> date:
        return date.today()


def system_clock() -> Clock:
    """The clock the offers use in production."""
    return SystemClock()
