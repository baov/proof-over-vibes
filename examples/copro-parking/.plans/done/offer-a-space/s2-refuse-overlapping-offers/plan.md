---
role: planner
status: done
reasons: []
---

# S2 Refuse overlapping offers of the same space

## TL;DR
S2 adds one rule to `OfferBook.add`: a new offer sharing a day with an open offer of the same space is refused, naming that offer, last in the check order. Q1 and Q2 are answered by delegate: D-63 (a stored overlapping pair is tolerated), D-64 (the refusal names the earliest-start offer, ties by lowest number). M1 is deferred to S4.

## 1. Metadata
- **Type**: feature (prompt, no ticket)
- **Date**: 2026-11-11
- **Status**: in-progress

## 2. Goal
A space is never offered twice for the same day: an offer sharing at least one day (both dates included) with an open offer of the same space is refused with a reason that names the existing offer; offers of other spaces, adjacent days and expired offers do not block. The refusal changes nothing.

## 3. Context
- Built by S1: `OfferBook.add/open_offers/restore` (`domain/offers.py`), `offer_space` (`application/offer_use_cases.py`), `JsonOfferRepository`, fakes in `tests/fakes.py`; `_REFUSALS` mapping and `_refuse` in `application/use_cases.py`; `InMemoryOfferRepository`, `FixedClock`.
- Architect: `../architect.md`, ADR-0004. S2 brings `OverlappingOffer` (carries the existing offer number) and the overlap rule in `OfferBook.add`; refusal `OverlapRefused` in `application/refusals.py`.
- Decisions: D-48 (overlap refused), D-52 (open until the end day), D-61 (numbers), PRD 15 (overlap last). D-63 replaces the load-time check of the architect's note.
- Invariants: INV-001 rings, INV-002 each test has a test-case, INV-003..006 (`offer_space` stays at 5 parameters, no new one; `add` stays short), INV-007 mutation score of the critical scope not below 90, INV-008 no system date: `add` receives `today`, it never reads it.
- Sensitive zones (a diff escalates): `offer_use_cases.py` (role check, not changed in meaning) and the offers write path `json_offer_repository.py`. S2 does not touch `json_offer_repository.py` (D-63: tolerate); `offer_use_cases.py` is touched for the `today` argument, so expect an escalation by the zone rule.
- Lessons: no `.plans/FEEDBACK.md`.

## 4. Expected behaviors
Boundary: `offer_space(registers, offers, clock, role, request)` (the use case, fakes `InMemoryOfferRepository`, `FixedClock`); persistence checks over `json_offer_repository(path)` on a temp dir.
- AC1: given an open offer of P1 from 10 to 14, when the owner offers P1 from 14 to 20 (or 8 to 10, or 11 to 12, or 5 to 30), then `OverlapRefused` naming offer 1; the sharing of a single day is enough.
- AC1 naming (D-64): given two open offers 1 (10-12) and 2 (14-16) of P1, when an offer spans 11-15, the refusal names offer 1 (earliest start; ties lowest number). The named number is the one the listing shows, readable on the error (`offer_number`).
- AC2: given an open offer of P1, when the owner offers P2 on the same days, then it is accepted.
- AC3: given an offer of P1 from 10 to 14, when offering 15 to 20 or 5 to 9 (the days next to it), then accepted; a one-day offer (start = end) on 14 is refused.
- AC4: given an offer of P1 whose end date has passed (clock moved after it), when offering P1 over those days again, then accepted (D-52: open until its end day included, so an offer ending today still blocks today).
- AC5: given an overlapping request that also fits an earlier refusal, then the earlier one wins: role, invalid period or blank, unknown space, not the owner, each tested with the overlap also present.
- AC6: after the refusal the offers file bytes (real repository), the list and `next_number` are unchanged; the next accepted offer gets the number it would have had; no file is created on a first-use refusal.
- Space comparison: the overlap uses the space as registered, so " p1 " and "P1" are the same space.
- Interface edges (`offer_space` changes): called twice with the same request: the second is refused naming the first (the S1 test `the same request twice makes two offers` is rewritten to distinct, non-overlapping periods; its test-case is updated); called with nothing/invalid value: unchanged (S1); edge of range: first day and last day shared, adjacent day; different order: offering the later period first, then the earlier one, gives the same refusal.
- D-63: given a stored file with two overlapping open offers of one space (written directly), then listing shows both, a new offer elsewhere or on free days succeeds, and a new offer overlapping them is refused naming the earliest.

## 5. Steps
Tests first; run `python3 -m unittest discover -s tests` after each step.
- [x] Step 1: test-cases. Write `docs/business/test-cases/offer-a-space/s2-*.md` (one per AC behavior and Q1/Q2, `status: pending`, `source: stories.md S2 ACn` or decisions D-63/D-64). Update `s1-offer-numbers.md` if it describes the repeated request.
- [x] Step 2: domain. `domain/errors.py`: `OverlappingOffer(DomainError)` with an `offer_number` attribute. `domain/offers.py`: `Period.shares_a_day_with(other)`; `OfferBook.add(space_number, period, today)` raises `OverlappingOffer` for the earliest-start (then lowest number) open offer of that space sharing a day with `period`; open = `today <= end`.
- [x] Step 3: application. `application/refusals.py`: `OverlapRefused(Refusal)` with `offer_number`; map `OverlappingOffer` to it in `_REFUSALS` (`use_cases.py`) or in `offer_use_cases.py`, keeping the number; `offer_use_cases.py`: pass `clock.today()` (already read once) to `add`, and catch `OverlappingOffer` around `add` before `save` so the refusal never saves. Rewrite the S1 "twice" test; tests in `tests/test_offer_use_cases.py` for AC1-AC6 and the D-63/D-64 cases. Sensitive zone: escalate on diff.
- [x] Step 4: infrastructure. None in the code; add one test in `tests/test_json_offer_repository.py` that a file holding a stored overlapping pair loads (pinning the tolerance). No load-time overlap check is added to `OfferBook.restore`.
- [x] Step 5 (developer part): docs. For the Architect (runs separately): amend the "On load ... two offers of the same space sharing a day is unreadable" lines of ADR-0004 and `architect.md` per D-63 (tolerated, only new offers are checked). The developer does not edit them. Then fill `automated_test`, `status: covered`; run `bash tools/harness/run_all.sh`, the unit suite, the harness self-tests and `python3 tools/harness/run_mutation.py --scope diff`.

## 6. Risks & edge cases
- Off-by-one on both ends of the overlap test (`a.start <= b.end and b.start <= a.end`): one test per side and per adjacent day.
- Expired but stored offers must not block; an offer ending today must still block.
- The check must run after the owner check and before `save`: a mis-ordered check would leak the existence of offers to non-owners.
- Two simultaneous callers can both pass the check: documented limit (ADR-0004), not prevented.
- Orphan offers (M1, space gone from the register) still count as blocking for their stored space number: if the number is registered again, the new owner is refused because of an offer they never made. S4 closes this.

## 7. Out of scope
Withdrawal (S3); `OfferCheck` and the `remove_space`/`change_space_number` changes (S4); price; concurrency lock; purge of expired offers.
- **M1 (orphan offers reappear under another owner): deferred to S4**, which blocks the removal and renumbering of a space with an open offer (S4 AC1, AC6). S1 and S2 must not be released alone, as the review said.

## 8. Deviations
- No change of intent. S1 tests that made overlapping offers were rewritten with non-overlapping periods: the "same request twice" test (as planned), the list-order test (its fourth offer is now P3/Martin on the same start instead of a second P2 offer, so the order [3, 2, 4, 1] holds), and the restart test of `test_json_offer_repository.py` (third offer on distinct days). Test-cases `s1-offer-numbers` and `s1-list-open-offers-order` updated to the new test names.
- `OverlappingOffer` is mapped to `OverlapRefused` inside `offer_use_cases.py` (around `add`), not in `_REFUSALS`, because `OverlapRefused` also carries the offer number.
- Tests added in `test_json_offer_repository.py`: bytes unchanged after an overlap refusal, and D-63 (stored pair tolerated).

## 9. Self-review
(empty)

## 10. Follow-up actions
(empty)

## Technical choices (for the reviewer)
- `OfferBook.add` takes `today` so the domain stays clock-free (INV-008) and expiry is judged in the domain.
- The overlap test lives on `Period`, the naming rule in `OfferBook`.
- `OverlapRefused` and `OverlappingOffer` carry the offer number as an attribute, besides the message.
