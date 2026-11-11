"""Use cases of the rules. Every write checks the role first (D-16, D-38)."""
from dataclasses import dataclass

from ..domain import errors
from ..domain.rules import Rule
from .ports import RuleRepository
from .role import Role
from .use_cases import _refuse, _require_manager


@dataclass(frozen=True)
class RuleSpec:
    kind: object
    parameter: object
    note: object = None


@dataclass(frozen=True)
class RuleChange:
    """What a change gives: `None` keeps the parameter or the note (D-39, D-40)."""
    parameter: object = None
    note: object = None


@dataclass(frozen=True)
class RuleEntry:
    name: str
    kind: str
    parameter: dict
    note: str | None


def _entry(rule: Rule) -> RuleEntry:
    return RuleEntry(rule.name, rule.kind, rule.condition.parameter(), rule.note)


def add_rule(repository: RuleRepository, role: Role,
             name: object, spec: RuleSpec) -> None:
    _require_manager(role)
    rules = repository.load()
    try:
        rules.add(name, spec.kind, spec.parameter, spec.note)
    except errors.DomainError as error:
        raise _refuse(error) from error
    repository.save(rules)


def change_rule(repository: RuleRepository, role: Role,
                name: object, change: RuleChange) -> None:
    _require_manager(role)
    rules = repository.load()
    try:
        rules.change(name, change.parameter, change.note)
    except errors.DomainError as error:
        raise _refuse(error) from error
    repository.save(rules)


def remove_rule(repository: RuleRepository, role: Role, name: object) -> None:
    _require_manager(role)
    rules = repository.load()
    try:
        rules.remove(name)
    except errors.DomainError as error:
        raise _refuse(error) from error
    repository.save(rules)


def list_rules(repository: RuleRepository) -> list[RuleEntry]:
    return [_entry(rule) for rule in repository.load().rules()]
