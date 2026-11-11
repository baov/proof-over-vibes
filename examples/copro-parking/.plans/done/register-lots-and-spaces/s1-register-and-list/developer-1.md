---
role: developer
status: done
reasons: []
---

# Developer, iteration 1: S1 Register lots and spaces and list them

- Implemented plan steps 1-5: `domain` (errors, text, owner, lot, parking_space, register), `application` (role, refusals, ports, use_cases), `infrastructure` (json_repository, wiring), `tests/` (bootstrap, fakes, 3 test files). No commit, no git.
- Honest process note: the production code was written before the tests in this pass (not strict red-green); the tests were then checked by mutation testing. The reviewer may want to weigh that.
- Tests: 27 behavior tests green (`python3 -m unittest discover -s tests`); harness selftests 10 green.
- `bash tools/harness/run_all.sh`: exit 0, no warning; 12/12 test-cases `covered` with `automated_test` filled.
- Mutation (critical): 84.8% (28/33). 5 survivors, all equivalent: `frozen=True` -> `False` on 4 dataclasses (Owner, Lot, ParkingSpace, LotEntry; immutability is a safety property, no stated behavior) and `json.dumps(indent=2)` -> `3` (file layout only). No test added for them; INV-007 baseline can be set at 84.8%.
- Test run note: `tests/bootstrap.py` puts `src` on the path so the documented command works without PYTHONPATH.

## Behaviors added (not listed in the plan)
- `Role` enum has three members: `MANAGER`, `OWNER`, `RESIDENT` (taken from framing.md; only MANAGER has a meaning). Anything that is not `Role.MANAGER` (None, the string "manager") gets `ManagerOnly`.
- Public use case signatures: `register_lot(repository, role, identifier, owner)`, `register_space(repository, role, number, lot_identifier)`, `list_register(repository)`; listing returns `LotEntry(identifier, owner, spaces)` sorted lots/spaces (sort ignores case); `list_register` takes no role (reading is open, D-3 only restricts writes).
- Refusal classes: `ManagerOnly`, `BlankValueRefused`, `DuplicateLotRefused`, `DuplicateSpaceRefused`, `UnknownLotRefused`, all under `Refusal`.
- A space's lot is matched by trimmed, case-folded identifier; a blank lot reference for a space is `BlankValueRefused`, not `UnknownLotRefused`.
- JSON file layout `{"lots": [{identifier, owner}], "spaces": [{number, lot}]}`; a refused first write creates no file.

None of these is decided by a document and may be seen by a consumer: the role names and "listing is open to any caller" are the ones to confirm (no blocking question raised, as the plan implies them).
