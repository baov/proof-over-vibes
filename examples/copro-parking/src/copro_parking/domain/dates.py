"""Dates of the offers: whole calendar days, no time of day (D-60)."""
import re
from datetime import date, datetime

from .errors import InvalidPeriod

_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def parse_date(value: object) -> date:
    """A date object (a datetime is refused) or text `YYYY-MM-DD`, spaces ignored."""
    if isinstance(value, datetime):
        raise InvalidPeriod(repr(value))
    if isinstance(value, date):
        return value
    if isinstance(value, str) and _ISO.fullmatch(value.strip()):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            pass
    raise InvalidPeriod(repr(value))
