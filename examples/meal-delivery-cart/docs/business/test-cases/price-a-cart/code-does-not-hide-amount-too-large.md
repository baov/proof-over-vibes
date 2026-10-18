---
feature: price-a-cart
type: functional
priority: high
source: PRD A10, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a code never hides an amount that is too large
status: covered
---

# A code never hides an amount that is too large

- Given: a total beyond the money range with an unknown code, a valid code below the minimum and a valid code
- When: the cart is priced with the code
- Then: each is refused as amount too large; no price is returned carrying a reason
