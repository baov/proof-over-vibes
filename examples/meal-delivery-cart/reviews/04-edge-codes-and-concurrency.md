---
role: reviewer
status: escalate
verdict: GO
reasons:
  - "Gauntlet green; no blocking finding; one major (<= 2), so GO by the mechanical rule."
  - "Escalate: the diff touches the sensitive zone domain.pricing (one line in Pricing.kt); a person reads that diff."
severity: major
open_majors:
  - "C4 (a pricing never waits for another) is checked by nothing: @Synchronized on price() passes the whole suite, INV-004 and INV-007 (M1)."
---

# Pre-merge review: claude/bank-account-poc-1435f8 (edge-codes-and-concurrency, n=1)

**Verdict: GO** · status `escalate` (money zone)
**Date**: 2026-10-18 · **Base**: bd8b550..8b4070b · **Scope**: examples/meal-delivery-cart only, 22 files, +597/-3 (2 lines of `src/main`, 2 test classes, 18 test-cases)
**Criticality**: critical. Signals: `domain.pricing` (declared sensitive zone) and `domain.rules` touched; money flow; a contract consumed by callers changes (blank code, rules construction).

## Summary

Two behavior changes (D-40, D-45, D-46) in two production lines: a blank cart code is normalised to "no code" after the currency check, and `PricingRules` refuses a blank promotion code. Both are correct, ordered so that no other refusal is hidden, and the definition of "blank" matches D-45 character for character (verified, below). The concurrency tests are a real tripwire against shared mutable state (they failed 8/8 in my experiments) and are not flaky (30/30 green). The remaining gap is that nothing verifies "never waits" (C4), and the ADR-0004 wording is a little stronger than what INV-007 can carry.

## Gauntlet

| Check | Result |
|-------|--------|
| Test suite | OK: 78 tests (run by the mutation step and by my repeated runs) |
| Lint / format | not available (no linter configured in the project) |
| Harness invariants (INV-001..004, INV-007) | OK, exit 0 |
| Test-case bridge (INV-005) | OK: 76 covered_ok, 0 pending, 0 broken, 0 malformed, 0 orphan |
| Mutation (critical) | run: 82.3% (65/79), no threshold set, so nothing fails. 14 survivors, none on the new check or the `takeUnless`; 2 on `Pricing.kt:28` are the inlined stdlib `isBlank()` (`length == 0` -> false), an equivalent mutant (empty text is still blank through the vacuous `all`). The rest are in `Money.kt` / `Percentage.kt`, untouched by this diff |
| Test-cases touched | 18 read (16 new, 2 reworded: `code-matches-exactly`, `unknown-code-gives-no-discount`). Their `automated_test` is unchanged and still true: the old tests never supplied a blank code, so no old assertion changed meaning; the new coverage is `EdgeCodesTest` |

Gauntlet command: `MVN_OFFLINE=1 bash tools/harness/run_all.sh --with-mutation` from the project folder, exit 0, about 107 s.

## Verification done in a scratch copy (outside the repository)

**Blank definition against D-45.** One code per character, cart side and rules side, rules with a promotion at minimum 1000:
- Cart code treated as no code, and rules refuse it as a promotion code: U+0009..U+000D, U+001C..U+001F, U+0020, U+00A0, U+1680, U+2000..U+200A (including U+2007), U+2028, U+2029, U+202F, U+205F, U+3000.
- Ordinary code (cart: `UNKNOWN_CODE`; rules: accepted): U+0085, U+200B, U+FEFF (also U+180E, U+2060, which I added).
- This is exactly D-45. The two sides agree on every character.

**Interplay with each other path** (codes `""`, `" "`, U+3000): foreign-currency line gives `IllegalArgumentException` with or without promotion in the rules; amount too large gives `AmountTooLargeException` with or without promotion; empty cart, below the minimum, and rules without promotion all equal the price with no code. The currency check runs before the normalisation, so D-42 order is intact and a blank code hides no refusal.

**Order of the rules refusal.** The blank-code `require` is last in `init`. Every earlier refusal (fee currency, fee sign, rate range, minimum currency, minimum sign) still fires first, so a blank code never hides another problem; the cost is that a rules set with two problems reports the other one first and the blank one after correction (message only, not a contract). Not pinned by a test (all are `IllegalArgumentException`), see m3.

**Caller behavior change.** A blank code gave `UNKNOWN_CODE` before; it now gives no reason. No pre-existing test supplied a blank code, so no old test turned red, and the change is pinned only by the new `EdgeCodesTest` (B1 to B7), which is correct. Rules that used to build with a blank promotion code now throw at construction (B8 to B10).

**Concurrency experiment** (the Developer's `var`, redone; `rounds` = 20000, 16 threads, `ConcurrentPricingTest`):

| Experiment | Tests red | INV-007 (`check_layers.py`) |
|---|---|---|
| top-level `private var last: Money?` with `Thread.yield()` between write and read | 2 of 6 in 5/5 runs ("one cart" and "different carts") | flagged: `PricingKt.last does not have modifier FINAL` |
| same `var`, no yield | 2 of 6 in 4/5 runs, 1 of 6 in 1/5 | flagged |
| shared final array `private val last = arrayOfNulls<Money>(1)` used the same way | 2 of 6 in 3/3 runs | **not flagged** (exit 0) |
| `@Synchronized` on `price()` | 0 of 6 (3.4 s instead of 1.7 s) | **not flagged** (exit 0); INV-004 does not flag it either |

So the tests are an effective tripwire for shared mutable state, including the case INV-007 cannot see (final field, mutable content). They are blind to locks. Developer's report said the no-yield variant failed in 1 of 2 runs at 20000 rounds; on my machine it failed in 5/5, so the margin depends on cores and is real but not guaranteed.

**Flakiness and cost.** 30 separate Maven runs of `ConcurrentPricingTest` on the real code: 30 passed, 0 failed. The class takes 1.5 to 1.9 s (6 tests, equality assertions only, no sleep, no randomness, join timeout 30 s). The 20000-round tests do not cost enough to lower.

## Findings

### Blocking
None.

### Major
- **[M1] C4 "a pricing never waits for or fails because of another" is verified by nothing** — `src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt` (`a pricing never fails or waits because of another`) · `docs/technical/invariants.md` INV-007 · angle: bugs/compliance
  The test only asserts that no exception is thrown and that threads finish within 30 s. Adding `@Synchronized` (or any lock) to `price()` keeps all 78 tests green, INV-004 and INV-007 green (INV-007 states it does not ban locks; INV-004 bans only `java.util.concurrent`). ADR-0004 forbids locks and says simultaneous use is "enforced by structure", but no rule enforces the lock ban. The test-case wording ("finishes within the time limit") is honest, but a reader of C4 would believe it is checked. Recommendation: either add a cheap structural rule (ban `synchronized` / `@Synchronized` / `kotlin.concurrent` locks in the core, as an addition to INV-004 or INV-007), or state in the test-case and in ADR-0004 that C4 is carried by review alone. Not blocking: the ADR is explicit, nothing in the diff adds a lock, and the limit is disclosed in INV-007. Hesitated with minor; kept major because C4 is an acceptance criterion with no check.

### Minor
- **[m1] D-45 names U+0085 (not blank) and U+001C..U+001F (blank) but no test pins them** — `EdgeCodesTest.kt` `what counts as blank for a code is pinned by named characters` · angle: bugs. Also unpinned: U+1680, U+2000..U+200A except U+2003/U+2007, U+2028, U+2029, U+205F. A switch to a Unicode White_Space regex would flip U+0085 and U+001C..U+001F unnoticed, and mutation cannot see it. The plan accepted this gap; adding the decided characters to the map costs one line each. Hesitated with major; kept minor because the main classes are pinned and I verified the behavior by hand.
- **[m2] The definition of blank is "Kotlin `isBlank()`", not a fixed table, so it follows the JDK's Unicode data** — `Pricing.kt:13`, `PricingRules.kt:24` · angle: compliance. Verified on JDK 21.0.8. A JDK upgrade may change which rare characters are blank (U+180E was whitespace in older Unicode). Acceptable; the named-character tests would show it. Mention it in D-45 or the test-case if a portable contract matters.
- **[m3] ADR-0004's "this ADR and INV-007 are what carry the guarantee" reads stronger than INV-007's reach** — `docs/technical/adr/0004-*.md` (Consequences) · angle: debt. Honest answer to the question asked: the claim is only partly honest. INV-007 catches a `var`, `lateinit var`, or mutable `object` field, and nothing else: a final field holding mutable content (`val x = LongArray(1)`, a `HashMap` memo, a `lazy`) passes it (verified), and locks pass it (see M1). INV-007 itself documents these limits ("tests of simultaneous use and ADR-0004 carry the rest") and the test class header says "smoke check and tripwire", so no one is misled who reads them. But ADR-0004 should name the same limit (final mutable content, locks) rather than just point to INV-007. In practice the final-array case was caught by the tests (3/3), not by INV-007.
- **[m4] The "whatever other rule problem" test cannot tell which refusal fires** — `EdgeCodesTest.kt` `a blank promotion code is refused whatever other problem there is` · angle: bugs. Every case asserts `IllegalArgumentException`, so the order of the checks (and thus which message a caller sees first) is unpinned. Nothing is hidden today (shown above); say so in the test name or assert the message fragment of the first problem if the order matters.
- **[m5] Release notes for the two caller-visible changes are not done** — `developer-1.md` ("release notes ... remain to do"); the architect asked for them · angle: debt. No release-notes file exists in the project; the Orchestrator should carry it to whoever communicates changes to callers (blank cart code: no longer `UNKNOWN_CODE`; rules with a blank promotion code: now refused at construction).
- **[m6] `require(promotion.code.isBlank().not())`** — `PricingRules.kt:24` · `promotion.code.isNotBlank()` reads better. One-line change.
- **[m7] Equivalent PIT survivors on `Pricing.kt:28` (inlined `isBlank`) are not documented** — `pom.xml` · angle: debt. Harmless (empty text is blank either way), but the line number points into a 26-line file; add a comment in the report baseline or an exclusion with a reason, as INV-006 asks, when a threshold is set.

## Checks not performed

- Lint / format: none configured in the project.
- Mutation threshold: none exists, so INV-006 cannot fail; the 82.3% score is information only. I did not compare with a baseline from before this request.
- Test-cases of the previous requests (60) were not re-read; only the 18 touched by the diff.
- The harness engineer's commit 096a281 (INV-007) and ADR-0004 are outside the diff; INV-007 was reviewed only through its behavior in my experiments and the limits it states.
- No consumer-side adapter exists in the project (`src/main` holds only domain and application), so how an outer layer maps a refused rules set is out of reach of this review.

## Positive notes

- The two production changes are two lines, placed so that existing refusals keep their order (D-42), and the cart side and rules side use the same definition, so a code the rules accept can always be matched by a non-blank supplied code.
- The tests pin behavior by named characters and by comparison with the price with no code, not by calling `isBlank()` themselves; the Developer's `trim()` and `isEmpty()` variants were killed.
- The concurrency tests are honest about their reach (class header), compare with the solo result, are deterministic in their assertions, and were demonstrably sensitive: they caught every shared-state variant I tried, including the one INV-007 misses.
