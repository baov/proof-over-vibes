---
feature: price-a-cart
type: functional
priority: high
source: D-42; PRD A3
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a line in another currency is refused before any amount is looked at
status: covered
---

# A line in another currency is refused before any amount is looked at

- Given: a cart with a line in yen, priced with rules in euros, together with an amount beyond the money range (in an earlier line, in the same line, or in the sum)
- When: the cart is priced
- Then: the caller gets the invalid-input error (IllegalArgumentException), never amount too large
