---
role: developer
status: done
reasons: []
---

# Developer, iteration 1: S3 Remove a space

Nothing committed (instructed). All 5 plan steps done, no deviation. Each test was written before its code.

## What changed
- `domain/register.py`: `Register.space(number)` (lookup ignoring case/spaces; `BlankValue`, then `UnknownSpace`) and `Register.remove_space(number)`.
- `application/ports.py`: `RentalCheck.has_rental(space_number) -> bool`. `application/refusals.py`: `SpaceRentedRefused(Refusal)`.
- `application/use_cases.py`: `remove_space(repository, rentals, role, number)`; order role, blank, unknown, rental, remove, save. Returns nothing.
- `infrastructure/wiring.py`: `NoRentalYet` (always `False`, no I/O) and `rental_check()`. JSON repository untouched.
- Tests: `test_register.py` `Removal` (5), `test_use_cases.py` `Removal` (10), `test_json_repository.py` `JsonRemoval` (3) plus `remove_space` added to the corrupt-store loop (D-19); `StubRentals` (recording stub) in `fakes.py`.
- The six `s3-*` test-cases: `automated_test` filled, `status: covered`. Plan steps ticked.

## Red evidence
- Domain: `test_register.Removal` 5 errors before the code (`AttributeError: 'Register' object has no attribute 'space'` / `'remove_space'`), then 23 OK.
- Use case: `ImportError: cannot import name 'remove_space'` (suite 36 run, 1 error), then 68 OK.
- Persistence tests passed at once, since they exercise the existing save path. To check they can fail, I removed `repository.save` from `remove_space` for one run: 6 failures and 1 error (including 2 `JsonRemoval` tests); restored, green.

## Results
- Unit suite: 72 tests OK (54 before, +18). Harness self-tests OK.
- `bash tools/harness/run_all.sh`: exit 0, no violation; 28 test-cases covered_ok, 0 orphan.
- Mutation, critical scope: 90.6% (48/53). First run 88.7%; one real survivor, `NoRentalYet.has_rental` `return False` to `None` (falsy, so invisible through the `if`). I added `test_the_default_rental_check_answers_no_rental_for_every_space`, which states the port's bool contract and kills it. Baseline for INV-007 is still unset: suggest threshold 90.
- Remaining 5 survivors are equivalent or out of S3: `frozen=True` to `False` on 4 value objects (immutability untested, pre-existing; `use_cases.py:21` is `LotEntry`) and JSON `indent` 2 to 3 (layout).

## Behaviors added (not listed in the plan)
- `rental_check()` returns a `RentalCheck`; the concrete class `NoRentalYet` is public in `wiring.py`. No consumer-visible rule invented.
- The `SpaceRentedRefused` message names the number as stored; the text is not a contract.
- `Register.space()` / `Register.remove_space()` are public domain methods; `remove_space` on an unknown or blank number raises the same `UnknownSpace`/`BlankValue` as `space`.

## Notes for the reviewer
- Sensitive zones: the role check is the first line of the new use case (tested with 4 non-manager values x 5 numbers, port never asked). The JSON write path is not modified.
- I ran one read-only `git diff --stat` by mistake while checking; it changed nothing.
