"""JSON file repository (ADR-0002): whole register in one file, atomic write."""
import json
import os
import tempfile
from pathlib import Path

from ..application.ports import RegisterRepository
from ..application.refusals import StoreUnreadable
from ..domain.errors import DomainError
from ..domain.register import Register


class JsonRegisterRepository(RegisterRepository):
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def load(self) -> Register:
        try:
            return self._build(self._read())
        except (ValueError, KeyError, TypeError, AttributeError, DomainError) as error:
            raise StoreUnreadable(f"{self._path} cannot be read") from error

    @staticmethod
    def _build(document: dict) -> Register:
        register = Register()
        for lot in document.get("lots", []):
            register.add_lot(lot["identifier"], lot["owner"])
        for space in document.get("spaces", []):
            register.add_space(space["number"], space["lot"])
        return register

    def save(self, register: Register) -> None:
        document = {"lots": [], "spaces": []}
        for lot in register.lots():
            document["lots"].append(
                {"identifier": lot.identifier, "owner": lot.owner.name})
            for space in register.spaces_of(lot):
                document["spaces"].append(
                    {"number": space.number, "lot": lot.identifier})
        self._write(json.dumps(document, indent=2))

    def _read(self) -> dict:
        if not self._path.is_file():
            return {}
        text = self._path.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else {}

    def _write(self, text: str) -> None:
        handle, temporary = tempfile.mkstemp(
            dir=self._path.parent, prefix=self._path.name, suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                stream.write(text)
            os.replace(temporary, self._path)
        except BaseException:
            if os.path.exists(temporary):
                os.unlink(temporary)
            raise
