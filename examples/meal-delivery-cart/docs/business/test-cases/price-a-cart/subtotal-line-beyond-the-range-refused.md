---
feature: price-a-cart
type: functional
priority: high
source: PRD A2, A4, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::a line beyond the money range is refused, one at the limit is priced
status: covered
---

# A line beyond the money range is refused, one at the limit is priced

- Given: a line whose unit price times quantity is the largest amount, and one a unit beyond
- When: the cart is priced
- Then: the largest amount is priced exactly; one unit beyond is refused as amount too large and no price is returned
