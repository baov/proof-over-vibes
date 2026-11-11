"""Use cases of the offers. The role is checked first (ADR-0003, ADR-0004)."""
from dataclasses import dataclass
from datetime import date

from ..domain import errors
from ..domain.offers import Offer, Period, offer_number
from ..domain.text import clean, key
from .ports import Clock, OfferRepository, RegisterRepository
from .refusals import (NotAllowedToOffer, NotTheOwner, OverlapRefused,
                       UnknownOfferRefused)
from .role import Role
from .use_cases import _refuse


@dataclass(frozen=True)
class OfferRequest:
    """What an owner gives to offer a space; there is no price (D-49)."""
    space: object
    offerer: object
    start: object
    end: object


@dataclass(frozen=True)
class WithdrawRequest:
    """What an owner gives to withdraw an offer: their name and the number the list shows."""
    offerer: object
    number: object


@dataclass(frozen=True)
class OfferEntry:
    number: int
    space: str
    lot: str
    owner: str
    start: date
    end: date


def _require_owner(role: object) -> None:
    """Only the owner role may offer a space or withdraw an offer.

    This is not an authentication: without accounts the declared name proves
    nothing about who is typing (D-46, ADR-0004).
    """
    if role is not Role.OWNER:
        raise NotAllowedToOffer("only an owner can offer a space or withdraw an offer")


def _entry(offer: Offer, lot: str, owner: str) -> OfferEntry:
    return OfferEntry(offer.number, offer.space_number, lot, owner,
                      offer.period.start, offer.period.end)


def offer_space(registers: RegisterRepository, offers: OfferRepository,
                clock: Clock, role: Role, request: OfferRequest) -> OfferEntry:
    """An owner offers a registered space of their lot for a period.

    Role first, then invalid input, unknown space, not the owner, and last an
    overlap with an open offer of the same space. The name of
    the offerer is compared with the lot owner; this is not an authentication
    (D-46): it proves nothing about who is typing.
    """
    _require_owner(role)
    try:
        today = clock.today()
        period = Period.starting_from(today, request.start, request.end)
        space, offerer = clean(request.space), clean(request.offerer)
        register = registers.load()
        registered = register.space(space).number
        lot = register.lot_of(space)
    except errors.DomainError as error:
        raise _refuse(error) from error
    if key(lot.owner.name) != key(offerer):
        raise NotTheOwner(f"{offerer} is not the owner of {registered}")
    book = offers.load()
    try:
        offer = book.add(registered, period, today)
    except errors.OverlappingOffer as error:
        raise OverlapRefused(str(error), error.offer_number) from error
    offers.save(book)
    return _entry(offer, lot.identifier, lot.owner.name)


def withdraw_offer(registers: RegisterRepository, offers: OfferRepository,
                   clock: Clock, role: Role, request: WithdrawRequest) -> OfferEntry:
    """The owner of an offer takes it back, designating it by its number.

    Role first, then invalid input, unknown offer (never made, withdrawn,
    ended, or whose space left the register, D-65), and last not the owner.
    The name is compared with the current owner of the lot; this is not an
    authentication (D-46): it proves nothing about who is typing.
    """
    _require_owner(role)
    try:
        offerer, number = clean(request.offerer), offer_number(request.number)
    except errors.DomainError as error:
        raise _refuse(error) from error
    today = clock.today()
    book = offers.load()
    try:
        space = book.open_offer(number, today).space_number
        lot = registers.load().lot_of(space)
    except (errors.UnknownOffer, errors.UnknownSpace) as error:
        raise UnknownOfferRefused(f"offer {number} is not open") from error
    if key(lot.owner.name) != key(offerer):
        raise NotTheOwner(f"{offerer} is not the owner of offer {number}")
    offer = book.withdraw(number, today)
    offers.save(book)
    return _entry(offer, lot.identifier, lot.owner.name)


def list_open_offers(registers: RegisterRepository, offers: OfferRepository,
                     clock: Clock) -> list[OfferEntry]:
    """The open offers, by start then space; the owner is the register's current one."""
    today = clock.today()
    register = registers.load()
    entries = []
    for offer in offers.load().open_offers(today):
        try:
            lot = register.lot_of(offer.space_number)
        except errors.UnknownSpace:
            continue  # the space left the register: no lot or owner to show
        entries.append(_entry(offer, lot.identifier, lot.owner.name))
    return entries
