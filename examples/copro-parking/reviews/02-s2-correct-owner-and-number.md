---
role: reviewer
status: escalate
verdict: GO
reasons:
  - gauntlet green; S2 AC1-AC6, D-16, D-19..D-23 verified by own probes; both S1 majors closed; no blocking finding, 1 new open major
  - escalate: the diff touches the sensitive zones (manager-only check, JSON read path, listing sort); the human confirms
severity: major
open_majors:
  - "Natural sort key crashes with a raw ValueError on an identifier or number holding a digit-like character that is not a decimal digit (e.g. '²', 'P1²'): save and listing fail; no decision covers it (src/copro_parking/domain/text.py:22)"
---

# Review 1: S2 Correct a lot's owner and a space's number

Skill `premerge-review`, criticality critical (role check, persisted format, sort). No commit: S2's changes on top of S1 reviewed in the working tree.

## Gauntlet (run by me)
- `python3 -m unittest discover -s tests`: 53 OK.
- `bash tools/harness/run_all.sh`: exit 0, 22/22 test-cases covered, 0 orphan tests.
- Mutation `--scope critical`: 88.9% (40/45). The 5 survivors are the S1 equivalents (`frozen=True` x4, `indent=2`); the developer's note matches.

## Probes (own scripts, real JSON repository)
- D-16: Owner role, `None` role, with blank values: `ManagerOnly` first, file untouched.
- AC3b/AC4 and order: blank/`None` -> `BlankValueRefused`; unknown lot/space -> `UnknownLotRefused`/`UnknownSpaceRefused`; blank beats unknown; unknown beats duplicate; `' p1 '` on P2 -> `DuplicateSpaceRefused`. File byte-identical after every refusal.
- D-21: same owner (`' a12 '` -> `' Durand '`), `P1` -> `p1` accepted, stored text becomes the new trimmed text.
- AC1/AC2/AC6: owner " Martin ", `P1` -> " P9 " keeps lot A12, no P1 left; a fresh repository reads the same listing.
- D-20/D-22: `[a2, A12]`, `[P9, P10]`; ties follow registration order (tests).
- D-19/D-23: 9 corrupt stores (bad JSON, binary, top-level list, duplicate lot, orphan space, blank owner, `null`, string, numeric owner) -> `StoreUnreadable` on list, register, and both corrections; file byte-identical, no temp file left. A non-manager gets `ManagerOnly` before the load (D-16 order). Atomic write (temp file + `os.replace`) unchanged.

## S1 majors
- Corrupt store: closed (D-19, D-23, probes above).
- Natural order: closed for ordinary text (D-20), but see M1.

## Findings
- **major M1** `domain/text.py:22` · angle: bugs. `natural_key` tests `p.isdigit()` while the split uses `\d`: `'²'.isdigit()` is true but not a `\d` match, so `int('²')` raises a raw `ValueError`. Probed: `register_lot(..., '²', ...)` crashes in `save` (file unchanged), and an in-memory register or a hand-written store holding such an identifier or `'P1²'` makes `list_register` crash. Same class as S1's raw-error major. Fix: test `p.isdecimal()` (or the `\d` match) instead of `isdigit()`, with a test.
- **minor m1** Test-first claim cannot be verified from history (nothing committed). The tests are at behavior level and the mutation score holds; no defect traced to process.
- **minor m2** `StoreUnreadable` sits in `refusals.py` but is not a `Refusal`; fine per the plan, only a naming surprise for a caller catching `Refusal`.
- **minor m3** `OSError` on read (permissions, a directory at the path on write) is not converted; D-23 does not list it. Out of D-19's scope as decided.

## Compliance
ADR-0001 layers respected (harness green, domain free of I/O), ADR-0002 write path unchanged, ADR-0003 manager check first in both new use cases. Vocabulary consistent with decisions D-19..D-23.

Verdict: GO (one major, under the threshold of three), status `escalate` for the human: three sensitive zones touched. M1 goes to the next planner.
