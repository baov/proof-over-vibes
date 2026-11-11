---
role: planner
status: done
reasons: []
---

# S3 Remove a space

## 1. Metadata
- **Type**: feature
- **Date**: 2026-11-11
- **Status**: in-progress

## 2. Goal
The manager removes a space registered by mistake; the number becomes free again, the lot stays. Removal is refused for an unknown space, for a space with a rental (existing or planned, via a port that answers "no rental" until E3), and for any other role. Every refusal changes nothing.

## 3. Context
- S1 and S2 merged: `Register`, `use_cases.py` (write use cases: role first, load, domain call, map `DomainError`, save), `refusals.py`, `JsonRegisterRepository`. ADR-0001..0003 respected, no structural change.
- Decisions: D-3/D-4/D-18 (manager only), D-10 (no lot removal), D-11 (target found ignoring case and surrounding spaces), D-12 (blank number refused), D-13/D-20 (listing order), D-14 (named `Refusal`), D-16 (manager-only first), D-19 (`StoreUnreadable` on load).
- Invariants: INV-001 (the rental port lives in `application/ports.py`; its "no rental" adapter holds no I/O), INV-002 (each `s3-*` test-case points at a test), INV-003..006 (shape), INV-007 (mutation score must not fall below the baseline).
- Sensitive zones, escalate on diff: role check in `use_cases.py` (new write use case); JSON write path is reused unchanged (a diff there escalates).
- Test-cases: `docs/business/test-cases/register-lots-and-spaces/s3-*.md` (6, `pending`); the developer fills `automated_test` and sets `covered`.
- Open minor from S2 (4300-digit identifiers) is out of scope.

## 4. Expected behaviors
Boundary: application use case `remove_space` on the in-memory repository with a stub rental port; persistence through the JSON repository on a temp dir.
- AC1: given P1 on A12 and P2 on B1, when removing " p1 ", then the listing shows A12 with no space and B1 with P2; a new JSON repository on the same file shows the same. The use case returns nothing, like every write.
- AC2: given no P7, when removing "P7", then `UnknownSpaceRefused`, register and file unchanged. Removing P1 twice: the second call is that same refusal. A blank, whitespace-only or `None` number: `BlankValueRefused`, unchanged. Check order: role, blank, unknown, rental.
- AC3: given a rental port answering "rented" for P1, when removing P1, then `SpaceRentedRefused` (new, under `Refusal`), P1 stays listed, register and file unchanged. The port is asked with the number as stored (trimmed text); it is not asked for an unknown space, nor for a non-manager. With the default port the removal goes through.
- AC4: owner, resident, `None`, other value: `ManagerOnly`, checked first, even with an unknown or blank number or a rented space.
- AC5: given P1 removed, when registering "P1" (same lot or another), then accepted and listed.
- AC6: given A12 with the single P1, when removing P1, then A12 and its owner still appear, with no space. No lot is ever removed.
- D-19: removal on a corrupt store raises `StoreUnreadable`, file identical (covered by the existing load path; one test through `remove_space`).

## 5. Steps
- [x] Step 1: add `Register.space(number)` (lookup ignoring case and spaces; blank raises `BlankValue`, absent raises `UnknownSpace`) and `Register.remove_space(number)` in `domain/register.py`; tests in `tests/test_register.py`.
- [x] Step 2: add `RentalCheck` port in `application/ports.py` (`has_rental(space_number: str) -> bool`) and `SpaceRentedRefused` in `application/refusals.py`; add `NoRentalYet` (always `False`) in `infrastructure/wiring.py` with `rental_check()` next to `json_repository()`.
- [x] Step 3: add `remove_space(repository, rentals, role, number)` in `application/use_cases.py`: `_require_manager`, load, `register.space(number)` (map `DomainError`), refuse with `SpaceRentedRefused` if `rentals.has_rental(space.number)`, `register.remove_space`, save. Tests in `tests/test_use_cases.py` with a stub `RentalCheck` in `tests/fakes.py`: AC1-AC6.
- [x] Step 4: persistence tests in `tests/test_json_repository.py`: removal survives re-read, refusals (unknown, rented) leave the file byte-identical, corrupt store through `remove_space`.
- [x] Step 5: fill `automated_test` and `status: covered` in the six `s3-*` test-cases; run the unit suite and `bash tools/harness/run_all.sh`.

## 6. Risks & edge cases
- Role check forgotten on the new use case: one non-manager test, with the unknown/blank/rented variants proving it runs first.
- Rental port asked before the unknown check, or for a refused role: tests with a recording stub assert it is not called.
- The removed space must also leave the space index (re-registering its number works), and the lot must remain.
- Domain stays free of I/O (INV-001); the rental check is not a domain error, the refusal is raised by the use case.

## 7. Out of scope
Removing a lot (D-10), real rentals and offers (E3), a rental-lookup adapter, history of removals, undo, concurrency, the 4300-digit identifier minor.

## 8. Deviations
(empty)

## 9. Self-review
(empty)

## 10. Follow-up actions
(empty)

## Technical choices (for the reviewer)
- `remove_space` takes the rental port as an explicit argument (after the repository) rather than a hidden default, so E3 plugs in without touching callers' signatures again; `rental_check()` in `wiring.py` gives the "no rental" adapter.
- The rental refusal is an application-level `Refusal`, not a `DomainError`: the register knows nothing of rentals.
- Lookup then removal as two `Register` methods, so the rental check sits between them without the domain knowing about it.
- Unconsulted answers from the stories and decisions, applied as is: unknown or already-removed space is the S2 `UnknownSpaceRefused`; blank number is `BlankValueRefused` (D-12); target matching follows D-11; all write use cases return nothing.
