---
role: developer
status: done
reasons: []
---

# Developer note, S3 Withdraw an offer (iteration 1)

Nothing committed (asked not to touch git). Skills applied: `plan-driven-dev` (implementation steps), `behavior-driven-testing`.

## Test-first
- Step 1: 17 test-cases `s3-*.md` written as `status: pending`; `run_all.sh` showed them as pending warnings.
- Step 2: tests written before any code. Red shown: `python3 -m unittest discover -s tests` gave `FAILED (errors=11)` (`test_offer_use_cases` could not import `WithdrawRequest`/`withdraw_offer`; 10 JSON withdrawal tests errored on the missing import).
- Then domain, application, refusals; green: 242 tests OK (188 before, +54). Test-cases switched to `covered`, 94 test-cases, 0 pending, 0 broken.
- One test was never red: the stored-pair tie order in `OfferBookWithdrawal` already passed on the stable sort; I made the order explicit in code (number in the sort key) and the test pins it.

## What changed
- `domain/errors.py`: `UnknownOffer`, `InvalidOfferNumber`. `domain/offers.py`: `offer_number()`, `OfferBook.open_offer`, `OfferBook.withdraw`, number as last key of `open_offers`.
- `application/refusals.py`: `UnknownOfferRefused`, `InvalidOfferNumberRefused`; both registered in `_REFUSALS`. `application/offer_use_cases.py`: `WithdrawRequest`, `withdraw_offer` (5 parameters), `_require_owner` message now covers both actions.
- `infrastructure/`: untouched. `decisions.md`: untouched by me.
- Tests: `tests/test_offer_use_cases.py` (`OfferBookWithdrawal`, `WithdrawRules`, `WithdrawUnknownOffer`, `WithdrawInvalidInput`, `WithdrawNotTheOwner`, `WithdrawRoleRule`, `WithdrawRefusalOrder`, `WithdrawStores`, `WithdrawEdges`), `tests/test_json_offer_repository.py` (10 tests).

## Results
- `python3 -m unittest discover -s tests`: 242 OK. Harness selftests: 14 OK.
- `bash tools/harness/run_all.sh`: exit 0, no warning.
- `python3 tools/harness/run_mutation.py --scope critical`: 91.0% (181/199), threshold 90. 18 survivors, none in the behavior of S3: `frozen=True -> False` on dataclasses (including `WithdrawRequest`), the initial `_next_number = 1`, and `indent=2 -> 3` in the three JSON repositories (equivalent, pre-existing). `--scope diff` not used (no-op here).
- Glossary check ok.

## Behaviors added (no document decides them)
- When both the offerer and the number are unusable, the offerer is reported first (`BlankValueRefused`), then the number (`InvalidOfferNumberRefused`). D-66 says only "invalid input"; the types and this inner order follow the plan's names and the field order of `WithdrawRequest`. Pinned by a test.
- `OfferBook.open_offers` now orders by start, natural space order, then offer number (was implicit).
- A missing register is not read when the offer is unknown (the offers are loaded first): with an unreadable register and an unknown offer, the refusal is `UnknownOfferRefused`, not `StoreUnreadable`. Invalid input and role stay before any store.

## Sensitive zones touched
`application/offer_use_cases.py` (role check kept first, new owner-only write entry point `withdraw_offer`). `use_cases.py` only gained two `_REFUSALS` entries and imports. `json_offer_repository.py` and `atomic_file.py` untouched. The diff escalates to the human per the brief.

## Carried over
M1 (orphan offers) deferred to S4: S1..S3 must not be released without S4. M2 (wording) is D-68, already in `decisions.md`.
