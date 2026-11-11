---
role: developer
status: escalate
reasons:
  - Sensitive zones touched: owner role check (`_require_owner` in `application/offer_use_cases.py`) and the offers write path (`infrastructure/json_offer_repository.py` via `atomic_file.py`). The brief says such a diff goes to the human.
  - One interim behavior no document decides (dangling offer in the listing, see "Behaviors added"); it disappears with S4.
---

# Developer note: S1 Offer a space and list the open offers

Skills applied: `plan-driven-dev`, `behavior-driven-testing`. Nothing committed, git untouched, so there are no commits to list.

## Result
- Plan followed, steps 2 to 6. Step 1 deviation: the 22 test-cases were written straight as `status: covered` once their tests existed, not first as `pending`.
- Red before green: tests (`tests/test_offer_use_cases.py`, `tests/test_json_offer_repository.py`, 3 in `tests/test_register.py`, fakes `FixedClock` and `InMemoryOfferRepository`) were written first and ran red (`ImportError: cannot import name 'Clock'`, 5 modules in error). Then the code was written; the first full run was green.
- `python3 -m unittest discover -s tests`: 177 tests OK (was 41 before S1 plus the new ones).
- `bash tools/harness/run_all.sh`: exit 0, 69 test-cases all covered_ok, 0 orphan. Harness self-tests: 14 OK.
- Mutation `--scope critical`: 90.6% (164/181), equal to the baseline; the 17 survivors are equivalent (`frozen=True` True->False on dataclasses, `indent` 2->3, `_next_number = 1` overwritten by `restore`).
- `invariants.md`: "Not written yet" removed from the offers write-path line only; the `check_proposal` and `OfferCheck` lines keep theirs.

## Files
- domain: `dates.py`, `offers.py` (`Period`, `Offer`, `OfferBook`), `errors.py` (+`InvalidPeriod`, `InconsistentOffers`), `register.py` (+`lot_of`).
- application: `ports.py` (+`OfferRepository`, `Clock`), `refusals.py` (+4), `offer_use_cases.py`, `use_cases.py` (one mapping line and one import for `InvalidPeriod`).
- infrastructure: `json_offer_repository.py`, `wiring.py` (+`json_offer_repository`, `SystemClock`, `system_clock`).
- docs: `docs/business/test-cases/offer-a-space/` (22 files), `invariants.md`.

## Behaviors added (not stated by the plan)
1. **Dangling offer**: until S4, `remove_space` can remove a space that has an offer. `list_open_offers` then skips that offer (no lot or owner to show) instead of failing. Tested. Question for the human: skip, or fail with `OffersUnreadable`? It ends when S4 blocks the removal.
2. Order inside invalid input: the period is checked before the blank space/offerer. Not tested as a pair.
3. Input and ownership refusals come before the offers file is read: an unreadable offers file does not hide `InvalidPeriodRefused`, `UnknownSpaceRefused` or `NotTheOwner`. Tested. The register is read before the offers.
4. A stored file `{}` or one lacking `next_number` reads as `next_number = 1`; a stored offer then has to be numbered below it, else unreadable.
5. `Period.of` / `Period.starting_from`: a past start is refused only for new offers; stored past offers load fine.
6. Space numbers are stored as registered (not as typed).

## Sensitive zones touched
`application/offer_use_cases.py` (`_require_owner`, role first) and `infrastructure/json_offer_repository.py` (atomic write, unreadable file never overwritten). The `OfferCheck` zone (S4) is not touched.
