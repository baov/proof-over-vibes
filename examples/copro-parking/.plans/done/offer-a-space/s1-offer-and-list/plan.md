---
role: planner
status: done
reasons: []
---

# S1 Offer a space and list the open offers

Q1-Q3 answered by delegate: D-59, D-60, D-61.

## 1. Metadata
- **Type**: feature (prompt, no ticket)
- **Date**: 2026-11-11
- **Status**: in-progress

## 2. Goal
An owner offers a registered space of their lot for a period (two dates, both included) and anyone lists the open offers. Offers live in a third JSON file, survive a restart, fail closed when unreadable. S1 brings the whole base: dates, `Period`, `OfferBook`, `Register.lot_of`, the three ports, the adapter, the clock, `offer_space`, `list_open_offers`, the refusals.

## 3. Context
- Architect: `../architect.md`, ADR-0004 (accepted); ADR-0001..0003 unchanged. Decisions D-45..D-58 (D-45/46 owner role and name, D-47/53 start not before today, D-52 open until the day after the end, D-54 offer number, D-56 current owner).
- Reused patterns: `_refuse` and the mapping table in `use_cases.py`, `Refusal`/`StoreUnreadable`, `text.clean/key/natural_key`, `atomic_file.write_atomically`, `JsonRuleRepository` as model for the adapter, `LotEntry`-style frozen public type, fakes in `tests/fakes.py`.
- Invariants: INV-001 (rings), INV-002 (a test-case per test), INV-003..006 (`offer_space` has 5 parameters: at the limit, no more), INV-007 (new files join the critical scope), INV-008 (no system date in `domain`/`application`: the `Clock` port).
- Sensitive zones (a diff touching them escalates): `_require_owner` in `application/offer_use_cases.py`; the offers write path (`infrastructure/json_offer_repository.py`, via `atomic_file.py`). The fail-closed `OfferCheck` zone is S4, not touched here.
- Lessons: no `.plans/FEEDBACK.md`. Known minor of F1.2 (digit runs over 4300 in a natural sort) not widened.
- S1 does not refuse overlaps (S2): until S2, two offers of one space may share days. Therefore the load check "two offers of the same space sharing a day is unreadable" of the architect's note is NOT in S1; S2 adds it with the overlap rule.

## 4. Expected behaviors
Boundary: `offer_space(registers, offers, clock, role, request)` with `OfferRequest(space, offerer, start, end)` returning the new `OfferEntry`; `list_open_offers(registers, offers, clock)` returning `OfferEntry(number, space, lot, owner, start, end)` (frozen); fakes `InMemoryOfferRepository`, `FixedClock`. Persistence over `json_offer_repository(path)` on a temp dir. Dates: a `date` or ISO text `YYYY-MM-DD` (D-60).
- AC1: owner offers a registered space of their lot with start and end; it appears in the list with number, space, lot, owner, start, end; the call returns that entry.
- AC2: space unknown: `UnknownSpaceRefused`; number compared with `key` (case, surrounding spaces); the space is shown as registered.
- AC3: whole days, both included: start = end valid; end before start, missing or unreadable date: `InvalidPeriodRefused`.
- AC4: start before today: `InvalidPeriodRefused` (invalid input, PRD 15); start = today accepted. Today from the clock.
- AC5: offerer not the lot owner (compared by `key`): `NotTheOwner`; an owner of another lot is refused.
- AC6: role other than owner (manager, resident, `None`, other value): `NotAllowedToOffer`, first, before any other check and before the stores are read, even with bad dates or an unreadable file.
- AC7: no price field in request or entry.
- AC8: list open offers, no role; sorted by start, then `natural_key(space)`; empty list when none; twice gives the same list. Offers of different spaces sharing start are ordered by space ("p2" before "P10"); in S1 two offers of one space with same start can exist (no overlap rule yet): ties then keep creation order (stable sort, number order).
- AC9: open until the end date included; from the day after the end it is gone (clock moved by the test). The owner shown is the register's current owner, also after `change_lot_owner`; the offer stores the space number only.
- AC10: check order: role, invalid input (period; blank fields (D-59)), unknown space, not the owner. Each pair tested with both fitting.
- AC11: after any refusal the offers file bytes, the register and the list are identical; a refusal on first use creates no file.
- AC12: offers file invalid JSON, non-UTF-8, wrong shape, missing field, bad date, duplicate number, number at or above `next_number`: `OffersUnreadable` (a `StoreUnreadable`, not a `Refusal`) on list and offer; bytes identical afterwards. Missing or blank file = no offers.
- AC13: a new repository on the same file lists the same offers; numbers are integers from `next_number`, first is 1 (D-61), never reused; register file and rules file bytes unchanged by offering (a test asserts it).
- AC14: the limit is stated in the docstring of `offer_space` and `_require_owner` (the name proves nothing about who types); a test asserts the docstring mentions it is not an authentication, nothing more.
- Interface edges for the new public operations: `offer_space` twice with the same request: two offers, numbers 1 and 2 (S2 later refuses); `list_open_offers` empty/twice: above; invalid value: `request` fields of wrong type (`int`, `None`) are invalid input like blank (D-59); edge of range: start = today, start = end, end = last representable day not tested; different order: refusal order AC10.

## 5. Steps
Tests first, then code; run `python3 -m unittest discover -s tests` after each step.
- [ ] Step 1: test-cases. Write `docs/business/test-cases/offer-a-space/s1-*.md` (one per AC behavior, `status: pending`, front-matter as the rules ones, `source: stories.md S1 ACn`).
- [ ] Step 2: dates and period. `domain/dates.py` `parse_date(value)` (D-60); `domain/errors.py` `InvalidPeriod`; `domain/offers.py` `Period(start, end, today)`-validation (a factory taking today), `Offer`, `OfferBook` (`add`, `open_offers(today)`, `next_number`; no overlap rule). Tested through the use cases (Step 4); `tests/test_offers.py` only where they cannot reach.
- [ ] Step 3: `Register.lot_of(space) -> Lot` (additive; unknown space raises `UnknownSpace`, blank raises `BlankValue` as `space()`); existing tests untouched.
- [ ] Step 4: application. Ports `OfferRepository`, `Clock` in `ports.py` (`OfferCheck` is S4); refusals `NotAllowedToOffer`, `NotTheOwner`, `InvalidPeriodRefused`, `OffersUnreadable(StoreUnreadable)` (+ reuse `UnknownSpaceRefused`, `BlankValueRefused`); `offer_use_cases.py` with `_require_owner`, `OfferRequest`, `OfferEntry`, `offer_space`, `list_open_offers`; fakes `InMemoryOfferRepository`, `FixedClock`. Tests in `tests/test_offer_use_cases.py` for AC1-AC10. Sensitive zone: escalate on diff.
- [ ] Step 5: infrastructure. `infrastructure/json_offer_repository.py` (`{"next_number", "offers": [{"number","space","start","end"}]}`, load builds the book, any parse/shape failure becomes `OffersUnreadable`, save through `write_atomically`), `SystemClock`, factories `json_offer_repository(path)` and `system_clock()` in `wiring.py`. Tests in `tests/test_json_offer_repository.py`: AC11 bytes, AC12, AC13, failed write leaves no leftover (`os.replace` patched). Sensitive zone: escalate on diff.
- [ ] Step 6: fill `automated_test` and `status: covered`; run `bash tools/harness/run_all.sh`, the unit suite, the harness self-tests and `python3 tools/harness/run_mutation.py --scope diff`; remove "Not written yet" from the offers write-path line of `invariants.md` (harness engineer).

## 6. Risks & edge cases
- Role check forgotten or placed after a read: test each non-owner role with an unreadable store and bad dates.
- `datetime` is a `date`: guard explicitly (D-60).
- Midnight race: the use case reads the clock once per call.
- Today equals start/end boundaries and the day-after expiry: off-by-one mutants; one test per side.
- The owner shown must come from the register at list time (a stale stored owner would fail AC9 after a correction).
- Overlap on one space is possible until S2; documented, not hidden.

## 7. Out of scope
Overlap refusal (S2); withdrawal and `UnknownOffer` (S3); `OfferCheck`, `StoreAdapter` for it and the `remove_space`/`change_space_number` signatures (S4); concurrency (ADR-0004 limit); price; E5 rules; accounts.

## 8. Deviations
(empty)

## 9. Self-review
(empty)

## 10. Follow-up actions
(empty)

## Technical choices (for the reviewer)
- `Period` built by a factory that takes today, so the domain never reads the date (INV-008).
- Reviewer, please challenge: the load-time overlap check ("two offers of the same space sharing a day is unreadable", architect.md) is moved from S1 to S2, with the overlap rule. Otherwise S1, which accepts overlapping offers, would write files it cannot read.
- Public names only the developer sees: `Offer`, `OfferBook`, `Period`, `parse_date`; consumer-visible names follow the architect.
- One clock read per call; `list_open_offers` filters by `today <= end`.
