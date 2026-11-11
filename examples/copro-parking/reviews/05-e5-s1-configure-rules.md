---
role: reviewer
status: escalate
verdict: GO
reasons: [sensitive zones touched: atomic_file.py, json_repository.py write path, rule_use_cases.py role check, json_rule_repository.py]
severity: minor
open_majors: []
---

# Review 1 - E5 S1 configure and list duration-bounds rules

Skill `premerge-review`. Criticality: critical (domain layer, persisted format, role check). Scope: working tree against HEAD (nothing of S1 is committed): 9 modified files, 8 new.

## Gauntlet
| Check | Result |
|---|---|
| Unit suite | OK, 125 tests |
| Harness `run_all.sh` | OK: 47 test-cases, 47 covered_ok, 0 pending, 0 violation |
| Mutation | `--scope diff` finds nothing to mutate (uncommitted work), so run with `--scope critical`: 90.9% (110/121), threshold 90. The 11 survivors are `frozen=True` -> False (8) and JSON `indent` 2 -> 3 (2) plus one old one: equivalent, as the developer said |
| Lint | none configured in the project |

## Probes (own script against the real JSON adapters, temp dir)
- D-16: owner, resident, `None`, `"manager"` string on add with a blank name and unknown kind: `ManagerOnly` each time; no file created.
- Check orders: add = blank, unknown kind, parameter, duplicate; change = blank, unknown rule, parameter (an unknown rule with an invalid parameter gives `UnknownRuleRefused`). As planned.
- Parameters: `None`/`{}`/both `None` -> `NoBoundRefused`; `1.5`, `"30"`, `True`, `0`, `-1` -> `InvalidDaysRefused`; 5>4 -> `MinimumAboveMaximumRefused`; `{5,5}`, maximum only accepted (D-36 stored as given); unknown key, list, text -> `InvalidParameterRefused`.
- D-39/D-40: `RuleChange()` leaves the bytes identical; note `"  "` clears; text replaces; a parameter change keeps the note; `parameter={}` -> `NoBoundRefused` (D-44); note `5` -> `BlankValueRefused` (D-43).
- D-33, D-32: `a01, A1, r2, R10` whatever the add order; remove, remove twice (`UnknownRuleRefused`), name free again.
- D-35: 16 corrupt files (invalid JSON, non-UTF-8, list root, `rules` null/text, entry as text, missing field, unknown kind, kind as list, text/zero/empty parameter, duplicate name, note `5`, name `5`, blank name, `NaN`, 1e400, 100000 nested brackets): `RulesUnreadable` on list, add, change and remove, bytes identical every time. A file with `{"minimum": 2}` only reads fine (D-42) and is normalised on the next write.
- Atomic write: with `os.replace` patched to fail, the file is unchanged and no `.tmp` is left. `json_repository.py` diff is a pure move (the same code in `atomic_file.py`, only `self._path` -> `path`); the register file is never created or touched by rule writes.

## Findings
### Minor
- **[m1] Mutation `--scope diff` is a no-op while the work is uncommitted** - `tools/harness/run_mutation.py` - angle: debt. The gauntlet check was passed with `--scope critical` instead. Run `--scope diff` after the commit.
- **[m2] Read of a rules file normalises silently** - `json_rule_repository.py:_build` - angle: bugs. A hand-edited note (` x `) or a one-key parameter is trimmed/completed on load and rewritten on the next save. Consistent with D-42; mention only.

## Checks not performed
Lint (none in the project). Performance: no target declared, none checked.

## Positive notes
Tests-first evidence is credible; the refactor is a faithful move; the fail-closed read-before-write holds on all three writes.

## Escalation
Sensitive zones are touched (atomic write path, role check, rule store). Verdict GO, status `escalate`: the human decides before merge.
