---
feature: price-a-cart
type: functional
priority: high
source: PRD A4, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a total beyond the money range is refused when the subtotal alone fits
status: covered
---

# A total beyond the money range is refused when the subtotal alone fits

- Given: a subtotal that fits and a fee that brings the total to the largest amount, or one unit beyond
- When: the cart is priced
- Then: the total at the largest amount is priced; one unit beyond is refused as amount too large; the same cart with no fee is priced
