---
role: reviewer
status: escalate
verdict: GO
reasons:
  - gauntlet green (72 tests, harness exit 0, mutation 90.6%); S3 acceptance criteria verified by own probes on the real JSON repository; no blocking or major finding
  - escalate: the diff adds a write use case with the manager-only check (sensitive zone); the human confirms. The JSON write path is untouched and its atomic write is intact
severity: minor
open_majors: []
---

# Review 1: S3 Remove a space (iteration 1)

Skill `premerge-review`, criticality critical (new write use case with the role check; a persisted-format consumer). Nothing committed, working tree reviewed (S3 on top of S1+S2).

## Gauntlet (run by me)
- `python3 -m unittest discover -s tests`: 72 OK.
- `bash tools/harness/run_all.sh`: exit 0, 28/28 test-cases covered, 0 orphan tests.
- Mutation `--scope critical`: 90.6% (48/53). The 5 survivors are the known equivalents (`frozen=True` x4, JSON `indent` 2 to 3). `NoRentalYet.has_rental` returning `None` is killed. INV-007 baseline still unset.

## Probes (own script, real `JsonRegisterRepository` on a temp dir)
- D-16: roles owner, resident, `None`, `"manager"` (string), `1` x numbers `P1`, `P9`, `""`, `None`, `"  "`: always `ManagerOnly`, file hash unchanged, rental port never called.
- Order after the role: blank / whitespace / `None` / `5` give `BlankValueRefused`; `P9` gives `UnknownSpaceRefused`; neither asks the port. A fake port answering "rented" for `P1`: `" p1 "` gives `SpaceRentedRefused`, the port received `"P1"` (number as stored, even when the file holds `" Pa "`), `P1` stays listed, file unchanged.
- Default port: `" p1 "` removed, returns `None`; the listing shows A12 with no space and B1 with P2; a new repository on the same file shows the same. A second removal gives `UnknownSpaceRefused`, file unchanged.
- Reuse: `p1` registered again on B1, accepted and listed. Removing every space leaves both lots and their owners in the listing and in the file (`"spaces": []`) (D-10, D-13).
- D-19: malformed JSON and a space on an unknown lot: `StoreUnreadable`, file identical, no `.tmp` left; a non-manager still gets `ManagerOnly` first.
- Atomic write: `json_repository.py` unchanged (temp file, `os.replace`, cleanup); removal goes through the same `save`.

## Rental port (PRD 7)
Honest stub: `RentalCheck` is an abstract port in `application/ports.py`; `NoRentalYet` is the only adapter, always `False`, no I/O, no state, imports nothing but the port. The use case really consults it between the lookup and the removal: a fake port answering "rented" produces `SpaceRentedRefused`. No real rental logic is faked. Harmless caveat: a caller passes the port explicitly, so nothing in the code forces the production caller to pass the real one once E3 exists (that wiring is E3's job).

## Findings
- **minor m1** `docs/business/test-cases/.../s3-remove-space.md`, `s3-refuse-rented-space.md` · angle: debt. Both test-cases state "still there when the register is read again" / "register and its file unchanged", but `automated_test` points at the in-memory use-case test; the file-level tests are `JsonRemoval` in `tests/test_json_repository.py`. The bridge cannot see it. Recommendation: mention the second test in the text, or point at it.
- **minor m2** `application/use_cases.py:75` · angle: bugs. An exception raised by a future real `RentalCheck` propagates raw (nothing is saved, so the register is safe). No decision says what the manager sees when the rental service is unavailable; relevant when E3 lands, not now. Recommendation: the E3 planner decides it.
- **minor m3** INV-007: baseline unset; the developer suggests threshold 90 (score 90.6%). Recommendation: the human sets it as `warn`.
- Carried: m1, m2, m3 of review-1 (S2) and m4 (4300-digit identifiers) stand unchanged.

## Compliance
ADR-0001 layers respected (domain has no rental notion; refusal raised by the use case), ADR-0003 explicit role, ADR-0002 untouched. Refusals named as D-14 requires. Glossary words used. No test-case describes a wrong behavior.

## Closing view of F1.2 against the 9 PRD requirements
1 duplicate lot refused (S1), 2 unique space number + one lot (S1), 3 one owner, none refused (S1), 4 unknown lot refused (S1), 5 listing with number/lot/owner, sorted (S1/S2), 6 change owner and number with uniqueness kept (S2), 7 removal refused if rental, via a stubbed port until E3 (S3), 8 manager-only on every write, checked first (S1-S3), 9 every refusal leaves the register and the file unchanged (probed here for S3, covered earlier for S1/S2). All 9 covered with tests and test-cases; none open. Requirement 7's rental half is deliberately inert until E3.

Verdict: GO (no blocking, no major), status `escalate`: sensitive zone (manager-only check on a new write use case).
