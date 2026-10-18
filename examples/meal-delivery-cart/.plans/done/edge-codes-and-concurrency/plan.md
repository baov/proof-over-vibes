---
role: planner
status: done
reasons:
  - "Q1 answered (D-45 option A: Kotlin isBlank for cart code and rules promotion code; D-46 amends D-33/D-34). Nothing consumer-visible remains open."
---

# Price a cart, blank codes and simultaneous pricing (C1..C9)

## 1. Metadata
- **Type**: feature
- **Date**: 2026-10-18
- **Status**: in-progress (Q1 answered: D-45, D-46)

## 2. Goal

A blank or empty code supplied with a cart means no code: no discount, no reason, pricing succeeds as without a code (C7, D-40). Rules whose promotion code is blank or empty are refused when built (C8, D-40). A non-blank code keeps its meaning: exact text, case-sensitive, never trimmed (C1, D-34). Any number of simultaneous pricings of the same cart and rules each give the result they give alone (C2..C6, D-41); this is already true by construction (ADR-0004, INV-007), and the plan adds the tests that show it on the current code and would show a visible break. Acceptance criteria: C1..C9 of `docs/product/prd/price-a-cart-edge-codes-and-concurrency.md`, nothing else.

## 3. Context

Sources read: brief (`Carried over`: no major; minors out of this request), `architect.md` and `harness-engineer.md` (both done), ADR-0001..0004, `docs/technical/invariants.md` (INV-001..007), the PRD, decisions D-28, D-33, D-34, D-36, D-37, D-40..D-44, the code (`domain.pricing.price`, `PricingRules`, `Promotion`, `Cart`, `PriceCart`), `ApplyPromotionTest`, `PriceCartTest`, the test-cases of `price-a-cart/`, the plans of `.plans/done/`. No `.plans/FEEDBACK.md`.

**Code as found.** `domain.pricing.price(cart, rules, code: String? = null)`: after the currency `require`, `when { code == null -> null; promotion == null || code != promotion.code -> UNKNOWN_CODE; subtotal < minimum -> SUBTOTAL_BELOW_MINIMUM; else -> null }`; the discount is taken when `code != null && promotion != null && notApplied == null`. `PriceCart.price` is a pure delegate. `PricingRules.init` requires the fee currency, fee >= 0, and, when a promotion exists, rate within 0..100 percent, minimum in the rules currency and minimum >= 0, all with `require` (so `IllegalArgumentException`). `Cart` copies its list; every class is `val`-only; `Price` is a data class (equality by value).

**Existing tests and test-cases that treat `""` or `" "` as a code: none.** I searched `src/test` and `docs/business/test-cases`. No test supplies an empty or blank code, and none builds rules with one. What changes meaning without a test failing:
- `code-matches-exactly` / test `a code matches only the exact configured text`: its "differs by a space" is a leading or trailing space on a non-blank code (`" WELCOME10"`, `"WELCOME10 "`). Still unknown, still green. The test-case wording gets one sentence ("a code that is only blank is no code, see ...").
- `unknown-code-gives-no-discount` ("pricing with another code", "rules with no promotion at all"): still true for a non-blank code; blank is no longer "another code". Wording gets the same precision.
- Decision text D-34 ("any supplied code is then unknown") and D-33 ("empty when ... no code was supplied") are amended for blank codes by D-40. That log belongs to the product owner: listed in section 10, not edited here.

**Invariants that apply** (run `bash tools/harness/run_all.sh` after each green; the sensitive money zone `domain.pricing` is touched, a person reads that diff)
- INV-001 (`domain` free of foreign imports): `isBlank()` is the Kotlin stdlib, no import. INV-004 (core purity): no clock, no `java.util.concurrent`, nothing in `domain`/`application` changes for concurrency; the concurrency tests use `java.util.concurrent` and live in `src/test`, which INV-004 excludes. INV-007 (every field of the core is final): the change adds no field; it must stay green, and it is what carries C2..C6 together with ADR-0004. INV-005: every new test has a test-case and every test-case a test. INV-006: mutation on the diff, see section 4 "What mutation cannot see". INV-002/003 untouched.

**Decisions applied, not reopened**: ADR-0001..0004; architect: normalise once at the top of `domain.pricing.price` (`val code = code?.takeUnless { it.isBlank() }`), the existing `when` unchanged on the normalised code, a non-blank code never trimmed; blank check on the rules in `PricingRules.init` inside the `if (promotion != null)` block, same `isBlank()`; `Promotion(code = "")` alone still builds. D-28/D-36/D-37 (rules refuse with `IllegalArgumentException`), D-42 (currency refusal wins).

### What the plan decides from the documents (no question)

- **Blank code with rules that have no promotion.** C7: "pricing succeeds as without a code" (R11). So: no reason, not `UNKNOWN_CODE`. D-34's "any supplied code is then unknown" is amended by D-40 for blank codes.
- **Blank code with a promotion, below the minimum.** No code means no check of the minimum: no `SUBTOTAL_BELOW_MINIMUM` either. The whole `Price` equals the one with no code.
- **Blank code with an empty cart.** Same as no code: zeros, no fee line, no reason (not `SUBTOTAL_BELOW_MINIMUM`).
- **Blank code with a line of quantity zero.** Unreachable: `CartLine` refuses quantity zero at construction (R18), before any code exists. Unchanged.
- **Blank code with a foreign-currency line or an amount that is too large.** A blank code hides no refusal: the currency refusal (D-42) and `AmountTooLargeException` (D-38) still come out, exactly as with no code.
- **Refusal of a blank promotion code in the rules.** `IllegalArgumentException` raised by `PricingRules(...)`, like the rate, minimum and fee refusals (D-28, D-36, D-37). The caller observes the type only; the message is not a contract and no test pins it (D-43 style).
- **Several rules problems at once** (blank code and a rate out of range, a negative minimum, a minimum in another currency, a fee in another currency). Every one of them is an `IllegalArgumentException` raised at construction, so the type is identical whichever check fires first, and no pricing happens. Which message comes first is not observable beyond the message: untested, not a question (same reasoning as the edge-amounts plan, section 3).
- **A cart priced with foreign-currency line AND rules that were refused.** Cannot happen: the rules do not exist.
- **Whitespace around a non-blank code is part of the code (C1).** A promotion code `" SAVE10 "` is not blank, is accepted by the rules, and matches only the supplied text `" SAVE10 "` exactly; `"SAVE10"` does not match it.
- **A code made only of invisible characters** (zero-width space U+200B, BOM U+FEFF): decided by D-45. Under option A it is a non-blank code: an unknown code on the cart side (`UNKNOWN_CODE`), and accepted as a promotion code on the rules side (matched by exact text).
- **Twice / nothing / invalid / edge / order**, for each thing the plan adds or changes
  - *Blank code on the cart side*: twice = same Price, nothing accumulates; nothing = the same as `null` (and `price(cart, rules)` with the default); invalid = not a refusal, a blank code is never invalid; edge = the named characters of the table (section 4), a one-character blank, a blank next to a valid code (`"SAVE10 "` is unknown); order = no effect on the lines or on a refusal, blank code with a code supplied before or after another pricing gives the same result (B8).
  - *Blank promotion code in the rules*: twice = building refused twice, the same; nothing = `""`; invalid = `" "`, tab, newline, no-break space, ideographic space; edge = `"A"` and `" A "` are accepted; order = refused whichever of the other rule checks also fails, same type; a refused construction leaves nothing behind, the next rules build (B6).
  - *Simultaneous use*: twice = repeated calls; nothing = empty cart and no code in parallel; invalid = a refused pricing in parallel with good ones does not disturb them (T5); edge = a single thread, and the number of threads above the number of cores; order = results do not depend on which call starts first (T3).

### Technical choices (no caller can observe; for the reviewer to challenge)

- Normalisation is one line at the top of `domain.pricing.price`, after the currency `require`. `PriceCart.price` stays a pure delegate; no new type, parameter or helper in `domain.rules`.
- The rules check is a `require(promotion.code.isBlank().not())` in the promotion block of `PricingRules.init`, placed after the rate, currency and minimum checks (order is unobservable, all `IllegalArgumentException`).
- New test classes in `application`: `EdgeCodesTest` (codes, boundary `PriceCart.price` and the `PricingRules(...)` construction that refuses) and `ConcurrentPricingTest` (boundary `PriceCart.price`). Fixtures: EUR, the same helper names as `ApplyPromotionTest` (`eur`, `line`, `cartOf`, `rules`), code `WELCOME10`, minimum 1000, fee 250, rate 10 percent.
- Concurrency tests use plain `Thread`s and a `CountDownLatch` as start gate (so no executor to leak), a fixed thread count (16, above any usual core count), a fixed number of rounds (200), no randomness, no sleeping. Exceptions of a worker are collected in a `ConcurrentLinkedQueue` and asserted empty on the main thread. The join has a timeout (30 seconds) so a hang is a failure, not a stuck build.
- Blank characters are written as Unicode escapes with a named constant each (`noBreakSpace = " "`), never as the literal character, so the source shows what is tested.

## 4. Expected behaviors

Test boundary unless stated: `PriceCart.price(cart, rules, code)`; refusal of rules observed at the `PricingRules(...)` call. Amounts in minor units, EUR, rules: fee 250, promotion `WELCOME10`, 10 percent, minimum 1000.

**Blank codes (C7, C1, C9)**, in `EdgeCodesTest`

- **B1 a blank code is no code (C7)**: given a cart of subtotal 2000 and the rules with a promotion, when it is priced with each of `""`, `" "`, `"   "`, tab, newline, carriage return, `" "` (no-break space), `"　"` (ideographic space), `" \t\n "`, then the whole `Price` equals `price(cart, rules)` with no code and equals `price(cart, rules, null)`: discount 0, no reason, total 2250. Same cart, subtotal 999 (below the minimum): still no reason (not `SUBTOTAL_BELOW_MINIMUM`), total 1249.
- **B2 a blank code with rules that have no promotion (C7, D-34 amended)**: given `PricingRules(eur, eur(250))`, when priced with `""` and `" "`, then no reason (not `UNKNOWN_CODE`), discount 0, total as without a code; while `"WELCOME10"` on the same rules is still `UNKNOWN_CODE` (the existing test).
- **B3 a blank code with an empty cart (C7)**: given `Cart(emptyList())` and rules with a promotion, when priced with `""`, then subtotal, discount and total are 0, no fee line, no reason; with `"WELCOME10"` it is still `SUBTOTAL_BELOW_MINIMUM` (existing test).
- **B4 a blank code hides no refusal (C7, D-42, D-38)**: given a line in JPY and EUR rules, when priced with `""`, then `IllegalArgumentException` as with no code; given a total beyond the range, when priced with `" "`, then `AmountTooLargeException` as with no code.
- **B5 a non-blank code is never trimmed or reinterpreted (C1)**: given the promotion `WELCOME10`, when priced with `"WELCOME10"`, then the discount of 10 percent and no reason; with `" WELCOME10"`, `"WELCOME10 "`, `" WELCOME10 "`, `"WELCOME10\n"`, `"welcome10"`, `"WELCOME 10"` then `UNKNOWN_CODE`, discount 0; with `"​"` (zero-width space) and `"​ "` then `UNKNOWN_CODE` (an invisible character is a character, not blank). The mutant that trims, or that tests `trim().isEmpty()`, dies on `"WELCOME10 "`.
- **B6 the definition of blank is pinned by named characters (architect, D-45)**: a table of one-character codes, each priced against the rules above, expecting "no code" for: empty, U+0020 space, U+0009 tab, U+000A newline, U+000D carriage return, U+000B vertical tab, U+000C form feed, U+00A0 no-break space, U+2003 em space, U+3000 ideographic space, and "unknown code" for: U+200B zero-width space, U+FEFF byte order mark, `"A"`, `"0"`. U+0085 and U+001C..U+001F are not asserted (accepted gaps: nobody types them, see Q1); U+2007 and U+202F (no-break variants) are asserted blank (option A: this is the reason for choosing Kotlin over Java).
- **B7 twice and nothing (C6, C7)**: pricing with `""` twice gives equal Prices; `""`, `" "` and no code give equal Prices; the cart and the rules are equal to copies taken before.

**Blank promotion code in the rules (C8, C9)**, in `EdgeCodesTest`

- **B8 rules with a blank promotion code are refused at construction (C8)**: `PricingRules(eur, eur(250), Promotion(code, rate, eur(1000)))` raises `IllegalArgumentException` for code `""`, `" "`, tab, newline, `" "`, `"　"`; no cart is priced with them. Accepted: `"WELCOME10"`, `"A"`, `" WELCOME10 "` (spaces are part of the code), `"​"`. `Promotion(code = "", ...)` on its own still builds (only the rules refuse).
- **B9 the refusal comes from the code alone and wins over nothing (C8)**: the same blank code with a rate out of range, a negative minimum, a minimum in another currency, or a fee in another currency also raises `IllegalArgumentException` (type only, no order asserted); the same promotion with a non-blank code and a valid rate is accepted, so removing or inverting the check dies. Rules without a promotion and rules with a promotion of any valid code are unchanged.
- **B10 a refused construction leaves nothing behind (A5-style, C2)**: after a refused `PricingRules`, a corrected `PricingRules` builds and prices correctly, equal to a fresh result; a refused construction twice refuses twice.
- **B11 the currency stays out of it (C9)**: nothing is asked of the currency by this request: `PricingRules(eur, ...)` with a valid code is unchanged; no other identifier of the feature is checked for blankness. (No new test: covered by every existing test that builds rules; recorded as the acceptance of C9.)

**Simultaneous pricing (C2..C6)**, in `ConcurrentPricingTest`; the pricing is the same function in every thread

- **T1 same cart, same rules, same code, at once (C3, C2)**: given a cart of three lines and the rules with a promotion, when 16 threads, released together by a latch, each price it 200 times, once per round with each of: a valid code, an unknown code, a valid code below the minimum, a blank code and no code, then every result equals the result the same call gives alone (computed before the threads start), and the cart (`lines`) and the rules are equal to copies taken before and after (C2).
- **T2 different carts at once, no mix (C5)**: given 16 carts that differ from each other by one line (different unit price and quantity), priced with the same rules, when each thread prices its own cart 200 times at once, then each result equals the solo result of its own cart (a result of another cart, or of a half of two, differs in at least one amount); the subtotal of each result equals the exact sum of its own lines.
- **T3 repeated and in another order (C6)**: given carts A and B, pricing A, B, A, B 1000 times gives always the same two results; pricing them as B, A, B, A gives the same two results (no counter, no memory of an earlier call); the result of A after 1000 pricings of B equals the solo result of A.
- **T4 a pricing never waits or fails because of another (C4)**: in T1 and T2 every thread finishes within the timeout and none raised an exception (the collected exceptions are empty). What this proves: no deadlock or failure on this run. What it does not: that no lock exists (rests on ADR-0004 and INV-004, no `java.util.concurrent` and no `synchronized` in the core).
- **T5 a refusal in one thread disturbs no other (C4, C5)**: half the threads price a cart with a line in JPY against EUR rules (`IllegalArgumentException` each time), the other half price a good cart; every good result equals its solo result, every bad call raised the same refusal.
- **T6 empty and no code, in parallel (C3)**: `Cart(emptyList())` priced at once with a blank code and with no code gives the same result in every thread.

**What these tests cannot prove, and what carries the guarantee.** A test that passes shows that this run did not misbehave, not that no interleaving can: a data race that does not happen during the run is not seen, and no mutation tool changes that. The guarantee that holds for every interleaving is structural: ADR-0004 (pricing is a pure function over immutable inputs, no cache, memo, counter or lock) and INV-007 (every field of `domain` and `application` is final, run by `check_layers.py` and `run_all.sh`), with INV-004 (no clock, no `java.util.concurrent` in the core). The tests are a smoke check on the current code and a tripwire for a visible shared-state break; INV-007 and the ADR are the guard. Known limit of INV-007 (stated in `invariants.md`): it sees the field, not the content of a final field. Step 5 shows that the tests are able to fail.

**What mutation cannot see.** `isBlank()` is a stdlib call: PIT mutates the conditional around it but not its definition, so a changed definition is caught only by the named characters of B6 and B8. No mutator introduces shared state or a race, so the concurrency tests will bring no mutation gain; no test is added to chase a score there. The survivors to separate on the branches: blank vs `""` vs `" WELCOME10 "` vs the exact code, with and without a promotion in the rules, below and above the minimum (B1, B2, B5); the rules check needs `""`, `" "` and a valid code on the same promotion (B8, B9).

## 5. Steps

TDD, one behavior at a time (red, green, refactor); after each green `bash tools/harness/run_all.sh`; Maven: `tools/harness/_maven.sh -o test`. Each test-case file is created together with its test (front-matter as in the existing files: `feature: price-a-cart`, `source: PRD C.., D-40/D-41`, `status: covered`, `automated_test` exactly the test name). The existing tests stay unchanged and green at every step (C1); if one must change, that is a deviation.

- [ ] Step 1: blank code is no code. Create `src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt` with B1, B2, B3, B4 (red), then in `src/main/kotlin/io/example/mealcart/domain/pricing/Pricing.kt` add `val code = code?.takeUnless { it.isBlank() }` after the currency `require` (the `when` and the discount line read the normalised value; rename the parameter or shadow as the code style allows). Test-cases: `blank-code-is-no-code`, `blank-code-with-rules-without-promotion`, `blank-code-with-an-empty-cart`, `blank-code-hides-no-refusal`.
- [ ] Step 2: non-blank codes unchanged and the definition pinned. Add B5, B6, B7 to `EdgeCodesTest` (B5 and the "unknown" half of B6 are green at once: they pin C1; write them before Step 1's change is merged and watch that a `trim()` variant of the change makes them red). Test-cases: `non-blank-code-is-never-trimmed`, `what-counts-as-blank-for-a-code`, `blank-code-twice-gives-the-same-result`.
- [ ] Step 3: blank promotion code in the rules. Add B8, B9, B10 to `EdgeCodesTest` (red), then in `src/main/kotlin/io/example/mealcart/domain/rules/PricingRules.kt` add `require(promotion.code.isBlank().not())` in the promotion block, after the minimum checks, and extend the doc comment of `PricingRules` (the promotion code must not be blank). Test-cases: `rules-with-a-blank-promotion-code-refused`, `blank-promotion-code-refused-with-any-other-rule-problem`, `refused-rules-leave-nothing-behind`.
- [ ] Step 4: simultaneous pricing. Create `src/test/kotlin/io/example/mealcart/application/ConcurrentPricingTest.kt` with T1..T6 (a private helper `runTogether(threads, task)`: starts the threads, releases them with the latch, joins with the timeout, returns the collected exceptions and results). They are green at once (nothing in `src/main` changes for them). Test-cases: `simultaneous-pricings-give-the-solo-result`, `different-carts-at-once-never-mix`, `repeated-pricings-give-the-same-result-in-any-order`, `a-pricing-never-fails-because-of-another`, `a-refusal-does-not-disturb-other-pricings`, `empty-cart-priced-at-once`.
- [ ] Step 5: show that the concurrency tests can fail (not committed). Temporarily add a mutable top-level `private var last: Money? = null` in `Pricing.kt` that the subtotal passes through (written by each call, read to build the result), run `ConcurrentPricingTest`: T2 must fail (a result carrying the subtotal of another cart); run `check_layers.py`: INV-007 must report the `var`. Revert and record the two outcomes in section 9. If T2 does not fail on this machine within the rounds, raise the rounds in the test, not the threshold of INV-007.
- [ ] Step 6: documentation of the changed meaning. Edit the wording of the test-cases `code-matches-exactly` and `unknown-code-gives-no-discount` (a code that is only blank is no code); no change of their `automated_test`. Confirm no existing test changed.
- [ ] Step 7: closing. `tools/harness/_maven.sh -o test`; `bash tools/harness/run_all.sh` (INV-001..005 and INV-007; `check_test_coverage.py`: 0 pending, 0 broken, 0 orphan); `bash tools/harness/run_mutation.sh --scope diff` (record the score; survivors on `Pricing.kt` or `PricingRules.kt` are real gaps, to fix by a behavior); run the new tests through the "wrong direction signals" of `behavior-driven-testing`.

## 6. Risks & edge cases

- **Sensitive zone**: `domain.pricing.price` changes at its entry: a mistake changes who gets a discount. B1 (all blank forms), B5 (the exact code still applies and nothing is trimmed) and the existing `a valid code takes the rate off the subtotal` protect it.
- **A caller that showed "code failed" for a cleared field stops seeing it; rules with a blank code that used to build now throw at construction.** Both are the requested changes (D-40). Say so in release notes (architect).
- **`isBlank()` definition**: invisible to PIT; pinned by named characters only (B6, B8). A later change of Kotlin version in its definition would be caught there.
- **The tests of simultaneity are probabilistic by nature** (see section 4): they must never be read as a proof, and a green run is not a reason to relax ADR-0004 or INV-007. Flakiness risk: the tests assert equality only, never timing; a slow machine only slows them down (join timeout 30 seconds, not a performance check).
- **Mutable runtime list in `Cart`**: `Cart.lines` is typed `List` but holds an `ArrayList`; pricing never writes to it (INV-007 does not see content). Accepted by the architect.
- **Merge** with `edge-amounts` already done: `Pricing.kt` and `PricingRules.init` were both edited there; the diff here is two small lines.

### Question to the product owner (round 1: answered, D-45 = Q1 A, D-46 amends D-33/D-34; nothing consumer-visible remains open)

**Q1. Which characters make a code "blank" (C7, C8)?** The PRD says "only whitespace" without a character class. A caller sees the difference: a code pasted from a web page that holds only a no-break space is either "no code" or "a code that failed"; the same definition is applied to the promotion code of the rules. Characters concerned: ordinary space, tab, newlines, no-break spaces (U+00A0, U+2007, U+202F), ideographic space (U+3000) and other Unicode space separators; and the edge ones, U+0085 (next line), U+001C to U+001F (control separators), U+200B and U+FEFF (zero-width, invisible).
- A (recommended): the Kotlin definition (the architect's choice): blank = empty or only space characters, tabs and line breaks, the no-break spaces and the other Unicode space separators; U+001C..U+001F count as blank; U+0085 and the invisible U+200B and U+FEFF do not. A code made only of an invisible character is a code (unknown on the cart side; accepted as a promotion code in the rules).
- B: strictly the Unicode White_Space property: like A, but U+0085 counts as blank and U+001C..U+001F do not. Same for invisible characters (they are not blank).
- C: the Java definition: no-break spaces (U+00A0, U+2007, U+202F) do NOT count as blank, so a code of one no-break space is an unknown code.
- D: A plus the invisible characters (U+200B, U+FEFF, and other format characters) also count as blank. Needs a hand-written character list; a cart code of invisible characters means no code, and the rules refuse such a promotion code.
- E: other / let me explain.

No other point is a question: the type of the rules refusal and the order against the other rule checks (section 3), a blank code with rules that have no promotion, an empty cart or a quantity-zero line (section 3, from C7 and R18) are decided by the documents. Not questions either: the message text of any refusal, the number of threads and rounds of the tests, the open minors carried over (exact-text match, D-34; `Percentage(10, 2) != Percentage(100, 3)`).

## 7. Out of scope

- Negative and too-large amounts (another request, done: `edge-amounts`).
- A catalogue, sessions, editing a cart while it is priced (the PRD says C5 would be read again then; a new ADR superseding ADR-0004 would be needed).
- Trimming, case-folding or normalising a non-blank code (C1, D-34); a second promotion; Unicode normalisation of codes.
- Any lock, cache, executor or concurrency type in `domain` or `application` (ADR-0004, INV-004). A performance or throughput test.
- Any change of `PriceCart.price` or `Promotion` signatures; any change to INV-007 or the harness.
- Editing `docs/business/decisions.md` (product owner): the amendment of D-33/D-34 by D-40 is a follow-up.
- Chasing a mutation score with concurrency tests.

## 8. Deviations

(empty)

## 9. Self-review

(empty)

## 10. Follow-up actions

(to fill at closing) Known from planning: D-46 already records the amendment of D-33/D-34 and D-45 the definition of blank; release notes for the two behavior changes; the carried-over minors stay open.
