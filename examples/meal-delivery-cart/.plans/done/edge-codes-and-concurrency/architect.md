---
role: architect
status: done
structure: decided
reasons:
  - "No costly decision: ADR-0001..0003 and INV-001..004 stay intact, signatures unchanged. The two behavior changes were approved by the human (D-40). One additive ADR (0004) and one proposed invariant for the harness engineer."
---

# Architect note: blank codes and simultaneous pricing

## (a) Signature and contract

- The code is `code: String? = null` in `PriceCart.price` and in `domain.pricing.price`. Unchanged: no new type, no new parameter.
- **Behavior change for callers, not a signature break.** Before: a supplied `""` or `"  "` gave `UNKNOWN_CODE` (D-33, D-34: exact text, and also with rules without promotion). Now (D-40, C7): it gives no discount and no reason, as if no code. A caller that displayed "code failed" for a cleared field will stop seeing it, which is the goal.
- **Second change, stricter:** rules with a blank promotion code used to build; now `PricingRules(...)` throws `IllegalArgumentException` (C8). A caller that built such rules fails at construction, not at pricing.
- Neither supersedes an ADR (ADR-0001..0003 say nothing on codes) and the human decided both (D-40, status `answered`), so there is no escalation. The sensitive zone (`domain.pricing`) is touched; as for the amounts request, D-40 is the approval of the behavior. A person still reads that diff. Tell release notes about both changes.

## (b) Whitespace definition: Kotlin `String.isBlank()` (cheap to reverse, decided)

The three candidates differ:

- Unicode `White_Space`: U+0009-000D, U+0020, U+0085, U+00A0, U+1680, U+2000-200A, U+2028, U+2029, U+202F, U+205F, U+3000. Not U+001C-001F.
- Java `Character.isWhitespace` (also Java's `String.isBlank`): space separators except the no-break ones (U+00A0, U+2007, U+202F), plus U+0009-000D and U+001C-001F. So a code of only a no-break space is NOT blank; U+0085 is not blank.
- Kotlin `Char.isWhitespace` (so `String.isBlank()`): Java's set plus the no-break spaces (`isWhitespace || isSpaceChar`). U+0085 is still not blank; U+001C-001F are blank.

Choice: Kotlin `isBlank()`. A code pasted from a web page often carries a no-break space; Java's definition would call it an unknown code, the very message C7 wants to avoid. Gaps against Unicode: U+0085 not blank, U+001C-001F blank; accepted (nobody types them). A zero-width space (U+200B, a format character) is not whitespace in any of the three: a code made only of it stays an unknown code. For the Planner: pin the definition with named cases (empty, space, tab, newline, U+00A0, U+3000 blank; U+200B and `" SAVE10 "` not blank), since no mutant will notice a changed definition.

## Where the checks live

- **Supplied code (before matching, not inside):** at the top of `domain.pricing.price`, normalise once: `val code = code?.takeUnless { it.isBlank() }`, then the existing `when` runs unchanged on the normalised code. Reasons: one place for every caller of the domain function; `PriceCart` stays a pure delegate; a non-blank code is never trimmed (C1), so the match still compares the original text. The currency `require` keeps its place before it (D-42 order is unaffected, a blank code refuses nothing).
- **(c) Blank promotion code in the rules:** `PricingRules.init`, in the `if (promotion != null)` block, a `require(promotion.code.isBlank().not())` next to the rate, currency and minimum checks, `IllegalArgumentException` with a message that names the rule. Same precedent as D-36 and the negative fee/minimum: the rules refuse, the value classes (`Promotion`, `Percentage`) stay plain. Same `isBlank()` as the cart side, so a code the rules accept can always be matched by a non-blank supplied code and the two sides cannot disagree. `Promotion(code = "")` alone still builds; only the rules refuse it.

## (d) ADR for simultaneous use

Yes: ADR-0004 written (`docs/technical/adr/0004-pricing-is-pure-over-immutable-inputs.md`). The decision existed only in the `price-a-cart` architect note, it is lasting, and it is the guard against a later cache, counter or editable cart. No new code is needed to satisfy C2 to C6: `Cart` copies its list, all classes are `val`-only, `price` builds a new `Price`.

**For the harness engineer: INV-007 (proposed, cheap).** ArchUnit in `ArchitectureTest`: "every field of every class in `domain` and `application` is final" (`fields().that().areDeclaredInClassesThat().resideInAnyPackage("..domain..", "..application..").should().beFinal()`). Kotlin `val` compiles to a final field and `var` to a non-final one, `object` instances and `companion` statics are `static final`, so the rule catches a `var`, a mutable cache or a counter. Source: ADR-0004. Add `synchronized`/lock bans only if wanted: INV-004 already forbids `java.util.concurrent`. Known limit: it sees the field, not the content (a final field holding a mutable list passes); `Cart.lines` is a private copy but is typed as a mutable `ArrayList` at runtime, which is acceptable since pricing never writes it. Severity warn, like the others.

## For the Planner

- **Testing C3 to C5:** no new production seam. Tests (they may use `java.util.concurrent`; INV-004 excludes tests) price the same cart and rules from N threads released together by a latch, many rounds, plus sequential repeats, and compare every result by equality (`Price` is a data class) with the solo result; also several different carts at once, each against its own solo result (C5, no mix); also that the cart and rules are equal to a copy taken before (C2). Say in the plan what the tests cannot do: a race that does not happen on this run is not seen, so the guarantee rests on ADR-0004 and INV-007. C4 (never waits) rests on the absence of locks; a timeout on the join is enough as a test. C6: two calls with the clock/order changed give the same result (already covered by `same-input-same-result`).
- **Mutation gap:** (1) `isBlank()` is a stdlib call: PIT mutates the conditional around it but not its definition, so only named-character cases (above) protect it. (2) Cases to separate the mutants: a whitespace-only code vs `""` vs `" SAVE10 "` vs the exact code, with and without a promotion in the rules, below and above the minimum (a blank code must not leak `SUBTOTAL_BELOW_MINIMUM` either). (3) The blank rules check needs `""`, `" "` and a valid code on the same promotion, so removing the `require` or inverting it dies. (4) No PIT mutator introduces shared state or a race, so concurrency tests will show no mutation gain: do not add tests to chase score there.
- Existing test-cases `code-matches-exactly` and the `UNKNOWN_CODE` ones that use `""` or a blank code must be re-read: they change meaning. Update INV-005 test-cases for every new test.
- Open minors carried over (not in this request): the exact-text match stays (D-34); `Percentage(10,2) != Percentage(100,3)`.
