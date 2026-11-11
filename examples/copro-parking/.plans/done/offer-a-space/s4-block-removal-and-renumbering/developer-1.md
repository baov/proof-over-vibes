---
role: developer
status: done
reasons: []
---

# Developer 1: S4 A space with an open offer cannot be removed or renumbered

Skills applied: `plan-driven-dev` (implementation steps) and `behavior-driven-testing`. All 7 steps of `plan.md` are done and ticked. Nothing committed, git untouched.

## Test first, red before green
- Step 1: the 15 new test-cases were written first as `status: pending` (the harness listed 15 pending), the two existing `s3-*` cases edited (D-70, D-69).
- Step 2 (domain): `OfferBookOpenOffer` written first; red = 5 `AttributeError` (`has_open_offer` missing); then green.
- Steps 3 and 4: tests and fakes written first; red = `ImportError` on `OfferCheck` in 5 test modules (a signature change breaks every importer); the port, refusal and use cases then made `test_use_cases` green; JSON and offer tests written next, red = `ImportError` on `offer_check`; the adapter then turned them green except the D-70 and m3 tests.
- Step 5: red = 3 errors (`test_an_unreadable_register_wins_over_an_unknown_offer_whatever_the_number`, numbers 2, 3, 99) and 3 failures (`__cause__` was set); then `withdraw_offer` changed, green.
- Step 6: the two orphan tests that used `remove_space` now store the orphan as a pre-S4 file would (`store_orphan` helper); re-registration test (D-69) added in `OrphanOffersAlreadyStored`. The orphan test was renamed `..._whose_space_is_not_registered_...` and its test-case reference follows.
- Step 7: test-cases filled (`status: covered`), "Not written yet." removed from the fail-closed `OfferCheck` line of `invariants.md`.

## Results
- Unit suite: 303 tests, OK (242 before: +61).
- `bash tools/harness/run_all.sh`: exit 0, 109 test-cases, 109 covered_ok, 0 pending, 0 orphan test.
- Harness selftests: 14 tests, OK.
- Mutation, `--scope critical`: 91.3 % (188 / 206, threshold 90). The 18 survivors are the existing kinds (`frozen=True` True->False, an indentation 2->3, `_next_number = 1`); none sits on a line S4 added or changed.

## Changes
- Domain: `OfferBook.has_open_offer(space_number, today)` (compares by `key`, end not before today).
- Application: port `OfferCheck`; refusal `SpaceOfferedRefused`; `remove_space(repository, rentals, offers, role, number)`; `change_space_number(repository, offers, role, number, new_number)`; no `except` around the offers call; `withdraw_offer` reads offers then register, then looks up, unknown offer raised `from None`.
- Infrastructure: `StoredOfferCheck` and `offer_check(repository, clock)` in `wiring.py`.
- Tests: `StubOffers`, `FailingOffers` in `fakes.py`; every caller of the two changed signatures updated (`test_use_cases.py` `Removal`, `Corrections`; `test_json_repository.py` `JsonRemoval`, `JsonCorrections`, `CorruptStore`; `test_offer_use_cases.py`).
- Docs: 15 new test-cases, 2 edited, `invariants.md` marker cleared, plan ticked and Deviations filled.

## Behaviors added (no document decides them)
- `OfferBook.has_open_offer` given a blank or non-text number raises `BlankValue` (a domain error, via `clean`) instead of answering False. Unreachable from the use cases (the number comes from the register); consumers of the port get no such error from `StoredOfferCheck` in practice. Not a question, noted for the reviewer.
- `StoredOfferCheck` accepts the number as typed or as stored (stated in the plan's technical choices, ADR-0004 says nothing more).
- An old call of `remove_space` or `change_space_number` without the `offers` argument fails with `TypeError` (decided by the plan, pinned by `test_an_old_call_without_the_offers_fails_loudly`).

None of these changes what a consumer sees through the use cases, so no question is raised.

## Deviations
Two entries in plan section 8, neither a departure: the `_registered_number` helper (keeps the register's refusal order), and the extra `FailingOffers` fake.

## Sensitive zones touched (for the human)
- Manager-only role check: `remove_space` and `change_space_number` rewritten; `_require_manager` untouched and still the first statement.
- Fail-closed `OfferCheck` call in both (new, no `except` around it, pinned by tests with `OffersUnreadable` and a `RuntimeError`).
- `offer_use_cases.py` (`withdraw_offer`, role-check file): `_require_owner` untouched and first; only the read order and `from None` changed.
- Offers write path (`json_offer_repository.py`, `atomic_file.py`): not touched.

## Not done / for others
- Orphans: no purge (D-69, out of scope). `OfferBook.add` still compares the space exactly (latent, listed in the plan's out of scope).
- Commits: none, as asked; the orchestrator commits.
