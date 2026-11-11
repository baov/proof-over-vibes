"""Offers: a registered space made available for a period of whole days."""
from dataclasses import dataclass
from datetime import date

from .dates import parse_date
from .errors import (InconsistentOffers, InvalidOfferNumber, InvalidPeriod,
                     OverlappingOffer, UnknownOffer)
from .text import clean, key, natural_key


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

    def shares_a_day_with(self, other: "Period") -> bool:
        return self.start <= other.end and other.start <= self.end


@dataclass(frozen=True)
class Offer:
    number: int
    space_number: str
    period: Period


def _is_number(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 1


def offer_number(value: object) -> int:
    """An offer number as given by a caller: a whole number from 1, nothing else (D-66)."""
    if not _is_number(value):
        raise InvalidOfferNumber(f"{value!r} is not an offer number")
    return value


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

    def add(self, space_number: object, period: Period, today: date) -> Offer:
        """Add an offer; refused when it shares a day with an open offer of the space.

        The refusal names the open offer with the earliest start, then the
        lowest number (D-64). Stored overlapping pairs are tolerated (D-63).
        """
        space = clean(space_number)
        blocking = [o for o in self.open_offers(today)
                    if o.space_number == space and o.period.shares_a_day_with(period)]
        if blocking:
            raise OverlappingOffer(
                min(blocking, key=lambda o: (o.period.start, o.number)).number)
        offer = Offer(self._next_number, space, period)
        self._offers.append(offer)
        self._next_number += 1
        return offer

    def open_offer(self, number: int, today: date) -> Offer:
        """The open offer with this number; any other number is an unknown offer."""
        for offer in self.open_offers(today):
            if offer.number == number:
                return offer
        raise UnknownOffer(f"offer {number} is not open")

    def withdraw(self, number: int, today: date) -> Offer:
        """Delete the open offer with this number (D-61: its number is never reused).

        The other offers, the expired ones included, and the next number are kept.
        """
        offer = self.open_offer(number, today)
        self._offers.remove(offer)
        return offer

    def has_open_offer(self, space_number: object, today: date) -> bool:
        """True when an offer of the space ends today or later (D-52).

        The numbers are compared by key: a file written before S4 may hold
        "P1" for a space now registered as "p1".
        """
        space = key(clean(space_number))
        return any(key(o.space_number) == space for o in self.open_offers(today))

    def offers(self) -> list[Offer]:
        """Every stored offer, in number order, open or not."""
        return list(self._offers)

    def open_offers(self, today: date) -> list[Offer]:
        """Offers whose end is not before `today`, by start then natural space order."""
        open_ones = [o for o in self._offers if today <= o.period.end]
        return sorted(open_ones,
                      key=lambda o: (o.period.start, natural_key(o.space_number), o.number))
