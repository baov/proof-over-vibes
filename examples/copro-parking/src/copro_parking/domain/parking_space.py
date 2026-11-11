from dataclasses import dataclass

from .text import clean


@dataclass(frozen=True)
class ParkingSpace:
    number: str
    lot_identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "number", clean(self.number))
