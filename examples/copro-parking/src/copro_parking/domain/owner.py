from dataclasses import dataclass

from .text import clean


@dataclass(frozen=True)
class Owner:
    """The single owner of a lot, known by name."""

    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", clean(self.name))
