"""JSON file repository for the offers (ADR-0004): whole book in one file, atomic write."""
import json
from pathlib import Path

from ..application.ports import OfferRepository
from ..application.refusals import OffersUnreadable
from ..domain.errors import DomainError
from ..domain.offers import Offer, OfferBook, Period
from .atomic_file import write_atomically


class JsonOfferRepository(OfferRepository):
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def load(self) -> OfferBook:
        try:
            return self._build(self._read())
        except (ValueError, KeyError, TypeError, AttributeError, DomainError) as error:
            raise OffersUnreadable(f"{self._path} cannot be read") from error

    @staticmethod
    def _build(document: dict) -> OfferBook:
        offers = []
        for entry in document.get("offers", []):
            space = entry["space"]
            if not isinstance(space, str) or not space.strip():
                raise ValueError("a space number is non-blank text")
            offers.append(Offer(entry["number"], space.strip(),
                                Period.of(entry["start"], entry["end"])))
        return OfferBook.restore(offers, document.get("next_number", 1))

    def save(self, book: OfferBook) -> None:
        document = {"next_number": book.next_number, "offers": [
            {"number": o.number, "space": o.space_number,
             "start": o.period.start.isoformat(), "end": o.period.end.isoformat()}
            for o in book.offers()]}
        write_atomically(self._path, json.dumps(document, indent=2))

    def _read(self) -> dict:
        if not self._path.is_file():
            return {}
        text = self._path.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else {}
