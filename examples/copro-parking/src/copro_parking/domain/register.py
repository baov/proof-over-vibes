"""The register aggregate: lots, their owner and their spaces."""
from .errors import DuplicateLot, DuplicateSpace, UnknownLot, UnknownSpace
from .lot import Lot
from .owner import Owner
from .parking_space import ParkingSpace
from .text import clean, key, natural_key


class Register:
    def __init__(self) -> None:
        self._lots: dict[str, Lot] = {}
        self._spaces: dict[str, ParkingSpace] = {}

    def add_lot(self, identifier: object, owner_name: object) -> Lot:
        lot = Lot(identifier, Owner(owner_name))
        if key(lot.identifier) in self._lots:
            raise DuplicateLot(lot.identifier)
        self._lots[key(lot.identifier)] = lot
        return lot

    def add_space(self, number: object, lot_identifier: object) -> ParkingSpace:
        number = clean(number)
        lot = self._lots.get(key(clean(lot_identifier)))
        if lot is None:
            raise UnknownLot(lot_identifier)
        if key(number) in self._spaces:
            raise DuplicateSpace(number)
        space = ParkingSpace(number, lot.identifier)
        self._spaces[key(number)] = space
        return space

    def change_owner(self, identifier: object, owner_name: object) -> Lot:
        owner = Owner(owner_name)
        old = self._lots.get(key(clean(identifier)))
        if old is None:
            raise UnknownLot(identifier)
        lot = Lot(old.identifier, owner)
        self._lots[key(lot.identifier)] = lot
        return lot

    def change_space_number(self, number: object, new_number: object) -> ParkingSpace:
        new_number = clean(new_number)
        old = self._spaces.get(key(clean(number)))
        if old is None:
            raise UnknownSpace(number)
        if key(new_number) in self._spaces and key(new_number) != key(old.number):
            raise DuplicateSpace(new_number)
        del self._spaces[key(old.number)]
        space = ParkingSpace(new_number, old.lot_identifier)
        self._spaces[key(new_number)] = space
        return space

    def space(self, number: object) -> ParkingSpace:
        """The registered space, found ignoring case and surrounding spaces."""
        found = self._spaces.get(key(clean(number)))
        if found is None:
            raise UnknownSpace(number)
        return found

    def remove_space(self, number: object) -> None:
        """Forget a space: its number is free again, its lot stays (D-10)."""
        del self._spaces[key(self.space(number).number)]

    def lots(self) -> list[Lot]:
        """Lots sorted by identifier."""
        return sorted(self._lots.values(), key=lambda lot: natural_key(lot.identifier))

    def spaces_of(self, lot: Lot) -> list[ParkingSpace]:
        """Spaces of a lot sorted by number."""
        own = [s for s in self._spaces.values() if s.lot_identifier == lot.identifier]
        return sorted(own, key=lambda space: natural_key(space.number))
