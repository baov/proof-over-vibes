---
role: developer
status: done
reasons: []
---

# Developer note, iteration 1: blank, empty or absent identifiers

Skills announced: `plan-driven-dev` (implementation steps), `behavior-driven-testing`. The plan was followed without deviation.

## Commits (on the shared branch, nothing pushed)

1. `0b55761` Refuse a booking whose patient identifier is absent, empty or blank (MISSING_IDENTIFIER): `RefusalReason.MISSING_IDENTIFIER`, `BookingRule.isMissing` (Unicode White_Space, `\p{IsWhite_Space}*`), first check of `decide`, `BookSlot` skips the store when an identifier is missing. Test 1 + its test-case. Seen red first (the null patient was stored and the next read threw).
2. `6c151f1` Missing slot identifier, what is not blank, both missing. Tests 2, 3, 4 + 3 test-cases.
3. `8773ed3` Order (missing first) and "changes nothing". Tests 5, 6 + 2 test-cases.
4. Reword of `refusal-order-unknown-first.md` (title only; its test is unchanged).

## Red proofs

Tests 1 was red naturally. Tests 2-5 passed at once after step 1, so the code was broken on purpose and restored each time: slot half of the check removed (test 2 red), `\p{IsWhite_Space}` replaced by a class with `\s`, U+200B and U+001F (tests 1, 2, 3 red), missing check moved after the other checks (tests 1, 2, 5, 6 red). Test 6 (nothing changes, later bookings still succeed) was not broken separately: the first red of test 1 already showed a stored null patient breaking later bookings.

## Gauntlet

- Full test suite: green. INV-001: green. INV-002: 28 test-cases, 28 covered_ok, 0 orphan.
- Mutation, scope critical (`run_all.sh --with-mutation`): 100.0% (29 killed / 29 generated), no survivor. No threshold or baseline recorded (human decision).

## Behaviors added

None beyond the plan. Noted for the reviewer:
- `BookingRule.decide` now takes the slot identifier as a second parameter, and `BookingRule.isMissing(PatientId, SlotId)` is a new public static method. Both are internal to the module (the only caller is `BookSlot`); no consumer sees them.
- `RefusalReason.MISSING_IDENTIFIER` added at the end of the enum (D-36).

## Points for the reviewer

- `BookSlot` calls `BookingRule.isMissing` only to decide whether to read the store, as the plan describes; the refusal itself always comes from the rule.
- `BookSlotTest` has a store decorator that throws on a missing identifier (local to the test file, no mocking framework), proving no lookup is made.
- Zero-width characters read as not blank (D-37); surrounding white space is not trimmed.

## Questions

None.
