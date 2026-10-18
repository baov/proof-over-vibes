---
feature: price-a-cart
type: functional
priority: high
source: PRD C7, D-38, D-42
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeCodesTest.kt::a blank code hides no refusal
status: covered
---

# A blank code hides no refusal

- Given: a cart with a line in another currency, or a total beyond the money range
- When: the cart is priced with an empty or blank code
- Then: the same refusal as with no code: the currency refusal, or the amount-too-large refusal
