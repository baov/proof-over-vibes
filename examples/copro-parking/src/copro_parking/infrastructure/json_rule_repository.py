"""JSON file repository for the rules (ADR-0002): whole set in one file, atomic write."""
import json
from pathlib import Path

from ..application.ports import RuleRepository
from ..application.refusals import RulesUnreadable
from ..domain.errors import DomainError
from ..domain.rules import RuleSet
from .atomic_file import write_atomically


class JsonRuleRepository(RuleRepository):
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def load(self) -> RuleSet:
        try:
            return self._build(self._read())
        except (ValueError, KeyError, TypeError, AttributeError, DomainError) as error:
            raise RulesUnreadable(f"{self._path} cannot be read") from error

    @staticmethod
    def _build(document: dict) -> RuleSet:
        rules = RuleSet()
        for entry in document.get("rules", []):
            note = entry["note"]
            if note is not None and not isinstance(note, str):
                raise ValueError("a note is text or null")
            rules.add(entry["name"], entry["kind"], entry["parameter"], note)
        return rules

    def save(self, rules: RuleSet) -> None:
        document = {"rules": [
            {"name": rule.name, "kind": rule.kind,
             "parameter": rule.condition.parameter(), "note": rule.note}
            for rule in rules.in_registration_order()]}
        write_atomically(self._path, json.dumps(document, indent=2))

    def _read(self) -> dict:
        if not self._path.is_file():
            return {}
        text = self._path.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else {}
