---
role: developer
status: done
reasons: []
---

# Developer, iteration 1: S2 Correct a lot's owner and a space's number

- Process: strict test-first this time. For each step the tests were written and run red (import error or failing assertion) before the production code; then green. Natural order was observed red separately (2 failures) before the sort change. Two steps (JSON corrections, same-value) were green on first run because S1 code already carried them; those tests are regression guards.
- Changed: `Register.change_owner` / `change_space_number` + `UnknownSpace` (domain); `natural_key` in `domain/text.py` used by `lots()` / `spaces_of()`; `UnknownSpaceRefused`, `StoreUnreadable`, `change_lot_owner`, `change_space_number` (application); `JsonRegisterRepository.load` wraps parse/shape errors (infrastructure). All 6 plan steps ticked, no deviation.
- Tests: 53 unit tests green (27 -> 53), harness selftests 10 green. `bash tools/harness/run_all.sh`: exit 0, 22/22 test-cases `covered` (10 `s2-*` filled).
- Mutation (critical): 88.9% (40/45). 5 survivors, all equivalent and the same as S1: `frozen=True` -> `False` x4 (Owner, Lot, ParkingSpace, LotEntry), `json.dumps(indent=2)` -> `3`. Two new survivors (domain return values of the two change methods) were killed by asserting the returned lot / space. INV-007 baseline can be set at 88.9%.
- Sensitive zones touched (escalate on diff per brief): role check (two new use cases, manager check first), JSON read path (`load`, D-19), listing sort (D-20). The write path (`_write`) is unchanged.

## Behaviors added (not listed in the plan)
- `StoreUnreadable` is NOT a subclass of `Refusal` (plan: "not under the register's rules"); it lives in `application/refusals.py`. A caller catching `Refusal` will not catch it.
- "Unreadable" covers: invalid JSON, non-UTF-8 bytes, top level not an object, `lots`/`spaces` not lists of objects, missing or non-text fields, blank owner, duplicate lot or space, space on an unknown lot. A file with only `lots`, only `spaces`... or `{}` still reads. `OSError` (permissions) is not converted.
- Targeting a blank lot identifier or space number in a correction is `BlankValueRefused`, not unknown (same as S1's blank lot reference for a space). Blank new value is checked before unknown target.
- Natural order: digit runs compare as numbers, case ignored; ties impossible between distinct keys except "a01" vs "a1", whose relative order follows the stable sort (registration order).
- Public signatures: `change_lot_owner(repository, role, identifier, owner)`, `change_space_number(repository, role, number, new_number)`.

No consumer-visible rule was invented; the points above follow D-14, D-19..D-21 and S1 conventions. Worth a glance: the `StoreUnreadable` class position and "a01" vs "a1" order.
