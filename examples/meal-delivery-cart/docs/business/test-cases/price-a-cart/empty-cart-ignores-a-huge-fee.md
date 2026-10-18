---
feature: price-a-cart
type: functional
priority: high
source: PRD A6, R17, D-32
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::an empty cart ignores a fee of any size
status: covered
---

# An empty cart ignores a fee of any size

- Given: an empty cart and rules with a fee at the largest amount
- When: the cart is priced
- Then: every amount is 0, there is no fee line, and nothing is refused
