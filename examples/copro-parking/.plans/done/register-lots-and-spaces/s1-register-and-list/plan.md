---
role: planner
status: done
reasons: []
---

# S1 Register lots and spaces and list them

## 1. Metadata
- **Type**: feature
- **Date**: 2026-11-11
- **Status**: in-progress

## 2. Goal
The manager gets a first usable register: register an owned lot, register spaces on it, list everything, refusals changing nothing, entries persisted in a JSON file. The role check and persistence are built here for S2/S3.

## 3. Context
- Empty code; Python 3.14, `unittest`, stdlib only. ADR-0001 (rings `domain`/`application`/`infrastructure` under `src/copro_parking/`), ADR-0002 (JSON, atomic write, rules in domain), ADR-0003 (role argument on every write).
- Decisions D-1..D-5, D-10..D-16 (D-14 refusals are application errors under one `Refusal` base; D-15 stored and listed text is trimmed, case kept; D-16 manager-only check first). D-6..D-9 superseded.
- Invariants: INV-001 (imports inward; no `json`/`os`/`pathlib` in domain), INV-002 (every test-case points at a real test), INV-003..006 (40 lines, complexity 10, nesting 4, 5 params), INV-007 (no baseline yet).
- Sensitive zones, escalate to the human on diff: role check in `application`; JSON write path in `infrastructure`.
- Test-cases written in `docs/business/test-cases/register-lots-and-spaces/s1-*.md` (12, `status: pending`); the developer fills `automated_test` and sets `covered` as each test goes green.

## 4. Expected behaviors
Test boundary: the application use cases (`register_lot`, `register_space`, `list_register`) with an in-memory repository; persistence behaviors go through the JSON repository adapter on a temp dir.
- AC1 Nominal: given empty register, when manager registers lot A12/owner Durand, then listing shows A12 with Durand. Boundary: `register_lot`.
- AC2: given A12, when registering " a12 ", then duplicate refusal, register unchanged.
- AC3: given owner missing or blank, then refusal.
- AC4: given lot A12, when registering space P1, then listed under A12 with its owner.
- AC5: given P1 (any lot), when registering " p1 ", then duplicate refusal.
- AC6: given unknown lot, then refusal.
- AC7/7b: listing shows lots by identifier with owner, spaces by number, empty lots included. Boundary: `list_register`.
- AC7c: blank lot identifier or space number refused.
- AC8: any non-manager role refused with the manager-only refusal on both registrations.
- AC9: after each refusal above, the register (listing and file content) equals the one before.
- AC10: register through the JSON repository, build a new repository on the same file, listing is identical. Boundary: JSON repository + use cases.
- Atomic write: a failure during write leaves the previous file intact (test by making the replace step fail). Boundary: JSON repository.
- Edge on the new operations: registering the same lot twice = duplicate refusal (AC2); empty/None arguments = blank refusal; order of registration does not change the listing (AC7b). Non-manager with blank or duplicate value: manager-only refusal wins (D-16). Listing of " a12 " shows "a12" (D-15). Refusals are raised (D-14).

## 5. Steps
- [ ] Step 1: create `src/copro_parking/domain/` (`errors.py` domain errors, `owner.py` Owner value object, `lot.py`, `parking_space.py`, `register.py` aggregate with the uniqueness/normalization/blank rules) with `tests/test_register.py`.
- [ ] Step 2: create `src/copro_parking/application/` (`role.py`, `refusals.py`, `ports.py` repository port, `use_cases.py` with `register_lot`, `register_space`, `list_register`, manager check first) with `tests/test_use_cases.py` on an in-memory repository (`tests/fakes.py`).
- [ ] Step 3: create `src/copro_parking/infrastructure/json_repository.py` (temp file + `os.replace`) with `tests/test_json_repository.py` (re-read, atomic failure).
- [ ] Step 4: create `src/copro_parking/__init__.py` and the sub-package `__init__.py` files; wiring `infrastructure/wiring.py`.
- [ ] Step 5: fill `automated_test` and `status: covered` in each test-case; run `bash tools/harness/run_all.sh` and the unit suite.

Refusals are raised errors (D-14); comparison uses a trimmed, case-folded key while the trimmed text is stored as typed (D-15); the role check runs before any validation (D-16).

## 6. Risks & edge cases
- Role check forgotten on a use case: sensitive zone; one non-manager test per write use case.
- Normalization applies to comparison only; stored text is trimmed, case kept (D-15).
- JSON file missing or empty at first read: treated as an empty register.
- Partial write: covered by atomic replace test.
- Domain must not import `json`/`os`: INV-001.

## 7. Out of scope
S2, S3, lot removal (D-10), rentals, prices, legal rules, concurrency, CLI/UI, history of owners.

## 8. Deviations
(empty)

## 9. Self-review
(empty)

## 10. Follow-up actions
(empty)

## Technical choices (for the reviewer)
Module names above; owner as value object; in-memory fake repository for use-case tests; one JSON document `{lots: [...], spaces: [...]}`, adapter-private.
