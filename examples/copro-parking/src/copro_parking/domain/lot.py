from dataclasses import dataclass

from .owner import Owner
from .text import clean


@dataclass(frozen=True)
class Lot:
    identifier: str
    owner: Owner

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", clean(self.identifier))
