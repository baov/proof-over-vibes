---
role: planner
status: done
reasons: []
---

# S2 Corriger le propriétaire d'un lot et le numéro d'une place

Decisions D-19 (corrupt store), D-20 (natural order), D-21 (same-value correction) answered by the human.

## 1. Metadata
- **Type**: feature
- **Date**: 2026-11-11
- **Status**: in-progress

## 2. Goal
The manager changes a lot's owner and a space's number without removing the entry; uniqueness, blank and role rules still hold; every refusal changes nothing. Closes S1's two open majors (corrupt store, sort order) here (D-19, D-20).

## 3. Context
- S1 merged: `Register` (domain), `use_cases.py`, `refusals.py`, `JsonRegisterRepository`. ADR-0001..0003 respected, no structural change.
- Decisions: D-2, D-3/D-4, D-11, D-12, D-14 (named Refusal), D-15 (trimmed text as typed), D-16 (manager-only first), D-18.
- Invariants: INV-001 (domain stays free of I/O), INV-002 (each test-case points at a test), INV-003..006 (shape), INV-007 (first baseline after this story).
- Sensitive zones, escalate on diff: role check in `use_cases.py` (two new write use cases); JSON read path (`_read`, D-19) and the listing sort in `domain/register.py` (D-20): escalate on diff. Role check also applies to the new use cases.
- Test-cases: `docs/business/test-cases/register-lots-and-spaces/s2-*.md` (10, `pending`); developer fills `automated_test` and sets `covered`.

## 4. Expected behaviors
Boundary: application use cases `change_lot_owner`, `change_space_number` on the in-memory repository; persistence through the JSON repository on a temp dir.
- AC1: given A12/Durand, when changing the owner to " Martin ", then listing shows A12/"Martin". Boundary: `change_lot_owner`.
- AC2: given P1 on A12, when changing P1 to " P9 ", then listing shows P9 under A12, no P1; the lot stays. Boundary: `change_space_number`.
- AC3: given P1 and P2, when changing P2 to " p1 ", then duplicate refusal, register and file unchanged; changing P1 to "p1" is not a duplicate of itself (AC3 says "another space").
- AC3b: blank, whitespace-only or `None` new owner or number: blank refusal, unchanged.
- AC4: unknown lot or unknown space (found ignoring case and spaces): refusal, unchanged. New refusal `UnknownSpaceRefused` under `Refusal`; unknown lot reuses `UnknownLotRefused`.
- AC5: owner, resident, `None`, other value: `ManagerOnly`, checked first, even with blank or duplicate values (D-16).
- AC6: listing after each change shows the new value and stays sorted; re-read through a new JSON repository shows it too.
- D-21: same owner, or same number differing by case, is accepted; stored text becomes the new trimmed text. Check order follows S1: role, blank, unknown, duplicate.
- D-19: invalid JSON or wrong shape in the store raises `StoreUnreadable` (application error, not under the register's rules) on load, hence on every read and write; the file is byte-identical afterwards. Boundary: JSON repository + use cases.
- D-20: given lots A10, a2 and spaces P10, p2 in any order, listing gives a2, A10 and p2, P10. Boundary: `list_register`.

## 5. Steps
- [x] Step 1: add `Register.change_owner(identifier, owner_name)` and `Register.change_space_number(number, new_number)` in `domain/register.py`, plus `UnknownSpace` in `domain/errors.py`; tests in `tests/test_register.py`.
- [x] Step 2: add `UnknownSpaceRefused` in `application/refusals.py` and its mapping; add `change_lot_owner` and `change_space_number` in `application/use_cases.py` (manager check first); tests in `tests/test_use_cases.py`.
- [x] Step 3: persistence re-read and file-identical-on-refusal tests for corrections in `tests/test_json_repository.py`.
- [x] Step 4: corrupt-store handling in `infrastructure/json_repository.py`, with its test: `StoreUnreadable` in `application/refusals.py`-side errors, raised by the adapter on bad JSON or shape, file never written.
- [x] Step 5: sort order in `Register.lots` / `spaces_of`, with its test.
- [x] Step 6: fill `automated_test` and `status: covered` in the `s2-*` test-cases; run `bash tools/harness/run_all.sh` and the unit suite.

## 6. Risks & edge cases
- Role check forgotten on a new use case: one non-manager test per use case.
- Renaming a space must re-key the space index and keep its lot; renaming to its own number in another case must not self-collide.
- A lot's identifier is not changed here, so spaces keep pointing at it.
- Domain stays free of I/O (INV-001).

## 7. Out of scope
Changing a lot identifier, moving a space to another lot, removal (S3), history of owners (architect), concurrency.

## 8. Deviations
(empty)

## 9. Self-review
(empty)

## 10. Follow-up actions
(empty)

## Technical choices (for the reviewer)
Domain methods mutate the aggregate like `add_*`; use cases mirror `register_lot` (check role, load, call, map `DomainError`, save); the new refusal follows the existing mapping table.
