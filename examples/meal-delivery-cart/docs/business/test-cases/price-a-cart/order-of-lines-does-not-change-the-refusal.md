---
feature: price-a-cart
type: functional
priority: high
source: PRD A2, D-38
automated_test: src/test/kotlin/io/example/mealcart/application/EdgeAmountsTest.kt::the refusal does not depend on the order of the lines
status: covered
---

# The refusal does not depend on the order of the lines

- Given: two lines whose sum is the largest amount, or one unit beyond, in either order
- When: the cart is priced
- Then: the sum that fits is priced and the one beyond is refused, in both orders
