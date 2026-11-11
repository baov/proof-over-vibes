"""Offers: a registered space made available for a period of whole days."""
from dataclasses import dataclass
from datetime import date

from .dates import parse_date
from .errors import InconsistentOffers, InvalidPeriod
from .text import clean, natural_key


@dataclass(frozen=True)
class Period:
    """Whole calendar days, both ends included; the end is not before the start."""
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise InvalidPeriod(f"{self.end} is before {self.start}")

    @classmethod
    def of(cls, start: object, end: object) -> "Period":
        return cls(parse_date(start), parse_date(end))

    @classmethod
    def starting_from(cls, today: date, start: object, end: object) -> "Period":
        """A new period: the start may not be before `today` (D-47, D-53)."""
        period = cls.of(start, end)
        if period.start < today:
            raise InvalidPeriod(f"{period.start} is before today")
        return period


@dataclass(frozen=True)
class Offer:
    number: int
    space_number: str
    period: Period


def _is_number(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


class OfferBook:
    """The offers and the next number to give; numbers are never reused (D-61)."""

    def __init__(self) -> None:
        self._offers: list[Offer] = []
        self._next_number = 1

    @classmethod
    def restore(cls, offers: list[Offer], next_number: object) -> "OfferBook":
        if not _is_number(next_number):
            raise InconsistentOffers(f"next number {next_number!r}")
        numbers = [offer.number for offer in offers]
        if not all(_is_number(n) and n < next_number for n in numbers):
            raise InconsistentOffers("an offer number is invalid or not below the next one")
        if len(set(numbers)) != len(numbers):
            raise InconsistentOffers("duplicate offer number")
        book = cls()
        book._offers = sorted(offers, key=lambda offer: offer.number)
        book._next_number = next_number
        return book

    @property
    def next_number(self) -> int:
        return self._next_number

    def add(self, space_number: object, period: Period) -> Offer:
        offer = Offer(self._next_number, clean(space_number), period)
        self._offers.append(offer)
        self._next_number += 1
        return offer

    def offers(self) -> list[Offer]:
        """Every stored offer, in number order, open or not."""
        return list(self._offers)

    def open_offers(self, today: date) -> list[Offer]:
        """Offers whose end is not before `today`, by start then natural space order."""
        open_ones = [o for o in self._offers if today <= o.period.end]
        return sorted(open_ones,
                      key=lambda o: (o.period.start, natural_key(o.space_number)))
