---
role: developer
status: done
reasons: []
---

# Developer note, iteration 1 (edge-codes-and-concurrency)

Skills announced and applied: `plan-driven-dev` (implementation steps) and `behavior-driven-testing`. The plan was followed as written; no deviation, no question.

## Commits (shared branch, only files under `examples/meal-delivery-cart`)

- `6cd63de` A blank code is no code when pricing a cart (Steps 1 and 2: `EdgeCodesTest` B1-B7, `Pricing.kt`, 7 test-cases)
- `d5e5b2c` Refuse rules whose promotion code is blank (Step 3: B8-B10, `PricingRules.kt` check and doc comment, 3 test-cases)
- `d4284d4` Show that simultaneous pricings give the result each gives alone (Step 4: `ConcurrentPricingTest` T1-T6, 6 test-cases)
- `8b4070b` Test-cases: a code that is only blank is no code (Step 6: wording of `code-matches-exactly` and `unknown-code-gives-no-discount`; their `automated_test` unchanged)

Red then green was watched for B1-B3 (3 failures before the change) and B8-B10 (2 failures before the check; B9 holds trivially before the check as the other problems already refuse). B4 and B5 pin existing behavior and were green at once, as the plan says.

## Code change in `src/main` (two lines)

- `Pricing.kt`: `val code = code?.takeUnless { it.isBlank() }` after the currency `require` (the parameter keeps its public name `code`; the local shadows it).
- `PricingRules.kt`: `require(promotion.code.isBlank().not())` in the promotion block, after the minimum checks; doc comment extended.

No existing test changed; the 60 existing test-cases and tests are untouched. 78 tests, 76 test-cases (60 + 16 new; one per new test: 7 + 3 + 6).

## Verification

- `tools/harness/_maven.sh -o test`: 78 tests, 0 failures. `bash tools/harness/run_all.sh`: exit 0 (INV-001..004, INV-007 clean; INV-005: 76 covered_ok, 0 pending, 0 broken, 0 orphan).
- `trim()` variant of the normalisation: `a non-blank code is never trimmed or reinterpreted` goes red. `isEmpty()` variant: 4 tests red (blank, definition-by-characters, rules). Restored from a file copy.
- **Step 5 (not committed, reverted from a file copy, working tree clean after)**: a top-level `private var last: Money?` that the subtotal passes through.
  - With `Thread.yield()` between write and read: T1 and T2 fail at 200 rounds (results of another cart, e.g. subtotal 3020 for a cart of 150). `check_layers.py` reports INV-007 on `PricingKt.last` (and INV-004 on `Thread.yield`).
  - Without the yield (a realistic narrow race): the tests at 200 rounds did NOT fail in 3 runs; at 20000 rounds one failure per run in 2 runs. Per the plan ("raise the rounds in the test, not the threshold of INV-007"), `rounds` is now 20000 (about 1.8 s for the class). INV-007 is the real guard; the tests remain a tripwire.
- **Flake check**: `ConcurrentPricingTest` run in 35 separate JVM runs (surefire, 20000 rounds, 16 threads): 35 passed, 0 failed. Assertions are equality only, no sleeping, no randomness, join timeout 30 s.
- **Mutation (`run_all.sh --with-mutation`, scope critical, PIT)**: score 82.3% (65 killed / 79 generated), no threshold set (a human decision; none written). 14 survivors, none introduced by a behavior of this request:
  - `Money.kt` (lines 35, 36, 37, 46: Kotlin null-check intrinsics and `Money::exactly` returning 0) and `Percentage.kt:7` `getScale` returning 0: all in code this request did not touch (survivors of earlier requests; I did not re-run a baseline to compare, so I cannot say whether the score moved).
  - `Pricing.kt:28` twice, `RemoveConditionalMutator_EQUAL_ELSE`: the file has 26 lines, so this is the inlined stdlib `isBlank()` (`length == 0` replaced by false). Equivalent: the empty string is then still blank through the vacuous "all characters are whitespace". Not excluded in `pom.xml` (decision for a person); no behavior is unprotected.
  - Nothing survives on the new `PricingRules` check or on the normalisation `takeUnless`.
- "Wrong direction" signals checked: no test mirrors the implementation; B6 pins the definition by named characters, not by calling `isBlank()`.

## Behaviors added

None beyond the plan. Noted for the reviewer (all in the plan or its decisions):
- The rules refusal is an `IllegalArgumentException` with a message ("The promotion code is empty or only blank"); the message is not a contract and no test pins it (plan, section 3).
- `Promotion(code = "")` alone still builds (tested).
- A promotion code made only of U+200B is accepted and matched by exact text (D-45; tested).

## For the reviewer / follow-ups (not done by me)

- Sensitive money zone `domain.pricing` is touched (one line): a person reads that diff.
- U+0085 and U+001C..U+001F are not asserted (accepted gap, plan B6).
- Plan sections 9 (self-review) and 10 (follow-ups) and `decisions.md` are not mine and were left alone; release notes for the two behavior changes remain to do.
- Local scratch (not in the repo): Maven wrapper script in the session scratchpad, since `_maven.sh` is only a sourced resolver.
