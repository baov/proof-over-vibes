"""Text handling shared by the domain: trimmed as typed, compared by key."""
import re

from .errors import BlankValue


def clean(value: object) -> str:
    """The trimmed text; a missing or blank value is refused."""
    if not isinstance(value, str) or not value.strip():
        raise BlankValue("a blank value is not accepted")
    return value.strip()


def key(value: str) -> str:
    """The comparison key: surrounding spaces and case are ignored."""
    return value.strip().casefold()


def natural_key(value: str) -> tuple:
    """The sort key: case ignored, digit runs compared as numbers (D-20)."""
    parts = re.split(r"(\d+)", key(value))
    return tuple(int(p) if i % 2 else p for i, p in enumerate(parts))
