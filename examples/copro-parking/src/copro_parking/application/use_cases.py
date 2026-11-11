"""Use cases of the register. Every write checks the role first (D-16)."""
from dataclasses import dataclass

from ..domain import errors
from .ports import RegisterRepository, RentalCheck
from .refusals import (BlankValueRefused, DuplicateLotRefused,
                       DuplicateRuleRefused, DuplicateSpaceRefused,
                       InvalidDaysRefused, InvalidParameterRefused,
                       InvalidPeriodRefused,
                       ManagerOnly, MinimumAboveMaximumRefused,
                       NoBoundRefused, SpaceRentedRefused, UnknownKindRefused,
                       UnknownLotRefused, UnknownRuleRefused,
                       UnknownSpaceRefused)
from .role import Role

_REFUSALS = {
    errors.BlankValue: BlankValueRefused,
    errors.DuplicateLot: DuplicateLotRefused,
    errors.DuplicateSpace: DuplicateSpaceRefused,
    errors.UnknownLot: UnknownLotRefused,
    errors.UnknownSpace: UnknownSpaceRefused,
    errors.UnknownKind: UnknownKindRefused,
    errors.NoBound: NoBoundRefused,
    errors.InvalidDays: InvalidDaysRefused,
    errors.MinimumAboveMaximum: MinimumAboveMaximumRefused,
    errors.InvalidParameter: InvalidParameterRefused,
    errors.DuplicateRule: DuplicateRuleRefused,
    errors.UnknownRule: UnknownRuleRefused,
    errors.InvalidPeriod: InvalidPeriodRefused,
}


@dataclass(frozen=True)
class LotEntry:
    identifier: str
    owner: str
    spaces: tuple[str, ...]


def _require_manager(role: object) -> None:
    if role is not Role.MANAGER:
        raise ManagerOnly("only the manager can change the register")


def _refuse(error: errors.DomainError) -> Exception:
    return _REFUSALS[type(error)](str(error))


def register_lot(repository: RegisterRepository, role: Role,
                 identifier: object, owner: object) -> None:
    _require_manager(role)
    register = repository.load()
    try:
        register.add_lot(identifier, owner)
    except errors.DomainError as error:
        raise _refuse(error) from error
    repository.save(register)


def register_space(repository: RegisterRepository, role: Role,
                   number: object, lot_identifier: object) -> None:
    _require_manager(role)
    register = repository.load()
    try:
        register.add_space(number, lot_identifier)
    except errors.DomainError as error:
        raise _refuse(error) from error
    repository.save(register)


def change_lot_owner(repository: RegisterRepository, role: Role,
                     identifier: object, owner: object) -> None:
    _require_manager(role)
    register = repository.load()
    try:
        register.change_owner(identifier, owner)
    except errors.DomainError as error:
        raise _refuse(error) from error
    repository.save(register)


def change_space_number(repository: RegisterRepository, role: Role,
                        number: object, new_number: object) -> None:
    _require_manager(role)
    register = repository.load()
    try:
        register.change_space_number(number, new_number)
    except errors.DomainError as error:
        raise _refuse(error) from error
    repository.save(register)


def remove_space(repository: RegisterRepository, rentals: RentalCheck,
                 role: Role, number: object) -> None:
    _require_manager(role)
    register = repository.load()
    try:
        space = register.space(number)
    except errors.DomainError as error:
        raise _refuse(error) from error
    if rentals.has_rental(space.number):
        raise SpaceRentedRefused(f"space {space.number} has a rental")
    register.remove_space(space.number)
    repository.save(register)


def list_register(repository: RegisterRepository) -> list[LotEntry]:
    register = repository.load()
    return [
        LotEntry(lot.identifier, lot.owner.name,
                 tuple(s.number for s in register.spaces_of(lot)))
        for lot in register.lots()
    ]
